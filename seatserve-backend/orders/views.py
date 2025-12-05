from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Q, F

from orders.models import Order, OrderItem
from orders.serializers import (
    OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer,
    OrderPublicStatusSerializer, OrderItemSerializer
)
from menu.models import MenuItem
from restaurants.models import Restaurant, Table
from restaurants.permissions import IsRestaurantUser, IsRestaurantOrderOwner


class OrderViewSet(viewsets.ModelViewSet):
    """Restaurant order management"""
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated, IsRestaurantUser)

    def get_queryset(self):
        """Get orders for current user's restaurant"""
        restaurant = Restaurant.objects.filter(owner=self.request.user).first()
        if restaurant:
            return Order.objects.filter(restaurant=restaurant).prefetch_related('items')
        return Order.objects.none()

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's orders"""
        from django.utils.timezone import now
        today = now().date()
        
        restaurant = Restaurant.objects.filter(owner=request.user).first()
        if not restaurant:
            return Response(
                {'detail': 'Restaurant not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        orders = Order.objects.filter(
            restaurant=restaurant,
            created_at__date=today
        ).prefetch_related('items').order_by('-created_at')
        
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending orders"""
        restaurant = Restaurant.objects.filter(owner=request.user).first()
        if not restaurant:
            return Response(
                {'detail': 'Restaurant not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        orders = Order.objects.filter(
            restaurant=restaurant,
            status__in=['RECEIVED', 'IN_KITCHEN']
        ).prefetch_related('items').order_by('-created_at')
        
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update order status"""
        order = get_object_or_404(Order, pk=pk, restaurant__owner=request.user)
        serializer = OrderStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            order.status = serializer.validated_data['status']
            order.save()
            return Response(
                OrderSerializer(order).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get order statistics for restaurant"""
        from django.utils.timezone import now
        today = now().date()
        
        restaurant = Restaurant.objects.filter(owner=request.user).first()
        if not restaurant:
            return Response(
                {'detail': 'Restaurant not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        today_orders = Order.objects.filter(
            restaurant=restaurant,
            created_at__date=today
        )
        
        return Response({
            'total_orders_today': today_orders.count(),
            'total_revenue_today': float(today_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
            'paid_orders': today_orders.filter(payment_status='PAID').count(),
            'pending_orders': today_orders.filter(status__in=['RECEIVED', 'IN_KITCHEN']).count(),
            'served_orders': today_orders.filter(status='SERVED').count(),
        })


class PublicOrderViewSet(viewsets.ViewSet):
    """Public API for customers - QR-based ordering"""
    permission_classes = (AllowAny,)

    @action(detail=False, methods=['get'], url_path='restaurant/(?P<restaurant_public_id>[^/.]+)/table/(?P<table_token>[^/.]+)/menu')
    def menu(self, request, restaurant_public_id=None, table_token=None):
        """Get menu for a specific table (public access)"""
        restaurant = get_object_or_404(
            Restaurant,
            public_id=restaurant_public_id,
            is_active=True
        )
        
        table = get_object_or_404(
            Table,
            restaurant=restaurant,
            token=table_token,
            is_active=True
        )

        # Check if restaurant has active subscription
        if not restaurant.active_subscription:
            return Response(
                {'detail': 'Restaurant is not active'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get menu grouped by category
        from menu.models import Category
        categories = Category.objects.filter(
            restaurant=restaurant,
            is_active=True
        ).prefetch_related('items')
        
        data = {
            'restaurant': {
                'id': restaurant.id,
                'public_id': str(restaurant.public_id),
                'name': restaurant.name,
                'logo_url': restaurant.logo_url,
            },
            'table': {
                'id': table.id,
                'name': table.name,
            },
            'menu': []
        }
        
        for category in categories:
            items = []
            for item in category.items.filter(is_available=True):
                items.append({
                    'id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'price': str(item.price),
                    'image_url': item.image_url,
                    'tags': item.tags,
                })
            
            if items:  # Only include categories with available items
                data['menu'].append({
                    'id': category.id,
                    'name': category.name,
                    'items': items
                })
        
        return Response(data)

    @action(detail=False, methods=['post'], url_path='restaurant/(?P<restaurant_public_id>[^/.]+)/table/(?P<table_token>[^/.]+)/orders')
    def create_order(self, request, restaurant_public_id=None, table_token=None):
        """Create an order from QR (public access)"""
        restaurant = get_object_or_404(
            Restaurant,
            public_id=restaurant_public_id,
            is_active=True
        )
        
        table = get_object_or_404(
            Table,
            restaurant=restaurant,
            token=table_token,
            is_active=True
        )

        # Check if restaurant has active subscription
        if not restaurant.active_subscription:
            return Response(
                {'detail': 'Restaurant is not active'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Create order
            order = Order.objects.create(
                restaurant=restaurant,
                table=table,
                payment_status='PENDING',  # Will be updated after payment
                status='RECEIVED',
                customer_note=serializer.validated_data.get('customer_note', '')
            )

            total_amount = 0
            # Create order items
            for item_data in serializer.validated_data['items']:
                menu_item = get_object_or_404(
                    MenuItem,
                    id=item_data['menu_item_id'],
                    restaurant=restaurant
                )
                
                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=item_data['quantity'],
                    price_at_time=menu_item.price
                )
                
                total_amount += menu_item.price * item_data['quantity']

            order.total_amount = total_amount
            order.save()

            # TODO: In production, redirect to payment gateway
            # For MVP, mark as PAID automatically
            order.payment_status = 'PAID'
            order.save()

            return Response(
                OrderPublicStatusSerializer(order).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='order/(?P<order_token>[^/.]+)')
    def order_status(self, request, order_token=None):
        """Get order status by public token"""
        order = get_object_or_404(Order, public_token=order_token)
        return Response(OrderPublicStatusSerializer(order).data)
