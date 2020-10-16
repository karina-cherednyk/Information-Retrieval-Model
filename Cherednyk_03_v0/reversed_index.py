from sortedcontainers import SortedDict

from collection_info import WordCollectionInfo
from fileIO import get_words, word_regex, get_words_pair, get_positioned_words
from term import Term

# def get_reversed_index(documents) -> WordCollectionInfo:
#     words_dict = {}
#     all_words_counter = 0
#     for word, docID in get_words(documents):
#         all_words_counter += 1
#         if word not in words_dict:
#             words_dict[word] = [docID]
#         elif words_dict[word][-1] != docID:
#             words_dict[word].append(docID)
#     return WordCollectionInfo(SortedDict(words_dict), documents, all_words_counter)

def get_reversed_index(documents) -> WordCollectionInfo:
    words_dict = {}
    all_words_counter = 0
    for word, docID in get_words(documents):
        all_words_counter += 1
        if word not in words_dict:
            words_dict[word] = Term([docID]) #postings is a list of docID
        elif words_dict[word].postings[-1] != docID:
            words_dict[word].postings.append(docID)
        words_dict[word].freq+=1
    return WordCollectionInfo(SortedDict(words_dict), documents, all_words_counter)


def get_biword_index(documents) -> WordCollectionInfo:
    words_dict = {}
    all_words_counter = 0
    for word, docID in get_words_pair(documents):
        all_words_counter += 1
        if word not in words_dict:
            words_dict[word] = Term([docID])  # postings is a list of docID
        elif words_dict[word].postings[-1] != docID:
            words_dict[word].postings.append(docID)
        words_dict[word].freq += 1
    return WordCollectionInfo(SortedDict(words_dict), documents, all_words_counter)


def get_coordinate_index(documents) -> WordCollectionInfo:
    words_dict = {}
    all_words_counter = 0
    for word,pos, docID in get_positioned_words(documents):
        all_words_counter += 1
        if word not in words_dict:
            words_dict[word] = Term() #postings  is [ dictionary key-docID, value - list of positions in document ]
        if docID not in words_dict[word].postings:
            words_dict[word].postings[docID] = {"frequncy":1, "positions":[pos]}
        else:
            words_dict[word].postings[docID]["frequency"]+=1
            words_dict[word].postings[docID]["positions"].append(pos)
    words_dict[word].freq += 1
    return WordCollectionInfo(SortedDict(words_dict), documents, all_words_counter)


def AND(row1, row2):
    res = []
    i_to = len(row1)
    j_to = len(row2)
    i = j = 0
    while i < i_to and j < j_to:
        if row1[i] == row2[j]:
            res.append(row1[i])
            i += 1
            j += 1
        elif row1[i] > row2[j]:
            j += 1
        else:
            i += 1
    return res


def OR(row1, row2):
    return list(sorted(set(row1 + row2)))


def NOT(doc_count, row):
    return [i for i in range(doc_count) if i not in row]
