from utils.visitors import CFGVisitor

from utils.structures.AST import *
from utils.structures.CFG import *
from utils.structures.SymbolTable import SymbolTable

class Context:
  def __init__(self, current_block = None):
    self.current_block = current_block

class Data:
  def __init__(self, obj, ctx: Context):
    self.obj = obj
    self.ctx = ctx

class CFGInforAssigner(CFGVisitor):
    '''
      Assign a unique Id to each Stmt and its parent block
    
    '''
    def __init__(self, cfg: CFG, log_file = None):
      self.cfg = cfg
      self.log_file = log_file

    def assign(self):
      data = Data(self.cfg, Context())
      return self.visit(self.cfg, data).obj

    def visitCFG(self, cfg : CFG, data): 
        for block in cfg.blocks:
            data = self.visit(block, data)
        return data
    
    def visitBlock(self, cfg : Block, data):
        if cfg.cond is None:
            data.ctx.current_block = cfg
            for stmt in cfg.stmts:
                data = self.visit(stmt, data)
        else:
            cfg.cond.block = cfg
        return data

    def visitAssignStmt(self, cfg : AssignStmt, data : Data):
        cfg.block = data.ctx.current_block
        return data