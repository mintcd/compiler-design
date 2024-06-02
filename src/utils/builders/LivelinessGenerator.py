from utils.structures.CFG import *
from utils.visitor_pattern import Data
from utils.visitors import CFGVisitor
# from utils.structures.AST import
import json
from typing import Set
import copy

class LiveGenContext:
  def __init__(self, stmt: Stmt or None = None, 
                    refered_syms: Set[str] or None = None):
    self.refered_syms = refered_syms if refered_syms is not None else set()

class LiveGenData(Data):
  def __init__(self, obj : dict(), ctx : LiveGenContext):
    self.obj = obj
    self.ctx = ctx

class LivelinessGenerator(CFGVisitor):
  '''
    Visitees : CFG and its children
    Data:
      obj: a dictionary (stmt_id, symbol, "in" | "out") --> True | False
      ctx: stmt_id : (int,int)
  '''
  def __init__(self, cfg : CFG):
    self.cfg = cfg

  def get_succ_stmts(self, stmt : AssignStmt):
    succs = []
    stmt_block = self.cfg.get_block_by_id(stmt.id[0])

    # If this is the last stmt in the block, look for first stmts in succ blocks   
    if isinstance(stmt_block, CondBlock) or stmt.id[1] == len(stmt_block.stmts) - 1:
      for succ_block in stmt_block.get_successors():
        if isinstance(succ_block, StmtBlock) and len(succ_block.stmts) > 0:
          succs.append(succ_block.stmts[0])
        if isinstance(succ_block, CondBlock):
          succs.append(succ_block.cond)
    # Else add its succ stmt in the same block
    else:
      succs.append(stmt_block.stmts[stmt.id[1] + 1])
    
    return succs
    
  def generate(self):
    obj = dict()
    for sym_name in self.cfg.get_symbols():
      for stmt in self.cfg.get_stmts():
        obj[(stmt.id, sym_name, "in")] = False
        obj[(stmt.id, sym_name, "out")] = False
    
    ctx = LiveGenContext()

    data = LiveGenData(obj , ctx)
    loop = 0

    data = Rule12(self.cfg, data).generate()
    data = Rule3(self.cfg, data).generate()

    while True:
      new_data = copy.deepcopy(data)
      # new_data = Rule4(self.cfg, new_data).generate()
      new_data = Rule5(self.cfg, new_data).generate()
      if data.obj == new_data.obj:
          break
      loop += 1
      if loop == 100:
        raise Exception(f"Executed {loop} loop")

    live = dict()

    for stmt in self.cfg.get_stmts():
      live[stmt.id] = set()
      for sym in self.cfg.get_symbols():
        if data.obj[(stmt.id, sym, 'out')] == True:
          live[stmt.id].add(sym)
        for succ_stmt in self.get_succ_stmts(stmt):
          if data.obj[(succ_stmt.id, sym, 'in')] == True: 
            live[stmt.id].add(sym)
      live[stmt.id] = list(live[stmt.id])

    return live

class Rule12(CFGVisitor):
  '''
  stmt : AssignStmt(lhs, rhs) ---> live[stmt, rhs, in] = True

  expr ---> live[stmt, expr, in] = True
  '''

  def __init__(self, cfg : CFG, data : LiveGenData):
    self.cfg = cfg
    self.data = data
    self.syms = self.cfg.get_symbols()
  
  def generate(self):
    return self.visit(self.cfg, self.data)

  def visitCFG(self, cfg: CFG, data : LiveGenData):
    for block in cfg.blocks:
      data = self.visit(block, data)
    return data
  
  def visitStmtBlock(self, cfg: StmtBlock, data : LiveGenData):
    for stmt in cfg.stmts:
      data = self.visit(stmt, data)

    return data
  
  def visitCondBlock(self, cfg: CondBlock, data : LiveGenData):
    live_dict = data.obj
    ctx = data.ctx

    ctx.refered_syms = set()
    data = self.visit(cfg.cond, data)
    for sym in ctx.refered_syms:
      data.obj[(cfg.cond.id, sym, 'in')] = True

    return data
  
  def visitAssignStmt(self, cfg: AssignStmt, data : LiveGenData):
    live_dict = data.obj
    ctx = data.ctx

    ctx.refered_syms = set()
    data = self.visit(cfg.rhs, data)
    for sym in ctx.refered_syms:
      data.obj[(cfg.id, sym, 'in')] = True
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

