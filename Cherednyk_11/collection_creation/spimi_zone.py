import gc
from contextlib import ExitStack
from queue import PriorityQueue
from pathlib import Path

import psutil as psutil
from sortedcontainers import SortedDict

from collection_creation.fileIO import get_words_zones
from converter.postings_converter_zone import to_gamma_str_zone
from converter.vocab_converter import IndexBuilder


def write_block_zone(counter, m_dict, blocks_dir, encoding):
    """ format key, [freq,[rank,docId]] to key:frequency$rank1:doc1,rank2:doc2... """
    file = 'block' + str(counter) + '.txt'
    with open(blocks_dir + file, 'w', encoding=encoding) as f:
        for term in m_dict:
            f.write(term + ':' + str(m_dict[term][0]) + '$' + ','.join(
                str(zones) + ':' + str(id) for zones, id in m_dict[term][1]) + '\n')


def to_set(line, f_id):
    """ from 'key:frequency$rank1:doc1,rank2:doc2...' string to [term,doc id, freq, [rank,id pairs]] """
    term_end = line.index(':')
    freq_end = line.index('$')
    term = line[: term_end]
    freq = int(line[term_end + 1: freq_end])
    rank_id_pairs = [list(map(int, pair.split(':'))) for pair in line[freq_end + 1:].split(',')]
    return term, f_id, freq, rank_id_pairs


def unite_blocks_zone(counter, blocks_dir, res_dir, encoding, encode=to_gamma_str_zone, block_len=4):
    with ExitStack() as stack:
        files = [stack.enter_context(open(f, 'r', encoding=encoding)) for f in
                 [blocks_dir + 'block' + str(i) + '.txt' for i in range(counter)]]

        queue = PriorityQueue()
        for i, f in enumerate(files):
            queue.put(to_set(f.readline().strip(), i))

        min_term = ''
        min_term_zone_id_pairs = []
        min_term_freq = 0

        with open(res_dir + '/gamma_vocab.txt', 'wb') as gv_file, \
                open(res_dir + '/gamma_postings.txt', 'wb') as gp_file, \
                open(res_dir + '/table.txt', 'wb') as table_file:
            min_term_id = 0
            block = []
            table_builder = IndexBuilder(encode, encoding)

            def save():
                table_block, term_str, posting_bytes = table_builder.add_block(block)
                gv_file.write(term_str)
                gp_file.write(posting_bytes)
                table_file.write(table_block)

            while queue.qsize():
                min_set = queue.get()
                (term, f_id, freq, zone_id_pairs) = min_set

                if term == min_term:
                    if min_term_zone_id_pairs[-1][1] == zone_id_pairs[0][1]:
                        min_term_zone_id_pairs[-1][0] |= zone_id_pairs[0][0]
                        zone_id_pairs = zone_id_pairs[1:]
                    min_term_zone_id_pairs.extend(zone_id_pairs)
                    min_term_freq += freq

                else:
                    if min_term:
                        block.append([min_term, min_term_freq, min_term_zone_id_pairs])
                        if len(block) == block_len:
                            save()
                            block = []
                        min_term_id += 1
                    min_term = term
                    min_term_zone_id_pairs = zone_id_pairs
                    min_term_freq = freq
                next_line = files[f_id].readline().strip()
                if next_line:
                    queue.put(to_set(next_line, f_id))

            block.append([min_term, min_term_freq, min_term_zone_id_pairs])
            save()
            added_zeros, last_byte = table_builder.get_last_byte()
            if last_byte:
                gp_file.write(last_byte)
            table_file.write(added_zeros)


def spimi_zone(documents, res_dir='D:/res/', blocks_dir='D:/blocks/', encoding='utf-8', encode=to_gamma_str_zone,
               block_len=4):
    Path(res_dir).mkdir(parents=True, exist_ok=True)
    Path(blocks_dir).mkdir(parents=True, exist_ok=True)

    counter = 0
    m_dict = dict()  # key-word, value - [frequency, [rank, doc id] ]
    gc.collect()

    for zone, word, docID in get_words_zones(documents, encoding):
        if psutil.virtual_memory().percent > 60:
            write_block_zone(counter, SortedDict(m_dict), blocks_dir, encoding)
            counter += 1
            m_dict.clear()
            gc.collect()

        if word in m_dict:
            m_dict[word][0] += 1
            if m_dict[word][1][-1][1] != docID:
                m_dict[word][1].append([zone, docID])
            else:
                m_dict[word][1][-1][0] |= zone
        else:
            m_dict[word] = [1, [[zone, docID]]]

    if m_dict:
        write_block_zone(counter, SortedDict(m_dict), blocks_dir, encoding)
        counter += 1

    print('unite blocks')
    unite_blocks_zone(counter, blocks_dir, res_dir, encoding, encode, block_len)
    print('after union completed')
