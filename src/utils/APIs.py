'''
  Organized APIs from assistant visitors and helper functions
'''

from utils.assist_visitors.TypeGetter import TypeGetter
from utils.assist_visitors.InforAssigner import InforAssigner
from utils.assist_visitors.SymbolTableBuilder import SymbolTableBuilder
from utils.assist_visitors.ReferredSymbolGetter import ReferredSymbolGetter

def get_type(expr, st):
  return TypeGetter(expr, st).get()

def assign_info(ast):
  return InforAssigner(ast).assign()

def get_referred_symbols(node, st):
  return ReferredSymbolGetter(node, st).get()

def build_symbol_table(ast, log_file = None):
  return SymbolTableBuilder(ast, log_file).build()
