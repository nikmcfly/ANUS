"""
Tool Agent module that extends the react agent with tool execution capabilities.
"""

from typing import Dict, List, Any, Optional, Tuple
import importlib
import logging
import re

from anus.core.agent.react_agent import ReactAgent

class ToolAgent(ReactAgent):
    """
    An agent that can use tools to interact with its environment.
    
    Extends the ReactAgent with the ability to discover, load, and execute tools.
    """
    
    def __init__(
        self, 
        name: Optional[str] = None, 
        max_iterations: int = 10, 
        tools: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize a ToolAgent instance.
        
        Args:
            name: Optional name for the agent.
            max_iterations: Maximum number of thought-action cycles to perform.
            tools: Optional list of tool names to load.
            **kwargs: Additional configuration options for the agent.
        """
        super().__init__(name=name, max_iterations=max_iterations, **kwargs)
        self.tools: Dict[str, Any] = {}
        
        # Load specified tools or default tools
        if tools:
            for tool_name in tools:
                self.load_tool(tool_name)
    
    def load_tool(self, tool_name: str) -> bool:
        """
        Load a tool by name.
        
        Args:
            tool_name: The name of the tool to load.
            
        Returns:
            True if the tool was successfully loaded, False otherwise.
        """
        try:
            # Dynamically import the tool module
            module_path = f"anus.tools.{tool_name}"
            module = importlib.import_module(module_path)
            
            # Get the tool class (assumed to be the same name as the module but capitalized)
            class_name = "".join(word.capitalize() for word in tool_name.split("_")) + "Tool"
            tool_class = getattr(module, class_name)
            
            # Instantiate the tool
            tool_instance = tool_class()
            
            # Register the tool
            self.tools[tool_name] = tool_instance
            
            self.log_action("load_tool", {"tool_name": tool_name, "status": "success"})
            return True
            
        except (ImportError, AttributeError, Exception) as e:
            self.log_action("load_tool", {"tool_name": tool_name, "status": "error", "error": str(e)})
            logging.error(f"Failed to load tool {tool_name}: {e}")
            return False
    
    def _decide_action(self, context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Decide on the next action to take based on the task.
        
        Args:
            context: The current execution context.
            
        Returns:
            A tuple of (action_name, action_input).
        """
        task = context['task'].lower()
        
        # Check for calculator tasks
        calc_pattern = r'calculate\s+(.+)$'
        calc_match = re.search(calc_pattern, task, re.IGNORECASE)
        
        if calc_match and 'calculator' in self.tools:
            expression = calc_match.group(1).strip()
            logging.info(f"Matched calculator expression: '{expression}'")
            return "calculator", {"expression": expression}
            
        # Check for search tasks
        search_patterns = [
            r'search(?:\s+for)?\s+(.+)',
            r'find(?:\s+information(?:\s+about)?)?\s+(.+)',
            r'look\s+up\s+(.+)'
        ]
        
        for pattern in search_patterns:
            search_match = re.search(pattern, task, re.IGNORECASE)
            if search_match and 'search' in self.tools:
                query = search_match.group(1)
                return "search", {"query": query}
                
        # Check for text processing tasks
        text_patterns = {
            r'count\s+characters\s+in\s+[\'"](.+)[\'"]': ("count", lambda m: m.group(1)),
            r'count\s+words\s+in\s+[\'"](.+)[\'"]': ("wordcount", lambda m: m.group(1)),
            r'reverse\s+[\'"](.+)[\'"]': ("reverse", lambda m: m.group(1)),
            r'uppercase\s+[\'"](.+)[\'"]': ("uppercase", lambda m: m.group(1)),
            r'lowercase\s+[\'"](.+)[\'"]': ("lowercase", lambda m: m.group(1)),
            r'capitalize\s+[\'"](.+)[\'"]': ("capitalize", lambda m: m.group(1))
        }
        
        for pattern, (operation, extractor) in text_patterns.items():
            text_match = re.search(pattern, task, re.IGNORECASE)
            if text_match and 'text' in self.tools:
                text = extractor(text_match)
                return "text", {"text": text, "operation": operation}
                
        # Check for code execution tasks
        code_patterns = [
            r'run\s+code\s+```(?:python)?\s*(.+?)```',
            r'execute\s+```(?:python)?\s*(.+?)```',
            r'evaluate\s+```(?:python)?\s*(.+?)```'
        ]
        
        for pattern in code_patterns:
            code_match = re.search(pattern, task, re.IGNORECASE | re.DOTALL)
            if code_match and 'code' in self.tools:
                code = code_match.group(1).strip()
                return "code", {"code": code}
                
        # Default to dummy action for other tasks
        return "dummy_action", {"query": f"Placeholder action for {task}"}
    
    def _execute_action(self, action_name: str, action_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action using the appropriate tool.
        
        Args:
            action_name: The name of the action/tool to execute.
            action_input: The input parameters for the action.
            
        Returns:
            The observation from executing the action.
        """
        # Check if the action corresponds to a loaded tool
        if action_name in self.tools:
            try:
                tool = self.tools[action_name]
                result = tool.execute(**action_input)
                
                # Log the result (with some fun ANUS flair)
                logging.info(f"Tool {action_name} successfully executed.")
                
                # If result is already a dict with status, return it directly
                if isinstance(result, dict) and "status" in result:
                    return result
                    
                # Otherwise, wrap it in a success response
                return {"status": "success", "result": result}
                
            except Exception as e:
                error_message = f"Error executing tool {action_name}: {str(e)}"
                logging.error(error_message)
                return {"status": "error", "error": error_message}
        else:
            # Try to load the tool if it's not already loaded
            if self.load_tool(action_name):
                # Retry execution with the newly loaded tool
                return self._execute_action(action_name, action_input)
            
            return {"status": "error", "error": f"Unknown action or tool: {action_name}"}
    
    def list_available_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools.
        
        Returns:
            A list of tool information dictionaries.
        """
        tool_info = []
        for name, tool in self.tools.items():
            info = {
                "name": name,
                "description": getattr(tool, "description", "No description available"),
                "parameters": getattr(tool, "parameters", {})
            }
            tool_info.append(info)
        return tool_info 