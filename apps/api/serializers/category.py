from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from slugify import slugify
from apps.main.models import Category


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.SlugField()

    class Meta:
        model = Category
        fields = ["name", "slug", "created_at", "updated_at"]


class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name"]

    def create(self, validated_data):
        slug = slugify(validated_data.get("name"))
        if Category.objects.filter(slug=slug).exists():
            raise ValidationError({"name": "Category slug not unique."})
        return Category.objects.create(**validated_data, slug=slug)
