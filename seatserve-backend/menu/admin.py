from django.contrib import admin
from menu.models import Category, MenuItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'sort_order', 'is_active', 'created_at')
    list_filter = ('is_active', 'restaurant', 'created_at')
    search_fields = ('name', 'restaurant__name')
    ordering = ('restaurant', 'sort_order')


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'category', 'price', 'is_available', 'created_at')
    list_filter = ('is_available', 'restaurant', 'category', 'created_at')
    search_fields = ('name', 'restaurant__name', 'description')
    readonly_fields = ('created_at', 'updated_at')
