"""
环境变量配置源 - 从环境变量加载配置
"""

import os
import logging
from typing import Dict, Any, Optional, List, Set

from .. import ConfigSource

logger = logging.getLogger(__name__)


class EnvConfigSource(ConfigSource):
    """
    从环境变量加载配置的配置源
    """
    
    def __init__(
        self,
        name: str = "env",
        priority: int = 10,
        prefix: str = "",
        lowercase_keys: bool = True,
        include_keys: Optional[List[str]] = None,
        exclude_keys: Optional[List[str]] = None
    ):
        """
        初始化环境变量配置源
        
        Args:
            name: 配置源名称
            priority: 配置源优先级
            prefix: 环境变量前缀，只加载以该前缀开头的环境变量
            lowercase_keys: 是否将键名转为小写
            include_keys: 只包含的键名列表（不包含前缀），如果为None则包含所有
            exclude_keys: 排除的键名列表（不包含前缀）
        """
        data = self._load_from_env(prefix, lowercase_keys, include_keys, exclude_keys)
        
        super().__init__(
            name=name,
            priority=priority,
            data=data,
            readonly=True  # 环境变量配置源默认为只读
        )
        
        self.prefix = prefix
        self.lowercase_keys = lowercase_keys
        self.include_keys = include_keys
        self.exclude_keys = exclude_keys
    
    def reload(self) -> None:
        """重新加载环境变量配置"""
        data = self._load_from_env(
            self.prefix,
            self.lowercase_keys,
            self.include_keys,
            self.exclude_keys
        )
        self.data = data
        logger.debug(f"重新加载环境变量配置: {self.name}")
    
    def _load_from_env(
        self,
        prefix: str,
        lowercase_keys: bool,
        include_keys: Optional[List[str]],
        exclude_keys: Optional[List[str]]
    ) -> Dict[str, Any]:
        """
        从环境变量加载配置
        
        Args:
            prefix: 环境变量前缀
            lowercase_keys: 是否将键名转为小写
            include_keys: 只包含的键名列表（不包含前缀）
            exclude_keys: 排除的键名列表（不包含前缀）
            
        Returns:
            Dict[str, Any]: 加载的配置
        """
        config = {}
        
        include_set = set(include_keys) if include_keys else None
        exclude_set = set(exclude_keys) if exclude_keys else set()
        
        for key, value in os.environ.items():
            if prefix and not key.startswith(prefix):
                continue
            
            # 移除前缀
            config_key = key[len(prefix):] if prefix else key
            
            # 检查是否在包含列表中
            if include_set and config_key not in include_set:
                continue
            
            # 检查是否在排除列表中
            if config_key in exclude_set:
                continue
            
            # 转换为小写
            if lowercase_keys:
                config_key = config_key.lower()
            
            # 尝试转换值类型
            config[config_key] = self._convert_value(value)
        
        logger.debug(f"从环境变量加载了 {len(config)} 项配置")
        return config
    
    def _convert_value(self, value: str) -> Any:
        """
        尝试转换值的类型
        
        Args:
            value: 原始字符串值
            
        Returns:
            Any: 转换后的值
        """
        # 尝试转换为布尔值
        if value.lower() in ("true", "yes", "1"):
            return True
        if value.lower() in ("false", "no", "0"):
            return False
        
        # 尝试转换为数字
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            pass
        
        # 保持为字符串
        return value 