from django.urls import path
from .views import category, product, order, auth, user, seller
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path(
        "categories/",
        category.CategoryListCreateView.as_view(),
        name="categories",
    ),
    path(
        "categories/popular/",
        category.PopularCategoryListView.as_view(),
        name="popular categories",
    ),
    path(
        "categories/<slug:category_slug>/",
        category.CategoryRetrieveDestroyView.as_view(),
        name="category",
    ),
    path(
        "categories/<slug:category_slug>/products/popular/",
        category.CategoryPopularProductsListView.as_view(),
        name="category's popular products",
    ),
    path(
        "categories/<slug:category_slug>/products/",
        product.ProductListCreateView.as_view(),
        name="category's products",
    ),
    path(
        "products/<slug:product_slug>/images/",
        product.ProductImageListCreateView.as_view(),
        name="product's images",
    ),
    path(
        "products/<slug:product_slug>/images/<int:pk>/",
        product.ProductImageRetrieveUpdateDestroyView.as_view(),
        name="product's image",
    ),
    path(
        "categories/<slug:category_slug>/products/<slug:product_slug>/likes/",
        product.ProductLikeListView.as_view(),
        name="category's product's likes",
    ),
    path(
        "categories/<slug:category_slug>/products/<slug:product_slug>/like/",
        product.ProductLikeCreateView.as_view(),
        name="category's product's like creation",
    ),
    path(
        "categories/<slug:category_slug>/products/<slug:product_slug>/dislikes/",
        product.ProductDislikeListView.as_view(),
        name="category's product's dislikes",
    ),
    path(
        "categories/<slug:category_slug>/products/<slug:product_slug>/dislike/",
        product.ProductDislikeCreateView.as_view(),
        name="category's product's dislike creation",
    ),
    path("products/", product.ProductListView.as_view(), name="products"),
    path(
        "products/popular/",
        product.PopularProductsListView.as_view(),
        name="popular products",
    ),
    path(
        "products/new/",
        product.NewProductsListView.as_view(),
        name="new products",
    ),
    path(
        "products/<slug:product_slug>/",
        product.ProductRetrieveUpdateDestroyView.as_view(),
        name="product",
    ),
    path(
        "products/<slug:product_slug>/comments/",
        product.ProductCommentListCreateView.as_view(),
        name="product comments",
    ),
    path(
        "products/<slug:product_slug>/comments/<int:pk>/",
        product.ProductCommentRetrieveUpdateDestroyView.as_view(),
        name="product comment",
    ),
    path("auth/login/", TokenObtainPairView.as_view(), name="login"),
    path("auth/login/refresh/", TokenRefreshView.as_view(), name="refresh the token"),
    path("auth/register/", auth.register_user, name="register"),
    path(
        "users/me/", user.UserProfileRetrieveUpdateView.as_view(), name="user profile"
    ),
    path(
        "users/me/toggle-is-seller/",
        seller.ToggleIsSellerView.as_view(),
        name="user becoming/unbecoming a seller",
    ),
    path(
        "users/me/seller/orders/",
        seller.SellerOrdersListView.as_view(),
        name="seller orders",
    ),
    path(
        "users/me/seller/statistics/",
        seller.SellerStatisticsView.as_view(),
        name="seller statistics",
    ),
    path(
        "users/me/products/",
        seller.UserProductsListView.as_view(),
        name="user products",
    ),
    path(
        "users/me/favorites/",
        user.UserFavoritesRetrieveView.as_view(),
        name="user's favorites",
    ),
    path(
        "users/me/favorites/<slug:product_slug>/",
        user.UserFavoritesCreateView.as_view(),
        name="delete or add the user's favorite",
    ),
    path(
        "users/me/cart/",
        user.UserCartRetrieveDestroyView.as_view(),
        name="user cart",
    ),
    path(
        "users/me/cart/products/<slug:product_slug>/",
        user.UserCartCreateView.as_view(),
        name="add/remove to/from cart",
    ),
    path(
        "users/me/cart/products/<slug:product_slug>/quantity/",
        user.UserCartQuantityUpdateView.as_view(),
        name="update quantity of items in user cart",
    ),
    path("users/me/orders/", order.OrderListCreateView.as_view(), name="orders"),
    path(
        "users/me/orders/<int:order_id>/",
        order.OrderRetrieveUpdateDestroyView.as_view(),
        name="order",
    ),
    path(
        "users/me/orders/<int:order_id>/items/",
        order.OrderItemListCreateView.as_view(),
        name="order's items",
    ),
    path(
        "users/me/orders/<int:order_id>/items/<int:order_item_id>/",
        order.OrderItemRetrieveUpdateDestroyView.as_view(),
        name="order's item",
    ),
]
