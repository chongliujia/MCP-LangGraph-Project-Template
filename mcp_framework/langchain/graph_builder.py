"""
LangGraph workflow builder for MCP AI Framework.
"""

from typing import Dict, Any, List, Optional, Sequence
from langchain_core.language_models import BaseLLM
from langchain_core.tools import BaseTool
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.base import BaseCheckpointSaver
try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """State for the agent workflow."""
    messages: List[BaseMessage]
    next_action: Optional[str]


class GraphBuilder:
    """Builder for creating LangGraph workflows."""
    
    def __init__(
        self,
        llm: BaseLLM,
        tools: List[BaseTool],
        memory: Optional[BaseCheckpointSaver] = None
    ):
        self.llm = llm
        self.tools = tools
        self.memory = memory
        
        # Bind tools to LLM if available
        if self.tools:
            self.llm_with_tools = self.llm.bind_tools(self.tools)
        else:
            self.llm_with_tools = self.llm
    
    def build_default_graph(self) -> StateGraph:
        """Build a default agent workflow graph."""
        
        # Define the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", self._call_model)
        
        if self.tools:
            workflow.add_node("tools", self._call_tools)
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools" if self.tools else END,
                "end": END,
            },
        )
        
        if self.tools:
            workflow.add_edge("tools", "agent")
        
        return workflow
    
    def build_rag_graph(self, vectorstore) -> StateGraph:
        """Build a RAG (Retrieval-Augmented Generation) workflow."""
        
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("retrieve", lambda state: self._retrieve_documents(state, vectorstore))
        workflow.add_node("generate", self._generate_with_context)
        
        # Set entry point and edges
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)
        
        return workflow
    
    def build_multi_agent_graph(self, agents: Dict[str, BaseLLM]) -> StateGraph:
        """Build a multi-agent workflow."""
        
        workflow = StateGraph(AgentState)
        
        # Add agent nodes
        for agent_name, agent_llm in agents.items():
            workflow.add_node(agent_name, lambda state, llm=agent_llm: self._call_specific_model(state, llm))
        
        # Add router node
        workflow.add_node("router", self._route_to_agent)
        
        # Set entry point
        workflow.set_entry_point("router")
        
        # Add conditional edges from router to agents
        workflow.add_conditional_edges(
            "router",
            lambda state: state.next_action,
            {agent_name: agent_name for agent_name in agents.keys()}
        )
        
        # Add edges from agents to end
        for agent_name in agents.keys():
            workflow.add_edge(agent_name, END)
        
        return workflow
    
    def _call_model(self, state: AgentState) -> Dict[str, Any]:
        """Call the language model."""
        messages = state["messages"]
        # Use sync invoke for compatibility with LangGraph
        response = self.llm_with_tools.invoke(messages)
        return {"messages": messages + [response]}
    
    def _call_tools(self, state: AgentState) -> Dict[str, Any]:
        """Call tools based on the last message."""
        messages = state["messages"]
        last_message = messages[-1]
        
        # Extract tool calls from the last message
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            tool_results = []
            for tool_call in last_message.tool_calls:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("args", {})
                
                # Find and execute the tool
                for tool in self.tools:
                    if tool.name == tool_name:
                        try:
                            # Use sync run for compatibility
                            result = tool.run(**tool_args)
                            tool_results.append(f"Tool {tool_name} result: {result}")
                        except Exception as e:
                            tool_results.append(f"Tool {tool_name} error: {str(e)}")
                        break
            
            # Create a response message with tool results
            from langchain_core.messages import AIMessage
            tool_response = AIMessage(content="\n".join(tool_results))
            return {"messages": messages + [tool_response]}
        
        return {"messages": messages}
    
    def _call_specific_model(self, state: AgentState, llm: BaseLLM) -> Dict[str, Any]:
        """Call a specific language model."""
        messages = state["messages"]
        response = llm.invoke(messages)
        return {"messages": messages + [response]}
    
    def _should_continue(self, state: AgentState) -> str:
        """Determine whether to continue or end the workflow."""
        messages = state["messages"]
        last_message = messages[-1]
        
        # If there are tool calls, continue to tools
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "continue"
        
        # Otherwise, end
        return "end"
    
    def _retrieve_documents(self, state: AgentState, vectorstore) -> Dict[str, Any]:
        """Retrieve relevant documents."""
        messages = state["messages"]
        query = messages[-1].content if messages else ""
        
        # Retrieve documents (use sync method for compatibility)
        import asyncio
        try:
            docs = asyncio.run(vectorstore.asimilarity_search(query, k=3))
        except:
            # Fallback to empty docs if async fails
            docs = []
        
        # Add retrieved context to the last message
        context = "\n".join([doc.page_content for doc in docs])
        enhanced_query = f"Context: {context}\n\nQuestion: {query}"
        
        # Update the last message with context
        if messages:
            messages[-1] = HumanMessage(content=enhanced_query)
        
        return {"messages": messages}
    
    def _generate_with_context(self, state: AgentState) -> Dict[str, Any]:
        """Generate response with retrieved context."""
        messages = state["messages"]
        response = self.llm.invoke(messages)
        return {"messages": messages + [response]}
    
    def _route_to_agent(self, state: AgentState) -> Dict[str, Any]:
        """Route to appropriate agent based on the query."""
        messages = state["messages"]
        query = messages[-1].content if messages else ""
        
        # Simple routing logic (can be enhanced with a classifier)
        if "code" in query.lower() or "programming" in query.lower():
            next_action = "coder"
        elif "math" in query.lower() or "calculate" in query.lower():
            next_action = "mathematician"
        else:
            next_action = "general"
        
        return {"next_action": next_action}
    
    def create_custom_graph(self, nodes: Dict[str, callable], edges: List[tuple]) -> StateGraph:
        """Create a custom graph with specified nodes and edges."""
        
        workflow = StateGraph(AgentState)
        
        # Add nodes
        for node_name, node_func in nodes.items():
            workflow.add_node(node_name, node_func)
        
        # Add edges
        for edge in edges:
            if len(edge) == 2:
                workflow.add_edge(edge[0], edge[1])
            elif len(edge) == 3:
                # Conditional edge
                workflow.add_conditional_edges(edge[0], edge[1], edge[2])
        
        return workflow 