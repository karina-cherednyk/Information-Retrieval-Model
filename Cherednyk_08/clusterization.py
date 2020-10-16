import math

from collection_creation.collection_info import WordCollectionInfo
from collection_model.reversed_index import NOT


def get_documents_vector(info: WordCollectionInfo):
    vocabulary = info.vocabulary
    postings = info.postings
    docs = info.documents
    doc_vectors = []
    for i in range(len(docs) + 1):
        doc_vectors.append(list())

    for term in vocabulary.keys():
        idf = math.log(len(docs) / vocabulary[term]['df'])
        if idf == 0:
            pass  # n == df, term is in every doc
        postings_list = postings[vocabulary[term]['id']]
        for doc_id, tf in postings_list:  # as each term tf_idf is appended to every document consequently
            doc_vectors[doc_id].append(tf * idf)  # index for term in list will be the same in every document vector
        not_in_postings_list = NOT(len(docs), [doc_id for [doc_id,df] in postings_list])
        # if term is not in doc weight = 0
        for doc_id in not_in_postings_list:
            doc_vectors[doc_id].append(0)
    # normalization
    for i, doc_vector in enumerate(doc_vectors):
        sq_sum = sum(tf_idf * tf_idf for tf_idf in doc_vector)
        sq_sum = math.sqrt(sq_sum)
        doc_vectors[i] = [tf_idf / sq_sum for tf_idf in doc_vector]
    return doc_vectors


def sim(v1, v2):
    assert len(v1) == len(v2)
    res = sum(v1[i] * v2[i] for i in range(len(v1)))
    return res


def clusterize(info: WordCollectionInfo):
    N = len(info.documents)
    sqN = int(math.sqrt(N))
    cluster_leaders = [i for i in range(1, sqN+1)]
    clusters = [[leader] for leader in cluster_leaders]
    doc_vectors = get_documents_vector(info)

    # determine to which cluster does every other term belongs
    for doc in range(sqN+1, N + 1):
        sim_vec = [sim(doc_vectors[i], doc_vectors[doc]) for i in cluster_leaders]
        cluster = sim_vec.index(max(sim_vec)) - 1  # .index() returns value from 1, clusters are indexed from 0
        clusters[cluster].append(doc)
    return clusters
