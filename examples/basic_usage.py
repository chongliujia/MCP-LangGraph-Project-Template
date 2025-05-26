"""
MCP AI Framework 基本使用示例
"""

import asyncio
import os
import sys
sys.path.append('..')

from mcp_framework import MCPFramework


async def basic_chat_example():
    """基本聊天示例"""
    print("=== 基本聊天示例 ===")
    
    async with MCPFramework() as framework:
        # 简单对话
        response = await framework.chat("你好，请简单介绍一下你自己")
        print(f"AI: {response}")


async def vector_database_example():
    """向量数据库示例"""
    print("\n=== 向量数据库示例 ===")
    
    async with MCPFramework() as framework:
        # 添加一些示例文档
        documents = [
            "Python是一种高级编程语言，具有简洁的语法和强大的功能。",
            "机器学习是人工智能的一个分支，通过算法让计算机从数据中学习。",
            "深度学习使用神经网络来模拟人脑的学习过程。"
        ]
        
        print("添加文档到向量数据库...")
        for i, doc in enumerate(documents):
            doc_id = await framework.add_document(
                text=doc,
                metadata={"doc_id": i, "category": "tech"}
            )
            print(f"文档 {i+1} 已添加，ID: {doc_id}")
        
        # 搜索相似文档
        print("\n搜索相似文档...")
        query = "什么是人工智能"
        results = await framework.search_similar(query, top_k=3)
        
        print(f"查询: {query}")
        print("相似文档:")
        for i, result in enumerate(results, 1):
            print(f"{i}. 相似度: {result.get('score', 'N/A'):.4f}")
            print(f"   内容: {result.get('text', 'N/A')}")
            print()


async def main():
    """主函数"""
    print("MCP AI Framework 示例程序")
    print("=" * 50)
    
    # 检查环境变量
    required_vars = ["QWEN_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"警告: 缺少环境变量 {missing_vars}")
        print("请设置相应的API密钥后再运行示例")
        print("参考 env.example 文件进行配置")
        return
    
    try:
        await basic_chat_example()
        await vector_database_example()
        
    except Exception as e:
        print(f"示例运行出错: {e}")
        print("请检查配置和网络连接")


if __name__ == "__main__":
    asyncio.run(main()) 