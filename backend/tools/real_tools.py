from typing import Dict, Any
import requests
import os
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class RealWebSearchTool:
    """Real web search using Google Custom Search API"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_CSE_API_KEY")
        self.cse_id = os.getenv("GOOGLE_CSE_ID")
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Perform web search using Google Custom Search API"""
        
        if not self.api_key or not self.cse_id:
            return {
                "status": "error",
                "message": "Google Custom Search API credentials not configured. Using fallback search.",
                "results": self._fallback_search(query, num_results)
            }
        
        try:
            params = {
                "key": self.api_key,
                "cx": self.cse_id,
                "q": query,
                "num": min(num_results, 10)  # API limit is 10
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            for item in data.get("items", []):
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "displayLink": item.get("displayLink", "")
                })
            
            return {
                "status": "success",
                "query": query,
                "total_results": data.get("searchInformation", {}).get("totalResults", "0"),
                "search_time": data.get("searchInformation", {}).get("searchTime", "0"),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error in web search: {e}")
            return {
                "status": "error",
                "message": f"Search failed: {str(e)}",
                "results": self._fallback_search(query, num_results)
            }
    
    def _fallback_search(self, query: str, num_results: int) -> list:
        """Fallback search results when API is not available"""
        fallback_results = [
            {
                "title": f"Search result for '{query}' - Government Resource",
                "link": "https://www.canada.ca/en/revenue-agency",
                "snippet": f"Official information related to {query} from the Canada Revenue Agency. This would contain authoritative information about your query.",
                "displayLink": "canada.ca"
            },
            {
                "title": f"Professional Guide: {query}",
                "link": "https://www.cpacanada.ca",
                "snippet": f"Professional accounting guidance and resources related to {query}. Detailed explanations and best practices.",
                "displayLink": "cpacanada.ca"
            },
            {
                "title": f"Current Information: {query}",
                "link": "https://www.canada.ca/en/financial-consumer-agency",
                "snippet": f"Up-to-date financial and regulatory information about {query}. Consumer protection and guidance resources.",
                "displayLink": "canada.ca"
            }
        ]
        
        return fallback_results[:num_results]


class RealCalculatorTool:
    """Real calculator with enhanced mathematical capabilities"""
    
    def calculate(self, expression: str) -> Dict[str, Any]:
        """Perform real mathematical calculations"""
        
        try:
            # Clean the expression
            cleaned_expr = self._clean_expression(expression)
            
            if not cleaned_expr:
                return {
                    "status": "error",
                    "message": "Invalid or empty expression",
                    "expression": expression
                }
            
            # Evaluate the expression safely
            result = self._safe_eval(cleaned_expr)
            
            return {
                "status": "success",
                "expression": expression,
                "cleaned_expression": cleaned_expr,
                "result": result,
                "result_type": type(result).__name__,
                "timestamp": datetime.now().isoformat()
            }
            
        except ZeroDivisionError:
            return {
                "status": "error",
                "message": "Division by zero",
                "expression": expression
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Calculation error: {str(e)}",
                "expression": expression
            }
    
    def _clean_expression(self, expr: str) -> str:
        """Clean and validate the mathematical expression"""
        if not expr:
            return ""
        
        # Remove whitespace
        expr = expr.strip()
        
        # Replace common text representations
        replacements = {
            '^': '**',  # Power operator
            'x': '*',   # Multiplication
            '×': '*',   # Multiplication symbol
            '÷': '/',   # Division symbol
            'pi': '3.14159265359',
            'e': '2.71828182846'
        }
        
        for old, new in replacements.items():
            expr = expr.replace(old, new)
        
        # Only allow safe characters
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expr):
            raise ValueError("Expression contains invalid characters")
        
        return expr
    
    def _safe_eval(self, expression: str):
        """Safely evaluate mathematical expression"""
        # Create a safe namespace with only mathematical functions
        safe_dict = {
            "__builtins__": {},
            "abs": abs,
            "round": round,
            "pow": pow,
            "max": max,
            "min": min,
            "sum": sum
        }
        
        return eval(expression, safe_dict)


