from collection_creation.fileIO import is_function_word, norm_word
from collection_model.reversed_index import ANDmany, positionAND


def biword_query_parser(collection_info):
    vocab = collection_info.vocabulary
    post = collection_info.postings

    def search(query):
        res = []
        words = query.split(' ')
        words = list(filter(lambda x: not is_function_word(x), map(norm_word, (x for x in words))))

        word1 = words[0]
        res = list()
        for word in words[1:]:
            pair = word1+' '+word
            if pair not in vocab:
                return []
            res.append(post[vocab[pair]['id']])
            word1 = word
        return ANDmany(*res)

    return search


def coord_query_parser(collection_info):
    vocab = collection_info.vocabulary
    post = collection_info.postings

    def search(word1,word2,k):
        w1 = norm_word(word1)
        w2 = norm_word(word2)
        if w1 not in vocab or w2 not in vocab:
            return []
        return positionAND(post[vocab[w1]['id']], post[vocab[w2]['id']], int(k))

    return search
