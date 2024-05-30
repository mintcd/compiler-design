from parsing.parse import parse
from utils.builders.CFGBuilder import CFGBuilder
from optimization.refactorers import ASTRefactorer, CFGRefactorer
from optimization.local_optimizers import AlgebraicSimplifier
from utils.builders.LivelinessGenerator import LivelinessGenerator
from optimization.RegisterAllocator import RegisterAllocator
from utils.builders.SymbolTableBuilder import SymbolTableBuilder
from code_generation.CodeGenerator import CodeGenerator

import json

data = '''main : function void() {
  a,b,c,d,e,f : integer = 1,2,3,4,5,6;
  a = b + c + d;
  d = -a;
  e = f;
}'''

ast = parse(data)

code = CodeGenerator(ast, 4).generate()

print(code)

