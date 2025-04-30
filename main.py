"""
MCP LangGraph Framework - 主程序入口
"""

import os
import argparse
import asyncio
from typing import Dict, Any, List
from dotenv import load_dotenv

from src.agents import MCPAgent, AgentInput
from src.tools import BaseTool, ToolRegistry
from src.utils import setup_logger, load_config

# 加载环境变量
load_dotenv()

# 设置日志记录器
logger = setup_logger("mcp_framework")


async def main():
    """主程序入口"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="MCP LangGraph Framework")
    parser.add_argument("--config", type=str, default="config.json", help="配置文件路径")
    parser.add_argument("--query", type=str, help="查询")
    parser.add_argument("--provider", type=str, default="deepseek", help="LLM提供者（openai或deepseek）")
    parser.add_argument("--api-key", type=str, help="API密钥")
    args = parser.parse_args()
    
    # 加载配置
    default_config = {
        "model": os.getenv("DEFAULT_MODEL", "deepseek-chat"),
        "temperature": float(os.getenv("DEFAULT_TEMPERATURE", "0.1")),
        "provider": args.provider
    }
    config = load_config(args.config, default_config)
    
    # 如果命令行指定了提供者，覆盖配置文件中的设置
    if args.provider:
        config["provider"] = args.provider
    
    # 设置API密钥
    if args.api_key:
        config["api_key"] = args.api_key
    elif config["provider"] == "deepseek" and os.getenv("DEEPSEEK_API_KEY"):
        config["api_key"] = os.getenv("DEEPSEEK_API_KEY")
    elif config["provider"] == "openai" and os.getenv("OPENAI_API_KEY"):
        config["api_key"] = os.getenv("OPENAI_API_KEY")
    
    if "api_key" not in config or not config["api_key"]:
        logger.warning(f"未设置{config['provider']}的API密钥，请通过环境变量、配置文件或命令行参数提供")
    
    logger.info(f"加载配置: {config}")
    
    # 创建工具注册表
    tool_registry = ToolRegistry()
    
    # 创建Agent
    agent = MCPAgent(config=config, tool_registry=tool_registry)
    
    # 如果提供了查询，则运行查询
    if args.query:
        # 准备Agent输入
        agent_input = AgentInput(
            query=args.query,
            history=[],
            context={}
        )
        
        # 运行Agent
        logger.info(f"运行查询: {args.query}")
        agent_output = await agent.run(agent_input)
        
        # 打印结果
        print("\n" + "=" * 50)
        print("查询结果:")
        print("-" * 50)
        print(agent_output.response)
        print("=" * 50)
    else:
        print("请使用 --query 参数提供查询")


if __name__ == "__main__":
    # 运行主程序
    asyncio.run(main()) 