class RealEmailTool:
    """Real email functionality (demonstration only - no actual sending)"""
    
    def send_email(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        """Simulate sending an email (for security, actual sending is disabled)"""
        
        # Validate inputs
        if not to or not subject:
            return {
                "status": "error",
                "message": "Email address and subject are required"
            }
        
        # Simulate email sending
        email_data = {
            "status": "simulated",
            "message": "Email sending is simulated for security reasons",
            "details": {
                "to": to,
                "subject": subject,
                "body_length": len(body),
                "timestamp": datetime.now().isoformat(),
                "simulated_message_id": f"sim_{datetime.now().timestamp():.0f}"
            }
        }
        
        logger.info(f"Simulated email to {to} with subject: {subject}")
        
        return email_data


class RealDocumentAnalysisTool:
    """Real document analysis capabilities"""
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text content for various metrics"""
        
        if not text:
            return {"status": "error", "message": "No text provided"}
        
        # Basic text analysis
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        paragraphs = text.split('\n\n')
        
        # Word frequency (top 10)
        word_freq = {}
        for word in words:
            word = word.lower().strip('.,!?";')
            if len(word) > 3:  # Only count words longer than 3 chars
                word_freq[word] = word_freq.get(word, 0) + 1
        
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Readability estimate (simplified)
        avg_words_per_sentence = len(words) / max(len(sentences), 1)
        avg_chars_per_word = sum(len(word) for word in words) / max(len(words), 1)
        
        return {
            "status": "success",
            "analysis": {
                "character_count": len(text),
                "word_count": len(words),
                "sentence_count": len(sentences),
                "paragraph_count": len(paragraphs),
                "average_words_per_sentence": round(avg_words_per_sentence, 2),
                "average_characters_per_word": round(avg_chars_per_word, 2),
                "top_words": top_words,
                "reading_time_minutes": round(len(words) / 200, 1)  # Assuming 200 WPM
            },
            "timestamp": datetime.now().isoformat()
        }


class RealToolRegistry:
    """Registry for all real tools"""
    
    def __init__(self):
        self.tools = {
            "web_search": RealWebSearchTool(),
            "calculator": RealCalculatorTool(),
            "email": RealEmailTool(),
            "document_analysis": RealDocumentAnalysisTool()
        }
    
    def get_tool(self, tool_name: str):
        """Get a tool by name"""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """List all available tools with descriptions"""
        return {
            "web_search": {
                "description": "Search the web for current information using Google Custom Search",
                "methods": ["search"],
                "parameters": {"query": "string", "num_results": "integer (optional, default 5)"},
                "requires_api": True
            },
            "calculator": {
                "description": "Perform mathematical calculations and expressions",
                "methods": ["calculate"],
                "parameters": {"expression": "string (mathematical expression)"},
                "requires_api": False
            },
            "email": {
                "description": "Send emails (simulated for security)",
                "methods": ["send_email"],
                "parameters": {"to": "string", "subject": "string", "body": "string"},
                "requires_api": False
            },
            "document_analysis": {
                "description": "Analyze text documents for various metrics",
                "methods": ["analyze_text"],
                "parameters": {"text": "string"},
                "requires_api": False
            }
        }
    
    def execute_tool(self, tool_name: str, method: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool method with given parameters"""
        tool = self.get_tool(tool_name)
        if not tool:
            return {
                "status": "error",
                "message": f"Tool '{tool_name}' not found",
                "available_tools": list(self.tools.keys())
            }
        
        if not hasattr(tool, method):
            return {
                "status": "error",
                "message": f"Method '{method}' not found in tool '{tool_name}'",
                "available_methods": [m for m in dir(tool) if not m.startswith('_')]
            }
        
        try:
            method_func = getattr(tool, method)
            result = method_func(**kwargs)
            
            return {
                "status": "success",
                "tool": tool_name,
                "method": method,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error executing {tool_name}.{method}: {e}")
            return {
                "status": "error",
                "message": f"Tool execution failed: {str(e)}",
                "tool": tool_name,
                "method": method
            }