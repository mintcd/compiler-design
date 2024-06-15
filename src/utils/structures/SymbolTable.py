from typing import List
from utils.structures.AST import *

class Symbol:
    def __init__(self,  id: int,                   # unique ID for each symbol
                        name: str,                  # symbol name
                        datatype: Type,             # type of variable symbol, or return type of function symbol
                        scope: tuple = (0),
                        value=None,                 # current value, exclusive to variable and parameter
                        params: List[Type] or None = None  # List of parameter types, exclusive to function symbol
                ):

        self.id = id
        self.name = name
        self.scope = scope
        self.datatype = datatype
        self.value = value
        self.params = params

    def __str__(self):
        return "Symbol({}, {}, {}, {})".format(self.id, self.name, self.datatype, self.scope)

    def __repr__(self):
        return "Symbol({}, {}, {})".format(self.name, self.datatype, self.scope)

class FuncSym(Symbol):
    def __init__(self, id, name, rtype, params: List[Type] or None = None):
        super().__init__(id, name, rtype, (0, 0))
        self.params = params if params is not None else []

class VarSym(Symbol):
    def __init__(self, id, name, typ, scope, value):
        super().__init__(id, name, typ, scope)
        self.value = value

class SymbolTable:
    def __init__(self, symbols: List[Symbol] or None = None):
        self.symbols = symbols if symbols is not None else []
        self.avail_id = 0
        
        # Adding predefined symbols
        # self.symbols += [
        #     FuncSym(self.get_avail_id(), "readInteger", VoidType(), params=[IntegerType()]),
        #     FuncSym(self.get_avail_id(), "printInteger", VoidType()),
        #     FuncSym(self.get_avail_id(), "readFloat", VoidType(), params=[Float()]),
        #     FuncSym(self.get_avail_id(), "writeFloat", VoidType()),
        #     FuncSym(self.get_avail_id(), "readBoolean", VoidType(), params=[Boolean()]),
        #     FuncSym(self.get_avail_id(), "printBoolean", VoidType()),
        #     FuncSym(self.get_avail_id(), "readString", VoidType(), params=[String()]),
        #     FuncSym(self.get_avail_id(), "printString", VoidType())
        # ]
    
    def __str__(self):
        return ",\n".join(str(symbol) for symbol in self.symbols)

    # def has_scope(self, scope: tuple):
    #     for symbol in self.symbols:
    #         if symbol.scope == scope:
    #             return True
    #     return False

    # def get_varsym(self):
    #   return [sym for sym in self.symbols if isinstance(sym, VarSym)]
        
    def add_symbol(self, decl: VarDecl or FuncDecl or ParamDecl):
        if isinstance(decl, VarDecl):
                symbol = Symbol(self.avail_id, decl.name, decl.typ, decl.id[:len(decl.id)-1], decl.init)
        else:
                symbol = Symbol(self.avail_id, decl.name, decl.rtype, (0), params=decl.params)

        self.symbols.append(symbol)

        self.avail_id += 1

        return self

    def get_symbol(self, name: str, _id: tuple or None = None):
        exact_match = None
        name_match = None
        
        for symbol in self.symbols:
            if symbol.name == name:
                if _id is not None and symbol.id == _id:
                    return symbol
                name_match = symbol
        
        return name_match

    # def type_inference(self, name, typ):
    #     symbol = self.get_symbol(name)
    #     symbol.datatype = typ

    #     return self
