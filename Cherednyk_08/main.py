from clusterization import clusterize
from collection_creation.fileIO import create_dictionary, load_collection
from collection_model.reversed_index import get_reversed_index


def main():
    #create_dictionary(get_reversed_index, 'D:/lab8_files/', 'files',encoding='latin-1')
    collection_info = load_collection('files')
    clusters = clusterize(collection_info)
    for cluster in clusters:
       print(cluster)
       print('\n')



if __name__ == '__main__':
    main()