from typing import List
from StaticError import *
from utils.visitors import ASTVisitor
from utils.structures.AST import *
from utils.structures.SymbolTable import *


     
class GlobalSymbolAdder(Visitor):
    
    def __init__(self, ast):
        self.ast = ast

    def add(self, ast):
        return self.visitProgram(ast, SymbolTable())
    
    def visitProgram(self, ast: Program, st: SymbolTable):
        for decl in ast.decls:
            st = self.visit(ast, st)

        main = st.find_symbol("main")

        if main is None or main.symbol_type is not "func":
            raise NoEntryPoint()

        return st
    
    def visitFuncDecl(self, ast : FuncDecl, st : SymbolTable):
        if st.find_symbol(ast.name) is not None:
            raise Redeclared(Function(), ast.name)
        return st.add_symbol(FuncSym(ast.name, ast.rtype, st.context.scope, st.context.line_in_scope, ast.params))
    
    def visitVarDecl(self, ast : VarDecl, st : SymbolTable):
        if st.find_symbol(ast.name) is not None:
            raise Redeclared(Function(), ast.name)
        return st.add_symbol(FuncSym(ast.name, ast.typ, st.context.scope, st.context.line_in_scope, ast.init))
    
    def visitAssignStmt(self, ast, param):
        raise ContextError("Statements rather than variable declaration not allowed in global scope")
   
    def visitBlockStmt(self, ast, param):
        raise ContextError("Statements rather than variable declaration not allowed in global scope")

    def visitIfStmt(self, ast, param):
        raise ContextError("Statements rather than variable declaration not allowed in global scope")
 
    def visitForStmt(self, ast, param):
        raise ContextError("Statements rather than variable declaration not allowed in global scope")
 
    def visitWhileStmt(self, ast, param):
        raise ContextError("Statements rather than variable declaration not allowed in global scope")
   
    def visitDoWhileStmt(self, ast, param):
        raise ContextError("Statements rather than variable declaration not allowed in global scope")

    def visitBreakStmt(self, ast, param):
        raise ContextError("Statements rather than variable declaration not allowed in global scope")
 
    def visitContinueStmt(self, ast, param):
        raise ContextError("Statements rather than variable declaration not allowed in global scope")
  
    def visitReturnStmt(self, ast, param):
        raise ContextError("Statements rather than variable declaration not allowed in global scope")

    def visitCallStmt(self, ast, param):
        raise ContextError("Statements rather than variable declaration not allowed in global scope")

