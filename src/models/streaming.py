"""
流式模型响应支持 - 提供模型流式输出能力
"""

import asyncio
from typing import Dict, Any, Optional, AsyncGenerator, List, Union, Callable

from ..config import get_config
from ..utils import get_logger

# 设置日志记录器
logger = get_logger("streaming")

class StreamingManager:
    """流式响应管理器，处理模型流式输出"""
    
    def __init__(self):
        """初始化流式管理器"""
        # 默认启用状态从配置获取
        self.enabled = get_config("streaming_enabled", False)
        logger.info(f"流式响应管理器初始化: enabled={self.enabled}")
    
    def set_enabled(self, enabled: bool) -> None:
        """
        设置流式输出启用状态
        
        Args:
            enabled: 是否启用
        """
        self.enabled = enabled
        logger.info(f"流式响应状态更新: enabled={enabled}")
    
    def is_enabled(self) -> bool:
        """
        检查流式输出是否启用
        
        Returns:
            bool: 是否启用
        """
        return self.enabled
    
    async def transform_stream(
        self,
        raw_stream: AsyncGenerator[Dict[str, Any], None],
        transform_func: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        转换流式输出
        
        Args:
            raw_stream: 原始流式输出
            transform_func: 转换函数
            
        Yields:
            Dict[str, Any]: 转换后的流式输出项
        """
        async for chunk in raw_stream:
            # 应用转换函数
            if transform_func:
                chunk = transform_func(chunk)
            yield chunk
    
    async def collect_stream(
        self,
        stream: AsyncGenerator[Dict[str, Any], None]
    ) -> Dict[str, Any]:
        """
        收集流式输出为完整响应
        
        Args:
            stream: 流式输出
            
        Returns:
            Dict[str, Any]: 完整响应
        """
        content = ""
        tool_calls = []
        metadata = {}
        
        async for chunk in stream:
            # 提取内容
            if "content" in chunk and chunk["content"]:
                content += chunk["content"]
            
            # 收集工具调用
            if "tool_calls" in chunk and chunk["tool_calls"]:
                tool_calls.extend(chunk["tool_calls"])
            
            # 收集元数据
            if "metadata" in chunk:
                metadata.update(chunk["metadata"])
        
        return {
            "content": content,
            "tool_calls": tool_calls or None,
            "metadata": metadata or None
        }
    
    async def stream_to_callback(
        self,
        stream: AsyncGenerator[Dict[str, Any], None],
        callback: Callable[[Dict[str, Any]], None]
    ) -> Dict[str, Any]:
        """
        将流式输出发送到回调函数，同时收集完整响应
        
        Args:
            stream: 流式输出
            callback: 回调函数
            
        Returns:
            Dict[str, Any]: 完整响应
        """
        content = ""
        tool_calls = []
        metadata = {}
        
        async for chunk in stream:
            # 调用回调
            callback(chunk)
            
            # 提取内容
            if "content" in chunk and chunk["content"]:
                content += chunk["content"]
            
            # 收集工具调用
            if "tool_calls" in chunk and chunk["tool_calls"]:
                tool_calls.extend(chunk["tool_calls"])
            
            # 收集元数据
            if "metadata" in chunk:
                metadata.update(chunk["metadata"])
        
        return {
            "content": content,
            "tool_calls": tool_calls or None,
            "metadata": metadata or None
        }


class StreamBuffer:
    """流缓冲区，用于管理流式输出的状态"""
    
    def __init__(self):
        """初始化流缓冲区"""
        self.buffer = []
        self.complete = False
        self.lock = asyncio.Lock()
        self._event = asyncio.Event()
    
    async def add_chunk(self, chunk: Dict[str, Any]) -> None:
        """
        添加一个数据块到缓冲区
        
        Args:
            chunk: 数据块
        """
        async with self.lock:
            self.buffer.append(chunk)
            self._event.set()  # 通知有新数据
    
    async def mark_complete(self) -> None:
        """标记流已完成"""
        async with self.lock:
            self.complete = True
            self._event.set()  # 通知状态变化
    
    async def get_stream(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        获取流式输出
        
        Yields:
            Dict[str, Any]: 流式输出块
        """
        cursor = 0
        
        while True:
            # 等待新数据或完成状态
            if cursor >= len(self.buffer) and not self.complete:
                await self._event.wait()
                self._event.clear()
            
            # 获取新块
            async with self.lock:
                # 检查是否还有新数据
                if cursor < len(self.buffer):
                    chunk = self.buffer[cursor]
                    cursor += 1
                    yield chunk
                # 如果没有更多数据且已完成，则退出
                elif self.complete:
                    break
    
    async def get_full_content(self) -> Dict[str, Any]:
        """
        获取完整内容（等待流完成）
        
        Returns:
            Dict[str, Any]: 完整内容
        """
        # 等待流完成
        while not self.complete:
            await self._event.wait()
            self._event.clear()
        
        # 合并所有内容
        content = ""
        tool_calls = []
        metadata = {}
        
        for chunk in self.buffer:
            # 提取内容
            if "content" in chunk and chunk["content"]:
                content += chunk["content"]
            
            # 收集工具调用
            if "tool_calls" in chunk and chunk["tool_calls"]:
                tool_calls.extend(chunk["tool_calls"])
            
            # 收集元数据
            if "metadata" in chunk and chunk["metadata"]:
                metadata.update(chunk["metadata"])
        
        return {
            "content": content,
            "tool_calls": tool_calls or None,
            "metadata": metadata or None
        }


# 创建全局流式管理器实例
streaming_manager = StreamingManager() 