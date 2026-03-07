"""
SwasthCart AI - MCP (Model Context Protocol) Tool Definitions
Technical edge: Structured tool calling for AI agents following the MCP specification
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MCP TOOL SCHEMA DEFINITIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class MCPToolParameter:
    """MCP tool parameter schema"""
    name: str
    type: str
    description: str
    required: bool = True
    enum: Optional[List[str]] = None


@dataclass
class MCPTool:
    """MCP tool definition following Model Context Protocol spec"""
    name: str
    description: str
    parameters: List[MCPToolParameter] = field(default_factory=list)

    def to_schema(self) -> Dict:
        """Convert to MCP-compatible JSON schema"""
        properties = {}
        required = []
        for param in self.parameters:
            prop = {"type": param.type, "description": param.description}
            if param.enum:
                prop["enum"] = param.enum
            properties[param.name] = prop
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }


@dataclass
class MCPToolResult:
    """Result from MCP tool execution"""
    tool_name: str
    success: bool
    data: Any
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "tool_name": self.tool_name,
            "success": self.success,
            "data": self.data,
            "error": self.error
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SWASTHCART MCP TOOL REGISTRY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SwasthCartToolRegistry:
    """
    MCP Tool Registry for SwasthCart AI.

    Provides structured tool definitions that AI agents (Bedrock Claude, LangChain agents)
    can use for function calling. Follows Model Context Protocol patterns.

    Available Tools:
    1. analyze_product_risk - Analyze health risk for a specific product
    2. search_health_guidelines - Search medical guidelines knowledge base
    3. get_cart_health_score - Calculate overall cart health score
    4. suggest_alternatives - Find healthier product alternatives
    5. get_nutrition_summary - Get nutritional breakdown
    """

    def __init__(self):
        self.tools = self._register_tools()
        self._handlers = {}

    def _register_tools(self) -> List[MCPTool]:
        """Register all available MCP tools"""
        return [
            MCPTool(
                name="analyze_product_risk",
                description="Analyze the health risk score of a grocery product for specific health conditions. Returns a risk score (0-100), risk level, and detailed reasoning.",
                parameters=[
                    MCPToolParameter("product_id", "string", "The product ID to analyze"),
                    MCPToolParameter("health_conditions", "array", "List of health conditions e.g. ['Diabetes', 'Hypertension']"),
                    MCPToolParameter("use_rag", "boolean", "Whether to use RAG pipeline for enhanced analysis", required=False),
                ]
            ),
            MCPTool(
                name="search_health_guidelines",
                description="Search the medical guidelines knowledge base using semantic similarity. Returns relevant guidelines from ADA, AHA, WHO, NKF and other authoritative sources.",
                parameters=[
                    MCPToolParameter("query", "string", "Search query describing the health concern"),
                    MCPToolParameter("condition", "string", "Specific health condition to filter by", required=False),
                    MCPToolParameter("top_k", "integer", "Number of results to return (default: 5)", required=False),
                ]
            ),
            MCPTool(
                name="get_cart_health_score",
                description="Calculate the overall health score for the current shopping cart. Returns score (0-100), risk breakdown, and improvement suggestions.",
                parameters=[
                    MCPToolParameter("cart_items", "array", "List of product IDs in the cart"),
                    MCPToolParameter("health_conditions", "array", "User's health conditions"),
                ]
            ),
            MCPTool(
                name="suggest_alternatives",
                description="Find healthier product alternatives for a high-risk item. Searches the product catalog for items in the same category with lower risk scores.",
                parameters=[
                    MCPToolParameter("product_id", "string", "The high-risk product to find alternatives for"),
                    MCPToolParameter("health_conditions", "array", "User's health conditions"),
                    MCPToolParameter("max_results", "integer", "Maximum number of alternatives (default: 3)", required=False),
                ]
            ),
            MCPTool(
                name="get_nutrition_summary",
                description="Get a nutritional summary and health impact analysis for a product. Includes sodium, sugar, preservatives, and allergen information.",
                parameters=[
                    MCPToolParameter("product_id", "string", "The product ID to summarize"),
                ]
            ),
        ]

    def register_handler(self, tool_name: str, handler_fn):
        """Register a handler function for a tool"""
        self._handlers[tool_name] = handler_fn

    def execute_tool(self, tool_name: str, arguments: Dict) -> MCPToolResult:
        """Execute a registered tool with given arguments"""
        if tool_name not in self._handlers:
            return MCPToolResult(
                tool_name=tool_name,
                success=False,
                data=None,
                error=f"No handler registered for tool: {tool_name}"
            )

        try:
            result = self._handlers[tool_name](**arguments)
            return MCPToolResult(
                tool_name=tool_name,
                success=True,
                data=result
            )
        except Exception as e:
            return MCPToolResult(
                tool_name=tool_name,
                success=False,
                data=None,
                error=str(e)
            )

    def get_tool_schemas(self) -> List[Dict]:
        """Get all tool schemas in MCP format (for AI agent tool_use)"""
        return [tool.to_schema() for tool in self.tools]

    def get_bedrock_tool_config(self) -> Dict:
        """Get tool configuration formatted for AWS Bedrock tool_use"""
        return {
            "tools": [
                {
                    "toolSpec": {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": {
                            "json": tool.to_schema()["function"]["parameters"]
                        }
                    }
                }
                for tool in self.tools
            ]
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL HANDLER IMPLEMENTATIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def create_tool_registry(products: List[Dict], risk_engine, rag_chain) -> SwasthCartToolRegistry:
    """Create a fully configured tool registry with handlers"""
    registry = SwasthCartToolRegistry()

    def analyze_product_risk(product_id: str, health_conditions: List[str], use_rag: bool = True) -> Dict:
        product = next((p for p in products if p.get('product_id') == product_id), None)
        if not product:
            return {"error": f"Product {product_id} not found"}

        if use_rag and rag_chain:
            result = rag_chain.assess_risk(
                product_data=product,
                health_conditions=health_conditions,
                base_score=0
            )
            return result
        return {"score": 0, "reasoning": "No analysis available"}

    def search_health_guidelines(query: str, condition: str = None, top_k: int = 5) -> List[Dict]:
        if condition:
            query = f"{condition} {query}"
        return rag_chain.retrieve_guidelines(query, k=top_k) if rag_chain else []

    def get_nutrition_summary(product_id: str) -> Dict:
        product = next((p for p in products if p.get('product_id') == product_id), None)
        if not product:
            return {"error": f"Product {product_id} not found"}
        return {
            "name": product.get("name"),
            "sodium_mg": product.get("sodium_mg"),
            "sugar_g": product.get("sugar_g"),
            "has_preservatives": product.get("has_preservatives"),
            "allergens": product.get("allergens", []),
            "ingredients": product.get("ingredients", []),
        }

    registry.register_handler("analyze_product_risk", analyze_product_risk)
    registry.register_handler("search_health_guidelines", search_health_guidelines)
    registry.register_handler("get_nutrition_summary", get_nutrition_summary)

    return registry


def get_mcp_status() -> Dict[str, Any]:
    """Get MCP tool calling status"""
    registry = SwasthCartToolRegistry()
    return {
        "tools_registered": len(registry.tools),
        "tool_names": [t.name for t in registry.tools],
        "mcp_compatible": True,
        "bedrock_tool_use": True,
        "schemas_available": len(registry.get_tool_schemas()),
    }
