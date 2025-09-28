#!/bin/bash

# NEXUS Platform - Production Domain Setup Script
# Configure DNS, SSL certificates, and production domain

set -e

# Configuration
DOMAIN="nexus-platform.com"
EMAIL="admin@nexus-platform.com"
NGINX_CONFIG="/etc/nginx/sites-available/nexus-platform"
CERTBOT_DIR="/etc/letsencrypt/live/$DOMAIN"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        error "Please run as root (use sudo)"
        exit 1
    fi
}

# Install required packages
install_packages() {
    log "Installing required packages..."

    apt-get update
    apt-get install -y \
        nginx \
        certbot \
        python3-certbot-nginx \
        dnsutils \
        curl \
        wget \
        jq \
        ufw

    success "Packages installed"
}

# Configure firewall
configure_firewall() {
    log "Configuring firewall..."

    # Enable UFW
    ufw --force enable

    # Allow SSH
    ufw allow ssh

    # Allow HTTP and HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp

    # Allow NEXUS services
    ufw allow 8001/tcp  # Backend API
    ufw allow 3000/tcp  # Frontend
    ufw allow 9090/tcp  # Prometheus
    ufw allow 3001/tcp  # Grafana

    # Show status
    ufw status

    success "Firewall configured"
}

# Create Nginx configuration
create_nginx_config() {
    log "Creating Nginx configuration..."

    cat > "$NGINX_CONFIG" << EOF
# NEXUS Platform - Production Nginx Configuration
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL configuration (will be updated by certbot)
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Root location - serve frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # API endpoints
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8001/health;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}

# API subdomain
server {
    listen 443 ssl http2;
    server_name api.$DOMAIN;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # CORS headers
    add_header Access-Control-Allow-Origin "https://$DOMAIN" always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Requested-With" always;
    add_header Access-Control-Allow-Credentials "true" always;

    # API endpoints
    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}

# Monitoring subdomain
server {
    listen 443 ssl http2;
    server_name monitoring.$DOMAIN;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Basic authentication
    auth_basic "Monitoring Access";
    auth_basic_user_file /etc/nginx/.htpasswd;

    # Prometheus
    location /prometheus/ {
        proxy_pass http://localhost:9090/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Grafana
    location /grafana/ {
        proxy_pass http://localhost:3001/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Default to Prometheus
    location / {
        return 301 /prometheus/;
    }
}
EOF

    # Enable the site
    ln -sf "$NGINX_CONFIG" /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default

    # Test Nginx configuration
    nginx -t

    success "Nginx configuration created"
}

# Create certbot directory
create_certbot_directory() {
    log "Creating certbot directory..."

    mkdir -p /var/www/certbot
    chown -R www-data:www-data /var/www/certbot

    success "Certbot directory created"
}

# Generate SSL certificates
generate_ssl_certificates() {
    log "Generating SSL certificates..."

    # Start Nginx
    systemctl start nginx
    systemctl enable nginx

    # Generate certificates
    certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        --domains "$DOMAIN,www.$DOMAIN,api.$DOMAIN,monitoring.$DOMAIN"

    if [ $? -eq 0 ]; then
        success "SSL certificates generated"
    else
        error "SSL certificate generation failed"
        exit 1
    fi
}

# Configure automatic certificate renewal
configure_certificate_renewal() {
    log "Configuring automatic certificate renewal..."

    # Create renewal script
    cat > /etc/cron.d/certbot-renew << EOF
# Renew SSL certificates twice daily
0 12 * * * root certbot renew --quiet --post-hook "systemctl reload nginx"
0 0 * * * root certbot renew --quiet --post-hook "systemctl reload nginx"
EOF

    # Test renewal
    certbot renew --dry-run

    success "Certificate renewal configured"
}

# Create monitoring authentication
create_monitoring_auth() {
    log "Creating monitoring authentication..."

    # Create htpasswd file for monitoring
    htpasswd -cb /etc/nginx/.htpasswd admin "$(openssl rand -base64 12)"

    success "Monitoring authentication created"
}

# Test domain configuration
test_domain_configuration() {
    log "Testing domain configuration..."

    # Test DNS resolution
    if nslookup "$DOMAIN" > /dev/null 2>&1; then
        success "DNS resolution working"
    else
        warning "DNS resolution not working - please configure DNS records"
    fi

    # Test HTTP redirect
    if curl -s -I "http://$DOMAIN" | grep -q "301"; then
        success "HTTP to HTTPS redirect working"
    else
        warning "HTTP to HTTPS redirect not working"
    fi

    # Test HTTPS
    if curl -s -I "https://$DOMAIN" | grep -q "200"; then
        success "HTTPS working"
    else
        warning "HTTPS not working - check SSL certificates"
    fi
}

# Display configuration information
display_configuration_info() {
    log "Domain configuration completed!"
    echo
    echo "=========================================="
    echo "NEXUS Platform - Domain Configuration"
    echo "=========================================="
    echo
    echo "🌐 Main Domain: https://$DOMAIN"
    echo "🔧 API Domain: https://api.$DOMAIN"
    echo "📊 Monitoring: https://monitoring.$DOMAIN"
    echo
    echo "📋 DNS Records Required:"
    echo "  A    $DOMAIN           -> YOUR_SERVER_IP"
    echo "  A    www.$DOMAIN       -> YOUR_SERVER_IP"
    echo "  A    api.$DOMAIN       -> YOUR_SERVER_IP"
    echo "  A    monitoring.$DOMAIN -> YOUR_SERVER_IP"
    echo
    echo "🔐 SSL Certificates:"
    echo "  Location: $CERTBOT_DIR"
    echo "  Auto-renewal: Configured"
    echo
    echo "🔧 Nginx Configuration:"
    echo "  Config: $NGINX_CONFIG"
    echo "  Status: systemctl status nginx"
    echo "  Reload: systemctl reload nginx"
    echo
}

# Main function
main() {
    log "Starting NEXUS Platform domain setup..."

    check_root
    install_packages
    configure_firewall
    create_nginx_config
    create_certbot_directory
    generate_ssl_certificates
    configure_certificate_renewal
    create_monitoring_auth
    test_domain_configuration
    display_configuration_info

    success "Domain setup completed successfully!"
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --test         Test domain configuration only"
        echo "  --renew        Renew SSL certificates"
        echo
        exit 0
        ;;
    --test)
        test_domain_configuration
        ;;
    --renew)
        certbot renew --post-hook "systemctl reload nginx"
        ;;
    *)
        main
        ;;
esac
