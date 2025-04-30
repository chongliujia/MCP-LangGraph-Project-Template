"""
文件配置源 - 从配置文件加载配置
"""

import os
import json
import yaml
import logging
from typing import Dict, Any, Optional, Union, Callable

from .. import ConfigSource

logger = logging.getLogger(__name__)


class FileConfigSource(ConfigSource):
    """
    从文件加载配置的配置源
    """
    
    def __init__(
        self,
        file_path: str,
        name: Optional[str] = None,
        priority: int = 50,
        readonly: bool = False,
        file_format: Optional[str] = None,
        parser: Optional[Callable[[str], Dict[str, Any]]] = None
    ):
        """
        初始化文件配置源
        
        Args:
            file_path: 配置文件路径
            name: 配置源名称，如果为None则使用文件名
            priority: 配置源优先级
            readonly: 是否只读
            file_format: 文件格式，支持'json'、'yaml'，如果为None则根据文件扩展名自动判断
            parser: 自定义解析函数，接收文件内容字符串，返回解析后的配置字典
        """
        self.file_path = os.path.abspath(file_path)
        
        # 如果名称未指定，使用文件名
        if name is None:
            name = os.path.basename(file_path)
        
        # 确定文件格式
        if file_format is None:
            _, ext = os.path.splitext(file_path)
            if ext.lower() in ('.yaml', '.yml'):
                file_format = 'yaml'
            elif ext.lower() == '.json':
                file_format = 'json'
            else:
                file_format = 'unknown'
        
        self.file_format = file_format
        self.parser = parser
        
        # 加载配置
        data = self._load_from_file()
        
        super().__init__(
            name=name,
            priority=priority,
            data=data,
            readonly=readonly
        )
    
    def reload(self) -> None:
        """重新加载配置文件"""
        data = self._load_from_file()
        self.data = data
        logger.debug(f"重新加载配置文件: {self.file_path}")
    
    def save(self) -> None:
        """保存配置到文件"""
        if self.readonly:
            logger.warning(f"无法保存只读配置源: {self.name}")
            return
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            
            content = self._format_config()
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.debug(f"配置已保存到文件: {self.file_path}")
        except Exception as e:
            logger.error(f"保存配置文件时发生错误: {e}")
            raise
    
    def _load_from_file(self) -> Dict[str, Any]:
        """
        从文件加载配置
        
        Returns:
            Dict[str, Any]: 加载的配置
        """
        if not os.path.exists(self.file_path):
            logger.warning(f"配置文件不存在: {self.file_path}")
            return {}
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 使用自定义解析器
            if self.parser:
                return self.parser(content)
            
            # 根据文件格式解析
            if self.file_format == 'json':
                return json.loads(content)
            elif self.file_format == 'yaml':
                return yaml.safe_load(content) or {}
            else:
                logger.warning(f"不支持的文件格式: {self.file_format}")
                return {}
        except Exception as e:
            logger.error(f"加载配置文件时发生错误: {e}")
            return {}
    
    def _format_config(self) -> str:
        """
        将配置格式化为文件内容
        
        Returns:
            str: 格式化后的文件内容
        """
        if self.file_format == 'json':
            return json.dumps(self.data, ensure_ascii=False, indent=2)
        elif self.file_format == 'yaml':
            return yaml.dump(self.data, default_flow_style=False, allow_unicode=True)
        else:
            # 默认使用JSON格式
            return json.dumps(self.data, ensure_ascii=False, indent=2) 