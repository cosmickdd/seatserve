# ============================================================================
# PRODUCTION-READY MONOLITHIC DOCKERFILE
# Deploys Frontend + Backend in single container for Vercel/Railway
# ============================================================================

# Stage 1: Build Frontend
# ============================================================================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend source
COPY seatserve-frontend/package*.json ./
RUN npm install --legacy-peer-deps

COPY seatserve-frontend .

# Build frontend for production
RUN npm run build

# ============================================================================
# Stage 2: Build Backend & Runtime
# ============================================================================
FROM python:3.11-slim

WORKDIR /app

# ============================================================================
# Environment Setup
# ============================================================================
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/app/venv/bin:$PATH"
ENV NODE_ENV=production

# ============================================================================
# Install System Dependencies
# ============================================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# Python Setup
# ============================================================================
COPY seatserve-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn whitenoise

# ============================================================================
# Backend Setup
# ============================================================================
COPY seatserve-backend . 

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/logs

# ============================================================================
# Copy Built Frontend to Backend Static Files
# ============================================================================
COPY --from=frontend-builder /app/frontend/dist /app/static

# ============================================================================
# Collect Static Files & Verify Frontend
# ============================================================================
RUN echo "=== Collecting static files ===" && \
    python manage.py collectstatic --noinput --clear && \
    echo "=== Checking frontend files ===" && \
    ls -la /app/staticfiles/ && \
    if [ -f /app/staticfiles/index.html ]; then echo "✓ Frontend index.html found"; else echo "✗ WARNING: index.html not found!"; fi && \
    echo "✓ Static files collected successfully"

# ============================================================================
# Configuration & Health Check
# ============================================================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health/ || exit 1

# ============================================================================
# Expose Port
# ============================================================================
EXPOSE ${PORT:-8000}

# ============================================================================
# Production Start Command
# ============================================================================
CMD exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 4 \
    --worker-class sync \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
