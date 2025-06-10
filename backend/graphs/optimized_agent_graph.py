from typing import TypedDict, List, Dict, Any, Optional
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langgraph.graph import StateGraph, END
from langgraph.store.memory import InMemoryStore
from langmem import create_manage_memory_tool, create_search_memory_tool
import time
import os
from dotenv import load_dotenv
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import functools

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    messages: List[BaseMessage]
    question: str
    retrieved_docs: List[Dict[str, Any]]
    analysis: str
    response: str
    steps: List[Dict[str, Any]]
    conversation_id: str
    query_type: str
    memory_context: Optional[str]

class OptimizedInsightFlowAgent:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        logger.info("Initializing OptimizedInsightFlowAgent (singleton)")
        
        # Initialize Google API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        # Initialize LLM with optimizations
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=api_key,
            temperature=0.1,
            max_retries=2,
            timeout=30
        )
        
        # Initialize embeddings (cached)
        self.embeddings = SentenceTransformerEmbeddings(
            model_name="all-MiniLM-L6-v2",
            cache_folder=".cache/embeddings"
        )
        
        # Initialize memory store with LangMem
        self.memory_store = InMemoryStore(
            index={
                "dims": 384,  # all-MiniLM-L6-v2 dimensions
                "embed": lambda x: self.embeddings.embed_query(x),
            }
        )
        
        # Create memory tools
        self.memory_tools = [
            create_manage_memory_tool(namespace=("conversations",)),
            create_search_memory_tool(namespace=("conversations",)),
        ]
        
        # Load components (cached)
        self._load_components()
        
        # Build graph
        self.graph = self._build_graph()
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Conversation cache
        self.conversation_cache = {}
        
        self._initialized = True
        logger.info("OptimizedInsightFlowAgent initialized successfully")

    def _load_components(self):
        """Load vector store and tools with caching"""
        try:
            from retriever.real_vector_store import RealVectorStore
            self.vector_store = RealVectorStore(self.embeddings)
            
            from tools.real_tools import RealToolRegistry
            self.tools = RealToolRegistry()
            
            logger.info("Components loaded successfully")
        except Exception as e:
            logger.error(f"Error loading components: {e}")
            raise

    def _build_graph(self) -> StateGraph:
        """Build optimized graph with memory integration"""
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("load_memory", self.load_memory)
        graph.add_node("classify_query", self.classify_query)
        graph.add_node("retrieve_documents", self.retrieve_documents)
        graph.add_node("analyze_context", self.analyze_context)
        graph.add_node("use_tools", self.use_tools)
        graph.add_node("generate_response", self.generate_response)
        graph.add_node("save_memory", self.save_memory)
        
        # Add edges with memory flow
        graph.add_edge("load_memory", "classify_query")
        
        graph.add_conditional_edges(
            "classify_query",
            self._route_query,
            {
                "retrieval": "retrieve_documents",
                "tool_use": "use_tools",
                "direct": "generate_response"
            }
        )
        
        graph.add_edge("retrieve_documents", "analyze_context")
        graph.add_edge("analyze_context", "generate_response")
        graph.add_edge("use_tools", "generate_response")
        graph.add_edge("generate_response", "save_memory")
        graph.add_edge("save_memory", END)
        
        # Set entry point
        graph.set_entry_point("load_memory")
        
        return graph.compile()

    async def load_memory(self, state: AgentState) -> AgentState:
        """Load conversation memory and context"""
        start_time = time.time()
        conversation_id = state["conversation_id"]
        
        try:
            # Check cache first
            if conversation_id in self.conversation_cache:
                memory_context = self.conversation_cache[conversation_id]
                logger.info(f"Loaded memory from cache for {conversation_id}")
            else:
                # Search memory store for relevant context
                memory_search_tool = self.memory_tools[1]  # search tool
                
                # Search for relevant memories
                memory_result = await memory_search_tool.ainvoke({
                    "query": f"conversation {conversation_id} context history",
                    "k": 5
                })
                
                memory_context = ""
                if memory_result and hasattr(memory_result, 'content'):
                    memory_context = memory_result.content
                elif isinstance(memory_result, str):
                    memory_context = memory_result
                
                # Cache the result
                self.conversation_cache[conversation_id] = memory_context
            
            step = {
                "node": "MemoryLoader",
                "status": "completed",
                "timestamp": time.time() * 1000,
                "data": {
                    "memory_found": bool(memory_context),
                    "memory_length": len(memory_context) if memory_context else 0,
                    "processing_time_ms": int((time.time() - start_time) * 1000)
                }
            }
            
            state["steps"].append(step)
            state["memory_context"] = memory_context
            
        except Exception as e:
            logger.error(f"Error loading memory: {e}")
            
            step = {
                "node": "MemoryLoader",
                "status": "error",
                "timestamp": time.time() * 1000,
                "data": {
                    "error": str(e),
                    "processing_time_ms": int((time.time() - start_time) * 1000)
                }
            }
            
            state["steps"].append(step)
            state["memory_context"] = ""
        
        return state

    async def classify_query(self, state: AgentState) -> AgentState:
        """Enhanced query classification with memory context"""
        start_time = time.time()
        question = state["question"]
        memory_context = state.get("memory_context", "")
        
        # Enhanced classification prompt with memory
        classification_prompt = f"""
        Analyze this user question and classify it into one of these categories:
        
        1. "retrieval" - Questions about specific topics that need document search:
           - Tax rules, regulations, compliance
           - Business expenses, deductions
           - Legal requirements, procedures
           - Specific industry knowledge
           - Technical documentation
        
        2. "tool_use" - Questions needing calculations or current data:
           - Mathematical calculations
           - Current events, news, recent information
           - Weather, stock prices, live data
           - Web searches for current information
        
        3. "direct" - Questions answerable with general knowledge:
           - General concepts, definitions
           - Common knowledge topics
           - Simple explanations
           - Greetings, casual conversation
        
        Question: "{question}"
        
        {f"Previous conversation context: {memory_context[:500]}..." if memory_context else "No previous context available."}
        
        Consider the context when classifying. If the user is following up on a previous topic,
        classify accordingly.
        
        Respond with ONLY the category name: retrieval, tool_use, or direct
        """
        
        try:
            # Use async LLM call
            response = await self.llm.ainvoke([HumanMessage(content=classification_prompt)])
            classification_text = response.content.strip().lower()
            
            # Enhanced classification parsing
            if "retrieval" in classification_text:
                query_type = "retrieval"
            elif "tool_use" in classification_text:
                query_type = "tool_use"
            elif "direct" in classification_text:
                query_type = "direct"
            else:
                # Smarter fallback with context
                question_lower = question.lower()
                if any(keyword in question_lower for keyword in [
                    "tax", "deduction", "business expense", "regulation", "legal", 
                    "rule", "requirement", "compliance", "GST", "HST", "freelancer"
                ]):
                    query_type = "retrieval"
                elif any(keyword in question_lower for keyword in [
                    "calculate", "compute", "what is", "weather", "price", 
                    "current", "today", "recent", "news"
                ]):
                    query_type = "tool_use"
                else:
                    query_type = "direct"
                
        except Exception as e:
            logger.error(f"Error in query classification: {e}")
            # Intelligent fallback
            question_lower = question.lower()
            if any(keyword in question_lower for keyword in [
                "tax", "deduction", "business", "legal", "rule", "regulation"
            ]):
                query_type = "retrieval"
            else:
                query_type = "direct"
        
        step = {
            "node": "QueryClassifier",
            "status": "completed",
            "timestamp": time.time() * 1000,
            "data": {
                "query_type": query_type,
                "classification_reasoning": classification_text if 'classification_text' in locals() else "fallback classification",
                "memory_context_used": bool(memory_context),
                "processing_time_ms": int((time.time() - start_time) * 1000)
            }
        }
        
        state["steps"].append(step)
        state["query_type"] = query_type
        state["messages"] = [HumanMessage(content=question)]
        
        return state

    def _route_query(self, state: AgentState) -> str:
        """Route based on query classification"""
        return state.get("query_type", "direct")

    async def retrieve_documents(self, state: AgentState) -> AgentState:
        """Optimized document retrieval with parallel processing"""
        start_time = time.time()
        question = state["question"]
        
        try:
            # Run retrieval in thread pool for non-blocking
            loop = asyncio.get_event_loop()
            docs = await loop.run_in_executor(
                self.executor,
                functools.partial(self.vector_store.similarity_search, question, k=5)
            )
            
            step = {
                "node": "DocumentRetriever",
                "status": "completed",
                "timestamp": time.time() * 1000,
                "data": {
                    "documents_found": len(docs),
                    "avg_similarity_score": sum(doc.get("score", 0) for doc in docs) / len(docs) if docs else 0,
                    "sources": [doc.get("metadata", {}).get("source", "unknown") for doc in docs],
                    "processing_time_ms": int((time.time() - start_time) * 1000)
                }
            }
            
            state["steps"].append(step)
            state["retrieved_docs"] = docs
            
        except Exception as e:
            logger.error(f"Error in document retrieval: {e}")
            
            step = {
                "node": "DocumentRetriever",
                "status": "error",
                "timestamp": time.time() * 1000,
                "data": {
                    "error": str(e),
                    "documents_found": 0,
                    "processing_time_ms": int((time.time() - start_time) * 1000)
                }
            }
            
            state["steps"].append(step)
            state["retrieved_docs"] = []
        
        return state

    async def analyze_context(self, state: AgentState) -> AgentState:
        """Fast context analysis with memory integration"""
        start_time = time.time()
        question = state["question"]
        docs = state["retrieved_docs"]
        memory_context = state.get("memory_context", "")
        
        if not docs:
            state["analysis"] = "No relevant documents found for analysis."
            step = {
                "node": "ContextAnalyzer",
                "status": "completed",
                "timestamp": time.time() * 1000,
                "data": {
                    "analysis_type": "no_documents",
                    "processing_time_ms": int((time.time() - start_time) * 1000)
                }
            }
            state["steps"].append(step)
            return state
        
        # Create optimized context
        context = "\n\n".join([
            f"Document {i+1}: {doc.get('content', '')[:500]}..."  # Truncate for speed
            for i, doc in enumerate(docs[:3])  # Use only top 3
        ])
        
        analysis_prompt = f"""
        Based on the documents and conversation history, analyze how they relate to the user's question.
        Be concise but thorough.
        
        Question: "{question}"
        
        {f"Previous context: {memory_context[:300]}..." if memory_context else ""}
        
        Documents:
        {context}
        
        Provide a brief analysis focusing on:
        1. Key information that answers the question
        2. Confidence level (1-10)
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=analysis_prompt)])
            analysis = response.content
            
            step = {
                "node": "ContextAnalyzer",
                "status": "completed",
                "timestamp": time.time() * 1000,
                "data": {
                    "analysis_type": "document_analysis",
                    "documents_analyzed": len(docs),
                    "analysis_length": len(analysis),
                    "memory_integrated": bool(memory_context),
                    "processing_time_ms": int((time.time() - start_time) * 1000)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in context analysis: {e}")
            analysis = f"Error analyzing context: {str(e)}"
            
            step = {
                "node": "ContextAnalyzer",
                "status": "error",
                "timestamp": time.time() * 1000,
                "data": {
                    "error": str(e),
                    "processing_time_ms": int((time.time() - start_time) * 1000)
                }
            }
        
        state["steps"].append(step)
        state["analysis"] = analysis
        
        return state

    async def use_tools(self, state: AgentState) -> AgentState:
        """Optimized tool usage"""
        start_time = time.time()
        question = state["question"]
        
        tool_selection_prompt = f"""
        Based on this question, which tool should be used?
        
        Question: "{question}"
        
        Available tools:
        - web_search: For current information, news, or general web queries
        - calculator: For mathematical calculations
        
        Respond with: tool_name: specific_query
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=tool_selection_prompt)])
            tool_instruction = response.content.strip()
            
            # Run tool execution in thread pool
            loop = asyncio.get_event_loop()
            tool_result = None
            
            if "calculator:" in tool_instruction.lower():
                expression = tool_instruction.split(":", 1)[1].strip()
                tool_result = await loop.run_in_executor(
                    self.executor,
                    functools.partial(self.tools.execute_tool, "calculator", "calculate", expression=expression)
                )
            elif "web_search:" in tool_instruction.lower():
                query = tool_instruction.split(":", 1)[1].strip()
                tool_result = await loop.run_in_executor(
                    self.executor,
                    functools.partial(self.tools.execute_tool, "web_search", "search", query=query)
                )
            
            step = {
                "node": "ToolUser",
                "status": "completed",
                "timestamp": time.time() * 1000,
                "data": {
                    "tool_selected": tool_instruction.split(":")[0] if ":" in tool_instruction else "none",
                    "tool_result": str(tool_result)[:200] if tool_result else "No result",
                    "processing_time_ms": int((time.time() - start_time) * 1000)
                }
            }
            
            state["tool_result"] = tool_result
            
        except Exception as e:
            logger.error(f"Error using tools: {e}")
            
            step = {
                "node": "ToolUser",
                "status": "error",
                "timestamp": time.time() * 1000,
                "data": {
                    "error": str(e),
                    "processing_time_ms": int((time.time() - start_time) * 1000)
                }
            }
            
            state["tool_result"] = None
        
        state["steps"].append(step)
        return state

    async def generate_response(self, state: AgentState) -> AgentState:
        """Enhanced response generation with memory context"""
        start_time = time.time()
        question = state["question"]
        query_type = state.get("query_type", "direct")
        memory_context = state.get("memory_context", "")
        
        # Build context based on query type
        if query_type == "retrieval":
            context = f"""
            Analysis: {state.get('analysis', 'No analysis available')}
            Retrieved Documents: {len(state.get('retrieved_docs', []))} documents found
            """
        elif query_type == "tool_use":
            context = f"Tool Result: {state.get('tool_result', 'No tool result')}"
        else:
            context = "This is a direct question that can be answered with general knowledge."
        
        response_prompt = f"""
        Provide a comprehensive answer to the user's question.
        
        Question: "{question}"
        
        {f"Previous conversation context: {memory_context[:400]}..." if memory_context else ""}
        
        Current Context: {context}
        
        Guidelines:
        1. Be accurate and helpful
        2. Reference previous conversation if relevant
        3. Cite sources when available
        4. Be conversational but professional
        5. If information is limited, acknowledge it
        
        Provide a clear, well-structured response.
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=response_prompt)])
            final_response = response.content
            
            step = {
                "node": "ResponseGenerator",
                "status": "completed",
                "timestamp": time.time() * 1000,
                "data": {
                    "response_length": len(final_response),
                    "word_count": len(final_response.split()),
                    "sources_referenced": len(state.get('retrieved_docs', [])),
                    "memory_context_used": bool(memory_context),
                    "processing_time_ms": int((time.time() - start_time) * 1000)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            final_response = f"I apologize, but I encountered an error while generating a response: {str(e)}"
            
            step = {
                "node": "ResponseGenerator",
                "status": "error",
                "timestamp": time.time() * 1000,
                "data": {
                    "error": str(e),
                    "processing_time_ms": int((time.time() - start_time) * 1000)
                }
            }
        
        state["steps"].append(step)
        state["response"] = final_response
        state["messages"].append(AIMessage(content=final_response))
        
        return state

    async def save_memory(self, state: AgentState) -> AgentState:
        """Save conversation to memory for future context"""
        start_time = time.time()
        conversation_id = state["conversation_id"]
        question = state["question"]
        response = state["response"]
        
        try:
            # Create memory entry
            memory_content = f"""
            Conversation ID: {conversation_id}
            User Question: {question}
            Assistant Response: {response[:500]}...
            Query Type: {state.get('query_type', 'unknown')}
            Timestamp: {time.time()}
            """
            
            # Save to memory store
            memory_manage_tool = self.memory_tools[0]  # manage tool
            await memory_manage_tool.ainvoke({
                "action": "store",
                "content": memory_content,
                "metadata": {
                    "conversation_id": conversation_id,
                    "timestamp": time.time(),
                    "query_type": state.get('query_type', 'unknown')
                }
            })
            
            # Update cache
            if conversation_id in self.conversation_cache:
                self.conversation_cache[conversation_id] += f"\n{memory_content}"
            else:
                self.conversation_cache[conversation_id] = memory_content
            
            step = {
                "node": "MemorySaver",
                "status": "completed",
                "timestamp": time.time() * 1000,
                "data": {
                    "memory_saved": True,
                    "conversation_id": conversation_id,
                    "processing_time_ms": int((time.time() - start_time) * 1000)
                }
            }
            
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
            
            step = {
                "node": "MemorySaver",
                "status": "error",
                "timestamp": time.time() * 1000,
                "data": {
                    "error": str(e),
                    "processing_time_ms": int((time.time() - start_time) * 1000)
                }
            }
        
        state["steps"].append(step)
        return state

    async def process_query(self, question: str, conversation_id: str = "default") -> Dict[str, Any]:
        """Process a user query through the optimized agent graph"""
        
        # Initialize state
        initial_state = AgentState(
            messages=[],
            question=question,
            retrieved_docs=[],
            analysis="",
            response="",
            steps=[],
            conversation_id=conversation_id,
            query_type="",
            memory_context=""
        )
        
        try:
            # Run the graph asynchronously
            result = await self.graph.ainvoke(initial_state)
            
            # Calculate total processing time
            total_time = 0
            if result["steps"]:
                start_time = result["steps"][0]["timestamp"]
                end_time = result["steps"][-1]["timestamp"]
                total_time = int(end_time - start_time)
            
            return {
                "answer": result["response"],
                "steps": result["steps"],
                "conversation_id": conversation_id,
                "metadata": {
                    "query_type": result.get("query_type", "unknown"),
                    "total_processing_time_ms": total_time,
                    "documents_used": len(result.get("retrieved_docs", [])),
                    "steps_executed": len(result["steps"]),
                    "model_used": "gemini-2.0-flash-exp",
                    "memory_context_used": bool(result.get("memory_context")),
                    "performance_optimized": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            
            error_step = {
                "node": "ErrorHandler",
                "status": "error",
                "timestamp": time.time() * 1000,
                "data": {"error": str(e)}
            }
            
            return {
                "answer": f"I apologize, but I encountered an error while processing your question: {str(e)}",
                "steps": [error_step],
                "conversation_id": conversation_id,
                "metadata": {
                    "query_type": "error",
                    "total_processing_time_ms": 0,
                    "documents_used": 0,
                    "steps_executed": 1,
                    "model_used": "gemini-2.0-flash-exp",
                    "memory_context_used": False,
                    "performance_optimized": True
                }
            }

# Global agent instance
_agent_instance = None

def get_agent():
    """Get or create the singleton agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = OptimizedInsightFlowAgent()
    return _agent_instance