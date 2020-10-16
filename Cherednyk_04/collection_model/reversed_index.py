import math

from sortedcontainers import SortedDict

from collection_creation.collection_info import WordCollectionInfo
from collection_creation.fileIO import get_words, get_words_pair, get_positioned_words


# vocabulary [word] = {id,filesWhereFoundCount}
# list postings[word.id] = [docId1,docId2,......]
# or list postings[word.id] = [{docID,position},....]


def get_coordinate_index(documents) -> WordCollectionInfo:
    vocabulary = dict()
    postings = list()
    all_words_counter = 0
    unique_word_id = 0
    for word, pos, doc_id in get_positioned_words(documents):
        if word not in vocabulary:
            word_id = unique_word_id
            vocabulary[word] = {"id": word_id, "frequency": 0}
            postings.append(dict())
            unique_word_id += 1
        vocabulary[word]["frequency"] += 1
        word_id = vocabulary[word]["id"]
        if doc_id not in postings[word_id]:
            postings[word_id][doc_id] = [pos]
        else:
            postings[word_id][doc_id].append(pos)
        all_words_counter += 1
    return WordCollectionInfo(SortedDict(vocabulary), postings, documents, all_words_counter)


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


def get_biword_index(documents) -> WordCollectionInfo:
    vocabulary = dict()
    postings = list()
    all_words_counter = 0
    unique_word_id = 0
    for word_pair, doc_id in get_words_pair(documents):
        unique_word_id = add_word(word_pair, unique_word_id, doc_id, vocabulary, postings)
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


def ANDmany(rows):
    rows = sorted(rows, key=lambda x: len(x))
    res = rows.pop(0)
    while rows:
        res = AND(res, rows.pop(0))
    return res


def OR(row1, row2):
    return list(sorted(set(row1 + row2)))

def ORMany(rows):
    if not rows:
        return []
    res = rows[0]
    for row in rows[1:]:
        res +=row
    return list(sorted(set(res)))


def NOT(doc_count, row):
    return [i for i in range(doc_count) if i not in row]


def positionAND(row1, row2, k):
    res = []
    common_docIDs = AND([k for k in row1.keys()], [k for k in row2.keys()])
    for docID in common_docIDs:
        pos1 = row1[docID]
        pos2 = row2[docID]
        i1 = 0
        i2 = 0
        found = False
        while i1 < len(pos1):
            while i2 < len(pos2):
                if abs(pos1[i1] - pos2[i2]) <= k:
                    res.append(int(docID))
                    found = True
                    break
                elif pos2[i2] > pos1[i1]:
                    break
                else:
                    i2 += 1
            if found:
                break
            i1 += 1
        return res
