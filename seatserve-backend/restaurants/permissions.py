from rest_framework.permissions import BasePermission


class IsRestaurantOwner(BasePermission):
    """Permission to check if user is the restaurant owner"""
    
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsRestaurantUser(BasePermission):
    """Permission to check if user has a restaurant"""
    
    def has_permission(self, request, view):
        return hasattr(request.user, 'restaurant')


class IsRestaurantTableOwner(BasePermission):
    """Permission to check if user owns the restaurant that owns this table"""
    
    def has_object_permission(self, request, view, obj):
        return obj.restaurant.owner == request.user


class IsRestaurantOrderOwner(BasePermission):
    """Permission to check if user owns the restaurant that has this order"""
    
    def has_object_permission(self, request, view, obj):
        return obj.restaurant.owner == request.user
