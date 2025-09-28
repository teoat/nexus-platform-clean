#!/bin/bash
# NEXUS Platform - Domain Setup Script
# Complete domain configuration and validation

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN_NAME="${DOMAIN_NAME:-nexusplatform.com}"
AWS_REGION="${AWS_REGION:-us-east-1}"
NAMESPACE="nexus-platform"

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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi

    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed"
        exit 1
    fi

    if ! command -v curl &> /dev/null; then
        log_error "curl is not installed"
        exit 1
    fi

    if ! kubectl cluster-info &> /dev/null; then
        log_error "Kubernetes cluster is not accessible"
        exit 1
    fi

    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS CLI is not configured"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Get load balancer DNS name
get_load_balancer_dns() {
    log_info "Getting Application Load Balancer DNS name..."

    # Get ALB DNS name from Kubernetes service
    ALB_DNS_NAME=$(kubectl get service nexus-nginx -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")

    if [[ -z "$ALB_DNS_NAME" ]]; then
        # Try to get from AWS directly
        ALB_DNS_NAME=$(aws elbv2 describe-load-balancers \
            --query 'LoadBalancers[?contains(LoadBalancerName, `nexus-platform`)].DNSName' \
            --output text)
    fi

    if [[ -z "$ALB_DNS_NAME" ]]; then
        log_error "Could not find ALB DNS name"
        exit 1
    fi

    log_success "ALB DNS name: $ALB_DNS_NAME"
    echo "ALB_DNS_NAME=$ALB_DNS_NAME" >> .env
}

# Verify DNS resolution
verify_dns_resolution() {
    log_info "Verifying DNS resolution..."

    local max_attempts=30
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        if nslookup "$DOMAIN_NAME" > /dev/null 2>&1; then
            log_success "DNS resolution verified for $DOMAIN_NAME"
            break
        fi

        log_info "Attempt $attempt/$max_attempts: DNS not yet propagated, waiting..."
        sleep 10
        ((attempt++))
    done

    if [[ $attempt -gt $max_attempts ]]; then
        log_warning "DNS resolution verification timed out"
    fi
}

# Test HTTPS connectivity
test_https_connectivity() {
    log_info "Testing HTTPS connectivity..."

    local max_attempts=30
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        if curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN_NAME/health" | grep -q "200"; then
            log_success "HTTPS connectivity verified"
            break
        fi

        log_info "Attempt $attempt/$max_attempts: HTTPS not yet available, waiting..."
        sleep 10
        ((attempt++))
    done

    if [[ $attempt -gt $max_attempts ]]; then
        log_warning "HTTPS connectivity verification timed out"
    fi
}

# Test SSL certificate
test_ssl_certificate() {
    log_info "Testing SSL certificate..."

    # Check SSL certificate details
    local cert_info=$(echo | openssl s_client -servername "$DOMAIN_NAME" -connect "$DOMAIN_NAME:443" 2>/dev/null | openssl x509 -noout -dates 2>/dev/null || echo "")

    if [[ -n "$cert_info" ]]; then
        log_success "SSL certificate is valid"
        echo "Certificate details:"
        echo "$cert_info"
    else
        log_warning "SSL certificate validation failed"
    fi
}

# Test all endpoints
test_all_endpoints() {
    log_info "Testing all endpoints..."

    local endpoints=(
        "https://$DOMAIN_NAME/health"
        "https://$DOMAIN_NAME/api/health"
        "https://api.$DOMAIN_NAME/health"
        "https://monitoring.$DOMAIN_NAME"
        "https://grafana.$DOMAIN_NAME"
    )

    for endpoint in "${endpoints[@]}"; do
        log_info "Testing endpoint: $endpoint"

        local status_code=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint" || echo "000")

        if [[ "$status_code" == "200" ]]; then
            log_success "Endpoint $endpoint is accessible"
        else
            log_warning "Endpoint $endpoint returned status $status_code"
        fi
    done
}

# Check application health
check_application_health() {
    log_info "Checking application health..."

    # Check Kubernetes pods
    local pod_status=$(kubectl get pods -n $NAMESPACE -o jsonpath='{.items[*].status.phase}' | tr ' ' '\n' | sort -u)

    if echo "$pod_status" | grep -q "Running"; then
        log_success "Application pods are running"
    else
        log_warning "Some application pods may not be running"
    fi

    # Check services
    local service_count=$(kubectl get services -n $NAMESPACE --no-headers | wc -l)
    log_info "Found $service_count services in namespace $NAMESPACE"

    # Check ingress
    local ingress_count=$(kubectl get ingress -n $NAMESPACE --no-headers 2>/dev/null | wc -l || echo "0")
    log_info "Found $ingress_count ingress resources in namespace $NAMESPACE"
}

# Generate domain report
generate_domain_report() {
    log_info "Generating domain configuration report..."

    local report_file="/var/log/nexus/domain_setup_report_$(date +%Y%m%d_%H%M%S).json"

    cat > "$report_file" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "domain_name": "$DOMAIN_NAME",
    "alb_dns_name": "$ALB_DNS_NAME",
    "namespace": "$NAMESPACE",
    "dns_resolution": "$(nslookup $DOMAIN_NAME > /dev/null 2>&1 && echo 'success' || echo 'failed')",
    "https_connectivity": "$(curl -s -o /dev/null -w '%{http_code}' https://$DOMAIN_NAME/health 2>/dev/null || echo 'failed')",
    "ssl_certificate": "$(echo | openssl s_client -servername $DOMAIN_NAME -connect $DOMAIN_NAME:443 2>/dev/null | openssl x509 -noout -subject 2>/dev/null | cut -d'=' -f2- || echo 'unknown')",
    "pod_count": "$(kubectl get pods -n $NAMESPACE --no-headers | wc -l)",
    "service_count": "$(kubectl get services -n $NAMESPACE --no-headers | wc -l)",
    "status": "completed"
}
EOF

    log_success "Domain configuration report generated: $report_file"
}

# Main function
main() {
    log_info "Starting domain setup for NEXUS Platform..."

    check_prerequisites
    get_load_balancer_dns
    verify_dns_resolution
    test_https_connectivity
    test_ssl_certificate
    test_all_endpoints
    check_application_health
    generate_domain_report

    log_success "Domain setup completed successfully!"

    echo ""
    echo "=========================================="
    echo "Domain Setup Summary"
    echo "=========================================="
    echo "Domain: $DOMAIN_NAME"
    echo "ALB DNS: $ALB_DNS_NAME"
    echo "Namespace: $NAMESPACE"
    echo "Main URL: https://$DOMAIN_NAME"
    echo "API URL: https://api.$DOMAIN_NAME"
    echo "Monitoring: https://monitoring.$DOMAIN_NAME"
    echo "Grafana: https://grafana.$DOMAIN_NAME"
    echo "=========================================="
}

# Run main function
main "$@"
