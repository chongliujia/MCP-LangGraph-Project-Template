"""
Vector database configuration for Milvus.
"""

from typing import Dict, Any, Optional, List
try:
    from pydantic.v1 import BaseModel, Field
except ImportError:
    from pydantic import BaseModel, Field
from enum import Enum


class MetricType(str, Enum):
    """Supported similarity metrics."""
    L2 = "L2"
    IP = "IP"  # Inner Product
    COSINE = "COSINE"
    HAMMING = "HAMMING"
    JACCARD = "JACCARD"


class IndexType(str, Enum):
    """Supported index types."""
    FLAT = "FLAT"
    IVF_FLAT = "IVF_FLAT"
    IVF_SQ8 = "IVF_SQ8"
    IVF_PQ = "IVF_PQ"
    HNSW = "HNSW"
    SCANN = "SCANN"


class VectorConfig(BaseModel):
    """Configuration for vector database operations."""
    
    # Connection settings
    host: str = "localhost"
    port: int = 19530
    user: Optional[str] = None
    password: Optional[str] = None
    db_name: str = "mcp_framework"
    
    # Collection settings
    default_collection_name: str = "documents"
    embedding_dimension: int = 1536
    metric_type: MetricType = MetricType.COSINE
    
    # Index settings
    index_type: IndexType = IndexType.HNSW
    index_params: Dict[str, Any] = Field(default_factory=lambda: {
        "M": 16,
        "efConstruction": 200
    })
    
    # Search settings
    search_params: Dict[str, Any] = Field(default_factory=lambda: {
        "ef": 100
    })
    
    # Performance settings
    batch_size: int = 100
    timeout: int = 30
    consistency_level: str = "Strong"
    
    # Auto-flush settings
    auto_flush: bool = True
    flush_interval: int = 1000  # Number of entities


class CollectionConfig(BaseModel):
    """Configuration for a specific collection."""
    
    name: str
    description: str = ""
    embedding_dimension: int = 1536
    metric_type: MetricType = MetricType.COSINE
    index_type: IndexType = IndexType.HNSW
    
    # Schema fields
    fields: List[Dict[str, Any]] = Field(default_factory=lambda: [
        {
            "name": "id",
            "type": "int64",
            "is_primary": True,
            "auto_id": True
        },
        {
            "name": "vector",
            "type": "float_vector",
            "dimension": 1536
        },
        {
            "name": "text",
            "type": "varchar",
            "max_length": 65535
        },
        {
            "name": "metadata",
            "type": "json"
        },
        {
            "name": "timestamp",
            "type": "int64"
        }
    ])
    
    # Index configuration
    index_params: Dict[str, Any] = Field(default_factory=lambda: {
        "M": 16,
        "efConstruction": 200
    })
    
    # Search configuration
    search_params: Dict[str, Any] = Field(default_factory=lambda: {
        "ef": 100
    })
    
    # Partitioning
    enable_partitioning: bool = False
    partition_field: Optional[str] = None


# Default collection configurations
DEFAULT_COLLECTIONS = {
    "documents": CollectionConfig(
        name="documents",
        description="General document storage",
        embedding_dimension=1536,
        metric_type=MetricType.COSINE,
        index_type=IndexType.HNSW,
    ),
    
    "code": CollectionConfig(
        name="code",
        description="Code snippets and documentation",
        embedding_dimension=1536,
        metric_type=MetricType.COSINE,
        index_type=IndexType.HNSW,
        fields=[
            {
                "name": "id",
                "type": "int64",
                "is_primary": True,
                "auto_id": True
            },
            {
                "name": "vector",
                "type": "float_vector",
                "dimension": 1536
            },
            {
                "name": "code",
                "type": "varchar",
                "max_length": 65535
            },
            {
                "name": "language",
                "type": "varchar",
                "max_length": 50
            },
            {
                "name": "file_path",
                "type": "varchar",
                "max_length": 1000
            },
            {
                "name": "metadata",
                "type": "json"
            },
            {
                "name": "timestamp",
                "type": "int64"
            }
        ]
    ),
    
    "conversations": CollectionConfig(
        name="conversations",
        description="Chat conversations and context",
        embedding_dimension=1536,
        metric_type=MetricType.COSINE,
        index_type=IndexType.HNSW,
        fields=[
            {
                "name": "id",
                "type": "int64",
                "is_primary": True,
                "auto_id": True
            },
            {
                "name": "vector",
                "type": "float_vector",
                "dimension": 1536
            },
            {
                "name": "message",
                "type": "varchar",
                "max_length": 65535
            },
            {
                "name": "role",
                "type": "varchar",
                "max_length": 20
            },
            {
                "name": "session_id",
                "type": "varchar",
                "max_length": 100
            },
            {
                "name": "metadata",
                "type": "json"
            },
            {
                "name": "timestamp",
                "type": "int64"
            }
        ]
    )
}


def get_collection_config(collection_name: str) -> Optional[CollectionConfig]:
    """Get collection configuration by name."""
    return DEFAULT_COLLECTIONS.get(collection_name)


def get_index_params(index_type: IndexType) -> Dict[str, Any]:
    """Get default index parameters for a given index type."""
    params = {
        IndexType.FLAT: {},
        IndexType.IVF_FLAT: {"nlist": 1024},
        IndexType.IVF_SQ8: {"nlist": 1024},
        IndexType.IVF_PQ: {"nlist": 1024, "m": 16, "nbits": 8},
        IndexType.HNSW: {"M": 16, "efConstruction": 200},
        IndexType.SCANN: {"nlist": 1024}
    }
    return params.get(index_type, {})


def get_search_params(index_type: IndexType) -> Dict[str, Any]:
    """Get default search parameters for a given index type."""
    params = {
        IndexType.FLAT: {},
        IndexType.IVF_FLAT: {"nprobe": 10},
        IndexType.IVF_SQ8: {"nprobe": 10},
        IndexType.IVF_PQ: {"nprobe": 10},
        IndexType.HNSW: {"ef": 100},
        IndexType.SCANN: {"nprobe": 10}
    }
    return params.get(index_type, {}) 