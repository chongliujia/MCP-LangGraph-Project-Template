"""
MCP LangGraph Framework - Core framework built on LangChain and LangGraph.
"""

import asyncio
from typing import Dict, Any, Optional, List, Type
from loguru import logger

from langchain_core.language_models import BaseLLM
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from ..config.settings import Settings, get_settings
from ..tools.base import MCPTool
from ..langchain.graph_builder import GraphBuilder


class MCPLangGraphFramework:
    """
    Main framework class built on LangChain and LangGraph.
    
    This class provides:
    - LangGraph workflow orchestration
    - MCP protocol integration
    - Tool management via LangChain
    - Multi-model support
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """Initialize the MCP LangGraph Framework."""
        self.settings = settings or get_settings()
        self._initialized = False
        
        # Core components
        self.llm: Optional[BaseLLM] = None
        self.embeddings: Optional[Embeddings] = None
        self.vectorstore: Optional[VectorStore] = None
        self.tools: Dict[str, BaseTool] = {}
        self.graph: Optional[StateGraph] = None
        self.graph_builder: Optional[GraphBuilder] = None
        self.memory = MemorySaver()
        
        logger.info("MCP LangGraph Framework initialized")
    
    async def initialize(self) -> None:
        """Initialize all framework components."""
        if self._initialized:
            logger.warning("Framework already initialized")
            return
        
        try:
            logger.info("Initializing MCP LangGraph Framework components...")
            
            # Initialize LLM
            await self._initialize_llm()
            
            # Initialize embeddings
            await self._initialize_embeddings()
            
            # Initialize vector store
            await self._initialize_vectorstore()
            
            # Initialize graph builder
            self.graph_builder = GraphBuilder(
                llm=self.llm,
                tools=list(self.tools.values()),
                memory=self.memory
            )
            
            # Build default graph
            self.graph = self.graph_builder.build_default_graph()
            
            self._initialized = True
            logger.success("MCP LangGraph Framework fully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize framework: {e}")
            await self.cleanup()
            raise
    
    async def _initialize_llm(self) -> None:
        """Initialize the language model."""
        # Use OpenAI-compatible API for DeepSeek/Qwen
        if self.settings.deepseek_api_key:
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(
                api_key=self.settings.deepseek_api_key,
                base_url=self.settings.deepseek_base_url,
                model=self.settings.deepseek_model,
                temperature=0.7
            )
        elif self.settings.qwen_api_key:
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(
                api_key=self.settings.qwen_api_key,
                base_url=self.settings.qwen_base_url,
                model=self.settings.qwen_chat_model,
                temperature=0.7
            )
        else:
            logger.warning("No API key provided, using simple placeholder LLM")
            # Create a simple fake LLM to avoid compatibility issues
            from langchain_core.language_models.llms import LLM
            from langchain_core.callbacks.manager import CallbackManagerForLLMRun
            from typing import Any, List, Optional
            
            class SimpleFakeLLM(LLM):
                responses: List[str] = ["This is a placeholder response from SimpleFakeLLM"]
                
                @property
                def _llm_type(self) -> str:
                    return "simple_fake"
                
                def _call(
                    self,
                    prompt: str,
                    stop: Optional[List[str]] = None,
                    run_manager: Optional[CallbackManagerForLLMRun] = None,
                    **kwargs: Any,
                ) -> str:
                    return self.responses[0]
                
                async def _acall(
                    self,
                    prompt: str,
                    stop: Optional[List[str]] = None,
                    run_manager: Optional[CallbackManagerForLLMRun] = None,
                    **kwargs: Any,
                ) -> str:
                    return self.responses[0]
            
            self.llm = SimpleFakeLLM()
        
        logger.info(f"LLM initialized: {type(self.llm).__name__}")
    
    async def _initialize_embeddings(self) -> None:
        """Initialize embeddings model."""
        if self.settings.qwen_api_key:
            from langchain_openai import OpenAIEmbeddings
            self.embeddings = OpenAIEmbeddings(
                api_key=self.settings.qwen_api_key,
                base_url=self.settings.qwen_base_url,
                model=self.settings.qwen_embedding_model
            )
        else:
            logger.warning("No embedding API key provided, using simple fake embeddings")
            # Create a simple fake embeddings class to avoid compatibility issues
            class SimpleFakeEmbeddings:
                def __init__(self, size=1536):
                    self.size = size
                
                async def aembed_documents(self, texts):
                    import random
                    return [[random.random() for _ in range(self.size)] for _ in texts]
                
                async def aembed_query(self, text):
                    import random
                    return [random.random() for _ in range(self.size)]
                
                def embed_documents(self, texts):
                    import random
                    return [[random.random() for _ in range(self.size)] for _ in texts]
                
                def embed_query(self, text):
                    import random
                    return [random.random() for _ in range(self.size)]
            
            self.embeddings = SimpleFakeEmbeddings(size=1536)
        
        logger.info(f"Embeddings initialized: {type(self.embeddings).__name__}")
    
    async def _initialize_vectorstore(self) -> None:
        """Initialize vector store."""
        # Create a simple in-memory vector store to avoid FAISS dependency
        class SimpleVectorStore:
            def __init__(self, embeddings):
                self.embeddings = embeddings
                self.documents = []
                self.vectors = []
            
            async def aadd_texts(self, texts, metadatas=None):
                """Add texts to the vector store."""
                embeddings = await self.embeddings.aembed_documents(texts)
                for i, text in enumerate(texts):
                    self.documents.append({
                        "text": text,
                        "metadata": metadatas[i] if metadatas else {},
                        "embedding": embeddings[i]
                    })
                return [f"doc_{len(self.documents) - len(texts) + i}" for i in range(len(texts))]
            
            async def asimilarity_search(self, query, k=3):
                """Search for similar documents."""
                if not self.documents:
                    return []
                
                query_embedding = await self.embeddings.aembed_query(query)
                
                # Simple cosine similarity
                similarities = []
                for doc in self.documents:
                    # Calculate cosine similarity
                    dot_product = sum(a * b for a, b in zip(query_embedding, doc["embedding"]))
                    norm_a = sum(a * a for a in query_embedding) ** 0.5
                    norm_b = sum(b * b for b in doc["embedding"]) ** 0.5
                    similarity = dot_product / (norm_a * norm_b) if norm_a * norm_b > 0 else 0
                    similarities.append((similarity, doc))
                
                # Sort by similarity and return top k
                similarities.sort(key=lambda x: x[0], reverse=True)
                
                # Create document objects
                class SimpleDocument:
                    def __init__(self, page_content, metadata=None):
                        self.page_content = page_content
                        self.metadata = metadata or {}
                
                return [SimpleDocument(doc["text"], doc["metadata"]) for _, doc in similarities[:k]]
        
        self.vectorstore = SimpleVectorStore(self.embeddings)
        
        # Add some initial documents
        dummy_texts = ["Welcome to MCP LangGraph Framework"]
        await self.vectorstore.aadd_texts(dummy_texts)
        
        logger.info("Simple vector store initialized")
    
    async def cleanup(self) -> None:
        """Clean up all framework components."""
        logger.info("Cleaning up MCP LangGraph Framework...")
        
        self.llm = None
        self.embeddings = None
        self.vectorstore = None
        self.tools.clear()
        self.graph = None
        self.graph_builder = None
        
        self._initialized = False
        logger.info("MCP LangGraph Framework cleanup completed")
    
    def register_tool(self, tool: BaseTool) -> None:
        """Register a tool."""
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
        
        # Rebuild graph if already initialized
        if self.graph_builder:
            self.graph = self.graph_builder.build_default_graph()
    
    def unregister_tool(self, tool_name: str) -> None:
        """Unregister a tool."""
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.info(f"Unregistered tool: {tool_name}")
            
            # Rebuild graph if already initialized
            if self.graph_builder:
                self.graph = self.graph_builder.build_default_graph()
    
    async def run_workflow(
        self,
        input_data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run a workflow using the LangGraph."""
        if not self._initialized:
            await self.initialize()
        
        if not self.graph:
            raise RuntimeError("Graph not initialized")
        
        # Compile the graph with memory
        app = self.graph.compile(checkpointer=self.memory)
        
        # Prepare config with required thread_id
        run_config = config or {}
        if "configurable" not in run_config:
            run_config["configurable"] = {}
        if "thread_id" not in run_config["configurable"]:
            run_config["configurable"]["thread_id"] = "default_thread"
        
        # Run the workflow
        result = await app.ainvoke(input_data, config=run_config)
        return result
    
    async def chat(self, message: str, **kwargs) -> str:
        """Simple chat interface."""
        from langchain_core.messages import HumanMessage
        
        result = await self.run_workflow({
            "messages": [HumanMessage(content=message)]
        })
        
        # Extract the response from the result
        if "messages" in result and result["messages"]:
            last_message = result["messages"][-1]
            # Handle different message types
            if hasattr(last_message, 'content'):
                return last_message.content
            elif isinstance(last_message, dict):
                return last_message.get("content", "No response")
            elif isinstance(last_message, str):
                return last_message
        return "No response generated"
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        return list(self.tools.keys())
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        return {
            "framework": "healthy" if self._initialized else "not_initialized",
            "components": {
                "llm": "initialized" if self.llm else "not_initialized",
                "embeddings": "initialized" if self.embeddings else "not_initialized",
                "vectorstore": "initialized" if self.vectorstore else "not_initialized",
                "graph": "initialized" if self.graph else "not_initialized",
            },
            "tools_count": len(self.tools)
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup() 