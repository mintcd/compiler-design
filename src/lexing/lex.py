from lexing.Lexer import Lexer

def lex(data):
    lexer = Lexer()
    lexer.input(data)

    tokens = [token for token in lexer.Lexer]

    return tokens