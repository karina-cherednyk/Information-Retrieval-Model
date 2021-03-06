import os
import re
import time
from functools import reduce
from converter.postings_converter_zone import to_gamma_str_zone
from xml.dom.minidom import parse

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


def zone(z):
    if z == 'title':
        return 2
    if z == 'author':
        return 4
    return 1

#xml parser
def get_words_zones(documents, encoding):
    for docID, document in enumerate(documents):
        docID += 1
        dom = parse(document)
        title = dom.getElementsByTagName('book-title')[0].firstChild.data
        author = getText(dom.getElementsByTagName('author')[0].childNodes)
        str_file = getText(dom.getElementsByTagName('body')[0].childNodes)

        for word in re.findall(word_regex, author):
            yield zone('author'), norm_word(word), docID
        for word in re.findall(word_regex, title):
            yield zone('title'), norm_word(word), docID
        for word in re.findall(word_regex, str_file):
            yield zone('body'), norm_word(word), docID


def get_words(documents, encoding):
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


def create_dictionary(documents_dir, spimi, res_dir='D:/res/', blocks_dir='D:/blocks/', encoding='utf-8',
                      encode=to_gamma_str_zone):
    start_time = time.perf_counter()
    documents = getListOfFiles(documents_dir)
    spimi(documents, res_dir=res_dir, blocks_dir=blocks_dir, encoding=encoding, encode=encode)
    time_spent = time.perf_counter() - start_time
    with open(res_dir + 'info.txt', 'w') as f:
        f.write(f'time spent: {time_spent:0.4f}\n')
        f.write('collection size: ' + documents_size_kb(documents) + '\n')
        f.write('vocab size: ' + documents_size_kb('vocab.txt', 'D:/res/') + '\n')
        f.write('postings size: ' + documents_size_kb('postings.txt', 'D:/res/') + '\n')
