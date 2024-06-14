from utils.visitors import ASTVisitor
from utils.structures.AST import *
from utils.helpers import infer_type
from utils.structures.SymbolTable import Symbol

from utils.APIs import assign_info, get_type, build_symbol_table

class Context:
  def __init__(self):
    self.last_expr = None
    self.last_datatype = None
    self.used_sym = 0
    self.current_stmt = None

class Data:
  def __init__(self, obj : Program, ctx : Context):
    self.obj : Program = obj
    self.ctx : Context = ctx

class BinExprUnwrapper(ASTVisitor):

    '''
      Unwrap BinExpr
    '''

    def __init__(self, ast, log_file = None):
        self.ast = ast
        self.st = build_symbol_table(ast)
        self.log_file = log_file

    def unwrap(self):
        data = Data(self.ast, Context())
        
        unwrapped_ast = self.visit(self.ast, data).obj
        unwrapped_ast = assign_info(unwrapped_ast)

        with open(self.log_file, 'a') as file:
          file.write("AST after unwrapping BinExprs\n")
          file.write(f"{str(unwrapped_ast)}\n\n")
          file.write("--------------------------------------------------------\n\n")
          
        return unwrapped_ast
     
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
        data.ctx.current_stmt = ast
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
      ctx = data.ctx

      # Prepare ctx
      ctx.last_expr = None
      ctx.last_datatype = None

      data = self.visit(ast.left, data)
      left_expr = data.ctx.last_expr

      data = self.visit(ast.right, data)
      right_expr = data.ctx.last_expr

      last_expr = Id(f"unwrapping_id_({data.ctx.used_sym})")
      added_stmts = [VarDecl(last_expr.name, ctx.last_datatype), AssignStmt(last_expr, BinExpr(ast.op, left_expr, right_expr))]

      idx = ctx.current_stmt.block.stmts.index(ctx.current_stmt)
      ctx.current_stmt.block.stmts = ctx.current_stmt.block.stmts[:idx]  + added_stmts + ctx.current_stmt.block.stmts[idx:]
      
      ctx.used_sym += 1
      ctx.last_expr = last_expr

      return data
      
    def visitUnExpr(self, ast : UnExpr, data : Data):
      ctx = data.ctx

      data = self.visit(ast.val, data)
      val_expr = data.ctx.last_expr

      last_expr = Id(f"unwrapping_symbol_({data.ctx.used_sym})")
      added_stmts = [VarDecl(last_expr.name, data.ctx.last_datatype), AssignStmt(last_expr, UnExpr(ast.op, val_expr))]

      idx = ctx.current_stmt.block.stmts.index(ctx.current_stmt)
      ctx.current_stmt.block.stmts = ctx.current_stmt.block.stmts[:idx]  + added_stmts + ctx.current_stmt.block.stmts[idx:]
      
      data.ctx.used_sym += 1
      data.ctx.last_expr = last_expr

      return data

    def visitArrayCell(self, ast, data):
      for expr in ast.cell:
        data = self.visit(expr, data)
        
      data.ctx.last_expr = ast

      return data

    def visitId(self, ast : Id, data : Data):
      data.ctx.last_expr = ast
      symbol = self.st.get_symbol(ast.name)

      data.ctx.last_datatype = infer_type(data.ctx.last_datatype, symbol.datatype)

      return data

    def visitArrayLit(self, ast : ArrayLit, data : Data):
      for i in range(len(ast.explist)):
        data = self.visit(ast.explist[i], data)
        ast.explist[i] = data.ctx.last_expr
        
      data.ctx.last_expr = ast

      return data

    def visitIntegerLit(self, ast, data):
      data.ctx.last_expr = ast
      data.ctx.last_datatype = infer_type(IntegerType(), data.ctx.last_datatype)
      return data

    def visitFloatLit(self, ast, data):
      data.ctx.last_expr = ast
      data.ctx.last_datatype = infer_type(FloatType(), data.ctx.last_datatype)
      return data
    
    def visitStringLit(self, ast, data : Data):
      data.ctx.last_expr = ast
      data.ctx.last_datatype = StringType()
      return data

    def visitBooleanLit(self, ast, data : Data):
      data.ctx.last_expr = ast
      data.ctx.last_datatype = BooleanType()
      return data
