import os
import random
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth.models import User


FIRST_NAMES = [
    "John",
    "Michael",
    "David",
    "James",
    "Daniel",
    "William",
    "Alexander",
    "Emma",
    "Sophia",
    "Olivia",
    "Emily",
    "Isabella",
    "Mia",
    "Charlotte",
    "Amelia",
]

LAST_NAMES = [
    "Smith",
    "Johnson",
    "Brown",
    "Williams",
    "Jones",
    "Miller",
    "Davis",
    "Wilson",
    "Taylor",
    "Moore",
    "Anderson",
    "Thomas",
    "Jackson",
    "White",
    "Harris",
]


PASSWORD = "12345678"
USERS_TO_CREATE = 10


print("Creating test users...\n")

created = 0

for i in range(1, USERS_TO_CREATE + 1):
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)

    username = f"user{i}"
    email = f"{username}@example.com"

    if User.objects.filter(username=username).exists():
        print(f"{username} already exists.")
        continue

    User.objects.create_user(
        username=username,
        password=PASSWORD,
        first_name=first_name,
        last_name=last_name,
        email=email,
    )

    created += 1
    print(f"Created {username}")


print("\nDone!")
print(f"Created {created} new users.")
print(f"Total users: {User.objects.count()}")
print(f"Password for all test users: {PASSWORD}")