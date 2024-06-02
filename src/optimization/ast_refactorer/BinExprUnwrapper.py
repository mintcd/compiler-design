from utils.visitors import ASTVisitor
from utils.structures.AST import *
from optimization.ast_refactorer.InforAssigner import InforAssigner

class Context:
  def __init__(self, last_expr : Expr or None = None):
    self.last_expr = last_expr
    self.used_sym = 0

class Data:
  def __init__(self, obj : Program, ctx : Context):
    self.obj : Program = obj
    self.ctx : Context = ctx

class BinExprUnwrapper(ASTVisitor):

    '''
      Unwrap BinExpr
    '''

    def __init__(self, ast):
        self.ast = InforAssigner(ast).assign()

    def refactor(self):
        data = Data(self.ast, Context())
        return self.visit(self.ast, data).obj
     
    def visitProgram(self, ast: Program, data : Data):
        for decl in ast.decls:
          data = self.visit(decl, data)

        return data
    
    def visitFuncDecl(self, ast : FuncDecl, data : Data):
        for decl in data.obj.decls:
          if decl.name == ast.name:
            decl = FuncDecl(ast.name, ast.rtype, ast.params, ast.inherit, self.visit(ast.body, data))

        return data

    def visitStmtBlock(self, ast : StmtBlock, data : Data):
        for stmt in ast.stmts:
          data = self.visit(stmt, data)

        return data

    def visitIfStmt(self, ast : IfStmt, data : Data): 
        data = self.visit(ast.cond, data)
        ast.cond = data.ctx.last_expr

        data = self.visit(ast.tstmt, data)

        if ast.fstmt is not None:
          data = self.visit(ast.fstmt, data)
        
        data.ctx.used_sym = 0

        return data

    def visitWhileStmt(self, ast : WhileStmt, data : Data):
        data.ctx.current_stmt = ast

        data = self.visit(ast.cond, data)
        ast.cond = data.ctx.last_expr

        data = self.visit(ast.stmt, data)

        data.ctx.used_sym = 0

        return data
        
    def visitDoWhileStmt(self, ast : DoWhileStmt, data):
        data.ctx.current_stmt = ast
        
        data = self.visit(ast.cond)
        ast.cond = data.ctx.last_expr
        data = self.visit(ast.stmt, data)

        data.ctx.used_sym = 0

        return data

    def visitAssignStmt(self, ast : AssignStmt, data):
        data.ctx.current_stmt = ast

        data = self.visit(ast.rhs, data)
        
        ast.rhs = data.ctx.last_expr

        data.ctx.used_sym = 0

        return data

    def visitBinExpr(self, ast : BinExpr, data : Data):
      data = self.visit(ast.left, data)
      left_expr = data.ctx.last_expr

      data = self.visit(ast.right, data)
      right_expr = data.ctx.last_expr

      stmt_id = ast.stmt.block.get_index_of_stmt(ast.stmt)
      last_expr = Id(f"tmp_({data.ctx.used_sym})")

      ast.stmt.block.stmts = ast.stmt.block.stmts[:stmt_id] \
                                + [AssignStmt(last_expr, BinExpr(ast.op, left_expr, right_expr))] \
                                + ast.stmt.block.stmts[stmt_id:]

      data.ctx.used_sym += 1
      data.ctx.last_expr = last_expr

      return data
      
    def visitUnExpr(self, ast : UnExpr, data : Data):
      current_stmt = data.ctx.current_stmt

      data = self.visit(ast.val, data)
      val_expr = data.ctx.last_expr

      stmt_id = current_stmt.block.get_index_of_stmt(current_stmt)
      last_expr = Id(f"tmp_({data.ctx.used_sym})")

      block_stmts = current_stmt.block.stmts

      block_stmts = block_stmts[:stmt_id] + [AssignStmt(last_expr, BinExpr(ast.op, left_expr, right_expr))] + block_stmts[stmt_id:]


      data.ctx.used_sym += 1
      data.ctx.last_expr = last_expr

      return data

    def visitId(self, ast : Id, data : Data):
      data.ctx.last_expr = ast

      return data

    def visitArrayCell(self, ast, data):
      for expr in ast.cell:
        data = self.visit(expr)
        
      data.ctx.last_expr = ast

      return data

    def visitIntegerLit(self, ast, data):
      data.ctx.last_expr = ast

      return data

    def visitFloatLit(self, ast, data):
      data.ctx.last_expr = ast

      return data
    
    def visitStringLit(self, ast, data : Data):
      data.ctx.last_expr = ast

      return data

    def visitBooleanLit(self, ast, data : Data):
      data.ctx.last_expr = ast

      return data

    def visitArrayLit(self, ast, data : Data):
      for expr in ast.exprlist:
        data = self.visit(expr)
        
      data.ctx.last_expr = ast

      return data
