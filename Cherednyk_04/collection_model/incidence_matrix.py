from sortedcontainers import SortedDict
from bitarray import bitarray

from collection_creation.collection_info import WordCollectionInfo
from collection_creation.fileIO import get_words


def add_word(word: str, unique_word_id: int, doc_id: int, vocabulary: dict, postings: list, doc_count: int) -> int:
    if word not in vocabulary:
        word_id = unique_word_id
        vocabulary[word] = {"id": word_id, "frequency": 1}
        arr = bitarray(doc_count)
        arr.setall(0)
        arr[doc_id] = 1
        postings.append(arr)
        unique_word_id += 1
    else:
        vocabulary[word]["frequency"] += 1
        word_id = vocabulary[word]["id"]
        postings[word_id][doc_id] = 1
    return unique_word_id


def get_incidence_matrix(documents) -> WordCollectionInfo:
    vocabulary = dict()
    postings = list()
    all_words_counter = 0
    unique_word_id = 0
    doc_count = len(documents)
    for word, doc_id in get_words(documents):
        unique_word_id = add_word(word, unique_word_id, doc_id, vocabulary, postings,doc_count)
        all_words_counter += 1
    return WordCollectionInfo(SortedDict(vocabulary), postings, documents, all_words_counter)


def AND(row1, row2):
    return row1 & row2


def OR(row1, row2):
    return row1 | row2


def NOT(doc_count, row):
    return ~row
