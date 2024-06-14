from utils.visitors import CFGVisitor
from utils.structures.AST import *
from structures.CFG import StmtBlock, CFG


class Context:
  def __init__(self, single_assigns = None):
    self.single_assigns: List[AssignStmt] = single_assigns if single_assigns is not None else []
    self.propagated_expr = None

class Data: 
  def __init__(self, obj: CFG, ctx : Context):
    self.obj =obj
    self.ctx: Context = ctx

class ConstantFolder(CFGVisitor): 
  '''
    Whenever y := [expression of literals], compute it
  '''
  def __init__(self, cfg):
      self.cfg = cfg
  
  def propagate(self):
    return self.visit(self.cfg, Data(self.cfg, Context())).obj

  def visitCFG(self, cfg : CFG, data : Data): 
      for block in cfg.blocks: 
        if isinstance(block, StmtBlock):
          block = self.visit(block, data)
      return data
    
  def visitStmtBlock(self, cfg : StmtBlock, data : Data):
      data.ctx.single_assign_num = []
      for stmt in cfg.stmts:
        self.visit(stmt, data)
      return cfg

  def visitAssignStmt(self, cfg : AssignStmt, data : Data):
    # If it is a single assignment
    if isinstance(cfg.lhs, LHS) and isinstance(cfg.rhs, LHS):
      data.ctx.single_assigns.append(cfg)
    else:
      data = self.visit(cfg.rhs, data)

    return data

  def visitBinExpr(self, cfg : BinExpr, data : Data):
      # data.ctx.propagated_expr = None
      data = self.visit(cfg.left, data)
      if data.ctx.propagated_expr is not None:
        cfg.left = data.ctx.propagated_expr

      data.ctx.propagated_expr = None
      data = self.visit(cfg.right, data)
      if data.ctx.propagated_expr is not None:
        cfg.right = data.ctx.propagated_expr
     
  def visitUnExpr(self, cfg : UnExpr, data : Data):
      data.ctx.propagated_expr = None
      data = self.visit(cfg.val, data)
      if data.ctx.propagated_expr is not None:
        cfg.val = data.ctx.propagated_expr

  def visitId(self, cfg : Id, data : Data):
    # If Id in the lhs of single assignment
    for assign in data.ctx.single_assigns:
      if cfg.name == assign.lhs.name:
        data.ctx.propagated_expr = assign.rhs
        break
    return data
        
  # def visitArrayCell(self, cfg : ArrayCell, data : Data):

  #     for expr in cfg.cell:

  #       data = self.visit(expr, data)
      
  def visitIntegerLit(self, cfg, data : Data):
      return data

  def visitFloatLit(self, cfg, data : Data):
      return data
  
  def visitStringLit(self, cfg, data : Data):
      return data

  def visitBooleanLit(self, cfg, data : Data):
      return data

  # def visitArrayLit(self, cfg : ArrayLit, data : Data):
  #     return ArrayLit([self.visit(expr) for expr in cfg.explist])