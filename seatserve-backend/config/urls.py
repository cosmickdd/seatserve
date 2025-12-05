"""
URL configuration for seatserve project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, JsonResponse
import os

# Health check endpoint
def health_check(request):
    """Simple health check for deployment platforms."""
    return JsonResponse({
        'status': 'healthy',
        'service': 'SeatServe',
        'environment': 'production' if not settings.DEBUG else 'development'
    })

def spa_fallback(request, path=''):
    """
    Serve React index.html for SPA routing on all non-API routes.
    WhiteNoise will serve actual static files before this runs.
    """
    import os
    
    # After collectstatic, index.html should be in STATIC_ROOT
    index_path = os.path.join(settings.STATIC_ROOT, 'index.html')
    
    if os.path.isfile(index_path):
        with open(index_path, 'rb') as f:
            return HttpResponse(f.read(), content_type='text/html; charset=utf-8')
    
    # Fallback message if index.html not found
    return HttpResponse(
        '<!DOCTYPE html><html><body><h1>Frontend Not Found</h1>'
        '<p>index.html could not be located at: ' + index_path + '</p></body></html>',
        status=404,
        content_type='text/html'
    )

urlpatterns = [
    path('health/', health_check),
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/restaurants/', include('restaurants.urls')),
    path('api/menu/', include('menu.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/public/', include('orders.public_urls')),
    path('api/payments/', include('payments.urls')),
    # Root path - serve index.html
    path('', spa_fallback),
    # SPA catch-all: Serve React for all other non-API routes
    # This matches any path that doesn't start with admin/, api/, or static/
    re_path(r'^(?!admin/|api/|static/|media/).*$', spa_fallback),
]

# Serve media in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
