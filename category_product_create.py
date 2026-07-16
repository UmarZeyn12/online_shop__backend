import os
import random
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.main.models import Category, Product
from django.contrib.auth.models import User

admin = User.objects.get(username="admin")

CATEGORIES = {
    "Electronics": {
        "products": [
            "iPhone 16",
            "Samsung Galaxy S25",
            "MacBook Air M4",
            "Gaming Mouse",
            "Mechanical Keyboard",
            "Gaming Monitor",
            "Wireless Earbuds",
            "Smart Watch",
            "Bluetooth Speaker",
            "Power Bank",
        ],
    },
    "Clothing": {
        "products": [
            "T-Shirt",
            "Hoodie",
            "Jeans",
            "Sneakers",
            "Jacket",
            "Cap",
            "Sweater",
            "Shorts",
            "Socks",
            "Backpack",
        ],
    },
    "Books": {
        "products": [
            "Python Basics",
            "Clean Code",
            "Atomic Habits",
            "Deep Work",
            "Django Guide",
            "React Handbook",
            "Algorithms",
            "Data Structures",
            "The Pragmatic Programmer",
            "Design Patterns",
        ],
    },
    "Sports": {
        "products": [
            "Football",
            "Basketball",
            "Tennis Racket",
            "Yoga Mat",
            "Running Shoes",
            "Dumbbells",
            "Skipping Rope",
            "Fitness Band",
            "Cycling Helmet",
            "Boxing Gloves",
        ],
    },
    "Home": {
        "products": [
            "Chair",
            "Desk",
            "Lamp",
            "Sofa",
            "Curtains",
            "Coffee Table",
            "Bookshelf",
            "Mirror",
            "Carpet",
            "Wardrobe",
        ],
    },
    "Beauty": {
        "products": [
            "Shampoo",
            "Conditioner",
            "Face Cream",
            "Perfume",
            "Lipstick",
            "Mascara",
            "Body Lotion",
            "Hair Dryer",
            "Electric Razor",
            "Face Wash",
        ],
    },
    "Toys": {
        "products": [
            "LEGO Set",
            "Toy Car",
            "Puzzle",
            "Drone",
            "RC Car",
            "Stuffed Bear",
            "Chess Set",
            "Rubik Cube",
            "Board Game",
            "Action Figure",
        ],
    },
    "Food": {
        "products": [
            "Chocolate",
            "Coffee",
            "Green Tea",
            "Cookies",
            "Pasta",
            "Rice",
            "Olive Oil",
            "Honey",
            "Peanut Butter",
            "Orange Juice",
        ],
    },
    "Automotive": {
        "products": [
            "Car Vacuum",
            "Dash Camera",
            "Phone Holder",
            "Motor Oil",
            "Air Freshener",
            "Seat Cover",
            "Car Charger",
            "Jump Starter",
            "Tool Kit",
            "LED Headlights",
        ],
    },
    "Office": {
        "products": [
            "Notebook",
            "Pen Set",
            "Office Chair",
            "Printer",
            "Paper Pack",
            "Stapler",
            "Desk Organizer",
            "Whiteboard",
            "Calculator",
            "Monitor Stand",
        ],
    },
}

print("Creating categories and products...\n")

for category_name, data in CATEGORIES.items():
    category, _ = Category.objects.get_or_create(
        slug=category_name.lower().replace(" ", "-"),
        defaults={
            "name": category_name,
        },
    )

    for product_name in data["products"]:
        Product.objects.get_or_create(
            slug=product_name.lower().replace(" ", "-"),
            defaults={
                "name": product_name,
                "description": f"{product_name} is a high-quality product from the {category_name} category.",
                "price": random.randint(50_000, 5_000_000),
                "stock_amount": random.randint(100, 1000),
                "preview": None,
                "category": category,
                "posted_by": admin,
            },
        )

print("Done!")
print(f"Categories: {Category.objects.count()}")
print(f"Products: {Product.objects.count()}")
