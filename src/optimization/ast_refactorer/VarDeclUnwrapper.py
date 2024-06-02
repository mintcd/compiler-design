from utils.visitors import ASTVisitor
from utils.structures.AST import *
from optimization.ast_refactorer.InforAssigner import InforAssigner


class Data:
  def __init__(self, obj : Program, ctx = None):
    self.obj = obj
    self.ctx = ctx

class VarDeclUnwrapper(ASTVisitor):

    '''
      Turn VarDecl(x, typ, init) to 
        VarDecl(x,typ) 
        AssignStmt(x, init, typ)
    '''

    def __init__(self, ast):
        self.ast = InforAssigner(ast).assign()

    def unwrap(self):
        data = Data(self.ast)
        return self.visit(self.ast, data).obj
     
    def visitProgram(self, ast: Program, data : Data):
        for decl in ast.decls:
          data = self.visit(decl, data)

        return data
    
    def visitFuncDecl(self, ast : FuncDecl, data : Data):
        data = self.visit(ast.body, data)
        return data

    def visitStmtBlock(self, ast : StmtBlock, data : Data):
        for stmt in ast.stmts:
          data = self.visit(stmt, data)

        return data

    def visitIfStmt(self, ast : IfStmt, data : Data):
        data = self.visit(ast.tstmt, data)
        if ast.fstmt is not None:
          data = self.visit(ast.fstmt, data)

        return data

    def visitWhileStmt(self, ast : WhileStmt, data : Data):
        data = self.visit(ast.stmt, data)

        return data
        
    def visitForStmt(self, ast: ForStmt, data): 
        data = self.visit(ast.stmt, data)

        return data

    def visitDoWhileStmt(self, ast : DoWhileStmt, data):
        data = self.visit(ast.stmt, data)

        return data

    def visitVarDecl(self, ast : VarDecl, data : Data):
        if ast.init is not None:
          idx = ast.block.stmts.index(ast)
          modified_stmts = [VarDecl(ast.name, ast.typ), AssignStmt(Id(ast.name), ast.init, ast.typ)]
          if idx == len(ast.block.stmts) - 1:
            ast.block.stmts = ast.block.stmts[:idx] + modified_stmts
          else:
            ast.block.stmts = ast.block.stmts[:idx] + modified_stmts + ast.block.stmts[idx+1:]

        return data

    def visitAssignStmt(self, ast : AssignStmt, data):
        return data
