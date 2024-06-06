from parsing.parse import parse
from utils.builders.CFGBuilder import CFGBuilder
from optimization.refactorers import ASTRefactorer, CFGRefactorer

from code_generation.CodeGenerator import CodeGenerator

import json

data = '''
main : function void() {
  x,y,z : integer;
  x = y;
  y = z;
  z = x;
}'''

ast = parse(data)

# st = SymbolTableBuilder(ast).build()

# print(23, st)

code = CodeGenerator(ast, 4, 'log.log').generate()

# print(code)

