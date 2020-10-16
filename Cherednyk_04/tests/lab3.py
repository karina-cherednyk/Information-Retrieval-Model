import json

from collection_creation.collection_info import WordCollectionInfo
from collection_creation.fileIO import create_dictionary, load_collection, load_nfull_collection
from collection_model.reversed_index import get_reversed_index, get_biword_index, get_coordinate_index
from collection_model.reversed_index import AND as rev_AND, OR as rev_OR, NOT as rev_NOT
from query_parser.boolean_search import boolean_query_parser
from query_parser.phrasal_search import biword_query_parser, coord_query_parser



def main():
    # documents = ["../test_files/hp1.fb2", "../test_files/hp2.fb2", "../test_files/hp3.fb2", "../test_files/hp4.fb2",
    #              "../test_files/hp5.fb2", "../test_files/hp6.fb2", "../test_files/hp7.fb2",
    #              "../test_files/tygrolovy.fb2", "../test_files/eneida.fb2", "../test_files/misto.fb2"
    #              ]

    # create_dictionary(get_reversed_index, documents, 'files/ordinary')
    # create_dictionary(get_biword_index, documents, 'files/biwords')
    # create_dictionary(get_coordinate_index, documents, 'files/coordinate')

    collection_info = load_collection('../files/ordinary')
    biwords_info = load_nfull_collection('../files/biwords')
    kcoord_info = load_nfull_collection('../files/coordinate')
    query_parser = boolean_query_parser(collection_info, biwords_info, kcoord_info)

    queries =  ['прівітдрайв','пишалися','запідозрити','прівітдрайв AND (пишалися OR запідозрити)','"світло /6 ромбовидні"',
                '"Дамблдор уже в міністерстві"','(прівітдрайв AND (пишалися OR запідозрити)) OR "Дамблдор уже в міністерстві"',
                'прівітдрайв AND NOT "світло /6 ромбовидні"']

    print(query_parser('"Дамблдор уже в міністерстві"'))
    # for query in queries:
    #     print('Query: '+query)
    #     print(query_parser(query))
    #     print('____________________')


if __name__ == "__main__":
    main()
