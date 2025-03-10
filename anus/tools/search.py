"""
Search tool for basic web search simulation.

This tool simulates searching the web for information.
"""

import logging
import random
from typing import Dict, Any, Union, List

from anus.tools.base.tool import BaseTool
from anus.tools.base.tool_result import ToolResult

class SearchTool(BaseTool):
    """
    A tool for simulating web searches.
    
    ANUS can search the web for information, though the results might be a bit cheeky.
    """
    
    name = "search"
    description = "Search the web for information"
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query"
            }
        },
        "required": ["query"]
    }
    
    # Mock search results for common queries
    _mock_results = {
        "anus": [
            "Anatomical term for the opening at the end of the digestive tract",
            "ANUS: Autonomous Networked Utility System - An open-source AI framework",
            "10 Facts About the ANUS Framework You Won't Believe!",
            "Why ANUS is the Most Uncomfortably Named Software Project"
        ],
        "python": [
            "Python - High-level programming language",
            "Python (programming language) - Wikipedia",
            "Python.org - Official Python documentation and downloads",
            "Learning Python: The Definitive Guide"
        ],
        "ai": [
            "Artificial Intelligence - Overview, applications, and recent advances",
            "The Future of AI: Challenges and Opportunities",
            "OpenAI - Leading AI research laboratory",
            "How AI is Transforming Industries in 2025"
        ],
        "calculator": [
            "Online Calculator - Free and Easy to Use",
            "Scientific Calculator with Advanced Functions",
            "History of the Calculator: From Abacus to Digital",
            "Best Calculator Apps for Professionals"
        ]
    }
    
    # Funny search messages
    _search_messages = [
        "ANUS is probing the depths of the internet...",
        "ANUS is digging deep for results...",
        "ANUS is spreading wide to find all relevant information...",
        "ANUS is penetrating the web for answers...",
        "ANUS is squeezing out search results..."
    ]
    
    def execute(self, query: str, **kwargs) -> Union[Dict[str, Any], ToolResult]:
        """
        Execute the search tool.
        
        Args:
            query: The search query.
            **kwargs: Additional parameters (ignored).
            
        Returns:
            The search results.
        """
        try:
            # Log a funny search message
            if random.random() < 0.4:  # 40% chance
                logging.info(random.choice(self._search_messages))
            
            # Clean and lowercase the query for matching
            clean_query = query.lower().strip()
            
            # Check for exact matches in our mock database
            results = []
            exact_match = False
            
            for key, mock_results in self._mock_results.items():
                if key in clean_query:
                    results.extend(mock_results)
                    if key == clean_query:
                        exact_match = True
            
            # If no direct matches, generate a generic response
            if not results:
                results = [
                    f"Result 1 for '{query}'",
                    f"Article about {query} - Wikipedia",
                    f"The Complete Guide to {query}",
                    f"Latest News on {query}"
                ]
            
            # Add a cheeky comment for certain searches
            comment = None
            if "anus" in clean_query.lower() and not exact_match:
                comment = "I see you're interested in ANUS... the framework, right?"
            elif any(term in clean_query for term in ["joke", "humor", "funny"]):
                comment = "Looking for humor? ANUS itself is often the butt of jokes."
            
            # Return as ToolResult
            result_dict = {
                "query": query,
                "results": results,
                "result_count": len(results)
            }
            
            if comment:
                result_dict["comment"] = comment
                logging.info(f"ANUS search added a cheeky comment: {comment}")
            
            return {
                "query": query,
                "results": results,
                "result_count": len(results),
                "comment": comment
            }
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error in search tool: {e}")
            return {"status": "error", "error": f"Search error: {error_msg}"} 