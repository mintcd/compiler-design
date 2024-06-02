import ply.lex as lex
from lexing.rules import keywords, simple_tokens, action_tokens


class Lexer:
    # List of tokens required by ply.lex
    tokens = list([keyword.upper() for keyword in keywords]) + \
        list(simple_tokens.keys()) + list(action_tokens)

    # A string containing ignored characters (spaces and tabs)
    t_ignore = ' \t'

    # Dynamically define rules for simple tokens
    for token_name, token_regex in simple_tokens.items():
        exec(f't_{token_name} = {token_regex!r}')

    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def t_FLOATLIT(self, t):
        r'0|[1-9](_?[0-9]+)*\.\d+([eE][-+]?\d+)?|\.\d+([eE][-+]?\d+)?|\d+[eE][-+]?\d+'
        t.value = float(t.value.replace("_", ""))
        return t

    def t_INTLIT(self, t):
        r'0|[1-9](_?[0-9]+)*'
        t.value = int(t.value.replace("_", ""))
        return t

    def t_STRINGLIT(self, t):
        r'"[\w\s]*"'
        # Remove the surrounding double quotes and unescape escaped double quotes
        t.value = t.value[1:-1].replace('\\"', '"')
        return t

    def t_BOOLEANLIT(self, t):
        r'true|false'
        t.value = True if t.value == 'true' else False
        return t

    def t_ID(self, t):
        r'[_a-zA-Z][_a-zA-Z0-9]*'
        t.type = t.value.upper() if t.value in keywords else "ID"
        return t

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
    
    def t_COMMENT(self, t):
        r'//.*|/\*([^*]|\*+[^*/])*\*+/'
        pass

    # Error handling rule
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def input(self, data):
        self.lexer.input(data)

    def token(self):
        return self.lexer.token()
