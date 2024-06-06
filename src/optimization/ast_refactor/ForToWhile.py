from utils.visitors import ASTVisitor
from utils.structures.AST import *

class Context:
  pass

class Data:
  def __init__(self, obj : Program, ctx : Context):
    self.obj : Program = obj
    self.ctx : Context = ctx

class ForToWhile(ASTVisitor):

    '''
      Turn ForStmt to WhileStmt
    '''

    def __init__(self, ast):
        self.ast = ast

    def refactor(self):
        data = Data(self.ast, Context())
        return self.visit(self.ast, data).obj
     
    def visitProgram(self, ast: Program, data):
        for decl in ast.decls:
          data = self.visit(decl, data)

        return data
    
    def visitFuncDecl(self, ast : FuncDecl, data):
        for decl in data.obj.decls:
          if decl.name == ast.name:
            decl = FuncDecl(ast.name, ast.rtype, ast.params, ast.inherit, self.visit(ast.body, data))

        return data

    def visitStmtBlock(self, ast : StmtBlock, data):
        stmts = ast.stmts
        for i in range(len(stmts)):
          # Set ctx appropriately
          ctx = data.ctx
          ctx.current_block = ast

          ctx.stmt_id = i
          data = self.visit(stmts[i], data)

        return data

    def visitIfStmt(self, ast : IfStmt, data):
        data = self.visit(ast.tstmt, data)
        if ast.fstmt is not None:
          data = self.visit(ast.fstmt, data)

        return data

    def visitWhileStmt(self, ast : WhileStmt, data):
        data = self.visit(ast.stmt, data)

        return data
        
    def visitForStmt(self, ast: ForStmt, data): 
        idx = ast.block.stmts.index(ast)

        data = self.visit(ast.stmt, data)
        upd_stmts = [ast.init, WhileStmt(ast.cond, StmtBlock(ast.stmt.stmts + [AssignStmt(ast.init.lhs, ast.upd)]))]

        if self_num == len(ast.block.stmts) - 1:
          ast.block.stmts = ast.block.stmts[:idx] + upd_stmts
        else:
          ast.block.stmts = ast.block.stmts[:idx] + upd_stmts +ast.block.stmts[idx+1:]

        return data

    def visitDoWhileStmt(self, ast : DoWhileStmt, data):
        data = self.visit(ast.stmt, data)

        return data

    def visitVarDecl(self, ast : VarDecl, data):
        return data

    def visitAssignStmt(self, ast : AssignStmt, data):
        return data

