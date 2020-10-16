from collection_info import WordCollectionInfo
from fileIO import create_dictionary
from reversed_index import get_reversed_index, get_biword_index, get_coordinate_index


def main():
    documents = ["test_files/hp1.fb2", "test_files/hp2.fb2", "test_files/hp3.fb2", "test_files/hp4.fb2",
                 "test_files/hp5.fb2", "test_files/hp6.fb2", "test_files/hp7.fb2",
                 "test_files/tygrolovy.fb2", "test_files/eneida.fb2", "test_files/misto.fb2"
                 ]

    #one_word_key =  create_dictionary(get_reversed_index,documents, 'files/vocab1.txt', 'files/dict1.txt', 'files/term1.txt', 'files/postings1.txt', 'files/info1.txt')
    two_words_key = create_dictionary(get_biword_index, documents, 'files/vocab2.txt','files/dict2.txt', 'files/term2.txt', 'files/postings2.txt', 'files/info2.txt')
    #coordinate_value = create_dictionary(get_coordinate_index, documents, 'files/vocab3.txt', 'files/dict3.txt','files/term3.txt', 'files/postings3.txt', 'files/info3.txt')


if __name__ == "__main__":
    main()
