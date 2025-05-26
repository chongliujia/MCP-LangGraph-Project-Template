"""
Model configuration for different AI providers.
"""

from typing import Dict, Any, Optional, List
try:
    from pydantic.v1 import BaseModel, Field
except ImportError:
    from pydantic import BaseModel, Field
from enum import Enum


class ModelProvider(str, Enum):
    """Supported model providers."""
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    OPENAI = "openai"


class ModelType(str, Enum):
    """Types of models."""
    CHAT = "chat"
    EMBEDDING = "embedding"
    RERANK = "rerank"


class ModelConfig(BaseModel):
    """Configuration for a specific model."""
    
    name: str
    provider: ModelProvider
    model_type: ModelType
    api_key: Optional[str] = None
    base_url: str
    model_id: str
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 30
    max_retries: int = 3
    
    # Model-specific parameters
    extra_params: Dict[str, Any] = Field(default_factory=dict)


class ChatModelConfig(ModelConfig):
    """Configuration for chat models."""
    
    model_type: ModelType = ModelType.CHAT
    system_prompt: Optional[str] = None
    supports_function_calling: bool = True
    supports_streaming: bool = True
    context_window: int = 4096


class EmbeddingModelConfig(ModelConfig):
    """Configuration for embedding models."""
    
    model_type: ModelType = ModelType.EMBEDDING
    embedding_dimension: int = 1536
    max_input_length: int = 8192
    batch_size: int = 32


class RerankModelConfig(ModelConfig):
    """Configuration for reranking models."""
    
    model_type: ModelType = ModelType.RERANK
    max_query_length: int = 512
    max_document_length: int = 2048
    top_k: int = 10


# Default model configurations
DEFAULT_MODELS = {
    # DeepSeek Models
    "deepseek-chat": ChatModelConfig(
        name="deepseek-chat",
        provider=ModelProvider.DEEPSEEK,
        base_url="https://api.deepseek.com/v1",
        model_id="deepseek-chat",
        context_window=32768,
        max_tokens=4096,
        supports_function_calling=True,
        supports_streaming=True,
    ),
    
    "deepseek-coder": ChatModelConfig(
        name="deepseek-coder",
        provider=ModelProvider.DEEPSEEK,
        base_url="https://api.deepseek.com/v1",
        model_id="deepseek-coder",
        context_window=16384,
        max_tokens=4096,
        supports_function_calling=True,
        supports_streaming=True,
    ),
    
    # Qwen Models
    "qwen-turbo": ChatModelConfig(
        name="qwen-turbo",
        provider=ModelProvider.QWEN,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model_id="qwen-turbo",
        context_window=8192,
        max_tokens=2048,
        supports_function_calling=True,
        supports_streaming=True,
    ),
    
    "qwen-plus": ChatModelConfig(
        name="qwen-plus",
        provider=ModelProvider.QWEN,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model_id="qwen-plus",
        context_window=32768,
        max_tokens=4096,
        supports_function_calling=True,
        supports_streaming=True,
    ),
    
    "qwen-max": ChatModelConfig(
        name="qwen-max",
        provider=ModelProvider.QWEN,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model_id="qwen-max",
        context_window=32768,
        max_tokens=4096,
        supports_function_calling=True,
        supports_streaming=True,
    ),
    
    # Qwen Embedding Models
    "qwen-embedding": EmbeddingModelConfig(
        name="qwen-embedding",
        provider=ModelProvider.QWEN,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model_id="text-embedding-v1",
        embedding_dimension=1536,
        max_input_length=8192,
        batch_size=25,
    ),
    
    "qwen-embedding-v2": EmbeddingModelConfig(
        name="qwen-embedding-v2",
        provider=ModelProvider.QWEN,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model_id="text-embedding-v2",
        embedding_dimension=1536,
        max_input_length=8192,
        batch_size=25,
    ),
    
    # Qwen Rerank Models
    "qwen-rerank": RerankModelConfig(
        name="qwen-rerank",
        provider=ModelProvider.QWEN,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model_id="gte-rerank",
        max_query_length=512,
        max_document_length=2048,
        top_k=10,
    ),
}


def get_model_config(model_name: str) -> Optional[ModelConfig]:
    """Get model configuration by name."""
    return DEFAULT_MODELS.get(model_name)


def get_models_by_type(model_type: ModelType) -> List[ModelConfig]:
    """Get all models of a specific type."""
    return [
        config for config in DEFAULT_MODELS.values()
        if config.model_type == model_type
    ]


def get_models_by_provider(provider: ModelProvider) -> List[ModelConfig]:
    """Get all models from a specific provider."""
    return [
        config for config in DEFAULT_MODELS.values()
        if config.provider == provider
    ] 