from utils.visitors import ASTVisitor
from utils.structures.AST import *

class Context:
    def __init__(self, current_block: StmtBlock or None = None, 
                        current_id : list or None = None,
                        current_stmt: Stmt or None = None):
        self.current_block = current_block
        self.current_stmt = current_stmt
        self.current_id = current_id if current_id is not None else [0]

class Data:
  def __init__(self, obj : Program, ctx : Context or None = None):
    self.obj = obj
    self.ctx = Context() if ctx is None else ctx

class InforAssigner(ASTVisitor):
    '''
      1) Assign the parent block and a unique id to each statement
      2) Assign the parent statement to each expression
    '''

    def __init__(self, ast):
        self.ast = ast

    def assign(self):
        # We only need context, not data
        data = Data(self.ast)
        return self.visit(self.ast, data).obj
    
    def visitProgram(self, ast: Program, data : Data):
        for decl in ast.decls:
          if isinstance(decl, FuncDecl):
            data = self.visit(decl, data)
          else:
            decl.id = tuple(ctx.current_id[-1])
          data.ctx.current_id[-1] += 1
        return data
    
    def visitFuncDecl(self, ast : FuncDecl, data : Data):
        data = self.visit(ast.body, data)

        return data

    def visitStmtBlock(self, ast : StmtBlock, data : Data):
        # Create a new env
        data.ctx.current_block = ast
        parent_id = data.ctx.current_id
        data.ctx.current_id = parent_id + [0]

        for stmt in ast.stmts:
          data = self.visit(stmt, data)
        
        # Retend the last env
        data.ctx.current_id = parent_id

        return data
        
    def visitIfStmt(self, ast : IfStmt, data : Data):
        # Assign info
        parent_id = data.ctx.current_id

        ast.id = tuple(parent_id)
        ast.block = data.ctx.current_block

        # Set context and visit
        data.ctx.current_stmt = ast

        data = self.visit(ast.cond, data)
        data = self.visit(ast.tstmt, data)
        if ast.fstmt is not None:
          data = self.visit(ast.fstmt, data)

        parent_id[-1] += 1

        return data

    def visitWhileStmt(self, ast : WhileStmt, data : Data):
        # Assign info
        parent_id = data.ctx.current_id

        ast.id = tuple(parent_id)
        ast.block = data.ctx.current_block

        # Set context and visit
        data.ctx.current_stmt = ast
        data = self.visit(ast.cond, data)
        data = self.visit(ast.stmt, data)

        parent_id[-1] += 1

        return data
        
    def visitForStmt(self, ast: ForStmt, data): 
        # Assign info
        parent_id = data.ctx.current_id

        ast.id = tuple(parent_id)
        ast.block = data.ctx.current_block

        # Set context and visit
        data.ctx.current_stmt = ast
        data = self.visit(ast.cond, data)
        data = self.visit(ast.stmt, data)

        parent_id[-1] += 1

        return data

    def visitDoWhileStmt(self, ast : DoWhileStmt, data):
        # Assign info
        parent_id = data.ctx.current_id

        ast.id = tuple(parent_id)
        ast.block = data.ctx.current_block

        # Set context and visit
        data.ctx.current_stmt = ast
        data = self.visit(ast.cond, data)
        data = self.visit(ast.stmt, data)

        parent_id[-1] += 1

        return data

    def visitVarDecl(self, ast : VarDecl, data):
        # Assign info
        parent_id = data.ctx.current_id

        ast.id = tuple(parent_id)
        ast.block = data.ctx.current_block

        # Set context and visit
        data.ctx.current_stmt = ast

        if ast.init is not None:
          data = self.visit(ast.init, data)

        parent_id[-1] += 1

        return data

    def visitAssignStmt(self, ast : AssignStmt, data): 
        # Assign info
        parent_id = data.ctx.current_id

        ast.id = tuple(parent_id)
        ast.block = data.ctx.current_block

        # Set context and visit
        data.ctx.current_stmt = ast
        data = self.visit(ast.lhs, data)
        data = self.visit(ast.rhs, data)

        parent_id[-1] += 1

        return data

    def visitBinExpr(self, ast : BinExpr, data): 
      ast.stmt = data.ctx.current_stmt
      data = self.visit(ast.left, data)
      data = self.visit(ast.right, data)
      return data

    def visitUnExpr(self, ast : UnExpr, data): 
      ast.stmt = data.ctx.current_stmt
      data = self.visit(ast.val, data)

      return data

    def visitArrayLit(self, ast : ArrayLit, data):
      ast.stmt = data.ctx.current_stmt
      for expr in ast.explist:
        data = self.visit(expr, data)
      
      return data


    def visitId(self, ast : Id, data):
      ast.stmt = data.ctx.current_stmt
      return data 

    def visitIntegerLit(self, ast, data):
        return data

    def visitFloatLit(self, ast, data):
        return data
    
    def visitStringLit(self, ast, data):
        return data

    def visitBooleanLit(self, ast, data):
        return data