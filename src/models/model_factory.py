"""
模型工厂 - 用于创建和管理不同的模型提供者
"""

from typing import Dict, Any, Optional, Type
import os

from .base_model import BaseModelLayer
from .openai_model import OpenAIModel
from .deepseek_model import DeepSeekModel


class ModelFactory:
    """模型工厂类，用于创建不同的模型实例"""

    # 模型类型映射
    MODEL_TYPES = {
        "openai": OpenAIModel,
        "deepseek": DeepSeekModel,
    }

    @classmethod
    def create_model(cls, 
                    provider: str, 
                    config: Optional[Dict[str, Any]] = None) -> BaseModelLayer:
        """
        创建模型实例
        
        Args:
            provider: 模型提供者，如"openai"、"deepseek"等
            config: 模型配置参数
            
        Returns:
            BaseModelLayer: 模型实例
            
        Raises:
            ValueError: 如果提供者不支持
        """
        provider = provider.lower()
        config = config or {}
        
        # 对于DeepSeek，添加特定的配置参数
        if provider == "deepseek":
            # 确保API密钥被正确设置 - 直接使用config中的api_key
            api_key = config.get("api_key") or os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                print("警告: DeepSeek API密钥未设置")
            
            # 明确设置API密钥到配置中
            config["api_key"] = api_key
            
            # 设置其他参数
            if "api_base" not in config:
                config["api_base"] = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
            if "model" not in config:
                config["model"] = os.getenv("DEFAULT_DEEPSEEK_MODEL", "deepseek-chat")
                
        # 对于OpenAI，添加特定的配置参数
        elif provider == "openai":
            if "api_key" not in config:
                config["api_key"] = os.getenv("OPENAI_API_KEY")
            if "model" not in config:
                config["model"] = os.getenv("DEFAULT_MODEL", "gpt-4o")
        
        # 获取模型类
        model_class = cls.MODEL_TYPES.get(provider)
        if not model_class:
            supported = ", ".join(cls.MODEL_TYPES.keys())
            raise ValueError(f"不支持的模型提供者: {provider}。支持的提供者: {supported}")
        
        # 创建并返回模型实例
        return model_class(config) 