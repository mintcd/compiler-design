from utils.visitor_pattern import Data
from utils.visitors import ASTVisitor
from utils.structures.SymbolTable import *

class SymbolTableBuilderContext:
  def __init__(self, current_scope = (0,0), 
                      in_loop = False, 
                      current_datatype = None,
                      args = None
                      ):
    self.current_scope = current_scope
    self.in_loop = in_loop
    self.current_datatype = None
    self.args = args

class SymbolTableBuilderData(Data):
  def __init__(self, obj : SymbolTable or None = None, 
                    ctx : SymbolTableBuilderContext or None  = None):
    self.obj = SymbolTable() if obj is None else obj
    self.ctx = SymbolTableBuilderContext() if ctx is None else ctx

class SymbolTableBuilder(ASTVisitor):
  def __init__(self, ast : AST):
    self.ast = ast

  def build(self): 
    return self.visit(self.ast, SymbolTableBuilderData()).obj

  def visitAssignStmt(self, ast : AssignStmt, data): 
    return data

  def visitIfStmt(self, ast, data):
    return data

  def visitForStmt(self, ast, data):
    return data

  
  def visitWhileStmt(self, ast, data):
    return data

  
  def visitDoWhileStmt(self, ast, data):
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
      ctx = data.ctx

      st.add_symbol(Symbol(st.get_avail_id(), ast.name, ast.typ, ctx.current_scope, ast.init))

      return data

  def visitStmtBlock(self, ast : StmtBlock, data):
    for stmt in ast.stmts:
      data = self.visit(stmt, data)
    return data
  
  def visitFuncDecl(self, ast : FuncDecl, data : SymbolTableBuilderData):
      st = data.obj
      ctx = data.ctx

      st.add_symbol(Symbol(st.get_avail_id(), ast.name, ast.rtype, ctx.current_scope, params=ast.params))

      # If the function is called recursively, ignore
      if ctx.current_scope[1] == 1:
        return data
      else:
        if ctx.current_scope[0] == ast.name:
          ctx.current_scope[1] == 1
        else: 
          ctx.current_scope = (ast.name, 0)

      for i in range(len(ast.params)):
        st.add_symbol(Symbol(st.get_avail_id(), 
                            ast.params[i].name, 
                            ast.params[i].typ, 
                            ctx.current_scope,
                            ctx.args[i]))

      data = self.visit(ast.body, data)
      
      return data

  
  def visitProgram(self, ast : Program, data : SymbolTableBuilderData):
      st = data.obj
      ctx = data.ctx

      for decl in ast.decls:
        if isinstance(decl, VarDecl):
          data = self.visit(decl)
      
      for decl in ast.decls:
        if isinstance(decl, FuncDecl) and decl.name == "main":
          data = self.visit(decl, data)
      
      return data
