expression :  KEYWORD:LET IDENTIFIER EQ EXPR
              comp-expr ((KEYWORD: AND| KEYWORD: OR) comp-expr)*

comp-expr : NOT comp-expr
            arith-expr ((EE|LTE|GTE|GT|LT) arith-expr)*
            
artih-expr :  term ((PLUS|MINUS) term)*

term : factor ((MULTIPLY|DIVIDE) factor)*

factor : INT|FLOAT
       : (PLUS | MINUS) INT|FLOAT
       : LPAREN expression RPAREN
       : if-expr
       
if-expr : KEYWORD:IF condition KEYWORD:THEN expr
        : (KEYWORD:ELIF condition KEYWORD:THEN expr)*
        : (KEYWORD:ELSE expr)?

for-expr : KEYWORD:FOR IDENTIFIER IN expr TO expr
           (KEYWORD:STEP expr)? KEYWORD:DO expr

while-expr : KEYWORD:WHILE expr KEYWORD:DO expr

variable : let var_name = value
