from utils.visitors import CFGVisitor
from utils.structures.AST import *
from utils.structures.CFG import Block, CFG

from utils.APIs import assign_info

class EmptyBlockRemover(CFGVisitor):

  def __init__(self, cfg : CFG, st, log_file = None):
    super().__init__(cfg, st, log_file)

  def remove(self):
    cfg = self.visit(self.cfg, None)
    cfg = assign_info(cfg)

    if self.log_file is not None:
      with open(self.log_file, 'a') as file:
          file.write("CFG after removing empty blocks\n")
          file.write(f"{str(cfg)}\n\n")
          file.write("--------------------------------------------------------\n\n")

    return cfg

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