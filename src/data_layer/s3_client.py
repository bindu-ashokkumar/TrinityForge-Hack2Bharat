"""
S3 Client for product data management
"""

import json
import time
from typing import List
import boto3
from botocore.exceptions import ClientError

from src.models import Product


class S3Error(Exception):
    """S3 operation error"""
    pass


class S3Client:
    """Manages product data retrieval from S3"""
    
    def __init__(self, bucket_name: str, region: str, **kwargs):
        self.s3 = boto3.client('s3', region_name=region, **kwargs)
        self.bucket_name = bucket_name
        self.max_retries = 3
        self.retry_delay = 1  # seconds
    
    def load_products(self, key: str = "products.json") -> List[Product]:
        """
        Load product dataset from S3.
        
        Returns:
            List of Product objects with validated fields
        
        Raises:
            S3Error: If load fails after 3 retries
        """
        for attempt in range(self.max_retries):
            try:
                response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
                data = json.loads(response['Body'].read().decode('utf-8'))
                
                products = []
                for product_data in data.get('products', []):
                    if self._validate_product(product_data):
                        products.append(Product(
                            product_id=product_data['product_id'],
                            name=product_data['name'],
                            image_url=product_data['image_url'],
                            price=product_data['price'],
                            ingredients=product_data['ingredients'],
                            sodium_mg=product_data['sodium_mg'],
                            sugar_g=product_data['sugar_g'],
                            has_preservatives=product_data['has_preservatives'],
                            category=product_data['category'],
                            allergens=product_data.get('allergens', []),
                            ingredients_image=product_data.get('ingredients_image', '')
                        ))
                    else:
                        print(f"Warning: Skipping invalid product: {product_data.get('name', 'Unknown')}")
                
                return products
                
            except ClientError as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"S3 load failed (attempt {attempt + 1}/{self.max_retries}), retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise S3Error(f"Failed to load products from S3 after {self.max_retries} attempts: {str(e)}")
            except Exception as e:
                raise S3Error(f"Unexpected error loading products from S3: {str(e)}")
    
    def _validate_product(self, product_data: dict) -> bool:
        """Validate product has all required fields"""
        required_fields = [
            'product_id', 'name', 'image_url', 'price', 'ingredients',
            'sodium_mg', 'sugar_g', 'has_preservatives', 'category'
        ]
        
        for field in required_fields:
            if field not in product_data:
                return False
        
        # Validate types
        try:
            assert isinstance(product_data['product_id'], str)
            assert isinstance(product_data['name'], str)
            assert isinstance(product_data['image_url'], str)
            assert isinstance(product_data['price'], (int, float))
            assert isinstance(product_data['ingredients'], list)
            assert isinstance(product_data['sodium_mg'], (int, float))
            assert isinstance(product_data['sugar_g'], (int, float))
            assert isinstance(product_data['has_preservatives'], bool)
            assert isinstance(product_data['category'], str)
            return True
        except AssertionError:
            return False
