# UTP_AST_nodes.py
# AST Node Definitions

class ASTNode:
    """Base class for all AST nodes."""
    pass

# ---------------------------------------------------------------------
# Expressions
# ---------------------------------------------------------------------

class Integer(ASTNode):
    """Represents an integer literal."""
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Integer({self.value})"

class Float(ASTNode):
    """Represents a float literal."""
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Float({self.value})"

class BinOp(ASTNode):
    """Represents a binary operation (e.g., 2 + 3)."""
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinOp({self.op}, {self.left}, {self.right})"

class UnaryOp(ASTNode):
    """Represents a unary operation (e.g., -5, !true)."""
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

    def __repr__(self):
        return f"UnaryOp({self.op}, {self.operand})"

class Location(ASTNode):
    """Represents a location (variable or memory address)."""
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Location({self.name})"

class FunctionCall(ASTNode):
    """Represents a function call."""
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"FunctionCall({self.name}, {self.args})"

class TypeCast(ASTNode):
    """Represents a type cast (e.g., int(3.14))."""
    def __init__(self, target_type, expr):
        self.target_type = target_type
        self.expr = expr

    def __repr__(self):
        return f"TypeCast({self.target_type}, {self.expr})"

# ---------------------------------------------------------------------
# Additional Expressions
# ---------------------------------------------------------------------

class String(ASTNode):
    """Represents a string literal."""
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"String('{self.value}')"

class Boolean(ASTNode):
    """Represents a boolean literal."""
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Boolean({self.value})"

class CompareOp(ASTNode):
    """Represents a comparison operation (e.g., x > y)."""
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"CompareOp({self.op}, {self.left}, {self.right})"

class LogicalOp(ASTNode):
    """Represents a logical operation (e.g., x && y)."""
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"LogicalOp({self.op}, {self.left}, {self.right})"

class ArrayLiteral(ASTNode):
    """Represents an array literal."""
    def __init__(self, elements):
        self.elements = elements

    def __repr__(self):
        return f"ArrayLiteral({self.elements})"

class IndexAccess(ASTNode):
    """Represents an index access (e.g., arr[i])."""
    def __init__(self, array, index):
        self.array = array
        self.index = index

    def __repr__(self):
        return f"IndexAccess({self.array}, {self.index})"

# ---------------------------------------------------------------------
# Declarations
# ---------------------------------------------------------------------

class VariableDecl(ASTNode):
    """Represents a variable declaration."""
    def __init__(self, name, var_type, value=None):
        self.name = name
        self.var_type = var_type
        self.value = value

    def __repr__(self):
        return f"VariableDecl({self.name}, {self.var_type}, {self.value})"

class ConstantDecl(ASTNode):
    """Represents a constant declaration."""
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"ConstantDecl({self.name}, {self.value})"

class FunctionDecl(ASTNode):
    """Represents a function declaration."""
    def __init__(self, name, params, return_type, body):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body

    def __repr__(self):
        return f"FunctionDecl({self.name}, {self.params}, {self.return_type}, {self.body})"

# ---------------------------------------------------------------------
# Statements
# ---------------------------------------------------------------------

class Assignment(ASTNode):
    """Represents an assignment (e.g., x = 10)."""
    def __init__(self, location, expr):
        self.location = location
        self.expr = expr

    def __repr__(self):
        return f"Assignment({self.location}, {self.expr})"

class Print(ASTNode):
    """Represents a print statement (e.g., print x)."""
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"Print({self.expr})"

class If(ASTNode):
    """Represents an if/else statement."""
    def __init__(self, test, consequence, alternative=None):
        self.test = test
        self.consequence = consequence
        self.alternative = alternative

    def __repr__(self):
        return f"If({self.test}, {self.consequence}, {self.alternative})"

class While(ASTNode):
    """Represents a while loop."""
    def __init__(self, test, body):
        self.test = test
        self.body = body

    def __repr__(self):
        return f"While({self.test}, {self.body})"

class Return(ASTNode):
    """Represents a return statement (e.g., return x)."""
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"Return({self.expr})"

# ---------------------------------------------------------------------
# Additional Statements
# ---------------------------------------------------------------------

class For(ASTNode):
    """Represents a for loop."""
    def __init__(self, init, test, update, body):
        self.init = init
        self.test = test
        self.update = update
        self.body = body

    def __repr__(self):
        return f"For({self.init}, {self.test}, {self.update}, {self.body})"

class Block(ASTNode):
    """Represents a block of statements."""
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Block({self.statements})"

class Break(ASTNode):
    """Represents a break statement."""
    def __repr__(self):
        return "Break()"

class Continue(ASTNode):
    """Represents a continue statement."""
    def __repr__(self):
        return "Continue()"

# ---------------------------------------------------------------------
# Other
# ---------------------------------------------------------------------

class SymbolTable:
    """Manages symbol tables for variables and functions."""
    def __init__(self):
        self.scopes = [{}]

    def declare_variable(self, name, var_type, value=None):
        """Declares a variable in the current scope."""
        self.scopes[-1][name] = {'type': var_type, 'value': value}

    def declare_constant(self, name, value):
        """Declares a constant in the current scope."""
        self.scopes[-1][name] = {'type': type(value).__name__, 'value': value}

    def lookup(self, name):
        """Looks up a symbol in the scopes."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

class Parameter(ASTNode):
    """Represents a function parameter."""
    def __init__(self, name, param_type):
        self.name = name
        self.param_type = param_type

    def __repr__(self):
        return f"Parameter({self.name}, {self.param_type})"

class Program(ASTNode):
    """Root node representing a complete program."""
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Program({self.statements})"