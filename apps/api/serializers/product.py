from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from slugify import slugify
from apps.main.models import (
    Category,
    Product,
    ProductLike,
    ProductDislike,
    ProductImage,
    ProductComment,
    OrderItem,
)
from .category import CategorySerializer
from rest_framework.permissions import IsAuthenticated


class ProductSerializer(serializers.ModelSerializer):
    permission_classes = [IsAuthenticated]
    category = CategorySerializer(read_only=True)
    ordered_count = serializers.IntegerField(read_only=True)
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    liked_by_user = serializers.SerializerMethodField()
    disliked_by_user = serializers.SerializerMethodField()
    posted_by = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "name",
            "slug",
            "in_stock",
            "stock_amount",
            "ordered_count",
            "likes_count",
            "dislikes_count",
            "liked_by_user",
            "disliked_by_user",
            "posted_by",
            "description",
            "preview",
            "category",
            "price",
            "created_at",
            "updated_at",
        ]

    def get_ordered_count(self, obj):
        result = OrderItem.objects.filter(product=obj).aggregate(total=Sum("quantity"))
        return result["total"] if result["total"] is not None else 0

    def get_likes_count(self, obj):
        if hasattr(obj, "likes"):
            return obj.likes.user.count()
        return 0

    def get_dislikes_count(self, obj):
        if hasattr(obj, "dislikes"):
            return obj.dislikes.user.count()
        return 0

    def get_liked_by_user(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        if not hasattr(obj, "likes"):
            return False
        return obj.likes.user.filter(id=request.user.id).exists()

    def get_disliked_by_user(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        if not hasattr(obj, "dislikes"):
            return False
        return obj.dislikes.user.filter(id=request.user.id).exists()

    def get_posted_by(self, obj):
        from .user import UserSerializer

        if obj.posted_by:
            return UserSerializer(obj.posted_by).data
        return None


class ProductLikeSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()

    class Meta:
        model = ProductLike
        fields = ["user", "product"]

    def get_user(self, obj):
        from .user import UserSerializer

        return UserSerializer(obj.user.all(), many=True).data

    def get_product(self, obj):
        return ProductSerializer(obj.product).data


class ProductDislikeSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()

    class Meta:
        model = ProductDislike
        fields = ["user", "product"]

    def get_user(self, obj):
        from .user import UserSerializer

        return UserSerializer(obj.user.all(), many=True).data

    def get_product(self, obj):
        return ProductSerializer(obj.product).data


class ProductCreateSerializer(serializers.ModelSerializer):
    preview = serializers.FileField(required=False)

    class Meta:
        model = Product
        fields = [
            "name",
            "slug",
            "preview",
            "description",
            "price",
            "stock_amount",
        ]
        read_only_fields = ["slug"]

    def create(self, validated_data):
        user = self.context.get("user")

        if not user or not user.is_authenticated:
            raise ValidationError({"message": "Not authenticated"})

        slug = slugify(validated_data.get("name"))

        if Product.objects.filter(slug=slug).exists():
            raise ValidationError({"message": "slug not unique"})

        category_slug = self.context.get("category_slug")

        try:
            category = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            raise ValidationError(
                {"message": f"Category '{category_slug}' does not exist"}
            )

        name = validated_data.get("name")
        description = validated_data.get("description")
        price = validated_data.get("price")
        posted_by = user
        stock_amount = validated_data.get("stock_amount")

        preview = validated_data.get("preview")

        if preview is None:
            preview = None

        newProductData = {
            "name": name,
            "description": description,
            "price": price,
            "preview": preview,
            "posted_by": posted_by,
            "stock_amount": stock_amount,
        }

        product = Product.objects.create(**newProductData, slug=slug, category=category)

        ProductLike.objects.create(product=product)
        ProductDislike.objects.create(product=product)

        return product


class ProductLikeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductLike
        fields = []

    def create(self, validated_data):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise ValidationError(
                {"message": "Authentication required to like products"}
            )

        user = request.user

        product_slug = self.context.get("product_slug")
        product = get_object_or_404(Product, slug=product_slug)

        product_like, created = ProductLike.objects.get_or_create(product=product)
        product_dislike, _ = ProductDislike.objects.get_or_create(product=product)

        if product_like.user.filter(id=user.id).exists():
            product_like.user.remove(user)
        else:
            product_like.user.add(user)
            if product_dislike.user.filter(id=user.id).exists():
                product_dislike.user.remove(user)

        return product_like


class ProductDislikeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDislike
        fields = []

    def create(self, validated_data):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise ValidationError(
                {"message": "Authentication required to dislike products"}
            )

        user = request.user

        product_slug = self.context.get("product_slug")
        product = get_object_or_404(Product, slug=product_slug)

        product_dislike, created = ProductDislike.objects.get_or_create(product=product)
        product_like, _ = ProductLike.objects.get_or_create(product=product)

        if product_dislike.user.filter(id=user.id).exists():
            product_dislike.user.remove(user)
        else:
            product_dislike.user.add(user)
            if product_like.user.filter(id=user.id).exists():
                product_like.user.remove(user)

        return product_dislike


class ProductUpdateSerializer(serializers.ModelSerializer):
    preview = serializers.FileField(required=False)

    class Meta:
        model = Product
        fields = ["name", "description", "price", "preview", "category", "stock_amount"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "product", "image"]


class ProductImageCreateSerializer(serializers.ModelSerializer):
    image = serializers.FileField()

    class Meta:
        model = ProductImage
        fields = ["image"]

    def create(self, validated_data):
        product = get_object_or_404(
            Product,
            slug=self.context["product_slug"],
        )

        user = self.context["user"]

        if product.posted_by != user:
            raise serializers.ValidationError(
                "You can upload images only to your own products."
            )

        return ProductImage.objects.create(
            image=validated_data["image"],
            product=product,
        )


class ProductImageUpdateSerializer(serializers.ModelSerializer):
    image = serializers.FileField()

    class Meta:
        model = ProductImage
        fields = ["image"]

    def update(self, instance, validated_data):
        image = validated_data.get("image")
        product = get_object_or_404(Product, slug=self.context.get("product_slug"))

        instance.image = image
        instance.product = product
        instance.save()

        return instance


class ProductCommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    product_slug = serializers.SlugRelatedField(
        source="product", slug_field="slug", read_only=True
    )

    class Meta:
        model = ProductComment
        fields = [
            "id",
            "username",
            "product_slug",
            "content",
            "created_at",
            "updated_at",
        ]


class ProductCommentCreateSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    product_slug = serializers.SlugRelatedField(
        source="product", slug_field="slug", read_only=True
    )

    class Meta:
        model = ProductComment
        fields = ["id", "user_name", "product_slug", "content"]

    def create(self, validated_data):
        user = self.context["request"].user
        if not user or not user.is_authenticated:
            raise serializers.ValidationError(
                {"message": "Authentication required to comment"}
            )

        request = self.context["request"]
        user = request.user

        product_slug = self.context["product_slug"]

        try:
            product = Product.objects.get(slug=product_slug)
        except Product.DoesNotExist:
            raise serializers.ValidationError({"product": "No product found"})

        return ProductComment.objects.create(
            user=user, product=product, **validated_data
        )


class ProductCommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductComment
        fields = ["content"]
