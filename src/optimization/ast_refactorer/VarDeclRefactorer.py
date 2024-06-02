from utils.visitors import ASTVisitor
from utils.structures.AST import *
from optimization.ast_refactorer.InforAssigner import InforAssigner


class Data:
  def __init__(self, obj : Program, ctx = None):
    self.obj = obj
    self.ctx = ctx

class VarDeclRefactorer(ASTVisitor):

    '''
      Remove VarDecl(x, typ)
      Turn VarDecl(x, typ, init) to AssignStmt(x, init, typ), change name if need
    '''

    def __init__(self, ast):
        self.ast = InforAssigner(ast).assign()

    def refactor(self):
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
        if ast.init is None:
          ast.block.stmts.remove(ast)
        else:
          idx = ast.block.stmts.index(ast)
          ast.block.stmts[idx] = AssignStmt(ast.name, ast.init, ast.typ)   
        return data

    def visitAssignStmt(self, ast : AssignStmt, data):
        return data
