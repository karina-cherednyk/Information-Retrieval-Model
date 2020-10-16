import json

from sortedcontainers import SortedDict

from collection_creation.fileIO import matches, norm_word
from converter.postings_converter import *


def strFromBlock(block):
    m_len = min(map(len, block))
    common_i = -1
    first = block[0]
    for i in range(m_len):
        if not all(term[i] == first[i] for term in block):
            break
        else:
            common_i = i
    if common_i is not -1:
        res_str = str(len(first[:common_i + 1])) + first[:common_i + 1]
    else:
        res_str = '0'
    for term in block:
        sub = term[common_i + 1:]
        res_str += str(len(sub)) + sub
    return res_str


def blockFromStr(m_str):
    common_len = int(m_str[0])
    common_part = m_str[1: 1 + common_len]
    m_str = m_str[1 + common_len:]
    terms = []
    while m_str:
        l = int(m_str[0])
        terms.append(common_part + m_str[1: l + 1])
        m_str = m_str[l + 1:]
    return terms


vocab = SortedDict(
    {"a": {"id": 0, "frequency": 1},
     "b": {"id": 1, "frequency": 1},
     "c": {"id": 2, "frequency": 1},
     "d": {"id": 3, "frequency": 1},
     "e": {"id": 4, "frequency": 1},
     "f": {"id": 5, "frequency": 1}
     })

postings = [
    [1, 2, 3],  # 0 , 100 ,101 or 10000001, 10000010, 100000011
    [4, 5, 6, 7, 8, 9],  # 11000, ...
    [1, 2, 3, 6, 12],
    [1, 3, 4],
    [5, 6, 7],
    [8, 9]
]


def create_whole_table(vocab: SortedDict, postings, toSomeStr, k):
    postings_str = ''
    term_str = ''
    table = []
    vocab_terms = [x for x in vocab.keys()]
    i = 0
    while len(vocab_terms) > i:
        block = vocab_terms[i:i + k]
        table_block = []
        term_pointer = len(term_str)
        term_str += strFromBlock(block)
        for term in block:
            doc_ids = postings[vocab[term]['id']]
            freq = vocab[term]['frequency']
            postings_pointer = len(postings_str)
            postings_str += toSomeStr(doc_ids)
            table_block.append((postings_pointer, freq))
        table_block[0] = (term_pointer, *table_block[0])
        table.append(table_block)
        i += k

    return table, term_str, postings_str


class GammaIndexBuilder:
    def __init__(self):
        self.term_pointer = 0
        self.postings_pointer = 0
        self.table = []


    def add_block(self, block_dict):
        term_str = strFromBlock([m_set[0] for m_set in block_dict])
        table_block = []
        block_postings_str = ''
        for m_set in block_dict:
            freq = m_set[1]
            doc_ids = m_set[2]
            postings_str = toGammaStr(doc_ids)
            block_postings_str += postings_str
            table_block.append([self.postings_pointer, freq])
            self.postings_pointer += len(postings_str)
        table_block[0] = [self.term_pointer, *table_block[0]]
        self.term_pointer += len(term_str)
        self.table.append(table_block)

        return term_str, block_postings_str

    def get_table(self):
        return self.table


def get_postings(word, table, vocab_str, p_str, fromSomeF):
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

        terms = blockFromStr(sub_str)
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
                    post_max = len(p_str)
                elif i is len(terms) - 1:
                    post_max = table[middle + 1][0][-2]
                else:
                    post_max = table[middle][i + 1][-2]
                return fromSomeF(p_str[post_min:post_max])

        if bigger:
            low = middle + 1
        else:
            high = middle - 1
    return []


class GammaIndex:
    def __init__(self, table_json_file='table.json', vocab_file='gamma_vocab.txt',
                 postings_file='gamma_postings.bin', dir='res'):
        if dir[-1] != '/':
            dir += '/'
        with open(dir + table_json_file, 'r') as t, open(dir + vocab_file, 'r') as v, open(dir + postings_file, 'rb') as p:
            self.table = json.load(t)
            self.vocab_str = v.readline()
            self.postings_str = repr(p.readline())[2:-1]

    def get_postings(self, word):
        if not matches(word):
            return []
        term = norm_word(word)
        return get_postings(term, self.table, self.vocab_str, self.postings_str, fromGammaStr)
