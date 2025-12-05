from django.urls import path, include
from rest_framework.routers import DefaultRouter
from payments.views import PaymentViewSet, StripeWebhookViewSet

router = DefaultRouter()
router.register(r'', PaymentViewSet, basename='payment')
router.register(r'webhooks', StripeWebhookViewSet, basename='stripe-webhook')

urlpatterns = [
    path('', include(router.urls)),
]

