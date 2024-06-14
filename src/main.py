import sys, os
import argparse
from APIs import *

src_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(src_path)
testcase_dir = os.path.join(project_path, "test/testcases")

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
        src_program = file.read()

    solution_dir = os.path.join(project_path, "test/solutions", args.file_name.split('.')[0])

    if not os.path.exists(solution_dir):
        os.makedirs(solution_dir)

    log_file = os.path.join(solution_dir, f"{args.file_name.split('.')[0]}.log")

    solution = ""

    if args.command == 'lex':
        solution = lex(src_program, log_file)
    elif args.command == 'parse':
        solution = parse(src_program, log_file)
    elif args.command == 'codegen':
        with open(log_file, 'w') as file:
            file.write('')

        num_reg = int(args.num_reg)
        ast = parse(src_program, log_file)
        ast = optimize_ast(ast, log_file)

        st = build_symbol_table(ast, log_file)
        ast = remove_vardecls(ast, log_file)

        cfg = build_cfg(ast, log_file)

        cfg = optimize_cfg(cfg, log_file)
        code = generate_code(cfg, num_reg, st, log_file)

        with open(os.path.join(solution_dir, f"{args.file_name.split('.')[0]}.asm"), 'w') as file:
            file.write(str(code))

        print(f"Find solution in test/solutions/{args.file_name.split('.')[0]}/{args.file_name.split('.')[0]}.asm")
    else:
        print("Usage: with compiler-design/test/testcases/file_name")
        print("python main.py lex file_name")
        print("python main.py parse file_name")
        print("python main.py codegen file_name reg_num")




if __name__ == "__main__":
    main()
