class Trie:
    def __init__(self, words):
        self.root = dict()
        for word in words:
            self.add(word)

    def add(self, word):
        node = self.root
        for ch in word:
            if ch not in node:
                node[ch] = dict()
            node = node[ch]
        node['^'] = word

    def is_present(self, word):
        node = self.__find_word_node(word)
        return node and '^' in node

    def __find_word_node(self,word):
        node = self.root
        for ch in word:
            if ch not in node:
                return list()
            node = node[ch]
        return node

#param -> loof for every word that starts with 'param'
    def handle_wc_query(self, word):
        if '*'  in word:
            raise Exception('Word[::-1] mustn`t contain * ')
        node = self.__find_word_node(word)
        stack = list()
        words = set()
        stack.append(node)
        while len(stack) != 0:
            node = stack.pop()
            for key in node:
                if key == '^':
                    words.add(node[key])
                else:
                    stack.append(node[key])
        return words

