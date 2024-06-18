from utils.structures.CFG import *
from utils.structures.AST import *
from utils.structures.SymbolTable import SymbolTable

from utils.APIs import generate_liveness, get_referred_symbols

from utils.visitors import CFGVisitor, Data

class GlobalOptimizer(CFGVisitor):
  '''
    Remove statements containing dead symbols
  '''
  def __init__(self, cfg: CFG, st: SymbolTable, log_file = None):
    self.cfg = generate_liveness(cfg, st, log_file)
    self.st = st
    self.log_file = log_file

    self.dead_symbols = {symbol for symbol in self.st.symbols if symbol.dead == True}
  
  def optimize(self):
    data = Data(self.cfg, None)
    cfg = self.visit(self.cfg, data).obj

    if self.log_file is not None:
      with open(self.log_file, 'a') as file:
        file.write("Optimized CFG\n")
        file.write("{\n\t")
        file.write(str(cfg) + "\n")
        file.write("----------------------------------------\n\n")

    return cfg
  
  def visitCFG(self, cfg : CFG, data): 
      for block in cfg.blocks:
          data = self.visit(block, data)
      return data
  
  def visitBlock(self, cfg : Block, data):
    if cfg.cond is None:
      for stmt in cfg.stmts:
        refer_symbols = get_referred_symbols(stmt, self.st)
        if len(self.dead_symbols.intersection(refer_symbols)) > 0:
          cfg.stmts.remove(stmt)
          
    return data