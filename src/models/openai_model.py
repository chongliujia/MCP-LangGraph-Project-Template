"""
OpenAI模型实现 - 使用OpenAI API实现模型层
"""

import os
import asyncio
from typing import Dict, Any, Optional, List
import json

from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion

from . import ModelInput, ModelOutput
from .base_model import BaseModelLayer


class OpenAIModel(BaseModelLayer):
    """
    OpenAI模型实现
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化OpenAI模型层
        
        Args:
            config: 模型配置参数
        """
        super().__init__(config)
        self.api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
        self.default_model = config.get("model") or os.getenv("DEFAULT_MODEL", "gpt-4o")
        self.default_temperature = float(config.get("temperature") or os.getenv("DEFAULT_TEMPERATURE", 0.1))
        
        # 同步客户端
        self.client = OpenAI(api_key=self.api_key)
        # 异步客户端
        self.async_client = AsyncOpenAI(api_key=self.api_key)
    
    async def generate(self, input_data: ModelInput) -> ModelOutput:
        """
        异步生成响应
        
        Args:
            input_data: 模型输入数据
            
        Returns:
            ModelOutput: 模型输出数据
        """
        messages = self.prepare_messages(input_data)
        model = input_data.model or self.default_model
        temperature = input_data.temperature or self.default_temperature
        
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        
        # 添加工具配置
        if input_data.tools:
            kwargs["tools"] = input_data.tools
        
        # 添加其他参数
        if input_data.additional_params:
            kwargs.update(input_data.additional_params)
        
        # 调用API
        response = await self.async_client.chat.completions.create(**kwargs)
        
        return self._process_response(response)
    
    def generate_sync(self, input_data: ModelInput) -> ModelOutput:
        """
        同步生成响应
        
        Args:
            input_data: 模型输入数据
            
        Returns:
            ModelOutput: 模型输出数据
        """
        messages = self.prepare_messages(input_data)
        model = input_data.model or self.default_model
        temperature = input_data.temperature or self.default_temperature
        
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        
        # 添加工具配置
        if input_data.tools:
            kwargs["tools"] = input_data.tools
        
        # 添加其他参数
        if input_data.additional_params:
            kwargs.update(input_data.additional_params)
        
        # 调用API
        response = self.client.chat.completions.create(**kwargs)
        
        return self._process_response(response)
    
    def _process_response(self, response: ChatCompletion) -> ModelOutput:
        """
        处理模型响应
        
        Args:
            response: OpenAI API返回的响应
            
        Returns:
            ModelOutput: 处理后的模型输出
        """
        first_choice = response.choices[0]
        message = first_choice.message
        
        output = ModelOutput(
            content=message.content,
            tool_calls=[tool_call.model_dump() for tool_call in message.tool_calls] if message.tool_calls else None,
            metadata={
                "model": response.model,
                "usage": response.usage.model_dump(),
                "finish_reason": first_choice.finish_reason,
            }
        )
        
        return output 