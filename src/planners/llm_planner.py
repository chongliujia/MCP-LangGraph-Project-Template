"""
基于LLM的规划器 - 使用大语言模型生成执行计划
"""

import json
import uuid
from typing import Dict, Any, Optional, List

from .. import models
from . import PlannerInput, PlannerOutput, PlanStep, BasePlanner


class LLMPlanner(BasePlanner):
    """
    使用LLM生成执行计划的规划器
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, model_layer: Optional[models.BaseModelLayer] = None):
        """
        初始化LLM规划器
        
        Args:
            config: 规划器配置参数
            model_layer: 模型层实例
        """
        super().__init__(config)
        self.model_layer = model_layer or models.OpenAIModel(config)
    
    async def plan(self, input_data: PlannerInput) -> PlannerOutput:
        """
        异步生成执行计划
        
        Args:
            input_data: 规划器输入数据
            
        Returns:
            PlannerOutput: 执行计划输出
        """
        # 构建系统提示
        system_prompt = self._build_system_prompt(input_data)
        
        # 构建任务提示
        task_prompt = self._build_task_prompt(input_data)
        
        # 准备模型输入
        model_input = models.ModelInput(
            messages=[
                {"role": "user", "content": task_prompt}
            ],
            system_prompt=system_prompt,
            model=self.config.get("model"),
            temperature=self.config.get("temperature", 0.1),
        )
        
        # 调用模型生成计划
        model_output = await self.model_layer.generate(model_input)
        
        # 解析模型输出
        return self._parse_model_output(model_output, input_data)
    
    def plan_sync(self, input_data: PlannerInput) -> PlannerOutput:
        """
        同步生成执行计划
        
        Args:
            input_data: 规划器输入数据
            
        Returns:
            PlannerOutput: 执行计划输出
        """
        # 构建系统提示
        system_prompt = self._build_system_prompt(input_data)
        
        # 构建任务提示
        task_prompt = self._build_task_prompt(input_data)
        
        # 准备模型输入
        model_input = models.ModelInput(
            messages=[
                {"role": "user", "content": task_prompt}
            ],
            system_prompt=system_prompt,
            model=self.config.get("model"),
            temperature=self.config.get("temperature", 0.1),
        )
        
        # 调用模型生成计划
        model_output = self.model_layer.generate_sync(model_input)
        
        # 解析模型输出
        return self._parse_model_output(model_output, input_data)
    
    def _build_system_prompt(self, input_data: PlannerInput) -> str:
        """
        构建系统提示
        
        Args:
            input_data: 规划器输入数据
            
        Returns:
            str: 系统提示
        """
        # 基础系统提示
        system_prompt = """您是一个专业的任务规划器，负责将复杂目标分解为可执行的步骤。
请仔细分析提供的目标，并创建一个详细的执行计划。

每个计划步骤必须包含以下信息：
1. 唯一ID
2. 步骤名称
3. 步骤详细描述
4. 使用的工具名称（如果适用）
5. 工具的输入参数（如果适用）
6. 依赖的其他步骤ID列表（如果有）

请以JSON格式输出您的计划，确保JSON格式正确且可解析。
"""
        
        # 添加约束条件
        if input_data.constraints:
            constraints_text = "\n\n请确保您的计划遵守以下约束条件:\n"
            for i, constraint in enumerate(input_data.constraints, 1):
                constraints_text += f"{i}. {constraint}\n"
            system_prompt += constraints_text
        
        # 添加可用工具信息
        if input_data.available_tools:
            tools_text = "\n\n您可以使用以下工具:\n"
            for tool in input_data.available_tools:
                tools_text += f"- {tool.get('name')}: {tool.get('description')}\n"
            system_prompt += tools_text
        
        return system_prompt
    
    def _build_task_prompt(self, input_data: PlannerInput) -> str:
        """
        构建任务提示
        
        Args:
            input_data: 规划器输入数据
            
        Returns:
            str: 任务提示
        """
        task_prompt = f"目标: {input_data.objective}\n\n"
        
        # 添加上下文信息
        if input_data.context:
            task_prompt += "上下文信息:\n"
            for key, value in input_data.context.items():
                task_prompt += f"- {key}: {value}\n"
        
        task_prompt += "\n请为此目标创建一个详细的执行计划。"
        
        return task_prompt
    
    def _parse_model_output(self, model_output: models.ModelOutput, input_data: PlannerInput) -> PlannerOutput:
        """
        解析模型输出为规划器输出
        
        Args:
            model_output: 模型输出
            input_data: 规划器输入数据
            
        Returns:
            PlannerOutput: 执行计划输出
        """
        content = model_output.content
        
        # 尝试从内容中提取JSON
        try:
            # 找到JSON的开始和结束
            start_idx = content.find("{")
            end_idx = content.rfind("}")
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx+1]
                plan_data = json.loads(json_str)
                
                # 解析步骤
                plan_steps = []
                for step_data in plan_data.get("plan", []):
                    plan_step = PlanStep(
                        id=step_data.get("id", str(uuid.uuid4())),
                        name=step_data.get("name", ""),
                        description=step_data.get("description", ""),
                        tool=step_data.get("tool"),
                        tool_input=step_data.get("tool_input"),
                        dependencies=step_data.get("dependencies")
                    )
                    plan_steps.append(plan_step)
                
                # 创建输出
                return PlannerOutput(
                    plan=plan_steps,
                    reasoning=plan_data.get("reasoning"),
                    metadata={"original_model_output": content}
                )
            
        except (json.JSONDecodeError, KeyError) as e:
            # 如果解析失败，尝试创建一个简单的计划
            pass
        
        # 如果无法解析JSON，创建一个简单的单步计划
        plan_step = PlanStep(
            id="step_1",
            name="执行目标",
            description=input_data.objective,
            tool=None,
            tool_input=None,
            dependencies=None
        )
        
        return PlannerOutput(
            plan=[plan_step],
            reasoning="无法从模型输出解析详细计划，创建了一个简单的单步计划。",
            metadata={"original_model_output": content, "parsing_error": True}
        ) 