from utils.visitor_pattern import Visitor, VisitData
from utils.structures.CFG import *
from utils.structures.AST import *

class ASTVisitor(Visitor):

    def __init__(self, ast):
        self.ast = ast

    def visitFloatType(self, ast : FloatType, data : VisitData): 
        return data
    
    def visitIntegerType(self, ast : IntegerType, data : VisitData): 
        return data
 
    def visitBooleanType(self, ast, data : VisitData): 
        return data
 
    def visitStringType(self, ast, data : VisitData): 
        return data
 
    def visitArrayType(self, ast, data : VisitData):
        return data
 
    def visitAutoType(self, ast, data : VisitData):
        return data

    def visitVoidType(self, ast, data : VisitData):
        return data
 
    def visitBinExpr(self, ast, data : VisitData):
        return data
 
    def visitUnExpr(self, ast, data : VisitData):
        return data
  
    def visitId(self, ast, data : VisitData):
        return data
   
    def visitArrayCell(self, ast, data : VisitData):
        return data

    def visitIntegerLit(self, ast, data : VisitData):
        return data

    def visitFloatLit(self, ast, data : VisitData):
        return data
    
    def visitStringLit(self, ast, data : VisitData):
        return data

    def visitBooleanLit(self, ast, data : VisitData):
        return data

    def visitArrayLit(self, ast, data : VisitData):
        return data

    def visitFuncCall(self, ast, data : VisitData):
        return data

    def visitAssignStmt(self, ast : AssignStmt, data : VisitData): 
        return data
 
    def visitASTBlock(self, ast : Block, data : VisitData): 
        return data

    def visitIfStmt(self, ast, data : VisitData):
        return data

    def visitForStmt(self, ast, data : VisitData):
        return data

    
    def visitWhileStmt(self, ast, data : VisitData):
        return data

    
    def visitDoWhileStmt(self, ast, data : VisitData):
        return data

    
    def visitBreakStmt(self, ast, data : VisitData):
        return data

    
    def visitContinueStmt(self, ast, data : VisitData):
        return data

    
    def visitReturnStmt(self, ast, data : VisitData):
        return data

    
    def visitCallStmt(self, ast, data : VisitData):
        return data

    
    def visitVarDecl(self, ast, data : VisitData):
        return data

    
    def visitParamDecl(self, ast, data : VisitData):
        return data

    
    def visitFuncDecl(self, ast, data : VisitData):
        return data

    
    def visitProgram(self, ast, data : VisitData):
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
