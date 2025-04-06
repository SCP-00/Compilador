# GOX_error_handler.py
# Error handler for the compiler

class ErrorHandler:
    def __init__(self):
        self.errors = []  # List of registered errors

    def add_error(self, message, lineno, colno=None):
        """
        Registers an error with its message and location.
        - message: Error description
        - lineno: Line number
        - colno: Column number (optional)
        """
        error_entry = {
            'message': message,
            'lineno': lineno,
            'colno': colno
        }
        self.errors.append(error_entry)

    def has_errors(self):
        """Indicates if there are registered errors."""
        return len(self.errors) > 0

    def report_errors(self):
        """Prints all errors in a readable format."""
        for error in self.errors:
            line_info = f"Line {error['lineno']}"
            if error['colno']:
                line_info += f":{error['colno']}"
            print(f"{line_info} - Error: {error['message']}")

    def clear_errors(self):
        """Clears all registered errors."""
        self.errors = []

# Usage example
if __name__ == "__main__":
    error_handler = ErrorHandler()
    error_handler.add_error("Undeclared variable 'x'", 5)
    error_handler.add_error("Incompatible types in operation '+'", 10, 8)
    
    if error_handler.has_errors():
        print("--- Errors found ---")
        error_handler.report_errors()
