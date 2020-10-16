import codecs
import os
import re
import time
from functools import reduce
import json

from collection_info import WordCollectionInfo

non_letters = "`'-’"
word_regex = fr'\b[\w{non_letters}]+\b'

function_words = [
    "без", "біля", "в", "у", "від", "од", "для",
    "до", "з", "зі", "із", "зза", "ізза", "за",
    "к", "на", "о", "об", "під", "по", "при", "про",
    "адже", "аніж", "втім", "зате", "ніж", "отже", "отож",
    "щоб", "якби", "якщо", "хоч", "хоча", "аж", "таки",
    "чи", "ба", "ой", "ну", "би", "б", "ж", "най",
    "от", "це", "ось", "оце", "то", "ота", "он", "ген",
    "так", "еге", "ж", "атож", "аякже", "авжеж",
    "чи", "аби", "що", "би", "б", "же", "як"
]
function_words.sort()


def is_function_word(word) -> bool:
    low = 0
    high = len(function_words) - 1
    while low <= high:
        mid = low + (high - low) // 2;
        if function_words[mid] == word:
            return True
        elif function_words[mid] < word:
            low = mid + 1
        else:
            high = mid - 1

    return False


# token which passed regex filter can contain `'-
# they will be removed
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


def get_words_pair(documents):
    for docID, document in enumerate(documents):
        with codecs.open(document, 'r', 'utf-8') as reader:
            line = " ".join(reader.readlines())
            line = parse_line(line, document)
            words = re.findall(word_regex, line)
            prev_word = norm_word(words[0])
            for word in words[1:]:
                word = norm_word(word)
                if is_function_word(word):
                    continue

                yield prev_word + ' ' + word, docID
                prev_word = word


def get_positioned_words(documents):
    for docID, document in enumerate(documents):
        with codecs.open(document, 'r', 'utf-8') as reader:
            line = " ".join(reader.readlines())
            line = parse_line(line, document)
            pos = 0
            for word in re.findall(word_regex, line):
                word = norm_word(word)
                yield (word, pos, docID)
                pos += 1


def documents_size_kb(documents, dir='') -> str:
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


def load_collection(dir, vocab_json='vocab.json', postings_json='postings.json', documents_json='documents.json'):
    with open(dir + '/' + vocab_json, 'r') as vocab_file:
        vocabulary = json.load(vocab_file)
    with open(dir + '/' + postings_json, 'r') as postings_file:
        postings = json.load(postings_file)
    with open(dir + '/' + documents_json, 'r') as vocab_file:
        documents = json.load(vocab_file)
    return WordCollectionInfo(vocabulary, postings, documents)


def load_nfull_collection(dir, vocab_json='vocab.json', postings_json='postings.json'):
    with open(dir + '/' + vocab_json, 'r') as vocab_file:
        vocabulary = json.load(vocab_file)
    with open(dir + '/' + postings_json, 'r') as postings_file:
        postings = json.load(postings_file)
    return WordCollectionInfo(vocabulary, postings)


def create_dictionary(get_collection_info, documents, dir='', vocab_txt='vocab.txt', postings_txt='postings.txt',
                      vocab_json='vocab.json', postings_json='postings.json', documents_json='documents.json',
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
