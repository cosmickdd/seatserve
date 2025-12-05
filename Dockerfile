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
RUN VITE_API_URL=/api npm run build && \
    echo "=== Frontend Build Complete ===" && \
    echo "Checking /app/frontend/dist contents:" && \
    ls -la /app/frontend/dist/ && \
    if [ -f /app/frontend/dist/index.html ]; then \
        echo "✓ index.html successfully built"; \
    else \
        echo "✗ ERROR: index.html not in dist folder!"; \
        exit 1; \
    fi

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

# Create necessary directories (ensure static exists for frontend files)
RUN mkdir -p /app/staticfiles /app/logs /app/static

# ============================================================================
# Copy Built Frontend to Backend Static Files
# ============================================================================
RUN echo "=== Step 0: Checking if static dir exists ===" && \
    ls -la /app/static/ || echo "Static dir created fresh"

RUN echo "=== Step 1: Copying frontend dist to backend static ===" && \
    ls -la /app/frontend/dist/ | head -20

COPY --from=frontend-builder /app/frontend/dist /app/static

RUN echo "=== After copy: Contents of /app/static ===" && \
    ls -la /app/static/ | head -30 && \
    if [ -f /app/static/index.html ]; then echo "✓ Frontend files copied successfully"; fi

# ============================================================================
# Collect Static Files & Verify Frontend
# ============================================================================
RUN echo "=== Step 1: Contents of /app/static before collectstatic ===" && \
    ls -la /app/static/ 2>/dev/null || echo "No /app/static yet" && \
    echo "" && \
    echo "=== Step 2: Running collectstatic ===" && \
    python manage.py collectstatic --noinput --clear --verbosity 2 && \
    echo "" && \
    echo "=== Step 3: Contents of /app/staticfiles after collectstatic ===" && \
    ls -la /app/staticfiles/ && \
    echo "" && \
    echo "=== Step 4: Checking for index.html ===" && \
    if [ -f /app/staticfiles/index.html ]; then \
        echo "✓ SUCCESS: index.html found at /app/staticfiles/index.html"; \
        ls -la /app/staticfiles/index.html; \
    else \
        echo "✗ ERROR: index.html NOT found"; \
        echo "Contents of /app/staticfiles/:"; \
        find /app/staticfiles/ -type f | head -20; \
    fi

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
