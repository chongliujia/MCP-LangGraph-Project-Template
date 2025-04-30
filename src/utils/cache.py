"""
缓存工具 - 提供缓存功能以优化性能
"""

import time
import json
import hashlib
import os
from typing import Dict, Any, Optional, Callable, Tuple, List, Union, TypeVar, Generic
from functools import wraps
from datetime import datetime, timedelta
import threading
import pickle

from ..config import get_config
from .logger import get_logger

# 设置日志记录器
logger = get_logger("cache")

# 定义泛型类型变量
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

class CacheItem(Generic[V]):
    """缓存项，保存值和元数据"""
    
    def __init__(self, value: V, expire_at: Optional[float] = None):
        """
        初始化缓存项
        
        Args:
            value: 缓存值
            expire_at: 过期时间戳
        """
        self.value = value
        self.expire_at = expire_at
        self.created_at = time.time()
        self.last_accessed = self.created_at
        self.access_count = 0
    
    def is_expired(self) -> bool:
        """
        检查缓存项是否过期
        
        Returns:
            bool: 是否过期
        """
        if self.expire_at is None:
            return False
        return time.time() > self.expire_at
    
    def access(self) -> V:
        """
        访问缓存项并更新访问计数和时间
        
        Returns:
            缓存值
        """
        self.last_accessed = time.time()
        self.access_count += 1
        return self.value


class Cache(Generic[K, V]):
    """通用缓存实现"""
    
    def __init__(
        self,
        max_size: int = 1000,
        ttl: Optional[float] = None,
        eviction_policy: str = "lru",
        name: str = "default"
    ):
        """
        初始化缓存
        
        Args:
            max_size: 最大缓存条目数
            ttl: 缓存项生存时间（秒）
            eviction_policy: 清理策略 (lru, lfu, fifo)
            name: 缓存名称
        """
        self.max_size = max_size
        self.ttl = ttl
        self.eviction_policy = eviction_policy.lower()
        self.name = name
        self._cache: Dict[K, CacheItem[V]] = {}
        self._lock = threading.RLock()
        self._hit_count = 0
        self._miss_count = 0
        self._insert_count = 0
        self._eviction_count = 0
        self._expired_count = 0
        
        logger.debug(f"初始化缓存 {name}: max_size={max_size}, ttl={ttl}, policy={eviction_policy}")
    
    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """
        获取缓存项
        
        Args:
            key: 键
            default: 默认值
            
        Returns:
            缓存值或默认值
        """
        with self._lock:
            item = self._cache.get(key)
            
            # 如果项不存在或已过期
            if item is None or item.is_expired():
                if item is not None and item.is_expired():
                    # 删除过期项
                    del self._cache[key]
                    self._expired_count += 1
                    logger.debug(f"缓存项过期: {key}")
                
                self._miss_count += 1
                return default
            
            # 缓存命中
            self._hit_count += 1
            return item.access()
    
    def set(self, key: K, value: V, ttl: Optional[float] = None) -> None:
        """
        设置缓存项
        
        Args:
            key: 键
            value: 值
            ttl: 此项的生存时间（秒），如果不指定则使用默认值
        """
        with self._lock:
            # 如果达到最大大小，需要清除一个项
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict()
            
            # 计算过期时间
            expire_at = None
            if ttl is not None:
                expire_at = time.time() + ttl
            elif self.ttl is not None:
                expire_at = time.time() + self.ttl
            
            # 创建并存储缓存项
            self._cache[key] = CacheItem(value, expire_at)
            self._insert_count += 1
            
            logger.debug(f"设置缓存项: {key}, ttl={ttl}")
    
    def delete(self, key: K) -> bool:
        """
        删除缓存项
        
        Args:
            key: 键
            
        Returns:
            bool: 是否删除成功
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"删除缓存项: {key}")
                return True
            return False
    
    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            logger.debug(f"清空缓存: {self.name}")
    
    def _evict(self) -> None:
        """根据策略清除一个缓存项"""
        if not self._cache:
            return
        
        target_key = None
        
        if self.eviction_policy == "lru":  # 最近最少使用
            target_key = min(self._cache, key=lambda k: self._cache[k].last_accessed)
        elif self.eviction_policy == "lfu":  # 最不经常使用
            target_key = min(self._cache, key=lambda k: self._cache[k].access_count)
        elif self.eviction_policy == "fifo":  # 先进先出
            target_key = min(self._cache, key=lambda k: self._cache[k].created_at)
        else:  # 默认LRU
            target_key = min(self._cache, key=lambda k: self._cache[k].last_accessed)
        
        if target_key is not None:
            del self._cache[target_key]
            self._eviction_count += 1
            logger.debug(f"清除缓存项: {target_key}")
    
    def cleanup_expired(self) -> int:
        """
        清理过期项
        
        Returns:
            int: 清理的项数量
        """
        with self._lock:
            expired_keys = [k for k, v in self._cache.items() if v.is_expired()]
            for key in expired_keys:
                del self._cache[key]
                self._expired_count += 1
            
            if expired_keys:
                logger.debug(f"清理过期项: {len(expired_keys)}个")
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            Dict[str, Any]: 缓存统计
        """
        with self._lock:
            total_requests = self._hit_count + self._miss_count
            hit_rate = self._hit_count / total_requests if total_requests > 0 else 0
            
            return {
                "name": self.name,
                "size": len(self._cache),
                "max_size": self.max_size,
                "ttl": self.ttl,
                "eviction_policy": self.eviction_policy,
                "hits": self._hit_count,
                "misses": self._miss_count,
                "hit_rate": hit_rate,
                "inserts": self._insert_count,
                "evictions": self._eviction_count,
                "expirations": self._expired_count
            }


