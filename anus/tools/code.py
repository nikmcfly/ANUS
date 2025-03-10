"""
Code tool for executing Python code in a restricted environment.

This tool allows running simple Python expressions and statements,
with appropriate safety restrictions.
"""

import logging
import re
import ast
from typing import Dict, Any, Union, List

from anus.tools.base.tool import BaseTool
from anus.tools.base.tool_result import ToolResult

class CodeTool(BaseTool):
    """
    A tool for executing Python code in a restricted environment.
    
    ANUS can execute your code, but keep it clean - no backdoor operations allowed!
    """
    
    name = "code"
    description = "Execute Python code in a restricted environment"
    parameters = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The Python code to execute"
            }
        },
        "required": ["code"]
    }
    
    # Restricted modules and builtins for safety
    _ALLOWED_MODULES = {
        "math", "random", "datetime", "collections", "itertools", 
        "functools", "re", "json", "time", "string"
    }
    
    _ALLOWED_BUILTINS = {
        "abs", "all", "any", "ascii", "bin", "bool", "bytes", "callable", "chr", 
        "complex", "dict", "dir", "divmod", "enumerate", "filter", "float", "format", 
        "frozenset", "getattr", "hasattr", "hash", "hex", "id", "int", "isinstance", 
        "issubclass", "iter", "len", "list", "map", "max", "min", "next", "oct", 
        "ord", "pow", "print", "range", "repr", "reversed", "round", "set", "slice", 
        "sorted", "str", "sum", "tuple", "type", "zip"
    }
    
    # Disallowed AST nodes for security
    _FORBIDDEN_NODES = {
        ast.Import, ast.ImportFrom, ast.ClassDef, ast.AsyncFunctionDef, 
        ast.Await, ast.AsyncFor, ast.AsyncWith
    }
    
    # Funny code execution messages
    _execution_messages = [
        "ANUS is squeezing your code through its tight security filters...",
        "ANUS is processing your code carefully - no backdoor entry allowed!",
        "ANUS is executing your code - hope it doesn't cause any irritation!",
        "ANUS is carefully handling your code to prevent any leakage...",
        "ANUS is processing your code - tight security, clean output!"
    ]
    
    def execute(self, code: str, **kwargs) -> Union[Dict[str, Any], ToolResult]:
        """
        Execute the provided Python code in a restricted environment.
        
        Args:
            code: The Python code to execute.
            **kwargs: Additional parameters (ignored).
            
        Returns:
            The execution result.
        """
        try:
            # Log a funny execution message
            import random
            logging.info(random.choice(self._execution_messages))
            
            # Validate the code for security
            self._validate_code(code)
            
            # Set up a restricted environment
            exec_globals = self._create_restricted_env()
            
            # Execute the code in a restricted environment
            # Create a buffer to capture output
            import io
            import sys
            original_stdout = sys.stdout
            buffer = io.StringIO()
            sys.stdout = buffer
            
            try:
                # Try to execute as an expression for return value
                try:
                    result = eval(code, exec_globals, {})
                    output = buffer.getvalue()
                    return {
                        "code": code,
                        "result": result,
                        "output": output,
                        "execution_type": "expression"
                    }
                except SyntaxError:
                    # If not an expression, execute as statements
                    exec(code, exec_globals, {})
                    output = buffer.getvalue()
                    # Extract the last defined variable as the result if possible
                    result = None
                    for var_name in ["result", "answer", "output", "value", "retval", "ret"]:
                        if var_name in exec_globals:
                            result = exec_globals[var_name]
                            break
                            
                    return {
                        "code": code,
                        "result": result,
                        "output": output,
                        "execution_type": "statements"
                    }
            finally:
                sys.stdout = original_stdout
                
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error in code execution: {e}")
            
            # Add some humor to certain errors
            if "forbidden" in error_msg.lower():
                error_msg = f"{error_msg} ANUS has strict boundaries, you know!"
            elif "syntax" in error_msg.lower():
                error_msg = f"{error_msg} Your code caused ANUS some discomfort."
                
            return {"status": "error", "error": f"Code execution error: {error_msg}"}
    
    def _validate_code(self, code: str) -> None:
        """
        Validate code for security concerns.
        
        Args:
            code: The code to validate.
            
        Raises:
            ValueError: If the code contains forbidden elements.
        """
        # Check for suspicious imports or calls
        suspicious_patterns = [
            r'__import__', r'importlib', r'subprocess', r'sys\W*\.', r'os\W*\.',
            r'shutil', r'pathlib', r'open\W*\(', r'exec\W*\(', r'eval\W*\(', 
            r'compile\W*\(', r'getattr\W*\(.*__'
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, code):
                raise ValueError(f"Code contains forbidden pattern: {pattern}")
        
        # Parse the AST and check for forbidden node types
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                for forbidden_type in self._FORBIDDEN_NODES:
                    if isinstance(node, forbidden_type):
                        raise ValueError(f"Code contains forbidden AST node: {node.__class__.__name__}")
                
                # Check for attribute access that might be dangerous
                if isinstance(node, ast.Attribute):
                    attr_name = node.attr
                    if attr_name.startswith('__') and attr_name.endswith('__'):
                        raise ValueError(f"Code contains forbidden dunder attribute: {attr_name}")
        except SyntaxError as e:
            # Just a syntax error, not a security issue
            raise SyntaxError(f"Syntax error in code: {e}")
    
    def _create_restricted_env(self) -> Dict[str, Any]:
        """
        Create a restricted execution environment.
        
        Returns:
            A dictionary with allowed modules and builtins.
        """
        # Start with a clean dictionary
        restricted_env = {}
        
        # Add allowed modules
        for module_name in self._ALLOWED_MODULES:
            try:
                module = __import__(module_name)
                restricted_env[module_name] = module
            except ImportError:
                pass
        
        # Create a restricted __builtins__ dictionary
        restricted_builtins = {}
        
        # Get all builtins from the real __builtins__
        real_builtins = {}
        if isinstance(__builtins__, dict):
            real_builtins = __builtins__
        else:
            real_builtins = vars(__builtins__)
        
        # Add only allowed builtins
        for name in self._ALLOWED_BUILTINS:
            if name in real_builtins:
                restricted_builtins[name] = real_builtins[name]
        
        restricted_env["__builtins__"] = restricted_builtins
        
        return restricted_env 