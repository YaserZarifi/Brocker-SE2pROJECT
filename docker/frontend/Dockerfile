# ==============================================
# BourseChain Frontend - React + Nginx
# Sprint 6 - Docker (Multi-stage build)
# ==============================================

# ---------- Stage 1: Build React App ----------
FROM docker.arvancloud.ir/node:20-alpine AS builder

WORKDIR /app

# Install dependencies (cached layer)
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci 2>/dev/null || npm install

# Copy source and build
COPY frontend/ ./
RUN npm run build

# ---------- Stage 2: Serve with Nginx ----------
FROM docker.arvancloud.ir/nginx:1.27-alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config (proxies /api + /ws to backend)
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built React app
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose HTTP port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -q --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
