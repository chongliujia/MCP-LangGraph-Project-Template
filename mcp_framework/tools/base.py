"""
Base class for MCP tools compatible with LangChain.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
from langchain_core.tools import BaseTool as LangChainBaseTool
try:
    from pydantic.v1 import BaseModel, Field
except ImportError:
    from pydantic import BaseModel, Field


class MCPTool(LangChainBaseTool):
    """Base class for MCP tools that are compatible with LangChain."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.name:
            raise ValueError("Tool name must be defined")
        if not self.description:
            raise ValueError("Tool description must be defined")
    
    @abstractmethod
    def _run(self, **kwargs) -> Any:
        """Execute the tool synchronously."""
        pass
    
    async def _arun(self, **kwargs) -> Any:
        """Execute the tool asynchronously."""
        # Default implementation calls sync version
        return self._run(**kwargs)


# Example tools
class CalculatorTool(MCPTool):
    """Simple calculator tool."""
    
    name: str = "calculator"
    description: str = "Perform basic mathematical calculations. Input should be a mathematical expression."
    
    def _run(self, expression: str) -> str:
        """Calculate the result of a mathematical expression."""
        try:
            # Safe evaluation of mathematical expressions
            import ast
            import operator
            
            # Supported operations
            ops = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.USub: operator.neg,
            }
            
            def eval_expr(node):
                if isinstance(node, ast.Num):
                    return node.n
                elif isinstance(node, ast.BinOp):
                    return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
                elif isinstance(node, ast.UnaryOp):
                    return ops[type(node.op)](eval_expr(node.operand))
                else:
                    raise TypeError(node)
            
            result = eval_expr(ast.parse(expression, mode='eval').body)
            return f"The result is: {result}"
            
        except Exception as e:
            return f"Error calculating expression: {str(e)}"


class SearchTool(MCPTool):
    """Simple search tool."""
    
    name: str = "search"
    description: str = "Search for information. Input should be a search query."
    
    def _run(self, query: str) -> str:
        """Search for information (placeholder implementation)."""
        # This is a placeholder - in a real implementation, you might use
        # a search API like Google, Bing, or a custom search engine
        return f"Search results for '{query}': This is a placeholder search result. In a real implementation, this would return actual search results."


class WeatherTool(MCPTool):
    """Weather information tool."""
    
    name: str = "weather"
    description: str = "Get weather information for a location. Input should be a city name."
    
    def _run(self, location: str) -> str:
        """Get weather information (placeholder implementation)."""
        # This is a placeholder - in a real implementation, you might use
        # a weather API like OpenWeatherMap
        return f"Weather in {location}: This is a placeholder weather result. In a real implementation, this would return actual weather data." 