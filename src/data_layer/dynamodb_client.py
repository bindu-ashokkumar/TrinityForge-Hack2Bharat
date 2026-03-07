"""
DynamoDB Client for session and cart persistence
"""

import json
from typing import Optional
from datetime import datetime, timedelta
from decimal import Decimal
import boto3
from botocore.exceptions import ClientError

from src.models import Cart, HealthProfile, SessionState, CartItem, Product, RiskScore


class DynamoDBError(Exception):
    """DynamoDB operation error"""
    pass


def convert_floats_to_decimal(obj):
    """Recursively convert all floats to Decimal for DynamoDB"""
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(item) for item in obj]
    return obj


class DynamoDBClient:
    """Manages session and cart persistence"""
    
    def __init__(self, table_name: str, region: str, ttl_hours: int = 2):
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)
        self.ttl_hours = ttl_hours
    
    def save_session(
        self,
        session_id: str,
        cart: Cart,
        health_profile: HealthProfile,
        swasth_mode: bool
    ) -> None:
        """Save session state to DynamoDB with TTL"""
        try:
            ttl = int((datetime.utcnow() + timedelta(hours=self.ttl_hours)).timestamp())
            
            item = {
                'session_id': session_id,
                'cart': self._serialize_cart(cart),
                'health_profile': {
                    'mode': health_profile.mode,
                    'conditions': health_profile.conditions
                },
                'swasth_mode': swasth_mode,
                'ttl': ttl,
                'last_updated': datetime.utcnow().isoformat()
            }
            
            # Convert all floats to Decimal
            item = convert_floats_to_decimal(item)
            
            self.table.put_item(Item=item)
            
        except ClientError as e:
            raise DynamoDBError(f"Failed to save session: {str(e)}")
    
    def load_session(self, session_id: str) -> Optional[SessionState]:
        """Load session state from DynamoDB"""
        try:
            response = self.table.get_item(Key={'session_id': session_id})
            
            if 'Item' not in response:
                return None
            
            item = response['Item']
            
            # Deserialize cart
            cart = self._deserialize_cart(item['cart'])
            
            # Deserialize health profile
            health_profile = HealthProfile(
                mode=item['health_profile']['mode'],
                conditions=item['health_profile']['conditions']
            )
            
            return SessionState(
                session_id=session_id,
                cart=cart,
                health_profile=health_profile,
                swasth_mode=item['swasth_mode'],
                last_updated=datetime.fromisoformat(item['last_updated'])
            )
            
        except ClientError as e:
            raise DynamoDBError(f"Failed to load session: {str(e)}")
    
    def delete_session(self, session_id: str) -> None:
        """Delete session from DynamoDB"""
        try:
            self.table.delete_item(Key={'session_id': session_id})
        except ClientError as e:
            raise DynamoDBError(f"Failed to delete session: {str(e)}")
    
    def _serialize_cart(self, cart: Cart) -> dict:
        """Serialize cart to DynamoDB format"""
        return {
            'items': [
                {
                    'product_id': item.product.product_id,
                    'product_name': item.product.name,
                    'price': item.product.price,
                    'risk_score': item.risk_score.value,
                    'risk_badge': item.risk_score.badge,
                    'risk_reasoning': item.risk_score.reasoning
                }
                for item in cart.items
            ],
            'health_score': cart.health_score
        }
    
    def _deserialize_cart(self, cart_data: dict) -> Cart:
        """Deserialize cart from DynamoDB format"""
        # Note: This is a simplified deserialization that only stores minimal product info
        # In a full implementation, you'd need to fetch full product details from S3
        items = []
        for item_data in cart_data.get('items', []):
            # Create minimal product object (full details would be fetched separately)
            product = Product(
                product_id=item_data['product_id'],
                name=item_data['product_name'],
                image_url='',  # Would be fetched from S3
                price=item_data['price'],
                ingredients=[],  # Would be fetched from S3
                sodium_mg=0.0,  # Would be fetched from S3
                sugar_g=0.0,  # Would be fetched from S3
                has_preservatives=False,  # Would be fetched from S3
                category=''  # Would be fetched from S3
            )
            
            risk_score = RiskScore(
                value=item_data['risk_score'],
                badge=item_data['risk_badge'],
                reasoning=item_data.get('risk_reasoning', '')
            )
            
            items.append(CartItem(product=product, risk_score=risk_score))
        
        return Cart(
            items=items,
            health_score=cart_data.get('health_score', 100.0)
        )
