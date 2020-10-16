from collection_creation.fileIO import create_dictionary

# unite_blocks(counter, blocks_dir, res_dir, encoding, encode, block_len)
from collection_creation.spimi import unite_blocks


def main():
    create_dictionary('D:/lab8_files/', blocks_dir='D:/blocks01/', res_dir='D:/res01/', encoding='latin-1')
    print('union completed')

if __name__ == '__main__':
    main()
