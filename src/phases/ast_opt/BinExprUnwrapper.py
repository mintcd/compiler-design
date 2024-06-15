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
      # print(95, ast)

      data.ctx.current_stmt = ast
      data = self.visit(ast.lhs, data)
      data = self.visit(ast.rhs, data)
      
      ast.rhs = data.ctx.last_expr

      return data

    def visitBinExpr(self, ast : BinExpr, data : Data):
      print("Visiting", ast)
      ctx = data.ctx

      # Prepare context
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
      for i in range(len(ast.cell)):
        data = self.visit(ast.cell[i], data)
        ast.cell[i] = data.ctx.last_expr
        
      data.ctx.last_expr = ast

      return data

    def visitId(self, ast : Id, data : Data):
      data.ctx.last_expr = ast
      symbol = self.st.get_symbol(ast.name)

      data.ctx.last_datatype = infer_type(data.ctx.last_datatype, symbol.datatype)

      return data

    def visitArray(self, ast : Array, data : Data):
      for i in range(len(ast.val)):
        data = self.visit(ast.val[i], data)
        ast.val[i] = data.ctx.last_expr
        
      data.ctx.last_expr = ast

      return data

    def visitInteger(self, ast, data):
      data.ctx.last_expr = ast
      data.ctx.last_datatype = infer_type(ast, data.ctx.last_datatype)
      return data

    def visitFloat(self, ast, data):
      data.ctx.last_expr = ast
      data.ctx.last_datatype = infer_type(ast, data.ctx.last_datatype)
      return data
    
    def visitString(self, ast, data : Data):
      data.ctx.last_expr = ast
      data.ctx.last_datatype = ast
      return data

    def visitBoolean(self, ast, data : Data):
      data.ctx.last_expr = ast
      data.ctx.last_datatype = ast
      return data
