from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from menu.models import Category, MenuItem
from menu.serializers import CategorySerializer, MenuItemSerializer, MenuItemDetailSerializer
from restaurants.models import Restaurant
from restaurants.permissions import IsRestaurantUser
from restaurants.plan_service import PlanEnforcementService


class CategoryViewSet(viewsets.ModelViewSet):
    """Category management"""
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated, IsRestaurantUser)

    def get_queryset(self):
        """Get categories for current user's restaurant"""
        restaurant = Restaurant.objects.filter(owner=self.request.user).first()
        if restaurant:
            return Category.objects.filter(restaurant=restaurant)
        return Category.objects.none()

    def perform_create(self, serializer):
        """Create category for current user's restaurant"""
        restaurant = Restaurant.objects.filter(owner=self.request.user).first()
        if not restaurant:
            raise ValueError('Restaurant not found')
        serializer.save(restaurant=restaurant)

    def perform_update(self, serializer):
        """Update category"""
        serializer.save()


class MenuItemViewSet(viewsets.ModelViewSet):
    """Menu item management"""
    serializer_class = MenuItemSerializer
    permission_classes = (IsAuthenticated, IsRestaurantUser)

    def get_queryset(self):
        """Get menu items for current user's restaurant"""
        restaurant = Restaurant.objects.filter(owner=self.request.user).first()
        if restaurant:
            return MenuItem.objects.filter(restaurant=restaurant)
        return MenuItem.objects.none()

    def perform_create(self, serializer):
        """Create menu item for current user's restaurant"""
        restaurant = Restaurant.objects.filter(owner=self.request.user).first()
        if not restaurant:
            raise ValueError('Restaurant not found')
        
        # Check plan limits
        can_add, error_msg = PlanEnforcementService.can_add_menu_item(restaurant)
        if not can_add:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(error_msg)
        
        serializer.save(restaurant=restaurant)

    def perform_update(self, serializer):
        """Update menu item"""
        serializer.save()

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get menu items grouped by category"""
        restaurant = Restaurant.objects.filter(owner=request.user).first()
        if not restaurant:
            return Response(
                {'detail': 'Restaurant not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        categories = Category.objects.filter(restaurant=restaurant).prefetch_related('items')
        data = []
        for category in categories:
            data.append({
                'id': category.id,
                'name': category.name,
                'items': MenuItemSerializer(category.items.all(), many=True).data
            })
        return Response(data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get menu statistics"""
        restaurant = Restaurant.objects.filter(owner=request.user).first()
        if not restaurant:
            return Response(
                {'detail': 'Restaurant not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        items = MenuItem.objects.filter(restaurant=restaurant)
        plan_info = PlanEnforcementService.get_plan_info(restaurant)
        
        return Response({
            'total_items': items.count(),
            'available_items': items.filter(is_available=True).count(),
            'unavailable_items': items.filter(is_available=False).count(),
            'total_categories': Category.objects.filter(restaurant=restaurant).count(),
            'plan': plan_info,
        })
