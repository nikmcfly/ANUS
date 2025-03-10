"""
Text tool for basic text processing and manipulation.

This tool provides various text manipulation functions, such as counting words,
formatting text, and basic analysis.
"""

import logging
import re
from typing import Dict, Any, Union, List

from anus.tools.base.tool import BaseTool
from anus.tools.base.tool_result import ToolResult

class TextTool(BaseTool):
    """
    A tool for processing and manipulating text.
    
    ANUS can handle your text in all sorts of interesting ways.
    """
    
    name = "text"
    description = "Process and manipulate text"
    parameters = {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "The text to process"
            },
            "operation": {
                "type": "string",
                "description": "The operation to perform (count, reverse, uppercase, lowercase, capitalize, wordcount)",
                "enum": ["count", "reverse", "uppercase", "lowercase", "capitalize", "wordcount"]
            }
        },
        "required": ["text", "operation"]
    }
    
    # Operation descriptions with ANUS flair
    _operation_descriptions = {
        "count": "ANUS is counting characters...",
        "reverse": "ANUS is turning your text backward...",
        "uppercase": "ANUS is making everything BIGGER...",
        "lowercase": "ANUS is making everything smaller...",
        "capitalize": "ANUS is making your text look Important...",
        "wordcount": "ANUS is counting your words one by one..."
    }
    
    def execute(self, text: str, operation: str, **kwargs) -> Union[Dict[str, Any], ToolResult]:
        """
        Execute the text tool.
        
        Args:
            text: The text to process.
            operation: The operation to perform.
            **kwargs: Additional parameters (ignored).
            
        Returns:
            The processed text result.
        """
        try:
            # Log the operation with ANUS flair
            logging.info(self._operation_descriptions.get(operation, f"ANUS is processing your text with {operation}..."))
            
            # Perform the requested operation
            result = None
            if operation == "count":
                result = len(text)
            elif operation == "reverse":
                result = text[::-1]
            elif operation == "uppercase":
                result = text.upper()
            elif operation == "lowercase":
                result = text.lower()
            elif operation == "capitalize":
                result = text.title()
            elif operation == "wordcount":
                result = len(text.split())
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            # Add a fun fact for certain operations
            fun_fact = None
            if operation == "wordcount" and result > 100:
                fun_fact = "That's a lot of words! ANUS is impressed by your verbosity."
            elif operation == "uppercase":
                fun_fact = "ALL CAPS? ANUS FEELS LIKE YOU'RE SHOUTING!"
            elif operation == "count" and result > 500:
                fun_fact = "That's a substantial chunk of text. ANUS had to really stretch to process all of it!"
            
            # Return the result
            result_dict = {
                "text": text[:50] + "..." if len(text) > 50 else text,  # Truncate long inputs
                "operation": operation,
                "result": result
            }
            
            if fun_fact:
                result_dict["fun_fact"] = fun_fact
            
            return result_dict
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error in text tool: {e}")
            return {"status": "error", "error": f"Text processing error: {error_msg}"} 