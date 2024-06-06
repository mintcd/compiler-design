from code_generation.RegisterAllocator import RegisterAllocator
from utils.visitors import CFGVisitor
from utils.builders.CFGBuilder import CFGBuilder
from utils.builders.SymbolTableBuilder import SymbolTableBuilder
from optimization.refactorers import ASTRefactorer, CFGRefactorer
from optimization.local_optimizer import LocalOptimizer
from utils.structures.CFG import *
from utils.structures.AST import *

import os

class CodeGenerator(CFGVisitor):
  def __init__(self, ast : AST, num_reg : int, log_file = None):

    self.ast = ASTRefactorer(ast).refactor()
    with open(log_file, 'a') as file:
        file.write("Refactored AST\n")
        file.write(f"{str(self.ast)}\n\n")
        file.write("--------------------------------------------------------\n\n")

    self.st = SymbolTableBuilder(self.ast).build()
    with open(log_file, 'a') as file:
        file.write("Symbol Table\n\n")
        file.write(f"{str(self.st)}\n\n")      
        file.write("--------------------------------------------------------\n\n")    

    self.cfg = CFGBuilder(self.ast).build()
    self.cfg = LocalOptimizer(self.cfg).optimize()
    self.cfg = CFGRefactorer(self.cfg).refactor()
    with open(log_file, 'a') as file:
        file.write("CFG\n")
        file.write(f"{str(self.cfg)}\n")
        file.write("--------------------------------------------------------\n\n")
    
    self.reg_alloc = RegisterAllocator(self.cfg, num_reg, log_file).allocate()
    self.reg_alloc = {node : f"$t{attr}" for node, attr in self.reg_alloc.items()}

    with open(log_file, 'a') as file:
        file.write("Register allocation for symbols\n\n")
        file.write(f"{str(self.reg_alloc)}\n")
        file.write(f"--------------------------------------------------------\n")

  def generate(self):
    return self.visit(self.cfg, None)
  
  def visitCFG(self, cfg : CFG, data):
    # Create data field for unallocated symbols
    code = ".data\n\n"

    for sym in self.st.get_varsym():
      if self.reg_alloc.get(sym.name) is None:
        code += f"{sym}: .word {0}\n"

    code += "addi $0 $0 1\n"

    for block in cfg.blocks:
        code += self.visit(block, data)
    
    return code
  
  def visitBlock(self, cfg : Block, data):
    code = None
    if cfg.cond is not None:
      code = f"{cfg.name}_{cfg.id}:\n"

      code +=  f"beq $0 {cfg.true.name}_{cfg.true.id}\n"
      if cfg.false is not None:
        code += f"j {cfg.false.name}_{cfg.false.id}\n"

      code += "\n"
    else:
      code = (f"{cfg.name}_{cfg.id}:\n")

      for stmt in cfg.stmts:
        code += self.visit(stmt, data)

      if cfg.next is not None:
        code += f"j {cfg.next.name}_{cfg.next.id}\n\n"
    
    return code


  def visitAssignStmt(self, cfg : AssignStmt, data):
      code = ""

      if isinstance(cfg.rhs, AtomicLiteral):
        code += f"addi {self.reg_alloc[cfg.lhs.name]} 0 {cfg.rhs.val}\n"

      # if isinstance(cfg.rhs, AtomicLiteral):
      #   code += f"addi {self.reg_alloc[cfg.lhs.name]} 0 {rhs.value}"
      return code
  
  def visitBinExpr(self, cfg : BinExpr, data):
    ins = None
    if cfg.op == "+":
      ins = "add"
    if cfg.op == "-":
      ins = "sub"
    if cfg.op == "*":
      ins = "mul"
    if cfg.op == "/":
      ins = "div"
    
    left = self.reg_alloc[cfg.left.name] if isinstance(cfg.left, Id) else cfg.left.val
    right = self.reg_alloc[cfg.right.name] if isinstance(cfg.right, Id) else cfg.right.val

    return f"{ins} {ctx.lhs_reg} {left} {right}\n"

  def visitUnExpr(self, cfg, ctx):
    ins = None
    if cfg.op == "-":
      ins = 'sub'
    val = self.reg_alloc[cfg.val.name] if isinstance(cfg.val, Id) else cfg.val.val
    return f"{ins} {ctx.lhs_reg} {0} {val}\n"
    
  # def visitId(self, cfg : Id, ctx):
  #   return f"addi {ctx.lhs_reg} {self.reg_alloc[cfg.name]} 0\n"
  
  def visitIntegerLit(self, cfg: IntegerLit, ctx):
    return f"addi {ctx.lhs_reg} {cfg.val} 0\n"

