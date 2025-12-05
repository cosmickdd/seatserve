"""
URL configuration for seatserve project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, FileResponse
from django.views.static import serve
import os

# Serve React SPA
def frontend_fallback(request, path=''):
    """
    Serve React frontend from staticfiles/frontend/ or staticfiles/
    Falls back to index.html for client-side routing.
    """
    # Possible locations for frontend files
    possible_roots = [
        os.path.join(settings.STATIC_ROOT, 'frontend'),  # After collectstatic
        os.path.join(settings.STATIC_ROOT, 'frontend', 'assets'),  # Assets subfolder
        settings.STATIC_ROOT,  # Direct in staticfiles
    ]
    
    # Try to find and serve the requested file
    for root in possible_roots:
        file_path = os.path.join(root, path)
        if path and os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                # Determine content type
                if file_path.endswith('.js'):
                    content_type = 'application/javascript'
                elif file_path.endswith('.css'):
                    content_type = 'text/css'
                elif file_path.endswith('.json'):
                    content_type = 'application/json'
                elif file_path.endswith('.svg'):
                    content_type = 'image/svg+xml'
                elif file_path.endswith('.png'):
                    content_type = 'image/png'
                elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
                    content_type = 'image/jpeg'
                elif file_path.endswith('.woff2'):
                    content_type = 'font/woff2'
                else:
                    content_type = 'text/plain'
                return HttpResponse(f.read(), content_type=content_type)
    
    # Default to index.html for SPA routing
    for root in possible_roots:
        index_path = os.path.join(root, 'index.html')
        if os.path.isfile(index_path):
            with open(index_path, 'rb') as f:
                return HttpResponse(f.read(), content_type='text/html')
    
    return HttpResponse('Frontend index not found', status=404)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/restaurants/', include('restaurants.urls')),
    path('api/menu/', include('menu.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/public/', include('orders.public_urls')),
    path('api/payments/', include('payments.urls')),
]

# In production: WhiteNoise serves static files, add frontend catch-all
# In development: add debug routes
if not settings.DEBUG:
    # Serve static files directory (WhiteNoise handles this efficiently)
    urlpatterns += [
        path('static/<path:path>', serve, {'document_root': settings.STATIC_ROOT}),
    ]

# Frontend SPA catch-all - must be last!
# This catches everything that didn't match API or admin
urlpatterns += [
    re_path(r'^(?!admin/)(?!api/)(?!static/).*$', frontend_fallback),
]

# Development only
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
