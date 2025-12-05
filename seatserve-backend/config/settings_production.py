"""
Production-specific settings for SeatServe
Import this in addition to base settings in production environment
"""

import os
from decouple import config

# ============================================================================
# SECURITY SETTINGS (Production)
# ============================================================================

# HTTPS & Security Headers
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookie Security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'

# Host validation
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

# ============================================================================
# DATABASE (Production)
# ============================================================================

# Use managed database (Railway, Render, AWS RDS, etc.)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='seatserve'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='db'),
        'PORT': config('DB_PORT', default='5432', cast=int),
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# Alternative: Use DATABASE_URL format (Railway/Render compatibility)
import dj_database_url
if config('DATABASE_URL', default=None):
    DATABASES['default'] = dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )

# ============================================================================
# CACHING (Redis)
# ============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,  # Cache failures don't crash app
        }
    }
}

# ============================================================================
# STATIC FILES (Production)
# ============================================================================

# WhiteNoise for efficient static file serving
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Must be after SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

# Static files compression
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'staticfiles')
STATIC_URL = '/static/'

# Serve frontend from static files
STATICFILES_DIRS = [
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'),
]

# ============================================================================
# LOGGING (Production)
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/seatserve.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 20,
            'formatter': 'json',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/security.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 20,
            'formatter': 'json',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'seatserve': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ============================================================================
# PERFORMANCE & OPTIMIZATION
# ============================================================================

# Connection pooling
CONN_MAX_AGE = 600

# Email backend (for production notifications)
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)

# ============================================================================
# API & CORS Configuration
# ============================================================================

CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='https://localhost:3000'
).split(',')

CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

# ============================================================================
# STRIPE CONFIGURATION (if applicable)
# ============================================================================

STRIPE_LIVE_PUBLIC_KEY = config('STRIPE_LIVE_PUBLIC_KEY', default='')
STRIPE_LIVE_SECRET_KEY = config('STRIPE_LIVE_SECRET_KEY', default='')
STRIPE_TEST_PUBLIC_KEY = config('STRIPE_TEST_PUBLIC_KEY', default='')
STRIPE_TEST_SECRET_KEY = config('STRIPE_TEST_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')

# Use live keys in production
if not config('DEBUG', default=False, cast=bool):
    STRIPE_PUBLIC_KEY = STRIPE_LIVE_PUBLIC_KEY
    STRIPE_SECRET_KEY = STRIPE_LIVE_SECRET_KEY
else:
    STRIPE_PUBLIC_KEY = STRIPE_TEST_PUBLIC_KEY
    STRIPE_SECRET_KEY = STRIPE_TEST_SECRET_KEY

# ============================================================================
# CONTENT DELIVERY & COMPRESSION
# ============================================================================

# GZip compression
MIDDLEWARE += ['django.middleware.gzip.GZipMiddleware']

# REST Framework compression
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    }
}

# ============================================================================
# RATE LIMITING (DDoS Protection)
# ============================================================================

# Already configured in main settings.py but can be overridden here
DEFAULT_THROTTLE_RATES = {
    'anon': '100/hour',
    'user': '1000/hour',
    'login': '5/minute',
    'register': '3/hour',
    'webhook': '1000/hour',
}

# ============================================================================
# ERROR TRACKING (Optional - Sentry)
# ============================================================================

SENTRY_DSN = config('SENTRY_DSN', default=None)

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment=config('ENVIRONMENT', default='production'),
    )

# ============================================================================
# DEBUG & TESTING
# ============================================================================

DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

# Disallow DEBUG in production
if DEBUG:
    raise ValueError('DEBUG must be False in production!')

# ============================================================================
# SUMMARY
# ============================================================================
# This configuration ensures:
# ✅ HTTPS + Security headers
# ✅ Database connection pooling
# ✅ Redis caching
# ✅ Static files optimization
# ✅ Production logging
# ✅ Error tracking (Sentry)
# ✅ Rate limiting
# ✅ CORS restrictions
# ✅ Email backend
