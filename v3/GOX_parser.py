# GOX_Parser.py - GoxLang Parser Implementation

from GOX_lexer import Token, tokenize
from GOX_AST_nodes import Integer, Float, Boolean, String, BinOp, UnaryOp, Location, FunctionCall, Print
from GOX_AST_nodes import Assignment, If, ConstantDecl, VariableDecl, FunctionDecl, Return, While, Parameter, Program
from GOX_error_handler import ErrorHandler
import json


class Parser:
    def __init__(self, tokens, error_handler):
        self.tokens = tokens
        self.error_handler = error_handler
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def peek(self, offset=1):
        """Look ahead at the next token without consuming it"""
        peek_pos = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None

    def expect(self, token_type, err_msg=None):
        if self.current_token and self.current_token.type == token_type:
            token = self.current_token
            self.advance()
            return token
        else:
            err = err_msg or f"Expected {token_type}"
            if self.current_token:
                self.error_handler.add_error(err, self.current_token.lineno)
            else:
                self.error_handler.add_error(err, "End of file")
            return False

    def parse(self):
        """Entry point for parsing the entire program"""
        statements = []
        while self.current_token:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            else:
                # Skip invalid token to avoid infinite loop.
                self.advance()
        
        # Wrap statements in a Program node to represent the full AST
        return Program(statements)

    def parse_statement(self):
        """Parse a single statement"""
        if not self.current_token:
            return None

        # Añadir el caso para importar módulos
        if self.current_token.type == 'IMPORT':
            return self.parse_import()
        elif self.current_token.type in ['VAR', 'CONST']:
            stmt = self.parse_declaration()
            # Si la gramática requiere ';' al final de la declaración
            self.expect('SEMI', "Missing ';' after declaration")
            return stmt
        elif self.current_token.type == 'PRINT':
            return self.parse_print()
        elif self.current_token.type == 'IF':
            return self.parse_if()
        elif self.current_token.type == 'WHILE':
            return self.parse_while()
        elif self.current_token.type == 'FUNC':
            return self.parse_function()
        elif self.current_token.type == 'RETURN':
            return self.parse_return()
        elif self.current_token.type == 'ID':
            # Chequear si es llamada a función o asignación
            if self.peek() and self.peek().type == 'LPAREN':
                return self.parse_function_call()
            else:
                return self.parse_assignment()
        else:
            self.error_handler.add_error(
                f"Unexpected token type: {self.current_token.type}", 
                self.current_token.lineno
            )
            self.advance()
            return None

    def parse_expression(self):
        return self.parse_logic_or()

    def parse_logic_or(self):
        node = self.parse_logic_and()
        while self.current_token and self.current_token.type == 'LOR':
            op = self.current_token.value
            self.advance()
            right = self.parse_logic_and()
            node = BinOp(op, node, right)
        return node

    def parse_logic_and(self):
        node = self.parse_comparison()
        while self.current_token and self.current_token.type == 'LAND':
            op = self.current_token.value
            self.advance()
            right = self.parse_comparison()
            node = BinOp(op, node, right)
        return node

    def parse_comparison(self):
        node = self.parse_term()
        while self.current_token and self.current_token.type in ['LT', 'GT', 'LE', 'GE', 'EQ', 'NE']:
            op = self.current_token.value
            self.advance()
            right = self.parse_term()
            node = BinOp(op, node, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current_token and self.current_token.type in ['PLUS', 'MINUS']:
            op = self.current_token.value
            self.advance()
            right = self.parse_factor()
            node = BinOp(op, node, right)
        return node

    def parse_factor(self):
        node = self.parse_unary()
        while self.current_token and self.current_token.type in ['TIMES', 'DIVIDE', 'MOD', 'INT_DIV']:
            op = self.current_token.value
            self.advance()
            right = self.parse_unary()
            node = BinOp(op, node, right)
        return node

    def parse_unary(self):
        if self.current_token and self.current_token.type in ['PLUS', 'MINUS', 'NOT', 'DEREF']:
            op = self.current_token.value
            self.advance()
            return UnaryOp(op, self.parse_primary())
        return self.parse_primary()

    def parse_primary(self):
        token = self.current_token
        if token.type == 'INTEGER':
            self.advance()
            return Integer(int(token.value))
        elif token.type == 'FLOAT':
            self.advance()
            return Float(float(token.value))
        elif token.type == 'LPAREN':
            self.advance()
            expr = self.parse_expression()
            self.expect('RPAREN', "Missing closing parenthesis")
            return expr
        elif token.type == 'ID':
            self.advance()
            node = Location(token.value)
            if self.current_token and self.current_token.type == 'LPAREN':
                # Llamada a función
                self.advance()  # Consume LPAREN
                args = []
                if self.current_token.type != 'RPAREN':
                    args.append(self.parse_expression())
                    while self.current_token and self.current_token.type == 'COMMA':
                        self.advance()
                        args.append(self.parse_expression())
                self.expect('RPAREN', "Expected ')' after function arguments")
                node = FunctionCall(token.value, args)
            return node
        elif token.type in ['TRUE', 'FALSE']:
            self.advance()
            return Boolean(token.value.lower() == 'true')
        elif token.type == 'STRING':
            self.advance()
            return String(token.value)
        else:
            self.error_handler.add_error("Invalid expression", token.lineno)
            self.advance()
            return None

    def parse_location(self):
        ident = self.current_token.value
        self.expect('ID')
        return Location(ident)

    def parse_print(self):
        self.expect('PRINT')
        expr = self.parse_expression()
        self.expect('SEMI', "Missing ';' after print statement")
        return Print(expr)

    def parse_assignment(self):
        location = self.parse_location()
        self.expect('ASSIGN', "Missing '=' in assignment")
        expr = self.parse_expression()
        self.expect('SEMI', "Missing ';' after assignment")
        return Assignment(location, expr)

    def parse_if(self):
        self.expect('IF')
        test = self.parse_expression()
        self.expect('LBRACE', "Missing '{' after if condition")
        consequence = []
        while self.current_token and self.current_token.type != 'RBRACE':
            consequence.append(self.parse_statement())
        self.expect('RBRACE', "Missing '}' at the end of if block")
        
        alternative = []
        if self.current_token and self.current_token.type == 'ELSE':
            self.advance()
            self.expect('LBRACE', "Missing '{' after else")
            while self.current_token and self.current_token.type != 'RBRACE':
                alternative.append(self.parse_statement())
            self.expect('RBRACE', "Missing '}' at the end of else block")
        return If(test, consequence, alternative)

    def parse_while(self):
        self.expect('WHILE')
        test = self.parse_expression()
        self.expect('LBRACE', "Missing '{' after while condition")
        body = []
        while self.current_token and self.current_token.type != 'RBRACE':
            body.append(self.parse_statement())
        self.expect('RBRACE', "Missing '}' at the end of while block")
        return While(test, body)

    def parse_declaration(self):
        is_const = self.current_token.type == 'CONST'
        self.advance()
        ident = self.current_token.value
        self.expect('ID', "Expected identifier in declaration")
        
        # Add proper type handling
        var_type = None
        if self.current_token and self.current_token.type == 'ID':
            var_type = self.current_token.value
            self.advance()
        
        value = None
        if self.current_token and self.current_token.type == 'ASSIGN':
            self.advance()
            value = self.parse_expression()
        
        # More lenient semicolon handling
        if self.current_token and self.current_token.type == 'SEMI':
            self.advance()
        
        return ConstantDecl(ident, value) if is_const else VariableDecl(ident, var_type, value)

    def parse_function_call(self):
        name = self.current_token.value  # Se asume que es una llamada a función
        self.expect('ID', "Expected function name")
        self.expect('LPAREN', "Expected '(' after function name")
        args = []
        if self.current_token.type != 'RPAREN':
            args.append(self.parse_expression())
            while self.current_token and self.current_token.type == 'COMMA':
                self.advance()
                args.append(self.parse_expression())
        self.expect('RPAREN', "Expected ')' after function arguments")
        self.expect('SEMI', "Missing ';' after function call")
        return FunctionCall(name, args)

    def parse_function(self):
        self.expect('FUNC')
        name = self.current_token.value
        self.expect('ID', "Expected function name after FUNC keyword")
        self.expect('LPAREN', "Expected '(' after function name in declaration")
        params = []
        if self.current_token.type != 'RPAREN':
            param_name = self.current_token.value
            self.expect('ID', "Expected parameter name")
            params.append(Parameter(param_name, None))
            while self.current_token and self.current_token.type == 'COMMA':
                self.advance()
                param_name = self.current_token.value
                self.expect('ID', "Expected parameter name")
                params.append(Parameter(param_name, None))
        self.expect('RPAREN', "Expected ')' after parameters in function declaration")
        return_type = None  # Actualmente no se gestiona el tipo de retorno
        self.expect('LBRACE', "Expected '{' to start function body")
        body = []
        while self.current_token and self.current_token.type != 'RBRACE':
            body.append(self.parse_statement())
        self.expect('RBRACE', "Expected '}' to end function body")
        return FunctionDecl(name, params, return_type, body)

    def parse_return(self):
        self.expect('RETURN')
        expr = self.parse_expression()
        self.expect('SEMI', "Missing ';' after return statement")
        return Return(expr)

    def parse_import(self):
        """Parse an import declaration"""
        self.expect('IMPORT')
        module_token = self.expect('ID', "Expected module name after IMPORT")
        if not module_token:
            return None
        self.expect('SEMI', "Missing ';' after import declaration")
        from GOX_AST_nodes import ImportDecl  # Asegurarse de importar el nodo
        return ImportDecl(module_token.value)

    def to_json(self):
        """Convert the AST to JSON format"""
        ast = self.parse()
        if self.error_handler.has_errors():
            return {"errors": self.error_handler.errors}
        return self._serialize_ast(ast)

    def _serialize_ast(self, node):
        """Helper to serialize AST nodes to JSON-compatible dictionaries"""
        if node is None:
            return None
        if isinstance(node, list):
            return [self._serialize_ast(item) for item in node]

        data = {"type": node.__class__.__name__}
        if isinstance(node, Program):
            data["statements"] = self._serialize_ast(node.statements)
        elif isinstance(node, Integer):
            data["value"] = node.value
        elif isinstance(node, Float):
            data["value"] = node.value
        elif isinstance(node, Boolean):
            data["value"] = node.value
        elif isinstance(node, String):
            data["value"] = node.value
        elif isinstance(node, BinOp):
            data["operator"] = node.op
            data["left"] = self._serialize_ast(node.left)
            data["right"] = self._serialize_ast(node.right)
        elif isinstance(node, UnaryOp):
            data["operator"] = node.op
            data["operand"] = self._serialize_ast(node.operand)
        elif isinstance(node, Location):
            data["name"] = node.name
        elif isinstance(node, FunctionCall):
            data["name"] = node.name
            data["arguments"] = self._serialize_ast(node.args)
        elif isinstance(node, Print):
            data["expression"] = self._serialize_ast(node.expr)
        elif isinstance(node, Assignment):
            data["target"] = self._serialize_ast(node.location)
            data["value"] = self._serialize_ast(node.expr)
        elif isinstance(node, If):
            data["condition"] = self._serialize_ast(node.test)
            data["consequence"] = self._serialize_ast(node.consequence)
            data["alternative"] = self._serialize_ast(node.alternative)
        elif isinstance(node, While):
            data["condition"] = self._serialize_ast(node.test)
            data["body"] = self._serialize_ast(node.body)
        elif isinstance(node, VariableDecl):
            data["name"] = node.name
            data["type"] = node.var_type
            data["initial_value"] = self._serialize_ast(node.value)
        elif isinstance(node, ConstantDecl):
            data["name"] = node.name
            data["value"] = self._serialize_ast(node.value)
        elif isinstance(node, FunctionDecl):
            data["name"] = node.name
            data["parameters"] = self._serialize_ast(node.params)
            data["return_type"] = node.return_type
            data["body"] = self._serialize_ast(node.body)
        elif isinstance(node, Return):
            data["value"] = self._serialize_ast(node.expr)
        elif isinstance(node, Parameter):
            data["name"] = node.name
            data["type"] = node.param_type
        # Serializar el nuevo nodo de importación
        elif hasattr(node, "module_name"):
            data["module_name"] = node.module_name
        return data

    def save_ast_to_json(self, filename="ast_oGOXut.json"):
        """Save the AST to a JSON file"""
        ast_json = self.to_json()
        with open(filename, 'w') as f:
            json.dump(ast_json, f, indent=2)
        return ast_json


if __name__ == "__main__":
    import sys
    
    # Check if file argument is provided
    if len(sys.argv) < 2:
        print("Usage: python GOX_parser.py [filename].gox")
        sys.exit(1)
    
    # Get the filename from command line arguments
    filename = sys.argv[1]
    
    # Ensure it's a .gox file
    if not filename.endswith('.gox'):
        print("Error: File must have .gox extension")
        sys.exit(1)
    
    try:
        # Read the content of the file
        with open(filename, 'r') as file:
            code = file.read()
        
        # Create error handler and parse the code
        error_handler = ErrorHandler()
        tokens = tokenize(code, error_handler)
        parser = Parser(tokens, error_handler)
        ast = parser.parse()
        
        # Generate output filename (replace .gox with .json)
        output_filename = filename.rsplit('.', 1)[0] + '.json'
        
        # Handle errors or generate JSON
        if error_handler.has_errors():
            print(f"Parsing failed for {filename}:")
            error_handler.report_errors()
            sys.exit(1)
        else:
            print(f"Successfully parsed {filename}")
            parser.save_ast_to_json(output_filename)
            print(f"AST saved to {output_filename}")
    
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)