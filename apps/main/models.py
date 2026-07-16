from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        abstract = True


class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    image = models.ImageField(
        upload_to="users/profiles/%Y/%m/%d/", null=True, blank=True
    )
    is_seller = models.BooleanField(verbose_name="Is seller", default=False)

    def __str__(self):
        return f"{self.user.username} profile"


class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="Category Name")
    slug = models.SlugField(
        max_length=140, unique=True, verbose_name="Slug", primary_key=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Product(BaseModel):
    name = models.CharField(max_length=255, verbose_name="Product Name")
    slug = models.SlugField(
        max_length=140, unique=True, verbose_name="Slug", primary_key=True
    )
    description = models.TextField(verbose_name="Description")
    price = models.IntegerField(verbose_name="Price")
    stock_amount = models.IntegerField(verbose_name="Stock amount", default=0)
    in_stock = models.BooleanField(verbose_name="In stock", default=False)
    preview = models.ImageField(
        upload_to="products/previews/%Y/%m/%d",
        verbose_name="Preview",
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Category",
        related_name="category_name",
    )
    posted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posted_products",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def save(self, *args, **kwargs):
        if self.stock_amount > 0:
            self.in_stock = True
        else:
            self.in_stock = False

        super().save(*args, **kwargs)


class UserFavorites(BaseModel):
    user = models.OneToOneField(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="favorites",
    )

    products = models.ManyToManyField(
        Product,
        blank=True,
        related_name="favorited_by",
    )

    def __str__(self):
        return f"{self.user.username} favorites"


class UserCart(BaseModel):
    user = models.OneToOneField(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="cart",
    )

    def __str__(self):
        return f"{self.user.username} cart"


class CartItem(BaseModel):
    cart = models.ForeignKey(
        UserCart,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="cart_items"
    )

    quantity = models.PositiveIntegerField(default=1)


class ProductImage(BaseModel):
    id = models.AutoField(primary_key=True)

    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE,
    )

    image = models.ImageField(
        upload_to="products/images/%Y/%m/%d",
    )


class ProductComment(BaseModel):
    id = models.AutoField(verbose_name="ID", primary_key=True)
    user = models.ForeignKey(
        User, verbose_name="User", related_name="comments", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        verbose_name="Product",
        related_name="comments",
        on_delete=models.CASCADE,
    )
    content = models.TextField()


class ProductLike(BaseModel):
    id = models.AutoField(verbose_name="ID", primary_key=True)
    user = models.ManyToManyField(
        "auth.User", related_name="product_likes", verbose_name="User"
    )
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="likes", verbose_name="Product"
    )

    class Meta:
        verbose_name = "Product Like"
        verbose_name_plural = "Product Likes"


class ProductDislike(BaseModel):
    id = models.AutoField(verbose_name="ID", primary_key=True)
    user = models.ManyToManyField(
        "auth.User", related_name="product_dislikes", verbose_name="User"
    )
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="dislikes",
        verbose_name="Product",
    )

    class Meta:
        verbose_name = "Product Dislike"
        verbose_name_plural = "Product Dislikes"


class Order(BaseModel):
    id = models.AutoField(primary_key=True, verbose_name="ID")

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="User",
    )

    class Status(models.TextChoices):
        PENDING = "pending"
        PAID = "paid"
        PROCESSING = "processing"
        SHIPPED = "shipped"
        COMPLETED = "completed"
        CANCELLED = "cancelled"
        REFUNDED = "refunded"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Status",
    )

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(BaseModel):
    id = models.AutoField(primary_key=True, verbose_name="ID")

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Order",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="order_items",
        verbose_name="Product",
    )

    quantity = models.IntegerField(
        default=1,
        verbose_name="Quantity",
    )

    total_price = models.IntegerField(
        verbose_name="Total Price",
    )

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"
