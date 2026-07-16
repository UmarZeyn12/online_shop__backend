from django.contrib.auth.models import User
from rest_framework import serializers
from apps.main.models import UserProfile, UserFavorites, UserCart, CartItem


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ["user", "image", "is_seller"]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["image"]


class UserFavoritesSerializer(serializers.ModelSerializer):
    from apps.api.serializers.product import ProductSerializer

    user = UserSerializer(read_only=True)
    products = ProductSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = UserFavorites
        fields = [
            "user",
            "products",
        ]


class CartItemSerializer(serializers.ModelSerializer):
    from apps.api.serializers.product import ProductSerializer

    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "product",
            "quantity",
        ]


class UserCartSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    items = CartItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = UserCart
        fields = [
            "user",
            "items",
        ]


class CartItemQuantityUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(
        min_value=1,
    )
