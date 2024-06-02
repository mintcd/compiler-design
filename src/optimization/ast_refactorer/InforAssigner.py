class InforAssigner(ASTVisitor):
    '''
      Assign a unique id to each Stmt
      Assign parent block to each Stmt
    '''

    def __init__(self, ast):
        self.ast = ast

    def assign(self):
        data = ASTRefactorerData(self.ast, ASTRefactorerContext())
        return self.visit(self.ast, data).obj
    
    def visitProgram(self, ast: Program, data : ASTRefactorerData):
        for decl in ast.decls:
          if isinstance(decl, FuncDecl):
            data = self.visit(decl, data)
        return data
    
    def visitFuncDecl(self, ast : FuncDecl, data : ASTRefactorerData):
        data = self.visit(ast.body, data)

        return data

    def visitASTBlock(self, ast : Block, data : ASTRefactorerData):
        # Create a new env
        data.ctx.current_block = ast
        parent_id = data.ctx.current_id
        data.ctx.current_id = parent_id + [0]

        for stmt in ast.stmts:
          data = self.visit(stmt, data)
        
        # Retend the last env
        data.ctx.current_id = parent_id

        return data
        
    def visitIfStmt(self, ast : IfStmt, data : ASTRefactorerData):
        parent_id = data.ctx.current_id
        ast.id = copy.deepcopy(parent_id)
        ast.block = data.ctx.current_block

        data = self.visit(ast.tstmt, data)
        if ast.fstmt is not None:
          data = self.visit(ast.fstmt, data)

        parent_id[-1] += 1

        return data

    def visitWhileStmt(self, ast : WhileStmt, data : ASTRefactorerData):
        parent_id = data.ctx.current_id
        ast.id = copy.deepcopy(parent_id)
        ast.block = data.ctx.current_block
        data = self.visit(ast.stmt, data)

        parent_id[-1] += 1

        return data
        
    def visitForStmt(self, ast: ForStmt, data): 
        parent_id = data.ctx.current_id
        ast.id = copy.deepcopy(parent_id)
        ast.block = data.ctx.current_block
        data = self.visit(ast.stmt, data)

        parent_id[-1] += 1

        return data

    def visitDoWhileStmt(self, ast : DoWhileStmt, data):
        parent_id = data.ctx.current_id
        ast.id = copy.deepcopy(parent_id)
        ast.block = data.ctx.current_block
        data = self.visit(ast.stmt, data)

        parent_id[-1] += 1

        return data

    def visitVarDecl(self, ast : VarDecl, data):
        parent_id = data.ctx.current_id
        ast.id = copy.deepcopy(parent_id)
        parent_id[-1] += 1
        ast.block = data.ctx.current_block

        return data

    def visitAssignStmt(self, ast : AssignStmt, data):
        parent_id = data.ctx.current_id
        ast.id = copy.deepcopy(parent_id)
        parent_id[-1] += 1
        ast.block = data.ctx.current_block

        return data
