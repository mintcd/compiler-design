from utils.visitors import ASTVisitor, CFGVisitor
from utils.structures.CFG import CFG, Block
from utils.structures.AST import *
from typing import List
import copy

class ASTRefactorerContext:
  def __init__(self, last_expr : int or None = None):
    self.last_expr : Expr = last_expr
    self.used_sym = 0

    self.current_block: Block or None = None
    self.stmt_id = 0
    self.current_stmt: Stmt or None = None

    self.current_id = [0]

class ASTRefactorerData:
  def __init__(self, obj : Program, ctx : ASTRefactorerContext):
    self.obj = obj
    self.ctx = ctx

class ASTRefactorer(ASTVisitor):

    '''
      1) Assign a unique id to each stmt
      2) Eliminates dead code after Return.
      3) Turns Stmt used in IfStmt, WhileStmt and ForStmt to Block
      4) Turn initiated vardecl to assignstmt with infered type
      5) Turn For to While
      6) Unwrap BinExpr
    '''

    def __init__(self, ast : Program):
        self.ast = ast

    def refactor(self):
        ast = SubstatementRefactorer(self.ast).refactor()
        ast = VarDeclRefactorer(ast).refactor()
        ast = ForToWhile(ast).refactor()
        ast = BinExprUnwrapper(ast).refactor()

        return ast

class SubstatementRefactorer(ASTVisitor):
    '''
      Turns Stmt used in 

        IfStmt, 
        WhileStmt, and
        ForStmt 

      to Block 
    '''

    def __init__(self, ast):
        self.ast = ast

    def refactor(self):
        data = ASTRefactorerData(self.ast, ASTRefactorerContext())
        return self.visit(self.ast, data).obj
    
    def visitProgram(self, ast: Program, data : ASTRefactorerData):
        for decl in ast.decls:
          data = self.visit(decl, data)

        return data
    
    def visitFuncDecl(self, ast : FuncDecl, data : ASTRefactorerData):
        for decl in data.obj.decls:
          if decl.name == ast.name:
            decl = FuncDecl(ast.name, ast.rtype, ast.params, ast.inherit, self.visit(ast.body, data))

        return data

    def visitASTBlock(self, ast : StmtBlock, data : ASTRefactorerData):
        for stmt in ast.stmts:
          data = self.visit(stmt, data)

        return data
        
    def visitIfStmt(self, ast : IfStmt, data : ASTRefactorerData):
        # Retrieve the ctx
        self_block = data.ctx.current_block
        self_num = data.ctx.stmt_id

        # Turn the stmts to Block and visit it
        if not isinstance(ast.tstmt, Block):
          ast.tstmt = StmtBlock([ast.tstmt])
          data = self.visit(ast.tstmt, data)

        if ast.fstmt is not None and not isinstance(ast.fstmt, Block):
          ast.fstmt = StmtBlock([ast.fstmt])
          data = self.visit(ast.fstmt, data)

        # Use ctx to modify ast correctly
        self_block.stmts[self_num[-1]] = ast

        return data

    def visitWhileStmt(self, ast : WhileStmt, data : ASTRefactorerData):
        # Retrieve the ctx
        self_block = data.ctx.current_block
        self_num = data.ctx.stmt_id

        if not isinstance(ast.stmt, Block):
          ast.stmt = StmtBlock([ast.stmt])

        self_block.stmts[self_num[-1]] = ast
   
        return data
        
    def visitForStmt(self, ast: ForStmt, data): 
        # Retrieve the ctx
        self_block = data.ctx.current_block
        self_num = data.ctx.stmt_id

        if not isinstance(ast.stmt, Block):
          ast.stmt = StmtBlock([ast.stmt])
 
        return data

    def visitDoWhileStmt(self, ast : DoWhileStmt, data):
      return data

    def visitVarDecl(self, ast : VarDecl, data):
        return data

    def visitAssignStmt(self, ast : AssignStmt, data):
        return data

