from rest_framework import serializers
from orders.models import Order, OrderItem
from menu.models import MenuItem


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    menu_item_detail = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'menu_item', 'menu_item_name', 'menu_item_detail', 'quantity', 'price_at_time')
        read_only_fields = ('id', 'price_at_time')

    def get_menu_item_detail(self, obj):
        return {
            'id': obj.menu_item.id,
            'name': obj.menu_item.name,
            'price': str(obj.menu_item.price),
            'description': obj.menu_item.description,
        }


class OrderItemCreateSerializer(serializers.Serializer):
    menu_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    table_name = serializers.CharField(source='table.name', read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'public_token', 'restaurant', 'restaurant_name', 'table', 'table_name',
                  'status', 'payment_status', 'total_amount', 'estimated_time_minutes', 
                  'customer_note', 'items', 'created_at', 'updated_at')
        read_only_fields = ('id', 'public_token', 'restaurant', 'status', 'payment_status', 
                           'total_amount', 'created_at', 'updated_at')


class OrderCreateSerializer(serializers.Serializer):
    """For creating orders from customer QR flow"""
    items = OrderItemCreateSerializer(many=True)
    customer_note = serializers.CharField(required=False, allow_blank=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('At least one item is required.')
        return value


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('status',)

    def validate_status(self, value):
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(f'Invalid status. Must be one of: {valid_statuses}')
        return value


class OrderPublicStatusSerializer(serializers.ModelSerializer):
    """For public QR order status view"""
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'public_token', 'status', 'total_amount', 'estimated_time_minutes', 
                  'items', 'created_at')
        read_only_fields = fields
