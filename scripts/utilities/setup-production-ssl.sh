#!/bin/bash

# NEXUS Platform Production SSL Certificate Setup
# Automated SSL certificate management for production deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="${DOMAIN:-nexus.example.com}"
EMAIL="${EMAIL:-admin@nexus.example.com}"
SSL_DIR="/etc/ssl/nexus"
NGINX_SSL_DIR="/etc/nginx/ssl"
CERTBOT_DIR="/etc/letsencrypt"
STAGING="${STAGING:-false}"

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."

    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        log_error "This script must be run as root"
        exit 1
    fi

    # Check if certbot is installed
    if ! command -v certbot &> /dev/null; then
        log "Installing certbot..."
        apt-get update
        apt-get install -y certbot python3-certbot-nginx
        log_success "Certbot installed"
    else
        log_success "Certbot is already installed"
    fi

    # Check if nginx is installed
    if ! command -v nginx &> /dev/null; then
        log_error "Nginx is not installed. Please install nginx first."
        exit 1
    fi

    log_success "Prerequisites check completed"
}

# Create SSL directories
create_ssl_directories() {
    log "Creating SSL directories..."

    mkdir -p "$SSL_DIR"
    mkdir -p "$NGINX_SSL_DIR"
    mkdir -p "$CERTBOT_DIR"

    # Set proper permissions
    chmod 700 "$SSL_DIR"
    chmod 700 "$NGINX_SSL_DIR"
    chmod 700 "$CERTBOT_DIR"

    log_success "SSL directories created"
}

