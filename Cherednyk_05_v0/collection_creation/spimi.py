import json
from contextlib import ExitStack
from queue import PriorityQueue
from pathlib import Path

import psutil as psutil
from sortedcontainers import SortedDict

from collection_creation.fileIO import get_words
from converter.vocab_converter import GammaIndexBuilder


def write_block(counter, m_dict):
    dir = 'blocks/'
    file = 'block' + str(counter) + '.txt'
    with open(dir + file, 'w', encoding='ISO-8859-1') as f:
        for term in m_dict:
            f.write(term + ':' + str(m_dict[term][0]) + '$' + ','.join(str(id) for id in m_dict[term][1]) + '\n')


def to_set(line, f_id):
    term_end = line.index(':')
    freq_end = line.index('$')
    term = line[: term_end]
    freq = int(line[term_end + 1: freq_end])
    ids = [int(id) for id in line[freq_end + 1:].split(',')]

    return term, f_id, freq, ids


def unite_blocks(counter, res_dir='res'):
    dir = 'blocks/'
    block_k = 4

    with ExitStack() as stack:
        files = [stack.enter_context(open(f)) for f in [dir + 'block' + str(i) + '.txt' for i in range(counter)]]

        queue = PriorityQueue()
        for i, f in enumerate(files):
            queue.put(to_set(f.readline().strip(), i))

        min_term = ''
        min_term_ids = []
        min_term_freq = 0

        with open(res_dir + '/vocab.txt', 'w', encoding='ISO-8859-1') as v_file, open(res_dir + '/postings.txt', 'w') as p_file, \
                open(res_dir + '/gamma_vocab.txt', 'w', encoding='ISO-8859-1') as gv_file, open(res_dir + '/gamma_postings.bin',
                                                                         'wb') as gp_file:
            min_term_id = 0
            block = []
            table_builder = GammaIndexBuilder()

            while queue.qsize():
                min_set = queue.get()
                (term, f_id, freq, ids) = min_set

                if term == min_term:
                    if min_term_ids[-1] == ids[0]:
                        ids = ids[1:]
                    min_term_ids.extend(ids)
                    min_term_freq += freq

                else:
                    if min_term:
                        block.append([min_term, min_term_freq, min_term_ids])
                        if len(block) == block_k:
                            term_str, postings_str = table_builder.add_block(block)
                            gv_file.write(term_str)
                            gp_file.write(bytes(postings_str, 'utf-8'))
                            v_file.write(min_term + ',' + str(min_term_id) + ',' + str(min_term_freq) + '\n')
                            p_file.write(','.join(str(id) for id in min_term_ids) + '\n')
                            block = []

                        min_term_id += 1
                    min_term = term
                    min_term_ids = ids
                    min_term_freq = freq
                next_line = files[f_id].readline().strip()
                if next_line:
                    queue.put(to_set(next_line, f_id))

            if min_term:
                block.append([min_term, min_term_freq, min_term_ids])
                term_str, postings_str = table_builder.add_block(block)
                gv_file.write(term_str)
                gp_file.write(bytes(postings_str, 'utf-8'))
                v_file.write(min_term + ',' + str(min_term_id) + ',' + str(min_term_freq) + '\n')
                p_file.write(','.join(str(id) for id in min_term_ids) + '\n')

            with open(res_dir + '/table.json', 'w') as json_file:
                json.dump(table_builder.get_table(), json_file)

# svmem(total=17057050624, available=10177454080, percent=40.3, used=6879596544, free=10177454080)
def spimi(documents, res_dir='res'):
    Path(res_dir).mkdir(parents=True, exist_ok=True)
    Path('blocks').mkdir(parents=True, exist_ok=True)

    counter = 0
    m_dict = dict()
    print('begin')
    try:
        for word, docID in get_words(documents):
            if psutil.virtual_memory().percent > 40:
                write_block(counter, SortedDict(m_dict))
                counter += 1
                m_dict.clear()
                print(psutil.virtual_memory().percent)

            if word in m_dict:
                m_dict[word][0] += 1
                if m_dict[word][1][-1] != docID:
                    m_dict[word][1].append(docID)
            else:
                m_dict[word] = [1, [docID]]

        if m_dict:
            write_block(counter, SortedDict(m_dict))
            counter += 1

        print('unite blocks')
        unite_blocks(counter, res_dir)
        print('after union completed')
    except MemoryError:
        print(psutil.virtual_memory())
