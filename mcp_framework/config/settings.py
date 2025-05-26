"""
Configuration settings for MCP AI Framework.
"""

import os
from typing import Optional, List, Dict, Any
try:
    from pydantic.v1 import BaseSettings, Field
except ImportError:
    from pydantic import BaseSettings, Field
from functools import lru_cache


class Settings(BaseSettings):
    """Main configuration settings for the MCP AI Framework."""
    
    # Application Settings
    app_name: str = "MCP AI Framework"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # API Settings
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_workers: int = Field(default=1, env="API_WORKERS")
    
    # DeepSeek API Configuration
    deepseek_api_key: Optional[str] = Field(default=None, env="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com/v1", 
        env="DEEPSEEK_BASE_URL"
    )
    deepseek_model: str = Field(
        default="deepseek-chat", 
        env="DEEPSEEK_MODEL"
    )
    
    # Qwen API Configuration
    qwen_api_key: Optional[str] = Field(default=None, env="QWEN_API_KEY")
    qwen_base_url: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        env="QWEN_BASE_URL"
    )
    qwen_chat_model: str = Field(
        default="qwen-turbo",
        env="QWEN_CHAT_MODEL"
    )
    qwen_embedding_model: str = Field(
        default="text-embedding-v1",
        env="QWEN_EMBEDDING_MODEL"
    )
    qwen_rerank_model: str = Field(
        default="gte-rerank",
        env="QWEN_RERANK_MODEL"
    )
    
    # Milvus Configuration
    milvus_host: str = Field(default="localhost", env="MILVUS_HOST")
    milvus_port: int = Field(default=19530, env="MILVUS_PORT")
    milvus_user: Optional[str] = Field(default=None, env="MILVUS_USER")
    milvus_password: Optional[str] = Field(default=None, env="MILVUS_PASSWORD")
    milvus_db_name: str = Field(default="mcp_framework", env="MILVUS_DB_NAME")
    
    # Vector Database Settings
    default_collection_name: str = Field(
        default="documents", 
        env="DEFAULT_COLLECTION_NAME"
    )
    embedding_dimension: int = Field(default=1536, env="EMBEDDING_DIMENSION")
    similarity_metric: str = Field(default="COSINE", env="SIMILARITY_METRIC")
    
    # MCP Settings
    mcp_server_name: str = Field(
        default="mcp-ai-framework", 
        env="MCP_SERVER_NAME"
    )
    mcp_server_version: str = Field(default="0.1.0", env="MCP_SERVER_VERSION")
    
    # Tool Settings
    max_tool_execution_time: int = Field(
        default=30, 
        env="MAX_TOOL_EXECUTION_TIME"
    )
    enable_tool_logging: bool = Field(
        default=True, 
        env="ENABLE_TOOL_LOGGING"
    )
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(
        default=60, 
        env="RATE_LIMIT_RPM"
    )
    rate_limit_tokens_per_minute: int = Field(
        default=10000, 
        env="RATE_LIMIT_TPM"
    )
    
    # Security
    api_key_header: str = Field(default="X-API-Key", env="API_KEY_HEADER")
    allowed_origins: List[str] = Field(
        default=["*"], 
        env="ALLOWED_ORIGINS"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings() 