from utils.visitors import ASTVisitor, CFGVisitor
from utils.structures.CFG import CFG, Block
from utils.structures.AST import *
from typing import List

class ASTRefactorerContext:
  def __init__(self, last_sym : int or None = None):
    self.last_sym = last_sym
    self.used_sym = 0

class ASTRefactorer:
    '''
      1) Eliminates dead code after Return.
      2) Turns Stmt used in IfStmt, WhileStmt and ForStmt to BlockStmt
      3) Turn initiated vardecl to assignstmt with infered type
      4) Turn For to While
      5) Unwrap BinExpr
    '''
    def __init__(self, ast):
        self.ast = ast

    def refactor(self):
        ast = ASTRefactorer23(self.ast).refactor()

        ast = ASTRefactorer4(ast).refactor()

        ast = ASTRefactorer5(ast).refactor()  

        return ast       

class ASTRefactorer23(ASTVisitor):
    def __init__(self, ast):
        self.ast = ast

    def refactor(self):
        return self.visit(self.ast, None)
    
    def visitProgram(self, ast: Program, _):
        return Program([self.visit(decl, _) for decl in ast.decls])
    
    def visitFuncDecl(self, ast : FuncDecl, _):
        return FuncDecl(ast.name, ast.rtype, ast.params, ast.inherit, self.visit(ast.body, _))
    
    def visitVarDecl(self, ast : VarDecl, _):
        if ast.init is not None:
          return AssignStmt(Id(ast.name), ast.init, ast.typ)
        return []

    def visitBlockStmt(self, ast : BlockStmt, _):
        visited_stmts = []
        for stmt in ast.stmts:
          visited_stmt = self.visit(stmt, None)
          if isinstance(visited_stmt, list):
            visited_stmts += visited_stmt
          else:
            visited_stmts += [visited_stmt]
        return BlockStmt(visited_stmts)

    def visitAssignStmt(self, ast : AssignStmt, _):
        return ast

    def visitIfStmt(self, ast : IfStmt, _):
        if not isinstance(ast.tstmt, BlockStmt):
          ast.tstmt = BlockStmt([ast.tstmt])
        if ast.fstmt is not None and not isinstance(ast.fstmt, BlockStmt):
          ast.fstmt = BlockStmt([ast.fstmt])

        return IfStmt(ast.cond, 
                      self.visit(ast.tstmt, _), 
                      self.visit(ast.fstmt, _) if ast.fstmt is not None else None)

    def visitWhileStmt(self, ast : WhileStmt, _):
        if not isinstance(ast.stmt, BlockStmt):
          ast.stmt = BlockStmt([ast.stmt])
   
        return WhileStmt(ast.cond, self.visit(ast.stmt, _))
        
    def visitForStmt(self, ast: ForStmt, _): 
        if not isinstance(ast.tstmt, BlockStmt):
          ast.stmt = BlockStmt([ast.stmt])
        
        return ForStmt(ast.init, ast.cond, ast.upd)

    
    def visitDoWhileStmt(self, ast : DoWhileStmt, _):
      return ast

class ASTRefactorer4(ASTVisitor):
    '''
      Turn For to While
    '''
    def __init__(self, ast):
        self.ast = ast

    def refactor(self):
        return self.visit(self.ast, None)
    
    def visitProgram(self, ast: Program, _):
        return Program([self.visit(decl, _) for decl in ast.decls])
    
    def visitFuncDecl(self, ast : FuncDecl, _):
        return FuncDecl(ast.name, ast.rtype, ast.params, ast.inherit, self.visit(ast.body, _))
    
    def visitVarDecl(self, ast : VarDecl, _):
        return ast

    def visitBlockStmt(self, ast : BlockStmt, _):
        visited_stmts = []
        for stmt in ast.stmts:
          visited_stmt = self.visit(stmt, None)
          if isinstance(visited_stmt, list):
            visited_stmts += visited_stmt
          else:
            visited_stmts += [visited_stmt]
        return BlockStmt(visited_stmts)

    def visitAssignStmt(self, ast : AssignStmt, _):
        return ast

    def visitIfStmt(self, ast : IfStmt, _):
        return IfStmt(ast.cond, 
                      self.visit(ast.tstmt, _), 
                      self.visit(ast.fstmt, _) if ast.fstmt is not None else None)

    def visitWhileStmt(self, ast : WhileStmt, _):   
        return WhileStmt(ast.cond, self.visit(ast.stmt, _))
    
    def visitDoWhileStmt(self, ast : DoWhileStmt, _):
      return ast 

