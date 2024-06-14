import ply.yacc as yacc

from phases.lexing.Lexer import Lexer
from utils.structures.AST import *


class Parser:
    tokens = Lexer().tokens
    precedence = (
        ('left', 'CONCATE'),
        ('left', 'LT', 'GT', 'LE', 'GE', 'EQUAL', 'NOT_EQUAL'),
        ('left', 'OR', 'AND'),
        ('left', 'ADD', 'SUB'),
        ('left', 'MUL', 'DIV', 'MOD'),
        ('right', 'NOT'),
        ('right', 'SUB')
    )

    def __init__(self, **kwargs):
        self.parser = yacc.yacc(module=self, **kwargs)

    def p_program(self, p):
        '''
        program : declprime
        '''
        p[0] = Program(p[1])

    def p_declprime(self, p):
        '''
        declprime : decl declprime
                | decl
        '''
        if len(p) == 3:
            if isinstance(p[1], list):
                p[0] = p[1] + p[2]
            else:
                p[0] = [p[1]] + p[2]
        else:
            if isinstance(p[1], list):
                p[0] = p[1]
            else:
                p[0] = [p[1]]

############## DECLARATIONS #####################
    def p_decl(self, p):
        '''
        decl : vardecl
            | funcdecl
        '''
        p[0] = p[1]

    def p_vardecl(self, p):
        '''
        vardecl : idprime CL returnabletype SM
                | idprime CL returnabletype ASSIGN exprprime SM
        '''
        if len(p) == 5:
            p[0] = [VarDecl(idname, p[3]) for idname in p[1]]
        else:
            if len(p[1]) != len(p[5]):
                raise Exception("Names and Expressions of different lengths")
            declLen = len(p[1])
            # Take the name and init in the reverse order
            p[0] = [VarDecl(p[1][i], p[3], p[5][i]) 
                        for i in range(declLen)]

    def p_funcdecl(self, p):
        '''
            funcdecl : ID CL FUNCTION typ LP paramlist RP INHERIT ID blockstmt
                    | ID CL FUNCTION typ LP paramlist RP blockstmt
        '''
        if len(p) == 10:
            p[0] = FuncDecl(name=p[1], rtype=p[4], params=p[6],
                            inherit=p[8], body=p[10])
        else:
            p[0] = FuncDecl(name=p[1], rtype=p[4], params=p[6],
                            inherit=None, body=p[8])

    def p_paramdecl(self, p):
        ''' paramdecl : INHERIT OUT ID CL returnabletype
                        | OUT ID CL returnabletype
                        | INHERIT ID CL returnabletype
                        | ID CL returnabletype
        '''
        if len(p) == 6:
            p[0] = ParamDecl(p[3], p[5], True, True)
        elif p.slice(1).type == 'OUT':
            p[0] = ParamDecl(p[3], p[5], True, False)
        elif p.slice(1).type == 'INHERIT':
            p[0] = ParamDecl(p[3], p[5], False, True)
        else:
            p[0] = ParamDecl(p[3], p[5], False, False)

################## EXPRESSIONS ###########################
    def p_expr(self, p):
        ''' expr : expr CONCATE expr
                | expr LT expr
                | expr GT expr
                | expr LE expr
                | expr GE expr
                | expr EQUAL expr
                | expr NOT_EQUAL expr
                | expr OR expr
                | expr AND expr
                | expr ADD expr
                | expr SUB expr
                | expr MUL expr
                | expr DIV expr
                | expr MOD expr

                | NOT expr
                | SUB expr

                | arraylit
                | arraycell
                | LP expr RP
                | funccall

                | INTLIT
                | FLOATLIT
                | BOOLEANLIT
                | STRINGLIT
                | ID
        '''

        if len(p) == 4:
            if p.slice[1].type == 'LP': 
                p[0] = p[2]
            else:
                p[0] = BinExpr(p[2], p[1], p[3])
        elif len(p) == 3:
            p[0] = UnExpr(p[1], p[2])
        else:
            if p.slice[1].type == 'INTLIT':
                p[0] = IntegerLit(p[1])
            elif p.slice[1].type == 'FLOATLIT':
                p[0] = FloatLit(p[1])
            elif p.slice[1].type == 'STRINGLIT':
                p[0] = StringLit(p[1])
            elif p.slice[1].type == 'BOOLEANLIT':
                p[0] = BooleanLit(p[1])
            elif p.slice[1].type == 'ID':
                p[0] = Id(p[1])
            else:
                p[0] = p[1]

    def p_arraylit(self, p):
        '''arraylit : LB exprlist RB'''
        p[0] = ArrayLit(p[2])
    
    def p_arraycell(self, p):
        '''arraycell : ID LSB exprprime RSB'''
        p[0] = ArrayCell(p[1], p[3])

    def p_funccall(self, p):
       ''' funccall : ID LP exprlist RP'''
       p[0] = FuncCall(p[1], p[3])

