from utils.visitors import CFGVisitor
from utils.structures.AST import *
from utils.structures.CFG import *
from utils.structures.SymbolTable import *

from phases.code_generation.RegisterAllocator import RegisterAllocator

class CodeGenerator(CFGVisitor):
  def __init__(self, cfg : CFG, num_reg : int, st : SymbolTable, log_file = None):

    self.st = st
    self.cfg = cfg    
    self.reg_alloc = RegisterAllocator(cfg, st, num_reg, log_file).allocate()
    for symbol in self.st.symbols:
      symbol.register = f"$t{symbol.register}"

    with open(log_file, 'a') as file:
        file.write("Register allocation for symbols\n\n")
        file.write(f"{str(self.reg_alloc)}\n")
        file.write(f"--------------------------------------------------------\n")

  def generate(self):
    return self.visit(self.cfg, None)
  
  def visitCFG(self, cfg : CFG, data):
    # Create data field for unallocated symbols
    code = ".data\n\n"

    for symbol in self.st.symbols:
      if symbol.register == 'spill':
        if isinstance(symbol.datatype, String):
          code += f"{symbol.name}{symbol.id}: .asciiz ""\n"
        else:
          code += f"{symbol.name}{symbol.id}: .word 0\n"

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

      if isinstance(cfg.rhs, Atomic):
        for symbol in self.st.symbols:
          if symbol.id == cfg.lhs.id:
            code += f"addi {symbol.register} 0 {cfg.rhs.val}\n"

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
  
  def visitInteger(self, cfg: Integer, ctx):
    return f"addi {ctx.lhs_reg} {cfg.val} 0\n"

