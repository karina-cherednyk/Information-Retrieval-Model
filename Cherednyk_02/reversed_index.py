import math

from sortedcontainers import SortedDict

from collection_info import WordCollectionInfo
from fileIO import get_words


# vocabulary [word] = {id, total frequency}
# list postings[word.id] = [docId1,docId2,......]



def add_word(word: str, unique_word_id: int, doc_id: int, vocabulary: dict, postings: list) -> int:
    if word not in vocabulary:
        word_id = unique_word_id
        vocabulary[word] = {"id": word_id, "frequency": 1}
        postings.append([doc_id])
        unique_word_id += 1
    else:
        vocabulary[word]["frequency"] += 1
        word_id = vocabulary[word]["id"]
        if postings[word_id][-1] != doc_id:
            postings[word_id].append(doc_id)

    return unique_word_id


def get_reversed_index(documents) -> WordCollectionInfo:
    vocabulary = dict()
    postings = list()
    all_words_counter = 0
    unique_word_id = 0
    for word, doc_id in get_words(documents):
        unique_word_id = add_word(word, unique_word_id, doc_id, vocabulary, postings)
        all_words_counter += 1
    return WordCollectionInfo(SortedDict(vocabulary), postings, documents, all_words_counter)


def AND(row1, row2):
    res = []
    i_to = len(row1)
    j_to = len(row2)
    i = 0
    j = 0
    skip_i = int(math.sqrt(i_to))
    skip_j = int(math.sqrt(j_to))

    def i_can_skip():
        return i + skip_i < i_to and row1[i + skip_i] <= row2[j]

    def j_can_skip():
        return j + skip_j < j_to and row2[j + skip_j] <= row1[i]

    while i < i_to and j < j_to:
        if row1[i] == row2[j]:
            res.append(row1[i])
            i += 1
            j += 1
        elif row1[i] < row2[j]:
            if i_can_skip():
                while i_can_skip():
                    i += skip_i
            else:
                i += 1
        else:
            if j_can_skip():
                while j_can_skip():
                    j += skip_j
            else:
                j += 1
    return res


def ANDmany(*rows):
    rows = sorted(rows, key=lambda x: len(x))
    res = rows.pop(0)
    while rows:
        res = AND(res, rows.pop(0))
    return res


def OR(row1, row2):
    return list(sorted(set(row1 + row2)))


def NOT(doc_count, row):
    return [i for i in range(doc_count) if i not in row]

