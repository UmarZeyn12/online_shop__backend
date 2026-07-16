from rest_framework import serializers
from apps.main.models import (
    Product,
    Order,
    OrderItem,
)


class OrderItemSerializer(serializers.ModelSerializer):
    from apps.api.serializers.product import ProductSerializer

    product = ProductSerializer(
        read_only=True,
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "quantity",
            "total_price",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "status",
            "items",
            "created_at",
            "updated_at",
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = []

    def create(self, validated_data):
        return Order.objects.create(
            user=self.context["user"],
            **validated_data,
        )


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]


class OrderItemCreateSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(
        slug_field="slug", queryset=Product.objects.all()
    )

    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]

    def create(self, validated_data):
        order = self.context.get("order")
        product = validated_data.get("product")
        quantity = validated_data.get("quantity")

        return OrderItem.objects.create(order=order, product=product, quantity=quantity)


class OrderItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["quantity"]
