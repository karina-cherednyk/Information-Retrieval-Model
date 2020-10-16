class PermutermTrie:
    def __init__(self, words:list):
        self.root = dict()
        for word in words:
            self.rotate_and_add(word)

    def is_present(self, word):
        node = self.__find_word_node(word+'$')
        return node and '^' in node

#add all rotations of word$
    def rotate_and_add(self, word):
        rword = word + '$'
        for i in range(0, len(rword)):
            self.__add(rword[i:] + rword[:i], word)

    def __add(self, word, origin):
        node = self.root
        for ch in word:
            if ch not in node:
                node[ch] = dict()
            node = node[ch]
        node['^'] = origin

    def __find_word_node(self, word):
        node = self.root
        for ch in word:
            if ch not in node:
                return []
            node = node[ch]
        return node

    def find(self, word):
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

#param(must contain*) para*m -> para*m$ ->search m$para
    def handle_wc_query(self, word):
        word += '$'
        # position of first element after *
        # at least $ should be present
        pos = word.find('*') + 1
        if pos == 0:
            raise Exception('Word doesn`t contain * ')
        rotated = word[pos:] + word[:pos]
        return self.find(rotated[:-1])
