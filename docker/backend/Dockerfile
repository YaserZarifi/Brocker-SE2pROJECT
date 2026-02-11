# ==============================================
# BourseChain Backend - Django + Daphne (ASGI)
# Sprint 6 - Docker
# ==============================================

FROM docker.arvancloud.ir/python:3.12-slim

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings

WORKDIR /app

# Install system dependencies (PostgreSQL client + build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ .

# Copy entrypoint (fix Windows CRLF → LF)
COPY docker/backend/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

# Collect static files (whitenoise serves them in production)
RUN DJANGO_SECRET_KEY=build-placeholder \
    USE_SQLITE=True \
    USE_LOCMEM_CACHE=True \
    python manage.py collectstatic --noinput 2>/dev/null || true

# Expose Daphne port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
