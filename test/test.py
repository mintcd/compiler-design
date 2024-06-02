class ASTRefactorer5(ASTVisitor):
    '''
      Unwrap Binexpr
    '''
    def __init__(self, ast):
        self.ast = ast

    def refactor(self):
        return self.visit(self.ast, ASTRefactorerContext())
    
    def visitProgram(self, ast: Program, ctx : ASTRefactorerContext):
        return Program([self.visit(decl, ctx) for decl in ast.decls])
    
    def visitFuncDecl(self, ast : FuncDecl, ctx : ASTRefactorerContext):
        return FuncDecl(ast.name, ast.rtype, ast.params, ast.inherit, self.visit(ast.body, ctx))
    
    def visitBlock(self, ast : Block, ctx : ASTRefactorerContext):
        visited_stmts = []
        for stmt in ast.stmts:
          visited_stmt = self.visit(stmt, ctx)
          # print(146, visited_stmt)
          if isinstance(visited_stmt, list):
            visited_stmts += visited_stmt
          else:
            visited_stmts += [visited_stmt]
        return Block(visited_stmts)

    def visitAssignStmt(self, ast : AssignStmt, ctx : ASTRefactorerContext):
        ctx.last_sym = None
        visited_rhs = self.visit(ast.rhs, ctx)
        if ctx.last_sym is not None:
          return visited_rhs + [AssignStmt(ast.lhs, visited_rhs[-1].lhs)]
        return ast

    def visitIfStmt(self, ast : IfStmt, ctx : ASTRefactorerContext):
        visited_cond = self.visit(ast.cond, ctx)
        visited_tstmt = self.visit(ast.tstmt, ctx)
        visited_fstmt = self.visit(ast.fstmt, ctx) if ast.fstmt is not None else None

        if len(visited_cond) > 0:
          return visited_rhs + [IfStmt(visited_rhs[-1].name, visited_tstmt, visited_fstmt)]

        return IfStmt(ast.cond, visited_tstmt, visited_fstmt)

    def visitWhileStmt(self, ast : WhileStmt, ctx : ASTRefactorerContext):
        visited_stmt = self.visit(ast.stmt, ctx)

        ctx.last_sym = None
        visited_cond = self.visit(ast.cond, ctx)

        if ctx.last_sym is not None:
          return visited_cond + [WhileStmt(visited_cond[-1].lhs, Block(visited_stmt.stmts + visited_cond))]

        return WhileStmt(ast.cond, visited_stmt)
    
    def visitDoWhileStmt(self, ast : DoWhileStmt, ctx : ASTRefactorerContext):
        visited_cond = self.visit(ast.cond, ctx)
        visited_stmt = self.visit(ast.stmt, ctx)

        if len(visited_cond) > 0:
          return visited_cond + [DoWhileStmt(visited_rhs[-1].name, Block(visited_stmt.stmts + visited_cond))]

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

    def visitFloatLit(self, ast : FloatLit, ctx : ASTRefactorerContext):
      return []

    def visitBooleanLit(self, ast : BooleanLit, ctx : ASTRefactorerContext):
      return []

    def visitStringLit(self, ast : StringLit, ctx : ASTRefactorerContext):
      return []

    def visitArrayLit(self, ast : ArrayLit, ctx : ASTRefactorerContext):
      last_stmts = []
      for expr in ast.explist:
        visited_expr = self.visit(expr, ctx)
        if len(visited_expr) > 0:
          last_stmts += visited_expr
          expr = Id(ctx.last_sym)
      return last_stmts

    def visitArrayCell(self, ast : ArrayCell, ctx : ASTRefactorerContext):
      last_stmts = []
      for expr in ast.cell:
        visited_expr = self.visit(expr, ctx)
        if len(visited_expr) > 0:
          last_stmts += visited_expr
          expr = Id(ctx.last_sym)
      return last_stmts + []

