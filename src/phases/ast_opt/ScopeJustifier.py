from utils.visitors import ASTVisitor
from utils.structures.AST import *

from utils.assist_visitors.ASTInforAssigner import ASTInforAssigner
from utils.assist_visitors.SymbolTableBuilder import SymbolTableBuilder

from utils.structures.SymbolTable import SymbolTable

class Context:
    def __init__(self, symbols : List[VarDecl] or None = None, current_stmt : Stmt or None = None):
        self.symbols = symbols if symbols is not None else []
        self.current_stmt = current_stmt if current_stmt is not None else None

    
    def __str__(self):
        return f"[{', '.join(str(symbol) for symbol in self.symbols)}]"

class Data:
  def __init__(self, obj : Program, ctx : Context):
    self.obj = obj
    self.ctx = ctx
  
  def __str__(self):
    return str(self.ctx)

  
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

    def __init__(self, ast, log_file = None):
        self.ast = ASTInforAssigner(ast).assign()
        self.st = SymbolTableBuilder(ast, log_file).build()
        self.log_file = log_file

    def justify(self):
        data = Data(self.ast, Context())
        justified_ast = self.visit(self.ast, data).obj

        if self.log_file is not None:
          with open(self.log_file, 'a') as file:
            file.write("AST after justifying symbol scope\n")
            file.write(f"{str(justified_ast)}\n\n")
            file.write("--------------------------------------------------------\n\n")

        return justified_ast
    
    def visitProgram(self, ast: Program, data : Data):
        for sym in ast.decls:
          data = self.visit(sym, data)
        return data
    
    def visitFuncDecl(self, ast : FuncDecl, data : Data):
        data = self.visit(ast.body, data)

        return data

    def visitStmtBlock(self, ast : StmtBlock, data : Data):
        for stmt in ast.stmts:
          data = self.visit(stmt, data)
        
        return data
        
    def visitIfStmt(self, ast : IfStmt, data : Data):

        data.ctx.current_stmt = ast
        data = self.visit(ast.cond, data)

        data.ctx.current_stmt = ast
        data = self.visit(ast.tstmt, data)
        if ast.fstmt is not None:
          data.ctx.current_stmt = ast
          data = self.visit(ast.fstmt, data)

        return data

    def visitWhileStmt(self, ast : WhileStmt, data : Data):
        data.ctx.current_stmt = ast
        data = self.visit(ast.cond, data)

        data.ctx.current_stmt = ast
        data = self.visit(ast.stmt, data)

        return data
        
    # def visitForStmt(self, ast: ForStmt, data): 
    #     data = self.visit(ast.init, data)
    #     data = self.visit(ast.cond, data)
    #     data = self.visit(ast.upd, data)
    #     data = self.visit(ast.stmt, data)

    #     return data

    def visitDoWhileStmt(self, ast : DoWhileStmt, data):
        data.ctx.current_stmt = ast
        data = self.visit(ast.cond)

        data.ctx.current_stmt = ast
        data = self.visit(ast.stmt, data)

        return data

    def visitAssignStmt(self, ast : AssignStmt, data : Data):
        data.ctx.current_stmt = ast
        data = self.visit(ast.lhs, data)

        data.ctx.current_stmt = ast
        data = self.visit(ast.rhs, data)

        return data

    def visitVarDecl(self, ast : VarDecl, data):
        return data

    def visitBinExpr(self, ast : BinExpr, data):
        data = self.visit(ast.left, data)
        data = self.visit(ast.right, data)

        return data
    
    def visitUnExpr(self, ast : UnExpr, data):
        data = self.visit(ast.val, data)

        return data

    def visitArrayCell(self, ast : ArrayCell, data : Data):
        current_stmt = data.ctx.current_stmt
        # choose symbols from outer scopes to this scope
        similar_syms = [sym for sym in self.st.symbols if sym.name == ast.name and len(sym.scope) < len(current_stmt.id)]
        similar_syms = sorted(similar_syms, key= lambda sym: len(sym.scope), reverse=True)

        for sym in similar_syms:
          if current_stmt.id[:len(sym.scope)] == sym.scope:
            ast.id = sym.id
            break

        for expr in ast.cell:
          data = self.visit(expr, data)

        return data

    def visitId(self, ast : Id, data : Data):
        current_stmt = data.ctx.current_stmt
        # choose symbols from outer scopes to this scope
        similar_syms = [sym for sym in self.st.symbols if sym.name == ast.name and len(sym.scope) < len(current_stmt.id)]
        similar_syms = sorted(similar_syms, key= lambda sym: len(sym.scope), reverse=True)

        for sym in similar_syms:
          if current_stmt.id[:len(sym.scope)] == sym.scope:
            ast.id = sym.id
            break

        return data

    def visitInteger(self, ast, data : Data):
        return data

    def visitFloat(self, ast, data : Data):
        return data
    
    def visitString(self, ast, data : Data):
        return data

    def visitBoolean(self, ast, data : Data):
        return data
