"""
Diagnostic views for production troubleshooting
"""

import json
import os
from pathlib import Path
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def diagnostic_endpoint(request):
    """
    Production diagnostic endpoint
    Returns comprehensive system information for debugging
    Only accessible in non-production or with secret key
    """
    
    # Security: only show in debug or with special token
    secret = request.GET.get('secret', '')
    allowed_secret = getattr(settings, 'DIAGNOSTIC_SECRET', 'dev-secret-change-in-production')
    
    if not settings.DEBUG and secret != allowed_secret:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    def get_file_count_and_size(directory):
        """Get file count and size for a directory"""
        if not os.path.isdir(directory):
            return {'exists': False, 'count': 0, 'size': 0}
        
        count = 0
        total_size = 0
        for root, dirs, files in os.walk(directory):
            count += len(files)
            for file in files:
                try:
                    total_size += os.path.getsize(os.path.join(root, file))
                except:
                    pass
        
        return {
            'exists': True,
            'count': count,
            'size': total_size,
            'size_mb': round(total_size / 1024 / 1024, 2)
        }
    
    diagnostics = {
        'environment': {
            'debug': settings.DEBUG,
            'environment': getattr(settings, 'ENVIRONMENT', 'unknown'),
            'allowed_hosts': settings.ALLOWED_HOSTS,
        },
        'paths': {
            'base_dir': str(settings.BASE_DIR),
            'static_root': str(settings.STATIC_ROOT),
            'static_url': settings.STATIC_URL,
            'staticfiles_dirs': [str(d) for d in settings.STATICFILES_DIRS],
        },
        'static_files': {
            'static_root': get_file_count_and_size(settings.STATIC_ROOT),
            'static_dirs': [
                {
                    'path': str(d),
                    'info': get_file_count_and_size(str(d))
                }
                for d in settings.STATICFILES_DIRS
            ],
        },
        'frontend': {
            'index_html_locations': {}
        },
        'django_settings': {
            'static_storage': getattr(settings, 'STATICFILES_STORAGE', 'default'),
            'whitenoise_enabled': 'whitenoise.middleware.WhiteNoiseMiddleware' in settings.MIDDLEWARE,
            'secure_ssl_redirect': getattr(settings, 'SECURE_SSL_REDIRECT', False),
        },
        'checks': {
            'index_html_found': False,
            'static_root_exists': os.path.isdir(settings.STATIC_ROOT),
            'assets_directory_exists': os.path.isdir(os.path.join(settings.STATIC_ROOT, 'assets')),
        }
    }
    
    # Check for index.html
    index_locations = [
        os.path.join(settings.STATIC_ROOT, 'index.html'),
        os.path.join(settings.BASE_DIR, 'static', 'index.html'),
        os.path.join(settings.BASE_DIR, 'static', 'frontend', 'index.html'),
    ]
    
    for loc in index_locations:
        exists = os.path.isfile(loc)
        diagnostics['frontend']['index_html_locations'][loc] = exists
        if exists:
            diagnostics['checks']['index_html_found'] = True
    
    # List some sample static files
    if os.path.isdir(settings.STATIC_ROOT):
        sample_files = []
        for root, dirs, files in os.walk(settings.STATIC_ROOT):
            for file in files[:5]:  # Just first 5
                sample_files.append(os.path.join(root, file).replace(str(settings.STATIC_ROOT), ''))
        
        diagnostics['static_files']['sample_files'] = sample_files
    
    return JsonResponse(diagnostics, indent=2)


@require_http_methods(["GET"])
def diagnostic_summary(request):
    """
    Simple text-based diagnostic summary
    """
    
    lines = []
    lines.append("\n" + "="*70)
    lines.append("SeatServe Production Diagnostics")
    lines.append("="*70 + "\n")
    
    # Environment
    lines.append("ENVIRONMENT:")
    lines.append(f"  DEBUG: {settings.DEBUG}")
    lines.append(f"  STATIC_ROOT: {settings.STATIC_ROOT}")
    lines.append(f"  Static files exist: {os.path.isdir(settings.STATIC_ROOT)}")
    
    # Index.html check
    lines.append("\nFRONTEND:")
    index_found = False
    for loc in [
        os.path.join(settings.STATIC_ROOT, 'index.html'),
        os.path.join(settings.BASE_DIR, 'static', 'index.html'),
    ]:
        exists = os.path.isfile(loc)
        lines.append(f"  index.html at {loc}: {('✓ FOUND' if exists else '✗ NOT FOUND')}")
        if exists:
            index_found = True
    
    # Summary
    lines.append("\nSUMMARY:")
    if index_found:
        lines.append("  ✓ Frontend files appear to be present")
    else:
        lines.append("  ✗ CRITICAL: Frontend index.html not found!")
    
    if os.path.isdir(settings.STATIC_ROOT):
        file_count = sum([len(files) for r, d, files in os.walk(settings.STATIC_ROOT)])
        lines.append(f"  ✓ Static files collected ({file_count} files)")
    else:
        lines.append("  ✗ CRITICAL: Static root directory does not exist!")
    
    lines.append("\n" + "="*70 + "\n")
    
    return JsonResponse({
        'report': '\n'.join(lines),
        'timestamp': __import__('datetime').datetime.now().isoformat()
    })
