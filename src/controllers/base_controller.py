"""
基础控制器抽象类 - 定义控制器的接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable

from . import ControllerInput, ControllerOutput


class BaseController(ABC):
    """
    控制器的抽象基类，定义了控制器需要实现的接口
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化控制器
        
        Args:
            config: 控制器配置参数
        """
        self.config = config or {}
        self.handlers = {}
    
    @abstractmethod
    async def process(self, input_data: ControllerInput) -> ControllerOutput:
        """
        异步处理输入并产生输出
        
        Args:
            input_data: 控制器输入数据
            
        Returns:
            ControllerOutput: 控制器输出数据
        """
        pass
    
    @abstractmethod
    def process_sync(self, input_data: ControllerInput) -> ControllerOutput:
        """
        同步处理输入并产生输出
        
        Args:
            input_data: 控制器输入数据
            
        Returns:
            ControllerOutput: 控制器输出数据
        """
        pass
    
    def register_handler(self, event_type: str, handler: Callable):
        """
        注册事件处理器
        
        Args:
            event_type: 事件类型
            handler: 处理函数
        """
        self.handlers[event_type] = handler
    
    def get_handler(self, event_type: str) -> Optional[Callable]:
        """
        获取事件处理器
        
        Args:
            event_type: 事件类型
            
        Returns:
            Optional[Callable]: 处理函数，如果不存在则返回None
        """
        return self.handlers.get(event_type) 