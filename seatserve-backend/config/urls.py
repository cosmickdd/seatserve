"""
URL configuration for seatserve project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, JsonResponse
import os

# Import diagnostic views
from config.diagnostic_views import diagnostic_endpoint, diagnostic_summary

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
    Static files are served by WhiteNoise middleware BEFORE this view runs.
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

# CRITICAL: Static file patterns MUST come FIRST before SPA fallback
# This ensures /static/* and /assets/* are served by Django/WhiteNoise, not by spa_fallback
urlpatterns = []

# Add static file serving FIRST (before any other patterns)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Production: Include static patterns so WhiteNoise middleware can intercept them
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# NOW add all other URL patterns (API, admin, etc.)
urlpatterns += [
    path('health/', health_check),
    path('diagnostic/', diagnostic_endpoint, name='diagnostic'),
    path('diagnostic/summary/', diagnostic_summary, name='diagnostic_summary'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/restaurants/', include('restaurants.urls')),
    path('api/menu/', include('menu.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/public/', include('orders.public_urls')),
    path('api/payments/', include('payments.urls')),
    
    # SPA Fallback Routes (LAST - catch-all patterns)
    # These run AFTER static file patterns, so /static/* and /assets/* won't reach here
    re_path(r'^(?!.*\.)([a-zA-Z0-9/_-]+)/?$', spa_fallback),  # Paths without extensions
    path('', spa_fallback),  # Root path
]
