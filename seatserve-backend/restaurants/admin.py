from django.contrib import admin
from restaurants.models import Plan, Restaurant, RestaurantSubscription, Table


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'billing_period', 'max_tables', 'max_menu_items', 'is_active')
    list_filter = ('billing_period', 'is_active')
    search_fields = ('name',)


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'city', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'city')
    search_fields = ('name', 'owner__email', 'email')
    readonly_fields = ('public_id', 'created_at', 'updated_at')


@admin.register(RestaurantSubscription)
class RestaurantSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'plan', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'start_date')
    search_fields = ('restaurant__name', 'plan__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'capacity', 'is_active', 'created_at')
    list_filter = ('is_active', 'restaurant', 'created_at')
    search_fields = ('name', 'restaurant__name')
    readonly_fields = ('token', 'created_at', 'updated_at')
