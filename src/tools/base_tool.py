"""
基础工具抽象类 - 定义工具的接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable

from . import ToolInput, ToolOutput, ToolDefinition


class BaseTool(ABC):
    """
    工具的抽象基类，定义了工具需要实现的接口
    """
    
    def __init__(self, name: str, description: str, parameters_schema: Dict[str, Any]):
        """
        初始化工具
        
        Args:
            name: 工具名称
            description: 工具描述
            parameters_schema: 工具参数的JSON Schema
        """
        self.name = name
        self.description = description
        self.parameters_schema = parameters_schema
    
    @abstractmethod
    async def execute(self, input_data: ToolInput) -> ToolOutput:
        """
        异步执行工具
        
        Args:
            input_data: 工具输入数据
            
        Returns:
            ToolOutput: 工具输出数据
        """
        pass
    
    @abstractmethod
    def execute_sync(self, input_data: ToolInput) -> ToolOutput:
        """
        同步执行工具
        
        Args:
            input_data: 工具输入数据
            
        Returns:
            ToolOutput: 工具输出数据
        """
        pass
    
    def get_definition(self) -> ToolDefinition:
        """
        获取工具定义
        
        Returns:
            ToolDefinition: 工具定义
        """
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters_schema=self.parameters_schema,
            handler=self.execute
        )
    
    def get_schema_for_llm(self) -> Dict[str, Any]:
        """
        获取用于LLM工具调用的Schema
        
        Returns:
            Dict[str, Any]: LLM工具调用的Schema
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema
            }
        } 