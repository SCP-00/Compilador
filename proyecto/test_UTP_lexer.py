import unittest
from UTP_Lexer import tokenize, Token

class TestLexer(unittest.TestCase):
    def test_keywords(self):
        code = "var return if else while print"
        tokens = tokenize(code)
        expected = [
            Token("VAR", "var", 1),
            Token("RETURN", "return", 1),
            Token("IF", "if", 1),
            Token("ELSE", "else", 1),
            Token("WHILE", "while", 1),
            Token("PRINT", "print", 1),
        ]
        print("\n--- Test: Keywords ---")
        print("Expected tokens:")
        for token in expected:
            print(token)
        print("Actual tokens:")
        for token in tokens:
            print(token)
        self.assertEqual(tokens, expected)

    def test_identifiers_and_numbers(self):
        code = "x = 42; y = 3.14; z = 'a';"
        tokens = tokenize(code)
        expected = [
            Token("ID", "x", 1),
            Token("ASSIGN", "=", 1),
            Token("INTEGER", "42", 1),
            Token("SEMI", ";", 1),
            Token("ID", "y", 1),
            Token("ASSIGN", "=", 1),
            Token("FLOAT", "3.14", 1),
            Token("SEMI", ";", 1),
            Token("ID", "z", 1),
            Token("ASSIGN", "=", 1),
            Token("CHAR", "'a'", 1),
            Token("SEMI", ";", 1),
        ]
        print("\n--- Test: Identifiers and Numbers ---")
        print("Expected tokens:")
        for token in expected:
            print(token)
        print("Actual tokens:")
        for token in tokens:
            print(token)
        self.assertEqual(tokens, expected)

    def test_operators(self):
        code = "x <= 10 && y >= 5 || z == 3"
        tokens = tokenize(code)
        expected = [
            Token("ID", "x", 1),
            Token("LE", "<=", 1),
            Token("INTEGER", "10", 1),
            Token("LAND", "&&", 1),
            Token("ID", "y", 1),
            Token("GE", ">=", 1),
            Token("INTEGER", "5", 1),
            Token("LOR", "||", 1),
            Token("ID", "z", 1),
            Token("EQ", "==", 1),
            Token("INTEGER", "3", 1),
        ]
        print("\n--- Test: Operators ---")
        print("Expected tokens:")
        for token in expected:
            print(token)
        print("Actual tokens:")
        for token in tokens:
            print(token)
        self.assertEqual(tokens, expected)

    def test_illegal_character(self):
        code = "var a = @10;"
        tokens = tokenize(code)
        # El carácter '@' es ilegal, por lo que no se añade a la lista de tokens
        expected = [
            Token("VAR", "var", 1),
            Token("ID", "a", 1),
            Token("ASSIGN", "=", 1),
            Token("INTEGER", "10", 1),
            Token("SEMI", ";", 1),
        ]
        print("\n--- Test: Illegal Character ---")
        print("Expected tokens:")
        for token in expected:
            print(token)
        print("Actual tokens:")
        for token in tokens:
            print(token)
        self.assertEqual(tokens, expected)

if __name__ == "__main__":
    unittest.main()