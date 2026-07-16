from rest_framework import serializers
from apps.main.models import OrderItem, UserProfile
from rest_framework import serializers
from apps.main.models import Order, OrderItem
from .product import ProductSerializer
from .user import UserSerializer


class SellerOrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "quantity",
            "total_price",
        ]


class SellerOrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "status",
            "created_at",
            "updated_at",
            "items",
            "total_price",
        ]

    def get_items(self, obj):
        seller = self.context["user"]

        items = obj.items.filter(
            product__posted_by=seller,
        )

        return SellerOrderItemSerializer(
            items,
            many=True,
            context=self.context,
        ).data

    def get_total_price(self, obj):
        seller = self.context["user"]

        seller_items = obj.items.filter(product__posted_by=seller)

        total_price = sum(item.total_price for item in seller_items)
        return total_price


class UserProfileIsSellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["is_seller"]

    def update(self, instance, validated_data):
        instance.is_seller = not instance.is_seller
        instance.save()

        return instance
