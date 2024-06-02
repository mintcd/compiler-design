from utils.visitor_pattern import Visitee
from typing import List, Tuple

class AST(Visitee): pass

# Statment container
class StmtBlock(AST):
    def __init__(self, stmts):
        self.stmts = stmts

    def __repr__(self):
        return "StmtBlock([{}])".format(",\n".join([str(stmt) for stmt in self.stmts]))
    
    def get_index_of_stmt(self, stmt):
        for i in range(len(self.stmts)):
            if stmt.id == self.stmts[i].id:
                return i
        return None
    
    def insert_stmt(self, index, stmt):
        self.stmts.insert(index, stmt)

        return self

class Stmt(AST): 
    def __init__(self, _id = None, block: StmtBlock or None = None):
        self.id = _id if _id is not None else None
        self.block = block if block is not None else None
class Expr(AST): 
    def __int__(self,  _id = None):
        self.id = _id
class Type(AST): pass
class Decl(AST): pass

class Program(AST):
    def __init__(self, decls):
        self.decls = decls

    def __repr__(self):
        return "Program([\n\t{}\n])".format("\n\t".join([str(decl) for decl in self.decls]))

class AtomicLiteral(Expr): pass

################### Types ##########################
class AtomicType(Type): 
    def __repr__(self):
        return self.__class__.__name__

class IntegerType(AtomicType): 
    def __repr__(self):
        return self.__class__.__name__

class FloatType(AtomicType): 
    def __repr__(self):
        return self.__class__.__name__

class BooleanType(AtomicType): 
    def __repr__(self):
        return self.__class__.__name__

class StringType(AtomicType): 
    def __repr__(self):
        return self.__class__.__name__

class ArrayType(Type):
    def __init__(self, dimensions: List[int], typ: AtomicType):
        self.dimensions = dimensions
        self.typ = typ

    def __repr__(self):
        return "ArrayType([{}], {})".format(", ".join([str(dimen) for dimen in self.dimensions]), str(self.typ))

class AutoType(Type):
    def __repr__(self):
        return self.__class__.__name__

class VoidType(Type):
    def __repr__(self):
        return self.__class__.__name__


########################### Expressions #############################

class BinExpr(Expr):
    def __init__(self, op: str, left: Expr, right: Expr):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return "BinExpr({}, {}, {})".format(self.op, str(self.left), str(self.right))    

    def calculate(self):
        if self.op == "+":
            return self.left.val + self.right.val
        if self.op == "-":
            return self.left.val - self.right.val
        if self.op == "*":
            return self.left.val * self.right
        if self.op == "/":
            return self.left.val / self.right.val
        if self.op == "%":
            return self.left.val % self.right.val
        if self.op == "&&":
            return self.left.val and self.right.val
        if self.op == "||":
            return self.left.val or self.right.val
        if self.op == "==":
            return self.left.val == self.right.val
        if self.op == "!=":
            return self.left.val != self.right.val
        if self.op == "<":
            return self.left.val < self.right.val
        if self.op == ">":
            return self.left.val > self.right.val
        if self.op == "<=":
            return self.left.val > self.right.val
        if self.op == ">=":
            return self.left.val > self.right.val
        if self.op == "::":
            return self.left.val + self.right.val

class UnExpr(Expr):
    def __init__(self, op: str, val: Expr):
        self.op = op
        self.val = val

    def __repr__(self):
        return "UnExpr({}, {})".format(self.op, str(self.val))

    def calculate(self):
        if self.op == "-":
            return - self.val.val
        if self.op == "!":
            return not self.val.val

class Id(Expr):
    def __init__(self, name: str):
        self.name = name
    def __repr__(self):
        return f"Id({self.name})"

class ArrayCell(Expr):
    def __init__(self, name: str, cell: List[Expr]):
        self.name = name
        self.cell = cell
    def __repr__(self):
        return "ArrayCell({}, [{}])".format(self.name, ", ".join([str(expr) for expr in self.cell]))

class IntegerLit(AtomicLiteral):
    def __init__(self, val: int):
        self.val = val
    def __repr__(self):
        return str(self.val)

class FloatLit(AtomicLiteral):
    def __init__(self, val: float):
        self.val = val
    def __repr__(self):
        return str(self.val)

