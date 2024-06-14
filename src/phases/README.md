Main phases of the Compiler:

Input: string

Step                    Output

Lexing                  tokens
Parsing                 ast
Static Check            ast
AST Optimization        ast
ST Build                st
CFG Build               cfg
CFG Optimization        cfg
Code Generation         string
