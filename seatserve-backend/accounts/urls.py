from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import UserRegistrationView, UserAuthView, UserProfileView

router = DefaultRouter()
router.register(r'register', UserRegistrationView, basename='register')
router.register(r'auth', UserAuthView, basename='auth')
router.register(r'profile', UserProfileView, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
]
