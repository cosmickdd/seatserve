from django.urls import path, re_path
from orders.views import PublicOrderViewSet

# Custom URL patterns for public API with complex paths
public_views = PublicOrderViewSet()

urlpatterns = [
    # Menu endpoint
    re_path(
        r'^restaurant/(?P<restaurant_public_id>[^/]+)/table/(?P<table_token>[^/]+)/menu/$',
        public_views.menu,
        name='public_menu'
    ),
    # Create order endpoint
    re_path(
        r'^restaurant/(?P<restaurant_public_id>[^/]+)/table/(?P<table_token>[^/]+)/orders/$',
        public_views.create_order,
        name='create_public_order'
    ),
    # Order status endpoint
    re_path(
        r'^order/(?P<order_token>[^/]+)/$',
        public_views.order_status,
        name='order_status'
    ),
]
