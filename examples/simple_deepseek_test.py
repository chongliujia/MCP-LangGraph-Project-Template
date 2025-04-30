"""
DeepSeek API 简单测试脚本
使用直接HTTP请求来测试API连通性
"""

import requests
import json
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_deepseek_api():
    """使用请求库直接测试DeepSeek API"""
    
    # API 配置
    api_key = "sk-6542d2c775ea41b190b3ef7845b1fb35"
    api_url = "https://api.deepseek.com/v1/chat/completions"
    
    # 请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 请求体
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "Hello, please introduce yourself as an AI model."}
        ],
        "temperature": 0.7
    }
    
    print("发送请求到 DeepSeek API...")
    
    try:
        # 发送请求
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        
        # 检查响应
        if response.status_code == 200:
            response_data = response.json()
            
            print("\n" + "=" * 50)
            print("响应内容:")
            print("-" * 50)
            message = response_data.get("choices", [{}])[0].get("message", {})
            content = message.get("content", "没有内容")
            print(content)
            print("=" * 50)
            
            print("\n元数据:")
            print(f"Model: {response_data.get('model')}")
            print(f"Usage: {response_data.get('usage')}")
        else:
            print(f"API请求失败: {response.status_code}")
            print(f"错误消息: {response.text}")
    
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    test_deepseek_api() 