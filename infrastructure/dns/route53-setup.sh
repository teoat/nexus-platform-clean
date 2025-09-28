#!/bin/bash
# NEXUS Platform - Route53 DNS Configuration
# Automated DNS setup for production deployment

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN_NAME="${DOMAIN_NAME:-nexusplatform.com}"
HOSTED_ZONE_ID="${HOSTED_ZONE_ID:-}"
ALB_DNS_NAME="${ALB_DNS_NAME:-}"
AWS_REGION="${AWS_REGION:-us-east-1}"

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

    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed"
        exit 1
    fi

    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS CLI is not configured"
        exit 1
    fi

    if [[ -z "$HOSTED_ZONE_ID" ]]; then
        log_error "HOSTED_ZONE_ID environment variable is required"
        exit 1
    fi

    if [[ -z "$ALB_DNS_NAME" ]]; then
        log_error "ALB_DNS_NAME environment variable is required"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Create or get hosted zone
setup_hosted_zone() {
    log_info "Setting up Route53 hosted zone for $DOMAIN_NAME..."

    # Check if hosted zone exists
    if [[ -n "$HOSTED_ZONE_ID" ]]; then
        log_info "Using existing hosted zone: $HOSTED_ZONE_ID"
        return
    fi

    # Create hosted zone
    local response=$(aws route53 create-hosted-zone \
        --name "$DOMAIN_NAME" \
        --caller-reference "nexus-platform-$(date +%s)" \
        --hosted-zone-config Comment="NEXUS Platform production zone")

    HOSTED_ZONE_ID=$(echo "$response" | jq -r '.HostedZone.Id' | sed 's|/hostedzone/||')

    log_success "Created hosted zone: $HOSTED_ZONE_ID"
    echo "HOSTED_ZONE_ID=$HOSTED_ZONE_ID" >> .env
}

# Get ALB DNS name
get_alb_dns_name() {
    log_info "Getting Application Load Balancer DNS name..."

    if [[ -z "$ALB_DNS_NAME" ]]; then
        ALB_DNS_NAME=$(aws elbv2 describe-load-balancers \
            --query 'LoadBalancers[?contains(LoadBalancerName, `nexus-platform`)].DNSName' \
            --output text)

        if [[ -z "$ALB_DNS_NAME" ]]; then
            log_error "Could not find ALB DNS name"
            exit 1
        fi
    fi

    log_success "ALB DNS name: $ALB_DNS_NAME"
    echo "ALB_DNS_NAME=$ALB_DNS_NAME" >> .env
}

# Create DNS records
create_dns_records() {
    log_info "Creating DNS records..."

    # Create A record for main domain
    local change_batch=$(cat << EOF
{
    "Changes": [
        {
            "Action": "UPSERT",
            "ResourceRecordSet": {
                "Name": "$DOMAIN_NAME",
                "Type": "A",
                "AliasTarget": {
                    "DNSName": "$ALB_DNS_NAME",
                    "EvaluateTargetHealth": true,
                    "HostedZoneId": "Z35SXDOTRQ7X7K"
                }
            }
        },
        {
            "Action": "UPSERT",
            "ResourceRecordSet": {
                "Name": "www.$DOMAIN_NAME",
                "Type": "A",
                "AliasTarget": {
                    "DNSName": "$ALB_DNS_NAME",
                    "EvaluateTargetHealth": true,
                    "HostedZoneId": "Z35SXDOTRQ7X7K"
                }
            }
        },
        {
            "Action": "UPSERT",
            "ResourceRecordSet": {
                "Name": "api.$DOMAIN_NAME",
                "Type": "A",
                "AliasTarget": {
                    "DNSName": "$ALB_DNS_NAME",
                    "EvaluateTargetHealth": true,
                    "HostedZoneId": "Z35SXDOTRQ7X7K"
                }
            }
        }
    ]
}
EOF
)

    # Apply DNS changes
    local change_id=$(aws route53 change-resource-record-sets \
        --hosted-zone-id "$HOSTED_ZONE_ID" \
        --change-batch "$change_batch" \
        --query 'ChangeInfo.Id' \
        --output text)

    log_info "DNS changes submitted. Change ID: $change_id"

    # Wait for changes to propagate
    log_info "Waiting for DNS changes to propagate..."
    aws route53 wait resource-record-sets-changed --id "$change_id"

    log_success "DNS records created successfully"
}

# Create CNAME records for subdomains
create_subdomain_records() {
    log_info "Creating subdomain records..."

    local subdomains=("monitoring" "grafana" "prometheus" "admin")

    for subdomain in "${subdomains[@]}"; do
        local change_batch=$(cat << EOF
{
    "Changes": [
        {
            "Action": "UPSERT",
            "ResourceRecordSet": {
                "Name": "$subdomain.$DOMAIN_NAME",
                "Type": "CNAME",
                "TTL": 300,
                "ResourceRecords": [
                    {
                        "Value": "$ALB_DNS_NAME"
                    }
                ]
            }
        }
    ]
}
EOF
)

        aws route53 change-resource-record-sets \
            --hosted-zone-id "$HOSTED_ZONE_ID" \
            --change-batch "$change_batch" > /dev/null

        log_info "Created CNAME record for $subdomain.$DOMAIN_NAME"
    done

    log_success "Subdomain records created"
}

