"""
字典配置源 - 使用Python字典作为配置来源
"""

import logging
import copy
from typing import Dict, Any

from .. import ConfigSource

logger = logging.getLogger(__name__)


class DictConfigSource(ConfigSource):
    """
    使用Python字典作为配置来源的配置源
    """
    
    def __init__(
        self,
        data: Dict[str, Any],
        name: str = "dict",
        priority: int = 100,
        readonly: bool = False
    ):
        """
        初始化字典配置源
        
        Args:
            data: 配置数据字典
            name: 配置源名称
            priority: 配置源优先级
            readonly: 是否只读
        """
        # 深拷贝数据以避免外部修改
        super().__init__(
            name=name,
            priority=priority,
            data=copy.deepcopy(data),
            readonly=readonly
        )
        
        self.original_data = copy.deepcopy(data)
    
    def reload(self) -> None:
        """重新加载初始配置"""
        self.data = copy.deepcopy(self.original_data)
        logger.debug(f"重新加载字典配置: {self.name}")
    
    def update(self, data: Dict[str, Any], merge: bool = True) -> None:
        """
        更新配置数据
        
        Args:
            data: 新的配置数据
            merge: 是否合并而不是替换
        """
        if self.readonly:
            logger.warning(f"无法更新只读配置源: {self.name}")
            return
        
        if merge:
            # 合并数据
            new_data = copy.deepcopy(self.data)
            new_data.update(data)
            self.data = new_data
        else:
            # 替换数据
            self.data = copy.deepcopy(data)
        
        logger.debug(f"更新字典配置: {self.name} ({'合并' if merge else '替换'})")
    
    def reset(self) -> None:
        """重置为初始配置"""
        self.reload() 