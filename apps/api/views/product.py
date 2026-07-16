from apps.api.serializers import product, order
from apps.main.models import (
    Product,
    ProductLike,
    ProductDislike,
    Order,
    ProductImage,
    ProductComment,
)
from drf_spectacular.utils import extend_schema
from apps.api.pagination import DefaultPagination
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models.functions import Coalesce
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.api.permissions import (
    IsSeller,
    IsProductOwnerOrReadOnly,
    IsCommentOwnerOrReadOnly,
    IsProductImageOwnerOrReadOnly,
)


class ProductListCreateView(generics.ListCreateAPIView):
    pagination_class = DefaultPagination

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = {
        "price": ["gte", "lte"],
    }

    search_fields = [
        "name",
        "description",
    ]

    ordering_fields = [
        "price",
        "created_at",
        "name",
        "ordered_count",
    ]

    ordering = [
        "-ordered_count",
    ]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return product.ProductCreateSerializer

        return product.ProductSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()

        context["user"] = self.request.user
        context["category_slug"] = self.kwargs["category_slug"]

        return context

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsSeller()]

        return []


class ProductListView(generics.ListAPIView):
    serializer_class = product.ProductSerializer
    pagination_class = DefaultPagination

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = {
        "category__slug": ["exact"],
        "price": ["gte", "lte"],
    }

    search_fields = [
        "name",
        "description",
    ]

    ordering_fields = [
        "price",
        "created_at",
        "name",
        "ordered_count",
    ]

    ordering = [
        "-ordered_count",
    ]

    queryset = Product.objects.annotate(
        ordered_count=Coalesce(Sum("order_items__quantity"), 0)
    )


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "slug"
    lookup_url_kwarg = "product_slug"
    permission_classes = [IsProductOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return product.ProductUpdateSerializer
        return product.ProductSerializer

    def get_queryset(self):
        return Product.objects.annotate(
            ordered_count=Coalesce(
                Sum("order_items__quantity"),
                0,
            )
        )

    @extend_schema(responses={200: product.ProductSerializer})
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        instance = serializer.instance

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        read_serializer = product.ProductSerializer(
            instance, context=self.get_serializer_context()
        )
        return Response(read_serializer.data)


class ProductLikeListView(generics.ListAPIView):
    serializer_class = product.ProductLikeSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        category_slug = self.kwargs.get("category_slug")
        product_slug = self.kwargs.get("product_slug")

        return ProductLike.objects.filter(
            product__slug=product_slug,
            product__category__slug=category_slug,
        )


class ProductLikeCreateView(generics.CreateAPIView):
    serializer_class = product.ProductLikeCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        context["product_slug"] = self.kwargs["product_slug"]
        return context


class ProductDislikeListView(generics.ListAPIView):
    serializer_class = product.ProductDislikeSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        category_slug = self.kwargs.get("category_slug")
        product_slug = self.kwargs.get("product_slug")

        return ProductDislike.objects.filter(
            product__slug=product_slug,
            product__category__slug=category_slug,
        )


class ProductDislikeCreateView(generics.CreateAPIView):
    serializer_class = product.ProductDislikeCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        context["product_slug"] = self.kwargs["product_slug"]
        return context


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    pagination_class = DefaultPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return order.OrderCreateSerializer
        return order.OrderSerializer


class ProductImageListCreateView(generics.ListCreateAPIView):
    pagination_class = None

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsSeller()]

        return []

    def get_serializer_class(self):
        if self.request.method == "POST":
            return product.ProductImageCreateSerializer

        return product.ProductImageSerializer

    def get_queryset(self):
        return ProductImage.objects.filter(product__slug=self.kwargs["product_slug"])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["product_slug"] = self.kwargs["product_slug"]
        context["user"] = self.request.user
        return context


class ProductImageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    pagination_class = None
    permission_classes = [IsProductImageOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return product.ProductImageUpdateSerializer
        return product.ProductImageSerializer

    def get_queryset(self):
        return ProductImage.objects.filter(product__slug=self.kwargs["product_slug"])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        product_slug = self.kwargs["product_slug"]
        context["product_slug"] = product_slug

        return context


class PopularProductsListView(generics.ListAPIView):
    serializer_class = product.ProductSerializer
    pagination_class = None

    def get_limit(self, default):
        try:
            limit = int(self.request.query_params.get("limit", default))
            return max(1, min(limit, 100))
        except (TypeError, ValueError):
            return default

    def get_queryset(self):
        limit = self.get_limit(8)

        return Product.objects.annotate(
            bought_amount=Coalesce(
                Sum("order_items__quantity"),
                0,
            )
        ).order_by("-bought_amount")[:limit]


class NewProductsListView(generics.ListAPIView):
    serializer_class = product.ProductSerializer
    pagination_class = None

    def get_limit(self, default):
        try:
            limit = int(self.request.query_params.get("limit", default))
            return max(1, min(limit, 100))
        except (TypeError, ValueError):
            return default

    def get_queryset(self):
        limit = self.get_limit(8)

        return Product.objects.annotate(
            bought_amount=Coalesce(
                Sum("order_items__quantity"),
                0,
            )
        ).order_by("-created_at")[:limit]


class ProductCommentListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == "POST":
            return product.ProductCommentCreateSerializer
        return product.ProductCommentSerializer

    def get_queryset(self):
        product_slug = self.kwargs.get("product_slug")
        return (
            ProductComment.objects.filter(product__slug=product_slug)
            .select_related("user")
            .order_by("-created_at")
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        context["product_slug"] = self.kwargs.get("product_slug")

        return context

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]

        return []


class ProductCommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsCommentOwnerOrReadOnly]

    def get_queryset(self):
        return ProductComment.objects.filter(
            product__slug=self.kwargs["product_slug"]
        ).select_related(
            "user",
            "product",
        )

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return product.ProductCommentUpdateSerializer
        return product.ProductCommentSerializer