class Rule3(CFGVisitor):
  '''live(x := e, x, in) = False if e does not refer to x'''
  def __init__(self, cfg : CFG, data : LiveGenData):
    self.cfg = cfg
    self.data = data
    self.syms = self.cfg.get_symbols()
  
  def generate(self):
    return self.visit(self.cfg, self.data)

  def visitCFG(self, cfg: CFG, data : LiveGenData):
    for block in cfg.blocks:
      data = self.visit(block, data)
    return data
  
  def visitStmtBlock(self, cfg: StmtBlock, data : LiveGenData):
    for stmt in cfg.stmts:
      data = self.visit(stmt, data)
    return data
  
  def visitCondBlock(self, cfg: CondBlock, data : LiveGenData):
    return data
  
  def visitAssignStmt(self, cfg: AssignStmt, data : LiveGenData):
    data.ctx.refered_syms = set()

    # Visit RHS
    data = self.visit(cfg.rhs, data)
    
    for sym_name in self.cfg.get_symbols():
      if sym_name not in data.ctx.refered_syms:
        data.obj[(cfg.id, sym_name, 'in')] = False

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

class Rule4(CFGVisitor):
  '''live(s, x, in) = live(s, x, out) if s does not refer to x'''
  def __init__(self, cfg : CFG, data : LiveGenData):
    self.cfg = cfg
    self.data = data
    self.syms = self.cfg.get_symbols()
  
  def generate(self):
    return self.visit(self.cfg, self.data)

  def visitCFG(self, cfg: CFG, data : LiveGenData):
    for block in cfg.blocks:
      data = self.visit(block, data)
    return data
  
  def visitStmtBlock(self, cfg: StmtBlock, data : LiveGenData):
    for stmt in cfg.stmts:
      data = self.visit(stmt, data)

    return data
  
  def visitCondBlock(self, cfg: CondBlock, data : LiveGenData):
    data.ctx.refered_syms = set()
    data = self.visit(cfg.cond, data)
    for sym_name in self.cfg.get_symbols():
      if sym_name not in data.ctx.refered_syms:
        data.obj[(cfg.cond.id, sym_name, 'in')] = data.obj[(cfg.cond.id, sym_name, 'out')]
  
  def visitAssignStmt(self, cfg: AssignStmt, data : LiveGenData):
    data.ctx.refered_syms = {cfg.lhs.name}

    # Visit RHS
    data = self.visit(cfg.rhs, data)
    
    for sym_name in self.cfg.get_symbols():
      if sym_name not in data.ctx.refered_syms:
        data.obj[(cfg.id, sym_name, 'in')] = data.obj[(cfg.id, sym_name, 'out')]

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

class Rule5(CFGVisitor):
  '''
  L(p, x, out) = ∨ { L(s, x, in) | s a successor of p }
  '''
  def __init__(self, cfg : CFG, data : LiveGenData):
    self.cfg = cfg
    self.data = data
  
  def generate(self):
    return self.visit(self.cfg, self.data)

  def visitCFG(self, cfg: CFG, data : LiveGenData):
    for block in cfg.blocks:
      data = self.visitBlock(block, data)
    return data
  
  def visitStmtBlock(self, cfg: StmtBlock, data : LiveGenData):
    for stmt in reversed(cfg.stmts):
      data = self.visit(stmt, data)
          
    return data
  
  def visitCondBlock(self, cfg : CondBlock, data : LiveGenData):
    next_stmts = self.cfg.get_next_stmts(cfg.cond)

    if len(succ_stmts) == 0: 
      return data
    else:
      for next_stmt in next_stmts:
        if data.obj[(next_stmt, sym, 'in')] == True:
          data.obj[(cfg.cond.id, sym, 'out')] = True
          
    return data

  def visitAssignStmt(self, cfg: AssignStmt, data : LiveGenData):
    next_stmts = self.cfg.get_next_stmts(cfg)
    if len(succ_stmts) == 0: 
      return data
    else:
      for next_stmt in next_stmts:
        if data.obj[(next_stmt, sym, 'in')] == True:
          data.obj[(cfg.cond.id, sym, 'out')] = True

    return data
