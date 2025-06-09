from typing import Dict, Any, Optional
import random
import time
from datetime import datetime


class MockWeatherTool:
    """Mock weather checking tool"""
    
    @staticmethod
    def get_weather(location: str) -> Dict[str, Any]:
        cities = {
            "toronto": {"temp": 15, "condition": "Partly Cloudy"},
            "vancouver": {"temp": 18, "condition": "Rainy"},
            "montreal": {"temp": 12, "condition": "Sunny"},
            "calgary": {"temp": 8, "condition": "Snow"},
        }
        
        location_lower = location.lower()
        if location_lower in cities:
            weather = cities[location_lower]
        else:
            weather = {
                "temp": random.randint(-10, 25),
                "condition": random.choice(["Sunny", "Cloudy", "Rainy", "Snow"])
            }
        
        return {
            "location": location,
            "temperature": weather["temp"],
            "condition": weather["condition"],
            "timestamp": datetime.now().isoformat()
        }


class MockEmailTool:
    """Mock email sending tool"""
    
    @staticmethod
    def send_email(to: str, subject: str, body: str) -> Dict[str, Any]:
        # Simulate processing time
        time.sleep(0.5)
        
        return {
            "status": "sent",
            "message_id": f"msg_{random.randint(100000, 999999)}",
            "to": to,
            "subject": subject,
            "sent_at": datetime.now().isoformat()
        }


class MockProductTool:
    """Mock product information tool"""
    
    @staticmethod
    def get_product_info(product_id: str) -> Dict[str, Any]:
        products = {
            "laptop_001": {
                "name": "Professional Laptop Pro",
                "price": 1299.99,
                "stock": 15,
                "rating": 4.5
            },
            "phone_002": {
                "name": "SmartPhone X1",
                "price": 899.99,
                "stock": 8,
                "rating": 4.2
            },
            "tablet_003": {
                "name": "Tablet Ultra",
                "price": 599.99,
                "stock": 22,
                "rating": 4.7
            }
        }
        
        if product_id in products:
            product = products[product_id]
        else:
            product = {
                "name": f"Product {product_id}",
                "price": random.uniform(99.99, 1999.99),
                "stock": random.randint(0, 50),
                "rating": random.uniform(3.0, 5.0)
            }
        
        return {
            "product_id": product_id,
            **product,
            "last_updated": datetime.now().isoformat()
        }


class MockCalculatorTool:
    """Mock calculator tool"""
    
    @staticmethod
    def calculate(expression: str) -> Dict[str, Any]:
        try:
            # Simple evaluation for demo (in production, use a safer parser)
            result = eval(expression.replace('^', '**'))
            return {
                "expression": expression,
                "result": result,
                "status": "success"
            }
        except Exception as e:
            return {
                "expression": expression,
                "error": str(e),
                "status": "error"
            }


class ToolRegistry:
    """Registry for all available tools"""
    
    def __init__(self):
        self.tools = {
            "weather": MockWeatherTool(),
            "email": MockEmailTool(),
            "product": MockProductTool(),
            "calculator": MockCalculatorTool()
        }
    
    def get_tool(self, tool_name: str):
        return self.tools.get(tool_name)
    
    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        return {
            "weather": {
                "description": "Get weather information for a location",
                "methods": ["get_weather"],
                "parameters": {"location": "string"}
            },
            "email": {
                "description": "Send email messages",
                "methods": ["send_email"],
                "parameters": {"to": "string", "subject": "string", "body": "string"}
            },
            "product": {
                "description": "Get product information and inventory",
                "methods": ["get_product_info"],
                "parameters": {"product_id": "string"}
            },
            "calculator": {
                "description": "Perform mathematical calculations",
                "methods": ["calculate"],
                "parameters": {"expression": "string"}
            }
        }
    
    def execute_tool(self, tool_name: str, method: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool method with given parameters"""
        tool = self.get_tool(tool_name)
        if not tool:
            return {"error": f"Tool {tool_name} not found"}
        
        if not hasattr(tool, method):
            return {"error": f"Method {method} not found in tool {tool_name}"}
        
        try:
            method_func = getattr(tool, method)
            result = method_func(**kwargs)
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}