import unittest

from basic import (
    TT_DIVIDE,
    TT_FLOAT,
    TT_INT,
    TT_LPAREN,
    TT_MINUS,
    TT_MUL,
    TT_PLUS,
    TT_RPAREN,
    Lexer,
)


class TestLexer(unittest.TestCase):
    def test_empty_string(self):
        """Test that empty input returns no tokens and no error."""
        lexer = Lexer("")
        tokens, error = lexer.make_tokens()
        self.assertEqual(tokens, [])
        self.assertIsNone(error)

    def test_integers(self):
        """Test parsing of single and multiple integers."""
        lexer = Lexer("123 456")
        tokens, error = lexer.make_tokens()

        self.assertIsNone(error)
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].type, TT_INT)
        self.assertEqual(tokens[0].value, 123)
        self.assertEqual(tokens[1].type, TT_INT)
        self.assertEqual(tokens[1].value, 456)

    def test_floats(self):
        """Test parsing of floating point numbers."""
        lexer = Lexer("3.14 .5")
        tokens, error = lexer.make_tokens()

        self.assertIsNone(error)
        self.assertEqual(tokens[0].type, TT_FLOAT)
        self.assertEqual(tokens[0].value, 3.14)
        self.assertEqual(tokens[1].type, TT_FLOAT)
        self.assertEqual(tokens[1].value, 0.5)

    def test_operators(self):
        """Test that all arithmetic operators are recognized."""
        lexer = Lexer("+ - * /")
        tokens, error = lexer.make_tokens()

        self.assertIsNone(error)
        expected_types = [TT_PLUS, TT_MINUS, TT_MUL, TT_DIVIDE]

        self.assertEqual(len(tokens), 4)
        for i, token in enumerate(tokens):
            self.assertEqual(token.type, expected_types[i])

    def test_parentheses(self):
        """Test left and right parentheses."""
        # NOTE: This test assumes standard logic: '(' is LPAREN, ')' is RPAREN
        lexer = Lexer("( )")
        tokens, error = lexer.make_tokens()

        self.assertIsNone(error)
        self.assertEqual(tokens[0].type, TT_LPAREN)
        self.assertEqual(tokens[1].type, TT_RPAREN)

    def test_mixed_expression(self):
        """Test a complex expression with mixed types."""
        lexer = Lexer("10 + 2.5 * 4")
        tokens, error = lexer.make_tokens()

        self.assertIsNone(error)
        self.assertEqual(len(tokens), 5)
        self.assertEqual(tokens[0].value, 10)
        self.assertEqual(tokens[1].type, TT_PLUS)
        self.assertEqual(tokens[2].value, 2.5)

    def test_illegal_character(self):
        """Test that invalid characters return an error."""
        lexer = Lexer("1 + @")
        tokens, error = lexer.make_tokens()

        self.assertEqual(tokens, [])
        self.assertIsNotNone(error)
        self.assertEqual(error.error_name, "Illegal Character")
        self.assertIn("@", error.details)


if __name__ == "__main__":
    unittest.main()
