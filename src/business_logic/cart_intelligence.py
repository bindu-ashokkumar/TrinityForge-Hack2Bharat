"""
Cart Intelligence - Cart management and health scoring
"""

from typing import List
from copy import deepcopy

from src.models import Cart, CartItem, Product, HealthProfile, ProductSuggestion
from src.business_logic.risk_scoring_engine import RiskScoringEngine


class CartIntelligence:
    """Manages cart state and calculates cart-level health scores"""
    
    def __init__(self, risk_scoring_engine: RiskScoringEngine):
        self.risk_scoring_engine = risk_scoring_engine
    
    def add_product(
        self,
        cart: Cart,
        product: Product,
        health_profile: HealthProfile
    ) -> Cart:
        """Add product to cart and recalculate health score"""
        # Calculate risk score for the product
        risk_score = self.risk_scoring_engine.calculate_risk_score(product, health_profile)
        
        # Create cart item
        cart_item = CartItem(product=product, risk_score=risk_score)
        
        # Add to cart
        new_cart = deepcopy(cart)
        new_cart.items.append(cart_item)
        
        # Recalculate cart health score
        new_cart.health_score = self.calculate_cart_health_score(new_cart)
        
        return new_cart
    
    def remove_product(self, cart: Cart, product_id: str) -> Cart:
        """Remove product from cart and recalculate health score"""
        new_cart = deepcopy(cart)
        new_cart.items = [item for item in new_cart.items if item.product.product_id != product_id]
        
        # Recalculate cart health score
        new_cart.health_score = self.calculate_cart_health_score(new_cart)
        
        return new_cart
    
    def calculate_cart_health_score(self, cart: Cart) -> float:
        """
        Calculate weighted average of all product risk scores.
        
        Formula:
        Cart Health Score = 100 - (Sum of all product risk scores / Number of products)
        
        Higher cart health score = healthier cart
        """
        if not cart.items:
            return 100.0
        
        total_risk = sum(item.risk_score.value for item in cart.items)
        average_risk = total_risk / len(cart.items)
        
        # Convert risk to health score (inverse relationship)
        health_score = 100 - average_risk
        
        return max(0, min(100, health_score))
    
    def get_high_risk_items(self, cart: Cart) -> List[Product]:
        """Return products with risk score >= 71"""
        return [item.product for item in cart.items if item.risk_score.value >= 71]
    
    def suggest_improvements(
        self,
        cart: Cart,
        all_products: List[Product],
        health_profile: HealthProfile
    ) -> List[ProductSuggestion]:
        """
        Suggest lower-risk alternatives for high-risk items.
        
        For each high-risk item:
        1. Find products in same category
        2. Filter to products with risk score < 40
        3. Return top 3 by lowest risk score
        """
        suggestions = []
        high_risk_items = self.get_high_risk_items(cart)
        
        for high_risk_product in high_risk_items:
            # Find alternatives in same category
            alternatives = [
                p for p in all_products
                if p.category == high_risk_product.category
                and p.product_id != high_risk_product.product_id
            ]
            
            # Calculate risk scores for alternatives
            alternative_scores = []
            for alt_product in alternatives:
                risk_score = self.risk_scoring_engine.calculate_risk_score(
                    alt_product, health_profile, use_bedrock=False  # Use rule-based for speed
                )
                if risk_score.value < 40:  # Only safe alternatives
                    alternative_scores.append((alt_product, risk_score))
            
            # Sort by lowest risk score
            alternative_scores.sort(key=lambda x: x[1].value)
            
            # Take top 3
            for alt_product, alt_risk_score in alternative_scores[:3]:
                # Get original risk score
                original_risk = next(
                    (item.risk_score.value for item in cart.items if item.product.product_id == high_risk_product.product_id),
                    0
                )
                
                risk_reduction = ((original_risk - alt_risk_score.value) / original_risk * 100) if original_risk > 0 else 0
                
                suggestions.append(ProductSuggestion(
                    original_product=high_risk_product,
                    suggested_product=alt_product,
                    risk_reduction=risk_reduction
                ))
        
        return suggestions
