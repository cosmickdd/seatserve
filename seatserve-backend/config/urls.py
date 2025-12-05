"""
URL configuration for seatserve project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.static import serve
import os

def serve_spa(request, path=''):
    """
    Serve React SPA files from static/frontend directory.
    For any non-API route, serve index.html to let React Router handle it.
    """
    # Don't handle API routes
    if path.startswith('api/'):
        return None
    
    frontend_dir = os.path.join(settings.STATIC_ROOT, 'frontend')
    requested_file = os.path.join(frontend_dir, path)
    
    # If it's a static file that exists, serve it
    if os.path.isfile(requested_file):
        return serve(request, os.path.join('frontend', path), document_root=settings.STATIC_ROOT)
    
    # For everything else, serve index.html (SPA routing)
    index_file = os.path.join(frontend_dir, 'index.html')
    if os.path.isfile(index_file):
        with open(index_file, 'rb') as f:
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
]

# Serve static files with WhiteNoise in production
if not settings.DEBUG:
    # Serve static files explicitly
    urlpatterns += [
        path('static/<path:path>', serve, {'document_root': settings.STATIC_ROOT}),
    ]
    # SPA catch-all for all non-API routes
    urlpatterns += [
        re_path(r'^(?!admin/)(?!api/)(?P<path>.*)$', serve_spa, name='spa_catchall'),
    ]
else:
    # Development: use Django's default static file serving
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [
        re_path(r'^(?!admin/)(?!api/)(?P<path>.*)$', serve_spa, name='spa_catchall'),
    ]
