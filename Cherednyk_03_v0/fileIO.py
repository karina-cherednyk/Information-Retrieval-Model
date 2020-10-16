import codecs
import os
import json
import re
import time
from functools import reduce

from collection_info import WordCollectionInfo

word_regex = r'[^\W_][\w\`\'\-]*'


def get_words(documents):
    for docID, document in enumerate(documents):
        with codecs.open(document, "r", "utf-8") as reader:
            line = ' '.join(reader.readlines())
            line = parse_line(line, document)
            for word in re.findall(word_regex, line):
                yield (word.lower(), docID)


def get_words_pair(documents):
    for docID, document in enumerate(documents):
        with codecs.open(document, "r", "utf-8") as reader:
            line = ' '.join(reader.readlines())
            line = parse_line(line, document)
            prev_word = ""
            for word in re.findall(word_regex, line):
                if prev_word != "":
                    yield (prev_word + " " + word.lower(), docID)
                prev_word = word.lower()


def get_positioned_words(documents):
    for docID, document in enumerate(documents):
        with codecs.open(document, "r", "utf-8") as reader:
            line = ' '.join(reader.readlines())
            line = parse_line(line, document)
            pos = 0
            for word in re.findall(word_regex, line):
                yield (word.lower(), pos, docID)
                pos += 1


def documents_size_kb(documents: list) -> str:
    return f"{(reduce(lambda x, y: x + os.stat(y).st_size, documents, 0) / 1024):0.4f} KB"


def document_size_kb(document: str) -> str:
    return f"{(os.stat(document).st_size / 1024):0.4f} KB"


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


def write_data(collection_info: WordCollectionInfo, vocab_path, dict_path, json_terms_path, json_postings_path,
               info_path, time_spent=False):
    term_vocab = []
    term_vocab_str = ""
    postings = []
    postings_str = ""
    for term_name in collection_info.terms:
        term = collection_info.terms[term_name]
        term_vocab.append({"term": term_name, "frequency": term.freq, "termID": term.id})
        term_vocab_str += f'"term": {term_name}, "frequency": {term.freq}, "termID": {term.id}\n'
        postings.append({"termID": term.id, "postings": term.postings})
        postings_str += f'"termID": {term.id}, "postings": {term.postings}\n'


    with open(json_terms_path, 'w') as writer:
        json.dump(term_vocab, writer)
    with open(json_postings_path, 'w') as writer:
        json.dump(postings, writer)

    with codecs.open(vocab_path, "w", "utf-8") as writer:
        writer.write(term_vocab_str)
    with codecs.open(dict_path, "w", "utf-8") as writer:
        writer.write(postings_str)

    with open(info_path, 'w') as writer:
        writer.write(f"Dict size: {document_size_kb(dict_path)}\n")
        writer.write(f"Book collection size: {documents_size_kb(collection_info.documents)}\n")
        writer.write(f"Words in dict: {collection_info.uniqueWords}\n")
        writer.write(f"Words in collection: {collection_info.allWords}\n")
        writer.write(f"Document enumeration:\n")
        for i, doc in enumerate(collection_info.documents):
            writer.write(f"{i}) {doc}\n")
        if time_spent:
            writer.write(f"Total time spent: {time_spent:0.4f} seconds")


def create_dictionary(get_collection_info, documents, vocab_path='vocab.txt', dict_path='dict.txt',
                      json_terms_path='terms.txt', json_postings_path="postings.txt",
                      info_path='info.txt') -> WordCollectionInfo:
    tic = time.perf_counter()
    collection_info = get_collection_info(documents)
    toc = time.perf_counter()
    time_spent = toc - tic
    write_data(collection_info, vocab_path, dict_path, json_terms_path, json_postings_path, info_path, time_spent)
    return collection_info
