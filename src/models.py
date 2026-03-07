"""
Data models for SwasthCart AI
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class Product:
    """Grocery product with nutritional information"""
    product_id: str
    name: str
    display_image: str  # Path to product display image
    ingredients_image: str  # Path to ingredients label image
    price: float
    ingredients: List[str]
    sodium_mg: float
    sugar_g: float
    has_preservatives: bool
    category: str  # "snacks", "beverages", "dairy", etc.
    allergens: List[str] = field(default_factory=list)
    image_url: str = ""  # Backward compat for S3/DynamoDB modules


@dataclass
class HealthProfile:
    """User health profile with conditions"""
    mode: str  # "Individual" or "Family"
    conditions: List[str] = field(default_factory=list)  # ["Diabetes", "Hypertension", "Thyroid", "Depression"]


@dataclass
class RiskScore:
    """Product risk score with badge and reasoning"""
    value: float  # 0-100
    badge: str  # "🟢", "🟡", "🔴"
    reasoning: str  # From Bedrock or rule-based
    
    @property
    def risk_level(self) -> str:
        """Get risk level category"""
        if self.value <= 40:
            return "Safe"
        elif self.value <= 70:
            return "Moderate"
        else:
            return "High Risk"


@dataclass
class CartItem:
    """Item in shopping cart with risk assessment"""
    product: Product
    risk_score: RiskScore


@dataclass
class Cart:
    """Shopping cart with health intelligence"""
    items: List[CartItem] = field(default_factory=list)
    health_score: float = 100.0  # 0-100, higher is better
    
    @property
    def high_risk_count(self) -> int:
        """Count of high-risk items (score >= 71)"""
        return len([item for item in self.items if item.risk_score.value >= 71])
    
    @property
    def medium_risk_count(self) -> int:
        """Count of medium-risk items (41-70)"""
        return len([item for item in self.items if 41 <= item.risk_score.value <= 70])
    
    @property
    def total_price(self) -> float:
        """Calculate total price of all items in cart"""
        return sum(item.product.price for item in self.items)


@dataclass
class GuidelineSnippet:
    """Health guideline snippet from RAG retrieval"""
    text: str
    source: str
    similarity_score: float  # 0-1 from k-NN search


@dataclass
class Explanation:
    """Health risk explanation with citations"""
    text: str
    ingredient_triggers: List[str]
    condition_mappings: Dict[str, List[str]]
    citations: List[GuidelineSnippet]
    confidence: float  # 0-100
    disclaimer: str = "This tool provides informational guidance only and is not medical advice."


@dataclass
class SessionState:
    """User session state for persistence"""
    session_id: str
    cart: Cart
    health_profile: HealthProfile
    swasth_mode: bool
    last_updated: datetime


@dataclass
class ProductSuggestion:
    """Product alternative suggestion"""
    original_product: Product
    suggested_product: Product
    risk_reduction: float  # Percentage reduction in risk score
