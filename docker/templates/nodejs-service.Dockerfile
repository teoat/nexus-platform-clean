# Node.js Service Dockerfile Template
# Usage: Copy this template and customize for your Node.js service

# Build stage
FROM node:{{NODE_VERSION}}-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:{{NODE_VERSION}}-alpine as production

# Set environment variables
ENV NODE_ENV=production \
    NEXUS_MODE=production

# Create non-root user
RUN addgroup -g 1001 -S {{SERVICE_NAME}} && \
    adduser -S {{SERVICE_NAME}} -u 1001

# Set working directory
WORKDIR /app

# Copy built application from builder stage
COPY --from=builder --chown={{SERVICE_NAME}}:{{SERVICE_NAME}} /app/dist ./dist
COPY --from=builder --chown={{SERVICE_NAME}}:{{SERVICE_NAME}} /app/package*.json ./

# Install production dependencies only
RUN npm ci --only=production && \
    npm cache clean --force

# Switch to non-root user
USER {{SERVICE_NAME}}

# Expose port
EXPOSE {{PORT}}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node healthcheck.js || exit 1

# Start the application
CMD ["node", "dist/server.js"]