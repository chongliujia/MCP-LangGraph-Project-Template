"""
配置管理器 - 负责加载、管理和提供应用程序配置
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger("config_manager")

class ConfigManager:
    """配置管理器类，支持多环境配置和敏感信息管理"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        "model": "deepseek-chat",
        "temperature": 0.1,
        "provider": "deepseek",
        "log_level": "INFO",
        "max_tokens": 1000,
        "timeout": 60.0,
        "cache_enabled": False,
        "streaming_enabled": False,
    }
    
    def __init__(self, config_path: Optional[str] = None, env: str = "development"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
            env: 环境名称(development, testing, production)
        """
        self.env = env
        self.config_path = config_path
        self.secrets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".secrets")
        self.config = self.DEFAULT_CONFIG.copy()
        
        # 加载配置
        self._load_config()
        
        # 加载环境变量
        self._load_env_vars()
        
        # 加载密钥
        self._load_secrets()
        
        logger.info(f"配置加载完成: 环境={env}")
        
    def _load_config(self):
        """加载配置文件"""
        # 基础配置
        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config.update(json.load(f))
                logger.info(f"已加载基础配置: {self.config_path}")
            except Exception as e:
                logger.error(f"加载基础配置失败: {str(e)}")
        
        # 环境特定配置
        env_config_path = self.config_path.replace(".json", f".{self.env}.json") if self.config_path else f"config.{self.env}.json"
        if os.path.exists(env_config_path):
            try:
                with open(env_config_path, "r", encoding="utf-8") as f:
                    self.config.update(json.load(f))
                logger.info(f"已加载环境配置: {env_config_path}")
            except Exception as e:
                logger.error(f"加载环境配置失败: {str(e)}")
    
    def _load_env_vars(self):
        """加载环境变量覆盖配置"""
        # 从环境变量加载配置
        env_prefix = "MCP_"
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                config_key = key[len(env_prefix):].lower()
                # 尝试转换为正确的类型
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                elif value.isdigit():
                    value = int(value)
                elif value.replace(".", "", 1).isdigit() and value.count(".") == 1:
                    value = float(value)
                    
                self.config[config_key] = value
                logger.debug(f"从环境变量加载配置: {config_key}={value}")
    
    def _load_secrets(self):
        """加载密钥信息"""
        # 创建密钥目录（如果不存在）
        os.makedirs(self.secrets_path, exist_ok=True)
        
        # 加载密钥文件
        secrets_file = os.path.join(self.secrets_path, f"secrets.{self.env}.json")
        if os.path.exists(secrets_file):
            try:
                with open(secrets_file, "r", encoding="utf-8") as f:
                    secrets = json.load(f)
                    for key, value in secrets.items():
                        if key.endswith("_api_key"):
                            self.config[key] = value
                logger.info(f"已加载密钥: {secrets_file}")
            except Exception as e:
                logger.error(f"加载密钥失败: {str(e)}")
        
        # 从环境变量加载密钥
        for key in ["OPENAI_API_KEY", "DEEPSEEK_API_KEY", "QIANWEN_API_KEY"]:
            if key in os.environ:
                self.config[key.lower()] = os.environ[key]
                logger.debug(f"从环境变量加载密钥: {key}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        设置配置项
        
        Args:
            key: 配置键
            value: 配置值
        """
        self.config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        获取所有配置
        
        Returns:
            所有配置项
        """
        return self.config.copy()
    
    def save(self):
        """保存当前配置到文件"""
        # 保存基础配置
        if self.config_path:
            # 提取非敏感信息
            save_config = {k: v for k, v in self.config.items() if not k.endswith("_api_key")}
            
            try:
                with open(self.config_path, "w", encoding="utf-8") as f:
                    json.dump(save_config, f, indent=2, ensure_ascii=False)
                logger.info(f"配置已保存: {self.config_path}")
            except Exception as e:
                logger.error(f"保存配置失败: {str(e)}")
        
        # 保存密钥
        secrets = {k: v for k, v in self.config.items() if k.endswith("_api_key")}
        if secrets:
            secrets_file = os.path.join(self.secrets_path, f"secrets.{self.env}.json")
            try:
                with open(secrets_file, "w", encoding="utf-8") as f:
                    json.dump(secrets, f, indent=2, ensure_ascii=False)
                logger.info(f"密钥已保存: {secrets_file}")
                # 设置文件权限
                os.chmod(secrets_file, 0o600)
            except Exception as e:
                logger.error(f"保存密钥失败: {str(e)}") 