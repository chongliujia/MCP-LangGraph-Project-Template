"""
Command Line Interface for MCP AI Framework.
"""

import asyncio
import click
from loguru import logger
from typing import Optional

from .core.framework import MCPFramework
from .config.settings import get_settings


@click.group()
@click.version_option(version="0.1.0")
def main():
    """MCP AI Framework - 通用AI框架命令行工具"""
    pass


@main.command()
@click.option("--host", default="0.0.0.0", help="服务器主机地址")
@click.option("--port", default=8000, help="服务器端口")
@click.option("--debug", is_flag=True, help="启用调试模式")
def serve(host: str, port: int, debug: bool):
    """启动MCP服务器"""
    async def start_server():
        settings = get_settings()
        settings.api_host = host
        settings.api_port = port
        settings.debug = debug
        
        framework = MCPFramework(settings)
        try:
            await framework.start_server()
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在关闭服务器...")
        finally:
            await framework.stop_server()
    
    logger.info(f"启动MCP服务器在 {host}:{port}")
    asyncio.run(start_server())


@main.command()
@click.argument("message")
@click.option("--model", default=None, help="指定使用的模型")
def chat(message: str, model: Optional[str]):
    """与AI模型聊天"""
    async def run_chat():
        async with MCPFramework() as framework:
            response = await framework.chat(message, model_name=model)
            click.echo(f"AI: {response}")
    
    asyncio.run(run_chat())


@main.command()
@click.argument("text")
@click.option("--collection", default=None, help="指定集合名称")
def add_doc(text: str, collection: Optional[str]):
    """添加文档到向量数据库"""
    async def run_add():
        async with MCPFramework() as framework:
            doc_id = await framework.add_document(
                text=text,
                collection_name=collection
            )
            click.echo(f"文档已添加，ID: {doc_id}")
    
    asyncio.run(run_add())


@main.command()
@click.argument("query")
@click.option("--top-k", default=5, help="返回结果数量")
@click.option("--collection", default=None, help="指定集合名称")
def search(query: str, top_k: int, collection: Optional[str]):
    """搜索相似文档"""
    async def run_search():
        async with MCPFramework() as framework:
            results = await framework.search_similar(
                query=query,
                top_k=top_k,
                collection_name=collection
            )
            
            click.echo(f"找到 {len(results)} 个相似文档:")
            for i, result in enumerate(results, 1):
                click.echo(f"{i}. 相似度: {result.get('score', 'N/A')}")
                click.echo(f"   内容: {result.get('text', 'N/A')[:100]}...")
                click.echo()
    
    asyncio.run(run_search())


@main.command()
def health():
    """检查系统健康状态"""
    async def run_health():
        async with MCPFramework() as framework:
            health_status = await framework.health_check()
            
            click.echo("系统健康状态:")
            click.echo(f"框架状态: {health_status['framework']}")
            
            for component, status in health_status.get('components', {}).items():
                click.echo(f"{component}: {status}")
    
    asyncio.run(run_health())


@main.command()
def list_models():
    """列出可用的模型"""
    async def run_list():
        async with MCPFramework() as framework:
            models = framework.get_available_models()
            
            click.echo("可用模型:")
            for model_type, model_list in models.items():
                click.echo(f"\n{model_type.upper()}:")
                for model in model_list:
                    click.echo(f"  - {model}")
    
    asyncio.run(run_list())


@main.command()
def list_tools():
    """列出可用的工具"""
    async def run_list():
        async with MCPFramework() as framework:
            tools = framework.get_available_tools()
            
            click.echo("可用工具:")
            for tool in tools:
                click.echo(f"  - {tool}")
    
    asyncio.run(run_list())


@main.command()
@click.option("--config-file", default="config.yaml", help="配置文件路径")
def init(config_file: str):
    """初始化项目配置"""
    import yaml
    
    config = {
        "mcp_framework": {
            "models": {
                "default_chat": "qwen-turbo",
                "default_embedding": "qwen-embedding",
                "default_rerank": "qwen-rerank"
            },
            "vector_db": {
                "default_collection": "documents",
                "embedding_dimension": 1536
            },
            "tools": {
                "enabled": ["search", "calculator", "weather"]
            }
        }
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    click.echo(f"配置文件已创建: {config_file}")
    click.echo("请编辑配置文件并设置环境变量后使用框架。")


if __name__ == "__main__":
    main() 