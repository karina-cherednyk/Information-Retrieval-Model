import pickle

from tatsu.ast import AST
from tatsu import parse
from fileIO import word_regex


from collection_info import WordCollectionInfo

GRAMMAR = f'''
    @@grammar::Calc

    start = logical_or $ ;

    logical_or
        = 
        | left:logical_and op:or  right:logical_or 
        | logical_and
    ;
    logical_and
        =
        | left:factor op:and right:logical_and 
        | factor
    ;
    factor
       =
        | op:not operand:factor
        | primary
    ;
    primary
        =
        | word
        | "(" logical_or:logical_or ")" 
    ;
    or = "or";
    and = "and";
    not = "not";
    word = {word_regex} ;
'''


class QuerySemantics(object):
    def __init__(self, info: WordCollectionInfo, AND, OR, NOT):
        self.collection = info.collection
        self.doc_count = len(info.documents)
        self.AND = AND
        self.OR = OR
        self.NOT = NOT

    def word(self, ast):
        return self.collection[ast] if type(ast) == str else ast

    def logical_or(self, ast):
        if not isinstance(ast, AST):
            return ast
        elif ast.op == 'or':
            return self.OR(ast.left, ast.right)
        else:
            raise Exception('Unknown operator', ast.op)

    def logical_and(self, ast):
        if not isinstance(ast, AST):
            return ast
        elif ast.op == 'and':
            return self.AND(ast.left, ast.right)
        else:
            raise Exception('Unknown operator', ast.op)

    def factor(self, ast):
        if not isinstance(ast, AST):
            return ast
        elif ast.op == 'not':
            return self.NOT(self.doc_count,ast.operand)
        else:
            raise Exception('Unknown operator', ast.op)




#for case1:
from reversed_index import AND, OR, NOT
#for case2:
# from incidence_matrix import AND, OR, NOT

def main():

    one_word_term_file = 'files/term1.txt'
    two_words_term_file = 'files/term2.txt'
    one_word_postings_file = 'files/term1.txt'
    two_words_postings_file = 'files/term2.txt'

    with open(ser_file, 'rb') as file:
        info = pickle.load(file)
        qs = QuerySemantics(info, AND, OR, NOT)
        # print(parse(GRAMMAR, 'засмикався', semantics=qs))
        # print(parse(GRAMMAR, 'засмикала', semantics=qs))
        # print(parse(GRAMMAR, 'not засмикала', semantics=qs))
        # print(parse(GRAMMAR, 'засмикався and not засмикала', semantics=qs))
        # print(parse(GRAMMAR, 'засмикався or not засмикала', semantics=qs))


if __name__ == "__main__":
    main()
