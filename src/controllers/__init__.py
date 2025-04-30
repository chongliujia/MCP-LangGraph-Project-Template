"""
控制器层 - 控制系统流程，协调各组件间的交互
"""

from typing import Dict, Any, Optional, List, Union, Callable
from pydantic import BaseModel, Field

class ControllerInput(BaseModel):
    """控制器输入的标准格式"""
    state: Dict[str, Any] = Field(..., description="当前状态")
    event: Dict[str, Any] = Field(..., description="触发事件")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")

class ControllerOutput(BaseModel):
    """控制器输出的标准格式"""
    next_state: Dict[str, Any] = Field(..., description="更新后的状态")
    result: Optional[Any] = Field(None, description="操作结果")
    next_action: Optional[str] = Field(None, description="下一步动作")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据信息")

from .base_controller import BaseController
from .workflow_controller import WorkflowController

__all__ = ["ControllerInput", "ControllerOutput", "BaseController", "WorkflowController"] 