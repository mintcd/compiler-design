from utils.visitor_pattern import Visitee
from typing import List, Tuple

class AST(Visitee): 
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

# Statement container
class StmtBlock(AST):
    def __init__(self, stmts):
        self.stmts = stmts

    def __repr__(self):
        return "StmtBlock([\n{}\n])".format(",\n".join([str(stmt) for stmt in self.stmts]))
    
    def get_index_of_stmt(self, stmt):
        for i in range(len(self.stmts)):
            if stmt.id == self.stmts[i].id:
                return i
        return None
    
    def insert_stmt(self, index, stmt):
        self.stmts.insert(index, stmt)

        return self

class Stmt(AST): 
    def __init__(self, _id: Tuple[int] or None = None, block: StmtBlock or None = None):
        self.id = _id if _id is not None else None
        self.block = block if block is not None else None
class Expr(AST):
    def __init__(self, block = None):
        self.block = block
class Type(AST): pass
class Decl(AST): pass

class Program(AST):
    def __init__(self, decls):
        self.decls = decls

    def __repr__(self):
        return "Program([\n\t{}\n])".format("\n\t".join([str(decl) for decl in self.decls]))

class Atomic(Expr):
    def __init__(self, block = None):
        super().__init__(block)

########################### Expressions ##########################################

class LHS(Expr):
    def __init__(self):
        super().__init__()
        self.id = None  

class BinExpr(Expr):
    def __init__(self, op: str, left: Expr, right: Expr):
        super().__init__()
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return "BinExpr({}, {}, {})".format(self.op, str(self.left), str(self.right))    

    def calculate(self):
        calculated_val = None

        if self.op == "+":
            calculated_val = self.left.val + self.right.val
        if self.op == "-":
            calculated_val = self.left.val - self.right.val
        if self.op == "*":
            calculated_val = self.left.val * self.right
        if self.op == "/":
            calculated_val = self.left.val / self.right.val
        if self.op == "%":
            calculated_val = self.left.val % self.right.val
        if self.op == "&&":
            calculated_val = self.left.val and self.right.val
        if self.op == "||":
            calculated_val = self.left.val or self.right.val
        if self.op == "==":
            calculated_val = self.left.val == self.right.val
        if self.op == "!=":
            calculated_val = self.left.val != self.right.val
        if self.op == "<":
            calculated_val = self.left.val < self.right.val
        if self.op == ">":
            calculated_val = self.left.val > self.right.val
        if self.op == "<=":
            calculated_val = self.left.val > self.right.val
        if self.op == ">=":
            calculated_val = self.left.val > self.right.val
        if self.op == "::":
            calculated_val = self.left.val + self.right.val

        inferred_type = self._infer_type(self.left, self.right)
        inferred_type.val = calculated_val

        return inferred_type

    def _infer_type(self, typ1, typ2):
        if typ1 is None:
            return typ2
        if typ2 is None:
            return typ1

        if isinstance(typ1, Float) or isinstance(typ2, Float):
            return Float()
        return typ1

class UnExpr(Expr):
    def __init__(self, op: str, val: Expr):
        super().__init__()
        self.op = op
        self.val = val

    def __repr__(self):
        return "UnExpr({}, {})".format(self.op, str(self.val))

    def calculate(self):
        calculated_val = None
        if self.op == "-":
            calculated_val = - self.val.val
        if self.op == "!":
            calculated_val = not self.val.val
        
        self.val.val = calculated_val

        return self.val
        
class ArrayCell(LHS):
    def __init__(self, name: str, cell: List[Expr]):
        super().__init__()
        self.name = name
        self.cell = cell
    def __repr__(self):
        return f"ArrayCell({self.name}{(', ' + str(self.id)) if self.id is not None else ''}, [{', '.join(str(expr) for expr in self.cell)}]"

class FuncCall(Expr):
    def __init__(self, name: str, args: List[Expr]):
        super().__init__()
        self.name = name
        self.args = args

class Array(Expr):
    def __init__(self, val: List[Expr] or None = None, dim = None, typ = None):
        self.val = val
        self.dim = dim
        self.typ = typ

    def __repr__(self):
        return f"Array([{', '.join(str(expr) for expr in self.val)}], {self.typ})" if self.val is not None else f"Array({self.dim}, {self.typ})"

    def get_value(self):
        result = []
        for expr in self.val:
            if isinstance(expr, Array):
                result.append(expr.get_value())
            else:
                result.append(expr)
        return result

class Id(LHS):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
    def __str__(self):
        return f"Id({self.name}{(', ' + str(self.id)) if self.id is not None else ''})"

class Integer(Atomic):
    def __init__(self, val: int or None = None):
        self.val = val
    def __str__(self):
        return f"Int({str(self.val)})" if self.val is not None else "int"

class Float(Atomic):
    def __init__(self, val: float or None = None):
        self.val = val
    def __repr__(self):
        return f"Float({str(self.val)})" if self.val is not None else "float"

class String(Atomic):
    def __init__(self, val: str or None = None):
        self.val = val

class Boolean(Atomic):
    def __init__(self, val: bool or None = None):
        self.val = val

class Void():
  def __str__(self):
    return "Void"


############################### Statements ##################################

class AssignStmt(Stmt):
    def __init__(self, lhs: ArrayCell or Id, rhs: Expr, typ: Type or None = None):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs
        self.typ = typ
    def __repr__(self):
        return f"{self.id} {str(self.lhs)} := {str(self.rhs)}"

class IfStmt(Stmt):
    def __init__(self, cond: Expr, tstmt: StmtBlock, fstmt: StmtBlock or None = None):
        super().__init__()
        self.cond = cond
        self.tstmt = tstmt
        self.fstmt = fstmt

    def __repr__(self):
        return f"{self.id}: If({str(self.cond)}, {str(self.tstmt)}{str(self.fstmt) if self.fstmt else ''})"

class ForStmt(Stmt):
    def __init__(self, init: AssignStmt, cond: Expr, upd: Expr, stmt: StmtBlock):
        super().__init__()
        self.init = init
        self.cond = cond
        self.upd = upd
        self.stmt = stmt

    def __repr__(self):
        return f"{self.id}: ForStmt({str(self.init)}, {str(self.cond)}, {str(self.upd)}, {str(self.stmt)})"

class WhileStmt(Stmt):
    def __init__(self, cond: Expr, stmt: StmtBlock):
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
        return f"{self.id} {self.name}: {self.typ}{(' := ' + str(self.init)) if self.init is not None else ''}"

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


################### Types ##########################
# class AtomicType(Type): 
#     def __repr__(self):
#         return self.__class__.__name__

# class IntegerType(AtomicType): 
#     def __repr__(self):
#         return self.__class__.__name__

# class Float(AtomicType): 
#     def __repr__(self):
#         return self.__class__.__name__

# class Boolean(AtomicType): 
#     def __repr__(self):
#         return self.__class__.__name__

# class String(AtomicType): 
#     def __repr__(self):
#         return self.__class__.__name__

# class ArrayType(Type):
#     def __init__(self, dimensions: List[int], typ: AtomicType):
#         self.dimensions = dimensions
#         self.typ = typ

#     def __repr__(self):
#         return "ArrayType([{}], {})".format(", ".join([str(dimen) for dimen in self.dimensions]), str(self.typ))

# class Auto(Type):
#     def __repr__(self):
#         return self.__class__.__name__

# class Void(Type):
#     def __repr__(self):
#         return self.__class__.__name__