class StringLit(AtomicLiteral):
    def __init__(self, val: str):
        self.val = val

class BooleanLit(AtomicLiteral):
    def __init__(self, val: bool):
        self.val = val

class ArrayLit(Expr):
    def __init__(self, explist: List[Expr]):
        self.explist = explist
    def __repr__(self):
        return f"[{', '.join(str(expr) for expr in self.explist)}]"

class FuncCall(Expr):
    def __init__(self, name: str, args: List[Expr]):
        self.name = name
        self.args = args

############################### Statements ##################################

class AssignStmt(Stmt):
    def __init__(self, lhs: ArrayCell or Id, rhs: Expr, typ: Type or None = None):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs
        self.typ = typ
    def __repr__(self):
        return f"{self.id}: Assign({str(self.lhs)}, {str(self.rhs)})"

class IfStmt(Stmt):
    def __init__(self, cond: Expr, tstmt: Stmt, fstmt: Stmt or None = None):
        super().__init__()
        self.cond = cond
        self.tstmt = tstmt
        self.fstmt = fstmt

    def __repr__(self):
        return f"{self.id}: If({str(self.cond)}, {str(self.tstmt)}{str(self.fstmt) if self.fstmt else ''})"

class ForStmt(Stmt):
    def __init__(self, init: AssignStmt, cond: Expr, upd: Expr, stmt: Stmt):
        super().__init__()
        self.init = init
        self.cond = cond
        self.upd = upd
        self.stmt = stmt

    def __repr__(self):
        return f"{self.id}: ForStmt({str(self.init)}, {str(self.cond)}, {str(self.upd)}, {str(self.stmt)})"

class WhileStmt(Stmt):
    def __init__(self, cond: Expr, stmt: Stmt):
        super().__init__()
        self.cond = cond
        self.stmt = stmt

    def __repr__(self):
        return f"{self.id}: While({str(self.cond)}, {str(self.stmt)})"

class DoWhileStmt(Stmt):
    def __init__(self, cond: Expr, stmt: StmtBlock):
        super().__init__()
        self.cond = cond
        self.stmt = stmt

    def __repr__(self):
        return f"{self.id}: DoWhileStmt({str(self.cond)}, {str(self.stmt)})"

class BreakStmt(Stmt):
    def __init__(self):
        super().__init__()
    def __repr__(self):
        return f"{self.id}: BreakStmt()"

class ContinueStmt(Stmt):
    def __init__(self):
        super().__init__()

    def __repr__(self):
        return f"{self.id}: ContinueStmt()"

class ReturnStmt(Stmt):
    def __init__(self, expr: Expr or None = None):
        super().__init__()
        self.expr = expr

    def __repr__(self):
        return f"{self.id}: ReturnStmt({str(self.expr) if self.expr else ''})"

class CallStmt(Stmt):
    def __init__(self, name: str, args: List[Expr]):
        super().__init__()
        self.name = name
        self.args = args

    def __repr__(self):
        return f"{self.id}: CallStmt({self.name}, {', '.join([str(expr) for expr in self.args])})"

########################### Declarations ################################

class VarDecl(Stmt):
    def __init__(self, name: str, typ: Type, init: Expr or None = None):
        super().__init__()
        self.name = name
        self.typ = typ
        self.init = init
    def __repr__(self):
        return f"{self.id}: VarDecl({self.name}, {self.typ}{(', ' + str(self.init)) if self.init is not None else ''})"

class ParamDecl(Decl):
    def __init__(self, name: str, typ: Type, out: bool = False, inherit: bool = False):
        self.name = name
        self.typ = typ
        self.out = out
        self.inherit = inherit

    def __repr__(self):
        return "{}{}Param({}, {})".format("Inherit" if self.inherit else "", "Out" if self.out else "", self.name, str(self.typ))

class FuncDecl(Decl):
    def __init__(self, name: str, rtype: Type, params: List[ParamDecl], inherit: str or None, body: StmtBlock):
        self.name = name
        self.rtype = rtype
        self.params = params
        self.inherit = inherit
        self.body = body

    def __repr__(self):
        return "FuncDecl({}, {}, [{}], {}, {})".format(self.name, str(self.rtype), ", ".join([str(param) for param in self.params]), self.inherit if self.inherit else "None", str(self.body))