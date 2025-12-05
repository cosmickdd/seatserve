from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils.timezone import now, timedelta
from django.db.models import Q
import qrcode
from io import BytesIO
import base64
import uuid

from restaurants.models import Plan, Restaurant, RestaurantSubscription, Table
from restaurants.serializers import (
    PlanSerializer, RestaurantSerializer, RestaurantCreateSerializer,
    RestaurantSubscriptionSerializer, TableSerializer
)
from restaurants.permissions import IsRestaurantOwner, IsRestaurantUser, IsRestaurantTableOwner
from restaurants.plan_service import PlanEnforcementService


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    """List all available plans"""
    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None


class RestaurantViewSet(viewsets.ModelViewSet):
    """Restaurant management"""
    serializer_class = RestaurantSerializer
    permission_classes = (IsAuthenticated, IsRestaurantUser)

    def get_queryset(self):
        """Get restaurant for current user"""
        return Restaurant.objects.filter(owner=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user's restaurant"""
        restaurant = Restaurant.objects.filter(owner=request.user).first()
        if restaurant:
            return Response(RestaurantSerializer(restaurant).data)
        return Response(
            {'detail': 'Restaurant not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def create_restaurant(self, request):
        """Create a restaurant for current user"""
        # Check if user already has a restaurant
        if Restaurant.objects.filter(owner=request.user).exists():
            return Response(
                {'error': 'User already has a restaurant'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RestaurantCreateSerializer(data=request.data)
        if serializer.is_valid():
            restaurant = Restaurant.objects.create(
                owner=request.user,
                name=serializer.validated_data['name'],
                email=serializer.validated_data.get('email', request.user.email),
                phone=serializer.validated_data.get('phone', ''),
                city=serializer.validated_data.get('city', ''),
                country=serializer.validated_data.get('country', ''),
                address=serializer.validated_data.get('address', ''),
            )
            return Response(
                RestaurantSerializer(restaurant).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put', 'patch'], permission_classes=[IsAuthenticated])
    def update_me(self, request):
        """Update current user's restaurant"""
        restaurant = Restaurant.objects.filter(owner=request.user).first()
        if not restaurant:
            return Response(
                {'detail': 'Restaurant not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = RestaurantSerializer(restaurant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RestaurantSubscriptionViewSet(viewsets.ViewSet):
    """Manage restaurant subscriptions"""
    permission_classes = (IsAuthenticated, IsRestaurantUser)

    @action(detail=False, methods=['get'])
    def my_subscription(self, request):
        """Get current subscription"""
        restaurant = Restaurant.objects.filter(owner=request.user).first()
        if not restaurant:
            return Response(
                {'detail': 'Restaurant not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        subscription = restaurant.active_subscription
        if subscription:
            return Response(RestaurantSubscriptionSerializer(subscription).data)
        return Response({'detail': 'No active subscription'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def subscription_history(self, request):
        """Get all subscriptions history"""
        restaurant = Restaurant.objects.filter(owner=request.user).first()
        if not restaurant:
            return Response(
                {'detail': 'Restaurant not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        subscriptions = restaurant.subscriptions.all().order_by('-created_at')
        serializer = RestaurantSubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def select_plan(self, request):
        """Select/upgrade to a plan"""
        plan_id = request.data.get('plan_id')
        
        if not plan_id:
            return Response(
                {'error': 'plan_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        restaurant = Restaurant.objects.filter(owner=request.user).first()
        if not restaurant:
            return Response(
                {'detail': 'Restaurant not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        plan = get_object_or_404(Plan, id=plan_id, is_active=True)

        # In MVP: automatically activate the plan (without real payment)
        # In production: redirect to payment gateway
        end_date = now() + timedelta(days=30 if plan.billing_period == 'MONTH' else 365)
        
        subscription = RestaurantSubscription.objects.create(
            restaurant=restaurant,
            plan=plan,
            status='ACTIVE',
            end_date=end_date,
            payment_reference='mock_payment_' + str(uuid.uuid4())
        )

        return Response(
            RestaurantSubscriptionSerializer(subscription).data,
            status=status.HTTP_201_CREATED
        )


class TableViewSet(viewsets.ModelViewSet):
    """Table management"""
    serializer_class = TableSerializer
    permission_classes = (IsAuthenticated, IsRestaurantUser)

    def get_queryset(self):
        """Get tables for current user's restaurant"""
        restaurant = Restaurant.objects.filter(owner=self.request.user).first()
        if restaurant:
            return Table.objects.filter(restaurant=restaurant)
        return Table.objects.none()

    def perform_create(self, serializer):
        """Create table for current user's restaurant"""
        restaurant = Restaurant.objects.filter(owner=self.request.user).first()
        if not restaurant:
            raise ValueError('Restaurant not found')
        
        # Check plan limits
        can_add, error_msg = PlanEnforcementService.can_add_table(restaurant)
        if not can_add:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(error_msg)
        
        serializer.save(restaurant=restaurant)
        
        # Generate and store QR code
        instance = serializer.instance
        self._generate_qr_code(instance)

    def perform_update(self, serializer):
        """Update table"""
        serializer.save()

    @action(detail=True, methods=['get'])
    def qr_code(self, request, pk=None):
        """Get QR code for table"""
        table = get_object_or_404(Table, pk=pk, restaurant__owner=request.user)
        return Response({
            'table_id': table.id,
            'table_name': table.name,
            'qr_url': self._get_qr_code_url(table),
            'public_url': f'https://app.seatserve.local/order/{table.restaurant.public_id}/{table.token}'
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get table statistics"""
        restaurant = Restaurant.objects.filter(owner=request.user).first()
        if not restaurant:
            return Response(
                {'detail': 'Restaurant not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        tables = Table.objects.filter(restaurant=restaurant)
        plan_info = PlanEnforcementService.get_plan_info(restaurant)
        
        return Response({
            'total_tables': tables.count(),
            'active_tables': tables.filter(is_active=True).count(),
            'inactive_tables': tables.filter(is_active=False).count(),
            'plan': plan_info,
        })

    def _generate_qr_code(self, table):
        """Generate QR code for a table"""
        url = f'https://app.seatserve.local/order/{table.restaurant.public_id}/{table.token}'
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        
        # Save to BytesIO and convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Store as data URL or file URL (here we'll just store the URL for now)
        # In production, save to S3 or file storage
        table.qr_code_url = f'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode()
        table.save()

    def _get_qr_code_url(self, table):
        """Get QR code for a table"""
        if not table.qr_code_url:
            self._generate_qr_code(table)
        return table.qr_code_url
