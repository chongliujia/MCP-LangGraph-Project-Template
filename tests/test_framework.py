"""
Basic tests for MCP LangGraph Framework.
"""

import pytest
import asyncio
from mcp_framework import MCPLangGraphFramework
from mcp_framework.tools import CalculatorTool, SearchTool, WeatherTool
from langchain_core.messages import HumanMessage


@pytest.fixture
def framework():
    """Create framework for testing."""
    return MCPLangGraphFramework()


@pytest.mark.asyncio
async def test_framework_initialization():
    """Test framework initialization."""
    async with MCPLangGraphFramework() as framework:
        # Framework should be properly initialized in context manager
        assert framework.llm is not None
        assert framework.embeddings is not None
        assert framework.vectorstore is not None
        assert framework.graph is not None


@pytest.mark.asyncio
async def test_health_check():
    """Test health check functionality."""
    async with MCPLangGraphFramework() as framework:
        health = await framework.health_check()
        assert health["framework"] == "healthy"
        assert "components" in health
        assert health["components"]["llm"] == "initialized"
        assert health["components"]["embeddings"] == "initialized"
        assert health["components"]["vectorstore"] == "initialized"
        assert health["components"]["graph"] == "initialized"


@pytest.mark.asyncio
async def test_chat_functionality():
    """Test chat functionality."""
    async with MCPLangGraphFramework() as framework:
        response = await framework.chat("Hello, world!")
        assert isinstance(response, str)
        assert len(response) > 0


@pytest.mark.asyncio
async def test_embedding_functionality():
    """Test embedding functionality."""
    async with MCPLangGraphFramework() as framework:
        embedding = await framework.embeddings.aembed_query("Test text")
        assert isinstance(embedding, list)
        assert len(embedding) > 0  # Should have some dimensions


@pytest.mark.asyncio
async def test_vector_operations():
    """Test vector database operations."""
    async with MCPLangGraphFramework() as framework:
        doc_ids = await framework.vectorstore.aadd_texts(
            ["This is a test document", "Another test document"],
            [{"test": True}, {"test": False}]
        )
        assert isinstance(doc_ids, list)
        assert len(doc_ids) == 2
        
        results = await framework.vectorstore.asimilarity_search("test document", k=3)
        assert isinstance(results, list)
        assert len(results) > 0


@pytest.mark.asyncio
async def test_tool_management():
    """Test tool management functionality."""
    async with MCPLangGraphFramework() as framework:
        # Initially no tools
        tools = framework.get_available_tools()
        assert isinstance(tools, list)
        assert len(tools) == 0
        
        # Register a tool
        calc_tool = CalculatorTool()
        framework.register_tool(calc_tool)
        
        # Should have one tool now
        tools = framework.get_available_tools()
        assert len(tools) == 1
        assert "calculator" in tools


@pytest.mark.asyncio
async def test_workflow_execution():
    """Test workflow execution."""
    async with MCPLangGraphFramework() as framework:
        # Register calculator tool
        framework.register_tool(CalculatorTool())
        
        # Run workflow with calculation
        result = await framework.run_workflow({
            "messages": [HumanMessage(content="Calculate 2 + 3")]
        })
        
        assert "messages" in result
        assert len(result["messages"]) > 0


@pytest.mark.asyncio
async def test_multiple_tools():
    """Test multiple tool registration and usage."""
    async with MCPLangGraphFramework() as framework:
        # Register multiple tools
        framework.register_tool(CalculatorTool())
        framework.register_tool(SearchTool())
        framework.register_tool(WeatherTool())
        
        # Check all tools are registered
        tools = framework.get_available_tools()
        assert len(tools) == 3
        assert "calculator" in tools
        assert "search" in tools
        assert "weather" in tools


@pytest.mark.asyncio
async def test_context_manager():
    """Test that framework works properly as context manager."""
    framework = MCPLangGraphFramework()
    
    # Should not be initialized yet
    assert framework.llm is None
    
    async with framework:
        # Should be initialized now
        assert framework.llm is not None
        assert framework.embeddings is not None
        assert framework.vectorstore is not None
        assert framework.graph is not None
    
    # Should be cleaned up after context
    # Note: We don't test cleanup state as it depends on implementation


@pytest.mark.asyncio
async def test_tool_unregistration():
    """Test tool unregistration functionality."""
    async with MCPLangGraphFramework() as framework:
        # Register a tool
        calc_tool = CalculatorTool()
        framework.register_tool(calc_tool)
        
        # Verify it's registered
        tools = framework.get_available_tools()
        assert "calculator" in tools
        
        # Unregister the tool
        framework.unregister_tool("calculator")
        
        # Verify it's removed
        tools = framework.get_available_tools()
        assert "calculator" not in tools
        assert len(tools) == 0


@pytest.mark.asyncio
async def test_health_check_uninitialized():
    """Test health check on uninitialized framework."""
    framework = MCPLangGraphFramework()
    
    health = await framework.health_check()
    assert health["framework"] == "not_initialized"
    assert health["components"]["llm"] == "not_initialized"
    assert health["components"]["embeddings"] == "not_initialized"
    assert health["components"]["vectorstore"] == "not_initialized"
    assert health["components"]["graph"] == "not_initialized"
    assert health["tools_count"] == 0 