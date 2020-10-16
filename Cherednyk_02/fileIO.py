import codecs
import os
import pickle
import re
import time
from functools import reduce

from collection_info import WordCollectionInfo

non_letters = "`'-’"
word_regex = fr'\b[\w{non_letters}]+\b'


def norm_word(word: str) -> str:
    word = word.lower().translate(str.maketrans('', '', non_letters))
    return word


def get_words(documents):
    for docID, document in enumerate(documents):
        with codecs.open(document, 'r', 'utf-8') as reader:
            line = " ".join(reader.readlines())
            line = parse_line(line, document)
            for word in re.findall(word_regex, line):
                word = norm_word(word)
                yield word, docID


def documents_size_kb(documents, dir='') -> str:
    if type(documents) == list:
        return f"{(reduce(lambda x, y: x + os.stat(dir + y).st_size, documents, 0) / 1024):0.4f} KB"
    return f"{(os.stat(dir + documents).st_size / 1024):0.4f} KB"


def parse_fb2(line: str) -> str:
    line = re.sub(r'<\?xml(\r|\n|.)*><body[^>]*>', '', line)
    line = re.sub(r'<[^>]*>', '', line)
    line = re.sub(r'\\n', '', line)
    return line


def parse_line(line, document_name) -> str:
    if document_name.endswith(".fb2"):
        return parse_fb2(line)
    else:
        return line


def load_collection(dir, vocab_json='vocabSER.txt', postings_json='postingsSER.txt', documents_json='documentsSER.txt'):
    with open(dir + '/' + vocab_json, 'rb') as vocab_file:
        vocabulary = pickle.load(vocab_file)
    with open(dir + '/' + postings_json, 'rb') as postings_file:
        postings = pickle.load(postings_file)
    with open(dir + '/' + documents_json, 'rb') as vocab_file:
        documents = pickle.load(vocab_file)
    return WordCollectionInfo(vocabulary, postings, documents)


def create_dictionary(get_collection_info: WordCollectionInfo, documents, dir='', vocab_txt='vocab.txt',
                      postings_txt='postings.txt',
                      vocab_ser='vocabSER.txt', postings_ser='postingsSER.txt', documents_ser='documentsSER.txt',
                      info_txt='info.txt'):
    # create vocabulary with unique words, postings
    # calculate how much time it takes to create collection and write it to files
    start_time = time.perf_counter()
    collection_info = get_collection_info(documents)

    if dir:
        os.makedirs(dir, exist_ok=True)
        dir += '/'

    # write vocabulary and postings in files
    with codecs.open(dir + vocab_txt, 'w', 'utf-8') as writer:
        writer.write(collection_info.stringify_vocab())
    with codecs.open(dir + postings_txt, 'w', 'utf-8') as writer:
        writer.write(collection_info.stringify_postings())

    # serialize collection
    with open(dir + vocab_ser, 'wb') as writer:
        pickle.dump(collection_info.vocabulary, writer)
    with open(dir + postings_ser, 'wb') as writer:
        pickle.dump(collection_info.postings, writer)
    with open(dir + documents_ser, 'wb') as writer:
        pickle.dump(collection_info.documents, writer)

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
