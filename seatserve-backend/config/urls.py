"""
URL configuration for seatserve project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.http import FileResponse
import os

def serve_frontend(request, path=''):
    """Serve frontend files from staticfiles/frontend"""
    frontend_path = os.path.join(settings.STATIC_ROOT, 'frontend')
    
    # Try exact file first
    file_path = os.path.join(frontend_path, path)
    if os.path.isfile(file_path):
        return serve(request, path, document_root=frontend_path)
    
    # Default to index.html for SPA routing
    index_path = os.path.join(frontend_path, 'index.html')
    if os.path.isfile(index_path):
        return FileResponse(open(index_path, 'rb'), content_type='text/html')
    
    # Fallback 404
    from django.http import HttpResponseNotFound
    return HttpResponseNotFound('Frontend files not found')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/restaurants/', include('restaurants.urls')),
    path('api/menu/', include('menu.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/public/', include('orders.public_urls')),
    path('api/payments/', include('payments.urls')),
]

# Serve static and frontend
if not settings.DEBUG:
    urlpatterns += [
        path('static/<path:path>', serve, {'document_root': settings.STATIC_ROOT}),
        re_path(r'^(?!api)(?P<path>.*)$', serve_frontend),  # Catch non-API routes
    ]
else:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
