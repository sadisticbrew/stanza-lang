from stanza import Interpreter, Lexer, Parser, SymbolTable

global_table = SymbolTable()
global_table.set("null", 0)


def run(filename, text):
    # Generate tokens
    lexer = Lexer(filename, text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error
    # Generate AST
    print(tokens)
    parser = Parser(tokens)
    ast = parser.parse()
    print(ast.node)
    if ast.error:
        return None, ast.error
    interpreter = Interpreter(global_table)
    result = interpreter.visit(ast.node)
    return result.value, result.error
