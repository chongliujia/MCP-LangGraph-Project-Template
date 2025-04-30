"""
DeepSeek模型实现 - 使用DeepSeek API实现模型层
"""

import os
import asyncio
from typing import Dict, Any, Optional, List
import json
import httpx
import logging

from . import ModelInput, ModelOutput
from .base_model import BaseModelLayer

# 设置日志
logger = logging.getLogger("deepseek_model")


class DeepSeekModel(BaseModelLayer):
    """
    DeepSeek模型实现
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化DeepSeek模型层
        
        Args:
            config: 模型配置参数
        """
        super().__init__(config)
        # 添加调试信息，打印完整的config
        print(f"DeepSeek初始化配置: {config}")
        
        self.api_key = config.get("api_key") or os.getenv("DEEPSEEK_API_KEY")
        # 添加调试信息，打印API密钥状态
        print(f"DeepSeek API密钥: {self.api_key}")
        
        self.default_model = config.get("model") or os.getenv("DEFAULT_DEEPSEEK_MODEL", "deepseek-chat")
        self.default_temperature = float(config.get("temperature") or os.getenv("DEFAULT_TEMPERATURE", 0.1))
        self.api_base = config.get("api_base") or os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
        
        # 日志记录配置
        self.debug = config.get("debug", False)
        
        # 设置超时时间
        self.timeout = config.get("timeout", 60.0)
        
        # 创建客户端
        self.client = httpx.Client(timeout=self.timeout)
        
        if self.debug:
            logger.info(f"初始化DeepSeek模型: API基础URL={self.api_base}, 模型={self.default_model}")
    
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
        
        # 准备请求数据
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        
        # 添加工具配置
        if input_data.tools:
            payload["tools"] = input_data.tools
        
        # 添加其他参数
        if input_data.additional_params:
            payload.update(input_data.additional_params)
        
        # 设置请求头
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 打印调试信息，查看发送请求时的实际API密钥状态
        print(f"DeepSeek API请求头中的认证: Bearer {self.api_key}")
        
        # 日志记录
        if self.debug:
            logger.info(f"DeepSeek API请求: URL={self.api_base}/chat/completions")
            logger.info(f"请求参数: {json.dumps(payload, ensure_ascii=False)}")
        
        try:
            # 异步调用API
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    json=payload,
                    headers=headers
                )
                
                if response.status_code != 200:
                    error_msg = f"API 请求失败: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return ModelOutput(
                        content=f"调用DeepSeek API时出错: {error_msg}",
                        metadata={
                            "error": error_msg,
                            "status_code": response.status_code
                        }
                    )
                    
                response_data = response.json()
                
                # 日志记录
                if self.debug:
                    logger.info(f"DeepSeek API响应: {json.dumps(response_data, ensure_ascii=False)}")
                
                return self._process_response(response_data)
                
        except httpx.TimeoutException as e:
            error_msg = f"API请求超时: {str(e)}"
            logger.error(error_msg)
            return ModelOutput(
                content=f"调用DeepSeek API时超时: {error_msg}",
                metadata={
                    "error": error_msg,
                    "type": "timeout"
                }
            )
        except httpx.RequestError as e:
            error_msg = f"API请求错误: {str(e)}"
            logger.error(error_msg)
            return ModelOutput(
                content=f"调用DeepSeek API时出错: {error_msg}",
                metadata={
                    "error": error_msg,
                    "type": "request_error"
                }
            )
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            logger.error(error_msg)
            return ModelOutput(
                content=f"调用DeepSeek API时发生未知错误: {error_msg}",
                metadata={
                    "error": error_msg,
                    "type": "unknown"
                }
            )
    
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
        
        # 准备请求数据
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        
        # 添加工具配置
        if input_data.tools:
            payload["tools"] = input_data.tools
        
        # 添加其他参数
        if input_data.additional_params:
            payload.update(input_data.additional_params)
        
        # 设置请求头
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 日志记录
        if self.debug:
            logger.info(f"DeepSeek API请求: URL={self.api_base}/chat/completions")
            logger.info(f"请求参数: {json.dumps(payload, ensure_ascii=False)}")
        
        try:
            # 调用API
            response = self.client.post(
                f"{self.api_base}/chat/completions",
                json=payload,
                headers=headers
            )
            
            if response.status_code != 200:
                error_msg = f"API 请求失败: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return ModelOutput(
                    content=f"调用DeepSeek API时出错: {error_msg}",
                    metadata={
                        "error": error_msg,
                        "status_code": response.status_code
                    }
                )
                
            response_data = response.json()
            
            # 日志记录
            if self.debug:
                logger.info(f"DeepSeek API响应: {json.dumps(response_data, ensure_ascii=False)}")
            
            return self._process_response(response_data)
            
        except httpx.TimeoutException as e:
            error_msg = f"API请求超时: {str(e)}"
            logger.error(error_msg)
            return ModelOutput(
                content=f"调用DeepSeek API时超时: {error_msg}",
                metadata={
                    "error": error_msg,
                    "type": "timeout"
                }
            )
        except httpx.RequestError as e:
            error_msg = f"API请求错误: {str(e)}"
            logger.error(error_msg)
            return ModelOutput(
                content=f"调用DeepSeek API时出错: {error_msg}",
                metadata={
                    "error": error_msg,
                    "type": "request_error"
                }
            )
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            logger.error(error_msg)
            return ModelOutput(
                content=f"调用DeepSeek API时发生未知错误: {error_msg}",
                metadata={
                    "error": error_msg,
                    "type": "unknown"
                }
            )
    
    def _process_response(self, response_data: Dict[str, Any]) -> ModelOutput:
        """
        处理模型响应
        
        Args:
            response_data: DeepSeek API返回的响应数据
            
        Returns:
            ModelOutput: 处理后的模型输出
        """
        first_choice = response_data.get("choices", [{}])[0]
        message = first_choice.get("message", {})
        
        output = ModelOutput(
            content=message.get("content"),
            tool_calls=message.get("tool_calls"),
            metadata={
                "model": response_data.get("model"),
                "usage": response_data.get("usage"),
                "finish_reason": first_choice.get("finish_reason"),
            }
        )
        
        return output 