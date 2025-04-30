"""
使用 DeepSeek 的 MCP Agent 示例
"""

import os
import asyncio
import sys
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents import MCPAgent, AgentInput
from src.tools import ToolRegistry


async def test_mcp_agent_with_deepseek():
    """测试使用 DeepSeek 的 MCP Agent"""
    # 加载环境变量
    load_dotenv()
    
    # 准备配置
    config = {
        "provider": "deepseek",  # 使用 DeepSeek 模型
        "api_key": "sk-6542d2c775ea41b190b3ef7845b1fb35",  # DeepSeek API 密钥
        "temperature": 0.7,
    }
    
    # 创建工具注册表
    tool_registry = ToolRegistry()
    
    # 创建 Agent
    agent = MCPAgent(config=config, tool_registry=tool_registry)
    
    # 准备输入
    agent_input = AgentInput(
        query="请介绍一下量子计算的基本原理",
        history=[],
        context={}
    )
    
    # 运行 Agent
    print("运行 MCP Agent (DeepSeek)...")
    agent_output = await agent.run(agent_input)
    
    # 输出结果
    print("\n" + "=" * 50)
    print("响应内容:")
    print("-" * 50)
    print(agent_output.response)
    print("=" * 50)
    
    # 输出元数据
    print("\n元数据:")
    print(agent_output.metadata)


if __name__ == "__main__":
    asyncio.run(test_mcp_agent_with_deepseek()) 