from utils.visitors import ASTVisitor, CFGVisitor
from utils.structures.CFG import CFG, Block
from utils.structures.AST import *
from typing import List

from optimization.ast_refactorer.BinExprUnwrapper import BinExprUnwrapper
from optimization.ast_refactorer.ScopeJustifier import ScopeJustifier
from optimization.ast_refactorer.VarDeclUnwrapper import VarDeclUnwrapper
from optimization.ast_refactorer.ForToWhile import ForToWhile


class ASTRefactorerContext:
  def __init__(self, last_expr : int or None = None):
    self.last_expr : Expr = last_expr
    self.used_sym = 0

    self.current_block: Block or None = None
    self.stmt_id = 0
    self.current_stmt: Stmt or None = None

    self.current_id = [0]

class ASTRefactorerData:
  def __init__(self, obj : Program, ctx : ASTRefactorerContext):
    self.obj = obj
    self.ctx = ctx

class ASTRefactorer(ASTVisitor):

    '''
      1) Assign a unique id to each stmt
      2) Eliminates dead code after Return.
      3) Turns Stmt used in IfStmt, WhileStmt and ForStmt to Block
      4) Turn initiated vardecl to assignstmt with infered type
      5) Turn For to While
      6) Unwrap BinExpr
    '''

    def __init__(self, ast : Program):
        self.ast = ast

    def refactor(self):
        ast = VarDeclUnwrapper(self.ast).unwrap()
        ast = ScopeJustifier(ast).justify()
        ast = ForToWhile(ast).refactor()
        ast = BinExprUnwrapper(ast).refactor()
        return ast

class CFGRefactorer(CFGVisitor):
  '''
  Remove all empty StmtBlock
  '''
  def __init__(self, cfg : CFG):
    self.cfg = cfg

  def refactor(self):
    return self.visit(self.cfg, None)

  def visitCFG(self, cfg : CFG, data):
    for block in cfg.blocks:
      if isinstance(block, AssignStmt) and len(block.stmts) == 0:
        for another_block in cfg.blocks:
          if another_block.id != block.id:
            if another_block.jump.id == block.id:
              another_block.jump = block.next
            if another_block.link.id == block.id:
              another_block.link = block.next
              
            if isinstance(another_block, StmtBlock):
              if another_block.next.id == block.id:
                another_block.next = block.next
            else:
              if another_block.true.id == block.id:
                another_block.true = block.next
              if another_block.false.id == block.id:
                another_block.false = block.next
      cfg.blocks.remove(block)
    return cfg