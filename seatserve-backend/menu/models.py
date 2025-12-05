import json
from django.db import models
from restaurants.models import Restaurant


class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_categories')
    name = models.CharField(max_length=100)
    sort_order = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'menu_category'
        unique_together = ('restaurant', 'name')
        ordering = ['sort_order', 'name']

    def __str__(self):
        return f'{self.restaurant.name} - {self.name}'


class MenuItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='items')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True)
    
    tags = models.JSONField(default=list)  # e.g., ["veg", "spicy", "gluten-free"]
    is_available = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'menu_item'
        ordering = ['category', 'name']

    def __str__(self):
        return f'{self.restaurant.name} - {self.name}'
