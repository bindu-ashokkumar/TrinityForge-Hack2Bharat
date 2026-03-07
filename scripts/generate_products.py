"""
Generate 10 unique products for SwasthCart AI
"""

import json
import random

# 10 unique products with better, unique images
PRODUCTS = [
    {
        "product_id": "prod_001",
        "name": "Orange Juice",
        "image_url": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400&h=300&fit=crop",
        "price": 8.03,
        "category": "beverages",
        "ingredients": ["Water", "Orange Concentrate", "Sugar", "Citric Acid"],
        "sodium_mg": 45.0,
        "sugar_g": 22.0,
        "has_preservatives": False,
        "allergens": []
    },
    {
        "product_id": "prod_002",
        "name": "Apple Juice",
        "image_url": "https://images.unsplash.com/photo-1560180474-e8f2d2b9c3d0?w=400&h=300&fit=crop",
        "price": 12.42,
        "category": "beverages",
        "ingredients": ["Water", "Apple Concentrate", "Sugar", "Vitamin C"],
        "sodium_mg": 35.0,
        "sugar_g": 24.0,
        "has_preservatives": False,
        "allergens": []
    },
    {
        "product_id": "prod_003",
        "name": "Potato Chips",
        "image_url": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=400&h=300&fit=crop",
        "price": 5.99,
        "category": "snacks",
        "ingredients": ["Potatoes", "Vegetable Oil", "Salt"],
        "sodium_mg": 480.0,
        "sugar_g": 1.0,
        "has_preservatives": True,
        "allergens": []
    },
    {
        "product_id": "prod_004",
        "name": "Chocolate Cookies",
        "image_url": "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=400&h=300&fit=crop",
        "price": 7.50,
        "category": "snacks",
        "ingredients": ["Wheat Flour", "Sugar", "Chocolate Chips", "Butter", "Eggs"],
        "sodium_mg": 220.0,
        "sugar_g": 18.0,
        "has_preservatives": True,
        "allergens": ["Wheat", "Eggs", "Milk"]
    },
    {
        "product_id": "prod_005",
        "name": "Whole Milk",
        "image_url": "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&h=300&fit=crop",
        "price": 6.25,
        "category": "dairy",
        "ingredients": ["Milk", "Vitamin D"],
        "sodium_mg": 105.0,
        "sugar_g": 12.0,
        "has_preservatives": False,
        "allergens": ["Milk", "Lactose"]
    },
    {
        "product_id": "prod_006",
        "name": "Greek Yogurt",
        "image_url": "https://images.unsplash.com/photo-1571212515416-fca2ce42e2b9?w=400&h=300&fit=crop",
        "price": 9.99,
        "category": "dairy",
        "ingredients": ["Milk", "Live Cultures", "Sugar"],
        "sodium_mg": 75.0,
        "sugar_g": 15.0,
        "has_preservatives": False,
        "allergens": ["Milk"]
    },
    {
        "product_id": "prod_007",
        "name": "White Bread",
        "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400&h=300&fit=crop",
        "price": 4.50,
        "category": "grains",
        "ingredients": ["Wheat Flour", "Water", "Yeast", "Sugar", "Salt"],
        "sodium_mg": 320.0,
        "sugar_g": 5.0,
        "has_preservatives": True,
        "allergens": ["Wheat", "Gluten"]
    },
    {
        "product_id": "prod_008",
        "name": "Breakfast Cereal",
        "image_url": "https://images.unsplash.com/photo-1564890369478-c89ca6d9cde9?w=400&h=300&fit=crop",
        "price": 8.75,
        "category": "grains",
        "ingredients": ["Corn", "Sugar", "Salt", "Vitamins"],
        "sodium_mg": 280.0,
        "sugar_g": 12.0,
        "has_preservatives": True,
        "allergens": []
    },
    {
        "product_id": "prod_009",
        "name": "Frozen Pizza",
        "image_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400&h=300&fit=crop",
        "price": 11.99,
        "category": "frozen",
        "ingredients": ["Wheat Flour", "Cheese", "Tomato Sauce", "Preservatives"],
        "sodium_mg": 720.0,
        "sugar_g": 8.0,
        "has_preservatives": True,
        "allergens": ["Wheat", "Milk"]
    },
    {
        "product_id": "prod_010",
        "name": "Vanilla Ice Cream",
        "image_url": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&h=300&fit=crop",
        "price": 10.50,
        "category": "frozen",
        "ingredients": ["Milk", "Cream", "Sugar", "Vanilla Extract"],
        "sodium_mg": 85.0,
        "sugar_g": 21.0,
        "has_preservatives": False,
        "allergens": ["Milk"]
    }
]


def main():
    """Generate and save 10 unique products"""
    print("Generating 10 unique products...")
    
    dataset = {"products": PRODUCTS}
    
    # Save to JSON file
    output_file = "data/products.json"
    with open(output_file, 'w') as f:
        json.dump(dataset, f, indent=2)
    
    print(f"✅ Generated {len(PRODUCTS)} unique products")
    print(f"📁 Saved to {output_file}")
    print("\nNext steps:")
    print("1. Upload: aws s3 cp data/products.json s3://swasthcart-products/products.json --region ap-south-2")
    print("2. Run app: streamlit run app.py")


if __name__ == "__main__":
    main()
