from home.models import Category, Product

# Clear existing data
Category.objects.all().delete()
Product.objects.all().delete()

# Create categories
electronics = Category.objects.create(name="Electronics", description="Electronic devices and gadgets")
fashion = Category.objects.create(name="Fashion", description="Clothing and accessories")
home_cat = Category.objects.create(name="Home & Garden", description="Home and garden items")

# Create products
products_data = [
    {"name": "Wireless Headphones", "price": 99.99, "discount_price": 79.99, "category": electronics, "stock": 50, "is_featured": True, "description": "Premium wireless headphones with noise cancellation"},
    {"name": "Smartwatch", "price": 299.99, "discount_price": 249.99, "category": electronics, "stock": 30, "is_featured": True, "description": "Advanced smartwatch with fitness tracking"},
    {"name": "USB-C Cable", "price": 14.99, "discount_price": None, "category": electronics, "stock": 200, "is_featured": False, "description": "High-speed USB-C charging cable"},
    {"name": "Casual T-Shirt", "price": 29.99, "discount_price": 19.99, "category": fashion, "stock": 100, "is_featured": True, "description": "Comfortable casual cotton t-shirt"},
    {"name": "Blue Jeans", "price": 59.99, "discount_price": 49.99, "category": fashion, "stock": 80, "is_featured": False, "description": "Classic blue denim jeans"},
    {"name": "Desk Lamp", "price": 49.99, "discount_price": 39.99, "category": home_cat, "stock": 45, "is_featured": True, "description": "LED desk lamp with adjustable brightness"},
]

for data in products_data:
    Product.objects.create(
        name=data["name"],
        price=data["price"],
        discount_price=data["discount_price"],
        category=data["category"],
        stock=data["stock"],
        is_featured=data["is_featured"],
        description=data["description"],
        rating=4.5
    )

print("✅ Categories and products created successfully!")
