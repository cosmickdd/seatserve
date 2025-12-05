from django.urls import path, include
from rest_framework.routers import DefaultRouter
from restaurants.views import (
    PlanViewSet, RestaurantViewSet, RestaurantSubscriptionViewSet, TableViewSet
)
from restaurants.staff_views import StaffMemberViewSet

router = DefaultRouter()
router.register(r'plans', PlanViewSet, basename='plan')
router.register(r'me', RestaurantViewSet, basename='restaurant')
router.register(r'subscriptions', RestaurantSubscriptionViewSet, basename='subscription')
router.register(r'tables', TableViewSet, basename='table')
router.register(r'staff', StaffMemberViewSet, basename='staff')

urlpatterns = [
    path('', include(router.urls)),
]
