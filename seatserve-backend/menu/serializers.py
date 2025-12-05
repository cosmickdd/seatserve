from rest_framework import serializers
from menu.models import Category, MenuItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'restaurant', 'name', 'sort_order', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'restaurant', 'created_at', 'updated_at')


class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = MenuItem
        fields = ('id', 'restaurant', 'category', 'category_name', 'name', 'description', 
                  'price', 'image_url', 'tags', 'is_available', 'created_at', 'updated_at')
        read_only_fields = ('id', 'restaurant', 'created_at', 'updated_at')


class MenuItemDetailSerializer(serializers.ModelSerializer):
    """Detailed view including category info"""
    category = CategorySerializer(read_only=True)

    class Meta:
        model = MenuItem
        fields = ('id', 'category', 'name', 'description', 'price', 'image_url', 
                  'tags', 'is_available')
