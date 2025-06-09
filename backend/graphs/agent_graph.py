from typing import TypedDict, List, Dict, Any
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from langgraph.graph import StateGraph, END
import time
import json


class AgentState(TypedDict):
    messages: List[BaseMessage]
    question: str
    retrieved_docs: List[Dict[str, Any]]
    analysis: str
    response: str
    steps: List[Dict[str, Any]]
    conversation_id: str


class InsightFlowAgent:
    def __init__(self):
        self.memory = ConversationBufferMemory(return_messages=True)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("input_processor", self.process_input)
        graph.add_node("retriever", self.retrieve_documents)
        graph.add_node("analyzer", self.analyze_context)
        graph.add_node("responder", self.generate_response)
        
        # Add edges
        graph.add_edge("input_processor", "retriever")
        graph.add_edge("retriever", "analyzer")
        graph.add_edge("analyzer", "responder")
        graph.add_edge("responder", END)
        
        # Set entry point
        graph.set_entry_point("input_processor")
        
        return graph.compile()
    
    def process_input(self, state: AgentState) -> AgentState:
        start_time = time.time()
        
        # Parse and clean the input question
        question = state["question"].strip()
        
        # Add step tracking
        step = {
            "node": "InputProcessor",
            "status": "completed",
            "timestamp": time.time() * 1000,
            "data": {
                "parsed_query": question,
                "word_count": len(question.split())
            }
        }
        
        state["steps"].append(step)
        state["messages"] = [HumanMessage(content=question)]
        
        return state
    
    def retrieve_documents(self, state: AgentState) -> AgentState:
        start_time = time.time()
        
        # Mock document retrieval
        mock_docs = [
            {
                "content": "Sample document content about the query topic...",
                "source": "document_1.pdf",
                "score": 0.95
            },
            {
                "content": "Additional relevant information from another source...",
                "source": "document_2.pdf", 
                "score": 0.87
            },
            {
                "content": "Supporting context and examples...",
                "source": "document_3.pdf",
                "score": 0.72
            }
        ]
        
        step = {
            "node": "Retriever",
            "status": "completed",
            "timestamp": time.time() * 1000,
            "data": {
                "documents_found": len(mock_docs),
                "avg_score": sum(doc["score"] for doc in mock_docs) / len(mock_docs),
                "sources": [doc["source"] for doc in mock_docs]
            }
        }
        
        state["steps"].append(step)
        state["retrieved_docs"] = mock_docs
        
        return state
    
    def analyze_context(self, state: AgentState) -> AgentState:
        start_time = time.time()
        
        # Mock analysis process
        question = state["question"]
        docs = state["retrieved_docs"]
        
        analysis = f"""
        Analysis of query: "{question}"
        
        Based on {len(docs)} retrieved documents, I can see that:
        1. The query relates to {self._identify_topic(question)}
        2. The most relevant sources provide comprehensive coverage
        3. The information appears to be current and reliable
        
        Key insights:
        - Primary topic focus: {self._identify_topic(question)}
        - Evidence strength: High
        - Completeness: Good coverage found
        """
        
        step = {
            "node": "Analyzer",
            "status": "completed",
            "timestamp": time.time() * 1000,
            "data": {
                "reasoning": "Analyzed retrieved context and query intent",
                "topic_identified": self._identify_topic(question),
                "confidence": 0.89
            }
        }
        
        state["steps"].append(step)
        state["analysis"] = analysis
        
        return state
    
    def generate_response(self, state: AgentState) -> AgentState:
        start_time = time.time()
        
        question = state["question"]
        docs = state["retrieved_docs"]
        analysis = state["analysis"]
        
        # Generate a comprehensive response
        response = f"""Based on my analysis of your question "{question}", here's what I found:

{self._generate_contextual_answer(question, docs)}

This response is based on {len(docs)} relevant documents I retrieved and analyzed. The information appears to be comprehensive and up-to-date.

Would you like me to dive deeper into any specific aspect of this topic?"""
        
        step = {
            "node": "Responder",
            "status": "completed",
            "timestamp": time.time() * 1000,
            "data": {
                "response_length": len(response),
                "word_count": len(response.split()),
                "sources_cited": len(docs)
            }
        }
        
        state["steps"].append(step)
        state["response"] = response
        state["messages"].append(AIMessage(content=response))
        
        return state
    
    def _identify_topic(self, question: str) -> str:
        # Simple topic identification
        question_lower = question.lower()
        if any(word in question_lower for word in ["tax", "taxes", "taxation"]):
            return "taxation"
        elif any(word in question_lower for word in ["freelance", "freelancer", "freelancing"]):
            return "freelancing"
        elif any(word in question_lower for word in ["canada", "canadian"]):
            return "canadian_regulations"
        else:
            return "general_information"
    
    def _generate_contextual_answer(self, question: str, docs: List[Dict]) -> str:
        # Generate a contextual answer based on the question and docs
        topic = self._identify_topic(question)
        
        if topic == "taxation":
            return """Key tax considerations include:

• **Income Reporting**: All freelance income must be reported as business income
• **Deductible Expenses**: Home office, equipment, software, and professional development costs
• **GST/HST Registration**: Required if annual income exceeds $30,000
• **Quarterly Payments**: Consider making quarterly tax installments to avoid penalties
• **Record Keeping**: Maintain detailed records of all income and expenses

The documents I reviewed emphasize the importance of proper documentation and staying current with CRA requirements."""
        
        elif topic == "freelancing":
            return """For freelancers, important considerations include:

• **Business Structure**: Most freelancers operate as sole proprietors
• **Client Contracts**: Always use written agreements outlining scope, payment terms, and deliverables
• **Invoicing**: Implement a systematic invoicing process with clear payment terms
• **Professional Development**: Invest in skills that align with market demand
• **Networking**: Build relationships within your industry for referral opportunities

The retrieved documents highlight these as fundamental practices for successful freelancing."""
        
        else:
            return f"""Based on the retrieved documents, here are the key points relevant to your question:

• The topic appears to be well-documented with multiple authoritative sources
• Current best practices emphasize a systematic approach
• Implementation should consider both immediate and long-term implications
• Regular review and updates are recommended to stay current

The information I found provides a solid foundation for understanding this topic."""

    async def process_query(self, question: str, conversation_id: str = "default") -> Dict[str, Any]:
        """Process a user query through the agent graph"""
        
        # Initialize state
        initial_state = AgentState(
            messages=[],
            question=question,
            retrieved_docs=[],
            analysis="",
            response="",
            steps=[],
            conversation_id=conversation_id
        )
        
        # Run the graph
        result = self.graph.invoke(initial_state)
        
        return {
            "answer": result["response"],
            "steps": result["steps"],
            "conversation_id": conversation_id,
            "metadata": {
                "tokens_used": len(result["response"].split()),
                "latency_ms": int((result["steps"][-1]["timestamp"] - result["steps"][0]["timestamp"]) if result["steps"] else 0),
                "documents_retrieved": len(result["retrieved_docs"])
            }
        }