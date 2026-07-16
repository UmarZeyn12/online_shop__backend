from apps.api.serializers import user
from apps.main.models import Product, UserProfile, UserFavorites, UserCart, CartItem
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView


class UserProfileRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return user.UserProfileUpdateSerializer
        return user.UserProfileSerializer

    def get_object(self):
        user_profile, created = UserProfile.objects.get_or_create(
            user=self.request.user
        )

        return user_profile


class UserFavoritesRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = user.UserFavoritesSerializer

    def get_object(self):
        favorites, _ = UserFavorites.objects.get_or_create(user=self.request.user)

        return favorites


class UserFavoritesCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_slug):
        favorites, _ = UserFavorites.objects.get_or_create(user=request.user)

        product = get_object_or_404(
            Product,
            slug=product_slug,
        )

        if favorites.products.filter(pk=product.pk).exists():
            favorites.products.remove(product)

            return Response(
                {"detail": "Product removed from favorites."},
                status=status.HTTP_200_OK,
            )

        favorites.products.add(product)

        return Response(
            {"detail": "Product added to favorites."},
            status=status.HTTP_200_OK,
        )


class UserCartRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = user.UserCartSerializer

    def get_object(self):
        cart, _ = UserCart.objects.get_or_create(user=self.request.user)

        return cart

    def delete(self, request, *args, **kwargs):
        cart = self.get_object()

        cart.items.all().delete()

        return Response(
            {"detail": "Cart cleared."},
            status=status.HTTP_200_OK,
        )


class UserCartCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_slug):
        cart, _ = UserCart.objects.get_or_create(
            user=request.user,
        )

        product = get_object_or_404(
            Product,
            slug=product_slug,
        )

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                "quantity": 1,
            },
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save(update_fields=["quantity"])

        return Response(
            {
                "detail": "Product added to cart.",
                "quantity": cart_item.quantity,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, product_slug):
        cart, _ = UserCart.objects.get_or_create(
            user=request.user,
        )

        cart_item = get_object_or_404(
            CartItem,
            cart=cart,
            product__slug=product_slug,
        )

        cart_item.delete()

        return Response(
            {
                "detail": "Product removed from cart.",
            },
            status=status.HTTP_200_OK,
        )


class UserCartQuantityUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = user.CartItemQuantityUpdateSerializer

    def patch(self, request, product_slug):
        cart, _ = UserCart.objects.get_or_create(user=request.user)

        cart_item = get_object_or_404(
            CartItem,
            cart=cart,
            product__slug=product_slug,
        )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart_item.quantity = serializer.validated_data["quantity"]
        cart_item.save()

        return Response(
            {
                "detail": "Quantity updated.",
                "quantity": cart_item.quantity,
            },
            status=status.HTTP_200_OK,
        )