class VarDeclRefactorer(ASTVisitor):

    '''
      Remove VarDecl(x, typ)
      Turn VarDecl(x, typ, init) to AssignStmt(x, init)
    '''

    def __init__(self, ast):
        self.ast = ast

    def refactor(self):
        data = ASTRefactorerData(self.ast, ASTRefactorerContext())
        return self.visit(self.ast, data).obj
     
    def visitProgram(self, ast: Program, data : ASTRefactorerData):
        for decl in ast.decls:
          data = self.visit(decl, data)

        return data
    
    def visitFuncDecl(self, ast : FuncDecl, data : ASTRefactorerData):
        for decl in data.obj.decls:
          if decl.name == ast.name:
            decl = FuncDecl(ast.name, ast.rtype, ast.params, ast.inherit, self.visit(ast.body, data))

        return data

    def visitASTBlock(self, ast : Block, data : ASTRefactorerData):
        stmts = ast.stmts
        for i in range(len(stmts)):
          # Set ctx appropriately
          ctx = data.ctx
          ctx.current_block = ast

          ctx.stmt_id = i
          data = self.visit(stmts[i], data)

        return data

    def visitIfStmt(self, ast : IfStmt, data : ASTRefactorerData):
        # Retrieve the ctx
        self_block = data.ctx.current_block
        self_num = data.ctx.stmt_id

        data = self.visit(ast.tstmt, data)
        if ast.fstmt is not None:
          data = self.visit(ast.fstmt, data)

        return data

    def visitWhileStmt(self, ast : WhileStmt, data : ASTRefactorerData):
        self_block = data.ctx.current_block
        self_num = data.ctx.stmt_id

        data = self.visit(ast.stmt, data)

        return data
        
    def visitForStmt(self, ast: ForStmt, data): 
        self_block = data.ctx.current_block
        self_num = data.ctx.stmt_id

        data = self.visit(ast.stmt, data)

        return data

    def visitDoWhileStmt(self, ast : DoWhileStmt, data):
        self_block = data.ctx.current_block
        self_num = data.ctx.stmt_id

        data = self.visit(ast.stmt, data)

        return data

    def visitVarDecl(self, ast : VarDecl, data : ASTRefactorerData):
        ctx = data.ctx
        if ast.init is None:
          ctx.current_block.stmts.remove(ast)
        else:
          ctx.current_block.stmts[ctx.stmt_id] = AssignStmt(ast, ast.init)   
        return data

    def visitAssignStmt(self, ast : AssignStmt, data):
        return data

class ForToWhile(ASTVisitor):

    '''
      Turn ForStmt to WhileStmt
    '''

    def __init__(self, ast):
        self.ast = ast

    def refactor(self):
        data = ASTRefactorerData(self.ast, ASTRefactorerContext())
        return self.visit(self.ast, data).obj
     
    def visitProgram(self, ast: Program, data : ASTRefactorerData):
        for decl in ast.decls:
          data = self.visit(decl, data)

        return data
    
    def visitFuncDecl(self, ast : FuncDecl, data : ASTRefactorerData):
        for decl in data.obj.decls:
          if decl.name == ast.name:
            decl = FuncDecl(ast.name, ast.rtype, ast.params, ast.inherit, self.visit(ast.body, data))

        return data

    def visitASTBlock(self, ast : Block, data : ASTRefactorerData):
        stmts = ast.stmts
        for i in range(len(stmts)):
          # Set ctx appropriately
          ctx = data.ctx
          ctx.current_block = ast

          ctx.stmt_id = i
          data = self.visit(stmts[i], data)

        return data

    def visitIfStmt(self, ast : IfStmt, data : ASTRefactorerData):
        # Retrieve the ctx
        self_block = data.ctx.current_block
        self_num = data.ctx.stmt_id

        data = self.visit(ast.tstmt, data)
        if ast.fstmt is not None:
          data = self.visit(ast.fstmt, data)

        return data

    def visitWhileStmt(self, ast : WhileStmt, data : ASTRefactorerData):
        self_block = data.ctx.current_block
        self_num = data.ctx.stmt_id

        data = self.visit(ast.stmt, data)

        return data
        
    def visitForStmt(self, ast: ForStmt, data : ASTRefactorerData): 
        self_block = data.ctx.current_block
        self_num = data.ctx.stmt_id

        data = self.visit(ast.stmt, data)
        upd_stmts = [ast.init, WhileStmt(ast.cond, StmtBlock(ast.stmt.stmts + [AssignStmt(ast.init.lhs, ast.upd)]))]

        if self_num == len(self_block.stmts) - 1:
          self_block.stmts = self_block.stmts[:self_num] + upd_stmts
        else:
          self_block.stmts = self_block.stmts[:self_num] + upd_stmts +self_block.stmts[self_num+1:]

        return data

    def visitDoWhileStmt(self, ast : DoWhileStmt, data):
        self_block = data.ctx.current_block
        self_num = data.ctx.stmt_id

        data = self.visit(ast.stmt, data)

        return data

    def visitVarDecl(self, ast : VarDecl, data : ASTRefactorerData):
        return data

    def visitAssignStmt(self, ast : AssignStmt, data):
        return data

