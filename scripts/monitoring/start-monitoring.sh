#!/bin/bash
# NEXUS Platform - Monitoring Stack Startup Script
# Phase 2: Advanced Integration

set -e

echo "🚀 Starting NEXUS Platform Monitoring Stack..."

# Create data directories
mkdir -p /data/prometheus /data/grafana /data/loki /data/tempo

# Set permissions
chown -R prometheus:prometheus /data/prometheus
chown -R grafana:grafana /data/grafana

# Start Prometheus in background
echo "📊 Starting Prometheus..."
prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/data/prometheus \
  --web.console.libraries=/etc/prometheus/console_libraries \
  --web.console.templates=/etc/prometheus/consoles \
  --web.enable-lifecycle \
  --web.enable-admin-api \
  --log.level=info &

# Start Grafana in background
echo "📈 Starting Grafana..."
grafana-server \
  --config=/etc/grafana/grafana.ini \
  --homepath=/usr/share/grafana \
  --packaging=docker &

# Start Loki in background
echo "📝 Starting Loki..."
loki -config.file=/etc/loki/loki.yml &

# Start Tempo in background
echo "🔍 Starting Tempo..."
tempo -config.file=/etc/tempo/tempo.yml &

# Wait for all services to start
sleep 10

# Health check
echo "🔍 Performing health checks..."
curl -f http://localhost:9090/-/healthy || echo "❌ Prometheus health check failed"
curl -f http://localhost:3000/api/health || echo "❌ Grafana health check failed"

echo "✅ NEXUS Platform Monitoring Stack started successfully!"
echo "📊 Prometheus: http://localhost:9090"
echo "📈 Grafana: http://localhost:3000 (admin/admin123)"
echo "📝 Loki: http://localhost:3100"
echo "🔍 Tempo: http://localhost:3200"

# Keep the script running
wait
