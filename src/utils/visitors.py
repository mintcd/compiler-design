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
    def visitArray(self, ast: Array, data : Data):
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
    def visitInteger(self, ast: Integer, data : Data):
        return data

    def visitFloat(self, ast: Float, data : Data):
        return data
    
    def visitString(self, ast: String, data : Data):
        return data

    def visitBoolean(self, ast: Boolean, data : Data):
        return data

    def visitId(self, ast: Id, data : Data):
        return data

class CFGVisitor(Visitor):
    def __init__(self, cfg, st, log_file = None):
        self.cfg = cfg
        self.st = st
        self.log_file = log_file

    def visitCFG(self, cfg : CFG, data): 
        for block in cfg.blocks:
            data = self.visit(block, data)
        return data
    
    def visitBlock(self, cfg : Block, data):
        if cfg.cond is None:
            for stmt in cfg.stmts:
                data = self.visit(stmt, data)
        else:
            data = self.visit(cfg.cond, data)
        return data

    def visitAssignStmt(self, cfg : AssignStmt, data : Data):
        data = self.visit(cfg.lhs, data)
        data = self.visit(cfg.rhs, data)
        return data

############################ COMPLEX EXPRESSIONS #######################

    def visitBinExpr(self, cfg: BinExpr, data):
        return data
 
    def visitUnExpr(self, cfg, data):
        return data
   
    def visitArrayCell(cfg, ast, data):
        return data

    def visitArray(self, cfg, data):
        return data

############################ ATOMIC EXPRESSIONS ########################

    def visitId(self, cfg: Id, data):
        return data

    def visitInteger(self, cfg: Integer, data):
        return data

    def visitFloat(self, cfg: Float, data):
        return data
    
    def visitString(self, cfg: String, data):
        return data

    def visitBoolean(self, cfg: Boolean, data):
        return data
