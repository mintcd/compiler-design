from utils.visitors import ASTVisitor
from utils.structures.AST import *
from optimization.ast_refactor.InforAssigner import InforAssigner
from utils.structures.SymbolTable import Symbol


class Context:
    def __init__(self, symbols : List[VarDecl] or None = None):
        self.symbols = symbols if symbols is not None else []

class Data:
  def __init__(self, obj : Program, ctx : Context or None = None):
    self.obj = obj
    self.ctx = Context() if ctx is None else ctx

class ScopeJustifier(ASTVisitor):
    '''
      Justify same symbol name
      Example: {
        a = 1;
        {
          a = 2;
        }
        } ---> {
          0a = 1;
          {
            1a = 2;
          }
        }
    '''

    def __init__(self, ast):
        self.ast = InforAssigner(ast).assign()

    def justify(self):
        data = Data(self.ast, Context())
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
        data = self.visit(ast.cond, data)

        data = self.visit(ast.tstmt, data)
        if ast.fstmt is not None:
          data = self.visit(ast.fstmt, data)

        return data

    def visitWhileStmt(self, ast : WhileStmt, data : Data):
        data = self.visit(ast.cond, data)
        data = self.visit(ast.stmt, data)

        return data
        
    def visitForStmt(self, ast: ForStmt, data): 
        data = self.visit(ast.init, data)
        data = self.visit(ast.cond, data)
        data = self.visit(ast.upd, data)
        data = self.visit(ast.stmt, data)

        return data

    def visitDoWhileStmt(self, ast : DoWhileStmt, data):
        data = self.visit(ast.cond)
        data = self.visit(ast.stmt, data)

        return data

    def visitAssignStmt(self, ast : AssignStmt, data : Data):
        data = self.visit(ast.lhs, data)
        data = self.visit(ast.rhs, data)

        return data

    def visitVarDecl(self, ast : VarDecl, data):
        data.ctx.symbols.append(Symbol(ast.id, ast.name, ast.typ))
        ast.name = f"{ast.name}_{ast.id}"

        return data

    def visitBinExpr(self, ast : BinExpr, data):
        data = self.visit(ast.left, data)
        data = self.visit(ast.right, data)

        return data
    
    def visitUnExpr(self, ast : UnExpr, data):
        data = self.visit(ast.val, data)

        return data

    def visitId(self, ast : Id, data : Data):
        # choose symbols from outer scopes to this scope
        similar_syms = [decl for decl in data.ctx.symbols if decl.name == ast.name and len(decl.id) <= len(ast.stmt.id)]
        similar_syms = sorted(similar_syms, key= lambda decl: len(decl.id), reverse=True)

        for sym in similar_syms:
          if ast.stmt.id == sym.id or ast.stmt.id[:len(sym.id)-1] == sym.id[:len(sym.id)-1]:
            ast.name = f"{ast.name}_{sym.id}"
            return data

    def visitIntegerLit(self, ast, data : Data):
        return data

    def visitFloatLit(self, ast, data : Data):
        return data
    
    def visitStringLit(self, ast, data : Data):
        return data

    def visitBooleanLit(self, ast, data : Data):
        return data
