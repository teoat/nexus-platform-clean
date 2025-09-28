#!/bin/bash

# NEXUS Platform - Local Development Startup Script
# Starts the complete local development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    log_info "Checking Docker status..."
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    log_success "Docker is running"
}

# Check if Docker Compose is available
check_docker_compose() {
    log_info "Checking Docker Compose..."
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose not found. Please install Docker Compose."
        exit 1
    fi
    log_success "Docker Compose is available"
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    mkdir -p logs/{backend,frontend,nginx}
    mkdir -p config/{nginx,prometheus,grafana,logstash}
    mkdir -p data/{postgres,redis,prometheus,grafana,elasticsearch}
    log_success "Directories created"
}

# Create local environment file
create_env_file() {
    log_info "Creating local environment file..."
    cat > .env.local << EOF
# NEXUS Platform - Local Development Environment
NEXUS_ENV=local
NEXUS_DEBUG=true
LOG_LEVEL=DEBUG

# Database
POSTGRES_DB=nexus_local
POSTGRES_USER=nexus
POSTGRES_PASSWORD=nexus123
DATABASE_URL=postgresql://nexus:nexus123@postgres:5432/nexus_local

# Redis
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_DEBUG=true

# Frontend
REACT_APP_API_URL=http://localhost:8000
REACT_APP_DEBUG=true
REACT_APP_ENV=local

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
GRAFANA_ADMIN_PASSWORD=admin123

# Logging
ELASTICSEARCH_URL=http://elasticsearch:9200
KIBANA_URL=http://kibana:5601
EOF
    log_success "Environment file created"
}

# Create Nginx configuration
create_nginx_config() {
    log_info "Creating Nginx configuration..."
    mkdir -p config/nginx
    cat > config/nginx/nginx.local.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name localhost;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # Health checks
        location /health {
            proxy_pass http://backend/health;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
    }
}
EOF
    log_success "Nginx configuration created"
}

# Create Prometheus configuration
create_prometheus_config() {
    log_info "Creating Prometheus configuration..."
    mkdir -p config/prometheus
    cat > config/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'frontend'
    static_configs:
      - targets: ['frontend:3000']
    metrics_path: '/metrics'
    scrape_interval: 5s
EOF
    log_success "Prometheus configuration created"
}

# Create Logstash configuration
create_logstash_config() {
    log_info "Creating Logstash configuration..."
    mkdir -p config/logstash
    cat > config/logstash/logstash.conf << EOF
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "backend" {
    grok {
      match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}" }
    }
  }

  if [fields][service] == "frontend" {
    grok {
      match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "nexus-logs-%{+YYYY.MM.dd}"
  }
}
EOF
    log_success "Logstash configuration created"
}

# Start the development environment
start_environment() {
    log_info "Starting local development environment..."

    # Load environment variables
    if [ -f .env.local ]; then
        export $(cat .env.local | grep -v '^#' | xargs)
    fi

    # Start services
    docker-compose -f docker-compose.local.yml up -d

    log_success "Local development environment started"
}

# Wait for services to be ready
wait_for_services() {
    log_info "Waiting for services to be ready..."

    # Wait for backend
    log_info "Waiting for backend service..."
    timeout=60
    while ! curl -f http://localhost:8000/health > /dev/null 2>&1; do
        sleep 1
        timeout=$((timeout - 1))
        if [ $timeout -eq 0 ]; then
            log_error "Backend service failed to start"
            exit 1
        fi
    done
    log_success "Backend service is ready"

    # Wait for frontend
    log_info "Waiting for frontend service..."
    timeout=60
    while ! curl -f http://localhost:3000 > /dev/null 2>&1; do
        sleep 1
        timeout=$((timeout - 1))
        if [ $timeout -eq 0 ]; then
            log_error "Frontend service failed to start"
            exit 1
        fi
    done
    log_success "Frontend service is ready"
}

# Display service URLs
display_urls() {
    log_success "Local development environment is ready!"
    echo ""
    echo "🌐 Service URLs:"
    echo "  Frontend:     http://localhost:3000"
    echo "  Backend API:  http://localhost:8000"
    echo "  Nginx:        http://localhost:80"
    echo "  Prometheus:   http://localhost:9090"
    echo "  Grafana:      http://localhost:3001 (admin/admin123)"
    echo "  Kibana:       http://localhost:5601"
    echo "  Elasticsearch: http://localhost:9200"
    echo ""
    echo "📊 Monitoring:"
    echo "  Prometheus:   http://localhost:9090"
    echo "  Grafana:      http://localhost:3001"
    echo ""
    echo "📝 Logs:"
    echo "  View logs:    docker-compose -f docker-compose.local.yml logs -f"
    echo "  Backend logs: docker-compose -f docker-compose.local.yml logs -f backend"
    echo "  Frontend logs: docker-compose -f docker-compose.local.yml logs -f frontend"
    echo ""
    echo "🛠️  Development:"
    echo "  Stop services: docker-compose -f docker-compose.local.yml down"
    echo "  Restart:      docker-compose -f docker-compose.local.yml restart"
    echo "  Rebuild:      docker-compose -f docker-compose.local.yml up --build"
    echo ""
}

# Main execution
main() {
    echo "🚀 Starting NEXUS Platform Local Development Environment"
    echo "=================================================="

    check_docker
    check_docker_compose
    create_directories
    create_env_file
    create_nginx_config
    create_prometheus_config
    create_logstash_config
    start_environment
    wait_for_services
    display_urls

    log_success "Local development environment is ready!"
}

# Run main function
main "$@"
