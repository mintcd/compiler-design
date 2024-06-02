from optimization.RegisterAllocator import RegisterAllocator
from utils.visitors import CFGVisitor
from utils.builders.CFGBuilder import CFGBuilder
from utils.builders.SymbolTableBuilder import SymbolTableBuilder
from optimization.refactorers import ASTRefactorer
from utils.structures.CFG import *
from utils.structures.AST import *

class CodeGenContext:
  def __init__(self,  lhs_reg: str or None = None, 
                      left_reg: str or None = None, 
                      right_reg: str or None = None, 
                      pos : 'left' or 'right' or 'rhs' or None = None):
    self.lhs_reg = lhs_reg
    self.left_reg = left_reg
    self.right_reg = right_reg
    self.pos = pos

class CodeGenData:
  def __init__(self, obj : str, ctx : CodeGenContext):
    self.obj = obj
    self.ctx = ctx

class CodeGenerator(CFGVisitor):
  def __init__(self, ast : AST, num_reg : int):

    self.ast = ASTRefactorer(ast).refactor()
    self.cfg = CFGBuilder(self.ast).build()
    self.st = SymbolTableBuilder(self.ast).build()

    print(31, self.cfg)

    self.reg_alloc = RegisterAllocator(self.cfg, num_reg).allocate()
    
    for node, attr in self.reg_alloc.items():
      if attr is not None:
        self.reg_alloc[node] = f'${attr}'

    # print(self.reg_alloc)

  def generate(self):
    # Create data field for unallocated symbols
    code = ".data\n\n"

    for sym in self.st.get_varsym():
      if self.reg_alloc.get(sym.name) is None:
        code += f"{sym}: .word {0}"

    ctx =  CodeGenContext()
    return self.visit(self.cfg, ctx)
  
  def visitCFG(self, cfg : CFG, ctx: CodeGenContext):
    for block in cfg.blocks:
        data = self.visit(block, ctx)
    
    return data

  def visitStmtBlock(self, cfg : StmtBlock, ctx: CodeGenContext):
    code = (f"{cfg.name}_{cfg.id}:\n\n")

    for stmt in cfg.stmts:
      code += self.visit(stmt, ctx)
    
    return code

  def visitCondBlock(self, cfg: CondBlock, data: CodeGenData):
    code = data.obj
    ctx = data.ctx
    
    code = ""

    code += (f"{cfg.name}_{cfg.id}:"
              f"{self.visit(cfg.cond)}")

    return code
    

  def visitAssignStmt(self, cfg : AssignStmt, ctx):
      ctx.lhs_reg = self.reg_alloc.get(cfg.lhs.name)
      if ctx.lhs_reg is not None:
        return self.visit(cfg.rhs, ctx)
      return ""
  
  def visitBinExpr(self, cfg : BinExpr, ctx : CodeGenContext):
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
    

  def visitId(self, cfg : Id, ctx):
    return f"addi {ctx.lhs_reg} {self.reg_alloc[cfg.name]} 0\n"
  
  def visitIntegerLit(self, cfg: IntegerLit, ctx):
    return f"addi {ctx.lhs_reg} {cfg.val} 0\n"

