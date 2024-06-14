from utils.visitors import ASTVisitor
from utils.structures.AST import *

from utils.APIs import assign_info

import itertools


class Data:
  def __init__(self, obj : Program, ctx = None):
    self.obj = obj
    self.ctx = ctx

class VarDeclUnwrapper(ASTVisitor):

    '''
      Unwrap VarDecl(x, arrayType) to multiple VarDecls
      Unwrap VarDecl(x, typ, init) to 
        VarDecl(x,typ) 
        AssignStmt(x, init, typ)
    '''

    def __init__(self, ast, log_file = None):
        self.ast = assign_info(ast)
        self.log_file = log_file

    def unwrap(self):
        data = Data(self.ast)
        unwrapped_ast  = assign_info(self.ast)
        unwrapped_ast  = self.visit(self.ast, data).obj
        unwrapped_ast  = assign_info(unwrapped_ast)

        if self.log_file is not None:
          with open(self.log_file, 'a') as file:
              file.write("AST after unwrapping VarDecls\n")
              file.write(f"{str(unwrapped_ast)}\n\n")
              file.write("--------------------------------------------------------\n\n")
        
        return unwrapped_ast

     
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
        unwrapped = list()
        unwrapped.append(ast)
        modified_stmts = list()
        idx = ast.block.stmts.index(ast)

        for decl in unwrapped:
          modified_stmts += [decl]
          if decl.init is not None:
              modified_stmts += [AssignStmt(Id(decl.name), decl.init, decl.typ)]
          decl.init = None

        if idx == len(ast.block.stmts) - 1:
          ast.block.stmts = ast.block.stmts[:idx] + modified_stmts
        else:
          ast.block.stmts = ast.block.stmts[:idx] + modified_stmts + ast.block.stmts[idx+1:]

        return data

    def visitAssignStmt(self, ast : AssignStmt, data):
        return data
