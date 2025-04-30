"""
日志工具 - 提供增强的日志记录功能
"""

import os
import logging
import json
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from typing import Dict, Any, Optional, Union, List

from ..config import get_config

# 日志级别映射
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

# 日志格式定义
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
JSON_FORMAT = {
    "timestamp": "%(asctime)s",
    "level": "%(levelname)s",
    "name": "%(name)s",
    "message": "%(message)s",
    "file": "%(pathname)s",
    "line": "%(lineno)d",
    "function": "%(funcName)s",
    "thread": "%(threadName)s",
    "process": "%(processName)s"
}

class JsonFormatter(logging.Formatter):
    """JSON格式化器，将日志记录为JSON格式"""
    
    def __init__(self, fmt_dict: Optional[Dict[str, str]] = None):
        """
        初始化JSON格式化器
        
        Args:
            fmt_dict: 格式字典
        """
        self.fmt_dict = fmt_dict or JSON_FORMAT
        super().__init__()
    
    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录
        
        Args:
            record: 日志记录
            
        Returns:
            str: 格式化后的日志文本
        """
        log_dict = {}
        
        # 复制format dict中的所有键
        for key, value in self.fmt_dict.items():
            try:
                log_dict[key] = value % record.__dict__
            except (KeyError, TypeError):
                log_dict[key] = value
        
        # 添加异常信息
        if record.exc_info:
            log_dict["exc_info"] = self.formatException(record.exc_info)
        
        # 添加额外字段
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_dict.update(record.extra)
        
        return json.dumps(log_dict, ensure_ascii=False)

class LoggerFactory:
    """日志工厂，用于创建和配置日志记录器"""
    
    @staticmethod
    def create_logger(
        name: str,
        level: Optional[Union[str, int]] = None,
        log_file: Optional[str] = None,
        log_format: str = DEFAULT_FORMAT,
        json_format: bool = False,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        use_console: bool = True,
        propagate: bool = False
    ) -> logging.Logger:
        """
        创建配置好的日志记录器
        
        Args:
            name: 日志记录器名称
            level: 日志级别
            log_file: 日志文件路径
            log_format: 日志格式字符串
            json_format: 是否使用JSON格式
            max_bytes: 单个日志文件最大字节数
            backup_count: 保留的备份文件数量
            use_console: 是否输出到控制台
            propagate: 是否传播日志到父记录器
            
        Returns:
            logging.Logger: 配置好的日志记录器
        """
        # 获取日志级别
        if level is None:
            level = get_config("log_level", "INFO")
        
        if isinstance(level, str):
            level = LOG_LEVELS.get(level.upper(), logging.INFO)
        
        # 创建日志记录器
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.propagate = propagate
        
        # 清除现有处理器
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # 添加控制台处理器
        if use_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            
            if json_format:
                formatter = JsonFormatter()
            else:
                formatter = logging.Formatter(log_format)
                
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # 添加文件处理器
        if log_file:
            # 确保日志目录存在
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # 创建轮转文件处理器
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(level)
            
            if json_format:
                formatter = JsonFormatter()
            else:
                formatter = logging.Formatter(log_format)
                
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    @staticmethod
    def create_timed_logger(
        name: str,
        level: Optional[Union[str, int]] = None,
        log_file: Optional[str] = None,
        log_format: str = DEFAULT_FORMAT,
        json_format: bool = False,
        when: str = 'midnight',  # 每天午夜轮转
        interval: int = 1,
        backup_count: int = 30,  # 保留30天
        use_console: bool = True,
        propagate: bool = False
    ) -> logging.Logger:
        """
        创建基于时间轮转的日志记录器
        
        Args:
            name: 日志记录器名称
            level: 日志级别
            log_file: 日志文件路径
            log_format: 日志格式字符串
            json_format: 是否使用JSON格式
            when: 轮转时间单位
            interval: 轮转间隔
            backup_count: 保留的备份文件数量
            use_console: 是否输出到控制台
            propagate: 是否传播日志到父记录器
            
        Returns:
            logging.Logger: 配置好的日志记录器
        """
        # 获取日志级别
        if level is None:
            level = get_config("log_level", "INFO")
        
        if isinstance(level, str):
            level = LOG_LEVELS.get(level.upper(), logging.INFO)
        
        # 创建日志记录器
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.propagate = propagate
        
        # 清除现有处理器
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # 添加控制台处理器
        if use_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            
            if json_format:
                formatter = JsonFormatter()
            else:
                formatter = logging.Formatter(log_format)
                
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # 添加时间轮转文件处理器
        if log_file:
            # 确保日志目录存在
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # 创建时间轮转文件处理器
            file_handler = TimedRotatingFileHandler(
                log_file,
                when=when,
                interval=interval,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(level)
            
            if json_format:
                formatter = JsonFormatter()
            else:
                formatter = logging.Formatter(log_format)
                
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger

# 日志上下文管理
class LoggingContext:
    """日志上下文，用于在上下文中添加额外的日志字段"""
    
    def __init__(self, logger: logging.Logger, extra: Dict[str, Any]):
        """
        初始化日志上下文
        
        Args:
            logger: 日志记录器
            extra: 额外的日志字段
        """
        self.logger = logger
        self.extra = extra
        self.old_factory = logging.getLogRecordFactory()
    
    def __enter__(self):
        """进入上下文"""
        old_factory = self.old_factory
        
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.extra = self.extra
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        logging.setLogRecordFactory(self.old_factory)

# 创建应用默认日志目录
def get_default_log_path() -> str:
    """
    获取默认日志目录
    
    Returns:
        str: 默认日志目录路径
    """
    # 获取应用根目录
    app_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # 创建logs目录
    logs_dir = os.path.join(app_root, 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir, exist_ok=True)
    
    return logs_dir

# 应用程序日志设置
def setup_app_logging(
    app_name: str = "mcp",
    log_level: Optional[Union[str, int]] = None,
    json_format: bool = False,
    use_timed_rotation: bool = True
) -> logging.Logger:
    """
    设置应用程序日志
    
    Args:
        app_name: 应用名称
        log_level: 日志级别
        json_format: 是否使用JSON格式
        use_timed_rotation: 是否使用时间轮转
        
    Returns:
        logging.Logger: 应用程序根日志记录器
    """
    # 获取日志级别
    if log_level is None:
        log_level = get_config("log_level", "INFO")
    
    # 获取日志路径
    logs_dir = get_default_log_path()
    log_file = os.path.join(logs_dir, f"{app_name}.log")
    
    # 创建应用程序日志记录器
    if use_timed_rotation:
        logger = LoggerFactory.create_timed_logger(
            name=app_name,
            level=log_level,
            log_file=log_file,
            json_format=json_format
        )
    else:
        logger = LoggerFactory.create_logger(
            name=app_name,
            level=log_level,
            log_file=log_file,
            json_format=json_format
        )
    
    logger.info(f"应用程序日志已初始化: app={app_name}, level={log_level}, file={log_file}")
    return logger

# 导出实用方法
def get_logger(
    name: str,
    level: Optional[Union[str, int]] = None,
    use_json: bool = False
) -> logging.Logger:
    """
    获取配置好的日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别
        use_json: 是否使用JSON格式
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logs_dir = get_default_log_path()
    log_file = os.path.join(logs_dir, f"{name.replace('.', '_')}.log")
    
    return LoggerFactory.create_timed_logger(
        name=name,
        level=level,
        log_file=log_file,
        json_format=use_json
    )

def with_context(logger: logging.Logger, **extra) -> LoggingContext:
    """
    创建带有额外上下文的日志记录器
    
    Args:
        logger: 日志记录器
        **extra: 额外的日志字段
        
    Returns:
        LoggingContext: 日志上下文
    """
    return LoggingContext(logger, extra) 