from collection_model.reversed_index import get_reversed_index
from collection_model import reversed_index,incidence_matrix
from collection_model.incidence_matrix import get_incidence_matrix
from collection_creation.fileIO import create_dictionary, load_collection
from query_parser.boolean_search import boolean_query_parser

def main():
    documents = ["test_files/hp1.fb2", "test_files/hp2.fb2", "test_files/hp3.fb2", "test_files/hp4.fb2",
                 "test_files/hp5.fb2", "test_files/hp6.fb2", "test_files/hp7.fb2",
                 "test_files/tygrolovy.fb2", "test_files/eneida.fb2", "test_files/misto.fb2"
                 ]

    create_dictionary(get_reversed_index, documents, 'files/reversed')
    create_dictionary(get_incidence_matrix, documents,'files/incidence')

    reversed = load_collection('../files/reversed')
    matrix = load_collection('../files/incidence')

    reversed_query = boolean_query_parser(reversed,reversed_index.AND,reversed_index.OR,reversed_index.NOT)
    matrix_query = boolean_query_parser(matrix, incidence_matrix.AND, incidence_matrix.OR, incidence_matrix.NOT)
    queries = ['засмикався','засмикала','not засмикала','засмикався and not засмикала','відьму','чаклуна','відьму AND (засмикався OR чаклуна)']

    for query in queries:
        print('Query: '+query)
        print(reversed_query(query))
        print(matrix_query(query))
        print('____________________')


if __name__ == "__main__":
    main()
