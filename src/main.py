# src/main.py

import sys
from LexicalAnalysis.LexerBuilder import lexer
from Parsing.ParserBuilder import parser


def main():
    # Test data for the lexer
    data = '''
      3 + 4
    '''

    # Give the lexer some input
    lexer.input(data)

    # Tokenize and print each token
    while True:
        tok = lexer.token()
        if not tok:
            break      # No more input
        print(tok)

    ast = parser.parse(data)
    print(ast)


if __name__ == "__main__":
    main()
