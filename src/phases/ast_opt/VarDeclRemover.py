from utils.structures.AST import *
from utils.visitors import ASTVisitor

class Data:
  def __init__(self, obj, ctx = None):
    self.obj = obj
    self.ctx = None

class VarDeclRemover(ASTVisitor):

    def __init__(self, ast, log_file = None):
      self.ast = ast
      self.log_file = log_file
    
    def remove(self):
      data = Data(self.ast)
      return self.visit(self.ast, data).obj

    def visitProgram(self, ast: Program, data : Data):
      for decl in ast.decls:
          data = self.visit(decl, data)

      return data

    def visitStmtBlock(self, ast : StmtBlock, data : Data): 
      for stmt in ast.stmts:
        data = self.visit(stmt, data)
      return data
    
########################## DECLARATIONS ###############################
    def visitFuncDecl(self, ast: FuncDecl, data : Data):
        data = self.visit(ast.body, data)
        return data

    def visitParamDecl(self, ast: ParamDecl, data : Data):
        return data
        
    def visitVarDecl(self, ast: VarDecl, data : Data):
        ast.block.stmts.remove(ast)
        return data

########################## STATEMENTS ###################################

    def visitIfStmt(self, ast: IfStmt, data : Data):
      data = self.visit(ast.tstmt)
      if ast.fstmt is not None:
        data = self.visit(ast.fstmt)
      return data
    
    def visitWhileStmt(self, ast: WhileStmt, data : Data):
      data = self.visit(ast.stmt)
      return data

    
    def visitDoWhileStmt(self, ast: DoWhileStmt, data : Data):
      data = self.visit(ast.stmt)
      return data

    def visitBreakStmt(self, ast: BreakStmt, data : Data):
        return data

    
    def visitContinueStmt(self, ast: ContinueStmt, data : Data):
        return data

    
    def visitReturnStmt(self, ast: ReturnStmt, data : Data):
        return data

    
    def visitCallStmt(self, ast: CallStmt, data : Data):
        return data