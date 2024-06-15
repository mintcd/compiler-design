'''
  Organized APIs from assistant visitors and helper functions
'''

from utils.structures.AST import AST

from utils.assist_visitors.TypeGetter import TypeGetter
from utils.assist_visitors.ASTInforAssigner import ASTInforAssigner
from utils.assist_visitors.SymbolTableBuilder import SymbolTableBuilder
from utils.assist_visitors.ReferredSymbolGetter import ReferredSymbolGetter
from utils.assist_visitors.CFGInforAssigner import CFGInforAssigner

def get_type(expr, st):
  return TypeGetter(expr, st).get()

def assign_info(struct, log_file = None):
  if isinstance(struct, AST):
    return ASTInforAssigner(struct, log_file).assign() 
  else:
    return CFGInforAssigner(struct, log_file).assign() 

def get_referred_symbols(node, st):
  return ReferredSymbolGetter(node, st).get()

def build_symbol_table(ast, log_file = None):
  return SymbolTableBuilder(ast, log_file).build()
