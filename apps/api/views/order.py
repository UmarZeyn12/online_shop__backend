from apps.api.serializers import order
from django.shortcuts import get_object_or_404
from apps.main.models import Order, OrderItem
from apps.api.pagination import DefaultPagination
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class OrderListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return order.OrderCreateSerializer
        return order.OrderSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        return Response(
            order.OrderSerializer(
                instance,
                context=self.get_serializer_context(),
            ).data,
            status=status.HTTP_201_CREATED,
        )


class OrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    lookup_field = "id"
    lookup_url_kwarg = "order_id"

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return order.OrderUpdateSerializer
        return order.OrderSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        instance = serializer.instance

        read_serializer = order.OrderSerializer(
            instance, context=self.get_serializer_context()
        )
        return Response(read_serializer.data)


class OrderItemListCreateView(generics.ListCreateAPIView):
    queryset = OrderItem.objects.all()
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return order.OrderItemCreateSerializer
        return order.OrderItemSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        order = get_object_or_404(Order, id=self.kwargs.get("order_id"))
        context["order"] = order

        return context


class OrderItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderItem.objects.all()
    lookup_field = "id"
    lookup_url_kwarg = "order_item_id"
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return order.OrderItemUpdateSerializer
        return order.OrderItemSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        instance = serializer.instance

        read_serializer = order.OrderItemSerializer(
            instance, context=self.get_serializer_context()
        )
        return Response(read_serializer.data)
