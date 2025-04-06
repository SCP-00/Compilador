# GOX_lexer.py
import re

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

    # Data types
    ('INT', r'\bint\b'),
    ('FLOAT_TYPE', r'\bfloat\b'),
    ('BOOL', r'\bbool\b'),
    ('STRING_TYPE', r'\bstring\b'),
    ('CHAR_TYPE', r'\bchar\b'),

    ('HEX', r'0[xX][0-9a-fA-F]+'),
    ('BINARY', r'0[bB][01]+'),

    ('FLOAT', r'\d+\.\d*|\.\d+'),
    ('INTEGER', r'\d+'),
    ('CHAR', r"'([^\\]|\\.)'"),
    ('STRING', r'"([^\\"]|\\.)*"'),
    
    # Identificadores (después de las palabras reservadas)
    ('ID', r'[a-zA-Z_][a-zA-Z_0-9]*'),
    
    # Operadores compuestos (más de un carácter)
    ('INT_DIV', r'//(?=\s*\d)'),  # División entera: solo coincide si después de '//' hay dígitos (o espacios y dígitos)
    ('POWER', r'\*\*'),  # Potencia alternativa a ^

    # Comentarios (pueden ser de línea o de bloque, incluso si un bloque se extiende en una sola línea)
    ('COMMENT', r'//.*|/\*[\s\S]*?\*/'),
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
    
    
    # Espacios en blanco (se ignoran)
    ('WHITESPACE', r'\s+'),
    
    # Cualquier otro carácter (para capturar errores)
    ('MISMATCH', r'.')
]

# Crear la expresión regular combinada a partir de los tokens
token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC)

class Token:
    def __init__(self, type: str, value: str, lineno: int):
        self.type = type
        self.value = value
        self.lineno = lineno

    def __repr__(self):
        return f"Token(type='{self.type}', value='{self.value}', lineno={self.lineno})"

def tokenize(text, error_handler):
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
            error_handler.add_error(f"Caracter ilegal '{value}'", lineno)
            continue
        tokens.append(Token(kind, value, lineno))
    return tokens

# Ejemplo de uso del lexer
if __name__ == "__main__":
    from GOX_error_handler import ErrorHandler
    test_code = """
    /* mandelplot.gox */

import func put_image(base int, width int, height int) int;

const xmin = -2.0;
const xmax = 1.0;
const ymin = -1.5;
const ymax = 1.5;
const threshhold = 1000;

func in_mandelbrot(x0 float, y0 float, n int) bool {
    var x float = 0.0;
    var y float = 0.0;
    var xtemp float;
    while n > 0 {
        xtemp = x*x - y*y + x0;
        y = 2.0*x*y + y0;
        x = xtemp;
        n = n - 1;
        if x*x + y*y > 4.0 {
            return false;
        }
    }
    return true;
}

func mandel(width int, height int) int {
     var dx float = (xmax - xmin)/float(width);
     var dy float = (ymax - ymin)/float(height);
     var ix int = 0;
     var iy int = height-1;
     var addr int = 0;
     var memsize int = ^(width*height*4);

     while iy >= 0 {
         ix = 0;
         while ix < width {
             if in_mandelbrot(float(ix)*dx+xmin, float(iy)*dy+ymin, threshhold) {
        `addr = '\xff';
        `(addr+1) = '\x00';
        `(addr+2) = '\xff';
        `(addr+3) = '\xff';
             } else {
        `addr = '\xff';
        `(addr+1) = '\xff';
        `(addr+2) = '\xff';
        `(addr+3) = '\xff';
             }
             addr = addr + 4;
             ix = ix + 1;
         }
         iy = iy - 1;
     }
     return 0;
}

func make_plot(width int, height int) int {
    var result int = mandel(width, height);
    return put_image(0, width, height);
}

make_plot(800,800);



    """
    error_handler = ErrorHandler()
    tokens = tokenize(test_code, error_handler)
    for tok in tokens:
        print(tok)
    if error_handler.has_errors():
        print("--- Errors found ---")
        error_handler.report_errors()
