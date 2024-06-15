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
    def visitInteger(self, ast, data : Data):
        data.obj = Integer()
        data.ctx.last_type = Integer()
        return data

    def visitFloat(self, ast, data : Data):
        data.obj = Float()
        data.ctx.last_type = Float()
        return data
    
    def visitString(self, ast, data : Data):
        data.obj = String()
        data.ctx.last_type = String()
        return data

    def visitBoolean(self, ast, data : Data):
        data.obj = Boolean()
        data.ctx.last_type = Boolean()
        return data

    def visitArray(self, ast, data : Data):
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
