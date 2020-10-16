import codecs
import queue
import re
import pickle
import os
import threading
import time
from functools import reduce


# author: Cherednyk Karina
from vocabulary import parse_fb2, sorted_set_from_list, file_size

words = []
q = queue.Queue()



def get_words():
    global words
    global q
    while q.qsize() > 0:
        file = q.get()
        with codecs.open(file, "r", "utf-8") as reader:
            line = ' '.join(reader.readlines())
            if str(file).endswith(".fb2"):
                line = parse_fb2(line)
            for word in re.findall(r'[^\W_][\w\`\'\-]*', line):
                words.append(word.lower())
            q.task_done()


def set_words(files: list) -> list:
    global q
    for file in files:
        q.put(file)
    for _ in range(4):
        threading.Thread(target=get_words()).start()
    q.join()


def write_data(sset: list, all_words, col_size, dict_path, serialize_path, info_path, time_spent):
    with codecs.open(dict_path, "w", "utf-8") as writer:
        writer.write("\n".join(sset))
    with open(serialize_path, 'wb') as writer:
        pickle.dump(sset, writer)
    with open(info_path, 'w') as writer:
        writer.write(f"Dict size: {os.stat(dict_path).st_size / 1024}KB\n")
        writer.write(f"Book collection size: {col_size / 1024}KB\n")
        writer.write(f"Words in dict: {len(sset)}\n")
        writer.write(f"Words in collection: {all_words}\n")
        print(f"Total time spent: {time_spent:0.4f} seconds")


def create_vocabulary(files, vocab_file='vocab.txt', serialize_file='serialize.txt', info_file='info.txt'):
    global words
    tic = time.perf_counter()
    set_words(files)
    sset = sorted_set_from_list(words)
    toc = time.perf_counter()
    time_spent = toc - tic
    write_data(sset, len(words), file_size(files), vocab_file, serialize_file, info_file, time_spent)


def main():
    files = ["test_files/hp1.fb2", "test_files/hp2.fb2", "test_files/hp3.fb2", "test_files/hp4.fb2",
             "test_files/hp5.fb2", "test_files/hp6.fb2", "test_files/hp7.fb2",
             "test_files/tygrolovy.fb2", "test_files/eneida.fb2", "test_files/misto.fb2"
             ]

    create_vocabulary(files, 'files/vocab.txt', 'files/serialize.txt', 'files/info.txt')


main()
# 4.8sec
