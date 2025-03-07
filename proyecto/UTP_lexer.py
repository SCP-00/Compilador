import re
from dataclasses import dataclass

# Definición de tokens con orden adecuado:
TOKEN_SPEC = [
    # Palabras reservadas (se usan límites de palabra para evitar coincidencias parciales)
    ('CONST', r'\bconst\b'),
    ('VAR', r'\bvar\b'),
    ('PRINT', r'\bprint\b'),
    ('RETURN', r'\breturn\b'),
    ('BREAK', r'\bbreak\b'),
    ('CONTINUE', r'\bcontinue\b'),
    ('IF', r'\bif\b'),
    ('ELSE', r'\belse\b'),
    ('WHILE', r'\bwhile\b'),
    ('FUNC', r'\bfunc\b'),
    ('IMPORT', r'\bimport\b'),
    ('TRUE', r'\btrue\b'),
    ('FALSE', r'\bfalse\b'),
    ('INPUT', r'\binput\b'),
    # Nuevas palabras reservadas para funciones matemáticas
    ('LOG', r'\blog\b'),
    ('LN', r'\bln\b'),
    ('SIN', r'\bsin\b'),
    ('COS', r'\bcos\b'),
    ('TAN', r'\btan\b'),
    ('SQRT', r'\bsqrt\b'),
    
    # Literales numéricos y de caracteres
    # Notación científica y diferentes bases numéricas
    ('SCIENTIFIC', r'\d+(\.\d*)?[eE][+-]?\d+'),
    ('HEX', r'0[xX][0-9a-fA-F]+'),
    ('BINARY', r'0[bB][01]+'),
    ('OCTAL', r'0[oO][0-7]+'),
    ('FLOAT', r'\d+\.\d*|\.\d+'),
    ('INTEGER', r'\d+'),
    ('CHAR', r"'([^\\]|\\.)'"),
    ('STRING', r'"([^\\"]|\\.)*"'),
    
    # Identificadores (después de las palabras reservadas)
    ('ID', r'[a-zA-Z_][a-zA-Z_0-9]*'),
    
    # Operadores compuestos (más de un carácter)
    ('INT_DIV', r'//'),
    ('POWER', r'\*\*'),  # Potencia alternativa a ^
    ('LE', r'<='), ('GE', r'>='), ('EQ', r'=='), ('NE', r'!='), 
    ('LAND', r'&&'), ('LOR', r'\|\|'),
    ('INC', r'\+\+'), ('DEC', r'--'),
    ('PLUS_ASSIGN', r'\+='), ('MINUS_ASSIGN', r'-='), 
    ('TIMES_ASSIGN', r'\*='), ('DIV_ASSIGN', r'/='),
    ('MOD_ASSIGN', r'%='), ('POW_ASSIGN', r'\^='),
    
    # Operadores de un solo carácter
    ('LT', r'<'), ('GT', r'>'), ('PLUS', r'\+'), ('MINUS', r'-'),
    ('TIMES', r'\*'), ('DIVIDE', r'/'), ('MOD', r'%'), ('GROW', r'\^'), ('ASSIGN', r'='),
    
    # Otros símbolos
    ('SEMI', r';'), ('LPAREN', r'\('), ('RPAREN', r'\)'),
    ('LBRACE', r'\{'), ('RBRACE', r'\}'), ('LBRACKET', r'\['), ('RBRACKET', r'\]'),
    ('COMMA', r','), ('DOT', r'\.'), ('COLON', r':'), ('DEREF', r'`'),
    
    # Comentarios (pueden ser de línea o de bloque)
    ('COMMENT', r'//.*|/\*[\s\S]*?\*/'),
    
    # Espacios en blanco (se ignoran)
    ('WHITESPACE', r'\s+'),
    
    # Cualquier otro carácter (para capturar errores)
    ('MISMATCH', r'.')
]

# Crear la expresión regular combinada a partir de los tokens
token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC)

@dataclass
class Token:
    type: str   # Tipo del token (por ejemplo, VAR, ID, ASSIGN, etc.)
    value: str  # Cadena que coincide (lexema)
    lineno: int # Número de línea donde se encontró el token

def tokenize(text):
    """
    Función que recibe un código fuente y retorna una lista de tokens.
    Los tokens se generan utilizando la expresión regular compuesta.
    """
    tokens = []
    lineno = 1
    # re.finditer nos permite recorrer todas las coincidencias en el texto.
    for match in re.finditer(token_regex, text, re.DOTALL):
        kind = match.lastgroup  # Nombre del token
        value = match.group()     # Lexema encontrado
        if kind == 'WHITESPACE':
            lineno += value.count('\n')
            continue
        elif kind == 'COMMENT':
            # Se ignoran los comentarios
            lineno += value.count('\n')
            continue
        elif kind == 'MISMATCH':
            print(f"Línea {lineno}: Error - Caracter ilegal '{value}'")
            continue
        tokens.append(Token(kind, value, lineno))
    return tokens

# Ejemplo de uso del lexer
if __name__ == "__main__":
    test_code = """
    var a = 100;
    var b = @20;  // '@' es un caracter ilegal
    """
    for tok in tokenize(test_code):
        print(tok)
