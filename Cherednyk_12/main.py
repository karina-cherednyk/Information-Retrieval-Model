import os
import re
from xml.dom.minidom import parse
from gensim.summarization.bm25 import BM25

non_letters = "`'\-’"
word_regex = fr'\b[\w{non_letters}]+\b'


def norm_word(word: str) -> str:
    word = word.lower().translate(str.maketrans('', '', non_letters))
    return word


def matches(word):
    return re.search(word_regex, word)


def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
        else:
            nodelist.extend(node.childNodes)
    return ' '.join(rc)


def get_list_of_docs(dir):
    listOfFile = os.listdir(dir)
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(dir, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + get_list_of_docs(fullPath)
        else:
            allFiles.append(fullPath)

    return allFiles


def get_words(documents, encoding='utf-8'):
    corpus = list()
    doc_titles = list()
    for docID, document in enumerate(documents):
        corpus.append(list())
        if document.endswith('fb2'):
            dom = parse(document)
            str_file = getText(dom.getElementsByTagName('body')[0].childNodes)
            doc_titles.append(getText(dom.getElementsByTagName('book-title')[0].childNodes))
        else:
            with open(document, 'r', encoding=encoding) as reader:
                str_file = ''.join(reader.readlines())

        for word in re.findall(word_regex, str_file):
            word = norm_word(word)
            corpus[docID].append(word)

    return corpus, doc_titles


def get_ranked_docs(docs, scores):
    return [doc for _, doc in sorted(zip(scores, docs), reverse=True)]


# corpus (list of list of str) – Corpus of documents.
# n_jobs (int) – The number of processes to use for computing bm25.
def main():
    docs = get_list_of_docs('../test_files')
    corpus, doc_titles = get_words(docs)
    bm = BM25(corpus)
    while (True):
        query = input('Query:')
        scores = bm.get_scores(query.split(' '))
        print(list(enumerate(scores)))
        print(get_ranked_docs(doc_titles, scores))


# if __name__ =='__main__':
