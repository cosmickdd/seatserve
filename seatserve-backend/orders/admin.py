from django.contrib import admin
from orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('menu_item', 'quantity', 'price_at_time', 'created_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('public_token', 'restaurant', 'table', 'status', 'payment_status', 'total_amount', 'created_at')
    list_filter = ('status', 'payment_status', 'restaurant', 'created_at')
    search_fields = ('public_token', 'restaurant__name', 'table__name')
    readonly_fields = ('public_token', 'created_at', 'updated_at')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'menu_item', 'quantity', 'price_at_time', 'created_at')
    list_filter = ('order__restaurant', 'created_at')
    search_fields = ('order__public_token', 'menu_item__name')
    readonly_fields = ('created_at',)
