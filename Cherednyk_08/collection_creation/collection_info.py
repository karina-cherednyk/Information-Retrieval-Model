class WordCollectionInfo:
    def __init__(self, vocabulary, postings, documents=False, all_words=False):
        self.vocabulary = vocabulary
        self.postings = postings
        self.uniqueWords = len(vocabulary)
        if documents:
            self.documents = documents
        if all_words:
            self.allWords = all_words

    def stringify_vocab(self):
        res = ""
        for i,(key, values) in enumerate(self.vocabulary.items()):
            res+= str(i)+") "+key+"\n"+", ".join(x+": "+str(y) for x,y in values.items()) +"\n\n"
        return res

    def stringify_postings(self):
        res = ""
        for i, docs_info in enumerate(self.postings):
            res += "wordID: " + str(i) + "\ndocuments: " + ", ".join(str(info[0]) +': '+str(info[1]) for info in docs_info   ) + "\n\n"

        return res

