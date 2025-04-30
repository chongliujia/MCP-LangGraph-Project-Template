"""
基础规划器抽象类 - 定义规划器的接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from . import PlannerInput, PlannerOutput


class BasePlanner(ABC):
    """
    规划器的抽象基类，定义了规划器需要实现的接口
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化规划器
        
        Args:
            config: 规划器配置参数
        """
        self.config = config or {}
    
    @abstractmethod
    async def plan(self, input_data: PlannerInput) -> PlannerOutput:
        """
        异步生成执行计划
        
        Args:
            input_data: 规划器输入数据
            
        Returns:
            PlannerOutput: 执行计划输出
        """
        pass
    
    @abstractmethod
    def plan_sync(self, input_data: PlannerInput) -> PlannerOutput:
        """
        同步生成执行计划
        
        Args:
            input_data: 规划器输入数据
            
        Returns:
            PlannerOutput: 执行计划输出
        """
        pass
    
    def validate_plan(self, plan_output: PlannerOutput) -> bool:
        """
        验证计划的有效性
        
        Args:
            plan_output: 执行计划输出
            
        Returns:
            bool: 计划是否有效
        """
        # 检查计划中的每个步骤
        steps = plan_output.plan
        step_ids = set(step.id for step in steps)
        
        # 检查所有依赖项是否都存在
        for step in steps:
            if step.dependencies:
                for dep_id in step.dependencies:
                    if dep_id not in step_ids:
                        return False
        
        return True 