import ply.lex as lex


from LexicalAnalysis.rules import keywords, simple_tokens, action_tokens

# List of tokens required by ply.lex
tokens = list([keyword.upper() for keyword in keywords]) + \
    list(simple_tokens.keys()) + list(action_tokens)

# Dynamically define rules for simple tokens
for token_name, token_regex in simple_tokens.items():
    globals()[f't_{token_name}'] = token_regex


# Rules for action tokens

def t_FLOATLIT(t):
    r'0|[1-9](_?[0-9]+)*\.\d+([eE][-+]?\d+)?|\.\d+([eE][-+]?\d+)?|\d+[eE][-+]?\d+'
    t.value = float(t.value.replace("_", ""))
    return t


def t_INTLIT(t):
    r'0|[1-9](_?[0-9]+)*'
    t.value = int(t.value.replace("_", ""))
    return t


def t_STRINGLIT(t):
    r'"[\w\s]*"'
    # Remove the surrounding double quotes and unescape escaped double quotes
    t.value = t.value[1:-1].replace('\\"', '"')
    return t


def t_BOOLEANLIT(t):
    r'true|false'
    return t


def t_ID(t):
    r'[_a-zA-Z][_a-zA-Z0-9]*'
    t.type = t.value.upper() if t.value in keywords else "ID"
    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()
