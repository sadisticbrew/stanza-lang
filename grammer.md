expression : term ((PLUS|MINUS) term)*

term : factor ((MULTIPLY|DIVIDE) factor)*

factor : INT|FLOAT
