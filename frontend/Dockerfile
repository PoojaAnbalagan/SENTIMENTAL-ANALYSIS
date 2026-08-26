# =============================================================================
# Frontend Dockerfile — McDonald's Sentiment Analysis Platform
# =============================================================================
# Multi-stage build: Node build → Nginx production image
# Build context: frontend/ directory
# Usage (from repo root):
#   docker build -f frontend/Dockerfile -t sentiment-frontend ./frontend
#   docker run -p 80:80 sentiment-frontend
# =============================================================================

# =============================================================================
# Stage 1: BUILD — compile React app with Vite
# =============================================================================
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package manifests first for layer cache efficiency
# Only re-runs npm ci when package-lock.json changes
COPY package.json package-lock.json ./

# Install exact dependency versions (reproducible build)
RUN npm ci

# Copy all frontend source files
COPY . .

# Build the production bundle
# Outputs to /app/dist/
ENV NODE_ENV=production
RUN npm run build

# =============================================================================
# Stage 2: PRODUCTION — serve static files with Nginx
# =============================================================================
FROM nginx:1.27-alpine AS production

# Remove default Nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/app.conf

# Copy the React production build from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx runs as root by default; set up for non-root if desired
# For simplicity in K8s we keep default nginx user
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost/health || exit 1

# Nginx starts automatically; use CMD to stay in foreground
CMD ["nginx", "-g", "daemon off;"]
