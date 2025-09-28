#!/bin/bash

# NEXUS Platform - Production SSL Setup Script
# Automates SSL certificate generation and renewal using Certbot with Nginx

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Configuration
DOMAIN="${DOMAIN}"
EMAIL="${EMAIL}"

if [ -z "$DOMAIN" ]; then
    log_error "DOMAIN environment variable is not set."
    exit 1
fi

if [ -z "$EMAIL" ]; then
    log_error "EMAIL environment variable is not set."
    exit 1
fi

# Ensure Nginx is running for Certbot to validate
ensure_nginx_running() {
    log "Ensuring Nginx is running for Certbot validation..."
    docker-compose -f docker-compose.production.yml --env-file .env.production up -d nginx
    sleep 5 # Give Nginx some time to start
    if ! docker-compose -f docker-compose.production.yml --env-file .env.production ps nginx | grep -q "Up"; then
        log_error "Nginx container is not running. Certbot validation will fail."
        exit 1
    fi
    log_success "Nginx is running."
}

# Stop Nginx after Certbot is done
stop_nginx() {
    log "Stopping Nginx after Certbot operation..."
    docker-compose -f docker-compose.production.yml --env-file .env.production stop nginx
    log_success "Nginx stopped."
}

# Obtain or renew SSL certificates
obtain_certificates() {
    log "Obtaining/renewing SSL certificates for $DOMAIN..."

    # Use certbot with --nginx authenticator
    # We need to run certbot in a separate container or ensure it's installed on the host
    # For simplicity, we'll assume certbot is available on the host or run it via docker
    # This example assumes certbot is installed on the host or in a way accessible to this script.
    # A more robust solution might involve a dedicated certbot container.

    # First, stop Nginx to free up port 80/443 for certbot standalone or use webroot
    # For --nginx authenticator, Nginx needs to be running and configured for the domain.
    # Let's use --webroot as it's generally safer and doesn't require stopping Nginx.
    # We need to ensure the webroot path is accessible to certbot.
    # Assuming Nginx serves static files from /var/www/static, which is mounted from ./static

    # Ensure the static directory exists for webroot
    mkdir -p ./static/.well-known/acme-challenge

    # Run Certbot in a Docker container to avoid host dependencies
    docker run -it --rm --name certbot \
        -v "$(pwd)/ssl:/etc/letsencrypt" \
        -v "$(pwd)/static:/var/www/static" \
        certbot/certbot certonly \
        --webroot -w /var/www/static \
        -d "$DOMAIN" \
        --email "$EMAIL" \
        --rsa-key-size 4096 \
        --agree-tos \
        --non-interactive \
        --force-renewal # Force renewal for testing, remove in production if not needed

    # Check if certificates were obtained
    if [ -f "./ssl/live/$DOMAIN/fullchain.pem" ] && [ -f "./ssl/live/$DOMAIN/privkey.pem" ]; then
        log_success "SSL certificates obtained successfully."
        # Copy to Nginx expected paths
        cp "./ssl/live/$DOMAIN/fullchain.pem" "./ssl/cert.pem"
        cp "./ssl/live/$DOMAIN/privkey.pem" "./ssl/key.pem"
        log_success "Certificates copied to Nginx SSL directory."
    else
        log_error "Failed to obtain SSL certificates."
        exit 1
    fi
}

# Setup cron job for automatic renewal
setup_renewal_cron() {
    log "Setting up cron job for automatic SSL certificate renewal..."
    # This cron job will run certbot renew daily.
    # The --nginx authenticator will automatically reload Nginx if certificates are renewed.
    # Ensure certbot is installed on the host or run via docker cron job.
    # For Docker Compose, a dedicated certbot container for renewal is often better.
    # For simplicity, we'll add a host cron job that runs certbot in a container.

    (crontab -l 2>/dev/null; echo "0 3 * * * docker run --rm -v \"$(pwd)/ssl:/etc/letsencrypt\" -v \"$(pwd)/static:/var/www/static\" certbot/certbot renew --webroot -w /var/www/static --post-hook \"docker-compose -f $(pwd)/docker-compose.production.yml --env-file $(pwd)/.env.production exec nginx nginx -s reload\"") | crontab -
    log_success "Cron job for SSL renewal set up."
}

case "$1" in
    "setup")
        ensure_nginx_running
        obtain_certificates
        setup_renewal_cron
        # Nginx will be restarted by deploy-production.sh after this script
        ;;
    "renew")
        log "Manually renewing SSL certificates..."
        docker run -it --rm --name certbot_renew \
            -v "$(pwd)/ssl:/etc/letsencrypt" \
            -v "$(pwd)/static:/var/www/static" \
            certbot/certbot renew --webroot -w /var/www/static \
            --post-hook "docker-compose -f $(pwd)/docker-compose.production.yml --env-file $(pwd)/.env.production exec nginx nginx -s reload"
        log_success "SSL certificates renewal attempted."
        ;;
    *)
        log_error "Usage: $0 {setup|renew}"
        exit 1
        ;;
esac
