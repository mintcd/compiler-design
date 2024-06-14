from utils.structures.AST import *
from utils.structures.CFG import *

class Data:
    def __init__(self, obj, ctx):
        self.obj = obj
        self.ctx = ctx

class Visitee:
    def accept(self, visitor, data : Data):
        method_name = 'visit{}'.format(self.__class__.__name__)
        visit_function = getattr(visitor, method_name)
        return visit_function(self, data)

class Visitor:
    def visit(self, visitee, data : Data) ->  Data:
        return visitee.accept(self, data)

class ASTVisitor(Visitor):

    def __init__(self, ast, log_file = None):
        self.ast = ast
        self.log_file = log_file

    def visitProgram(self, ast: Program, data : Data):
        for decl in ast.decls:
            data = self.visit(decl)

        return data

    def visitStmtBlock(self, ast : StmtBlock, data : Data): 
        for stmt in ast.stmts:
            data = self.visit(stmt, data)
        return data
    
########################## DECLARATIONS #################################
    def visitFuncDecl(self, ast: FuncDecl, data : Data):
        return data

    def visitParamDecl(self, ast: ParamDecl, data : Data):
        return data
        
    def visitVarDecl(self, ast: VarDecl, data : Data):
        return data

########################## STATEMENTS ###################################

    def visitAssignStmt(self, ast : AssignStmt, data : Data): 
        return data

    def visitIfStmt(self, ast: IfStmt, data : Data):
        return data

    def visitForStmt(self, ast: ForStmt, data : Data):
        return data

    
    def visitWhileStmt(self, ast: WhileStmt, data : Data):
        return data

    
    def visitDoWhileStmt(self, ast: DoWhileStmt, data : Data):
        return data

    
    def visitBreakStmt(self, ast: BreakStmt, data : Data):
        return data

    
    def visitContinueStmt(self, ast: ContinueStmt, data : Data):
        return data

    
    def visitReturnStmt(self, ast: ReturnStmt, data : Data):
        return data

    
    def visitCallStmt(self, ast: CallStmt, data : Data):
        return data

########################## COMPLEX EXPRESSIONS ##########################
    def visitArrayLit(self, ast: ArrayLit, data : Data):
        return data
        
    def visitFuncCall(self, ast, data : Data):
        return data
    
    def visitArrayCell(self, ast: ArrayCell, data : Data):
        return data

    def visitBinExpr(self, ast: BinExpr, data : Data):
        return data
 
    def visitUnExpr(self, ast: UnExpr, data : Data):
        return data

########################## ATOMIC LITERALS ##############################
    def visitIntegerLit(self, ast: IntegerLit, data : Data):
        return data

    def visitFloatLit(self, ast: FloatLit, data : Data):
        return data
    
    def visitStringLit(self, ast: StringLit, data : Data):
        return data

    def visitBooleanLit(self, ast: BooleanLit, data : Data):
        return data

    def visitId(self, ast: Id, data : Data):
        return data

########################## TYPES ########################################    
    def visitIntegerType(self, ast: IntegerType, data : Data): 
        return data

    def visitFloatType(self, ast: FloatType, data : Data): 
        return data
 
    def visitBooleanType(self, ast: BooleanType, data : Data): 
        return data
 
    def visitStringType(self, ast: StringType, data : Data): 
        return data
 
    def visitArrayType(self, ast: ArrayType, data : Data):
        return data
 
    def visitAutoType(self, ast: AutoType, data : Data):
        return data

    def visitVoidType(self, ast: VoidType, data : Data):
        return data

class CFGVisitor(Visitor):
    def __init__(self, cfg):
        self.ast = cfg

    def visitCFG(self, cfg : CFG, data): 
        for block in cfg.blocks:
            data = self.visit(cfg, data)
        return data
    
    def visitBlock(self, cfg : Block, data):
        if cfg.cond is None:
            for stmt in cfg.stmts:
                data = self.visit(stmt)
        else:
            data = self.visit(cfg.cond)
        return data

    def visitAssignStmt(self, cfg : AssignStmt, data : Data):
        data = self.visit(cfg.lhs, data)
        data = self.visit(cfg.rhs, data)
        return data

    
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
