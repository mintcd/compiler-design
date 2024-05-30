from typing import List
from utils.structures.AST import *

class Symbol:
    def __init__(self,  id : int,
                        name: string, 
                        datatype: Type, 
                        scope: string or 0,
                        declared_line: int):
        '''
        The scope of a symbol is its parent function or 0 if global.
        When there is a FuncCall or CallStmt, a new scope is created.
        '''
        self.name = name
        self.datatype = datatype
        self.scope = scope
        self.declared_stmt = declared_line
        self.called_lines = List[int]

    def __str__(self):
        return "Symbol({}, {})".format(self.name, self.typ, self.scope)

class VarSym(Symbol):
    def __init__(self, name, datatype, scope, declared_line, 
                value = None, assigned_lines = None):
        super().__init__(name, datatype, scope, declared_line)
        self.value = value
        self.assigned_lines = assigned_lines if assigned_lines is not None else []


class FuncSym(Symbol):
    def __init__(self, name, datatype, scope, declared_line, 
                params : List[Type] or None = None):
        
        super().__init__(name, datatype, scope, declared_line, called_lines)
        self.params = params if params is not None else []


class Context:
    def __init__(self, scope = 0, line_in_scope = 0, in_loop = False, current_datatype = None):
        self.scope = scope
        self.line_in_scope = line_in_scope
        self.in_loop = in_loop
        self.current_datatype = None

class SymbolTable:
    def __init__(self, symbols: List[Symbol] or None = None, 
                        context: Context or None = None):

        self.symbols = symbols if symbols is not None else []
        
        # Adding predefined symbols
        self.symbols += [
            FuncSym("readInteger", VoidType(), 0, 0, [IntegerType()]),
            FuncSym("printInteger", VoidType(), 0, 0),
            FuncSym("readFloat", VoidType(), 0, 0, [FloatType()]),
            FuncSym("writeFloat", VoidType(), 0, 0),
            FuncSym("readBoolean", VoidType(), 0, 0, [BooleanType()]),
            FuncSym("printBoolean", VoidType(), 0, 0),
            FuncSym("readString", VoidType(), 0, 0, [StringType()]),
            FuncSym("printString", VoidType())
        ]
        
        self.context = context if context is not None else Context()
    
    def update_current_datatype(typ : Type):
        self.context.current_datatype = type
        return self

    def update_scope(self, scope):
        self.context.scope = scope
        self.context.line_in_scope = 0

        return self
    
    def add_symbol(self, symbol: Symbol):
        '''
        Add a new Symbol to the current Symbol Table and return a new Symbol Table instance
        '''
        self.symbols.append(symbol)
        self.context.line_in_scope += 1

        return self
    
    def find_symbol(self, name: str):
        for symbol in self.symbols:
            if symbol.name == name:
                return symbol
        return None
    
    def type_inference(self, name, typ):
        symbol = self.find_symbol(name)
        symbol.datatype = typ

        return self
