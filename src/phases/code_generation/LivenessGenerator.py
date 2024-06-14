from utils.structures.AST import *
from utils.structures.CFG import *
from utils.visitors import CFGVisitor

from utils.structures.SymbolTable import SymbolTable
from utils.APIs import get_referred_symbols


import json
from typing import Set
import copy

class Data:
  def __init__(self, obj : dict(), ctx = None):
    self.obj = obj

class LivenessGenerator(CFGVisitor):
  '''
    Generate liveness of each symbol incoming and outcoming each statement
    Data:
      obj: a dictionary (stmt_id, symbol, "in" | "out") --> True | False
  '''
  def __init__(self, cfg : CFG, st: SymbolTable, log_file = None):
    self.cfg = cfg
    self.st = st

  def generate(self):
    obj = dict()
    for symbol in self.st.symbols:
      for stmt in self.cfg.get_stmts():
        obj[(stmt.id, symbol.id, "in")] = False
        obj[(stmt.id, symbol.id, "out")] = False

    data = Data(obj)
    loop = 0

    data = LiveIncomingRetriever(self.cfg, self.st, data).generate()

    while True:
      new_data = copy.deepcopy(data)
      new_data = OutInPropagator(self.cfg, self.st, new_data).propagate()
      new_data = SuccessorPropagator(self.cfg, self.st, new_data).propagate()

      if data.obj == new_data.obj:
          break
      loop += 1
      data = new_data
      if loop == 100:
        raise Exception(f"Executed {loop} loop")

    live = dict()

    for stmt in self.cfg.get_stmts():
      live[stmt.id] = set()
      for sym in set(self.st.symbols):
        if data.obj[(stmt.id, sym.id, 'out')] == True:
          live[stmt.id].add(sym)
        for succ_stmt in self.cfg.get_successors(stmt):
          if data.obj[(succ_stmt.id, sym.id, 'in')] == True: 
            live[stmt.id].add(sym)
      live[stmt.id] = list(live[stmt.id])

    return live

class LiveIncomingRetriever(CFGVisitor):
  '''
  AssignStmt(lhs, rhs) ---> live[stmt, x, in] = True if rhs refers to x

  expr ---> live[stmt, x, in] = True if expr refers to x
  '''

  def __init__(self, cfg : CFG, st: SymbolTable, data: Data):
    self.cfg = cfg
    self.st = st
    self.data = data
  
  def generate(self):

    return self.visit(self.cfg, self.data)

  def visitCFG(self, cfg: CFG, data : Data):
    for block in cfg.blocks:
      data = self.visit(block, data)
    return data
  
  def visitBlock(self, cfg : Block, data : Data):
    if cfg.cond is None:
      for stmt in cfg.stmts:
        data = self.visit(stmt, data)
    else:
      for sym in get_referred_symbols(cfg.cond, self.st):
        data.obj[(cfg.cond.id, sym.id, 'in')] = True
    return data
  
  def visitAssignStmt(self, cfg: AssignStmt, data : Data):
    for sym in get_referred_symbols(cfg.rhs, self.st):
      data.obj[(cfg.id, sym.id, 'in')] = True

    return data

class OutInPropagator(CFGVisitor):
  '''live(s, x, in) = live(s, x, out) if s does not refer to x'''
  def __init__(self, cfg : CFG, st: SymbolTable, data : Data):
    self.cfg = cfg
    self.st = st
    self.data = data
  
  def propagate(self):
    return self.visit(self.cfg, self.data)

  def visitCFG(self, cfg: CFG, data : Data):
    for block in cfg.blocks:
      data = self.visit(block, data)
    return data
    
  def visitBlock(self, cfg : Block, data : Data):
    if cfg.cond is not None:
      for sym in set(self.st.symbols) - get_referred_symbols(cfg.cond, self.st):
          data.obj[(cfg.cond.id, sym.id, 'in')] = data.obj[(cfg.cond.id, sym.id, 'out')]
    else:
      for stmt in cfg.stmts:
        data = self.visit(stmt, data)

    return data
      
  def visitAssignStmt(self, cfg: AssignStmt, data : Data):
    for sym in set(self.st.symbols) - get_referred_symbols(cfg, self.st):
        data.obj[(cfg.id, sym.id, 'in')] = data.obj[(cfg.id, sym.id, 'out')]

    return data

class SuccessorPropagator(CFGVisitor):
  '''
  L(p, x, out) = ∨ { L(s, x, in) | s a successor of p }
  '''
  def __init__(self, cfg : CFG, st: SymbolTable, data : Data):
    self.cfg = cfg
    self.st = st
    self.data = data

  def propagate(self):
    return self.visit(self.cfg, self.data)

  def visitCFG(self, cfg: CFG, data : Data):
    for block in cfg.blocks:
      data = self.visitBlock(block, data)
    return data
  
  def visitBlock(self, cfg: Block, data : Data):
    if cfg.cond is not None:
      succ_stmts = self.cfg.get_successors(cfg.cond)
      if len(succ_stmts) == 0: 
        return data
      else:
        for succ_stmt in succ_stmts:
          if data.obj[(succ_stmt.id, sym, 'in')] == True:
            data.obj[(cfg.cond.id, sym, 'out')] = True
    else:
      for stmt in reversed(cfg.stmts):
        data = self.visit(stmt, data)
          
    return data
  
  def visitAssignStmt(self, cfg: AssignStmt, data : Data):
    succ_stmts = self.cfg.get_successors(cfg)
    if len(succ_stmts) > 0:
      for sym in set(self.st.symbols):
        for succ_stmt in succ_stmts:
          if data.obj[(succ_stmt.id, sym.id, 'in')] == True:
            data.obj[(cfg.id, sym.id, 'out')] = True  
    return data
