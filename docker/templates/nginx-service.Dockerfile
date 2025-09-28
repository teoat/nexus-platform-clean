# Nginx Service Dockerfile Template
# Usage: Copy this template and customize for your nginx-based service

# Build stage
FROM nginx:{{NGINX_VERSION}}-alpine as builder

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/

# Copy static files
COPY html/ /usr/share/nginx/html/

# Production stage
FROM nginx:{{NGINX_VERSION}}-alpine as production

# Set environment variables
ENV NEXUS_MODE=production

# Copy configuration and static files from builder
COPY --from=builder /etc/nginx/nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /etc/nginx/conf.d/ /etc/nginx/conf.d/
COPY --from=builder /usr/share/nginx/html/ /usr/share/nginx/html/

# Create non-root user
RUN addgroup -g 1001 -S nginx && \
    adduser -S nginx -u 1001 -G nginx

# Set proper permissions
RUN chown -R nginx:nginx /var/cache/nginx /var/run /var/log/nginx /usr/share/nginx/html

# Switch to non-root user
USER nginx

# Expose port
EXPOSE {{PORT}}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:{{PORT}}/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]