from utils.visitors import ASTVisitor
from utils.structures.AST import *
from utils.APIs import assign_info

class Data:
  def __init__(self, obj : Program, ctx = None):
    self.obj : Program = obj
    self.ctx : Context = ctx

class ForToWhile(ASTVisitor):

    '''
      Turn ForStmt to WhileStmt
    '''

    def __init__(self, ast, log_file = None):
        self.ast = ast
        self.log_file = log_file

    def refactor(self):
        data = Data(self.ast, None)
        refactored_ast = self.visit(self.ast, data).obj
        refactored_ast = assign_info(refactored_ast)
        
        with open(self.log_file, 'a') as file:
          file.write("AST after changing ForStmts to WhileStmts\n")
          file.write(f"{str(refactored_ast)}\n\n")
          file.write("--------------------------------------------------------\n\n")

        return refactored_ast
     
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
        for stmt in ast.stmts:
          data = self.visit(stmt, data)

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
        upd_stmts = [VarDecl(ast.init.lhs.name, IntegerType()), ast.init, WhileStmt(ast.cond, StmtBlock(ast.stmt.stmts + [AssignStmt(ast.init.lhs, ast.upd)]))]

        if ast.id[1] == len(ast.block.stmts) - 1:
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

