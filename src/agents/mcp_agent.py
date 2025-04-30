"""
MCP Agent - 基于MCP架构的Agent实现
"""

from typing import Dict, Any, Optional, List, Callable
import uuid
import asyncio

from ..models import BaseModelLayer, OpenAIModel, ModelInput, ModelOutput, ModelFactory
from ..controllers import BaseController, WorkflowController, ControllerInput, ControllerOutput
from ..planners import BasePlanner, LLMPlanner, PlannerInput, PlannerOutput, PlanStep
from ..tools import BaseTool, ToolRegistry, ToolInput, ToolOutput

from . import AgentInput, AgentOutput
from .base_agent import BaseAgent


class MCPAgent(BaseAgent):
    """
    基于MCP架构的Agent实现
    
    Model: 负责与LLM交互，处理自然语言理解和生成
    Controller: 控制系统流程，协调各组件间的交互
    Planner: 负责任务规划、分解和执行策略
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        model_layer: Optional[BaseModelLayer] = None,
        controller: Optional[BaseController] = None,
        planner: Optional[BasePlanner] = None,
        tool_registry: Optional[ToolRegistry] = None
    ):
        """
        初始化MCP Agent
        
        Args:
            config: Agent配置参数
            model_layer: 模型层实例
            controller: 控制器实例
            planner: 规划器实例
            tool_registry: 工具注册表实例
        """
        super().__init__(config)
        
        # 组件初始化
        if model_layer:
            self.model_layer = model_layer
        else:
            # 使用ModelFactory创建模型实例
            provider = config.get("provider", "openai")
            self.model_layer = ModelFactory.create_model(provider, config)
            
        self.controller = controller or self._create_default_controller()
        self.planner = planner or LLMPlanner(config, self.model_layer)
        self.tool_registry = tool_registry or ToolRegistry()
        
        # 设置工作流
        self._setup_workflow()
    
    async def run(self, input_data: AgentInput) -> AgentOutput:
        """
        异步运行Agent
        
        Args:
            input_data: Agent输入数据
            
        Returns:
            AgentOutput: Agent输出数据
        """
        # 处理输入
        processed_input = self.process_input(input_data)
        
        # 准备控制器输入
        controller_input = ControllerInput(
            state={
                "input": processed_input,
                "output": {
                    "response": "",
                    "actions": []
                },
                "context": input_data.context or {},
                "conversation_id": str(uuid.uuid4()),
                "status": "STARTED"
            },
            event={
                "type": "START",
                "data": processed_input
            }
        )
        
        # 运行控制器
        controller_output = await self.controller.process(controller_input)
        
        # 获取结果
        metadata = controller_output.metadata or {}
        result = {
            "response": controller_output.next_state.get("output", {}).get("response", ""),
            "actions": controller_output.next_state.get("output", {}).get("actions", []),
            "metadata": {
                "conversation_id": controller_output.next_state.get("conversation_id"),
                "status": controller_output.next_state.get("status"),
                **metadata
            }
        }
        
        # 格式化输出
        return self.format_output(result)
    
    def run_sync(self, input_data: AgentInput) -> AgentOutput:
        """
        同步运行Agent
        
        Args:
            input_data: Agent输入数据
            
        Returns:
            AgentOutput: Agent输出数据
        """
        # 处理输入
        processed_input = self.process_input(input_data)
        
        # 准备控制器输入
        controller_input = ControllerInput(
            state={
                "input": processed_input,
                "output": {
                    "response": "",
                    "actions": []
                },
                "context": input_data.context or {},
                "conversation_id": str(uuid.uuid4()),
                "status": "STARTED"
            },
            event={
                "type": "START",
                "data": processed_input
            }
        )
        
        # 运行控制器
        controller_output = self.controller.process_sync(controller_input)
        
        # 获取结果
        metadata = controller_output.metadata or {}
        result = {
            "response": controller_output.next_state.get("output", {}).get("response", ""),
            "actions": controller_output.next_state.get("output", {}).get("actions", []),
            "metadata": {
                "conversation_id": controller_output.next_state.get("conversation_id"),
                "status": controller_output.next_state.get("status"),
                **metadata
            }
        }
        
        # 格式化输出
        return self.format_output(result)
    
    def _create_default_controller(self) -> WorkflowController:
        """
        创建默认控制器
        
        Returns:
            WorkflowController: 默认控制器实例
        """
        return WorkflowController(self.config)
    
    def _setup_workflow(self):
        """
        设置Agent工作流
        """
        # 获取控制器
        controller = self.controller
        
        # 添加节点
        controller.add_node("start", self._start_node)
        controller.add_node("plan", self._plan_node)
        controller.add_node("execute", self._execute_node)
        controller.add_node("respond", self._respond_node)
        
        # 添加边
        controller.add_edge("start", "plan")
        controller.add_edge("plan", "execute")
        controller.add_edge("execute", "respond")
        
        # 设置入口点
        controller.set_entry_point("start")
    
    # 工作流节点处理函数
    
    async def _start_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        开始节点处理函数
        
        Args:
            state: 当前状态
            
        Returns:
            Dict[str, Any]: 更新后的状态
        """
        # 更新状态
        state["status"] = "PROCESSING"
        
        return state
    
    async def _plan_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        规划节点处理函数
        
        Args:
            state: 当前状态
            
        Returns:
            Dict[str, Any]: 更新后的状态
        """
        # 获取输入
        input_data = state.get("input", {})
        query = input_data.get("query", "")
        context = state.get("context", {})
        
        # 准备规划器输入
        planner_input = PlannerInput(
            objective=query,
            context=context,
            available_tools=[
                {
                    "name": tool.name,
                    "description": tool.description
                }
                for tool in self.tool_registry.get_all_tools().values()
            ]
        )
        
        # 生成计划
        plan_output = await self.planner.plan(planner_input)
        
        # 更新状态
        state["plan"] = plan_output.model_dump()
        
        return state
    
    async def _execute_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行节点处理函数
        
        Args:
            state: 当前状态
            
        Returns:
            Dict[str, Any]: 更新后的状态
        """
        # 获取计划
        plan_data = state.get("plan", {})
        steps = [PlanStep(**step) for step in plan_data.get("plan", [])]
        
        # 执行结果列表
        execution_results = []
        
        # 按顺序执行步骤
        for step in steps:
            # 如果有工具，则执行工具
            if step.tool and step.tool_input:
                # 获取工具
                tool = self.tool_registry.get_tool(step.tool)
                
                if tool:
                    # 准备工具输入
                    tool_input = ToolInput(
                        parameters=step.tool_input,
                        context=state.get("context", {})
                    )
                    
                    # 执行工具
                    try:
                        tool_output = await tool.execute(tool_input)
                        
                        # 记录结果
                        execution_results.append({
                            "step_id": step.id,
                            "step_name": step.name,
                            "tool": step.tool,
                            "result": tool_output.result,
                            "error": tool_output.error,
                            "status": "SUCCESS" if not tool_output.error else "ERROR"
                        })
                    except Exception as e:
                        # 记录错误
                        execution_results.append({
                            "step_id": step.id,
                            "step_name": step.name,
                            "tool": step.tool,
                            "result": None,
                            "error": str(e),
                            "status": "ERROR"
                        })
                else:
                    # 记录未找到工具的错误
                    execution_results.append({
                        "step_id": step.id,
                        "step_name": step.name,
                        "tool": step.tool,
                        "result": None,
                        "error": f"Tool '{step.tool}' not found",
                        "status": "ERROR"
                    })
            else:
                # 没有工具的步骤，仅记录为已完成
                execution_results.append({
                    "step_id": step.id,
                    "step_name": step.name,
                    "tool": None,
                    "result": None,
                    "error": None,
                    "status": "COMPLETED"
                })
        
        # 更新状态
        state["execution_results"] = execution_results
        
        return state
    
    async def _respond_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        响应节点处理函数
        
        Args:
            state: 当前状态
            
        Returns:
            Dict[str, Any]: 更新后的状态
        """
        # 获取输入、计划和执行结果
        input_data = state.get("input", {})
        query = input_data.get("query", "")
        plan_data = state.get("plan", {})
        execution_results = state.get("execution_results", [])
        
        # 构建系统提示
        system_prompt = """您是一个有用的AI助手。基于提供的任务执行结果，请生成一个全面、有帮助的回复。
