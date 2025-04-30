"""
内存管理 - 提供对话历史和向量存储功能
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field
from datetime import datetime

class Message(BaseModel):
    """对话消息"""
    role: str = Field(..., description="消息发送者角色，如'user'、'assistant'")
    content: str = Field(..., description="消息内容")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="消息时间戳")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

class MemoryItem(BaseModel):
    """内存项"""
    id: str = Field(..., description="唯一标识符")
    content: Any = Field(..., description="内容")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

from .base_memory import BaseMemory
from .message_memory import MessageMemory
from .vector_memory import VectorMemory
from .combined_memory import CombinedMemory
from .memory_manager import MemoryManager

__all__ = [
    "Message", "MemoryItem", "BaseMemory", "MessageMemory",
    "VectorMemory", "CombinedMemory", "MemoryManager"
] 