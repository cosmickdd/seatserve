"""
Payment serializers for DRF
"""
from rest_framework import serializers
from .models import Payment
from orders.serializers import OrderSerializer


class PaymentSerializer(serializers.ModelSerializer):
    order_detail = OrderSerializer(source='order', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'order_detail', 'status', 'status_display',
            'amount', 'currency', 'payment_method', 'payment_method_display',
            'gateway_reference', 'session_id', 'refund_amount', 'is_refundable',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order_detail', 'status', 'status_display',
            'gateway_reference', 'session_id', 'refund_amount',
            'created_at', 'updated_at'
        ]


class PaymentDetailSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = [
            'id', 'restaurant', 'status', 'gateway_reference', 'session_id',
            'refund_amount', 'refunded_at', 'created_at', 'updated_at'
        ]


class CreateCheckoutSessionSerializer(serializers.Serializer):
    """Serializer for creating Stripe checkout session"""
    order_id = serializers.IntegerField()
    
    def validate_order_id(self, value):
        from orders.models import Order
        try:
            Order.objects.get(id=value)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found")
        return value


class ConfirmPaymentSerializer(serializers.Serializer):
    """Serializer for confirming payment from Stripe session"""
    session_id = serializers.CharField()
    
    def validate_session_id(self, value):
        if not value:
            raise serializers.ValidationError("session_id is required")
        return value


class RefundPaymentSerializer(serializers.Serializer):
    """Serializer for refunding a payment"""
    amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True
    )
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate_amount(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value


class StripeWebhookSerializer(serializers.Serializer):
    """Serializer for handling Stripe webhooks"""
    event_id = serializers.CharField()
    event_type = serializers.CharField()
