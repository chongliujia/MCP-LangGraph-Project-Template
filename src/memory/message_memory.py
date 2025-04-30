"""
消息内存 - 存储和管理对话消息
"""

import asyncio
from typing import Dict, Any, Optional, List, Tuple, cast
from datetime import datetime
import logging

from . import Message, MemoryItem
from .base_memory import BaseMemory

logger = logging.getLogger(__name__)


class MessageMemory(BaseMemory[Message]):
    """
    用于存储和管理对话消息的内存
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化消息内存
        
        Args:
            config: 内存配置，可包含：
                - max_messages: 最大消息数，超过后将删除最旧的消息
                - ttl: 消息生存时间（秒），超过后将被忽略
        """
        super().__init__(config)
        self.messages: Dict[str, MemoryItem] = {}
        self.max_messages = self.config.get("max_messages")
        self.ttl = self.config.get("ttl")  # 生存时间（秒）
    
    async def add(self, content: Message, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        异步添加消息到内存
        
        Args:
            content: 要添加的消息
            metadata: 元数据
            
        Returns:
            str: 消息的唯一标识符
        """
        item = self.create_memory_item(content, metadata)
        self.messages[item.id] = item
        
        # 检查并删除过多的消息
        await self._enforce_limits()
        
        return item.id
    
    def add_sync(self, content: Message, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        同步添加消息到内存
        
        Args:
            content: 要添加的消息
            metadata: 元数据
            
        Returns:
            str: 消息的唯一标识符
        """
        item = self.create_memory_item(content, metadata)
        self.messages[item.id] = item
        
        # 检查并删除过多的消息
        self._enforce_limits_sync()
        
        return item.id
    
    async def get(self, item_id: str) -> Optional[MemoryItem]:
        """
        异步获取内存中的消息
        
        Args:
            item_id: 消息的唯一标识符
            
        Returns:
            Optional[MemoryItem]: 内存项，如果不存在则返回None
        """
        item = self.messages.get(item_id)
        
        # 检查TTL
        if item and self.ttl:
            age = (datetime.now() - item.created_at).total_seconds()
            if age > self.ttl:
                logger.debug(f"消息已过期: {item_id}")
                return None
        
        return item
    
    def get_sync(self, item_id: str) -> Optional[MemoryItem]:
        """
        同步获取内存中的消息
        
        Args:
            item_id: 消息的唯一标识符
            
        Returns:
            Optional[MemoryItem]: 内存项，如果不存在则返回None
        """
        item = self.messages.get(item_id)
        
        # 检查TTL
        if item and self.ttl:
            age = (datetime.now() - item.created_at).total_seconds()
            if age > self.ttl:
                logger.debug(f"消息已过期: {item_id}")
                return None
        
        return item
    
    async def update(self, item_id: str, content: Message, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        异步更新内存中的消息
        
        Args:
            item_id: 消息的唯一标识符
            content: 新的消息
            metadata: 新的元数据，如果为None则保持不变
            
        Returns:
            bool: 是否更新成功
        """
        item = self.messages.get(item_id)
        if not item:
            return False
        
        item.content = content
        if metadata is not None:
            item.metadata = metadata
        item.updated_at = datetime.now()
        
        return True
    
    def update_sync(self, item_id: str, content: Message, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        同步更新内存中的消息
        
        Args:
            item_id: 消息的唯一标识符
            content: 新的消息
            metadata: 新的元数据，如果为None则保持不变
            
        Returns:
            bool: 是否更新成功
        """
        item = self.messages.get(item_id)
        if not item:
            return False
        
        item.content = content
        if metadata is not None:
            item.metadata = metadata
        item.updated_at = datetime.now()
        
        return True
    
    async def delete(self, item_id: str) -> bool:
        """
        异步删除内存中的消息
        
        Args:
            item_id: 消息的唯一标识符
            
        Returns:
            bool: 是否删除成功
        """
        if item_id in self.messages:
            del self.messages[item_id]
            return True
        return False
    
    def delete_sync(self, item_id: str) -> bool:
        """
        同步删除内存中的消息
        
        Args:
            item_id: 消息的唯一标识符
            
        Returns:
            bool: 是否删除成功
        """
        if item_id in self.messages:
            del self.messages[item_id]
            return True
        return False
    
    async def clear(self) -> None:
        """异步清空内存"""
        self.messages.clear()
    
    def clear_sync(self) -> None:
        """同步清空内存"""
        self.messages.clear()
    
    async def get_messages(self, n: Optional[int] = None, roles: Optional[List[str]] = None) -> List[Message]:
        """
        异步获取消息列表
        
        Args:
            n: 要获取的消息数量，如果为None则获取所有消息
            roles: 要获取的消息角色列表，如果为None则获取所有角色的消息
            
        Returns:
            List[Message]: 消息列表，按时间升序排序
        """
        # 获取有效消息（考虑TTL）
        valid_messages = []
        for item in self.messages.values():
            if self.ttl:
                age = (datetime.now() - item.created_at).total_seconds()
                if age > self.ttl:
                    continue
            
            message = cast(Message, item.content)
            if roles and message.role not in roles:
                continue
            
            valid_messages.append((item.created_at, item.id, message))
        
        # 按时间排序
        valid_messages.sort()
        
        # 截取所需数量
        if n is not None:
            valid_messages = valid_messages[-n:]
        
        # 提取消息
        return [message for _, _, message in valid_messages]
    
    def get_messages_sync(self, n: Optional[int] = None, roles: Optional[List[str]] = None) -> List[Message]:
        """
        同步获取消息列表
        
        Args:
            n: 要获取的消息数量，如果为None则获取所有消息
            roles: 要获取的消息角色列表，如果为None则获取所有角色的消息
            
        Returns:
            List[Message]: 消息列表，按时间升序排序
        """
        # 获取有效消息（考虑TTL）
        valid_messages = []
        for item in self.messages.values():
            if self.ttl:
                age = (datetime.now() - item.created_at).total_seconds()
                if age > self.ttl:
                    continue
            
            message = cast(Message, item.content)
            if roles and message.role not in roles:
                continue
            
            valid_messages.append((item.created_at, item.id, message))
        
        # 按时间排序
        valid_messages.sort()
        
        # 截取所需数量
        if n is not None:
            valid_messages = valid_messages[-n:]
        
        # 提取消息
        return [message for _, _, message in valid_messages]
    
    async def search(self, query: str, **kwargs) -> List[MemoryItem]:
        """
        异步搜索消息
        
        Args:
            query: 搜索查询字符串
            **kwargs: 其他搜索参数，包括：
                - n: 返回结果数量限制
                - roles: 角色过滤
                
        Returns:
            List[MemoryItem]: 搜索结果
        """
        n = kwargs.get("n")
        roles = kwargs.get("roles")
        case_sensitive = kwargs.get("case_sensitive", False)
        
        # 简单关键词搜索
        results = []
        
        for item in self.messages.values():
            # 检查TTL
            if self.ttl:
                age = (datetime.now() - item.created_at).total_seconds()
                if age > self.ttl:
                    continue
            
            message = cast(Message, item.content)
            
            # 检查角色
            if roles and message.role not in roles:
                continue
            
            # 检查内容
            if case_sensitive:
                if query in message.content:
                    results.append(item)
            else:
                if query.lower() in message.content.lower():
                    results.append(item)
        
        # 按时间排序
        results.sort(key=lambda x: x.created_at)
        
        # 限制数量
        if n is not None:
            results = results[:n]
        
        return results
    
    def search_sync(self, query: str, **kwargs) -> List[MemoryItem]:
        """
        同步搜索消息
        
        Args:
            query: 搜索查询字符串
            **kwargs: 其他搜索参数，包括：
                - n: 返回结果数量限制
                - roles: 角色过滤
                
        Returns:
            List[MemoryItem]: 搜索结果
        """
        n = kwargs.get("n")
        roles = kwargs.get("roles")
        case_sensitive = kwargs.get("case_sensitive", False)
        
        # 简单关键词搜索
        results = []
        
        for item in self.messages.values():
            # 检查TTL
            if self.ttl:
                age = (datetime.now() - item.created_at).total_seconds()
                if age > self.ttl:
                    continue
            
            message = cast(Message, item.content)
            
            # 检查角色
            if roles and message.role not in roles:
                continue
            
            # 检查内容
            if case_sensitive:
                if query in message.content:
                    results.append(item)
            else:
                if query.lower() in message.content.lower():
                    results.append(item)
        
        # 按时间排序
        results.sort(key=lambda x: x.created_at)
        
        # 限制数量
        if n is not None:
            results = results[:n]
        
        return results
    
    async def _enforce_limits(self) -> None:
        """异步强制执行限制"""
        # 如果设置了最大消息数，则删除多余的消息
        if self.max_messages and len(self.messages) > self.max_messages:
            # 按创建时间排序
            sorted_items = sorted(
                self.messages.items(),
                key=lambda x: x[1].created_at
            )
            
            # 计算要删除的数量
            count_to_remove = len(self.messages) - self.max_messages
            
            # 删除最旧的消息
            for i in range(count_to_remove):
                item_id, _ = sorted_items[i]
                del self.messages[item_id]
            
            logger.debug(f"删除了 {count_to_remove} 条旧消息以保持在限制范围内")
    
    def _enforce_limits_sync(self) -> None:
        """同步强制执行限制"""
        # 如果设置了最大消息数，则删除多余的消息
        if self.max_messages and len(self.messages) > self.max_messages:
            # 按创建时间排序
            sorted_items = sorted(
                self.messages.items(),
                key=lambda x: x[1].created_at
            )
            
            # 计算要删除的数量
            count_to_remove = len(self.messages) - self.max_messages
            
            # 删除最旧的消息
            for i in range(count_to_remove):
                item_id, _ = sorted_items[i]
                del self.messages[item_id]
            
            logger.debug(f"删除了 {count_to_remove} 条旧消息以保持在限制范围内") 