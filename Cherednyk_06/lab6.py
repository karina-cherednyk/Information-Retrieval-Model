from collection_creation.fileIO import create_dictionary, documents_size_kb
from converter.vocab_converter import Index


def main():
   create_dictionary('../test_files/', blocks_dir='D:/blocks6/', res_dir='D:/res6/', encoding='cp1251')
   i = Index(dir='D:/res6/', encoding='cp1251')
   while True:
    print('your query:')
    print(i.get_postings(input()))



if __name__ == '__main__':
    main()
