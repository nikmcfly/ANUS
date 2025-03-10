"""
React Agent module that extends the base agent with reasoning capabilities.
"""

from typing import Dict, List, Any, Optional, Tuple
import json
import logging

from anus.core.agent.base_agent import BaseAgent

class ReactAgent(BaseAgent):
    """
    A reasoning agent that follows the React paradigm (Reasoning and Acting).
    
    This agent implements a thought-action-observation loop for complex reasoning.
    """
    
    def __init__(self, name: Optional[str] = None, max_iterations: int = 10, **kwargs):
        """
        Initialize a ReactAgent instance.
        
        Args:
            name: Optional name for the agent.
            max_iterations: Maximum number of thought-action cycles to perform.
            **kwargs: Additional configuration options for the agent.
        """
        super().__init__(name=name, **kwargs)
        self.max_iterations = max_iterations
        self.current_iteration = 0
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a task using the React paradigm.
        
        Args:
            task: The task description to execute.
            **kwargs: Additional parameters for task execution.
            
        Returns:
            A dictionary containing the execution result and metadata.
        """
        self.update_state(status="executing", task=task)
        self.current_iteration = 0
        
        # Initialize the context with the task
        context = {
            "task": task,
            "thoughts": [],
            "actions": [],
            "observations": []
        }
        
        # Main React loop
        while self.current_iteration < self.max_iterations:
            # Generate thought
            thought = self._generate_thought(context)
            context["thoughts"].append(thought)
            
            # Decide on action
            action_name, action_input = self._decide_action(context)
            action = {"name": action_name, "input": action_input}
            context["actions"].append(action)
            
            # Execute action and get observation
            observation = self._execute_action(action_name, action_input)
            context["observations"].append(observation)
            
            # Log the iteration
            self.log_action("iteration", {
                "iteration": self.current_iteration,
                "thought": thought,
                "action": action,
                "observation": observation
            })
            
            # Check if we should terminate
            if self._should_terminate(context):
                break
                
            self.current_iteration += 1
        
        # Generate final answer
        final_answer = self._generate_final_answer(context)
        
        result = {
            "task": task,
            "answer": final_answer,
            "iterations": self.current_iteration,
            "context": context
        }
        
        self.update_state(status="completed")
        return result
    
    def _generate_thought(self, context: Dict[str, Any]) -> str:
        """
        Generate a thought based on the current context.
        
        Args:
            context: The current execution context.
            
        Returns:
            The thought string.
        """
        # This should be implemented using a language model
        # Currently using a placeholder
        return f"Thinking about how to {context['task']} (iteration {self.current_iteration})"
    
    def _decide_action(self, context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Decide on the next action to take.
        
        Args:
            context: The current execution context.
            
        Returns:
            A tuple of (action_name, action_input).
        """
        # This should be implemented using a language model
        # Currently using a placeholder
        return "dummy_action", {"query": f"Placeholder action for {context['task']}"}
    
    def _execute_action(self, action_name: str, action_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action and return the observation.
        
        Args:
            action_name: The name of the action to execute.
            action_input: The input parameters for the action.
            
        Returns:
            The observation from executing the action.
        """
        # This should be overridden by subclasses
        return {"status": "error", "error": f"Unknown action or tool: {action_name}"}
    
    def _should_terminate(self, context: Dict[str, Any]) -> bool:
        """
        Check if execution should terminate.
        
        Args:
            context: The current execution context.
            
        Returns:
            True if execution should terminate, False otherwise.
        """
        # This should check if we've found a satisfactory answer
        # Currently using a placeholder
        return self.current_iteration >= self.max_iterations - 1
    
    def _generate_final_answer(self, context: Dict[str, Any]) -> str:
        """
        Generate a final answer based on the context.
        
        Args:
            context: The current execution context.
            
        Returns:
            The final answer string.
        """
        # Check if we have any successful tool executions
        for observation in context.get("observations", []):
            if isinstance(observation, dict) and "result" in observation:
                result = observation["result"]
                
                # Handle calculator tool
                if isinstance(result, dict):
                    # Calculator tool
                    if "expression" in result and "result" in result and result.get("status") == "success":
                        expression = result["expression"]
                        calc_result = result["result"]
                        return f"The result of {expression} is {calc_result}"
                    elif result.get("status") == "error" and "error" in result:
                        return f"Calculator error: {result['error']}"
                    
                    # Search tool
                    if "query" in result and "results" in result:
                        query = result["query"]
                        results = result["results"]
                        result_count = result.get("result_count", len(results))
                        
                        # Format the results
                        formatted_results = "\n".join([f"- {r}" for r in results[:5]])
                        comment = result.get("comment", "")
                        comment_text = f"\n\n{comment}" if comment else ""
                        
                        return f"I searched for '{query}' and found {result_count} results:\n\n{formatted_results}{comment_text}"
                    
                    # Text tool
                    if "text" in result and "operation" in result and "result" in result:
                        text = result["text"]
                        operation = result["operation"]
                        text_result = result["result"]
                        fun_fact = result.get("fun_fact", "")
                        
                        operation_description = {
                            "count": "characters in",
                            "reverse": "reversed",
                            "uppercase": "in uppercase",
                            "lowercase": "in lowercase",
                            "capitalize": "capitalized",
                            "wordcount": "words in"
                        }.get(operation, operation)
                        
                        fun_fact_text = f"\n\n{fun_fact}" if fun_fact else ""
                        
                        if operation in ["count", "wordcount"]:
                            return f"I counted {text_result} {operation_description} '{text}'{fun_fact_text}"
                        else:
                            return f"I processed '{text}' with {operation} operation:\n\n{text_result}{fun_fact_text}"
                    
                    # Code tool
                    if "code" in result and ("result" in result or "output" in result):
                        code = result["code"]
                        code_result = result.get("result", "No direct result")
                        output = result.get("output", "")
                        execution_type = result.get("execution_type", "code")
                        
                        if output:
                            return f"I executed your Python code:\n\n```python\n{code}\n```\n\nOutput:\n```\n{output}\n```"
                        else:
                            return f"I executed your Python code:\n\n```python\n{code}\n```\n\nResult: {code_result}"
                
                    # Multi-agent results
                    if "agent_results" in result:
                        agent_results = result["agent_results"]
                        final_answer = []
                        
                        # Process each agent's contribution
                        if "researcher" in agent_results:
                            research = agent_results["researcher"].get("answer", "")
                            if research:
                                final_answer.append(f"Research findings:\n{research}")
                        
                        if "planner" in agent_results:
                            plan = agent_results["planner"].get("answer", "")
                            if plan:
                                final_answer.append(f"Execution plan:\n{plan}")
                        
                        if "executor" in agent_results:
                            execution = agent_results["executor"].get("answer", "")
                            if execution:
                                final_answer.append(f"Execution results:\n{execution}")
                        
                        if "critic" in agent_results:
                            critique = agent_results["critic"].get("answer", "")
                            if critique:
                                final_answer.append(f"Analysis and recommendations:\n{critique}")
                        
                        # Combine all parts with proper formatting
                        if final_answer:
                            return "\n\n".join(final_answer)
                            
        # If no successful results found after analyzing the task
        return "I was unable to process your request successfully. Please try again." 