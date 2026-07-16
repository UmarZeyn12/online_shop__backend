from apps.api.serializers import product, seller
from apps.main.models import (
    Product,
    ProductLike,
    ProductDislike,
    Order,
    OrderItem,
    ProductComment,
)
from apps.api.pagination import DefaultPagination
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models.functions import Coalesce
from django.db.models import Sum, Count
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.api.permissions import IsSeller
from rest_framework.views import APIView


class ToggleIsSellerView(generics.UpdateAPIView):
    serializer_class = seller.UserProfileIsSellerSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class UserProductsListView(generics.ListAPIView):
    serializer_class = product.ProductSerializer
    permission_classes = [IsSeller]
    pagination_class = None

    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "name",
        "description",
    ]

    ordering_fields = [
        "price",
        "created_at",
        "ordered_count",
    ]

    ordering = [
        "-created_at",
    ]

    def get_queryset(self):
        return Product.objects.filter(posted_by=self.request.user).annotate(
            ordered_count=Coalesce(
                Sum("order_items__quantity"),
                0,
            )
        )


class SellerOrdersListView(generics.ListAPIView):
    serializer_class = seller.SellerOrderSerializer
    permission_classes = [IsSeller]
    pagination_class = DefaultPagination

    def get_queryset(self):
        return (
            Order.objects.filter(
                items__product__posted_by=self.request.user,
            )
            .select_related("user")
            .prefetch_related(
                "items",
                "items__product",
            )
            .distinct()
            .order_by("-created_at")
        )


class SellerStatisticsView(APIView):
    permission_classes = [IsSeller]

    def get(self, request):
        products = Product.objects.filter(
            posted_by=request.user,
        )

        return Response(
            {
                "products": products.count(),
                "sold_items": OrderItem.objects.filter(
                    product__posted_by=request.user,
                ).aggregate(
                    total=Coalesce(Sum("quantity"), 0),
                )[
                    "total"
                ],
                "revenue": OrderItem.objects.filter(
                    product__posted_by=request.user,
                ).aggregate(
                    total=Coalesce(Sum("total_price"), 0),
                )[
                    "total"
                ],
                "likes": ProductLike.objects.filter(
                    product__posted_by=request.user,
                ).aggregate(total=Count("user"))[
                    "total"
                ],
                "dislikes": ProductDislike.objects.filter(
                    product__posted_by=request.user,
                ).aggregate(total=Count("user"))[
                    "total"
                ],
                "comments": ProductComment.objects.filter(
                    product__posted_by=request.user,
                ).count(),
            }
        )
