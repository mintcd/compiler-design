from utils.visitors import ASTVisitor
from utils.structures.AST import *
from utils.structures.SymbolTable import SymbolTable

class Context:
  def __init__(self, last_type: Type or None  = None):
    self.last_type = last_type

class Data:
  def __init__(self, obj: Type or None = None, ctx: Context or None = None):
    self.obj = obj
    self.ctx = Context()

class TypeGetter(ASTVisitor):
    '''
      Return the visitee datatype.
      Input:
        ast: AST
        st (optional): the symbol table
    '''
    def __init__(self, ast, st):
        self.ast = ast
        self.st = st

    def get(self, node):
      data = Data()
      return self.visit(node, data).obj

    ################################ LITERALS ############################
    def visitIntegerLit(self, ast, data : Data):
        data.obj = IntegerType()
        data.ctx.last_type = IntegerType()
        return data

    def visitFloatLit(self, ast, data : Data):
        data.obj = FloatType()
        data.ctx.last_type = FloatType()
        return data
    
    def visitStringLit(self, ast, data : Data):
        data.obj = StringType()
        data.ctx.last_type = StringType()
        return data

    def visitBooleanLit(self, ast, data : Data):
        data.obj = BooleanType()
        data.ctx.last_type = BooleanType()
        return data

    def visitArrayLit(self, ast, data : Data):
        return data

    ################################## OTHER EXPRESSIONS ################################

    def visitId(self, ast: Id, data : Data):
        symbol_datatype = self.st.get_symbol(ast.name, ast.id).datatype
        data.obj = symbol_datatype
        data.ctx.last_type = symbol_datatype
        return data
    
    def visitArrayCell(self, ast: ArrayCell, data : Data):
        typ = self.st.get_symbol(ast.name, ast.id)
        data.obj = symbol_datatype
        data.ctx.last_type = symbol_datatype
        return data

    def visitBinExpr(self, ast: BinExpr, data : Data):
        left_type = self.visit(ast.left, data).obj
        right_type = self.visit(ast.left, data).obj

        inferred_type = infer_type(left_type, right_type)
        data.obj = inferred_type
        data.ctx.last_type = inferred_type

        return data
 
    def visitUnExpr(self, ast: UnExpr, data : Data):
        typ = self.visit(ast.val, data).obj
        data.obj = typ
        data.ctx.last_type = typ

        return data

    def visitFuncCall(self, ast, data : Data):
        symbol_datatype = self.st.get_symbol(ast.name, ast.id).datatype
        data.obj = symbol_datatype
        data.ctx.last_type = symbol_datatype
        return data
