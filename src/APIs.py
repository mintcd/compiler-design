'''
 Organized APIs from Visitors
'''

from utils.APIs import assign_info, build_symbol_table

# Lexing and Parsing
from phases.lexing.Lexer import Lexer
from phases.parsing.Parser import Parser

# AST optimization
from phases.ast_opt.VarDeclUnwrapper import VarDeclUnwrapper
from phases.ast_opt.ScopeJustifier import ScopeJustifier
from phases.ast_opt.ForToWhile import ForToWhile
from phases.ast_opt.BinExprUnwrapper import BinExprUnwrapper

# CFG Building
from phases.cfg_build.CFGBuilder import CFGBuilder

# CFG Optimization
from phases.cfg_opt.EmptyBlockRemover import EmptyBlockRemover
from phases.cfg_opt.LocalOptimizer import LocalOptimizer
from phases.cfg_opt.GlobalOptimizer import GlobalOptimizer

# Code Generation
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
  ast = BinExprUnwrapper(ast, log_file).unwrap()
  ast = ScopeJustifier(ast, log_file).justify()

  return ast

# def build_symbol_table(ast, log_file = None):
#   return SymbolTableBuilder(ast, log_file).build()

def build_cfg(ast, log_file = None):
  return CFGBuilder(ast, log_file).build()

def optimize_cfg(cfg, st, log_file = None):
  cfg = EmptyBlockRemover(cfg, st, log_file).remove()
  cfg = LocalOptimizer(cfg, st, log_file).optimize()
  cfg = GlobalOptimizer(cfg, st, log_file).optimize()

  return cfg

def generate_code(cfg, num_reg, st, log_file = None):
  return CodeGenerator(cfg, num_reg, st, log_file).generate()

