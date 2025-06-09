from typing import TypedDict, List, Dict, Any, Optional
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langgraph.graph import StateGraph, END
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
    conversation_history: List[Dict[str, Any]]

class FastInsightFlowAgent:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        logger.info("Initializing FastInsightFlowAgent (singleton)")
        
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
            model_name="all-MiniLM-L6-v2"
        )
        
        # Simple memory storage
        self.conversation_memory = {}
        
        # Load components
        self._load_components()
        
        # Build graph
        self.graph = self._build_graph()
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        self._initialized = True
        logger.info("FastInsightFlowAgent initialized successfully")

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
        """Build optimized graph"""
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("classify_query", self.classify_query)
        graph.add_node("retrieve_documents", self.retrieve_documents)
        graph.add_node("analyze_context", self.analyze_context)
        graph.add_node("use_tools", self.use_tools)
        graph.add_node("generate_response", self.generate_response)
        
        # Add edges
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
        graph.add_edge("generate_response", END)
        
        # Set entry point
        graph.set_entry_point("classify_query")
        
        return graph.compile()

    async def classify_query(self, state: AgentState) -> AgentState:
        """Fast query classification with memory context"""
        start_time = time.time()
        question = state["question"]
        conversation_id = state["conversation_id"]
        
        # Get conversation history
        history = self.conversation_memory.get(conversation_id, [])
        context = ""
        if history:
            recent_topics = []
            for exchange in history[-3:]:  # Last 3 exchanges
                if 'question' in exchange:
                    recent_topics.append(exchange['question'].lower())
                if 'answer' in exchange:
                    recent_topics.append(exchange['answer'].lower()[:100])
            context = " ".join(recent_topics)
        
        # Enhanced classification considering context
        question_lower = question.lower()
        combined_text = f"{question_lower} {context}"
        
        # Rule-based classification with context awareness
        if any(keyword in combined_text for keyword in [
            "tax", "deduction", "business expense", "regulation", "legal", 
            "rule", "requirement", "compliance", "GST", "HST", "freelancer",
            "rate", "bracket", "income tax"  # Added tax-related terms
        ]):
            query_type = "retrieval"
        elif any(keyword in combined_text for keyword in [
            "calculate", "compute", "weather", "price", 
            "current", "recent", "news", "+", "%", "percent",
            "date", "time", "today", "now", "what day", "what time"
        ]):
            query_type = "tool_use"
        else:
            # Check if question is contextual (short questions that need previous context)
            if len(question.split()) <= 3 and history:
                # Short questions with history likely need context
                last_topic = history[-1] if history else {}
                if 'question' in last_topic:
                    last_q = last_topic['question'].lower()
                    if any(keyword in last_q for keyword in [
                        "tax", "deduction", "business", "legal", "rule"
                    ]):
                        query_type = "retrieval"
                    else:
                        query_type = "direct"
                else:
                    query_type = "direct"
            else:
                query_type = "direct"
        
        step = {
            "node": "QueryClassifier",
            "status": "completed",
            "timestamp": time.time() * 1000,
            "data": {
                "query_type": query_type,
                "classification_method": "rule_based_fast",
                "memory_context_used": bool(context),
                "processing_time_ms": int((time.time() - start_time) * 1000)
            }
        }
        
        state["steps"].append(step)
        state["query_type"] = query_type
        state["messages"] = [HumanMessage(content=question)]
        state["conversation_history"] = history
        
        return state

    def _route_query(self, state: AgentState) -> str:
        """Route based on query classification"""
        return state.get("query_type", "direct")

    async def retrieve_documents(self, state: AgentState) -> AgentState:
        """Fast document retrieval"""
        start_time = time.time()
        question = state["question"]
        
        try:
            # Run retrieval in thread pool
            loop = asyncio.get_event_loop()
            docs = await loop.run_in_executor(
                self.executor,
                functools.partial(self.vector_store.similarity_search, question, k=3)  # Reduced for speed
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
        """Fast context analysis"""
        start_time = time.time()
        question = state["question"]
        docs = state["retrieved_docs"]
        
        if not docs:
            state["analysis"] = "No relevant documents found."
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
        
        # Quick analysis - just extract key info
        key_info = []
        for doc in docs[:2]:  # Only top 2 for speed
            content = doc.get('content', '')[:300]  # Truncate
            key_info.append(content)
        
        analysis = f"Found {len(docs)} relevant documents with key information about: {question}"
        
        step = {
            "node": "ContextAnalyzer",
            "status": "completed",
            "timestamp": time.time() * 1000,
            "data": {
                "analysis_type": "fast_analysis",
                "documents_analyzed": len(docs),
                "analysis_length": len(analysis),
                "processing_time_ms": int((time.time() - start_time) * 1000)
            }
        }
        
        state["steps"].append(step)
        state["analysis"] = analysis
        
        return state

    async def use_tools(self, state: AgentState) -> AgentState:
        """Fast tool usage"""
        start_time = time.time()
        question = state["question"]
        
        try:
            # Smart tool selection based on question content
            question_lower = question.lower()
            
            if any(keyword in question_lower for keyword in ["date", "today", "now", "what day"]) or \
               ("what" in question_lower and "time" in question_lower):
                # Date/time query
                loop = asyncio.get_event_loop()
                if "time" in question_lower:
                    tool_result = await loop.run_in_executor(
                        self.executor,
                        functools.partial(self.tools.execute_tool, "datetime", "get_current_datetime")
                    )
                else:
                    tool_result = await loop.run_in_executor(
                        self.executor,
                        functools.partial(self.tools.execute_tool, "datetime", "get_today_date")
                    )
            elif any(op in question_lower for op in ["+", "-", "*", "/", "calculate", "compute"]):
                # Math calculation
                import re
                numbers = re.findall(r'\d+(?:\.\d+)?', question)
                if len(numbers) >= 2:
                    if "%" in question or "percent" in question:
                        # Percentage calculation
                        result = float(numbers[0]) * float(numbers[1]) / 100
                        tool_result = {"result": result, "calculation": f"{numbers[0]}% of {numbers[1]} = {result}"}
                    elif "+" in question:
                        result = sum(float(n) for n in numbers)
                        tool_result = {"result": result, "calculation": f"Sum = {result}"}
                    else:
                        result = float(numbers[0]) * float(numbers[1])
                        tool_result = {"result": result, "calculation": f"{numbers[0]} × {numbers[1]} = {result}"}
                else:
                    tool_result = {"error": "Could not extract numbers for calculation"}
            else:
                # Use appropriate tool
                loop = asyncio.get_event_loop()
                if any(keyword in question_lower for keyword in ["weather", "news", "current events"]):
                    tool_result = await loop.run_in_executor(
                        self.executor,
                        functools.partial(self.tools.execute_tool, "web_search", "search", query=question)
                    )
                else:
                    tool_result = await loop.run_in_executor(
                        self.executor,
                        functools.partial(self.tools.execute_tool, "calculator", "calculate", expression=question)
                    )
            
            # Determine which tool was actually used
            if any(keyword in question_lower for keyword in ["date", "today", "now", "what day"]) or \
               ("what" in question_lower and "time" in question_lower):
                tool_name = "datetime"
            elif any(keyword in question_lower for keyword in ["weather", "news", "current events"]):
                tool_name = "web_search"
            else:
                tool_name = "calculator"
                
            step = {
                "node": "ToolUser",
                "status": "completed",
                "timestamp": time.time() * 1000,
                "data": {
                    "tool_selected": tool_name,
                    "tool_result": str(tool_result)[:200],
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
        """Fast response generation with memory"""
        start_time = time.time()
        question = state["question"]
        query_type = state.get("query_type", "direct")
        conversation_id = state["conversation_id"]
        history = state.get("conversation_history", [])
        
        # Build comprehensive context with conversation history
        context_parts = []
        
        # Add conversation history with full context
        if history:
            context_parts.append("Recent conversation context:")
            for exchange in history[-3:]:  # Last 3 exchanges for better context
                if 'question' in exchange and 'answer' in exchange:
                    context_parts.append(f"User asked: {exchange['question']}")
                    # Keep more context, especially for questions and options
                    answer_text = exchange['answer'][:500]  # Increased from 100 to 500
                    context_parts.append(f"You responded: {answer_text}...")
        
        # Add current query context naturally
        if query_type == "retrieval":
            docs = state.get('retrieved_docs', [])
            if docs and docs[0].get('content'):
                context_parts.append(f"\nRelevant information: {docs[0]['content'][:200]}...")
        elif query_type == "tool_use":
            tool_result = state.get('tool_result')
            if tool_result:
                # Check if it's a datetime result
                if isinstance(tool_result, dict) and 'result' in tool_result and 'today' in str(tool_result):
                    context_parts.append(f"\nCurrent date information: {tool_result}")
                else:
                    context_parts.append(f"\nCalculation result: {tool_result}")
        
        context = "\n".join(context_parts) if context_parts else "No previous context"
        
        # Enhanced natural conversation prompt
        if history and len(question.split()) <= 3:
            # Short question with history - likely contextual
            last_response = history[-1].get('answer', '') if history else ''
            response_prompt = f"""
            Continue this natural conversation. The user just said: "{question}"
            
            {context}
            
            Important: If the user's response refers to options or choices you previously offered (like "general", "specific", "yes", "no"), understand which option they're choosing and respond accordingly. Don't ask the same clarifying questions again - they already answered.
            
            Respond naturally and directly based on their choice.
            """
        else:
            # Regular question
            if "tool_result" in state and state.get("query_type") == "tool_use":
                tool_result = state.get('tool_result', {})
                
                # Extract date information if available
                if isinstance(tool_result, dict) and 'result' in tool_result:
                    if 'today' in str(tool_result):
                        try:
                            date_info = tool_result['result']['today']['formatted']
                            response_prompt = f"""
                            The user asked: "{question}"
                            
                            The current date tool returned: {date_info}
                            
                            CRITICAL: You MUST use this exact date information. Do NOT use any other date. 
                            Answer with the date from the tool result only.
                            """
                        except:
                            response_prompt = f"""
                            Answer this question using the tool result: "{question}"
                            Tool result: {tool_result}
                            IMPORTANT: Use only the information from the tool result.
                            """
                    else:
                        response_prompt = f"""
                        Answer this question using the tool result: "{question}"
                        Tool result: {tool_result}
                        IMPORTANT: Use only the information from the tool result.
                        """
                else:
                    response_prompt = f"""
                    Answer this question using the tool result provided: "{question}"
                    
                    {context if context != "No previous context" else ""}
                    
                    IMPORTANT: Use the exact information from the tool result. Do not make up or guess information.
                    """
            else:
                response_prompt = f"""
                Answer this question helpfully and naturally: "{question}"
                
                {context if context != "No previous context" else ""}
                """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=response_prompt)])
            final_response = response.content
            
            # Save to memory with full context
            self.conversation_memory.setdefault(conversation_id, []).append({
                "question": question,
                "answer": final_response[:800],  # Much more content for context continuity
                "query_type": query_type,
                "timestamp": time.time()
            })
            
            # Keep only last 10 exchanges
            if len(self.conversation_memory[conversation_id]) > 10:
                self.conversation_memory[conversation_id] = self.conversation_memory[conversation_id][-10:]
            
            step = {
                "node": "ResponseGenerator",
                "status": "completed",
                "timestamp": time.time() * 1000,
                "data": {
                    "response_length": len(final_response),
                    "word_count": len(final_response.split()),
                    "sources_referenced": len(state.get('retrieved_docs', [])),
                    "memory_updated": True,
                    "processing_time_ms": int((time.time() - start_time) * 1000)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            final_response = f"I apologize, but I encountered an error: {str(e)}"
            
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

    async def process_query(self, question: str, conversation_id: str = "default") -> Dict[str, Any]:
        """Process a user query through the fast agent graph"""
        
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
            conversation_history=[]
        )
        
        try:
            # Run the graph
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
                    "memory_enabled": True,
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
                "answer": f"I apologize, but I encountered an error: {str(e)}",
                "steps": [error_step],
                "conversation_id": conversation_id,
                "metadata": {
                    "query_type": "error",
                    "total_processing_time_ms": 0,
                    "documents_used": 0,
                    "steps_executed": 1,
                    "model_used": "gemini-2.0-flash-exp",
                    "memory_enabled": True,
                    "performance_optimized": True
                }
            }

# Global agent instance
_agent_instance = None

def get_fast_agent():
    """Get or create the singleton agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = FastInsightFlowAgent()
    return _agent_instance