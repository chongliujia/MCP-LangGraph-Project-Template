"""
向量存储内存 - 支持向量化存储和语义搜索
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Tuple, Union, Callable
import numpy as np
from datetime import datetime

from . import MemoryItem
from .base_memory import BaseMemory

logger = logging.getLogger(__name__)


class VectorMemory(BaseMemory[str]):
    """
    向量存储内存，支持语义搜索
    """
    
    def __init__(
        self,
        embedding_function: Callable[[str], List[float]],
        config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化向量存储内存
        
        Args:
            embedding_function: 将文本转换为向量的函数
            config: 内存配置，可包含：
                - dimensions: 向量维度
                - similarity_threshold: 相似度阈值，只返回超过阈值的结果
                - max_items: 最大项目数，超过后将删除最旧的项目
        """
        super().__init__(config)
        self.embedding_function = embedding_function
        self.items: Dict[str, MemoryItem] = {}
        self.vectors: Dict[str, np.ndarray] = {}
        
        self.similarity_threshold = self.config.get("similarity_threshold", 0.7)
        self.max_items = self.config.get("max_items")
    
    async def add(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        异步添加文本到向量存储
        
        Args:
            content: 要添加的文本
            metadata: 元数据
            
        Returns:
            str: 内容的唯一标识符
        """
        # 创建内存项
        item = self.create_memory_item(content, metadata)
        
        # 计算向量表示
        embedding = self._get_embedding(content)
        
        # 存储
        self.items[item.id] = item
        self.vectors[item.id] = embedding
        
        # 检查并删除过多的项目
        await self._enforce_limits()
        
        return item.id
    
    def add_sync(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        同步添加文本到向量存储
        
        Args:
            content: 要添加的文本
            metadata: 元数据
            
        Returns:
            str: 内容的唯一标识符
        """
        # 创建内存项
        item = self.create_memory_item(content, metadata)
        
        # 计算向量表示
        embedding = self._get_embedding(content)
        
        # 存储
        self.items[item.id] = item
        self.vectors[item.id] = embedding
        
        # 检查并删除过多的项目
        self._enforce_limits_sync()
        
        return item.id
    
    async def get(self, item_id: str) -> Optional[MemoryItem]:
        """
        异步获取存储中的项目
        
        Args:
            item_id: 项目的唯一标识符
            
        Returns:
            Optional[MemoryItem]: 内存项，如果不存在则返回None
        """
        return self.items.get(item_id)
    
    def get_sync(self, item_id: str) -> Optional[MemoryItem]:
        """
        同步获取存储中的项目
        
        Args:
            item_id: 项目的唯一标识符
            
        Returns:
            Optional[MemoryItem]: 内存项，如果不存在则返回None
        """
        return self.items.get(item_id)
    
    async def update(self, item_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        异步更新存储中的项目
        
        Args:
            item_id: 项目的唯一标识符
            content: 新的文本内容
            metadata: 新的元数据，如果为None则保持不变
            
        Returns:
            bool: 是否更新成功
        """
        item = self.items.get(item_id)
        if not item:
            return False
        
        # 更新内容
        item.content = content
        if metadata is not None:
            item.metadata = metadata
        item.updated_at = datetime.now()
        
        # 重新计算向量
        self.vectors[item_id] = self._get_embedding(content)
        
        return True
    
    def update_sync(self, item_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        同步更新存储中的项目
        
        Args:
            item_id: 项目的唯一标识符
            content: 新的文本内容
            metadata: 新的元数据，如果为None则保持不变
            
        Returns:
            bool: 是否更新成功
        """
        item = self.items.get(item_id)
        if not item:
            return False
        
        # 更新内容
        item.content = content
        if metadata is not None:
            item.metadata = metadata
        item.updated_at = datetime.now()
        
        # 重新计算向量
        self.vectors[item_id] = self._get_embedding(content)
        
        return True
    
    async def delete(self, item_id: str) -> bool:
        """
        异步删除存储中的项目
        
        Args:
            item_id: 项目的唯一标识符
            
        Returns:
            bool: 是否删除成功
        """
        if item_id in self.items:
            del self.items[item_id]
            del self.vectors[item_id]
            return True
        return False
    
    def delete_sync(self, item_id: str) -> bool:
        """
        同步删除存储中的项目
        
        Args:
            item_id: 项目的唯一标识符
            
        Returns:
            bool: 是否删除成功
        """
        if item_id in self.items:
            del self.items[item_id]
            del self.vectors[item_id]
            return True
        return False
    
    async def clear(self) -> None:
        """异步清空存储"""
        self.items.clear()
        self.vectors.clear()
    
    def clear_sync(self) -> None:
        """同步清空存储"""
        self.items.clear()
        self.vectors.clear()
    
    async def search(self, query: Union[str, List[float]], **kwargs) -> List[MemoryItem]:
        """
        异步搜索最相似的项目
        
        Args:
            query: 搜索查询，可以是文本字符串或向量
            **kwargs: 其他搜索参数，包括：
                - n: 返回结果数量限制
                - threshold: 相似度阈值，覆盖默认设置
                - metadata_filter: 元数据过滤函数
                
        Returns:
            List[MemoryItem]: 搜索结果，按相似度降序排序
        """
        n = kwargs.get("n")
        threshold = kwargs.get("threshold", self.similarity_threshold)
        metadata_filter = kwargs.get("metadata_filter")
        
        # 处理空存储的情况
        if not self.vectors:
            return []
        
        # 如果查询是字符串，转换为向量
        if isinstance(query, str):
            query_vector = self._get_embedding(query)
        else:
            query_vector = np.array(query)
        
        # 计算所有向量的相似度
        similarities = []
        for item_id, vector in self.vectors.items():
            item = self.items[item_id]
            
            # 应用元数据过滤
            if metadata_filter and not metadata_filter(item.metadata):
                continue
            
            # 计算余弦相似度
            similarity = self._cosine_similarity(query_vector, vector)
            
            # 应用阈值过滤
            if similarity >= threshold:
                similarities.append((item_id, similarity))
        
        # 按相似度降序排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # 限制数量
        if n is not None:
            similarities = similarities[:n]
        
        # 获取结果
        results = [self.items[item_id] for item_id, _ in similarities]
        
        return results
    
    def search_sync(self, query: Union[str, List[float]], **kwargs) -> List[MemoryItem]:
        """
        同步搜索最相似的项目
        
        Args:
            query: 搜索查询，可以是文本字符串或向量
            **kwargs: 其他搜索参数，包括：
                - n: 返回结果数量限制
                - threshold: 相似度阈值，覆盖默认设置
                - metadata_filter: 元数据过滤函数
                
        Returns:
            List[MemoryItem]: 搜索结果，按相似度降序排序
        """
        n = kwargs.get("n")
        threshold = kwargs.get("threshold", self.similarity_threshold)
        metadata_filter = kwargs.get("metadata_filter")
        
        # 处理空存储的情况
        if not self.vectors:
            return []
        
        # 如果查询是字符串，转换为向量
        if isinstance(query, str):
            query_vector = self._get_embedding(query)
        else:
            query_vector = np.array(query)
        
        # 计算所有向量的相似度
        similarities = []
        for item_id, vector in self.vectors.items():
            item = self.items[item_id]
            
            # 应用元数据过滤
            if metadata_filter and not metadata_filter(item.metadata):
                continue
            
            # 计算余弦相似度
            similarity = self._cosine_similarity(query_vector, vector)
            
            # 应用阈值过滤
            if similarity >= threshold:
                similarities.append((item_id, similarity))
        
        # 按相似度降序排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # 限制数量
        if n is not None:
            similarities = similarities[:n]
        
        # 获取结果
        results = [self.items[item_id] for item_id, _ in similarities]
        
        return results
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """
        获取文本的向量表示
        
        Args:
            text: 文本
            
        Returns:
            np.ndarray: 向量表示
        """
        try:
            embedding = self.embedding_function(text)
            return np.array(embedding)
        except Exception as e:
            logger.error(f"获取文本嵌入向量时发生错误: {e}")
            # 返回零向量作为回退
            dimensions = self.config.get("dimensions", 1536)
            return np.zeros(dimensions)
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        计算两个向量的余弦相似度
        
        Args:
            a: 向量a
            b: 向量b
            
        Returns:
            float: 余弦相似度，范围[0,1]
        """
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0
        
        return np.dot(a, b) / (norm_a * norm_b)
    
    async def _enforce_limits(self) -> None:
        """异步强制执行限制"""
        # 如果设置了最大项目数，则删除多余的项目
        if self.max_items and len(self.items) > self.max_items:
            # 按创建时间排序
            sorted_items = sorted(
                self.items.items(),
                key=lambda x: x[1].created_at
            )
            
            # 计算要删除的数量
            count_to_remove = len(self.items) - self.max_items
            
            # 删除最旧的项目
            for i in range(count_to_remove):
                item_id, _ = sorted_items[i]
                del self.items[item_id]
                del self.vectors[item_id]
            
            logger.debug(f"删除了 {count_to_remove} 个旧项目以保持在限制范围内")
    
    def _enforce_limits_sync(self) -> None:
        """同步强制执行限制"""
        # 如果设置了最大项目数，则删除多余的项目
        if self.max_items and len(self.items) > self.max_items:
            # 按创建时间排序
            sorted_items = sorted(
                self.items.items(),
                key=lambda x: x[1].created_at
            )
            
            # 计算要删除的数量
            count_to_remove = len(self.items) - self.max_items
            
            # 删除最旧的项目
            for i in range(count_to_remove):
                item_id, _ = sorted_items[i]
                del self.items[item_id]
                del self.vectors[item_id]
            
            logger.debug(f"删除了 {count_to_remove} 个旧项目以保持在限制范围内") 