from utils.structures.AST import *
from utils.structures.CFG import *
from utils.visitor_pattern import Data
from utils.visitors import CFGVisitor


import json
from typing import Set
import copy

class LiveGenContext:
  def __init__(self, refered_syms: Set[str] or None = None):
    self.refered_syms = refered_syms if refered_syms is not None else set()

class LiveGenData(Data):
  def __init__(self, obj : dict(), ctx : LiveGenContext):
    self.obj = obj
    self.ctx = ctx

class LivenessGenerator(CFGVisitor):
  '''
    Generate liveness of each symbol incoming and outcoming each statement
    Data:
      obj: a dictionary (stmt_id, symbol, "in" | "out") --> True | False
  '''
  def __init__(self, cfg : CFG, log_file = None):
    self.cfg = cfg
    self.symbols = cfg.get_symbols()
    
  def generate(self):
    obj = dict()
    for sym in self.cfg.get_symbols():
      for stmt in self.cfg.get_stmts():
        obj[(stmt.id, sym, "in")] = False
        obj[(stmt.id, sym, "out")] = False
    
    ctx = LiveGenContext()

    data = LiveGenData(obj , ctx)
    loop = 0

    data = LiveIncomingRetriever(self.cfg, data).generate()

    # written_data = { str(key) : data.obj[key] for key in sorted(list(data.obj.keys()))}
    # json.dump(written_data, open("live.json", "w"), indent=2)

    # new_data = copy.deepcopy(data)
    

    # new_data = SuccessorPropagator(self.cfg, new_data).propagate()

    # if new_data.obj != data.obj:
    #   print(359, new_data.obj.keys() == data.obj.keys())
    #   for key in list(new_data.obj.keys()):
    #     if new_data.obj[key] != data.obj[key]:
    #       print(360, key, new_data.obj[key], data.obj[key])

    # written_data = { str(key) : data.obj[key] for key in sorted(list(new_data.obj.keys()))}
    # json.dump(written_data, open("live.json", "a"), indent=2)

    while True:
      new_data = copy.deepcopy(data)
      new_data = OutInPropagator(self.cfg, new_data).propagate()
      new_data = SuccessorPropagator(self.cfg, new_data).propagate()

      if data.obj == new_data.obj:
          break
      loop += 1
      data = new_data
      if loop == 100:
        raise Exception(f"Executed {loop} loop")



    live = dict()

    for stmt in self.cfg.get_stmts():
      live[stmt.id] = set()
      for sym in self.cfg.get_symbols():
        if data.obj[(stmt.id, sym, 'out')] == True:
          live[stmt.id].add(sym)
        for succ_stmt in self.cfg.get_successors(stmt):
          if data.obj[(succ_stmt.id, sym, 'in')] == True: 
            live[stmt.id].add(sym)
      live[stmt.id] = list(live[stmt.id])

    return live

class LiveIncomingRetriever(CFGVisitor):
  '''
  AssignStmt(lhs, rhs) ---> live[stmt, x, in] = True if rhs refers to x

  expr ---> live[stmt, x, in] = True if expr refers to x
  '''

  def __init__(self, cfg : CFG, data : LiveGenData):
    self.cfg = cfg
    self.data = data
    self.symbols = self.cfg.get_symbols()
  
  def generate(self):
    return self.visit(self.cfg, self.data)

  def visitCFG(self, cfg: CFG, data : LiveGenData):
    for block in cfg.blocks:
      data = self.visit(block, data)
    return data
  
  def visitBlock(self, cfg : Block, data : LiveGenData):
    if cfg.cond is not None:
      if hasattr(cfg.cond, 'name'):
        data.obj[(cfg.cond.id, cfg.cond.name, 'in')] = True
    else:
      for stmt in cfg.stmts:
        data = self.visit(stmt, data)
    return data
  
  def visitAssignStmt(self, cfg: AssignStmt, data : LiveGenData):
    data.ctx.refered_syms = set()
    data = self.visit(cfg.rhs, data)

    for sym in data.ctx.refered_syms:
      data.obj[(cfg.id, sym, 'in')] = True
    return data

  def visitBinExpr(self, cfg : BinExpr, data : LiveGenData):
    if hasattr(cfg.left, 'name'):
      data.ctx.refered_syms.add(cfg.left.name)

    if hasattr(cfg.right, 'name'):
      data.ctx.refered_syms.add(cfg.right.name)

    return data

  def visitUnExpr(self, cfg : Expr, data : LiveGenData):
    if hasattr(cfg.val, 'name'):
      data.ctx.refered_syms.add(cfg.val.name)

    return data
  
  def visitId(self, cfg : Id, data : LiveGenData):
    data.ctx.refered_syms.add(cfg.name)

    return data

  def visitArrayCell(self, cfg : ArrayCell, data : LiveGenData):
    data.ctx.refered_syms.add(cfg.name)

    for expr in cfg.cell:
      data = self.visit(expr, data)

    return data

  def visitArrayLit(self, arraylit : ArrayLit, data : LiveGenData):
    for expr in arraylit.explist:
      data = self.visit(expr, data)
    return data

  def visitIntegerLit(self, ast, data):
    return data

  def visitFloatLit(self, ast, data):
    return data
  
  def visitStringLit(self, ast, data):
    return data

  def visitBooleanLit(self, ast, data):
    return data

# class Rule3(CFGVisitor):
#   '''live(x := e, x, in) = False if e does not refer to x'''
#   def __init__(self, cfg : CFG, data : LiveGenData):
#     self.cfg = cfg
#     self.data = data
#     self.symbols = self.cfg.get_symbols()
  
