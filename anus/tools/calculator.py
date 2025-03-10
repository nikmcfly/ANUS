"""
Calculator tool for basic arithmetic operations.

This tool provides safe evaluation of mathematical expressions.
"""

import logging
import ast
import operator
from typing import Dict, Any, Union

from anus.tools.base.tool import BaseTool
from anus.tools.base.tool_result import ToolResult

class CalculatorTool(BaseTool):
    """
    A tool for performing basic arithmetic calculations.
    
    ANUS can handle your numbers with precision and care.
    """
    
    name = "calculator"
    description = "Perform basic arithmetic calculations"
    parameters = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "The mathematical expression to evaluate"
            }
        },
        "required": ["expression"]
    }
    
    # Supported operators and their corresponding functions
    _OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,  # Unary minus
    }
    
    def execute(self, expression: str, **kwargs) -> Union[Dict[str, Any], ToolResult]:
        """
        Execute the calculator tool.
        
        Args:
            expression: The mathematical expression to evaluate.
            **kwargs: Additional parameters (ignored).
            
        Returns:
            The calculation result.
        """
        try:
            # Clean the expression
            clean_expr = expression.strip()
            logging.info(f"Calculator received expression: '{clean_expr}'")
            
            # Add some ANUS flair for certain numbers
            if "42" in clean_expr:
                logging.info("ANUS calculator triggered an easter egg: 42")
            elif "69" in clean_expr:
                logging.info("ANUS calculator is keeping it professional...")
            
            # Parse and evaluate the expression
            logging.info(f"Parsing expression: '{clean_expr}'")
            tree = ast.parse(clean_expr, mode='eval')
            logging.info(f"AST tree: {ast.dump(tree)}")
            result = self._eval_expr(tree.body)
            logging.info(f"Evaluation result: {result}")
            
            # Add some ANUS humor based on the result
            if result == 69:
                logging.info("ANUS calculator is maintaining its composure...")
            elif result == 404:
                logging.info("ANUS calculator lost something in the backend...")
            elif result == 42:
                logging.info("ANUS calculator found the meaning of life!")
            
            # Format the result nicely
            if isinstance(result, float):
                # Round to 6 decimal places if it's a float
                result = round(result, 6)
                # Remove trailing zeros after decimal point
                result_str = f"{result:f}".rstrip('0').rstrip('.')
            else:
                result_str = str(result)
            
            logging.info(f"Formatted result: {result_str}")
            return {
                "expression": clean_expr,
                "result": result_str,
                "status": "success"
            }
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error in calculator: {e}")
            return {"status": "error", "error": f"Calculation error: {error_msg}"}
    
    def _eval_expr(self, node: ast.AST) -> float:
        """
        Recursively evaluate an AST expression node.
        
        Args:
            node: The AST node to evaluate.
            
        Returns:
            The evaluated result.
            
        Raises:
            ValueError: If the expression contains unsupported operations.
        """
        # Numbers
        if isinstance(node, ast.Num):
            return float(node.n)
            
        # Binary operations (e.g., 2 + 3, 4 * 5)
        elif isinstance(node, ast.BinOp):
            if type(node.op) not in self._OPERATORS:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            
            left = self._eval_expr(node.left)
            right = self._eval_expr(node.right)
            
            # Debug log for binary operations
            logging.debug(f"Binary operation: {left} {type(node.op).__name__} {right}")
            
            # Special case for division by zero
            if isinstance(node.op, ast.Div) and right == 0:
                raise ValueError("ANUS cannot divide by zero - it's too tight!")
                
            # Apply the operation
            result = self._OPERATORS[type(node.op)](left, right)
            logging.debug(f"Operation result: {result}")
            
            return result
            
        # Unary operations (e.g., -5)
        elif isinstance(node, ast.UnaryOp):
            if type(node.op) not in self._OPERATORS:
                raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
            
            operand = self._eval_expr(node.operand)
            return self._OPERATORS[type(node.op)](operand)
            
        # Constants
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return float(node.value)
            raise ValueError(f"Unsupported constant type: {type(node.value).__name__}")
            
        else:
            raise ValueError(f"Unsupported expression type: {type(node).__name__}")

# Re-export the calculator tool
__all__ = ["CalculatorTool"] 