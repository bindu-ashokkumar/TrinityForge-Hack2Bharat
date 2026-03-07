"""
Risk Scoring Engine - Rule-based and AI-enhanced risk assessment
"""

import json
from typing import Tuple

from src.models import Product, HealthProfile, RiskScore
from src.data_layer.bedrock_client import BedrockClient, BedrockTimeoutError, BedrockError


class RiskScoringEngine:
    """Calculates risk scores using rule-based thresholds and Bedrock enhancement"""
    
    def __init__(self, bedrock_client: BedrockClient):
        self.bedrock_client = bedrock_client
        
        # Stricter thresholds for health conditions
        self.rule_thresholds = {
            "diabetes": {
                "sugar_g_high": 5,      # High risk threshold
                "sugar_g_moderate": 3,  # Moderate risk threshold
            },
            "hypertension": {
                "sodium_mg_high": 300,     # High risk threshold
                "sodium_mg_moderate": 200, # Moderate risk threshold
            },
            "heart_disease": {
                "sodium_mg_high": 250,
                "sugar_g_high": 8,
            },
            "obesity": {
                "sugar_g_high": 6,
            },
            "high_cholesterol": {
                "sodium_mg_high": 300,
            },
            "general": {
                "sugar_g": 15,
                "sodium_mg": 600
            }
        }
        
        # High-risk categories for specific conditions
        self.high_risk_categories = {
            "diabetes": ["frozen", "snacks", "beverages"],  # Desserts, sweets, sugary drinks
            "hypertension": ["snacks", "frozen"],           # Salty snacks, processed foods
            "obesity": ["frozen", "snacks"],                # High-calorie foods
        }
    
    def calculate_risk_score(
        self,
        product: Product,
        health_profile: HealthProfile,
        use_bedrock: bool = True
    ) -> RiskScore:
        """
        Calculate risk score for a product.
        
        Steps:
        1. Apply rule-based scoring using thresholds
        2. If use_bedrock=True, enhance with Bedrock reasoning
        3. Return RiskScore with value (0-100) and reasoning
        """
        # Step 1: Rule-based scoring
        base_score = self._apply_rule_based_scoring(product, health_profile)
        
        # Step 2: Bedrock enhancement (if enabled)
        if use_bedrock:
            try:
                enhanced_score, reasoning = self._enhance_with_bedrock(
                    product, health_profile, base_score
                )
                final_score = min(100, max(0, enhanced_score))
            except (BedrockTimeoutError, BedrockError) as e:
                print(f"Bedrock enhancement failed: {str(e)}, using rule-based score")
                final_score = base_score
                reasoning = self._generate_rule_based_reasoning(product, health_profile, base_score)
        else:
            final_score = base_score
            reasoning = self._generate_rule_based_reasoning(product, health_profile, base_score)
        
        # Step 3: Assign badge
        badge = self._assign_risk_badge(final_score)
        
        return RiskScore(
            value=final_score,
            badge=badge,
            reasoning=reasoning
        )
    
    def _apply_rule_based_scoring(
        self,
        product: Product,
        health_profile: HealthProfile
    ) -> float:
        """Apply threshold rules to calculate base risk score"""
        score = 0.0
        
        if health_profile.conditions:
            # User has specific health conditions
            for condition in health_profile.conditions:
                condition_lower = condition.lower()
                
                # DIABETES - Sugar is critical
                if condition_lower == "diabetes":
                    if product.sugar_g >= self.rule_thresholds["diabetes"]["sugar_g_high"]:
                        score += 50  # High sugar = major risk
                    elif product.sugar_g >= self.rule_thresholds["diabetes"]["sugar_g_moderate"]:
                        score += 25  # Moderate sugar = moderate risk
                    
                    # Extra penalty for high-risk categories (desserts, sweets)
                    if product.category in self.high_risk_categories.get("diabetes", []):
                        score += 20
                
                # HYPERTENSION - Sodium is critical
                if condition_lower == "hypertension":
                    if product.sodium_mg >= self.rule_thresholds["hypertension"]["sodium_mg_high"]:
                        score += 50  # High sodium = major risk
                    elif product.sodium_mg >= self.rule_thresholds["hypertension"]["sodium_mg_moderate"]:
                        score += 25  # Moderate sodium = moderate risk
                    
                    # Extra penalty for high-risk categories (salty snacks)
                    if product.category in self.high_risk_categories.get("hypertension", []):
                        score += 15
                
                # HEART DISEASE - Both sodium and sugar matter
                if condition_lower == "heart disease":
                    if product.sodium_mg >= self.rule_thresholds["heart_disease"]["sodium_mg_high"]:
                        score += 40
                    if product.sugar_g >= self.rule_thresholds["heart_disease"]["sugar_g_high"]:
                        score += 30
                
                # OBESITY - High sugar and calories
                if condition_lower == "obesity":
                    if product.sugar_g >= self.rule_thresholds["obesity"]["sugar_g_high"]:
                        score += 40
                    if product.category in self.high_risk_categories.get("obesity", []):
                        score += 20
                
                # HIGH CHOLESTEROL - Sodium matters
                if condition_lower == "high cholesterol":
                    if product.sodium_mg >= self.rule_thresholds["high_cholesterol"]["sodium_mg_high"]:
                        score += 35
                
                # KIDNEY DISEASE - Sodium is very critical
                if condition_lower == "kidney disease":
                    if product.sodium_mg >= 200:
                        score += 55
                
                # THYROID - Preservatives and processed foods
                if condition_lower == "thyroid":
                    if product.has_preservatives:
                        score += 30
                
                # CELIAC DISEASE - Check for gluten allergens
                if condition_lower == "celiac disease":
                    if "Wheat" in product.allergens or "Gluten" in product.allergens:
                        score += 90  # Extremely dangerous
                
                # LACTOSE INTOLERANCE - Check for dairy
                if condition_lower == "lactose intolerance":
                    if "Milk" in product.allergens or "Lactose" in product.allergens:
                        score += 85  # Very dangerous
                
                # IBS - Preservatives and high sodium
                if condition_lower == "ibs":
                    if product.has_preservatives:
                        score += 35
                    if product.sodium_mg >= 400:
                        score += 25
            
            # Preservatives are concerning for most conditions
            if product.has_preservatives:
                score += 15
        else:
            # No specific conditions - use general health thresholds
            if product.sugar_g > self.rule_thresholds["general"]["sugar_g"]:
                score += 20
            
            if product.sodium_mg > self.rule_thresholds["general"]["sodium_mg"]:
                score += 20
            
            if product.has_preservatives:
                score += 10
        
        # Cap at 100
        return min(100, score)
    
    def _enhance_with_bedrock(
        self,
        product: Product,
        health_profile: HealthProfile,
        base_score: float
    ) -> Tuple[float, str]:
        """Send to Bedrock for enhanced scoring and reasoning"""
        prompt = f"""You are a health nutrition expert. Analyze this product for health risks.

Product: {product.name}
Ingredients: {', '.join(product.ingredients[:10])}  # Limit to first 10 ingredients
Sodium: {product.sodium_mg}mg
Sugar: {product.sugar_g}g
Preservatives: {product.has_preservatives}

User Health Profile: {', '.join(health_profile.conditions) if health_profile.conditions else 'No specific conditions'}

Rule-based risk score: {base_score}/100

Task:
1. Review the nutritional content and ingredients
2. Consider the user's health conditions
3. Provide a risk score adjustment (-20 to +20)
4. Explain your reasoning in 2-3 sentences

Response format (JSON only):
{{
  "score_adjustment": <number between -20 and 20>,
  "reasoning": "<brief explanation>"
}}"""
        
        response = self.bedrock_client.invoke_model(prompt, max_tokens=300, temperature=0.3)
        
        # Parse response
        score_adjustment = response.get('score_adjustment', 0)
        reasoning = response.get('reasoning', 'AI-enhanced risk assessment')
        
        # Apply adjustment
        enhanced_score = base_score + score_adjustment
        
        return enhanced_score, reasoning
    
    def _assign_risk_badge(self, score: float) -> str:
        """Assign risk badge based on score"""
        if score <= 40:
            return "🟢"
        elif score <= 70:
            return "🟡"
        else:
            return "🔴"
    
    def _generate_rule_based_reasoning(
        self,
        product: Product,
        health_profile: HealthProfile,
        score: float
    ) -> str:
        """Generate explanation using only rule-based logic"""
        reasons = []
        
        if health_profile.conditions:
            for condition in health_profile.conditions:
                condition_lower = condition.lower()
                
                # DIABETES
                if condition_lower == "diabetes":
                    if product.sugar_g >= self.rule_thresholds["diabetes"]["sugar_g_high"]:
                        reasons.append(f"⚠️ High sugar content ({product.sugar_g}g) can cause dangerous blood glucose spikes")
                    elif product.sugar_g >= self.rule_thresholds["diabetes"]["sugar_g_moderate"]:
                        reasons.append(f"Moderate sugar content ({product.sugar_g}g) may affect blood glucose control")
                    
                    if product.category in self.high_risk_categories.get("diabetes", []):
                        reasons.append(f"This {product.category} category typically contains high sugar and should be limited")
                
                # HYPERTENSION
                if condition_lower == "hypertension":
                    if product.sodium_mg >= self.rule_thresholds["hypertension"]["sodium_mg_high"]:
                        reasons.append(f"⚠️ High sodium content ({product.sodium_mg}mg) can significantly increase blood pressure")
                    elif product.sodium_mg >= self.rule_thresholds["hypertension"]["sodium_mg_moderate"]:
                        reasons.append(f"Moderate sodium content ({product.sodium_mg}mg) may elevate blood pressure")
                
                # HEART DISEASE
                if condition_lower == "heart disease":
                    if product.sodium_mg >= self.rule_thresholds["heart_disease"]["sodium_mg_high"]:
                        reasons.append(f"High sodium ({product.sodium_mg}mg) increases cardiovascular strain")
                    if product.sugar_g >= self.rule_thresholds["heart_disease"]["sugar_g_high"]:
                        reasons.append(f"High sugar ({product.sugar_g}g) contributes to heart disease risk")
                
                # OBESITY
                if condition_lower == "obesity":
                    if product.sugar_g >= self.rule_thresholds["obesity"]["sugar_g_high"]:
                        reasons.append(f"High sugar content ({product.sugar_g}g) contributes to weight gain")
                
                # HIGH CHOLESTEROL
                if condition_lower == "high cholesterol":
                    if product.sodium_mg >= self.rule_thresholds["high_cholesterol"]["sodium_mg_high"]:
                        reasons.append(f"High sodium ({product.sodium_mg}mg) can worsen cholesterol-related risks")
                
                # KIDNEY DISEASE
                if condition_lower == "kidney disease":
                    if product.sodium_mg >= 200:
                        reasons.append(f"⚠️ Sodium content ({product.sodium_mg}mg) is dangerous for kidney function")
                
                # CELIAC DISEASE
                if condition_lower == "celiac disease":
                    if "Wheat" in product.allergens or "Gluten" in product.allergens:
                        reasons.append("🚫 CONTAINS GLUTEN - Extremely dangerous for celiac disease")
                
                # LACTOSE INTOLERANCE
                if condition_lower == "lactose intolerance":
                    if "Milk" in product.allergens or "Lactose" in product.allergens:
                        reasons.append("🚫 CONTAINS LACTOSE - Will cause digestive distress")
                
                # IBS
                if condition_lower == "ibs":
                    if product.has_preservatives:
                        reasons.append("Preservatives can trigger IBS symptoms")
                    if product.sodium_mg >= 400:
                        reasons.append(f"High sodium ({product.sodium_mg}mg) may worsen IBS")
            
            # General preservative warning
            if product.has_preservatives and not any("preservative" in r.lower() for r in reasons):
                reasons.append("Contains preservatives which may be concerning for your health conditions")
        else:
            # No specific conditions
            if product.sugar_g > self.rule_thresholds["general"]["sugar_g"]:
                reasons.append(f"High sugar content ({product.sugar_g}g) exceeds healthy limits")
            
            if product.sodium_mg > self.rule_thresholds["general"]["sodium_mg"]:
                reasons.append(f"High sodium content ({product.sodium_mg}mg) exceeds healthy limits")
            
            if product.has_preservatives:
                reasons.append("Contains preservatives")
        
        if reasons:
            return " • ".join(reasons)
        else:
            return "✅ This product appears to be within healthy nutritional ranges for your profile."
