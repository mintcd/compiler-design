'''
 Organized APIs from Visitors
'''

from utils.assist_visitors.SymbolTableBuilder import SymbolTableBuilder
from utils.APIs import assign_info

from phases.lexing.Lexer import Lexer
from phases.parsing.Parser import Parser

from phases.ast_opt.VarDeclUnwrapper import VarDeclUnwrapper
from phases.ast_opt.ScopeJustifier import ScopeJustifier
from phases.ast_opt.ForToWhile import ForToWhile
from phases.ast_opt.BinExprUnwrapper import BinExprUnwrapper
from phases.ast_opt.VarDeclRemover import VarDeclRemover

from phases.cfg_build.CFGBuilder import CFGBuilder

from phases.code_generation.CodeGenerator import CodeGenerator


def lex(string, log_file = None):
    lexer = Lexer()
    lexer.input(string)

    tokens = [token for token in lexer.Lexer]

    return tokens

def parse(string, log_file = None):
    lexer = Lexer()
    parser = Parser()

    ast = parser.parse(string)

    return ast

def optimize_ast(ast, log_file = None):
  ast = assign_info(ast)
  ast = VarDeclUnwrapper(ast, log_file).unwrap()
  ast = ForToWhile(ast, log_file).refactor()
  ast = ScopeJustifier(ast, log_file).justify()
  ast = BinExprUnwrapper(ast, log_file).unwrap()

  return ast

def remove_vardecls(ast, log_file = None):
  return VarDeclRemover(ast, log_file).remove()

def build_symbol_table(ast, log_file = None):
  return SymbolTableBuilder(ast, log_file).build()

def build_cfg(ast, log_file = None):
  return CFGBuilder(ast, log_file).build()

def optimize_cfg(cfg, log_file = None):
  return cfg

def generate_code(cfg, num_reg, st, log_file = None):
  return CodeGenerator(cfg, num_reg, st, log_file).generate()

