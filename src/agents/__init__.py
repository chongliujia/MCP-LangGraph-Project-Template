"""
Agent系统 - 将模型、控制器和规划器组合成完整的Agent
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field

class AgentInput(BaseModel):
    """Agent输入的标准格式"""
    query: str = Field(..., description="用户查询或任务描述")
    history: Optional[List[Dict[str, str]]] = Field(None, description="对话历史")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")

class AgentOutput(BaseModel):
    """Agent输出的标准格式"""
    response: str = Field(..., description="响应文本")
    actions: Optional[List[Dict[str, Any]]] = Field(None, description="执行的动作列表")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据信息")

from .base_agent import BaseAgent
from .mcp_agent import MCPAgent

__all__ = ["AgentInput", "AgentOutput", "BaseAgent", "MCPAgent"] 