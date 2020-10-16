import codecs
import json
import os
import re
import time
from functools import reduce

from collection_creation.collection_info import WordCollectionInfo

non_letters = "`'\-’"
word_regex = fr'\b[\w{non_letters}]+\b'


def norm_word(word: str) -> str:
    word = word.lower().translate(str.maketrans('', '', non_letters))
    return word


def matches(word):
    return re.search(word_regex, word)


from xml.dom.minidom import parse


def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
        else:
            nodelist.extend(node.childNodes)
    return ''.join(rc)


def get_words(documents, encoding='utf-8'):
    for docID, document in enumerate(documents):
        docID += 1
        if document.endswith('fb2'):
            dom = parse(document)
            str_file = getText(dom.getElementsByTagName('body')[0].childNodes)
        else:
            with open(document, 'r', encoding=encoding) as reader:
                str_file = ''.join(reader.readlines())

        for word in re.findall(word_regex, str_file):
            word = norm_word(word)
            yield word, docID


def documents_size_kb(documents, dir='') -> str:
    if type(documents) == list:
        return f"{(reduce(lambda x, y: x + os.stat(dir + y).st_size, documents, 0) / 1024):0.4f} KB"
    return f"{(os.stat(dir + documents).st_size / 1024):0.4f} KB"


def getListOfFiles(dir):
    listOfFile = os.listdir(dir)
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(dir, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)

    return allFiles


def getListOfFiles(dir):
    listOfFile = os.listdir(dir)
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(dir, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)

    return allFiles


def create_dictionary(get_collection_info, documents, dir='', vocab_txt='vocab.txt', postings_txt='postings.txt',
                      vocab_json='vocab.json', postings_json='postings.json', documents_json='documents.json',
                      info_txt='info.txt', encoding='utf-8'):
    # create vocabulary with unique words, postings
    # calculate how much time it takes to create collection and write it to files
    start_time = time.perf_counter()
    if isinstance(documents, str):
        documents = getListOfFiles(documents)
    collection_info = get_collection_info(documents,encoding)

    if dir:
        os.makedirs(dir, exist_ok=True)
        dir += '/'

    # write vocabulary and postings in files
    with codecs.open(dir + vocab_txt, 'w', encoding) as writer:
        writer.write(collection_info.stringify_vocab())
    with codecs.open(dir + postings_txt, 'w', encoding) as writer:
        writer.write(collection_info.stringify_postings())

    # serialize collection
    with open(dir + vocab_json, 'w') as writer:
        json.dump(collection_info.vocabulary, writer)
    with open(dir + postings_json, 'w') as writer:
        json.dump(collection_info.postings, writer)
    with open(dir + documents_json, 'w') as writer:
        json.dump(collection_info.documents, writer)

    stop_time = time.perf_counter()
    time_spent = stop_time - start_time

    # write additional inforamtion
    with open(dir + info_txt, 'w') as writer:
        writer.write(f"Dict size: {documents_size_kb(vocab_txt, dir)}\n")
        writer.write(f"Book collection size: {documents_size_kb(collection_info.documents)}\n")
        writer.write(f"Words in dict: {collection_info.uniqueWords}\n")
        writer.write(f"Words in collection: {collection_info.allWords}\n")
        writer.write(f"Total time spent: {time_spent:0.4f} seconds\n")
        writer.write(f"Document enumeration:\n")
        for i, doc in enumerate(collection_info.documents):
            writer.write(f"{i}) {doc}\n")


def load_collection(dir, vocab_json='vocab.json', postings_json='postings.json', documents_json='documents.json'):
    with open(dir + '/' + vocab_json, 'r') as vocab_file:
        vocabulary = json.load(vocab_file)
    with open(dir + '/' + postings_json, 'r') as postings_file:
        postings = json.load(postings_file)
    with open(dir + '/' + documents_json, 'r') as vocab_file:
        documents = json.load(vocab_file)
    return WordCollectionInfo(vocabulary, postings, documents)
