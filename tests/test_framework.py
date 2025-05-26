"""
Basic tests for MCP AI Framework.
"""

import pytest
import asyncio
from mcp_framework import MCPFramework
from mcp_framework.config.settings import Settings


@pytest.fixture
def settings():
    """Create test settings."""
    return Settings(
        debug=True,
        log_level="DEBUG",
        # Use placeholder values for testing
        qwen_api_key="test_key",
        deepseek_api_key="test_key"
    )


@pytest.fixture
def framework(settings):
    """Create framework for testing."""
    return MCPFramework(settings)


@pytest.mark.asyncio
async def test_framework_initialization(settings):
    """Test framework initialization."""
    framework = MCPFramework(settings)
    assert not framework._initialized
    
    await framework.initialize()
    assert framework._initialized
    
    await framework.cleanup()
    assert not framework._initialized


@pytest.mark.asyncio
async def test_health_check(framework):
    """Test health check functionality."""
    await framework.initialize()
    try:
        health = await framework.health_check()
        assert health["framework"] == "healthy"
        assert "components" in health
    finally:
        await framework.cleanup()


@pytest.mark.asyncio
async def test_model_manager(framework):
    """Test model manager functionality."""
    models = framework.get_available_models()
    assert "chat" in models
    assert "embedding" in models
    assert "rerank" in models


@pytest.mark.asyncio
async def test_chat_functionality(framework):
    """Test chat functionality."""
    response = await framework.chat("Hello, world!")
    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.asyncio
async def test_embedding_functionality(framework):
    """Test embedding functionality."""
    embedding = await framework.embed_text("Test text")
    assert isinstance(embedding, list)
    assert len(embedding) == 1536  # Default embedding dimension


@pytest.mark.asyncio
async def test_vector_operations(framework):
    """Test vector database operations."""
    # Add a document
    doc_id = await framework.add_document(
        text="This is a test document",
        metadata={"test": True}
    )
    assert isinstance(doc_id, str)
    
    # Search for similar documents
    results = await framework.search_similar("test document", top_k=3)
    assert isinstance(results, list)


@pytest.mark.asyncio
async def test_tool_management(framework):
    """Test tool management functionality."""
    tools = framework.get_available_tools()
    assert isinstance(tools, list) 