"""
组合内存 - 同时提供消息存储和向量存储功能
"""

import asyncio
from typing import Dict, Any, Optional, List, Union, Callable, Generic, TypeVar
import logging

from . import Message, MemoryItem
from .base_memory import BaseMemory
from .message_memory import MessageMemory
from .vector_memory import VectorMemory

logger = logging.getLogger(__name__)


class CombinedMemory:
    """
    组合内存，同时提供消息存储和向量存储功能
    """
    
    def __init__(
        self,
        message_memory: Optional[MessageMemory] = None,
        vector_memory: Optional[VectorMemory] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化组合内存
        
        Args:
            message_memory: 消息内存实例，如果为None则创建新实例
            vector_memory: 向量内存实例，如果为None则必须在配置中提供embedding_function
            config: 内存配置
        """
        self.config = config or {}
        
        # 创建消息内存
        self.message_memory = message_memory or MessageMemory(self.config.get("message_config"))
        
        # 创建向量内存
        if vector_memory:
            self.vector_memory = vector_memory
        else:
            embedding_function = self.config.get("embedding_function")
            if not embedding_function:
                raise ValueError("必须提供embedding_function或vector_memory实例")
            
            self.vector_memory = VectorMemory(
                embedding_function,
                self.config.get("vector_config")
            )
    
    async def add_message(self, message: Message, store_vector: bool = True) -> Dict[str, str]:
        """
        异步添加消息，可同时存储到消息内存和向量内存
        
        Args:
            message: 消息
            store_vector: 是否同时存储到向量内存
            
        Returns:
            Dict[str, str]: 包含message_id和可选的vector_id的字典
        """
        result = {}
        
        # 添加到消息内存
        message_id = await self.message_memory.add(message)
        result["message_id"] = message_id
        
        # 如果需要，同时添加到向量内存
        if store_vector:
            metadata = {
                "message_id": message_id,
                "role": message.role,
                "timestamp": message.timestamp.isoformat() if message.timestamp else None
            }
            
            # 如果消息有元数据，合并到向量存储的元数据中
            if message.metadata:
                metadata.update(message.metadata)
            
            vector_id = await self.vector_memory.add(message.content, metadata)
            result["vector_id"] = vector_id
        
        return result
    
    def add_message_sync(self, message: Message, store_vector: bool = True) -> Dict[str, str]:
        """
        同步添加消息，可同时存储到消息内存和向量内存
        
        Args:
            message: 消息
            store_vector: 是否同时存储到向量内存
            
        Returns:
            Dict[str, str]: 包含message_id和可选的vector_id的字典
        """
        result = {}
        
        # 添加到消息内存
        message_id = self.message_memory.add_sync(message)
        result["message_id"] = message_id
        
        # 如果需要，同时添加到向量内存
        if store_vector:
            metadata = {
                "message_id": message_id,
                "role": message.role,
                "timestamp": message.timestamp.isoformat() if message.timestamp else None
            }
            
            # 如果消息有元数据，合并到向量存储的元数据中
            if message.metadata:
                metadata.update(message.metadata)
            
            vector_id = self.vector_memory.add_sync(message.content, metadata)
            result["vector_id"] = vector_id
        
        return result
    
    async def add_knowledge(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        异步添加知识（仅向量存储）
        
        Args:
            content: 知识内容
            metadata: 元数据
            
        Returns:
            str: 知识的唯一标识符
        """
        return await self.vector_memory.add(content, metadata)
    
    def add_knowledge_sync(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        同步添加知识（仅向量存储）
        
        Args:
            content: 知识内容
            metadata: 元数据
            
        Returns:
            str: 知识的唯一标识符
        """
        return self.vector_memory.add_sync(content, metadata)
    
    async def get_message(self, message_id: str) -> Optional[Message]:
        """
        异步获取消息
        
        Args:
            message_id: 消息ID
            
        Returns:
            Optional[Message]: 消息，如果不存在则返回None
        """
        item = await self.message_memory.get(message_id)
        if item:
            return item.content
        return None
    
    def get_message_sync(self, message_id: str) -> Optional[Message]:
        """
        同步获取消息
        
        Args:
            message_id: 消息ID
            
        Returns:
            Optional[Message]: 消息，如果不存在则返回None
        """
        item = self.message_memory.get_sync(message_id)
        if item:
            return item.content
        return None
    
    async def get_messages(self, n: Optional[int] = None, roles: Optional[List[str]] = None) -> List[Message]:
        """
        异步获取消息列表
        
        Args:
            n: 要获取的消息数量，如果为None则获取所有消息
            roles: 要获取的消息角色列表，如果为None则获取所有角色的消息
            
        Returns:
            List[Message]: 消息列表，按时间升序排序
        """
        return await self.message_memory.get_messages(n, roles)
    
    def get_messages_sync(self, n: Optional[int] = None, roles: Optional[List[str]] = None) -> List[Message]:
        """
        同步获取消息列表
        
        Args:
            n: 要获取的消息数量，如果为None则获取所有消息
            roles: 要获取的消息角色列表，如果为None则获取所有角色的消息
            
        Returns:
            List[Message]: 消息列表，按时间升序排序
        """
        return self.message_memory.get_messages_sync(n, roles)
    
    async def search_knowledge(self, query: str, **kwargs) -> List[MemoryItem]:
        """
        异步搜索知识库
        
        Args:
            query: 搜索查询文本
            **kwargs: 其他搜索参数
            
        Returns:
            List[MemoryItem]: 搜索结果
        """
        return await self.vector_memory.search(query, **kwargs)
    
    def search_knowledge_sync(self, query: str, **kwargs) -> List[MemoryItem]:
        """
        同步搜索知识库
        
        Args:
            query: 搜索查询文本
            **kwargs: 其他搜索参数
            
        Returns:
            List[MemoryItem]: 搜索结果
        """
        return self.vector_memory.search_sync(query, **kwargs)
    
    async def search_messages(self, query: str, **kwargs) -> List[Message]:
        """
        异步搜索消息
        
        Args:
            query: 搜索查询文本
            **kwargs: 其他搜索参数
            
        Returns:
            List[Message]: 搜索结果
        """
        items = await self.message_memory.search(query, **kwargs)
        return [item.content for item in items]
    
    def search_messages_sync(self, query: str, **kwargs) -> List[Message]:
        """
        同步搜索消息
        
        Args:
            query: 搜索查询文本
            **kwargs: 其他搜索参数
            
        Returns:
            List[Message]: 搜索结果
        """
        items = self.message_memory.search_sync(query, **kwargs)
        return [item.content for item in items]
    
    async def clear(self) -> None:
        """异步清空所有内存"""
        await self.message_memory.clear()
        await self.vector_memory.clear()
    
    def clear_sync(self) -> None:
        """同步清空所有内存"""
        self.message_memory.clear_sync()
        self.vector_memory.clear_sync()
    
    async def clear_messages(self) -> None:
        """异步清空消息内存"""
        await self.message_memory.clear()
    
    def clear_messages_sync(self) -> None:
        """同步清空消息内存"""
        self.message_memory.clear_sync()
    
    async def clear_knowledge(self) -> None:
        """异步清空知识库"""
        await self.vector_memory.clear()
    
    def clear_knowledge_sync(self) -> None:
        """同步清空知识库"""
        self.vector_memory.clear_sync() 