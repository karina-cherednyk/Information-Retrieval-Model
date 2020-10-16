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
        self.term_pointer = 0
        self.postings_pointer = 0
        self.left_bits = ''
        self.encode = f
        self.encoding = encoding

    def add_block(self, block_dict):
        terms_bytes = str_from_block([m_set[0] for m_set in block_dict], encoding=self.encoding)
        table_block = []
        block_postings_str = ''
        for m_set in block_dict:
            freq = m_set[1]
            doc_ids = m_set[2]
            postings_str = self.encode(doc_ids)
            block_postings_str += postings_str
            table_block.append([self.postings_pointer, freq])
            self.postings_pointer += len(postings_str)
        table_block[0] = [self.term_pointer, *table_block[0]]
        self.term_pointer += len(terms_bytes)
        posting_bytes = self.from_str_to_bytes(block_postings_str)
        table_block_bytes = b''
        for row in table_block:
            for col in row:
                table_block_bytes += col.to_bytes(4, 'big')

        return table_block_bytes, terms_bytes, posting_bytes

    def from_str_to_bytes(self, postings_str):
        postings_str = self.left_bits + postings_str
        res = b''
        while len(postings_str) >= 8:
            res += (int(postings_str[:8], 2).to_bytes(1, byteorder='big'))
            postings_str = postings_str[8:]
        self.left_bits = postings_str
        return res

    def get_last_byte(self):
        if self.left_bits == '':
            return BYTE_ZERO, ''
        added_zeros = (8 - len(self.left_bits))
        return added_zeros.to_bytes(1, 'big'), int(self.left_bits + '0' * added_zeros, 2).to_bytes(1, byteorder='big')


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


def get_postings(word, table, vocab_str, p_str, zeros, decode, encoding):
    low = 0
    MAX = high = len(table) - 1
    last_p = len(vocab_str)
    while low <= high:
        middle = int((high + low) / 2)
        block_p = table[middle][0][0]  # 'term_pointer stores in first elem of block'
        if middle is MAX:
            next_p = last_p
        else:
            next_p = table[middle + 1][0][0]

        sub_str = vocab_str[block_p:next_p]
        terms = block_from_str(sub_str, encoding=encoding)
        bigger = False
        for i, term in enumerate(terms):
            if word > term:
                bigger = True
            elif word < term:
                if bigger:
                    return []  # word is bigger than first and smaller than second consecutive term
                else:
                    break  # word is less than first elem
            else:
                post_min = table[middle][i][-2]
                if i is len(terms) - 1 and middle is MAX:
                    post_max = len(p_str) * 8 - zeros
                elif i is len(terms) - 1:
                    post_max = table[middle + 1][0][-2]
                else:
                    post_max = table[middle][i + 1][-2]
                return decode(get_bits_str(p_str, post_min, post_max - 1))

        if bigger:
            low = middle + 1
        else:
            high = middle - 1
    return []


def num(b):
    return int.from_bytes(b, 'big')


class Index:
    def __init__(self, block_len=4, decode=from_gamma_str, table_file='table.txt', vocab_file='gamma_vocab.txt',
                 postings_file='gamma_postings.txt', dir='D:/res/', encoding='utf-8'):
        with open(dir + table_file, 'rb') as t, open(dir + vocab_file, 'rb') as v, \
                open(dir + postings_file, 'rb') as p:
            self.vocab_str = v.read()
            self.posting_bytes = p.read()
            self.table = []
            self.decode = decode
            self.encoding = encoding
            table_bytes = t.read()
            self.added_zeros = table_bytes[-1]
            table_bytes = table_bytes[:-1]
            j = 0
            while len(table_bytes) > j:
                block = list()
                block.append([num(table_bytes[j:j + 4]), num(table_bytes[j + 4:j + 8]), num(table_bytes[j + 8:j + 12])])
                j += 12
                i = 1
                while i < block_len and len(table_bytes) > j:
                    block.append([num(table_bytes[j:j + 4]), num(table_bytes[j + 4:j + 8])])
                    j += 8
                    i+=1
                self.table.append(block)

    def get_postings(self, word):
        if not matches(word):
            return []
        term = norm_word(word)
        return get_postings(term, self.table, self.vocab_str, self.posting_bytes, self.added_zeros, self.decode,
                            self.encoding)
