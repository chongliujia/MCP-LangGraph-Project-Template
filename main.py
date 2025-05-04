"""
MCP LangGraph Framework - Main Entry Point
"""

import os
import argparse
import asyncio
from typing import Dict, Any, List
from dotenv import load_dotenv

from src.agents import MCPAgent, AgentInput
from src.tools import BaseTool, ToolRegistry
from src.utils import setup_logger, load_config

# Load environment variables
load_dotenv()

# Setup logger
logger = setup_logger("mcp_framework")


async def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="MCP LangGraph Framework")
    parser.add_argument("--config", type=str, default="config.json", help="Path to configuration file")
    parser.add_argument("--query", type=str, help="Query to process")
    parser.add_argument("--provider", type=str, default="deepseek", help="LLM provider (openai or deepseek)")
    parser.add_argument("--api-key", type=str, help="API key")
    args = parser.parse_args()
    
    # Load configuration
    default_config = {
        "model": os.getenv("DEFAULT_MODEL", "deepseek-chat"),
        "temperature": float(os.getenv("DEFAULT_TEMPERATURE", "0.1")),
        "provider": args.provider
    }
    config = load_config(args.config, default_config)
    
    # If provider specified in command line, override configuration file setting
    if args.provider:
        config["provider"] = args.provider
    
    # Set API key
    if args.api_key:
        config["api_key"] = args.api_key
    elif config["provider"] == "deepseek" and os.getenv("DEEPSEEK_API_KEY"):
        config["api_key"] = os.getenv("DEEPSEEK_API_KEY")
    elif config["provider"] == "openai" and os.getenv("OPENAI_API_KEY"):
        config["api_key"] = os.getenv("OPENAI_API_KEY")
    
    if "api_key" not in config or not config["api_key"]:
        logger.warning(f"No API key set for {config['provider']}. Please provide it through environment variables, configuration file, or command line arguments")
    
    logger.info(f"Loaded configuration: {config}")
    
    # Create tool registry
    tool_registry = ToolRegistry()
    
    # Create Agent
    agent = MCPAgent(config=config, tool_registry=tool_registry)
    
    # If query provided, run it
    if args.query:
        # Prepare Agent input
        agent_input = AgentInput(
            query=args.query,
            history=[],
            context={}
        )
        
        # Run Agent
        logger.info(f"Running query: {args.query}")
        agent_output = await agent.run(agent_input)
        
        # Print results
        print("\n" + "=" * 50)
        print("Query result:")
        print("-" * 50)
        print(agent_output.response)
        print("=" * 50)
    else:
        print("Please provide a query using the --query parameter")


if __name__ == "__main__":
    # Run main program
    asyncio.run(main()) 