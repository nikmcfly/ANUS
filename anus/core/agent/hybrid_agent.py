"""
Hybrid Agent module that combines single and multi-agent capabilities.

This agent can dynamically switch between single and multi-agent modes based on task complexity.
"""

import logging
import re
from typing import Dict, Any, List, Tuple, Optional

from anus.core.agent.tool_agent import ToolAgent

class HybridAgent(ToolAgent):
    """
    A hybrid agent that can switch between single and multi-agent modes.
    
    This agent assesses task complexity and chooses the appropriate mode.
    """
    
    def __init__(
        self,
        name: Optional[str] = None,
        max_iterations: int = 10,
        tools: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize a HybridAgent instance.
        
        Args:
            name: Optional name for the agent.
            max_iterations: Maximum number of thought-action cycles to perform.
            tools: Optional list of tool names to load.
            **kwargs: Additional configuration options for the agent.
        """
        super().__init__(name=name, max_iterations=max_iterations, tools=tools, **kwargs)
        self.mode = "auto"
        
        # Specialized agents for multi-agent mode
        self.specialized_agents = {
            "researcher": ToolAgent(name="researcher", tools=tools),
            "planner": ToolAgent(name="planner", tools=tools),
            "executor": ToolAgent(name="executor", tools=tools),
            "critic": ToolAgent(name="critic", tools=tools)
        }

    def add_specialized_agent(self, role: str, config: Dict[str, Any]) -> bool:
        """
        Add a specialized agent for a specific role.
        
        Args:
            role: The role of the specialized agent.
            config: Configuration for the specialized agent.
            
        Returns:
            True if the agent was successfully added, False otherwise.
        """
        try:
            # Create a new ToolAgent with the given configuration
            agent_name = config.get("name", f"{role}-agent")
            agent = ToolAgent(
                name=agent_name,
                max_iterations=config.get("max_iterations", self.max_iterations),
                tools=config.get("tools", []),
                **config.get("kwargs", {})
            )

            # Register the specialized agent
            self.specialized_agents[role] = agent

            self.log_action("add_specialized_agent", {"role": role, "agent_name": agent_name})

            # Add easter egg log message based on role
            if role == "researcher":
                logging.debug(f"Added a researcher agent to probe deep into any subject matter")
            elif role == "coder":
                logging.debug(f"Added a coder agent to handle the backend implementation")
            elif role == "planner":
                logging.debug(f"Added a planner agent to ensure smooth passage through complex tasks")
            elif role == "critic":
                logging.debug(f"Added a critic agent to ensure everything comes out right in the end")
            else:
                logging.debug(f"Added a {role} agent to the ANUS collective")

            return True

        except Exception as e:
            error_message = f"Error adding specialized agent for role {role}: {str(e)}"
            logging.error(error_message)
            self.log_action("add_specialized_agent", {"role": role, "status": "error", "error": error_message})
            return False
    
    def _assess_complexity(self, task: str) -> float:
        """
        Assess the complexity of a task.
        
        Args:
            task: The task description.
            
        Returns:
            A complexity score between 0 and 10.
        """
        complexity = 0.0
        
        # Check for multiple operations
        operations = [
            (r'(calculate|compute|evaluate)', 1.0),  # Basic calculations
            (r'(search|find|look up)', 1.0),  # Search operations
            (r'(count|process|analyze|transform)\s+text', 1.0),  # Text operations
            (r'run\s+code|execute', 1.5),  # Code execution
            (r'compare|contrast|evaluate', 2.0),  # Analysis operations
            (r'optimize|improve|enhance', 2.5),  # Optimization tasks
            (r'and|then|after|before', 1.0),  # Task chaining
            (r'if|when|unless|otherwise', 1.5),  # Conditional operations
            (r'all|every|each', 1.0),  # Comprehensive operations
            (r'most|best|optimal', 1.5)  # Decision making
        ]


        
        # Add complexity for each operation found
        for pattern, score in operations:
            matches = re.findall(pattern, task.lower())
            complexity += score * len(matches)
        
        # Add complexity for length of task description
        words = task.split()
        complexity += len(words) * 0.1  # 0.1 points per word
        
        # Add complexity for special characters (potential complex expressions)
        special_chars = sum(1 for c in task if not c.isalnum() and not c.isspace())
        complexity += special_chars * 0.2
        
        # Add complexity for multiple tools needed
        tool_keywords = {
            'calculator': ['calculate', 'compute', 'evaluate', 'math'],
            'search': ['search', 'find', 'look up', 'query'],
            'text': ['text', 'string', 'characters', 'words'],
            'code': ['code', 'execute', 'run', 'python']
        }
        
        tools_needed = 0
        task_lower = task.lower()
        for tool_name, keywords in tool_keywords.items():
            if any(kw in task_lower for kw in keywords):
                tools_needed += 1
            
        complexity += tools_needed * 1.5
        
        # Cap the complexity at 10
        return min(10.0, complexity)
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a task using the appropriate mode based on complexity.
        
        Args:
            task: The task description to execute.
            **kwargs: Additional parameters for task execution.
            
        Returns:
            A dictionary containing the execution result and metadata.
        """
        complexity = self._assess_complexity(task)
        
        # Decide on mode based on complexity
        if complexity < 3.0:
            logging.info(f"Task complexity ({complexity:.1f}) below threshold (3.0). ANUS staying tight in single-agent mode.")
            logging.info("This task is so simple even a constipated ANUS could handle it.")
            return super().execute(task, **kwargs)
        else:
            logging.info(f"Task complexity ({complexity:.1f}) above threshold (3.0). ANUS expanding to multi-agent mode.")
            logging.info("ANUS is expanding to accommodate multiple agents for this complex task.")
            return self._execute_multi_agent(task, **kwargs)
    
    def _execute_multi_agent(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a task using multiple specialized agents.
        
        Args:
            task: The task description to execute.
            **kwargs: Additional parameters for task execution.
            
        Returns:
            A dictionary containing the aggregated results.
        """
        logging.info("ANUS expanding to accommodate multiple agents")
        logging.info("Task decomposed into subtasks for optimal ANUS performance")
        
        # For simple calculator tasks, use direct execution
        if task.lower().startswith("calculate"):
            # Use the ToolAgent's _decide_action method to determine the action
            action_name, action_input = self._decide_action({"task": task})
            
            # If it's a calculator action, execute it directly
            if action_name == "calculator" and "expression" in action_input:
                result = self._execute_action(action_name, action_input)
                if result.get("status") == "success" and "result" in result:
                    return {
                        "task": task,
                        "answer": f"The result of {action_input['expression']} is {result['result']}",
                        "direct_result": result,
                        "mode": "direct"
                    }
        
        # For complex tasks, use multi-agent approach
        results = {}
        final_result = None
        
        # Researcher analyzes the task and gathers information
        researcher_result = self.specialized_agents["researcher"].execute(
            f"Analyze and gather information for: {task}"
        )
        results["researcher"] = researcher_result
        
        # Planner creates a strategy based on research
        planner_result = self.specialized_agents["planner"].execute(
            f"Plan execution strategy for: {task}\nBased on research: {researcher_result}"
        )
        results["planner"] = planner_result
        
        # Executor carries out the plan
        executor_result = self.specialized_agents["executor"].execute(
            f"Execute plan for: {task}\nFollowing strategy: {planner_result}"
        )
        results["executor"] = executor_result
        final_result = executor_result  # Use executor's result as the primary result
        
        # Critic evaluates the results
        critic_result = self.specialized_agents["critic"].execute(
            f"Evaluate results for: {task}\nAnalyzing output: {executor_result}"
        )
        results["critic"] = critic_result
        
        logging.info("All agents have finished their tasks. ANUS is aggregating results...")
        logging.info("ANUS has successfully completed multi-agent processing")
        
        return {
            "task": task,
            "answer": final_result.get("answer", str(final_result)),
            "agent_results": results,
            "mode": "multi"
        } 
