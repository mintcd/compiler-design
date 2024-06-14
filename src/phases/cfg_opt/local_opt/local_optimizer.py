from utils.visitors import CFGVisitor
from structures.CFG import Block, CFG
from optimization.cfg_refactor.CopyPropagator import CopyPropagator

class LocalOptimizer:
  def __init__(self, cfg):
    self.cfg = cfg

  def optimize(self): 
    cfg = CopyPropagator(self.cfg).propagate()

    return cfg