class ASTRefactorer5(ASTVisitor):
    def __init__(self, ast):
        self.ast = ast

    def refactor(self):
        return self.visit(self.ast, ASTRefactorerContext())
    
    def visitProgram(self, ast: Program, ctx : ASTRefactorerContext):
        return Program([self.visit(decl, ctx) for decl in ast.decls])
    
    def visitFuncDecl(self, ast : FuncDecl, ctx : ASTRefactorerContext):
        return FuncDecl(ast.name, ast.rtype, ast.params, ast.inherit, self.visit(ast.body, ctx))
    
    def visitBlockStmt(self, ast : BlockStmt, ctx : ASTRefactorerContext):
        visited_stmts = []
        for stmt in ast.stmts:
          visited_stmt = self.visit(stmt, ctx)
          # print(146, visited_stmt)
          if isinstance(visited_stmt, list):
            visited_stmts += visited_stmt
          else:
            visited_stmts += [visited_stmt]
        return BlockStmt(visited_stmts)

    def visitAssignStmt(self, ast : AssignStmt, ctx : ASTRefactorerContext):
        # print(155, ast.rhs)
        visited_rhs = self.visit(ast.rhs, ctx)
        if len(visited_rhs) > 0:
          return visited_rhs + [AssignStmt(ast.lhs, visited_rhs[-1].lhs)]
        # print(158, visited_rhs, ast)
        return ast

    def visitIfStmt(self, ast : IfStmt, ctx : ASTRefactorerContext):
        visited_cond = self.visit(ast.cond, ctx)
        visited_tstmt = self.visit(ast.tstmt, ctx)
        visited_fstmt = self.visit(ast.fstmt, ctx) if ast.fstmt is not None else None

        if len(visited_cond) > 0:
          return visited_rhs + [IfStmt(visited_rhs[-1].name, visited_tstmt, visited_fstmt)]

        return IfStmt(ast.cond, visited_tstmt, visited_fstmt)

    def visitWhileStmt(self, ast : WhileStmt, ctx : ASTRefactorerContext):
        visited_cond = self.visit(ast.cond, ctx)
        visited_stmt = self.visit(ast.stmt, ctx)

        if len(visited_cond) > 0:
          return visited_cond + [WhileStmt(visited_rhs[-1].name, BlockStmt(visited_stmt.stmts + visited_cond))]

        return WhileStmt(ast.cond, visited_stmt)
    
    def visitDoWhileStmt(self, ast : DoWhileStmt, ctx : ASTRefactorerContext):
        visited_cond = self.visit(ast.cond, ctx)
        visited_stmt = self.visit(ast.stmt, ctx)

        if len(visited_cond) > 0:
          return visited_cond + [DoWhileStmt(visited_rhs[-1].name, BlockStmt(visited_stmt.stmts + visited_cond))]

        return DoWhileStmt(ast.cond, visited_stmt)

    def visitBinExpr(self, ast : BinExpr, ctx : ASTRefactorerContext):
      visited_left = self.visit(ast.left, ctx)
      left_sym = ctx.last_sym

      visited_right = self.visit(ast.right, ctx)
      right_sym = ctx.last_sym

      sym_to_use = Id(f"{ctx.used_sym}_tmp")
      ctx.used_sym += 1
      ctx.last_sym = sym_to_use

      return visited_left + visited_right + [AssignStmt(sym_to_use, BinExpr(ast.op, left_sym, right_sym))]

    def visitUnExpr(self, ast : UnExpr, ctx : ASTRefactorerContext):
      visited_val = self.visit(ast.val, ctx)
      val_sym = ctx.last_sym

      sym_to_use = f"{ctx.used_sym}_tmp"
      ctx.used_sym += 1

      return visited_val + [AssignStmt(Id(sym_to_use), UnExpr(ast.op, val_sym))]

    def visitId(self, ast : Id, ctx : ASTRefactorerContext):
      ctx.last_sym = ast
      return []

    def visitIntegerLit(self, ast : IntegerLit, ctx : ASTRefactorerContext):
      return []


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