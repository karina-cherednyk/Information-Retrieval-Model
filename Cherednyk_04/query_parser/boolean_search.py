import pickle
import re

from tatsu.ast import AST
from tatsu import parse

from collection_creation.collection_info import WordCollectionInfo
from collection_creation.fileIO import word_regex, norm_word, non_letters
from query_parser.phrasal_search import coord_query_parser, biword_query_parser
import collection_model.reversed_index as reversed_index

or_regex = '(or|OR|\|)'
and_regex = '(and|AND|&)'
not_regex = '(not|NOT|!)'

GRAMMAR = f'''

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
        | kphrase
        | bphrase
        | word
        | "(" nested:logical_or ")" 
    ;
    kphrase = /['"]/ word1:my_word lim:number word2:my_word /['"]/ ;
    bphrase = /['"]/ phrase:phrase /['"]/ ;
    or =  /{or_regex}/;
    and = /{and_regex}/;
    not = /{not_regex}/;
    word = /{word_regex}/;
    my_word = /{word_regex}/;
    phrase = /[\w{non_letters} ]+/;
    number = /\/\d+/;
'''


class BooleanQuerySemantics(object):
    def __init__(self, info: WordCollectionInfo, binfo: WordCollectionInfo, cinfo: WordCollectionInfo, AND, OR, NOT):
        self.vocabulary = info.vocabulary
        self.postings = info.postings
        self.doc_count = len(info.documents)
        self.AND = AND
        self.OR = OR
        self.NOT = NOT
        self.coord_p = coord_query_parser(cinfo)
        self.biword_p = biword_query_parser(binfo)

    def word(self, ast):
        ast_norm = norm_word(ast)
        if ast_norm not in self.vocabulary:
            raise Exception('Vocabulary doesn`t contain word ' + ast)
        return self.postings[self.vocabulary[ast_norm]['id']]

    def kphrase(self, ast):
        return self.coord_p(ast.word1, ast.word2, int(ast.lim[1:]))

    def bphrase(self, ast):
        return self.biword_p(ast.phrase)

    def primary(self, ast):
        if 'nested' in ast:
            return ast.nested
        return ast

    def logical_or(self, ast):
        if not isinstance(ast, AST):
            return ast
        elif re.match(or_regex, ast.op):
            return self.OR(ast.left, ast.right)
        else:
            raise Exception('Unknown operator', ast.op)

    def logical_and(self, ast):
        if not isinstance(ast, AST):
            return ast
        elif re.match(and_regex, ast.op):
            return self.AND(ast.left, ast.right)
        else:
            raise Exception('Unknown operator', ast.op)

    def factor(self, ast):
        if not isinstance(ast, AST):
            return ast
        elif re.match(not_regex, ast.op):
            return self.NOT(self.doc_count, ast.operand)
        else:
            raise Exception('Unknown operator', ast.op)


def boolean_query_parser(collection_info, binfo, kinfo, AND=reversed_index.AND, OR=reversed_index.OR,
                         NOT=reversed_index.NOT):
    qs = BooleanQuerySemantics(collection_info, binfo, kinfo, AND, OR, NOT)

    def search(query):
        return parse(GRAMMAR, query, semantics=qs)

    return search
