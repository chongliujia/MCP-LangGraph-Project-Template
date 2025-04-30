"""
基础内存抽象类 - 定义内存管理的接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union, Generic, TypeVar
import uuid
import time
from datetime import datetime

from . import MemoryItem

T = TypeVar('T')


class BaseMemory(Generic[T], ABC):
    """
    内存管理的抽象基类，定义了内存管理需要实现的接口
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化内存
        
        Args:
            config: 内存配置
        """
        self.config = config or {}
    
    @abstractmethod
    async def add(self, content: T, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        异步添加内容到内存
        
        Args:
            content: 要添加的内容
            metadata: 元数据
            
        Returns:
            str: 内容的唯一标识符
        """
        pass
    
    @abstractmethod
    def add_sync(self, content: T, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        同步添加内容到内存
        
        Args:
            content: 要添加的内容
            metadata: 元数据
            
        Returns:
            str: 内容的唯一标识符
        """
        pass
    
    @abstractmethod
    async def get(self, item_id: str) -> Optional[MemoryItem]:
        """
        异步获取内存中的内容
        
        Args:
            item_id: 内容的唯一标识符
            
        Returns:
            Optional[MemoryItem]: 内存项，如果不存在则返回None
        """
        pass
    
    @abstractmethod
    def get_sync(self, item_id: str) -> Optional[MemoryItem]:
        """
        同步获取内存中的内容
        
        Args:
            item_id: 内容的唯一标识符
            
        Returns:
            Optional[MemoryItem]: 内存项，如果不存在则返回None
        """
        pass
    
    @abstractmethod
    async def update(self, item_id: str, content: T, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        异步更新内存中的内容
        
        Args:
            item_id: 内容的唯一标识符
            content: 新的内容
            metadata: 新的元数据，如果为None则保持不变
            
        Returns:
            bool: 是否更新成功
        """
        pass
    
    @abstractmethod
    def update_sync(self, item_id: str, content: T, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        同步更新内存中的内容
        
        Args:
            item_id: 内容的唯一标识符
            content: 新的内容
            metadata: 新的元数据，如果为None则保持不变
            
        Returns:
            bool: 是否更新成功
        """
        pass
    
    @abstractmethod
    async def delete(self, item_id: str) -> bool:
        """
        异步删除内存中的内容
        
        Args:
            item_id: 内容的唯一标识符
            
        Returns:
            bool: 是否删除成功
        """
        pass
    
    @abstractmethod
    def delete_sync(self, item_id: str) -> bool:
        """
        同步删除内存中的内容
        
        Args:
            item_id: 内容的唯一标识符
            
        Returns:
            bool: 是否删除成功
        """
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """异步清空内存"""
        pass
    
    @abstractmethod
    def clear_sync(self) -> None:
        """同步清空内存"""
        pass
    
    @abstractmethod
    async def search(self, query: Any, **kwargs) -> List[MemoryItem]:
        """
        异步搜索内存
        
        Args:
            query: 搜索查询
            **kwargs: 其他搜索参数
            
        Returns:
            List[MemoryItem]: 搜索结果
        """
        pass
    
    @abstractmethod
    def search_sync(self, query: Any, **kwargs) -> List[MemoryItem]:
        """
        同步搜索内存
        
        Args:
            query: 搜索查询
            **kwargs: 其他搜索参数
            
        Returns:
            List[MemoryItem]: 搜索结果
        """
        pass
    
    def generate_id(self) -> str:
        """
        生成唯一标识符
        
        Returns:
            str: 唯一标识符
        """
        return str(uuid.uuid4())
    
    def create_memory_item(self, content: T, metadata: Optional[Dict[str, Any]] = None) -> MemoryItem:
        """
        创建内存项
        
        Args:
            content: 内容
            metadata: 元数据
            
        Returns:
            MemoryItem: 内存项
        """
        now = datetime.now()
        return MemoryItem(
            id=self.generate_id(),
            content=content,
            metadata=metadata or {},
            created_at=now,
            updated_at=now
        ) 