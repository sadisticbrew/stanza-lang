from lexer import Lexer
from parser import Parser


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
    return ast.node, ast.error
