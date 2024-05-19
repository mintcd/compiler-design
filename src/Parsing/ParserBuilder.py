import ply.yacc as yacc

# Get the token map from the lexer, required by ply.yacc
from LexicalAnalysis.LexerBuilder import tokens


def p_expr(p):
    '''expr : expr ADD expr
            | INTLIT
            | ID'''
    if len(p) == 4:
        p[0] = ('BINOP', p[1], p[2], p[3])
    else:
        p[0] = p[1]


# Error rule for syntax errors
def p_error(p):
    print(f"Syntax error in input {p}")


parser = yacc.yacc()