# Generate self-signed certificates (for development/testing)
generate_self_signed_cert() {
    log "Generating self-signed certificates for development..."

    local cert_file="$SSL_DIR/nexus.crt"
    local key_file="$SSL_DIR/nexus.key"
    local csr_file="$SSL_DIR/nexus.csr"

    # Generate private key
    openssl genrsa -out "$key_file" 2048

    # Generate certificate signing request
    openssl req -new -key "$key_file" -out "$csr_file" -subj "/C=US/ST=CA/L=San Francisco/O=NEXUS Platform/OU=IT Department/CN=$DOMAIN"

    # Generate self-signed certificate
    openssl x509 -req -days 365 -in "$csr_file" -signkey "$key_file" -out "$cert_file"

    # Generate Diffie-Hellman parameters
    openssl dhparam -out "$SSL_DIR/dhparam.pem" 2048

    # Copy to nginx directory
    cp "$cert_file" "$NGINX_SSL_DIR/"
    cp "$key_file" "$NGINX_SSL_DIR/"
    cp "$SSL_DIR/dhparam.pem" "$NGINX_SSL_DIR/"

    # Set proper permissions
    chmod 600 "$NGINX_SSL_DIR"/*.key
    chmod 644 "$NGINX_SSL_DIR"/*.crt
    chmod 644 "$NGINX_SSL_DIR"/*.pem

    log_success "Self-signed certificates generated"
}

# Obtain Let's Encrypt certificates
obtain_letsencrypt_cert() {
    log "Obtaining Let's Encrypt certificates..."

    local certbot_args=""

    if [ "$STAGING" = "true" ]; then
        certbot_args="--staging"
        log_warning "Using Let's Encrypt staging environment"
    fi

    # Stop nginx temporarily
    systemctl stop nginx

    # Obtain certificate
    certbot certonly \
        --standalone \
        --non-interactive \
        --agree-tos \
        --email "$EMAIL" \
        --domains "$DOMAIN" \
        $certbot_args

    # Copy certificates to nginx directory
    cp "$CERTBOT_DIR/live/$DOMAIN/fullchain.pem" "$NGINX_SSL_DIR/nexus.crt"
    cp "$CERTBOT_DIR/live/$DOMAIN/privkey.pem" "$NGINX_SSL_DIR/nexus.key"

    # Generate Diffie-Hellman parameters
    openssl dhparam -out "$NGINX_SSL_DIR/dhparam.pem" 2048

    # Set proper permissions
    chmod 600 "$NGINX_SSL_DIR"/*.key
    chmod 644 "$NGINX_SSL_DIR"/*.crt
    chmod 644 "$NGINX_SSL_DIR"/*.pem

    # Start nginx
    systemctl start nginx

    log_success "Let's Encrypt certificates obtained"
}

# Configure nginx for SSL
configure_nginx_ssl() {
    log "Configuring Nginx for SSL..."

    local nginx_conf="/etc/nginx/sites-available/nexus"

    cat > "$nginx_conf" << EOF
# NEXUS Platform SSL Configuration
server {
    listen 80;
    server_name $DOMAIN;

    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    # SSL Configuration
    ssl_certificate $NGINX_SSL_DIR/nexus.crt;
    ssl_certificate_key $NGINX_SSL_DIR/nexus.key;
    ssl_dhparam $NGINX_SSL_DIR/dhparam.pem;

    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:; frame-ancestors 'none';" always;

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # API proxy
    location /api/ {
        proxy_pass http://backend:8002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;

        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Static files
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Vary Accept-Encoding;
    }

    # Main application
    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
EOF

    # Enable the site
    ln -sf "$nginx_conf" /etc/nginx/sites-enabled/

    # Test nginx configuration
    nginx -t

    # Reload nginx
    systemctl reload nginx

    log_success "Nginx SSL configuration completed"
}

# Set up automatic certificate renewal
setup_certificate_renewal() {
    log "Setting up automatic certificate renewal..."

    # Create renewal script
    cat > /usr/local/bin/renew-nexus-certs.sh << 'EOF'
#!/bin/bash
# NEXUS Platform Certificate Renewal Script

DOMAIN="${DOMAIN:-nexus.example.com}"
NGINX_SSL_DIR="/etc/nginx/ssl"

# Renew certificates
certbot renew --quiet

# Copy renewed certificates
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $NGINX_SSL_DIR/nexus.crt
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $NGINX_SSL_DIR/nexus.key

# Reload nginx
systemctl reload nginx

# Log renewal
echo "$(date): Certificates renewed for $DOMAIN" >> /var/log/nexus-cert-renewal.log
EOF

    chmod +x /usr/local/bin/renew-nexus-certs.sh

    # Add cron job for automatic renewal
    (crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/renew-nexus-certs.sh") | crontab -

    log_success "Automatic certificate renewal configured"
}

# Verify SSL configuration
verify_ssl_configuration() {
    log "Verifying SSL configuration..."

    # Check if certificates exist
    if [ ! -f "$NGINX_SSL_DIR/nexus.crt" ] || [ ! -f "$NGINX_SSL_DIR/nexus.key" ]; then
        log_error "SSL certificates not found"
        return 1
    fi

    # Check certificate validity
    local cert_info=$(openssl x509 -in "$NGINX_SSL_DIR/nexus.crt" -text -noout)
    local subject=$(echo "$cert_info" | grep "Subject:" | head -1)
    local issuer=$(echo "$cert_info" | grep "Issuer:" | head -1)
    local not_after=$(echo "$cert_info" | grep "Not After" | head -1)

    log "Certificate Information:"
    log "  Subject: $subject"
    log "  Issuer: $issuer"
    log "  Valid Until: $not_after"

    # Test SSL connection
    if command -v openssl &> /dev/null; then
        local ssl_test=$(echo | openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" 2>/dev/null | openssl x509 -noout -dates)
        if [ $? -eq 0 ]; then
            log_success "SSL connection test passed"
        else
            log_warning "SSL connection test failed (domain may not be accessible)"
        fi
    fi

    log_success "SSL configuration verification completed"
}

# Generate SSL report
generate_ssl_report() {
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local report_file="/var/log/nexus-ssl-report-$timestamp.txt"

    log "Generating SSL report..."

    cat > "$report_file" << EOF
NEXUS Platform SSL Configuration Report
Generated: $(date)
Domain: $DOMAIN
SSL Directory: $NGINX_SSL_DIR

Certificate Files:
$(ls -la $NGINX_SSL_DIR/)

Certificate Information:
$(openssl x509 -in $NGINX_SSL_DIR/nexus.crt -text -noout | grep -E "(Subject:|Issuer:|Not Before|Not After)")

Nginx Configuration:
$(nginx -T 2>/dev/null | grep -A 20 "server_name $DOMAIN")

SSL Test Results:
$(echo | openssl s_client -connect $DOMAIN:443 -servername $DOMAIN 2>/dev/null | openssl x509 -noout -dates)

Cron Jobs:
$(crontab -l | grep renew-nexus-certs)
EOF

    log_success "SSL report generated: $report_file"
}

# Main execution
case "${1:-setup}" in
    "setup")
        check_prerequisites
        create_ssl_directories

        if [ "$STAGING" = "true" ] || [ "$2" = "staging" ]; then
            generate_self_signed_cert
        else
            obtain_letsencrypt_cert
            setup_certificate_renewal
        fi

        configure_nginx_ssl
        verify_ssl_configuration
        generate_ssl_report

        log_success "SSL setup completed successfully"
        ;;
    "renew")
        log "Renewing SSL certificates..."
        certbot renew --quiet
        cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $NGINX_SSL_DIR/nexus.crt
        cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $NGINX_SSL_DIR/nexus.key
        systemctl reload nginx
        log_success "SSL certificates renewed"
        ;;
    "verify")
        verify_ssl_configuration
        ;;
    "report")
        generate_ssl_report
        ;;
    *)
        echo "Usage: $0 {setup|renew|verify|report}"
        echo ""
        echo "Commands:"
        echo "  setup   - Set up SSL certificates and nginx configuration"
        echo "  renew   - Renew existing SSL certificates"
        echo "  verify  - Verify SSL configuration"
        echo "  report  - Generate SSL configuration report"
        echo ""
        echo "Environment Variables:"
        echo "  DOMAIN  - Domain name for SSL certificate (default: nexus.example.com)"
        echo "  EMAIL   - Email address for Let's Encrypt (default: admin@nexus.example.com)"
        echo "  STAGING - Use staging environment (default: false)"
        echo ""
        echo "Examples:"
        echo "  $0 setup"
        echo "  DOMAIN=nexus.mydomain.com EMAIL=admin@mydomain.com $0 setup"
        echo "  STAGING=true $0 setup"
        exit 1
        ;;
esac
