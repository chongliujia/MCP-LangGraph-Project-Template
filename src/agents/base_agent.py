"""
基础Agent抽象类 - 定义Agent的接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from . import AgentInput, AgentOutput


class BaseAgent(ABC):
    """
    Agent的抽象基类，定义了Agent需要实现的接口
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化Agent
        
        Args:
            config: Agent配置参数
        """
        self.config = config or {}
    
    @abstractmethod
    async def run(self, input_data: AgentInput) -> AgentOutput:
        """
        异步运行Agent
        
        Args:
            input_data: Agent输入数据
            
        Returns:
            AgentOutput: Agent输出数据
        """
        pass
    
    @abstractmethod
    def run_sync(self, input_data: AgentInput) -> AgentOutput:
        """
        同步运行Agent
        
        Args:
            input_data: Agent输入数据
            
        Returns:
            AgentOutput: Agent输出数据
        """
        pass
    
    def process_input(self, input_data: AgentInput) -> Dict[str, Any]:
        """
        处理输入数据
        
        Args:
            input_data: Agent输入数据
            
        Returns:
            Dict[str, Any]: 处理后的输入数据
        """
        processed_input = {
            "query": input_data.query,
        }
        
        # 添加历史记录
        if input_data.history:
            processed_input["history"] = input_data.history
        
        # 添加上下文
        if input_data.context:
            processed_input["context"] = input_data.context
        
        return processed_input
    
    def format_output(self, result: Dict[str, Any]) -> AgentOutput:
        """
        格式化输出结果
        
        Args:
            result: 原始结果
            
        Returns:
            AgentOutput: 格式化的输出
        """
        return AgentOutput(
            response=result.get("response", ""),
            actions=result.get("actions"),
            metadata=result.get("metadata")
        ) 