# Create MX records for email
create_mx_records() {
    log_info "Creating MX records for email..."

    local change_batch=$(cat << EOF
{
    "Changes": [
        {
            "Action": "UPSERT",
            "ResourceRecordSet": {
                "Name": "$DOMAIN_NAME",
                "Type": "MX",
                "TTL": 300,
                "ResourceRecords": [
                    {
                        "Value": "10 mail.$DOMAIN_NAME"
                    }
                ]
            }
        }
    ]
}
EOF
)

    aws route53 change-resource-record-sets \
        --hosted-zone-id "$HOSTED_ZONE_ID" \
        --change-batch "$change_batch" > /dev/null

    log_success "MX records created"
}

# Create TXT records for verification
create_txt_records() {
    log_info "Creating TXT records for verification..."

    # SPF record
    local spf_record=$(cat << EOF
{
    "Changes": [
        {
            "Action": "UPSERT",
            "ResourceRecordSet": {
                "Name": "$DOMAIN_NAME",
                "Type": "TXT",
                "TTL": 300,
                "ResourceRecords": [
                    {
                        "Value": "\"v=spf1 include:_spf.google.com ~all\""
                    }
                ]
            }
        }
    ]
}
EOF
)

    aws route53 change-resource-record-sets \
        --hosted-zone-id "$HOSTED_ZONE_ID" \
        --change-batch "$spf_record" > /dev/null

    # DKIM record (placeholder)
    local dkim_record=$(cat << EOF
{
    "Changes": [
        {
            "Action": "UPSERT",
            "ResourceRecordSet": {
                "Name": "default._domainkey.$DOMAIN_NAME",
                "Type": "TXT",
                "TTL": 300,
                "ResourceRecords": [
                    {
                        "Value": "\"v=DKIM1; k=rsa; p=YOUR_DKIM_PUBLIC_KEY\""
                    }
                ]
            }
        }
    ]
}
EOF
)

    aws route53 change-resource-record-sets \
        --hosted-zone-id "$HOSTED_ZONE_ID" \
        --change-batch "$dkim_record" > /dev/null

    log_success "TXT records created"
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

# Generate DNS report
generate_dns_report() {
    log_info "Generating DNS configuration report..."

    local report_file="dns-configuration-report-$(date +%Y%m%d_%H%M%S).json"

    cat > "$report_file" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "domain_name": "$DOMAIN_NAME",
    "hosted_zone_id": "$HOSTED_ZONE_ID",
    "alb_dns_name": "$ALB_DNS_NAME",
    "records_created": [
        {
            "name": "$DOMAIN_NAME",
            "type": "A",
            "target": "$ALB_DNS_NAME"
        },
        {
            "name": "www.$DOMAIN_NAME",
            "type": "A",
            "target": "$ALB_DNS_NAME"
        },
        {
            "name": "api.$DOMAIN_NAME",
            "type": "A",
            "target": "$ALB_DNS_NAME"
        },
        {
            "name": "monitoring.$DOMAIN_NAME",
            "type": "CNAME",
            "target": "$ALB_DNS_NAME"
        },
        {
            "name": "grafana.$DOMAIN_NAME",
            "type": "CNAME",
            "target": "$ALB_DNS_NAME"
        },
        {
            "name": "prometheus.$DOMAIN_NAME",
            "type": "CNAME",
            "target": "$ALB_DNS_NAME"
        },
        {
            "name": "admin.$DOMAIN_NAME",
            "type": "CNAME",
            "target": "$ALB_DNS_NAME"
        }
    ],
    "status": "completed"
}
EOF

    log_success "DNS configuration report generated: $report_file"
}

# Main function
main() {
    log_info "Starting DNS configuration for NEXUS Platform..."

    check_prerequisites
    setup_hosted_zone
    get_alb_dns_name
    create_dns_records
    create_subdomain_records
    create_mx_records
    create_txt_records
    verify_dns_resolution
    test_https_connectivity
    generate_dns_report

    log_success "DNS configuration completed successfully!"

    echo ""
    echo "=========================================="
    echo "DNS Configuration Summary"
    echo "=========================================="
    echo "Domain: $DOMAIN_NAME"
    echo "Hosted Zone ID: $HOSTED_ZONE_ID"
    echo "ALB DNS Name: $ALB_DNS_NAME"
    echo "Main URL: https://$DOMAIN_NAME"
    echo "API URL: https://api.$DOMAIN_NAME"
    echo "Monitoring: https://monitoring.$DOMAIN_NAME"
    echo "Grafana: https://grafana.$DOMAIN_NAME"
    echo "=========================================="
}

# Run main function
main "$@"
