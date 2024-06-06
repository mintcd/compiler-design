from utils.visitors import ASTVisitor
from utils.structures.AST import *
from optimization.ast_refactor.InforAssigner import InforAssigner

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
        unwrapped = list()
        # if isinstance(ast.typ, ArrayType):
        #   ranges = [range(dim) for dim in ast.typ.dimensions]
        #   cells = list(itertools.product(*ranges))
        #   if ast.init:
        #     values = ast.init.get_value()
        #     for cell in cells:
        #       init = values[cell[0]]
        #       if len(cell) > 1:
        #         for dim in cell[1:]:
        #           init = values[dim]
        #       unwrapped.append(VarDecl(ArrayCell(ast.name, cell), ast.typ.typ, init))
        #   else:
        #     unwrapped.append(VarDecl(ArrayCell(ast.name, cell), ast.typ))
        # else: 
        unwrapped.append(ast)
        modified_stmts = list()
        idx = ast.block.stmts.index(ast)

        for decl in unwrapped:
          modified_stmts += [decl]
          if decl.init is not None:
              modified_stmts += [AssignStmt(Id(decl.name), decl.init, decl.typ)]

        if idx == len(ast.block.stmts) - 1:
          ast.block.stmts = ast.block.stmts[:idx] + modified_stmts
        else:
          ast.block.stmts = ast.block.stmts[:idx] + modified_stmts + ast.block.stmts[idx+1:]

        return data

    def visitAssignStmt(self, ast : AssignStmt, data):
        return data
