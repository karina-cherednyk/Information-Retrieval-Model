import codecs
import os
import re
import time
from functools import reduce
import json

from collection_creation.collection_info import WordCollectionInfo

non_letters = "`'-’"
word_regex = fr'\b[\w{non_letters}]+\b'


# token which passed regex filter can contain `'-
# they will be removed
def norm_word(word: str) -> str:
    word = word.lower().translate(str.maketrans('', '', non_letters))
    return word

def matches(word):
    return re.search(word_regex,word)


def get_words(documents):
    for docID, document in enumerate(documents):
        docID += 1
        with open(document, 'r', encoding='ISO-8859-1') as reader:
            line = " ".join(reader.readlines())
            for word in re.findall(word_regex, line):
                word = norm_word(word)
                yield word, docID


def documents_size_kb(documents, dir='') -> str:
    # if dir[-1] != '/':
    #     dir += '/'
    if type(documents) == list:
        return f"{(reduce(lambda x, y: x + os.stat(dir + y).st_size, documents, 0) / 1024):0.4f} KB"
    return f"{(os.stat(dir + documents).st_size / 1024):0.4f} KB"


def parse_fb2(line: str) -> str:
    line = re.sub(r'<\?xml(\r|\n|.)*><body[^>]*>', '', line)
    line = re.sub(r'(<[^>]*>|\\n|&quot;)', '', line)
    return line


def parse_line(line, document_name) -> str:
    if document_name.endswith(".fb2"):
        return parse_fb2(line)
    else:
        return line


