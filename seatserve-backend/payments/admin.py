from django.contrib import admin
from payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'status', 'amount', 'gateway', 'created_at')
    list_filter = ('status', 'gateway', 'created_at')
    search_fields = ('order__public_token', 'gateway_reference')
    readonly_fields = ('created_at', 'updated_at')
