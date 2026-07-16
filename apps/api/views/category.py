from apps.api.serializers import product, category
from apps.main.models import Category, Product
from apps.api.pagination import DefaultPagination
from rest_framework import generics
from django.db.models.functions import Coalesce
from django.db.models import Sum


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    pagination_class = DefaultPagination

    def paginate_queryset(self, queryset):
        if self.request.query_params.get("all", "").lower() == "true":
            return None
        return super().paginate_queryset(queryset)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return category.CategoryCreateSerializer
        return category.CategorySerializer


class CategoryRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = Category.objects.all()
    lookup_field = "slug"
    lookup_url_kwarg = "category_slug"
    serializer_class = category.CategorySerializer


class CategoryPopularProductsListView(generics.ListAPIView):
    serializer_class = product.ProductSerializer
    pagination_class = None

    def get_limit(self, default):
        try:
            limit = int(self.request.query_params.get("limit", default))
            return max(1, min(limit, 100))
        except (TypeError, ValueError):
            return default

    def get_queryset(self):
        category_slug = self.kwargs["category_slug"]
        limit = self.get_limit(4)

        return (
            Product.objects.filter(category__slug=category_slug)
            .annotate(
                ordered_count=Coalesce(
                    Sum("order_items__quantity"),
                    0,
                )
            )
            .order_by("-ordered_count")[:limit]
        )


class PopularCategoryListView(generics.ListAPIView):
    serializer_class = category.CategorySerializer
    pagination_class = None

    def get_limit(self, default):
        try:
            limit = int(self.request.query_params.get("limit", default))
            return max(1, min(limit, 100))
        except (TypeError, ValueError):
            return default

    def get_queryset(self):
        limit = self.get_limit(12)

        return Category.objects.annotate(
            ordered_count=Coalesce(
                Sum("category_name__order_items__quantity"),
                0,
            )
        ).order_by("-ordered_count")[:limit]
