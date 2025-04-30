"""
规划器层 - 负责任务规划、分解和执行策略
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field

class PlannerInput(BaseModel):
    """规划器输入的标准格式"""
    objective: str = Field(..., description="目标或任务描述")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")
    constraints: Optional[List[str]] = Field(None, description="约束条件")
    available_tools: Optional[List[Dict[str, Any]]] = Field(None, description="可用工具列表")

class PlanStep(BaseModel):
    """计划步骤"""
    id: str = Field(..., description="步骤ID")
    name: str = Field(..., description="步骤名称")
    description: str = Field(..., description="步骤描述")
    tool: Optional[str] = Field(None, description="使用的工具")
    tool_input: Optional[Dict[str, Any]] = Field(None, description="工具输入")
    dependencies: Optional[List[str]] = Field(None, description="依赖的步骤ID列表")

class PlannerOutput(BaseModel):
    """规划器输出的标准格式"""
    plan: List[PlanStep] = Field(..., description="执行计划步骤列表")
    reasoning: Optional[str] = Field(None, description="推理过程")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据信息")

from .base_planner import BasePlanner
from .llm_planner import LLMPlanner

__all__ = ["PlannerInput", "PlanStep", "PlannerOutput", "BasePlanner", "LLMPlanner"] 