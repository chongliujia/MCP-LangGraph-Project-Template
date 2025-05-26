"""
MCP LangGraph Framework 示例
"""

import asyncio
import os
import sys
sys.path.append('..')

from mcp_framework import MCPLangGraphFramework
from mcp_framework.tools import CalculatorTool, SearchTool, WeatherTool
from langchain_core.messages import HumanMessage


async def basic_chat_example():
    """基本聊天示例"""
    print("=== 基本聊天示例 ===")
    
    async with MCPLangGraphFramework() as framework:
        # 简单对话
        response = await framework.chat("你好，请简单介绍一下你自己")
        print(f"AI: {response}")


async def tool_usage_example():
    """工具使用示例"""
    print("\n=== 工具使用示例 ===")
    
    async with MCPLangGraphFramework() as framework:
        # 注册工具
        framework.register_tool(CalculatorTool())
        framework.register_tool(SearchTool())
        framework.register_tool(WeatherTool())
        
        print(f"可用工具: {framework.get_available_tools()}")
        
        # 使用计算器工具
        response = await framework.chat("请计算 15 + 27 * 3")
        print(f"计算结果: {response}")
        
        # 使用搜索工具
        response = await framework.chat("搜索关于人工智能的信息")
        print(f"搜索结果: {response}")
        
        # 使用天气工具
        response = await framework.chat("查询北京的天气")
        print(f"天气信息: {response}")


async def workflow_example():
    """工作流示例"""
    print("\n=== 工作流示例 ===")
    
    async with MCPLangGraphFramework() as framework:
        # 注册工具
        framework.register_tool(CalculatorTool())
        
        # 直接运行工作流
        result = await framework.run_workflow({
            "messages": [HumanMessage(content="计算 (10 + 5) * 2 的结果")]
        })
        
        print("工作流结果:")
        for message in result.get("messages", []):
            # Handle different message types
            if hasattr(message, 'content'):
                print(f"- {message.content}")
            elif isinstance(message, str):
                print(f"- {message}")
            else:
                print(f"- {str(message)}")


async def health_check_example():
    """健康检查示例"""
    print("\n=== 健康检查示例 ===")
    
    async with MCPLangGraphFramework() as framework:
        health = await framework.health_check()
        print("系统健康状态:")
        print(f"框架状态: {health['framework']}")
        print("组件状态:")
        for component, status in health.get('components', {}).items():
            print(f"  {component}: {status}")
        print(f"工具数量: {health.get('tools_count', 0)}")


async def main():
    """主函数"""
    print("MCP LangGraph Framework 示例程序")
    print("=" * 50)
    
    try:
        # 运行各种示例
        await basic_chat_example()
        await tool_usage_example()
        await workflow_example()
        await health_check_example()
        
    except Exception as e:
        print(f"示例运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 