"""
工具集 - 提供各种工具供系统使用
"""

from typing import Dict, Any, Optional, List, Callable, Union
from pydantic import BaseModel, Field

class ToolInput(BaseModel):
    """工具输入的标准格式"""
    parameters: Dict[str, Any] = Field(..., description="工具参数")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")

class ToolOutput(BaseModel):
    """工具输出的标准格式"""
    result: Any = Field(..., description="工具执行结果")
    error: Optional[str] = Field(None, description="错误信息，若执行成功则为None")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据信息")

class ToolDefinition(BaseModel):
    """工具定义"""
    name: str = Field(..., description="工具名称")
    description: str = Field(..., description="工具描述")
    parameters_schema: Dict[str, Any] = Field(..., description="工具参数的JSON Schema")
    handler: Optional[Callable] = Field(None, description="工具处理函数")

from .base_tool import BaseTool
from .tool_registry import ToolRegistry

__all__ = ["ToolInput", "ToolOutput", "ToolDefinition", "BaseTool", "ToolRegistry"] 