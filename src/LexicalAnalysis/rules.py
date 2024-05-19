# Lexer rules

# Keyword example: if --> (IF, 'if')


keywords = {'array', 'auto', 'boolean', 'break', 'continue', 'do', 'else', 'float', 'for',
            'function', 'if', 'inherit', 'integer', 'of', 'out', 'return', 'string', 'void', 'while'}

# Tokens not needing an action
simple_tokens = {
    # Operators
    'ADD': r'\+', 'SUB': r'-', 'MUL': r'\*', 'DIV': r'/', 'MOD': r'%',
    'NOT': r'!', 'AND': r'&&', 'OR': r'\|\|',
    'EQUAL': r'==', 'NOT_EQUAL': r'!=', 'LT': r'<', 'GT': r'>', 'LE': r'<=', 'GE': r'>=',
    'CONCATE': r'::',

    # Separators
    'ASSIGN': r'=',
    'LSB': r'\[', 'RSB': r'\]',
    'LP': r'\(', 'RP': r'\)',
    'LB': r'\{', 'RB': r'\}',
    'SM': r';',
    'CL': r':',
    'DOT': r'\.',
    'CM': r',',
}

# Tokens needing an action
action_tokens = {
    'INTLIT', 'FLOATLIT', 'BOOLEANLIT', 'STRINGLIT',
    'ID',
}