您的回复应该:
1. 解释执行了哪些步骤
2. 总结重要的结果
3. 如果有任何错误，解释这些错误
4. 提供一个清晰的结论或建议

保持回复简明扼要、信息丰富且对用户有帮助。
"""
        
        # 构建用户提示
        user_prompt = f"原始查询: {query}\n\n"
        
        # 添加计划信息
        user_prompt += "执行计划:\n"
        for i, step in enumerate(plan_data.get("plan", []), 1):
            step_info = f"{i}. {step.get('name')}: {step.get('description')}"
            user_prompt += f"{step_info}\n"
        
        # 添加执行结果
        user_prompt += "\n执行结果:\n"
        for i, result in enumerate(execution_results, 1):
            status = result.get("status", "")
            step_name = result.get("step_name", "")
            
            result_text = f"{i}. {step_name} - 状态: {status}"
            
            if status == "SUCCESS":
                result_value = result.get("result", "")
                if result_value:
                    if isinstance(result_value, (dict, list)):
                        import json
                        result_value = json.dumps(result_value, ensure_ascii=False, indent=2)
                    result_text += f"\n   结果: {result_value}"
            elif status == "ERROR":
                error = result.get("error", "")
                result_text += f"\n   错误: {error}"
            
            user_prompt += f"{result_text}\n"
        
        user_prompt += "\n请基于以上信息提供一个有帮助的响应。"
        
        # 准备模型输入
        model_input = ModelInput(
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            system_prompt=system_prompt,
            model=self.config.get("model"),
            temperature=self.config.get("temperature", 0.1),
        )
        
        # 调用模型生成响应
        model_output = await self.model_layer.generate(model_input)
        
        # 更新状态
        state["output"] = {
            "response": model_output.content,
            "actions": execution_results
        }
        state["status"] = "COMPLETED"
        
        return state 