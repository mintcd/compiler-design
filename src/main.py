import sys
import os
import argparse
from lexing.Lexer import Lexer
from parsing.Parser import Parser
from code_generation.CodeGenerator import CodeGenerator
from optimization.refactorers import ASTRefactorer

src_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(src_path)
testcase_dir = os.path.join(project_path, "test/testcases")


def lex(data):
    lexer = Lexer()
    lexer.input(data)

    tokens = [token for token in lexer.Lexer]

    return tokens


def parse(data):
    lexer = Lexer()
    parser = Parser()

    ast = ASTRefactorer(parser.parse(data)).refactor()

    return ast

def gen(data, num_reg, log_file):
    lexer = Lexer()
    parser = Parser()

    ast = parser.parse(data)
    
    with open(log_file, 'w') as file:
        file.write("Original AST\n")
        file.write(f"{str(ast)}\n")
        file.write("--------------------------------------------------------\n\n")

    code = CodeGenerator(ast, num_reg, log_file).generate()

    return code


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', required=True)

    lex_parser = subparsers.add_parser('lex')
    lex_parser.add_argument('file_name')

    parse_parser = subparsers.add_parser('parse')
    parse_parser.add_argument('file_name')

    gen_parser = subparsers.add_parser('codegen')
    gen_parser.add_argument('file_name')
    gen_parser.add_argument('num_reg')

    args = parser.parse_args()

    with open(os.path.join(testcase_dir, args.file_name), 'r') as file:
        data = file.read()

    solution_dir = os.path.join(project_path, "test/solutions", args.file_name.split('.')[0])

    if not os.path.exists(solution_dir):
        os.makedirs(solution_dir)

    log_file = os.path.join(solution_dir, f"{args.file_name.split('.')[0]}.log")

    solution = ""

    if args.command == 'lex':
        solution = lex(data)
    elif args.command == 'parse':
        solution = parse(data)
    elif args.command == 'codegen':
        num_reg = args.num_reg
        solution = gen(data, int(num_reg), log_file)
    else:
        print("Usage: with compiler-design/test/testcases/file_name")
        print("python main.py lex file_name")
        print("python main.py parse file_name")
        print("python main.py codegen file_name reg_num")

    with open(os.path.join(solution_dir, f"{args.file_name.split('.')[0]}.asm"), 'w') as file:
        file.write(str(solution))

    print(f"Find solution in test/solutions/{args.file_name.split('.')[0]}/{args.file_name.split('.')[0]}.asm")


if __name__ == "__main__":
    main()
