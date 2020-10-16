import time

from tolerant_retrieval.wildcard_queries import TrieSearch, ThreeGramIndex, PermutermTrieSearch
from collection_creation.fileIO import load_nfull_collection
from collection_model.reversed_index import OR

def toRows(postings,vocabulary, values):
    res = []
    for val in values:
        res.append(postings[vocabulary[val]["id"]])
    return res

def main():
    collection_info = load_nfull_collection('/files/ordinary')
    vocabulary = collection_info.vocabulary
    postings = collection_info.postings

    t_search = TrieSearch(vocabulary)
    p_search = PermutermTrieSearch(vocabulary)
    tg_search = ThreeGramIndex(vocabulary)

    words = ['най*р*','Найкращій','Найкр*','Найк*ій','*кращ*','найк ращ','*а*ращ*']

    for word in words:
        print("\nWord: "+word)

        start = time.perf_counter()
        res = t_search.search(word)
        time_spent = time.perf_counter() - start
        print(f"Trie: {time_spent:0.6f}, {res}\n")
        print(OR(toRows(postings, vocabulary, res)))
        print("\n")

        start = time.perf_counter()
        res = p_search.search(word)
        time_spent = time.perf_counter() - start
        print(f"Permuterm trie: {time_spent:0.6f}, {res}\n")
        print(OR(toRows(postings, vocabulary, res)))
        print("\n")
        start = time.perf_counter()
        res = tg_search.search(word)
        time_spent = time.perf_counter() - start
        print(f"3 gram index: {time_spent:0.6f}, {res}\n")
        print(OR(toRows(postings, vocabulary, res)))
        print("\n\n")



if __name__ == "__main__":
    main()
