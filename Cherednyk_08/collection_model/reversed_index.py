import math

from sortedcontainers import SortedDict

from collection_creation.collection_info import WordCollectionInfo
from collection_creation.fileIO import get_words


# vocabulary [word] = {id, num of docs with term}
# list postings[word.id] = [[docId1,freq] , [docId2,freq] ......]


def add_word(word: str, unique_word_id: int, doc_id: int, vocabulary: dict, postings: list) -> int:
    if word not in vocabulary:
        word_id = unique_word_id
        vocabulary[word] = {"id": word_id, "df": 1}
        postings.append([[doc_id, 1]])
        unique_word_id += 1
    else:
        word_id = vocabulary[word]["id"]

        if postings[word_id][-1][0] != doc_id:
            postings[word_id].append([doc_id, 1])
            vocabulary[word]["df"] += 1
        else:
            postings[word_id][-1][1] += 1

    return unique_word_id


def get_reversed_index(documents, encoding='utf-8') -> WordCollectionInfo:
    vocabulary = dict()
    postings = list()
    all_words_counter = 0
    unique_word_id = 0
    for word, doc_id in get_words(documents,encoding):
        unique_word_id = add_word(word, unique_word_id, doc_id, vocabulary, postings)
        all_words_counter += 1
    return WordCollectionInfo(SortedDict(vocabulary), postings, documents, all_words_counter)


def NOT(doc_count, row):
    return [i for i in range(1, doc_count + 1) if i not in row]

