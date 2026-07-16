import os
import random
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth.models import User
from apps.main.models import Product, Order, OrderItem


ORDERS_TO_CREATE = 100

STATUSES = [
    Order.Status.PENDING,
    Order.Status.PAID,
    Order.Status.PROCESSING,
    Order.Status.SHIPPED,
    Order.Status.COMPLETED,
    Order.Status.CANCELLED,
    Order.Status.REFUNDED,
]


users = list(User.objects.all())
products = list(Product.objects.all())

if not users:
    raise Exception("No users found. Run create_users.py first.")

if not products:
    raise Exception("No products found. Run create_products.py first.")

print("Creating orders...\n")

for _ in range(ORDERS_TO_CREATE):
    user = random.choice(users)

    order = Order.objects.create(
        user=user,
        status=random.choice(STATUSES),
    )

    products_count = random.randint(1, 5)

    selected_products = random.sample(
        products,
        min(products_count, len(products))
    )

    for product in selected_products:
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=random.randint(1, 3),
        )

print("Done!")
print(f"Orders: {Order.objects.count()}")
print(f"Order Items: {OrderItem.objects.count()}")