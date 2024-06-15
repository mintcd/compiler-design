from utils.visitors import ASTVisitor
from utils.structures.SymbolTable import *

from utils.assist_visitors.ASTInforAssigner import ASTInforAssigner

class Context:
  def __init__(self, current_scope = (0,0), 
                      current_datatype = None,
                      args = None
                      ):
    self.current_scope = current_scope
    self.current_datatype = None
    self.args = args

class Data:
  def __init__(self, obj : SymbolTable or None = None, 
                    ctx : Context or None  = None):
    self.obj = SymbolTable() if obj is None else obj
    self.ctx = Context() if ctx is None else ctx

class SymbolTableBuilder(ASTVisitor):
  '''
    Build Symbol Table for AST
  '''
  def __init__(self, ast : AST, log_file = None):
    self.ast = ASTInforAssigner(ast).assign()
    self.log_file = log_file

  def build(self): 
    st = self.visit(self.ast, Data()).obj
    if self.log_file is not None:
      with open(self.log_file, 'a') as file:
        file.write("Symbol Table\n")
        file.write(f"{str(st)}\n\n")
        file.write("--------------------------------------------------------\n\n")

    return st

  def visitAssignStmt(self, ast : AssignStmt, data): 
    return data

  def visitIfStmt(self, ast, data):
    return data

  def visitForStmt(self, ast, data):
    return data

  
  def visitWhileStmt(self, ast : WhileStmt, data):
    data = self.visit(ast.stmt, data)

    return data

  
  def visitDoWhileStmt(self, ast, data):
    data = self.visit(ast.stmt, data)

    return data

  
  def visitBreakStmt(self, ast, data):
    return data

  
  def visitContinueStmt(self, ast, data):
    return data

  
  def visitReturnStmt(self, ast, data):
    return data

  
  def visitCallStmt(self, ast, data):
    return data

  
  def visitVarDecl(self, ast : VarDecl, data):
      st = data.obj
      st.add_symbol(ast)

      return data

  def visitStmtBlock(self, ast : StmtBlock, data):
    for stmt in ast.stmts:
      data = self.visit(stmt, data)
    return data
  
  def visitFuncDecl(self, ast : FuncDecl, data : Data):
      st = data.obj
      ctx = data.ctx

      st.add_symbol(ast)

      # for param in ast.params:
      #   st.symbols.append(Symbol(st.get_avail_id(), 
      #                       ast.params[i].name, 
      #                       ast.params[i].typ, 
      #                       ast.id,
      #                       ctx.args[i]))

      data = self.visit(ast.body, data)
      
      return data

  
  def visitProgram(self, ast : Program, data : Data):
      st = data.obj
      ctx = data.ctx

      for decl in ast.decls:
        if isinstance(decl, VarDecl):
          data = self.visit(decl)
      
      for decl in ast.decls:
        if isinstance(decl, FuncDecl) and decl.name == "main":
          data = self.visit(decl, data)
      
      return data
