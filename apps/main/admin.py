from django.contrib import admin
from . import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "created_at", "updated_at"]
    search_fields = ["name"]
    readonly_fields = ["created_at", "updated_at"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "slug",
        "price",
        "preview",
        "category",
        "created_at",
        "updated_at",
    ]
    list_filter = ["category", "created_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]
    prepopulated_fields = {"slug": ("name",)}
    list_display_links = ["name"]


@admin.register(models.ProductLike)
class ProductLikeAdmin(admin.ModelAdmin):
    list_display = ["product", "get_users", "created_at", "updated_at"]
    list_filter = ["created_at"]
    readonly_fields = ["created_at", "updated_at"]
    filter_horizontal = ["user"]

    def get_users(self, obj):
        return ", ".join([user.username for user in obj.user.all()])

    get_users.short_description = "User"


@admin.register(models.ProductDislike)
class ProductDislikeAdmin(admin.ModelAdmin):
    list_display = ["product", "get_users", "created_at", "updated_at"]
    list_filter = ["created_at"]
    readonly_fields = ["created_at", "updated_at"]
    filter_horizontal = ["user"]

    def get_users(self, obj):
        return ", ".join([user.username for user in obj.user.all()])

    get_users.short_description = "User"


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "status", "created_at", "updated_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["user__username"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(models.OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "product", "quantity", "created_at", "updated_at"]
    list_filter = ["order", "created_at"]
    search_fields = ["order__id", "product__name"]
    readonly_fields = ["created_at", "updated_at"]
