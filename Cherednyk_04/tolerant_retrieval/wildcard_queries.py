import re

from tolerant_retrieval.permuterm_trie import PermutermTrie
from tolerant_retrieval.trie import Trie
from collection_creation.fileIO import norm_word, word_regex

def filter_word(word):
    if not re.match(word_regex,word.replace('*','')):
        return ''
    return norm_word(word)

# checks whether word contains every subword in order
def match(word, subwords):
    # iterate over every character
    word_char = 0
    w_len = len(word)
    for sub in subwords:
        if not sub:  # if sub = ''
            continue
        s_len = len(sub)
        if word_char + s_len > w_len:  # word surely wont`t contain this subword
            return False

        while word[word_char:word_char + s_len] != sub:  # search for position of this word
            word_char += 1
            if word_char + s_len - 1 >= w_len:
                return False
        word_char = word_char + s_len  # 1 char after subword end position
    return True


class TrieSearch:
    def __init__(self, vocab: dict):
        self.words = [x for x in vocab.keys()]
        assert('найкращій' in self.words)
        self.trie = Trie(self.words)
        self.reverse_trie = Trie([x[::-1] for x in self.words])

    def is_present(self, word):
        return self.trie.is_present(word)

    def reverse_word(self, word):
        return word[::-1]

    def search(self, word):
        word = filter_word(word)
        if not word:
            return []
        if '*' not in word:
            return [word] if self.is_present(word) else []

        subwords = word.split('*')

        if not subwords[0] and not subwords[-1]:  # word.startswith('*') and word.endswith('*')
            res = self.words

        elif not subwords[0]:  # word.startswith('*')
            res = self.reverse_trie.handle_wc_query(self.reverse_word(subwords[-1]))
            res = set(map(self.reverse_word, res))

        elif not subwords[-1]:  # word.endswith('*')
            res = self.trie.handle_wc_query(subwords[0])

        else:  # word has * in the middle
            start = self.trie.handle_wc_query(subwords[0])
            end = self.reverse_trie.handle_wc_query(self.reverse_word(subwords[-1]))
            end = set(map(self.reverse_word, end))
            res = start & end

        return  sorted((word for word in res if match(word,subwords)))


class PermutermTrieSearch:
    def __init__(self, vocab: dict):
        self.words = [x for x in vocab.keys()]
        self.ptree = PermutermTrie(self.words)

    def is_present(self, word):
        return self.ptree.is_present(word)

    def search(self, word):
        word = filter_word(word)
        if '*' not in word:
            return [word] if self.is_present(word) else []
        subwords = word.split('*')
        if not subwords[0] and not subwords[-1]:  # word.startswith('*') and word.endswith('*')
            res = self.words
        else:
            res = self.ptree.handle_wc_query(subwords[0] +'*'+ subwords[-1])
        return  sorted((word for word in res if match(word,subwords)))


class ThreeGramIndex:
    def __init__(self, vocab: dict):
        self.words = [x for x in vocab.keys()]
        self.postings = dict()
        for word in self.words:
            self.add(word)

    def is_present(self, word):
        return word in self.words

    def add(self, word):
        new_word = '$' + word + '$'
        for i in range(len(new_word) - 2):
            sub = new_word[i:i + 3]
            if sub not in self.postings:
                self.postings[sub] = set()
            self.postings[sub].add(word)

    def search(self, word):
        word = filter_word(word)
        if not word:
            return []
        if '*' not in word:
            return [word] if self.is_present(word) else []

        new_word = word

        if not word.startswith('*'):
            new_word = '$' + new_word
        if not word.endswith('*'):
            new_word = new_word + '$'

        # min length new word $a* or *a$
        # it cannot be found in 3 gram index, so only needs to be filtered at the end
        possible_3grams = list()
        for i in range(len(new_word)-2):
            possible_3grams.append(new_word[i:i+3])
        possible_3grams = list(filter(lambda x: '*' not in x, possible_3grams))
        res = set()
        if possible_3grams:
            res |= self.postings[possible_3grams[0]]
            for sub in possible_3grams[1:]:
                res &= self.postings[sub]

        subwords = word.split('*')
        if subwords[0]:
            res = list(filter(lambda x: x.startswith(subwords[0]), res))
        if subwords[-1]:
            res = list(filter(lambda x: x.endswith(subwords[-1]), res))

        return sorted((word for word in res if match(word,subwords)))