class ModelResponseCache:
    """模型响应缓存"""
    
    def __init__(
        self,
        cache_dir: Optional[str] = None,
        max_memory_items: int = 1000,
        memory_ttl: float = 3600,  # 1小时
        disk_ttl: float = 86400 * 7,  # 7天
        use_disk: bool = True
    ):
        """
        初始化模型响应缓存
        
        Args:
            cache_dir: 缓存目录
            max_memory_items: 内存缓存最大条目数
            memory_ttl: 内存缓存生存时间（秒）
            disk_ttl: 磁盘缓存生存时间（秒）
            use_disk: 是否使用磁盘缓存
        """
        self.use_disk = use_disk
        self.disk_ttl = disk_ttl
        
        # 创建内存缓存
        self.memory_cache = Cache[str, Dict](
            max_size=max_memory_items,
            ttl=memory_ttl,
            eviction_policy="lru",
            name="model_response_memory"
        )
        
        # 设置磁盘缓存目录
        if cache_dir is None:
            app_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            cache_dir = os.path.join(app_root, 'cache', 'models')
        
        self.cache_dir = cache_dir
        if use_disk and not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
            logger.info(f"创建缓存目录: {cache_dir}")
    
    def _compute_key(self, provider: str, model: str, messages: List[Dict], **kwargs) -> str:
        """
        计算缓存键
        
        Args:
            provider: 模型提供者
            model: 模型名称
            messages: 消息列表
            **kwargs: 其他参数
            
        Returns:
            str: 缓存键
        """
        # 提取并规范化系统提示
        system_prompt = kwargs.get("system_prompt")
        
        # 构建包含关键信息的字典
        key_data = {
            "provider": provider,
            "model": model,
            "messages": messages,
            "system_prompt": system_prompt,
        }
        
        # 添加可能影响输出的其他参数
        for param in ["temperature", "top_p", "top_k", "max_tokens"]:
            if param in kwargs and kwargs[param] is not None:
                key_data[param] = kwargs[param]
        
        # 序列化并哈希
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode('utf-8')).hexdigest()
    
    def get(self, provider: str, model: str, messages: List[Dict], **kwargs) -> Optional[Dict[str, Any]]:
        """
        获取缓存的响应
        
        Args:
            provider: 模型提供者
            model: 模型名称
            messages: 消息列表
            **kwargs: 其他参数
            
        Returns:
            Optional[Dict[str, Any]]: 缓存的响应或None
        """
        # 如果禁用缓存则直接返回None
        if not get_config("cache_enabled", False):
            return None
        
        # 对于非确定性请求不使用缓存
        if kwargs.get("temperature", 0) > 0.0:
            return None
        
        # 计算缓存键
        cache_key = self._compute_key(provider, model, messages, **kwargs)
        
        # 先检查内存缓存
        result = self.memory_cache.get(cache_key)
        if result is not None:
            logger.debug(f"内存缓存命中: {cache_key}")
            return result
        
        # 检查磁盘缓存
        if self.use_disk:
            disk_result = self._load_from_disk(cache_key)
            if disk_result is not None:
                # 将磁盘结果也放入内存缓存
                self.memory_cache.set(cache_key, disk_result)
                logger.debug(f"磁盘缓存命中: {cache_key}")
                return disk_result
        
        logger.debug(f"缓存未命中: {cache_key}")
        return None
    
    def set(self, provider: str, model: str, messages: List[Dict], response: Dict[str, Any], **kwargs) -> None:
        """
        缓存响应
        
        Args:
            provider: 模型提供者
            model: 模型名称
            messages: 消息列表
            response: 模型响应
            **kwargs: 其他参数
        """
        # 如果禁用缓存则不操作
        if not get_config("cache_enabled", False):
            return
        
        # 对于非确定性请求不缓存
        if kwargs.get("temperature", 0) > 0.0:
            return
        
        # 计算缓存键
        cache_key = self._compute_key(provider, model, messages, **kwargs)
        
        # 缓存到内存
        self.memory_cache.set(cache_key, response)
        
        # 缓存到磁盘
        if self.use_disk:
            self._save_to_disk(cache_key, response)
            
        logger.debug(f"缓存响应: {cache_key}")
    
    def _get_cache_path(self, key: str) -> str:
        """
        获取缓存文件路径
        
        Args:
            key: 缓存键
            
        Returns:
            str: 缓存文件路径
        """
        return os.path.join(self.cache_dir, f"{key}.pkl")
    
    def _save_to_disk(self, key: str, data: Dict[str, Any]) -> bool:
        """
        保存数据到磁盘
        
        Args:
            key: 缓存键
            data: 要缓存的数据
            
        Returns:
            bool: 是否成功保存
        """
        try:
            cache_path = self._get_cache_path(key)
            
            # 添加元数据
            cache_data = {
                "data": data,
                "created_at": time.time(),
                "expires_at": time.time() + self.disk_ttl
            }
            
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
            
            return True
        except Exception as e:
            logger.error(f"保存缓存到磁盘失败: {str(e)}")
            return False
    
    def _load_from_disk(self, key: str) -> Optional[Dict[str, Any]]:
        """
        从磁盘加载数据
        
        Args:
            key: 缓存键
            
        Returns:
            Optional[Dict[str, Any]]: 加载的数据或None
        """
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                cache_data = pickle.load(f)
            
            # 检查是否过期
            if time.time() > cache_data.get("expires_at", 0):
                # 删除过期文件
                os.remove(cache_path)
                logger.debug(f"删除过期缓存文件: {cache_path}")
                return None
            
            return cache_data.get("data")
        except Exception as e:
            logger.error(f"从磁盘加载缓存失败: {str(e)}")
            return None
    
    def cleanup(self) -> Tuple[int, int]:
        """
        清理过期缓存
        
        Returns:
            Tuple[int, int]: (清理的内存项数量, 清理的磁盘项数量)
        """
        # 清理内存缓存
        memory_cleaned = self.memory_cache.cleanup_expired()
        
        # 清理磁盘缓存
        disk_cleaned = 0
        if self.use_disk and os.path.exists(self.cache_dir):
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.pkl'):
                    cache_path = os.path.join(self.cache_dir, filename)
                    try:
                        with open(cache_path, 'rb') as f:
                            cache_data = pickle.load(f)
                        
                        # 检查是否过期
                        if time.time() > cache_data.get("expires_at", 0):
                            os.remove(cache_path)
                            disk_cleaned += 1
                    except Exception:
                        # 如果文件损坏，删除它
                        os.remove(cache_path)
                        disk_cleaned += 1
        
        logger.info(f"缓存清理完成: 内存={memory_cleaned}项, 磁盘={disk_cleaned}项")
        return memory_cleaned, disk_cleaned
    
    def clear(self) -> None:
        """清空所有缓存"""
        # 清空内存缓存
        self.memory_cache.clear()
        
        # 清空磁盘缓存
        if self.use_disk and os.path.exists(self.cache_dir):
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.pkl'):
                    os.remove(os.path.join(self.cache_dir, filename))
        
        logger.info("已清空所有缓存")


# 用于模型响应的缓存装饰器
def cached_model_response(func: Callable) -> Callable:
    """
    缓存模型响应的装饰器
    
    Args:
        func: 要装饰的函数
        
    Returns:
        Callable: 装饰后的函数
    """
    cache = ModelResponseCache()
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 提取Provider和模型名称
        self = args[0]  # BaseModelLayer的实例
        input_data = args[1]  # ModelInput
        
        provider = getattr(self, "provider", None) or self.__class__.__name__.lower().replace("model", "")
        model = input_data.model
        messages = input_data.messages
        
        # 其他可能影响输出的参数
        extra_args = {
            "system_prompt": input_data.system_prompt,
            "temperature": input_data.temperature,
            "max_tokens": input_data.max_tokens
        }
        
        # 检查缓存
        cached_result = cache.get(provider, model, messages, **extra_args)
        if cached_result is not None:
            # 从缓存构建响应
            from ..models import ModelOutput
            return ModelOutput(**cached_result)
        
        # 调用原始函数
        result = await func(*args, **kwargs)
        
        # 缓存结果
        cache.set(provider, model, messages, result.model_dump(), **extra_args)
        
        return result
    
    return wrapper

# 创建全局缓存实例
model_cache = ModelResponseCache() 