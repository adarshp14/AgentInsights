from typing import TypedDict, List, Dict, Any, Optional, AsyncGenerator
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
import json

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

class StreamingInsightFlowAgent:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        logger.info("Initializing StreamingInsightFlowAgent (singleton)")
        
        # Initialize Google API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        # Initialize LLM with streaming support
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=api_key,
            temperature=0.1,
            max_retries=2,
            timeout=30,
            streaming=True  # Enable streaming
        )
        
        # Initialize embeddings (cached)
        self.embeddings = SentenceTransformerEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Enhanced memory storage with metadata
        self.conversation_memory = {}
        self.session_metadata = {}  # Track session info
        
        # Load components
        self._load_components()
        
        # Build graph
        self.graph = self._build_graph()
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        self._initialized = True
        logger.info("StreamingInsightFlowAgent initialized successfully")
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up old inactive sessions"""
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)
        
        sessions_to_remove = []
        for session_id, metadata in self.session_metadata.items():
            if metadata["last_active"] < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            if session_id in self.conversation_memory:
                del self.conversation_memory[session_id]
            if session_id in self.session_metadata:
                del self.session_metadata[session_id]
        
        if sessions_to_remove:
            logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")
    
    def get_session_info(self, conversation_id: str) -> Dict[str, Any]:
        """Get session information"""
        if conversation_id not in self.session_metadata:
            return {"error": "Session not found"}
        
        metadata = self.session_metadata[conversation_id]
        memory_count = len(self.conversation_memory.get(conversation_id, []))
        
        return {
            "session_id": conversation_id,
            "created_at": metadata["created_at"],
            "last_active": metadata["last_active"],
            "message_count": metadata["message_count"],
            "memory_exchanges": memory_count,
            "active": True
        }

    def _load_components(self):
        """Load vector store and tools with caching"""
        try:
            from retriever.chroma_vector_store import ChromaVectorStore
            self.vector_store = ChromaVectorStore()
            
            from tools.real_tools import RealToolRegistry
            self.tools = RealToolRegistry()
            
            logger.info("Components loaded successfully")
        except Exception as e:
            logger.error(f"Error loading components: {e}")
            # Fallback to old vector store if ChromaDB fails
            try:
                from retriever.real_vector_store import RealVectorStore
                self.vector_store = RealVectorStore(self.embeddings)
                logger.info("Fallback to RealVectorStore successful")
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")
                raise

    def _build_graph(self) -> StateGraph:
        """Build optimized graph"""
        graph = StateGraph(AgentState)
        
        # Add nodes - RAG focused
        graph.add_node("classify_query", self.classify_query)
        graph.add_node("retrieve_documents", self.retrieve_documents)
        graph.add_node("analyze_context", self.analyze_context)
        graph.add_node("generate_response", self.generate_response)
        
        # Add edges - clean RAG flow
        graph.add_conditional_edges(
            "classify_query",
            self._route_query,
            {
                "retrieval": "retrieve_documents",
                "direct": "generate_response"
            }
        )
        
        graph.add_edge("retrieve_documents", "analyze_context")
        graph.add_edge("analyze_context", "generate_response")
        graph.add_edge("generate_response", END)
        
        # Set entry point
        graph.set_entry_point("classify_query")
        
        return graph.compile()

    async def classify_query(self, state: AgentState) -> AgentState:
        """Fast query classification with memory context"""
        start_time = time.time()
        question = state["question"]
        conversation_id = state["conversation_id"]
        
        # Get conversation history and initialize session if new
        if conversation_id not in self.session_metadata:
            self.session_metadata[conversation_id] = {
                "created_at": time.time(),
                "last_active": time.time(),
                "message_count": 0
            }
        
        # Update session activity
        self.session_metadata[conversation_id]["last_active"] = time.time()
        
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
        
        # Simplified classification: Only RAG and Direct responses
        # First check for simple greetings and conversational queries
        if any(greeting in question_lower for greeting in [
            "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
            "how are you", "what's up", "thanks", "thank you", "bye", "goodbye"
        ]):
            query_type = "direct"
        elif any(keyword in combined_text for keyword in [
            "tax", "deduction", "business expense", "regulation", "legal", 
            "rule", "requirement", "compliance", "GST", "HST", "freelancer",
            "rate", "bracket", "income tax", "document", "policy", "guideline",
            "explain", "what is", "how to", "define", "meaning", "example"
        ]):
            query_type = "retrieval"
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
                functools.partial(self.vector_store.similarity_search, question, k=3)
            )
            
            step = {
                "node": "DocumentRetriever",
                "status": "completed",
                "timestamp": time.time() * 1000,
                "data": {
                    "documents_found": len(docs),
                    "avg_similarity_score": sum(doc.get("score", 0) for doc in docs) / len(docs) if docs else 0,
                    "sources": [doc.get("metadata", {}).get("filename", "unknown") for doc in docs],
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
        
        # Build proper conversation history for LLM context
        conversation_context = ""
        if history:
            conversation_context = "\n\nPrevious conversation:\n"
            for i, exchange in enumerate(history[-5:], 1):  # Last 5 exchanges
                conversation_context += f"Turn {i}:\n"
                conversation_context += f"Human: {exchange.get('question', '')}\n"
                conversation_context += f"Assistant: {exchange.get('answer', '')[:400]}\n\n"
        
        # Enhanced natural conversation prompt with full context
        if history and len(question.split()) <= 3:
            # Short question with history - likely contextual
            response_prompt = f"""
            You are continuing a conversation. Here is the full context:
            {conversation_context}
            
            Current user message: "{question}"
            
            IMPORTANT: 
            - If the user's response refers to options or choices you previously offered (like "general", "specific", "yes", "no"), understand which option they're selecting and respond accordingly
            - Don't repeat questions you already asked - they are responding to your previous message
            - Maintain conversation continuity and context
            - If they seem to be answering a previous question, acknowledge their choice and continue naturally
            
            Respond based on the full conversation context above.
            """
        else:
            # Regular conversation with full context
            response_prompt = f"""
            {conversation_context}
            
            Current question: "{question}"
            
            Answer this question helpfully and naturally, considering the conversation context above.
            """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=response_prompt)])
            final_response = response.content
            
            # Save to memory with full context
            self.conversation_memory.setdefault(conversation_id, []).append({
                "question": question,
                "answer": final_response[:1200],  # More content for better context continuity
                "query_type": query_type,
                "timestamp": time.time()
            })
            
            # Update session metadata
            if conversation_id in self.session_metadata:
                self.session_metadata[conversation_id]["message_count"] += 1
                self.session_metadata[conversation_id]["last_active"] = time.time()
            
            # Keep only last 20 exchanges for better context
            if len(self.conversation_memory[conversation_id]) > 20:
                self.conversation_memory[conversation_id] = self.conversation_memory[conversation_id][-20:]
            
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

    async def stream_response(self, prompt: str) -> AsyncGenerator[str, None]:
        """Stream response generation token by token"""
        try:
            async for chunk in self.llm.astream([HumanMessage(content=prompt)]):
                if hasattr(chunk, 'content') and chunk.content:
                    yield chunk.content
        except Exception as e:
            logger.error(f"Error in stream_response: {e}")
            yield f"Error: {str(e)}"

    async def process_query_stream(self, question: str, conversation_id: str = "default") -> AsyncGenerator[Dict[str, Any], None]:
        """Process a user query through the agent graph with streaming"""
        
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
            # Run classification step
            state = await self.classify_query(initial_state)
            yield {
                "type": "step",
                "step": state["steps"][-1],
                "progress": 20
            }
            
            query_type = state["query_type"]
            
            # Route based on query type
            if query_type == "retrieval":
                # Document retrieval
                state = await self.retrieve_documents(state)
                yield {
                    "type": "step",
                    "step": state["steps"][-1],
                    "progress": 50
                }
                
                # Context analysis
                state = await self.analyze_context(state)
                yield {
                    "type": "step", 
                    "step": state["steps"][-1],
                    "progress": 70
                }
                
            
            # Build response context
            history = self.conversation_memory.get(conversation_id, [])
            context_parts = []
            
            if history:
                context_parts.append("Recent conversation context:")
                for exchange in history[-3:]:
                    if 'question' in exchange and 'answer' in exchange:
                        context_parts.append(f"User asked: {exchange['question']}")
                        answer_text = exchange['answer'][:500]
                        context_parts.append(f"You responded: {answer_text}...")
            
            # Add query-specific context
            if query_type == "retrieval":
                docs = state.get('retrieved_docs', [])
                if docs and docs[0].get('content'):
                    context_parts.append(f"\nRelevant information: {docs[0]['content'][:500]}...")
            
            context = "\n".join(context_parts) if context_parts else "No previous context"
            
            # Generate clean streaming prompt
            prompt = f"""
            {context}
            
            Current question: "{question}"
            
            Answer this question naturally and helpfully. If you have relevant information from documents, use it to provide a comprehensive answer.
            """
            
            # Stream the response
            yield {
                "type": "step",
                "step": {
                    "node": "ResponseGenerator",
                    "status": "in_progress", 
                    "timestamp": time.time() * 1000,
                    "data": {"streaming": True}
                },
                "progress": 80
            }
            
            full_response = ""
            async for token in self.stream_response(prompt):
                full_response += token
                yield {
                    "type": "token",
                    "content": token,
                    "progress": min(95, 80 + (len(full_response) / 10))
                }
            
            # Save to memory
            self.conversation_memory.setdefault(conversation_id, []).append({
                "question": question,
                "answer": full_response[:800],
                "query_type": query_type,
                "timestamp": time.time()
            })
            
            # Keep only last 10 exchanges
            if len(self.conversation_memory[conversation_id]) > 10:
                self.conversation_memory[conversation_id] = self.conversation_memory[conversation_id][-10:]
            
            # Final metadata
            total_time = 0
            if state["steps"]:
                start_time = state["steps"][0]["timestamp"]
                end_time = time.time() * 1000
                total_time = int(end_time - start_time)
            
            yield {
                "type": "complete",
                "metadata": {
                    "query_type": query_type,
                    "total_processing_time_ms": total_time,
                    "documents_used": len(state.get("retrieved_docs", [])),
                    "steps_executed": len(state["steps"]),
                    "model_used": "gemini-2.0-flash-exp",
                    "memory_enabled": True,
                    "streaming_enabled": True
                },
                "progress": 100
            }
            
        except Exception as e:
            logger.error(f"Error processing streaming query: {e}")
            yield {
                "type": "error",
                "error": str(e),
                "progress": 100
            }

# Global agent instance
_streaming_agent_instance = None

def get_streaming_agent():
    """Get or create the singleton streaming agent instance"""
    global _streaming_agent_instance
    if _streaming_agent_instance is None:
        _streaming_agent_instance = StreamingInsightFlowAgent()
    return _streaming_agent_instance