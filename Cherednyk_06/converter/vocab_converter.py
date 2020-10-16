from collection_creation.fileIO import matches, norm_word
from converter.postings_converter import *

zero = 0
BYTE_ZERO = zero.to_bytes(1, 'big')


def str_from_block(block, encoding):
    m_len = min(map(len, block))
    common_i = -1
    first = block[0]

    for i in range(m_len):
        if not all(term[i] == first[i] for term in block):
            break
        else:
            common_i = i

    res_str = (common_i + 1).to_bytes(1, 'big')
    if common_i != -1:
        res_str += first[:common_i + 1].encode(encoding)
    for term in block:
        sub = term[common_i + 1:]
        res_str += (len(sub)).to_bytes(1, 'big') + sub.encode(encoding)
    return res_str


def block_from_str(m_str, encoding):
    len = m_str[0]
    common_part = m_str[1: 1 + len].decode(encoding)
    m_str = m_str[1 + len:]
    terms = []

    while m_str:
        len = m_str[0]
        terms.append(common_part + m_str[1: 1 + len].decode(encoding))
        m_str = m_str[1 + len:]
    return terms


class IndexBuilder:
    def __init__(self, f=to_gamma_str, encoding='utf-8'):
        self.postings_pointer = 0
        self.post_left_bits = ''
        self.encode = f
        self.encoding = encoding

    def add_block(self, block_dict):
        terms_bytes = str_from_block([m_set[0] for m_set in block_dict], encoding=self.encoding)
        table_block = []
        block_postings_str = ''
        for m_set in block_dict:
            doc_ids = m_set[2]
            postings_str = self.encode(doc_ids)
            block_postings_str += postings_str
            table_block.append(self.postings_pointer)
            self.postings_pointer += len(postings_str)
        posting_bytes = self.from_str_to_post_bytes(block_postings_str)
        table_block_bytes = b''
        for pointer in table_block:
            table_block_bytes = table_block_bytes + (pointer.to_bytes(4, byteorder='big'))

        return table_block_bytes, terms_bytes, posting_bytes

    def from_str_to_post_bytes(self, postings_str):
        postings_str = self.post_left_bits + postings_str
        res = b''
        while len(postings_str) >= 8:
            res += (int(postings_str[:8], 2).to_bytes(1, byteorder='big'))
            postings_str = postings_str[8:]
        self.post_left_bits = postings_str
        return res

    def get_last_byte(self):
        if self.post_left_bits == '':
            return BYTE_ZERO, b''
        added_zeros = (8 - len(self.post_left_bits))

        return self.postings_pointer.to_bytes(4, 'big'), int(self.post_left_bits + '0' * added_zeros, 2).to_bytes(1, byteorder='big')


def byte_to_str(string):
    string = string[2:]
    return (8 - len(string)) * '0' + string


def get_seq(b, from_byte, to_byte):
    res = ''
    for i in range(from_byte, to_byte + 1):
        res += byte_to_str(bin(b[i]))
    return res


def get_bits_str(b, from_i, to_i, zeros=0):
    from_byte, from_bit_i, to_byte = int(from_i / 8), from_i % 8, int(to_i / 8)
    to_bit_i = (to_byte - from_byte) * 8 + to_i % 8

    return get_seq(b, from_byte, to_byte)[from_bit_i: to_bit_i + 1 - zeros]


# get_bits_str(p_str, post_min, post_max - 1)

def num(b):
    return int.from_bytes(b, 'big')


def vocab_from_bytes(bytes_vocab, block_size, encoding):
    vocab = list()
    start = 0
    while start < len(bytes_vocab):
        common_i = bytes_vocab[start]  # returns int
        start = start + 1
        common_part = (bytes_vocab[start: start + common_i]).decode(encoding)
        start = start + common_i
        for i in range(block_size):
            if start >= len(bytes_vocab):
                break
            word_len = bytes_vocab[start]  # returns int
            start = start + 1
            subword = (bytes_vocab[start: start + word_len]).decode(encoding)
            start = start + word_len
            vocab.append(common_part + subword)
    return vocab


class Index:
    def __init__(self, block_size=4, decode=from_gamma_str, vocab_file='gamma_vocab.txt',
                 postings_file='gamma_postings.txt', pointers_file='table.txt', dir='D:/res/', encoding='utf-8'):
        with open(dir + vocab_file, 'rb') as v:
            self.vocab = vocab_from_bytes(v.read(), block_size, encoding)
        self.postings_file = dir + postings_file
        self.decode_postings = decode
        self.pointers = list()

        with open(dir + pointers_file, 'rb') as p:
            p_bytes = p.read()
            i = 0
            while i < len(p_bytes):
                pointer_bytes = p_bytes[i:4 + i]
                self.pointers.append(int.from_bytes(pointer_bytes, 'big'))
                i += 4

    def find_pos(self, term):
        for i, word in enumerate(self.vocab):
            if word == term:
                return i
        return -1

    def get_postings_bytes(self, pos):
        start_pointer = self.pointers[pos]
        end_pointer = self.pointers[pos + 1]-1

        from_byte, from_bit_i, to_byte = int(start_pointer / 8), start_pointer % 8, int(end_pointer / 8)
        to_bit_i = (to_byte - from_byte) * 8 + end_pointer % 8

        with open(self.postings_file, 'rb') as p:
            p.seek(from_byte)
            postings_bytes = p.read(to_byte - from_byte + 1)
        bytes_str = bin(int.from_bytes(postings_bytes, 'big'))[2:]
        return bytes_str[from_bit_i: to_bit_i + 1]

    def get_postings(self, word):
        if not matches(word):
            return []
        i = self.find_pos(norm_word(word))
        if i == -1:
            return []
        posting_bytes = self.get_postings_bytes(i)
        return self.decode_postings(posting_bytes)
