# Definición de tipos de token
NUMBER  = 'NUMBER'
ID      = 'ID'
PLUS    = 'PLUS'
MINUS   = 'MINUS'
TIMES   = 'TIMES'
DIVIDE  = 'DIVIDE'
LPAREN  = 'LPAREN'
RPAREN  = 'RPAREN'
ASSIGN  = 'ASSIGN'
EOF     = 'EOF'
POWER   = 'POWER'
INT_DIVIDE = 'INT_DIVIDE'

# Clase Token: representa un token con su tipo y valor.
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)})'

# Lexer: convierte el texto de entrada en una secuencia de tokens.
class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None

    def advance(self):
        """Avanza un carácter en el texto de entrada."""
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def peek(self):
        """Mira el siguiente carácter sin avanzar."""
        peek_pos = self.pos + 1
        if peek_pos < len(self.text):
            return self.text[peek_pos]
        else:
            return None

    def skip_whitespace(self):
        """Omite los espacios en blanco."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self):
        """Extrae un número (entero o flotante)."""
        result = ''
        dot_count = 0
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                dot_count += 1
                if dot_count > 1:
                    break  # No permitimos más de un punto
            result += self.current_char
            self.advance()
        if dot_count == 0:
            return Token(NUMBER, int(result))
        else:
            return Token(NUMBER, float(result))

    def identifier(self):
        """Extrae un identificador (variable)."""
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return Token(ID, result)

    def get_next_token(self):
        """Devuelve el siguiente token encontrado en el texto."""
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isdigit():
                return self.number()
            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()
            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')
            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')
            if self.current_char == '*':
                self.advance()
                if self.peek() == '*':
                    self.advance()
                    return Token(POWER, '**')
                else:
                    return Token(TIMES, '*')
            if self.current_char == '/':
                self.advance()
                if self.peek() == '/':
                    self.advance()
                    return Token(INT_DIVIDE, '//')
                else:
                    return Token(DIVIDE, '/')
            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')
            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')
                return Token(ASSIGN, '=')
            raise Exception(f"Carácter inesperado: {self.current_char}")
        return Token(EOF, None)

# Parser: analiza la secuencia de tokens utilizando recursión de acuerdo a la gramática.
class Parser:
    def __init__(self, lexer, env):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.env = env  # entorno para almacenar las variables

    def error(self, msg):
        raise Exception("Error de sintaxis: " + msg)

    def eat(self, token_type):
        """Consume el token actual si coincide con el tipo esperado."""
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Se esperaba {token_type}, se encontró {self.current_token.type}")

    def parse(self):
        """
        program ::= statement*
        Permite procesar varias líneas (declaraciones) a la vez.
        """
        results = []
        while self.current_token.type != EOF:
            results.append(self.statement())
        return results

    def statement(self):
        """
        statement ::= assignment | expression
        Si el token actual es ID y el siguiente es '=', se trata de una asignación.
        """
        if self.current_token.type == ID:
            # Se hace una verificación preliminar: ¿existe un '=' después del ID?
            # token_backup = self.current_token
            # lexer_backup_pos = self.lexer.pos
            # lexer_backup_char = self.lexer.current_char

            next_token = self.lexer.get_next_token()
            if next_token.type == ASSIGN:
                return self.assignment()

        # Si no es asignación, se procesa como expresión.
        return self.expression()

    def assignment(self):
        """
        assignment ::= 'ID' '=' expression
        Almacena el valor de la expresión en el entorno.
        """
        var_name = self.current_token.value
        self.eat(ID)
        self.eat(ASSIGN)
        value = self.expression()
        self.env[var_name] = value
        return value

    def expression(self):
        """
        expression ::= term (('+' | '-') term)*
        """
        result = self.term()
        while self.current_token.type in (PLUS, MINUS):
            if self.current_token.type == PLUS:
                self.eat(PLUS)
                result += self.term()
            elif self.current_token.type == MINUS:
                self.eat(MINUS)
                result -= self.term()
        return result

    def term(self):
        """
        term ::= factor (('*' | '/' | '//') factor)*
        """
        result = self.factor()
        while self.current_token.type in (TIMES, DIVIDE, INT_DIVIDE, POWER):
            if self.current_token.type == TIMES:
                self.eat(TIMES)
                result *= self.factor()
            elif self.current_token.type == DIVIDE:
                self.eat(DIVIDE)
                divisor = self.factor()
                if divisor == 0:
                    raise Exception("Error: División por cero")
                result /= divisor
            elif self.current_token.type == INT_DIVIDE:
                self.eat(INT_DIVIDE)
                divisor = self.factor()
                if divisor == 0:
                    raise Exception("Error: División por cero")
                result //= divisor
            elif self.current_token.type == POWER:
                self.eat(POWER)
                result **= self.factor()
        return result

    def factor(self):
        """
        factor ::= 'NUMBER' | 'ID' | '(' expression ')' | '-' factor
        """
        token = self.current_token
        if token.type == NUMBER:
            self.eat(NUMBER)
            return token.value
        elif token.type == ID:
            self.eat(ID)
            if token.value in self.env:
                return self.env[token.value]
            else:
                raise Exception(f"Variable '{token.value}' no definida")
        elif token.type == LPAREN:
            self.eat(LPAREN)
            result = self.expression()
            self.eat(RPAREN)
            return result
        elif token.type == MINUS:
            self.eat(MINUS)
            return -self.factor()
        else:
            self.error("Factor inesperado")

# Función principal que implementa un bucle interactivo para la calculadora.
def calculator():
    print("Calculadora - Analizador Descendente Recursivo")
    env = {}  # entorno para almacenar variables
    while True:
        try:
            text = input(">> ")  # se lee la entrada del usuario
            if text.strip() == "":
                continue
            if text.lower() == "exit":
                print("Saliendo de la calculadora.")
                exit()
            # Se crea el lexer y el parser para la línea ingresada.
            lexer = Lexer(text)
            parser = Parser(lexer, env)
            # Se procesa una declaración (assignment o expresión)
            result = parser.statement()
            print("Resultado:", result)
        except Exception as e:
            print("Error:", e)

def main():
    calculator()

if __name__ == '__main__':
    main()