class StaticChecker(Visitor):

    def __init__(self, ast):
        self.ast = ast
 
    def check(self):
        st = GlobalSymbolAdder(self.ast).add()
        return self.visitProgram(self.ast, st)
    
    def visit(self, ast, param = None) -> SymbolTable:
        return ast.accept(self, param)

    def visitArrayLit(self, ast : ArrayLit, st : SymbolTable):
        """ All elements must be of the same type and not be AutoType"""
        typ = AutoType()
        for expr in ast.explist:
            st, exptyp = self.visit(exp, st)
            # Element is invalid
            if type(exptyp) is IllegalType: 
                return st, IllegalType()
            elif type(typ) is AutoType: 
                typ = exptyp
            elif type(exptyp) is AutoType: 
                exptyp = Utils.infer(exp.name, typ, st)
            elif type(exp) is not type(exptyp) or type(exp) != type(exptyp): 
                return st, IllegalType()                   

        # Elements are arrays
        if type(typ) is ArrayType:
            return st.update_current_datatype(ArrayType([len(ast.explist)] + typ.dimensions, typ.typ))
        return st.update_current_datatype(ArrayType([len(ast.explist)], typ))

    def visitId(self, ast : Id, st: SymbolTable):
        symbol = st.find_symbol(ast.name)
        if symbol is None:
            raise Undeclared(Identifier(), ast.name)
        return st.update_current_datatype(symbol.datatype)

    def visitArrayCell(self, ast : ArrayCell, st : SymbolTable):
        sym = Utils.findVar(ast.name, st)
        if not sym: 
            raise Undeclared(Identifier(), ast.name)
        if type(sym) not in [VarSym, ParaSym] or type(sym.typ) is not ArrayType: raise TypeMismatchInExpression(ast)

        if len(ast.cell) > len(sym.typ.dimensions): raise TypeMismatchInExpression(ast)

        for idx in ast.cell:
            st, idxtype = self.visit(idx, st)
            if type(idxtype) is AutoType:
                if type(idx) is FuncCall: 
                    Utils.findFunc(idx.name, st).typ = IntegerType()
                else: Utils.findVar(idx.name, st).typ = IntegerType()
            elif type(idxtype) is not IntegerType:
                raise TypeMismatchInExpression(ast)
            
        subdim = sym.typ.dimensions[len(ast.cell):]
        if len(subdim) == 0: return st, sym.typ.typ
        return st, ArrayType(subdim, sym.typ.typ)

    def visitBinExpr(self, ast : BinExpr, st : SymbolTable):
        st, rtype = self.visit(ast.right, st)
        st, ltype = self.visit(ast.left, st)
        
        # One is AutoType, infer the other
        if type(rtype) is AutoType:
            Utils.infer(ast.right.name, ltype, st)
            rtype = ltype
            
        if type(ltype) is AutoType:
            Utils.infer(ast.left.name, rtype, st)
            ltype = rtype

        if ast.op in ["+", "-", "*"]:
            if type(ltype) not in [IntegerType, FloatType] or type(rtype) not in [IntegerType, FloatType]: raise TypeMismatchInExpression(ast)
            if FloatType in [type(ltype), type(rtype)]: return st, FloatType()
            return st, IntegerType()
        elif ast.op == "/":
            if type(rtype) not in [IntegerType, FloatType] or type(ltype) not in [IntegerType, FloatType]: raise TypeMismatchInExpression(ast)
            return st, FloatType()
        elif ast.op == "%":
            if type(rtype) is not IntegerType or type(ltype) is not IntegerType: raise TypeMismatchInExpression(ast)
            return st, IntegerType()
        elif ast.op in ["&&", "||"]:
            if type(rtype) is not BooleanType or type(ltype) is not BooleanType: raise TypeMismatchInExpression(ast)
            return st, BooleanType()
        elif ast.op == "::":
            if type(rtype) is not StringType or type(ltype) is not StringType: raise TypeMismatchInExpression(ast)
            return st, StringType()
        elif ast.op in ["==", "!="]:
            if type(rtype) is not type(ltype): raise TypeMismatchInExpression(ast)
            if ltype not in [IntegerType, BooleanType]: raise TypeMismatchInExpression(ast)
            return st, BooleanType()
        elif ast.op in ["<", ">", "<=", ">="]:
            if type(rtype) not in [IntegerType, FloatType] or type(ltype) not in [IntegerType, FloatType]: raise TypeMismatchInExpression(ast)
            return st, BooleanType()

    def visitUnExpr(self, ast, st):
        st, typ = self.visit(ast.val, st)
        if ast.op == "-":
            if type(typ) is AutoType: 
                typ = Utils.infer(ast.val.name, IntegerType(), st)
            elif type(typ) not in [IntegerType, FloatType]: raise TypeMismatchInExpression(ast)
            return st, typ
        elif ast.op == "!":
            if type(typ) is AutoType: 
                typ = Utils.infer(ast.val.name, BooleanType(), st)
            elif type(typ) is not BooleanType: raise TypeMismatchInExpression(ast)
            return st, BooleanType()

    def visitFuncCall(self, ast: FuncCall, st: SymbolTable):
        # Check if there is callee
        funcsym = Utils.findFunc(ast.name, st)
        if not funcsym: raise Undeclared(Function(), ast.name)
        if type(funcsym.typ) is VoidType: 
            raise TypeMismatchInExpression(ast)

        """ Check its args """
        # Different number of arguments
        if len(funcsym.params) < len(ast.args): 
            raise TypeMismatchInExpression(ast.args[len(funcsym.params)])
        if len(funcsym.params) > len(ast.args): 
            raise TypeMismatchInExpression(ast)

        for i in range(len(funcsym.params)):
            if funcsym.params[i].out and type(ast.args[i]) not in [Id, ArrayCell]:
                raise TypeMismatchInExpression(ast.args[i])
            
        # Infer for param or check param - arg agreements
        for i in range(len(funcsym.params)):
            st, argType = self.visit(ast.args[i], st)
            if type(funcsym.params[i].typ) is AutoType: 
                funcsym.params[i].typ = argType
            elif type(argType) is AutoType:
                Utils.infer(ast.args[i].name, funcsym.params[i].typ, st)
            elif not Utils.isCoercionable(funcsym.params[i].typ, argType): 
                raise TypeMismatchInExpression(ast.args[i])
        return st, funcsym.typ

    def visitAssignStmt(self, ast : AssignStmt, st : SymbolTable):
        st, rtype = self.visit(ast.rhs, st)
        st, ltype = self.visit(ast.lhs, st)

        """Cannot be assigned"""
        if type(ltype) in [VoidType, ArrayType]: raise TypeMismatchInStatement(ast)
        elif type(ltype) is AutoType: Utils.infer(ast.lhs.name, rtype, st)
        elif type(rtype) is AutoType: Utils.infer(ast.rhs.name, ltype, st)
        elif not Utils.isCoercionable(ltype, rtype): 
            raise TypeMismatchInStatement(ast)            
        return st, AssignStmtType()

    def visitIfStmt(self, ast : IfStmt, st : SymbolTable):
        """Check cond"""
        st, condtype = self.visit(ast.cond, st)

        if type(condtype) is AutoType: Utils.infer(ast.cond.name, BooleanType, st)
        if type(condtype) is not BooleanType: raise TypeMismatchInStatement(ast)
        
        newst = Utils.comeInBlock(st)

        newst, _ = self.visit(ast.tstmt, newst)

        if ast.fstmt: newst, _ = self.visit(ast.fstmt, newst)

        return st, IfStmtType()

    def visitForStmt(self, ast : ForStmt, st : SymbolTable):
        """ Visit assign statement to infer if there is any"""
        st, _ = self.visit(ast.init, st)
        st, lhs = self.visit(ast.init.lhs, st)
        st, rhs = self.visit(ast.init.rhs, st)

        if type(rhs) is not IntegerType or type(lhs) is not IntegerType: raise TypeMismatchInStatement(ast)
        """ Make sure cond is BooleanType"""
        st, condType = self.visit(ast.cond, st)
        if type(condType) is AutoType: Utils.infer(ast.cond.name, BooleanType, st)
        if type(condType) is not BooleanType: raise TypeMismatchInStatement(ast)
        
        """Make sure upd is IntegerType"""
        st, updType = self.visit(ast.upd, st)
        if type(updType) is not IntegerType: raise TypeMismatchInStatement(ast)

        """Pass infor before visiting child stmt"""
        st, _ = self.visit(ast.stmt, Utils.comeInLoop(st))
        return Utils.comeOutLoop(st), LoopStmtType()

    def visitWhileStmt(self, ast : WhileStmt, st : SymbolTable):
        st, condType = self.visit(ast.cond, st)
        if type(condType) is AutoType: Utils.infer(ast.cond.name, BooleanType, st)
        if type(condType) is not BooleanType: raise TypeMismatchInStatement(ast)
        
        st, _ = self.visit(ast.stmt, Utils.comeInLoop(st))
        return Utils.comeOutLoop(st), LoopStmtType()

    def visitDoWhileStmt(self, ast, st):
        st, condType = self.visit(ast.cond, st)

        if type(condType) is AutoType: Utils.infer(ast.cond.name, BooleanType, st)
        if type(condType) is not BooleanType: 
            raise TypeMismatchInStatement(ast)
        
        st, _ = self.visit(ast.stmt, Utils.comeInLoop(st))
        return Utils.comeOutLoop(st), LoopStmtType()
    
    def visitBreakStmt(self, ast : BreakStmt, st : SymbolTable):
        if st.properties.inLoop == 0:
            raise MustInLoop(ast)
        return st, MustInLoopStmtType()

    def visitContinueStmt(self, ast : ContinueStmt, st : SymbolTable):
        if st.properties.inLoop == 0:
            raise MustInLoop(ast)
        return st, MustInLoopStmtType()

    def visitReturnStmt(self, ast : ReturnStmt, st : SymbolTable):
        if not st.properties.inFunc: InvalidStatementInFunction(ast)

        if ast.expr is not None:
            st, exprtyp =  self.visit(ast.expr, st)
            """ Return type of the return statement expression"""
            # Compare and update return type
            if type(st.properties.inFunc.typ) is AutoType: 
                st.properties.inFunc.typ = exprtyp
            elif not Utils.isCoercionable(st.properties.inFunc.typ, exprtyp):
                raise TypeMismatchInStatement(ast) 
        else: 
            if type(st.properties.inFunc.typ) is AutoType: st.properties.inFunc.typ = VoidType()
            elif type(st.properties.inFunc.typ) is not VoidType: raise TypeMismatchInStatement(ast)

        return st, ReturnStmt()         

    def visitCallStmt(self, ast : CallStmt, st : SymbolTable):
        # Check if there is callee
        funcsym = st.find_symbol(ast.name)
        if funcsym is None or not isinstance(funcsym, FuncSym):
            raise Undeclared(Function(), ast.name)

        """ Check calling arguments """
        if len(funcsym.params) != len(ast.args):
            raise CallError(f"Numbers of parameters and arguments in {ast.name} do not match.")
        return st
    
    def visitBlockStmt(self, ast : BlockStmt, st : SymbolTable):
        for stmt in ast.body:
            st = self.visit(stmt, st)
            if type(stmt) is ReturnStmt: break
            
        return st

    def visitVarDecl(self, ast: VarDecl, st: SymbolTable):
        if ast.init: 
            # Get datatype of initial expression
            st = self.visit(ast.init, st)

            if isinstance(ast.type, AutoType) and isinstance(st.context.current_datatype, AutoType): 
                raise TypeMismatchInVarDecl(ast) 

            if isinstance(ast.type, AutoType) is AutoType:
                ast.typ = st.context.current_datatype
        
        if st.context.scope != 0:
            st.add_symbol(VarSym(ast.name, ast.typ, st.context.scope, st.context.line_in_scope, ast.init))

        return st
    
    def visitFuncDecl(self, ast: FuncDecl, st: SymbolTable):        
        # Check if scope is global
        if st.context.scope != 0:
            raise ContextError("Function must be declared in global scope")

        # Check if there are two params of the same name
        param_len = len(ast.params)
        for i in range(param_len):
            for j in range(i+1, param_len):
                if ast.params[i].name == ast.params[j].name:
                    raise Redeclared(f"Params {i} and {j} in Function {ast.name}")
        
        # Update the scope of Symbol Table
        st = st.update_scope(ast.name)

        """Traverse its body"""
        st = self.visit(ast.body, st)

    def visitProgram(self, ast : Program, st : SymbolTable):
        for decl in ast.decls:
            st = self.visit(decl, st)


