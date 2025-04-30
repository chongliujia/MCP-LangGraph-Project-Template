"""
简单示例 - 展示如何使用MCP框架创建一个简单的Agent
"""

import os
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv

from src.agents import MCPAgent, AgentInput
from src.models import OpenAIModel
from src.tools import BaseTool, ToolRegistry, ToolInput, ToolOutput


# 加载环境变量
load_dotenv()


# 定义一个简单的计算器工具
class CalculatorTool(BaseTool):
    """
    简单的计算器工具
    """
    
    def __init__(self):
        """初始化计算器工具"""
        super().__init__(
            name="calculator",
            description="执行简单的数学计算",
            parameters_schema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的数学表达式，如'1 + 2'"
                    }
                },
                "required": ["expression"]
            }
        )
    
    async def execute(self, input_data: ToolInput) -> ToolOutput:
        """
        异步执行计算
        
        Args:
            input_data: 工具输入数据
            
        Returns:
            ToolOutput: 工具输出数据
        """
        # 从输入中获取表达式
        expression = input_data.parameters.get("expression", "")
        
        try:
            # 安全地计算表达式
            # 注意：eval在生产环境中使用可能存在安全风险
            result = eval(expression, {"__builtins__": {}}, {})
            
            return ToolOutput(
                result=result,
                error=None
            )
        except Exception as e:
            return ToolOutput(
                result=None,
                error=f"计算错误: {str(e)}"
            )
    
    def execute_sync(self, input_data: ToolInput) -> ToolOutput:
        """
        同步执行计算
        
        Args:
            input_data: 工具输入数据
            
        Returns:
            ToolOutput: 工具输出数据
        """
        # 简单地调用异步方法
        return asyncio.run(self.execute(input_data))


async def main():
    """主程序入口"""
    # 配置
    config = {
        "model": os.getenv("DEFAULT_MODEL", "gpt-4o"),
        "temperature": 0.1,
    }
    
    # 创建工具注册表
    tool_registry = ToolRegistry()
    
    # 注册工具
    calculator_tool = CalculatorTool()
    tool_registry.register_tool(calculator_tool)
    
    # 创建Agent
    agent = MCPAgent(config=config, tool_registry=tool_registry)
    
    # 准备查询
    query = "请计算25乘以16，并告诉我结果"
    
    # 准备Agent输入
    agent_input = AgentInput(
        query=query,
        history=[],
        context={}
    )
    
    # 运行Agent
    print(f"运行查询: {query}")
    agent_output = await agent.run(agent_input)
    
    # 打印结果
    print("\n" + "=" * 50)
    print("查询结果:")
    print("-" * 50)
    print(agent_output.response)
    print("=" * 50)
    
    # 打印执行的动作
    if agent_output.actions:
        print("\n执行的动作:")
        for action in agent_output.actions:
            print(f"- {action.get('step_name')} ({action.get('status')})")
            if action.get('result') is not None:
                print(f"  结果: {action.get('result')}")
            if action.get('error') is not None:
                print(f"  错误: {action.get('error')}")


if __name__ == "__main__":
    # 运行主程序
    asyncio.run(main()) 