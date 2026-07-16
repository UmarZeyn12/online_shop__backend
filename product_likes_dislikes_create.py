import os
import random
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth.models import User
from apps.main.models import (
    Product,
    ProductLike,
    ProductDislike,
)

users = list(User.objects.filter(is_superuser=False))
products = Product.objects.all()

print("Creating product likes and dislikes...\n")

for product in products:
    like, _ = ProductLike.objects.get_or_create(product=product)
    dislike, _ = ProductDislike.objects.get_or_create(product=product)

    like.user.clear()
    dislike.user.clear()

    like_amount = random.randint(1, min(10, len(users)))
    like_users = random.sample(users, like_amount)

    remaining_users = [user for user in users if user not in like_users]

    if remaining_users:
        dislike_amount = random.randint(1, min(10, len(remaining_users)))
        dislike_users = random.sample(
            remaining_users,
            dislike_amount,
        )
    else:
        dislike_users = []

    like.user.add(*like_users)
    dislike.user.add(*dislike_users)

print("Done!")
print(f"Processed products: {products.count()}")
