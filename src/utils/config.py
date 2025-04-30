"""
配置工具函数 - 提供配置文件加载和保存功能
"""

import os
import json
from typing import Dict, Any, Optional


def load_config(config_path: str, default_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        default_config: 默认配置，当配置文件不存在时使用
        
    Returns:
        Dict[str, Any]: 加载的配置
    """
    # 如果不存在配置文件且提供了默认配置，则创建配置文件
    if not os.path.exists(config_path) and default_config:
        save_config(config_path, default_config)
        return default_config
    
    # 如果不存在配置文件且没有提供默认配置，则返回空字典
    if not os.path.exists(config_path):
        return {}
    
    # 加载配置文件
    with open(config_path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # 如果解析失败且提供了默认配置，则创建配置文件
            if default_config:
                save_config(config_path, default_config)
                return default_config
            return {}


def save_config(config_path: str, config: Dict[str, Any]) -> None:
    """
    保存配置文件
    
    Args:
        config_path: 配置文件路径
        config: 要保存的配置
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
    
    # 保存配置文件
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2) 