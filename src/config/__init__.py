"""
配置模块 - 负责管理应用程序的配置
"""

from typing import Dict, Any, Optional

from .config_manager import ConfigManager

# 创建默认配置管理器实例
default_config_manager = ConfigManager(config_path="config.json")

def get_config(key: str, default: Any = None) -> Any:
    """
    获取配置值
    
    Args:
        key: 配置键
        default: 默认值
        
    Returns:
        配置值
    """
    return default_config_manager.get(key, default)

def set_config(key: str, value: Any) -> None:
    """
    设置配置值
    
    Args:
        key: 配置键
        value: 配置值
    """
    default_config_manager.set(key, value)

def get_all_config() -> Dict[str, Any]:
    """
    获取所有配置
    
    Returns:
        所有配置项
    """
    return default_config_manager.get_all()

def save_config() -> None:
    """保存配置到文件"""
    default_config_manager.save()

__all__ = ["ConfigManager", "default_config_manager", 
           "get_config", "set_config", "get_all_config", "save_config"] 