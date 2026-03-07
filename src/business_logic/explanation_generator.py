"""
Explanation Generator - Generates health risk explanations using Bedrock
"""

from src.models import Product, RiskScore, HealthProfile, Explanation
from src.data_layer.bedrock_client import BedrockClient, BedrockError


class ExplanationGenerator:
    """Generates explanations for risk scores"""
    
    def __init__(self, bedrock_client: BedrockClient):
        self.bedrock_client = bedrock_client
    
    def generate(
        self,
        product: Product,
        risk_score: RiskScore,
        health_profile: HealthProfile
    ) -> Explanation:
        """
        Generate explanation with fallback handling.
        
        Try:
          1. Bedrock AI explanation
        Catch BedrockError:
          2. Rule-based explanation (no AI)
        """
        try:
            # Try Bedrock explanation
            return self._generate_bedrock_explanation(product, risk_score, health_profile)
        except BedrockError as e:
            print(f"Bedrock unavailable: {str(e)}, falling back to rule-based")
            return self._generate_rule_based_explanation(product, risk_score, health_profile)
        except Exception as e:
            print(f"Unexpected error: {str(e)}, falling back to rule-based")
            return self._generate_rule_based_explanation(product, risk_score, health_profile)
    
    def _generate_bedrock_explanation(
        self,
        product: Product,
        risk_score: RiskScore,
        health_profile: HealthProfile
    ) -> Explanation:
        """Generate explanation using Bedrock AI"""
        prompt = f"""Explain why this product has a risk score of {risk_score.value}/100.

Product: {product.name}
Ingredients: {', '.join(product.ingredients[:10])}
Sodium: {product.sodium_mg}mg
Sugar: {product.sugar_g}g
Preservatives: {product.has_preservatives}
User Health Conditions: {', '.join(health_profile.conditions) if health_profile.conditions else 'None'}

Provide a brief 2-3 sentence explanation in plain language.

Response format (JSON only):
{{
  "explanation": "<your explanation>",
  "ingredient_triggers": ["<ingredient1>", "<ingredient2>"],
  "condition_mappings": {{
    "<ingredient>": ["<condition1>"]
  }}
}}"""
        
        response = self.bedrock_client.invoke_model(prompt, max_tokens=300, temperature=0.3)
        
        return Explanation(
            text=response.get('explanation', risk_score.reasoning),
            ingredient_triggers=response.get('ingredient_triggers', []),
            condition_mappings=response.get('condition_mappings', {}),
            citations=[],
            confidence=70.0  # Good confidence with AI
        )
    
    def _generate_rule_based_explanation(
        self,
        product: Product,
        risk_score: RiskScore,
        health_profile: HealthProfile
    ) -> Explanation:
        """Generate explanation using only rule-based logic"""
        ingredient_triggers = []
        condition_mappings = {}
        
        # Identify triggers based on thresholds
        if product.sugar_g > 10:
            ingredient_triggers.append(f"Sugar ({product.sugar_g}g)")
            if "Diabetes" in health_profile.conditions:
                condition_mappings["Sugar"] = ["Diabetes"]
        
        if product.sodium_mg > 400:
            ingredient_triggers.append(f"Sodium ({product.sodium_mg}mg)")
            if "Hypertension" in health_profile.conditions:
                condition_mappings["Sodium"] = ["Hypertension"]
        
        if product.has_preservatives:
            ingredient_triggers.append("Preservatives")
            if health_profile.conditions:
                condition_mappings["Preservatives"] = health_profile.conditions
        
        # Use the risk score reasoning as explanation
        explanation_text = risk_score.reasoning
        
        return Explanation(
            text=explanation_text,
            ingredient_triggers=ingredient_triggers,
            condition_mappings=condition_mappings,
            citations=[],
            confidence=50.0  # Medium confidence for rule-based
        )
