"""
URL configuration for seatserve project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
import os

def index_view(request):
    """Serve React index.html for SPA routing"""
    index_path = os.path.join(settings.STATIC_ROOT, 'frontend', 'index.html')
    if os.path.isfile(index_path):
        with open(index_path, 'rb') as f:
            return HttpResponse(f.read(), content_type='text/html')
    # Fallback 404 if index.html not found
    return HttpResponse('Frontend not found', status=404)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/restaurants/', include('restaurants.urls')),
    path('api/menu/', include('menu.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/public/', include('orders.public_urls')),
    path('api/payments/', include('payments.urls')),
    path('', index_view),  # SPA catch-all
]

# Serve static/media in development only
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
