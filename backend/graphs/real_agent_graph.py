from typing import TypedDict, List, Dict, Any
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.embeddings import SentenceTransformerEmbeddings
from langgraph.graph import StateGraph, END
import time
import os
from dotenv import load_dotenv
import logging

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


class RealInsightFlowAgent:
    def __init__(self):
        self.memory = ConversationBufferMemory(return_messages=True)
        
        # Initialize Gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=api_key,
            temperature=0.1
        )
        
        # Initialize embeddings
        self.embeddings = SentenceTransformerEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Load vector store
        from retriever.real_vector_store import RealVectorStore
        self.vector_store = RealVectorStore(self.embeddings)
        
        # Load tools
        from tools.real_tools import RealToolRegistry
        self.tools = RealToolRegistry()
        
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("classify_query", self.classify_query)
        graph.add_node("retrieve_documents", self.retrieve_documents)
        graph.add_node("analyze_context", self.analyze_context)
        graph.add_node("use_tools", self.use_tools)
        graph.add_node("generate_response", self.generate_response)
        
        # Add conditional edges
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
    
    def classify_query(self, state: AgentState) -> AgentState:
        """Classify the user query to determine processing path"""
        start_time = time.time()
        question = state["question"]
        
        classification_prompt = f"""
        Analyze this user question and classify it into one of these categories:
        
        1. "retrieval" - Questions that need document search and analysis
        2. "tool_use" - Questions that need calculations, web search, or external data
        3. "direct" - Simple questions that can be answered directly
        
        Question: "{question}"
        
        Consider:
        - Does it ask for specific information that might be in documents?
        - Does it need calculations, current data, or web search?
        - Can it be answered with general knowledge?
        
        Respond with just the category name and a brief reason.
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=classification_prompt)])
            classification_text = response.content.lower()
            
            if "retrieval" in classification_text:
                query_type = "retrieval"
            elif "tool_use" in classification_text:
                query_type = "tool_use"
            else:
                query_type = "direct"
                
        except Exception as e:
            logger.error(f"Error in query classification: {e}")
            query_type = "direct"  # Safe fallback
        
        step = {
            "node": "QueryClassifier",
            "status": "completed",
            "timestamp": time.time() * 1000,
            "data": {
                "query_type": query_type,
                "classification_reasoning": classification_text if 'classification_text' in locals() else "fallback classification",
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
    
    def retrieve_documents(self, state: AgentState) -> AgentState:
        """Retrieve relevant documents using real vector search"""
        start_time = time.time()
        question = state["question"]
        
        try:
            # Perform real similarity search
            docs = self.vector_store.similarity_search(question, k=5)
            
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
    
    def analyze_context(self, state: AgentState) -> AgentState:
        """Analyze retrieved documents and form reasoning"""
        start_time = time.time()
        question = state["question"]
        docs = state["retrieved_docs"]
        
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
        
        # Create context from documents
        context = "\n\n".join([
            f"Document {i+1} (Source: {doc.get('metadata', {}).get('source', 'unknown')}):\n{doc.get('content', '')}"
            for i, doc in enumerate(docs[:3])  # Use top 3 documents
        ])
        
        analysis_prompt = f"""
        Based on the following documents, analyze how they relate to the user's question.
        
        Question: "{question}"
        
        Documents:
        {context}
        
        Provide a structured analysis including:
        1. Relevance of the documents to the question
        2. Key information that answers the question
        3. Any gaps or limitations in the available information
        4. Confidence level in the answer (1-10)
        
        Keep the analysis concise but thorough.
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
            analysis = response.content
            
            step = {
                "node": "ContextAnalyzer",
                "status": "completed",
                "timestamp": time.time() * 1000,
                "data": {
                    "analysis_type": "document_analysis",
                    "documents_analyzed": len(docs),
                    "analysis_length": len(analysis),
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
    
    def use_tools(self, state: AgentState) -> AgentState:
        """Use appropriate tools based on query type"""
        start_time = time.time()
        question = state["question"]
        
        # Determine which tool to use
        tool_selection_prompt = f"""
        Based on this question, which tool should be used?
        
        Question: "{question}"
        
        Available tools:
        - web_search: For current information, news, or general web queries
        - calculator: For mathematical calculations
        
        Respond with the tool name and the specific query/calculation to perform.
        Format: tool_name: specific_query
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=tool_selection_prompt)])
            tool_instruction = response.content.strip()
            
            tool_result = None
            if "calculator:" in tool_instruction.lower():
                expression = tool_instruction.split(":", 1)[1].strip()
                tool_result = self.tools.execute_tool("calculator", "calculate", expression=expression)
            elif "web_search:" in tool_instruction.lower():
                query = tool_instruction.split(":", 1)[1].strip()
                tool_result = self.tools.execute_tool("web_search", "search", query=query)
            
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
            
            # Store tool result for response generation
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
    
    def generate_response(self, state: AgentState) -> AgentState:
        """Generate final response using Gemini"""
        start_time = time.time()
        question = state["question"]
        query_type = state.get("query_type", "direct")
        
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
        Please provide a comprehensive answer to the user's question.
        
        Question: "{question}"
        
        Context: {context}
        
        Guidelines:
        1. Be accurate and helpful
        2. Cite sources when available
        3. If using retrieved documents, reference them appropriately
        4. If using tool results, explain the findings clearly
        5. Be conversational but professional
        6. If information is limited, acknowledge it
        
        Provide a clear, well-structured response.
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=response_prompt)])
            final_response = response.content
            
            step = {
                "node": "ResponseGenerator",
                "status": "completed",
                "timestamp": time.time() * 1000,
                "data": {
                    "response_length": len(final_response),
                    "word_count": len(final_response.split()),
                    "sources_referenced": len(state.get('retrieved_docs', [])),
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

    async def process_query(self, question: str, conversation_id: str = "default") -> Dict[str, Any]:
        """Process a user query through the real agent graph"""
        
        # Initialize state
        initial_state = AgentState(
            messages=[],
            question=question,
            retrieved_docs=[],
            analysis="",
            response="",
            steps=[],
            conversation_id=conversation_id,
            query_type=""
        )
        
        try:
            # Run the graph
            result = self.graph.invoke(initial_state)
            
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
                    "model_used": "gemini-1.5-pro"
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
                    "model_used": "gemini-1.5-pro"
                }
            }