################## STATEMENTS ############################

    def p_stmt(self, p):
        '''
            stmt : assignstmt
                | ifstmt
                | forstmt
                | whilestmt
                | dowhilestmt
                | breakstmt
                | continuestmt
                | returnstmt
                | callstmt
                | blockstmt
        '''
        p[0] = p[1]
    
    def p_assignstmt(self, p):
        '''
            assignstmt : lhs ASSIGN expr SM
        '''
        p[0] = AssignStmt(p[1], p[3])

    def p_ifstmt(self, p):
        ''' 
            ifstmt : IF LP expr RP stmt 
                    | IF LP expr RP stmt elsestmt
        '''
        if not isinstance(p[5], StmtBlock):
            p[5] = StmtBlock([p[5]])
        if len(p) == 6:
            p[0] = IfStmt(p[3], p[5])
        else : 
            p[0] = IfStmt(p[3], p[5], p[6])
    
    def p_elsestmt(self, p):
        '''elsestmt : ELSE stmt '''
        if not isinstance(p[2], StmtBlock):
            p[2] = StmtBlock([p[2]])

        p[0] = p[2]
    
    def p_forstmt(self, p):
        '''forstmt : FOR LP lhs ASSIGN expr CM expr CM expr RP stmt'''
        if not isinstance(p[11], StmtBlock):
            p[11] = StmtBlock([p[11]])

        p[0] = ForStmt(
            AssignStmt(p[3], p[5]),
            p[7],
            p[9],
            p[11]
        )

    def p_whilestmt(self, p):
        '''whilestmt : WHILE LP expr RP stmt'''
        if not isinstance(p[5], StmtBlock):
            p[5] = StmtBlock([p[5]])

        p[0] = WhileStmt(p[3], p[5])
    
    def p_dowhilestmt(self, p):            
        '''dowhilestmt : DO blockstmt WHILE LP expr RP SM'''
        if not isinstance(p[2], StmtBlock):
            p[2] = StmtBlock([p[2]])

        p[0] = DoWhileStmt(p[5], p[2])

    def p_blockstmt(self, p):
        '''blockstmt : LB stmtlist RB'''
        p[0] = StmtBlock(p[2])
    
    def p_callstmt(self, p):
        '''callstmt : ID LP exprlist RP SM'''
        p[0] = CallStmt(p[1], p[3])
    
    def p_breakstmt(self, p):
        '''breakstmt : BREAK SM'''
        p[0] = BreakStmt()

    def p_continuestmt(self, p):
        '''continuestmt : CONTINUE SM'''
        p[0] = ContinueStmt()
    
    def p_returnstmt(self, p):
        '''returnstmt : RETURN expr SM 
                    | RETURN SM '''
        if len(p) == 4:
            p[0] = ReturnStmt(p[2])
        else: p[0] = ReturnStmt()

################## DATA TYPES #########################

    def p_typ(self, p):
        '''typ : returnabletype
                | VOID
        '''
        if p.slice[1].type == 'VOID':
            p[1] = VoidType()
        p[0] = p[1]

    def p_returnabletype(self, p):
        '''returnabletype : array 
                        | atomictype 
                        | AUTO
        '''
        p[0] = p[1]

    def p_array(self, p):
        '''array : ARRAY LSB intprime RSB OF atomictype'''
        p[0] = ArrayType(p[3], p[6])

    def p_atomictype(self, p):
        '''atomictype : BOOLEAN 
                    | INTEGER 
                    | FLOAT 
                    | STRING
        '''
        if p.slice[1].type == 'BOOLEAN':
            p[0] = BooleanType()
        elif p.slice[1].type == 'INTEGER':
            p[0] = IntegerType()
        elif p.slice[1].type == 'FLOAT':
            p[0] = FloatType()
        else:
            p[0] = StringType()

################## LISTS ###############################
    def p_exprlist(self, p):
        '''
        exprlist : exprprime
                |
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = []

    def p_exprprime(self, p):
        '''
        exprprime : expr CM exprprime
                | expr
        '''
        if len(p) == 4:
            p[0] = [p[1]] + p[3]
        else:
            p[0] = [p[1]]

    def p_paramlist(self, p):
        '''
        paramlist : paramprime 
                    |
        '''
        if len(p) == 2:
            p[0] = p[1]
        else: p[0] = []
    
    def p_paramprime(self, p):
        ''' paramprime : paramdecl CM paramprime 
                    | paramdecl '''
        if len(p) == 4:
            p[0] =[p[1]] + p[3]
        else: p[0] = [p[1]]

    def p_stmtlist(self, p):
        '''
        stmtlist : stmt stmtlist 
                | vardecl stmtlist
                |
        '''
        if len(p) == 3:
            if isinstance(p[1], Stmt):
                p[0] = [p[1]] + p[2]
            else: p[0] = p[1] + p[2]
        else:
            p[0] = []

################## UTILS #############################
    def p_intprime(self, p):
        '''
            intprime : INTLIT CM intprime 
                    | INTLIT
        '''
        if len(p) == 4:
            p[0] = [p[1]] + p[3]
        else:
            p[0] = [p[1]]

    def p_idprime(self, p):
        ''' idprime : ID CM idprime 
                    | ID
        '''
        if len(p) == 4:
            p[0] = [p[1]] + p[3]
        else:
            p[0] = [p[1]]

    def p_lhs(self, p):
        '''
            lhs : ID 
                | arraycell
        '''
        if isinstance(p[1], ArrayCell):
            p[0] = p[1]
        else:
            p[0] = Id(p[1])
            
###############################################
    def p_error(self, p):
        print(f"Syntax error in input {p}")

    def parse(self, data):
        return self.parser.parse(data)