class BinExprUnwrapper(ASTVisitor):

    '''
      Unwrap BinExpr
    '''

    def __init__(self, ast):
        self.ast = InforAssigner(ast).assign()

    def refactor(self):
        data = ASTRefactorerData(self.ast, ASTRefactorerContext())
        return self.visit(self.ast, data).obj
     
    def visitProgram(self, ast: Program, data : ASTRefactorerData):
        for decl in ast.decls:
          data = self.visit(decl, data)

        return data
    
    def visitFuncDecl(self, ast : FuncDecl, data : ASTRefactorerData):
        for decl in data.obj.decls:
          if decl.name == ast.name:
            decl = FuncDecl(ast.name, ast.rtype, ast.params, ast.inherit, self.visit(ast.body, data))

        return data

    def visitASTBlock(self, ast : StmtBlock, data : ASTRefactorerData):
        for stmt in ast.stmts:
          data = self.visit(stmt, data)

        return data

    def visitIfStmt(self, ast : IfStmt, data : ASTRefactorerData): 
        data.ctx.current_stmt = ast

        data = self.visit(ast.cond, data)
        data = self.visit(ast.tstmt, data)

        if ast.fstmt is not None:
          data = self.visit(ast.fstmt, data)
        
        data.ctx.used_sym = 0

        return data

    def visitWhileStmt(self, ast : WhileStmt, data : ASTRefactorerData):
        data.ctx.current_stmt = ast

        data = self.visit(ast.cond, data)
        data = self.visit(ast.stmt, data)

        data.ctx.used_sym = 0

        return data
        
    def visitDoWhileStmt(self, ast : DoWhileStmt, data):
        data.ctx.current_stmt = ast
        
        data = self.visit(ast.cond)
        data = self.visit(ast.stmt, data)

        data.ctx.used_sym = 0

        return data

    def visitAssignStmt(self, ast : AssignStmt, data):
        data.ctx.current_stmt = ast

        data = self.visit(ast.rhs, data)
        
        ast.rhs = data.ctx.last_expr

        data.ctx.used_sym = 0

        return data

    def visitBinExpr(self, ast : BinExpr, data : ASTRefactorerData):
      current_stmt = data.ctx.current_stmt

      data = self.visit(ast.left, data)
      left_expr = data.ctx.last_expr

      data = self.visit(ast.right, data)
      right_expr = data.ctx.last_expr

      stmt_id = current_stmt.block.get_index_of_stmt(current_stmt)
      last_expr = Id(f"tmp_{data.ctx.used_sym}")

      current_stmt.block.stmts = current_stmt.block.stmts[:stmt_id] \
                                + [AssignStmt(last_expr, BinExpr(ast.op, left_expr, right_expr))] \
                                + current_stmt.block.stmts[stmt_id:]

      data.ctx.used_sym += 1
      data.ctx.last_expr = last_expr

      return data
      
    def visitUnExpr(self, ast : UnExpr, data : ASTRefactorerData):
      current_stmt = data.ctx.current_stmt

      data = self.visit(ast.val, data)
      val_expr = data.ctx.last_expr

      stmt_id = current_stmt.block.get_index_of_stmt(current_stmt)
      last_expr = Id(f"tmp_{data.ctx.used_sym}")

      block_stmts = current_stmt.block.stmts

      block_stmts = block_stmts[:stmt_id] + [AssignStmt(last_expr, BinExpr(ast.op, left_expr, right_expr))] + block_stmts[stmt_id:]


      data.ctx.used_sym += 1
      data.ctx.last_expr = last_expr

      return data

    def visitId(self, ast : Id, data : ASTRefactorerData):
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
    
    def visitStringLit(self, ast, data : ASTRefactorerData):
      data.ctx.last_expr = ast

      return data

    def visitBooleanLit(self, ast, data : ASTRefactorerData):
      data.ctx.last_expr = ast

      return data

    def visitArrayLit(self, ast, data : ASTRefactorerData):
      for expr in ast.exprlist:
        data = self.visit(expr)
        
      data.ctx.last_expr = ast

      return data

class CFGRefactorer(CFGVisitor):
  '''
  Remove all empty StmtBlock
  '''
  def __init__(self, cfg : CFG):
    self.cfg = cfg

  def refactor(self):
    return self.visit(self.cfg, None)

  def visitCFG(self, cfg : CFG, data):
    for block in cfg.blocks:
      if isinstance(block, AssignStmt) and len(block.stmts) == 0:
        for another_block in cfg.blocks:
          if another_block.id != block.id:
            if another_block.jump.id == block.id:
              another_block.jump = block.next
            if another_block.link.id == block.id:
              another_block.link = block.next
              
            if isinstance(another_block, StmtBlock):
              if another_block.next.id == block.id:
                another_block.next = block.next
            else:
              if another_block.true.id == block.id:
                another_block.true = block.next
              if another_block.false.id == block.id:
                another_block.false = block.next
      cfg.blocks.remove(block)
    return cfg