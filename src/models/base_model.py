"""
基础模型层抽象类 - 定义模型层的接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from .import ModelInput, ModelOutput


class BaseModelLayer(ABC):
    """
    模型层的抽象基类，定义了模型层需要实现的接口
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化模型层
        
        Args:
            config: 模型配置参数
        """
        self.config = config or {}
    
    @abstractmethod
    async def generate(self, input_data: ModelInput) -> ModelOutput:
        """
        异步生成响应
        
        Args:
            input_data: 模型输入数据
            
        Returns:
            ModelOutput: 模型输出数据
        """
        pass
    
    @abstractmethod
    def generate_sync(self, input_data: ModelInput) -> ModelOutput:
        """
        同步生成响应
        
        Args:
            input_data: 模型输入数据
            
        Returns:
            ModelOutput: 模型输出数据
        """
        pass
    
    def prepare_messages(self, input_data: ModelInput) -> List[Dict[str, Any]]:
        """
        准备发送给模型的消息格式
        
        Args:
            input_data: 模型输入数据
            
        Returns:
            List[Dict[str, Any]]: 准备好的消息列表
        """
        messages = []
        
        # 添加系统提示
        if input_data.system_prompt:
            messages.append({"role": "system", "content": input_data.system_prompt})
        
        # 添加对话历史
        messages.extend(input_data.messages)
        
        return messages 