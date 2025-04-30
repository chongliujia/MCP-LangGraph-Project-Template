"""
模型层 - 负责与LLM交互，处理自然语言理解和生成
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field

class ModelInput(BaseModel):
    """模型输入的标准格式"""
    messages: List[Dict[str, str]] = Field(..., description="对话消息列表")
    system_prompt: Optional[str] = Field(None, description="系统提示")
    tools: Optional[List[Dict[str, Any]]] = Field(None, description="可用工具列表")
    model: Optional[str] = Field(None, description="使用的模型名称")
    temperature: Optional[float] = Field(None, description="温度参数")
    max_tokens: Optional[int] = Field(None, description="最大生成token数")
    additional_params: Optional[Dict[str, Any]] = Field(None, description="其他参数")

class ModelOutput(BaseModel):
    """模型输出的标准格式"""
    content: Optional[str] = Field(None, description="生成的文本内容")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="工具调用结果")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据信息")

from .base_model import BaseModelLayer
from .openai_model import OpenAIModel
from .deepseek_model import DeepSeekModel
from .model_factory import ModelFactory

__all__ = ["ModelInput", "ModelOutput", "BaseModelLayer", "OpenAIModel", "DeepSeekModel", "ModelFactory"] 