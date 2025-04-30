"""
DeepSeek API 使用示例
"""

import os
import asyncio
from dotenv import load_dotenv
import sys
import logging

# 设置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("deepseek_example")

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import ModelFactory, ModelInput


async def test_deepseek_api():
    """测试 DeepSeek API"""
    # 加载环境变量
    load_dotenv()
    
    # 自定义 API 密钥（优先级高于环境变量）
    api_key = "sk-6542d2c775ea41b190b3ef7845b1fb35"
    
    # 创建 DeepSeek 模型实例，启用调试模式
    model = ModelFactory.create_model("deepseek", {
        "api_key": api_key,
        "temperature": 0.7,
        "debug": True,
        "timeout": 30.0  # 减少超时时间，以便更快地捕获问题
    })
    
    # 准备模型输入
    model_input = ModelInput(
        messages=[
            {"role": "user", "content": "你好，请介绍一下自己，你是什么模型？"}
        ]
    )
    
    try:
        # 调用模型
        logger.info("发送请求到 DeepSeek API...")
        response = await model.generate(model_input)
        
        # 检查是否有错误
        if response.metadata and response.metadata.get("error"):
            logger.error(f"API 调用出错: {response.metadata['error']}")
            print(f"\n错误: {response.content}")
            return
            
        # 输出结果
        print("\n" + "=" * 50)
        print("响应内容:")
        print("-" * 50)
        print(response.content)
        print("=" * 50)
        
        # 输出元数据
        print("\n元数据:")
        print(response.metadata)
        
    except Exception as e:
        logger.error(f"运行时异常: {str(e)}")
        print(f"\n发生错误: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_deepseek_api()) 