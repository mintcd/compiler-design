from copy import deepcopy

from utils.visitors import CFGVisitor
from utils.structures.CFG import *
from utils.structures.AST import *
from utils.APIs import assign_info

from utils.helpers import is_atomic

class Data:
  def __init__(self, obj, ctx):
    self.obj = obj
    self.ctx = ctx

class LocalOptimizer:
  def __init__(self, cfg, st, log_file):
    self.cfg = cfg
    self.st = st
    self.log_file = log_file

  def optimize(self):
    while True:
      cfg = deepcopy(self.cfg)
      cfg = ConstantFolder(self.cfg, self.st, self.log_file).fold()
      cfg = CopyPropagator(self.cfg, self.st, self.log_file).propagate()

      if cfg == self.cfg:
        break

      self.cfg = cfg

    cfg = assign_info(self.cfg)

    if self.log_file is not None:
      with open(self.log_file, 'a') as file:
          file.write("Optimized CFG\n")
          file.write(f"{str(cfg)}\n\n")
          file.write("--------------------------------------------------------\n\n")

    return self.cfg

class ConstantFolder(CFGVisitor):
    '''
    Whenever y := [expression of literals], compute it
    '''
    def __init__(self, cfg, st, log_file = None):
      self.cfg = cfg
      self.st = st
      self.log_file = log_file
    
    def fold(self):
      data = Data(self.cfg, None)
      return self.visit(self.cfg, data).obj

    def visitCFG(self, cfg : CFG, data): 
        for block in cfg.blocks:
            data = self.visit(block, data)
        return data
    
    def visitBlock(self, cfg : Block, data):
        if cfg.cond is None:
            for stmt in cfg.stmts:
                data = self.visit(stmt, data)
        else:
            data = self.visit(cfg.cond, data)
        return data

    def visitAssignStmt(self, cfg : AssignStmt, data : Data):
        if isinstance(cfg.rhs, BinExpr):
          if isinstance(cfg.rhs.left, Atomic) and isinstance(cfg.rhs.right, Atomic):
            cfg.rhs = cfg.rhs.calculate()

        if isinstance(cfg.rhs, UnExpr):
          if isinstance(cfg.rhs.val, Atomic):
            cfg.rhs = cfg.rhs.calculate()
        return data

class CopyPropagator(CFGVisitor):
    '''
    For each block:
      If y := x, replace further uses of y by x until the next assignment of y
    '''
    def __init__(self, cfg, st, log_file = None):
      super().__init__(cfg, st, log_file)

    def propagate(self):
      data = Data(self.cfg, None)
      return self.visit(self.cfg, data).obj

    def visitCFG(self, cfg : CFG, data): 
        for block in cfg.blocks:
            data = self.visit(block, data)
        return data
    
    def visitBlock(self, cfg : Block, data):
        if cfg.cond is None:
          for i in range(len(cfg.stmts)):
            # Get a single assignments
            if is_atomic(cfg.stmts[i].rhs):
              # Traverse next statements
              for j in range(i+1, len(cfg.stmts)):
                # Reassign is found, break
                if cfg.stmts[j].lhs == cfg.stmts[i].lhs:
                  break
                # Check for uses
                if isinstance(cfg.stmts[j].rhs, BinExpr):
                  if cfg.stmts[j].rhs.left == cfg.stmts[i].lhs:
                    cfg.stmts[j].rhs.left = cfg.stmts[i].rhs
                  if cfg.stmts[j].rhs.right == cfg.stmts[i].lhs:
                    cfg.stmts[j].rhs.right = cfg.stmts[i].rhs

                if isinstance(cfg.stmts[j], UnExpr):
                  if cfg.stmts[j].rhs.val == cfg.stmts[i].lhs:
                    cfg.stmts[j].rhs.val = cfg.stmts[i].rhs

                if isinstance(cfg.stmts[j], LHS):
                  if cfg.stmts[j] == cfg.stmts[i]:
                    cfg.stmts[j] = cfg.stmts[i]

        return data


