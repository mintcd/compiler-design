from utils.visitors import CFGVisitor
from utils.structures.CFG import CFG, Block

from optimization.ast_refactor.BinExprUnwrapper import BinExprUnwrapper
from optimization.ast_refactor.ScopeJustifier import ScopeJustifier
from optimization.ast_refactor.VarDeclUnwrapper import VarDeclUnwrapper
from optimization.ast_refactor.ForToWhile import ForToWhile
from optimization.ast_refactor.InforAssigner import InforAssigner

class ASTRefactorer:

    '''
      1) Assign a unique id to each stmt
      2) Eliminates dead code after Return.
      3) Turns Stmt used in IfStmt, WhileStmt and ForStmt to Block
      4) Turn initiated vardecl to assignstmt with infered type
      5) Turn For to While
      6) Unwrap BinExpr
    '''

    def __init__(self, ast):
        self.ast = ast

    def refactor(self):
        ast = VarDeclUnwrapper(self.ast).unwrap()
        ast = ScopeJustifier(ast).justify()
        ast = ForToWhile(ast).refactor()
        ast = BinExprUnwrapper(ast).unwrap()
        ast = InforAssigner(ast).assign()
        return ast

class CFGRefactorer(CFGVisitor):
  '''
  Remove empty StmtBlocks
  '''
  def __init__(self, cfg : CFG):
    self.cfg = cfg

  def refactor(self):
    return self.visit(self.cfg, None)

  def visitCFG(self, cfg : CFG, data):
    for block in cfg.blocks:
      if block.cond is None and len(block.stmts) == 0:
        for another_block in cfg.blocks:
          if another_block.id != block.id:
            if another_block.jump == block:
              another_block.jump = block.next
            if another_block.link == block:
              another_block.link = block.next
              
            if another_block.cond is None:
              if another_block.next == block:
                another_block.next = block.next
            else:
              if another_block.true == block:
                another_block.true = block.next
              if another_block.false == block:
                another_block.false = block.next
        cfg.blocks.remove(block)
    return cfg