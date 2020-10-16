from collection_creation.fileIO import create_dictionary
from collection_creation.spimi_zone import spimi_zone
from converter.postings_converter_zone import from_gamma_str_zone
from converter.vocab_converter import Index

#for lab 11: xml parser used in collection_creation.fileIO module
def main():
    # create_dictionary('../test_files/', spimi=spimi_zone, blocks_dir='D:/blocks7/', res_dir='D:/res7/',
    #                   encoding='cp1251')
    i = Index(dir='D:/res7/', encoding='cp1251', decode=from_gamma_str_zone)
    print('Your query:')

    while True:
        # show pairs [rank,doc id] for word
        # print(i.get_postings(input()))
        # show sorted by rank doc ids
        res = i.zone_query(input())
        for doc in res:
            print(str(doc[0])+': '+str(doc[1])+'\n')


if __name__ == '__main__':
    main()
