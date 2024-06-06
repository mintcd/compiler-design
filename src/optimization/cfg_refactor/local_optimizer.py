from utils.visitors import CFGVisitor
from utils.structures.CFG import Block, CFG
from optimization.local_optimizers.CopyPropagator import CopyPropagator

class LocalOptimizer:
  def __init__(self, cfg):
    self.cfg = cfg

  def optimize(self): 
    cfg = CopyPropagator(self.cfg).propagate()

    return cfg


# class AlgebraicSimplifier(CFGVisitor):

#   def __init__(self, cfg):
#     self.cfg = cfg
  
#   def simplify(self):
#     return self.visitCFG(self.cfg)

#   def visitCFG(self, cfg : CFG): 
#       for block in cfg.get_blocks():
#         block = self.visit(block)
#       return cfg
    
#   def visitBlock(self, cfg : Block, data = None):
#       for i in range(len(cfg.get_stmts())):
#         cfg.get_stmts()[i] = self.visit(cfg.get_stmts()[i])

#       return cfg

#   def visitAssignStmt(self, cfg : AssignStmt, data = None): 
#     return AssignStmt(cfg.lhs, self.visit(cfg.rhs), cfg.id)

#   def visitBinExpr(self, cfg : BinExpr, param = None):
#       visited_left = self.visit(cfg.left)
#       visited_right = self.visit(cfg.left)
#       if isinstance(visited_left, AtomicLiteral) and isinstance(visited_right, AtomicLiteral):
#         return BinExpr(cfg.op, visited_left, visited_right).calculate()
#       return BinExpr(cfg.op, visited_left, visited_right)
     
#   def visitUnExpr(self, cfg : UnExpr, param = None):
#       visited_val = self.visit(cfg.val)
#       if isinstance(visited_val, AtomicLiteral):
#         return UnExpr(cfg.op, visited_val).calculate
#       return UnExpr(cfg.op, visited_val)

#   def visitId(self, cfg : Id, param = None):
#       return cfg
  
#   def visitAPrrayCell(self, cfg : ArrayCell, param = None):
#       return ArrayCell(cfg.name, [self.visit(expr) for expr in cfg.cell])

#   def visitIntegerLit(self, cfg, param = None):
#       return cfg

#   def visitFloatLit(self, cfg, param = None):
#       return cfg
  
#   def visitStringLit(self, cfg, param = None):
#       return cfg

#   def visitBooleanLit(self, cfg, param = None):
#       return cfg

#   def visitArrayLit(self, cfg : ArrayLit, param = None):
#       return ArrayLit([self.visit(expr) for expr in cfg.explist])

