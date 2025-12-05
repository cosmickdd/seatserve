"""
URL configuration for seatserve project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
import os

def spa_fallback(request, path=''):
    """
    Serve React index.html for SPA routing on all non-API routes.
    WhiteNoise will serve actual static files before this runs.
    """
    # Try to find index.html in multiple locations
    index_locations = [
        os.path.join(settings.STATIC_ROOT, 'frontend', 'index.html'),
        os.path.join(settings.STATIC_ROOT, 'index.html'),
        os.path.join(settings.BASE_DIR, 'static', 'frontend', 'index.html'),
    ]
    
    for index_path in index_locations:
        if os.path.isfile(index_path):
            with open(index_path, 'rb') as f:
                return HttpResponse(f.read(), content_type='text/html')
    
    return HttpResponse('Frontend not found', status=404)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/restaurants/', include('restaurants.urls')),
    path('api/menu/', include('menu.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/public/', include('orders.public_urls')),
    path('api/payments/', include('payments.urls')),
    # SPA catch-all: Serve React for all non-API routes (must be last)
    re_path(r'^(?!admin|api).*/$', spa_fallback),
    re_path(r'^(?!admin|api).*$', spa_fallback),
]

# Serve media in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
