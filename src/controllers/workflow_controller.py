"""
工作流控制器 - 使用LangGraph构建工作流
"""

from typing import Dict, Any, Optional, List, Callable, Type, Union
import asyncio

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from . import ControllerInput, ControllerOutput
from .base_controller import BaseController


class WorkflowController(BaseController):
    """
    基于LangGraph实现的工作流控制器
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化工作流控制器
        
        Args:
            config: 控制器配置参数
        """
        super().__init__(config)
        self.nodes = {}
        self.edges = []
        self.entry_point = None
        self.graph = None
    
    def add_node(self, node_id: str, node_handler: Callable):
        """
        添加工作流节点
        
        Args:
            node_id: 节点ID
            node_handler: 节点处理函数
        """
        self.nodes[node_id] = node_handler
    
    def add_tool_node(self, node_id: str, tool_handler: Callable):
        """
        添加工具节点
        
        Args:
            node_id: 节点ID
            tool_handler: 工具处理函数
        """
        self.nodes[node_id] = ToolNode(tool_handler)
    
    def add_edge(self, from_node: str, to_node: Union[str, Type[END]], condition: Optional[Callable] = None):
        """
        添加工作流边
        
        Args:
            from_node: 起始节点ID
            to_node: 目标节点ID或END标记
            condition: 条件函数，用于确定是否应该沿着此边传递
        """
        self.edges.append((from_node, to_node, condition))
    
    def set_entry_point(self, node_id: str):
        """
        设置入口节点
        
        Args:
            node_id: 入口节点ID
        """
        self.entry_point = node_id
    
    def build_graph(self):
        """
        构建工作流图
        """
        if not self.entry_point:
            raise ValueError("必须设置入口节点")
        
        # 定义状态类型
        state_type = Dict[str, Any]
        
        # 创建状态图
        graph = StateGraph(state_type)
        
        # 添加节点
        for node_id, handler in self.nodes.items():
            graph.add_node(node_id, handler)
        
        # 添加边
        for from_node, to_node, condition in self.edges:
            if condition:
                graph.add_conditional_edges(from_node, condition, {True: to_node})
            else:
                graph.add_edge(from_node, to_node)
        
        # 设置入口节点
        graph.set_entry_point(self.entry_point)
        
        # 编译图
        self.graph = graph.compile()
    
    async def process(self, input_data: ControllerInput) -> ControllerOutput:
        """
        异步处理输入并产生输出
        
        Args:
            input_data: 控制器输入数据
            
        Returns:
            ControllerOutput: 控制器输出数据
        """
        if not self.graph:
            self.build_graph()
        
        # 运行工作流
        result = await self.graph.ainvoke(input_data.state)
        
        return ControllerOutput(
            next_state=result,
            result=result.get("result"),
            next_action=result.get("next_action"),
            metadata={"workflow_trace": result.get("__run", {}).get("trace", [])}
        )
    
    def process_sync(self, input_data: ControllerInput) -> ControllerOutput:
        """
        同步处理输入并产生输出
        
        Args:
            input_data: 控制器输入数据
            
        Returns:
            ControllerOutput: 控制器输出数据
        """
        if not self.graph:
            self.build_graph()
        
        # 运行工作流
        result = self.graph.invoke(input_data.state)
        
        return ControllerOutput(
            next_state=result,
            result=result.get("result"),
            next_action=result.get("next_action"),
            metadata={"workflow_trace": result.get("__run", {}).get("trace", [])}
        ) 