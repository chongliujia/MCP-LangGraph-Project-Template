"""
MCP LangGraph Framework - A universal MCP framework built on LangChain and LangGraph.

This framework provides:
- LangGraph-based workflow orchestration
- MCP protocol integration
- Modular tool system
- Multi-model support via LangChain
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .core.framework import MCPLangGraphFramework
from .core.mcp_server import MCPServer
from .tools.base import MCPTool
from .langchain.graph_builder import GraphBuilder

__all__ = [
    "MCPLangGraphFramework",
    "MCPServer",
    "MCPTool",
    "GraphBuilder",
] 