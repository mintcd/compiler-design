from utils.visitors import ASTVisitor
from utils.structures.AST import *
from optimization.ast_refactor.InforAssigner import InforAssigner
from utils.builders.SymbolTableBuilder import SymbolTableBuilder
from utils.helpers import type_inference

class Context:
  def __init__(self, last_expr : Expr or None = None):
    self.last_expr = last_expr
    self.last_datatype: Type or None  = None
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
        self.st = SymbolTableBuilder(ast).build()

    def unwrap(self):
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
        
        return data

    def visitWhileStmt(self, ast : WhileStmt, data : Data):
        data.ctx.current_stmt = ast

        data = self.visit(ast.cond, data)
        ast.cond = data.ctx.last_expr

        data = self.visit(ast.stmt, data)

        return data
        
    def visitDoWhileStmt(self, ast : DoWhileStmt, data):
        data.ctx.current_stmt = ast
        
        data = self.visit(ast.cond)
        ast.cond = data.ctx.last_expr
        data = self.visit(ast.stmt, data)

        return data

    def visitAssignStmt(self, ast : AssignStmt, data):
        data.ctx.current_stmt = ast

        data = self.visit(ast.rhs, data)
        
        ast.rhs = data.ctx.last_expr

        return data

    def visitBinExpr(self, ast : BinExpr, data : Data):
      # Prepare ctx
      data.ctx.last_expr = None
      data.ctx.last_datatype = None

      data = self.visit(ast.left, data)
      left_expr = data.ctx.last_expr

      data = self.visit(ast.right, data)
      right_expr = data.ctx.last_expr

      stmt_id = ast.stmt.block.get_index_of_stmt(ast.stmt)
      last_expr = Id(f"tmp_({data.ctx.used_sym})")

      modified_stmts = [VarDecl(last_expr.name, data.ctx.last_datatype), AssignStmt(last_expr, BinExpr(ast.op, left_expr, right_expr))]

      ast.stmt.block.stmts = ast.stmt.block.stmts[:stmt_id]  + modified_stmts + ast.stmt.block.stmts[stmt_id:]
      
      data.ctx.used_sym += 1
      data.ctx.last_expr = last_expr

      return data
      
    def visitUnExpr(self, ast : UnExpr, data : Data):
      current_stmt = data.ctx.current_stmt

      data = self.visit(ast.val, data)
      val_expr = data.ctx.last_expr

      stmt_id = current_stmt.block.get_index_of_stmt(current_stmt)
      last_expr = Id(f"tmp_({data.ctx.used_sym})")
      modified_stmts = [VarDecl(last_expr.name, data.ctx.last_datatype), AssignStmt(last_expr, UnExpr(ast.op, val_expr))]

      ast.stmt.block.stmts = ast.stmt.block.stmts[:stmt_id] + modified_stmts + ast.stmt.block.stmts[stmt_id:]

      data.ctx.used_sym += 1
      data.ctx.last_expr = last_expr

      return data

    def visitArrayCell(self, ast, data):
      for expr in ast.cell:
        data = self.visit(expr)
        
      data.ctx.last_expr = ast

      return data

    def visitId(self, ast : Id, data : Data):
      data.ctx.last_expr = ast
      symbol = self.st.get_symbol(ast.name)

      data.ctx.last_datatype = type_inference(data.ctx.last_datatype, symbol.datatype)

      return data

    def visitArrayLit(self, ast : ArrayLit, data : Data):
      for i in range(len(ast.explist)):
        data = self.visit(ast.explist[i], data)
        ast.explist[i] = data.ctx.last_expr
        
      data.ctx.last_expr = ast

      return data

    def visitIntegerLit(self, ast, data):
      data.ctx.last_expr = ast
      data.ctx.last_datatype = type_inference(IntegerType(), data.ctx.last_datatype)
      return data

    def visitFloatLit(self, ast, data):
      data.ctx.last_expr = ast
      data.ctx.last_datatype = type_inference(FloatType(), data.ctx.last_datatype)
      return data
    
    def visitStringLit(self, ast, data : Data):
      data.ctx.last_expr = ast
      data.ctx.last_datatype = StringType()
      return data

    def visitBooleanLit(self, ast, data : Data):
      data.ctx.last_expr = ast
      data.ctx.last_datatype = BooleanType()
      return data
