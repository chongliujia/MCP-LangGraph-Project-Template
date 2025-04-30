"""
配置监视器 - 支持配置文件热重载
"""

import os
import time
import threading
import logging
from typing import Dict, Any, Optional, List, Set, Callable

from .config_manager import ConfigManager

logger = logging.getLogger(__name__)


class ConfigWatcher:
    """
    配置监视器，用于监视配置文件变更并自动重载
    """
    
    def __init__(self, config_manager: ConfigManager, interval: float = 5.0):
        """
        初始化配置监视器
        
        Args:
            config_manager: 配置管理器
            interval: 检查间隔时间（秒）
        """
        self.config_manager = config_manager
        self.interval = interval
        self._watched_files: Dict[str, Dict[str, Any]] = {}  # {文件路径: {mtime: 修改时间, source: 配置源名称}}
        self._callback_handlers: Dict[str, List[Callable[[], None]]] = {}  # {文件路径: [回调函数]}
        self._stop_event = threading.Event()
        self._watcher_thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()
    
    def watch_file(self, file_path: str, source_name: str, callback: Optional[Callable[[], None]] = None) -> None:
        """
        监视配置文件
        
        Args:
            file_path: 文件路径
            source_name: 配置源名称
            callback: 可选的回调函数，当文件变更时调用
        """
        with self._lock:
            abs_path = os.path.abspath(file_path)
            
            if not os.path.exists(abs_path):
                logger.warning(f"要监视的文件不存在: {abs_path}")
                return
            
            mtime = os.path.getmtime(abs_path)
            
            self._watched_files[abs_path] = {
                "mtime": mtime,
                "source": source_name
            }
            
            if callback:
                if abs_path not in self._callback_handlers:
                    self._callback_handlers[abs_path] = []
                self._callback_handlers[abs_path].append(callback)
            
            logger.debug(f"开始监视配置文件: {abs_path} (源: {source_name})")
    
    def unwatch_file(self, file_path: str) -> None:
        """
        停止监视配置文件
        
        Args:
            file_path: 文件路径
        """
        with self._lock:
            abs_path = os.path.abspath(file_path)
            
            if abs_path in self._watched_files:
                del self._watched_files[abs_path]
                logger.debug(f"停止监视配置文件: {abs_path}")
            
            if abs_path in self._callback_handlers:
                del self._callback_handlers[abs_path]
    
    def start(self) -> None:
        """启动监视器"""
        if self._watcher_thread and self._watcher_thread.is_alive():
            logger.warning("配置监视器已经在运行")
            return
        
        self._stop_event.clear()
        self._watcher_thread = threading.Thread(
            target=self._watch_loop,
            name="ConfigWatcher",
            daemon=True
        )
        self._watcher_thread.start()
        logger.info(f"配置监视器已启动 (检查间隔: {self.interval}秒)")
    
    def stop(self) -> None:
        """停止监视器"""
        if not self._watcher_thread or not self._watcher_thread.is_alive():
            logger.warning("配置监视器未运行")
            return
        
        self._stop_event.set()
        self._watcher_thread.join(timeout=self.interval * 2)
        logger.info("配置监视器已停止")
    
    def is_running(self) -> bool:
        """
        检查监视器是否正在运行
        
        Returns:
            bool: 是否正在运行
        """
        return self._watcher_thread is not None and self._watcher_thread.is_alive()
    
    def _check_files(self) -> None:
        """检查文件变更"""
        changed_files = []
        
        with self._lock:
            for file_path, info in list(self._watched_files.items()):
                try:
                    if not os.path.exists(file_path):
                        logger.warning(f"监视的文件已不存在: {file_path}")
                        continue
                    
                    current_mtime = os.path.getmtime(file_path)
                    
                    if current_mtime > info["mtime"]:
                        # 文件已变更
                        logger.info(f"检测到配置文件变更: {file_path}")
                        info["mtime"] = current_mtime
                        changed_files.append(file_path)
                except Exception as e:
                    logger.error(f"检查文件变更时发生错误: {e}")
        
        # 处理变更的文件
        for file_path in changed_files:
            self._handle_file_change(file_path)
    
    def _handle_file_change(self, file_path: str) -> None:
        """
        处理文件变更
        
        Args:
            file_path: 文件路径
        """
        try:
            info = self._watched_files.get(file_path)
            if not info:
                return
            
            source_name = info["source"]
            source = self.config_manager.get_source(source_name)
            
            if source and hasattr(source, "reload") and callable(source.reload):
                # 重新加载配置源
                source.reload()
                logger.info(f"已重新加载配置源: {source_name}")
            
            # 调用回调函数
            callbacks = self._callback_handlers.get(file_path, [])
            for callback in callbacks:
                try:
                    callback()
                except Exception as e:
                    logger.error(f"执行配置变更回调函数时发生错误: {e}")
        except Exception as e:
            logger.error(f"处理文件变更时发生错误: {e}")
    
    def _watch_loop(self) -> None:
        """监视循环"""
        while not self._stop_event.is_set():
            try:
                self._check_files()
            except Exception as e:
                logger.error(f"配置监视循环发生错误: {e}")
            
            # 等待下一次检查
            self._stop_event.wait(self.interval) 