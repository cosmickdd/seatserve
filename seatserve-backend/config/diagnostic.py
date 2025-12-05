"""
Production Diagnostic Module
Comprehensive diagnostics for Render deployment issues
Run: python manage.py shell < diagnostic.py
"""

import os
import sys
from pathlib import Path
from django.conf import settings

class ProductionDiagnostic:
    """Comprehensive diagnostic checker for production deployment"""
    
    def __init__(self):
        self.BASE_DIR = settings.BASE_DIR
        self.STATIC_ROOT = settings.STATIC_ROOT
        self.STATIC_URL = settings.STATIC_URL
        self.STATICFILES_DIRS = settings.STATICFILES_DIRS
        self.DEBUG = settings.DEBUG
        self.results = []
        self.errors = []
        self.warnings = []
    
    def log(self, message, level="INFO"):
        """Log a diagnostic message"""
        timestamp = self._get_timestamp()
        formatted = f"[{timestamp}] [{level:8}] {message}"
        self.results.append(formatted)
        print(formatted)
    
    def error(self, message):
        """Log an error"""
        self.log(message, "ERROR")
        self.errors.append(message)
    
    def warning(self, message):
        """Log a warning"""
        self.log(message, "WARNING")
        self.warnings.append(message)
    
    def success(self, message):
        """Log a success message"""
        self.log(f"✓ {message}", "SUCCESS")
    
    def _get_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def check_environment(self):
        """Check Django environment settings"""
        self.log("\n" + "="*70, "INFO")
        self.log("DJANGO ENVIRONMENT", "INFO")
        self.log("="*70, "INFO")
        
        self.log(f"DEBUG: {self.DEBUG}", "INFO")
        self.log(f"BASE_DIR: {self.BASE_DIR}", "INFO")
        self.log(f"STATIC_ROOT: {self.STATIC_ROOT}", "INFO")
        self.log(f"STATIC_URL: {self.STATIC_URL}", "INFO")
        self.log(f"STATICFILES_DIRS: {self.STATICFILES_DIRS}", "INFO")
        
        if self.DEBUG:
            self.warning("DEBUG=True in production! Should be False")
        else:
            self.success("DEBUG=False (correct for production)")
    
    def check_static_directories(self):
        """Check if static directories exist"""
        self.log("\n" + "="*70, "INFO")
        self.log("STATIC FILE DIRECTORIES", "INFO")
        self.log("="*70, "INFO")
        
        # Check STATIC_ROOT
        if os.path.isdir(self.STATIC_ROOT):
            file_count = len(list(Path(self.STATIC_ROOT).rglob('*')))
            self.success(f"STATIC_ROOT exists with {file_count} files")
        else:
            self.error(f"STATIC_ROOT does not exist: {self.STATIC_ROOT}")
        
        # Check STATICFILES_DIRS
        for static_dir in self.STATICFILES_DIRS:
            if os.path.isdir(static_dir):
                file_count = len(list(Path(static_dir).rglob('*')))
                self.success(f"STATICFILES_DIR exists: {static_dir} ({file_count} files)")
            else:
                self.warning(f"STATICFILES_DIR not found: {static_dir}")
    
    def check_index_html(self):
        """Check if index.html exists in the right places"""
        self.log("\n" + "="*70, "INFO")
        self.log("FRONTEND INDEX.HTML CHECK", "INFO")
        self.log("="*70, "INFO")
        
        locations = [
            ("STATIC_ROOT", os.path.join(self.STATIC_ROOT, 'index.html')),
            ("static/ dir", os.path.join(self.BASE_DIR, 'static', 'index.html')),
            ("static/frontend/", os.path.join(self.BASE_DIR, 'static', 'frontend', 'index.html')),
        ]
        
        found_index = False
        for location_name, path in locations:
            if os.path.isfile(path):
                file_size = os.path.getsize(path)
                self.success(f"index.html found at {location_name}: {path} ({file_size} bytes)")
                found_index = True
                
                # Verify it's valid HTML
                try:
                    with open(path, 'r') as f:
                        content = f.read(100)
                        if '<!DOCTYPE html' in content or '<html' in content:
                            self.success(f"  → Valid HTML structure confirmed")
                        else:
                            self.error(f"  → File exists but may not be valid HTML")
                except Exception as e:
                    self.error(f"  → Could not read file: {e}")
            else:
                self.warning(f"index.html NOT found at {location_name}")
        
        if not found_index:
            self.error("CRITICAL: index.html not found in any location!")
        
        return found_index
    
    def check_static_files(self):
        """Check what static files are present"""
        self.log("\n" + "="*70, "INFO")
        self.log("STATIC FILES INVENTORY", "INFO")
        self.log("="*70, "INFO")
        
        if os.path.isdir(self.STATIC_ROOT):
            # Count file types
            file_types = {}
            total_size = 0
            
            for root, dirs, files in os.walk(self.STATIC_ROOT):
                for file in files:
                    filepath = os.path.join(root, file)
                    ext = os.path.splitext(file)[1] or 'no_ext'
                    
                    if ext not in file_types:
                        file_types[ext] = {'count': 0, 'size': 0}
                    
                    file_types[ext]['count'] += 1
                    file_types[ext]['size'] += os.path.getsize(filepath)
                    total_size += os.path.getsize(filepath)
            
            self.log(f"Total files: {sum(f['count'] for f in file_types.values())}", "INFO")
            self.log(f"Total size: {self._format_size(total_size)}", "INFO")
            self.log("\nBreakdown by file type:", "INFO")
            
            for ext in sorted(file_types.keys()):
                data = file_types[ext]
                self.log(f"  {ext:15} {data['count']:6} files  {self._format_size(data['size']):10}", "INFO")
        else:
            self.error(f"STATIC_ROOT directory does not exist: {self.STATIC_ROOT}")
    
    def check_django_settings(self):
        """Check critical Django settings"""
        self.log("\n" + "="*70, "INFO")
        self.log("DJANGO SETTINGS CHECK", "INFO")
        self.log("="*70, "INFO")
        
        # Check ALLOWED_HOSTS
        allowed_hosts = settings.ALLOWED_HOSTS
        self.log(f"ALLOWED_HOSTS: {allowed_hosts}", "INFO")
        
        # Check STATICFILES_STORAGE
        storage = getattr(settings, 'STATICFILES_STORAGE', 'default')
        self.log(f"STATICFILES_STORAGE: {storage}", "INFO")
        if 'Compressed' in storage or 'Manifest' in storage:
            self.success("Using optimized static file storage")
        
        # Check middleware
        if 'whitenoise.middleware.WhiteNoiseMiddleware' in settings.MIDDLEWARE:
            self.success("WhiteNoise middleware is enabled")
        else:
            self.error("WhiteNoise middleware NOT found in MIDDLEWARE")
        
        # Check SECURE settings
        self.log(f"SECURE_SSL_REDIRECT: {getattr(settings, 'SECURE_SSL_REDIRECT', False)}", "INFO")
        self.log(f"SECURE_HSTS_SECONDS: {getattr(settings, 'SECURE_HSTS_SECONDS', 0)}", "INFO")
    
    def check_urls_configuration(self):
        """Check URL routing"""
        self.log("\n" + "="*70, "INFO")
        self.log("URL ROUTING CHECK", "INFO")
        self.log("="*70, "INFO")
        
        try:
            from django.urls import get_resolver
            resolver = get_resolver()
            patterns = resolver.url_patterns
            self.log(f"Total URL patterns: {len(patterns)}", "INFO")
            
            pattern_names = []
            for pattern in patterns:
                if hasattr(pattern, 'name'):
                    pattern_names.append(pattern.name)
            
            self.log(f"Named patterns: {', '.join(filter(None, pattern_names[:5]))}", "INFO")
            self.success("URL configuration loaded successfully")
        except Exception as e:
            self.error(f"Could not load URL configuration: {e}")
    
    def check_whitenoise(self):
        """Check WhiteNoise configuration"""
        self.log("\n" + "="*70, "INFO")
        self.log("WHITENOISE CHECK", "INFO")
        self.log("="*70, "INFO")
        
        try:
            import whitenoise
            self.log(f"WhiteNoise version: {whitenoise.__version__}", "INFO")
            self.success("WhiteNoise is installed")
        except ImportError:
            self.error("WhiteNoise is not installed!")
    
    def check_assets_directory(self):
        """Check if assets directory exists and has files"""
        self.log("\n" + "="*70, "INFO")
        self.log("ASSETS DIRECTORY CHECK", "INFO")
        self.log("="*70, "INFO")
        
        assets_path = os.path.join(self.STATIC_ROOT, 'assets')
        if os.path.isdir(assets_path):
            files = os.listdir(assets_path)
            self.success(f"Assets directory found with {len(files)} files")
            
            # Show file samples
            for file in files[:5]:
                self.log(f"  - {file}", "INFO")
            
            if len(files) > 5:
                self.log(f"  ... and {len(files) - 5} more", "INFO")
        else:
            self.warning(f"Assets directory not found: {assets_path}")
    
    def run_health_check_url(self):
        """Try to reach the health check endpoint"""
        self.log("\n" + "="*70, "INFO")
        self.log("HEALTH CHECK ENDPOINT TEST", "INFO")
        self.log("="*70, "INFO")
        
        try:
            from django.test.client import Client
            client = Client()
            response = client.get('/health/')
            
            if response.status_code == 200:
                self.success(f"Health endpoint returned {response.status_code}")
                self.log(f"Response: {response.content.decode()[:100]}", "INFO")
            else:
                self.error(f"Health endpoint returned {response.status_code}")
        except Exception as e:
            self.error(f"Could not test health endpoint: {e}")
    
    def generate_report(self):
        """Generate a summary report"""
        self.log("\n" + "="*70, "INFO")
        self.log("DIAGNOSTIC SUMMARY", "INFO")
        self.log("="*70, "INFO")
        
        self.log(f"Total checks: {len(self.results)}", "INFO")
        self.log(f"Errors: {len(self.errors)}", "ERROR" if self.errors else "INFO")
        self.log(f"Warnings: {len(self.warnings)}", "WARNING" if self.warnings else "INFO")
        
        if self.errors:
            self.log("\nCRITICAL ERRORS:", "ERROR")
            for error in self.errors:
                self.log(f"  - {error}", "ERROR")
        
        if self.warnings:
            self.log("\nWARNINGS:", "WARNING")
            for warning in self.warnings:
                self.log(f"  - {warning}", "WARNING")
        
        if not self.errors:
            self.log("\n✓ All critical checks passed!", "SUCCESS")
        else:
            self.log(f"\n✗ {len(self.errors)} critical issues found!", "ERROR")
        
        self.log("\n" + "="*70, "INFO")
    
    def _format_size(self, bytes_size):
        """Format bytes to human readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f}{unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f}TB"
    
    def run_all(self):
        """Run all diagnostics"""
        print("\n" + "█"*70)
        print("█ SeatServe Production Diagnostic System".ljust(70) + "█")
        print("█"*70 + "\n")
        
        self.check_environment()
        self.check_static_directories()
        self.check_index_html()
        self.check_static_files()
        self.check_django_settings()
        self.check_urls_configuration()
        self.check_whitenoise()
        self.check_assets_directory()
        self.run_health_check_url()
        self.generate_report()
        
        print("\n" + "█"*70 + "\n")
        
        return len(self.errors) == 0


# Run diagnostics
if __name__ == '__main__':
    diagnostic = ProductionDiagnostic()
    success = diagnostic.run_all()
    sys.exit(0 if success else 1)
