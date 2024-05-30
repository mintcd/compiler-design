grammar MT22;

options {
	language = Python3;
}

program: declprime EOF;

declprime: decl declprime | decl;
decl: vardecl | funcdecl;

/***********DECLARATIONS***************/
vardecl: idprime CL returnabletype SM | multidecl SM;
multidecl: ID CM multidecl CM expr | ID CL returnabletype ASSIGN expr;
funcdecl: ID CL FUNCTION typ LP paramlist RP (INHERIT ID)? blockstmt;

/*********** LISTS  **************/
idprime: ID CM idprime | ID;

exprlist: exprprime |;
exprprime: expr CM exprprime | expr;

paramlist: paramprime |;
paramprime: paramdecl CM paramprime | paramdecl;
paramdecl: INHERIT? OUT? ID CL returnabletype;

/*********** STATEMENTS  **************/
stmt: 

assignstmt 
| ifstmt 
| forstmt 
| whilestmt 
| dowhilestmt 

| breakstmt 
| continuestmt
| returnstmt 
| callstmt 
| blockstmt;

assignstmt: lhs ASSIGN expr SM;
lhs: ID | arraycell;

ifstmt: IF LP expr RP stmt | IF LP expr RP stmt elsestmt;
elsestmt: ELSE stmt;
forstmt: FOR LP lhs ASSIGN expr CM expr CM expr RP stmt;
whilestmt: WHILE LP expr RP stmt;
dowhilestmt: DO blockstmt WHILE LP expr RP SM;

breakstmt: BREAK SM;
continuestmt: CONTINUE SM;
returnstmt: RETURN expr SM | RETURN SM;

callstmt: ID LP exprlist RP SM;
blockstmt: LB stmtlist RB;
stmtlist: (stmt | vardecl) stmtlist |;

/*********** EXPRESSIONS  ****************************/
expr: expr1 CONCATE expr1 | expr1;
expr1: expr2 (LT | GT | LE | GE | EQUAL | NOT_EQUAL) expr2 | expr2;
expr2: expr2 (OR | AND) expr3 | expr3;
expr3: expr3 (ADD | SUB) expr4 | expr4;
expr4: expr4 (MUL | DIV | MOD) expr5 | expr5;
expr5: NOT expr5 | expr6;
expr6: SUB expr6 | expr7;
expr7: arraylit | INTLIT | FLOATLIT | BOOLEANLIT | STRINGLIT | funccall | arraycell | ID | LP expr RP;

arraycell: ID LSB exprprime RSB;
funccall: ID LP exprlist RP;

/************** DATATYPES *******************/
typ: returnabletype | VOID;
returnabletype: array | atomictype | AUTO;
array: ARRAY LSB intprime RSB OF atomictype;
atomictype: BOOLEAN | INTEGER | FLOAT | STRING;

intprime: INTLIT CM intprime | INTLIT;
/*************** KEYWORDS *************/
ARRAY: 'array';		AUTO: 'auto';	BOOLEAN: 'boolean';	BREAK: 'break';	CONTINUE: 'continue';
DO: 'do';			ELSE: 'else';	FLOAT: 'float';		FOR: 'for';		FUNCTION: 'function';	
INHERIT: 'inherit';	IF: 'if';		INTEGER: 'integer';	OF: 'of';		OUT: 'out';
RETURN: 'return';	STRING: 'string';	VOID: 'void';	WHILE: 'while';

/****************** OPERATORS *********************/
ADD: '+';	
SUB: '-';	
MUL: '*';	
DIV: '/';	
MOD: '%';	
NOT: '!';	
AND: '&&';	
OR: '||';
EQUAL: '==';	
NOT_EQUAL: '!=';	
LT: '<';	
GT: '>';	
LE: '<=';	
GE: '>=';	
CONCATE: '::';

/****************** SEPARATORS *********************/
LSB: '[';	RSB: ']';	LP: '(';	RP: ')';	LB: '{';	RB: '}';	SM: ';';	CL: ':';
DOT: '.';	CM: ',';	ASSIGN: '=';

/************* FRAGMENTS ************************/
fragment DECPART: DOT [0-9]*;
fragment EXPPART: [eE] (ADD | SUB)? [0-9]+;
fragment CHAR_LIT: ~[\\\r\n\b\f'"] | ESC_SEQ | '\\"';
fragment ESC_SEQ:	'\\\''	| '\\\\'	| '\\b'	| '\\f'	| '\\n'	| '\\r'	| '\\t';
fragment ESC_ILLEGAL: '\\' ~[btnfr"\\] | '\\';
/*********** LITERALS  ***************/
arraylit: LB exprlist RB;
INTLIT: '0' | [1-9]('_'? [0-9])* { self.text = self.text.replace('_','')};
FLOATLIT: (INTLIT DECPART | INTLIT DECPART? EXPPART | DECPART EXPPART) { self.text = self.text.replace('_','')};
BOOLEANLIT: 'true' | 'false';
STRINGLIT: '"' CHAR_LIT* '"' { self.text = self.text[1:-1]};
ID: [_a-zA-Z][_a-zA-Z0-9]*;
UNCLOSE_STRING:
	'"' CHAR_LIT* ([\b\f\n\r"'\\] | EOF) {
if self.text[-1] in ['\b', '\f', '\n', '\r', '"', '\'', '\\']: 
	raise UncloseString(self.text[1:-1])
else: 
	raise UncloseString(self.text[1:])
};

ILLEGAL_ESCAPE:
	'"' CHAR_LIT* ESC_ILLEGAL {
    raise IllegalEscape(self.text[1:])
};

/************************************************/
/****** COMMENTS *****/
LINE_CMT: '//' ~[\r\n\f]* -> skip;
BLOCK_CMT: '/*' .*? '*/' -> skip;

// skip spaces, tabs, newlines
WS: [ \t\r\n\b]+ -> skip;
ERROR_CHAR: . {raise ErrorToken(self.text)};
