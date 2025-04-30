"""
工具注册表 - 管理系统中的工具
"""

from typing import Dict, Any, Optional, List, Type

from . import BaseTool, ToolDefinition


class ToolRegistry:
    """
    工具注册表，用于管理系统中的工具
    """
    
    def __init__(self):
        """
        初始化工具注册表
        """
        self.tools: Dict[str, BaseTool] = {}
    
    def register_tool(self, tool: BaseTool) -> None:
        """
        注册工具
        
        Args:
            tool: 要注册的工具实例
        """
        self.tools[tool.name] = tool
    
    def register_tools(self, tools: List[BaseTool]) -> None:
        """
        批量注册工具
        
        Args:
            tools: 要注册的工具实例列表
        """
        for tool in tools:
            self.register_tool(tool)
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        获取工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            Optional[BaseTool]: 工具实例，如果不存在则返回None
        """
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """
        列出所有工具名称
        
        Returns:
            List[str]: 工具名称列表
        """
        return list(self.tools.keys())
    
    def get_all_tools(self) -> Dict[str, BaseTool]:
        """
        获取所有工具
        
        Returns:
            Dict[str, BaseTool]: 工具字典
        """
        return self.tools
    
    def get_tool_definitions(self) -> List[ToolDefinition]:
        """
        获取所有工具定义
        
        Returns:
            List[ToolDefinition]: 工具定义列表
        """
        return [tool.get_definition() for tool in self.tools.values()]
    
    def get_schemas_for_llm(self) -> List[Dict[str, Any]]:
        """
        获取用于LLM工具调用的所有工具Schema
        
        Returns:
            List[Dict[str, Any]]: LLM工具调用的Schema列表
        """
        return [tool.get_schema_for_llm() for tool in self.tools.values()] 