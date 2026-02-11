#!/bin/bash
# ==============================================
# BourseChain Backend Entrypoint
# Waits for dependencies, runs migrations, starts server
# ==============================================

set -e

# ---------- Wait for PostgreSQL ----------
echo "⏳ Waiting for PostgreSQL (${DB_HOST:-postgres}:${DB_PORT:-5432})..."
while ! python -c "
import socket
s = socket.create_connection(('${DB_HOST:-postgres}', int('${DB_PORT:-5432}')), timeout=2)
s.close()
" 2>/dev/null; do
    sleep 2
done
echo "✅ PostgreSQL is ready!"

# ---------- Wait for Redis ----------
REDIS_HOST=$(echo "${REDIS_URL:-redis://redis:6379/1}" | sed -E 's|redis://([^:]+):.*|\1|')
REDIS_PORT=$(echo "${REDIS_URL:-redis://redis:6379/1}" | sed -E 's|redis://[^:]+:([0-9]+).*|\1|')
echo "⏳ Waiting for Redis (${REDIS_HOST}:${REDIS_PORT})..."
while ! python -c "
import socket
s = socket.create_connection(('${REDIS_HOST}', int('${REDIS_PORT}')), timeout=2)
s.close()
" 2>/dev/null; do
    sleep 2
done
echo "✅ Redis is ready!"

# ---------- Run Migrations ----------
echo "🔄 Running database migrations..."
python manage.py migrate --noinput
echo "✅ Migrations complete!"

# ---------- Collect Static Files ----------
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput
echo "✅ Static files collected!"

# ---------- Start Server ----------
echo "🚀 Starting BourseChain backend..."
exec "$@"
