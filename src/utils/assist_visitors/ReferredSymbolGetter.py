from utils.visitors import CFGVisitor
from utils.structures.CFG import *
from utils.structures.AST import *
from utils.structures.SymbolTable import SymbolTable, Symbol

from typing import Set


class Data:
  def __init__(self, obj : Set[Symbol] = None, ctx = None):
    self.obj = set()
    self.ctx = None

class ReferredSymbolGetter(CFGVisitor):
    '''
      Get the set of symbols referred by an AssignStmt or Expr
    '''

    def __init__(self, node: AssignStmt or Expr, st : SymbolTable):
        self.node = node
        self.st = st
    
    def get(self):
      data = Data()
      return self.visit(self.node, data).obj

    ################################ LITERALS ############################
    def visitArray(self, cfg: Array, data : Data):
        for expr in cfg.val:
          data = self.visit(expr, data)

        return data

    ################################## OTHER EXPRESSIONS ################################

    def visitId(self, cfg: Id, data : Data):
        data.obj.add(self.st.get_symbol(cfg.name, cfg.id))
        return data
    
    def visitArrayCell(self, cfg: ArrayCell, data : Data):
        data.obj.add(self.st.get_symbol(cfg.name, cfg.id))

        for expr in cfg.cell:
          data = self.visit(expr, data)

        return data

    def visitBinExpr(self, cfg: BinExpr, data : Data):
        data = self.visit(cfg.left, data)
        data = self.visit(cfg.right, data)

        return data
 
    def visitUnExpr(self, cfg: UnExpr, data : Data):
        data = self.visit(cfg.val, data)
        return data

    ########################## STATEMENTS ###################################

    def visitAssignStmt(self, cfg : AssignStmt, data : Data):
        data = self.visit(cfg.lhs, data)
        data = self.visit(cfg.rhs, data)
        return data
