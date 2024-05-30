from lexing.Lexer import Lexer
from parsing.Parser import Parser

from utils.structures.AST import Program

def parse(data) -> Program:
    lexer = Lexer()
    parser = Parser()

    ast = parser.parse(data)

    return ast