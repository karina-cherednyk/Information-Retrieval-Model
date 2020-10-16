class WordCollectionInfo:
    def __init__(self, terms, documents, all_words):
        self.terms = terms
        self.documents = documents
        self.uniqueWords = len(terms)
        self.allWords = all_words

    def __str__(self):
        res = ""
        for i, (key, val) in enumerate(self.terms.items()):
            res += f"{i}){key}: {val}\n"
        return res
