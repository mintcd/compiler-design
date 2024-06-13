from utils.visitors import CFGVisitor
from utils.structures.AST import *
from utils.structures.CFG import Block, CFG


class EmptyBlockRemover(CFGVisitor):

  def __init__(self, cfg : CFG):
    self.cfg = cfg

  def remove(self):
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