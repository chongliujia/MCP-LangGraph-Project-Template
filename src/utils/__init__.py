"""
工具模块 - 提供各种通用工具函数
"""

import json
import os
from typing import Dict, Any, Optional

from .logger import (
    get_logger, 
    setup_app_logging, 
    with_context, 
    LoggerFactory, 
    JsonFormatter, 
    LoggingContext
)
from .cache import (
    Cache,
    ModelResponseCache,
    cached_model_response,
    model_cache
)

def load_config(file_path: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    加载JSON格式的配置文件
    
    Args:
        file_path: 配置文件路径
        default: 默认配置
        
    Returns:
        Dict[str, Any]: 加载的配置
    """
    config = default or {}
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                loaded = json.load(f)
                config.update(loaded)
        except (json.JSONDecodeError, IOError) as e:
            print(f"加载配置文件失败: {e}")
    else:
        print(f"配置文件不存在: {file_path}")
    
    return config

# 使用新的日志系统
setup_logger = setup_app_logging

__all__ = [
    "load_config", "setup_logger", "get_logger", "with_context",
    "LoggerFactory", "JsonFormatter", "LoggingContext", "setup_app_logging",
    "Cache", "ModelResponseCache", "cached_model_response", "model_cache"
] 