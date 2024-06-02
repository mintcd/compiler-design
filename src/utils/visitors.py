from utils.visitor_pattern import Visitor, Data
from utils.structures.CFG import *
from utils.structures.AST import *

class ASTVisitor(Visitor):

    def __init__(self, ast):
        self.ast = ast

    def visitFloatType(self, ast : FloatType, data : Data): 
        return data
    
    def visitIntegerType(self, ast : IntegerType, data : Data): 
        return data
 
    def visitBooleanType(self, ast, data : Data): 
        return data
 
    def visitStringType(self, ast, data : Data): 
        return data
 
    def visitArrayType(self, ast, data : Data):
        return data
 
    def visitAutoType(self, ast, data : Data):
        return data

    def visitVoidType(self, ast, data : Data):
        return data
 
    def visitBinExpr(self, ast, data : Data):
        return data
 
    def visitUnExpr(self, ast, data : Data):
        return data
  
    def visitId(self, ast, data : Data):
        return data
   
    def visitArrayCell(self, ast, data : Data):
        return data

    def visitIntegerLit(self, ast, data : Data):
        return data

    def visitFloatLit(self, ast, data : Data):
        return data
    
    def visitStringLit(self, ast, data : Data):
        return data

    def visitBooleanLit(self, ast, data : Data):
        return data

    def visitArrayLit(self, ast, data : Data):
        return data

    def visitFuncCall(self, ast, data : Data):
        return data

    def visitAssignStmt(self, ast : AssignStmt, data : Data): 
        return data

    def visitIfStmt(self, ast, data : Data):
        return data

    def visitForStmt(self, ast, data : Data):
        return data

    
    def visitWhileStmt(self, ast, data : Data):
        return data

    
    def visitDoWhileStmt(self, ast, data : Data):
        return data

    
    def visitBreakStmt(self, ast, data : Data):
        return data

    
    def visitContinueStmt(self, ast, data : Data):
        return data

    
    def visitReturnStmt(self, ast, data : Data):
        return data

    
    def visitCallStmt(self, ast, data : Data):
        return data

    
    def visitVarDecl(self, ast, data : Data):
        return data

    
    def visitParamDecl(self, ast, data : Data):
        return data

    def visitStmtBlock(self, ast : Block, data : Data): 
        return data
    
    def visitFuncDecl(self, ast, data : Data):
        return data

    
    def visitProgram(self, ast, data : Data):
        return data

class CFGVisitor(Visitor):

    def visitCFG(self, cfg : CFG, data): 
        return data
    
    def visitBlock(self, cfg : Block, data):
        return data

    def visitAssignStmt(self, cfg : AssignStmt, data): return data

    
    def visitVarDecl(self, cfg : VarDecl, data):
        return data

    def visitBinExpr(self, ast, data):
        return data
 
    def visitUnExpr(self, ast, data):
        return data
  
    def visitId(self, ast, data):
        return data
   
    def visitArrayCell(self, ast, data):
        return data

    def visitArrayLit(self, ast, data):
        return data

    def visitIntegerLit(self, ast, data):
        return data

    def visitFloatLit(self, ast, data):
        return data
    
    def visitStringLit(self, ast, data):
        return data

    def visitBooleanLit(self, ast, data):
        return data
