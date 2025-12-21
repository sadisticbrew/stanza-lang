expression : term ((PLUS|MINUS) term)*

term : factor ((MULTIPLY|DIVIDE) factor)*

factor : INT|FLOAT
       : (PLUS | MINUS) INT|FLOAT
       : LPAREN expression RPAREN