#   def generate(self):
#     return self.visit(self.cfg, self.data)

#   def visitCFG(self, cfg: CFG, data : LiveGenData):
#     for block in cfg.blocks:
#       data = self.visit(block, data)
#     return data
  
#   def visitStmtBlock(self, cfg: StmtBlock, data : LiveGenData):
#     for stmt in cfg.stmts:
#       data = self.visit(stmt, data)
#     return data
  
#   def visitCondBlock(self, cfg: CondBlock, data : LiveGenData):
#     return data
  
#   def visitAssignStmt(self, cfg: AssignStmt, data : LiveGenData):
#     data.ctx.refered_syms = set()

#     # Visit RHS
#     data = self.visit(cfg.rhs, data)
    
#     for sym_name in self.cfg.get_symbols():
#       if sym_name not in data.ctx.refered_syms:
#         data.obj[(cfg.id, sym_name, 'in')] = False

#     return data
  

#   def visitBinExpr(self, cfg : BinExpr, data : LiveGenData):
#     data = self.visit(cfg.left, data)
#     data = self.visit(cfg.right, data)

#     return data

#   def visitUnExpr(self, cfg : UnExpr, data : LiveGenData):
#     data = self.visit(cfg.val, data)

#     return data

#   def visitId(self, cfg : Id, data : LiveGenData):
#     data.ctx.refered_syms.add(cfg.name)
#     return data
  
#   def visitArrayCell(self, cfg : ArrayCell, data : LiveGenData):
#     data.ctx.refered_syms.add(cfg.name)
#     for expr in cfg.cell:
#       data = self.visit(expr)
#     return data

#   def visitArrayLit(self, arraylit : ArrayLit, data : LiveGenData):
#     for expr in arraylit.explist:
#       data = self.visit(expr, data)
#     return data

#   def visitIntegerLit(self, ast, data):
#     return data

#   def visitFloatLit(self, ast, data):
#     return data
  
#   def visitStringLit(self, ast, data):
#     return data

#   def visitBooleanLit(self, ast, data):
#     return data

class OutInPropagator(CFGVisitor):
  '''live(s, x, in) = live(s, x, out) if s does not refer to x'''
  def __init__(self, cfg : CFG, data : LiveGenData):
    self.cfg = cfg
    self.data = data
    self.symbols = set(self.cfg.get_symbols())
  
  def propagate(self):
    return self.visit(self.cfg, self.data)

  def visitCFG(self, cfg: CFG, data : LiveGenData):
    for block in cfg.blocks:
      data = self.visit(block, data)
    return data
    
  def visitBlock(self, cfg : Block, data : LiveGenData):
    if cfg.cond is not None:
      data.ctx.refered_syms = set()
      data = self.visit(cfg.cond, data)
      for sym in self.symbols - data.ctx.refered_syms:
          data.obj[(cfg.cond.id, sym, 'in')] = data.obj[(cfg.cond.id, sym, 'out')]
    else:
      for stmt in cfg.stmts:
        data = self.visit(stmt, data)

    return data
      
  def visitAssignStmt(self, cfg: AssignStmt, data : LiveGenData):
    data.ctx.refered_syms = {cfg.lhs.name}
    data = self.visit(cfg.rhs, data)
    
    for sym in self.symbols - data.ctx.refered_syms:
        data.obj[(cfg.id, sym, 'in')] = data.obj[(cfg.id, sym, 'out')]

    return data
  

  def visitBinExpr(self, cfg : BinExpr, data : LiveGenData):
    data = self.visit(cfg.left, data)
    data = self.visit(cfg.right, data)

    return data

  def visitUnExpr(self, cfg : UnExpr, data : LiveGenData):
    data = self.visit(cfg.val, data)

    return data

  def visitId(self, cfg : Id, data : LiveGenData):
    data.ctx.refered_syms.add(cfg.name)
    return data
  
  def visitArrayCell(self, cfg : ArrayCell, data : LiveGenData):
    data.ctx.refered_syms.add(cfg.name)
    for expr in cfg.cell:
      data = self.visit(expr)
    return data

  def visitArrayLit(self, arraylit : ArrayLit, data : LiveGenData):
    for expr in arraylit.explist:
      data = self.visit(expr, data)
    return data

  def visitIntegerLit(self, ast, data):
    return data

  def visitFloatLit(self, ast, data):
    return data
  
  def visitStringLit(self, ast, data):
    return data

  def visitBooleanLit(self, ast, data):
    return data

class SuccessorPropagator(CFGVisitor):
  '''
  L(p, x, out) = ∨ { L(s, x, in) | s a successor of p }
  '''
  def __init__(self, cfg : CFG, data : LiveGenData):
    self.cfg = cfg
    self.data = data
    self.symbols = set(self.cfg.get_symbols())

  
  def propagate(self):
    return self.visit(self.cfg, self.data)

  def visitCFG(self, cfg: CFG, data : LiveGenData):
    for block in cfg.blocks:
      data = self.visitBlock(block, data)
    return data
  
  def visitBlock(self, cfg: Block, data : LiveGenData):
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
  
  def visitAssignStmt(self, cfg: AssignStmt, data : LiveGenData):
    succ_stmts = self.cfg.get_successors(cfg)
    if len(succ_stmts) > 0:
      for sym in self.symbols:
        for succ_stmt in succ_stmts:
          if data.obj[(succ_stmt.id, sym, 'in')] == True:
            data.obj[(cfg.id, sym, 'out')] = True  
    return data
