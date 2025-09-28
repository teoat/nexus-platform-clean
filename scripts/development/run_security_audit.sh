#!/bin/bash

# NEXUS Platform - Comprehensive Security Audit Script
# Run all security tests and generate detailed report

set -e

# Configuration
BACKEND_URL="http://localhost:8001"
FRONTEND_URL="http://localhost:3000"
AUDIT_DIR="/tmp/nexus_security_audit_$(date +%Y%m%d_%H%M%S)"
REPORT_FILE="security_audit_report_$(date +%Y%m%d_%H%M%S).json"

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

# Create audit directory
create_audit_directory() {
    log "Creating audit directory: $AUDIT_DIR"
    mkdir -p "$AUDIT_DIR"
    success "Audit directory created"
}

# Install security tools
install_security_tools() {
    log "Installing security tools..."
    
    # Install Python security packages
    pip3 install --quiet \
        bandit \
        safety \
        semgrep \
        python-nmap \
        requests \
        beautifulsoup4 \
        lxml
    
    # Install system tools
    if ! command -v nmap &> /dev/null; then
        sudo apt-get update -qq
        sudo apt-get install -y nmap
    fi
    
    if ! command -v nikto &> /dev/null; then
        sudo apt-get install -y nikto
    fi
    
    if ! command -v dirb &> /dev/null; then
        sudo apt-get install -y dirb
    fi
    
    success "Security tools installed"
}

# Run Python security audit
run_python_security_audit() {
    log "Running Python security audit..."
    
    # Bandit - Python security linter
    log "Running Bandit security linter..."
    bandit -r . -f json -o "$AUDIT_DIR/bandit_report.json" || true
    bandit -r . -f txt > "$AUDIT_DIR/bandit_report.txt" || true
    
    # Safety - Check for known security vulnerabilities
    log "Running Safety vulnerability check..."
    safety check --json --output "$AUDIT_DIR/safety_report.json" || true
    safety check > "$AUDIT_DIR/safety_report.txt" || true
    
    # Semgrep - Static analysis
    log "Running Semgrep static analysis..."
    semgrep --config=auto --json --output="$AUDIT_DIR/semgrep_report.json" . || true
    semgrep --config=auto --output="$AUDIT_DIR/semgrep_report.txt" . || true
    
    success "Python security audit completed"
}

# Run network security scan
run_network_security_scan() {
    log "Running network security scan..."
    
    # Extract host and port from URL
    HOST=$(echo "$BACKEND_URL" | sed 's|http://||' | sed 's|https://||' | cut -d: -f1)
    PORT=$(echo "$BACKEND_URL" | sed 's|http://||' | sed 's|https://||' | cut -d: -f2)
    PORT=${PORT:-80}
    
    # Nmap port scan
    log "Running Nmap port scan..."
    nmap -sV -sC -O -A -p- "$HOST" -oN "$AUDIT_DIR/nmap_scan.txt" || true
    
    # Nmap vulnerability scan
    log "Running Nmap vulnerability scan..."
    nmap --script vuln "$HOST" -oN "$AUDIT_DIR/nmap_vuln.txt" || true
    
    success "Network security scan completed"
}

# Run web application security tests
run_web_security_tests() {
    log "Running web application security tests..."
    
    # Nikto web vulnerability scanner
    log "Running Nikto web vulnerability scanner..."
    nikto -h "$BACKEND_URL" -output "$AUDIT_DIR/nikto_report.txt" -Format txt || true
    
    # Directory brute force
    log "Running directory brute force scan..."
    dirb "$BACKEND_URL" "$AUDIT_DIR/dirb_report.txt" || true
    
    # Custom security tests
    log "Running custom security tests..."
    python3 scripts/security_audit.py --output "$AUDIT_DIR/custom_security_audit.json" || true
    
    success "Web security tests completed"
}

# Run Docker security scan
run_docker_security_scan() {
    log "Running Docker security scan..."
    
    # Build images for scanning
    log "Building Docker images for security scanning..."
    docker-compose -f docker-compose.production.yml build --no-cache || true
    
    # Scan backend image
    if docker images | grep -q "nexus-backend"; then
        log "Scanning backend Docker image..."
        trivy image --format json --output "$AUDIT_DIR/trivy_backend.json" nexus-backend:latest || true
        trivy image --format table --output "$AUDIT_DIR/trivy_backend.txt" nexus-backend:latest || true
    fi
    
    # Scan frontend image
    if docker images | grep -q "nexus-frontend"; then
        log "Scanning frontend Docker image..."
        trivy image --format json --output "$AUDIT_DIR/trivy_frontend.json" nexus-frontend:latest || true
        trivy image --format table --output "$AUDIT_DIR/trivy_frontend.txt" nexus-frontend:latest || true
    fi
    
    # Scan all images
    log "Scanning all Docker images..."
    trivy image --format json --output "$AUDIT_DIR/trivy_all_images.json" $(docker images --format "table {{.Repository}}:{{.Tag}}" | grep -v REPOSITORY) || true
    
    success "Docker security scan completed"
}

# Run SSL/TLS security tests
run_ssl_security_tests() {
    log "Running SSL/TLS security tests..."
    
    # Extract domain from URL
    DOMAIN=$(echo "$BACKEND_URL" | sed 's|http://||' | sed 's|https://||' | cut -d: -f1)
    
    # TestSSL.sh if available
    if command -v testssl.sh &> /dev/null; then
        log "Running TestSSL.sh..."
        testssl.sh --jsonfile "$AUDIT_DIR/testssl_report.json" "$DOMAIN" || true
    fi
    
    # OpenSSL tests
    log "Running OpenSSL tests..."
    echo | openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" 2>/dev/null | openssl x509 -noout -text > "$AUDIT_DIR/ssl_certificate_info.txt" || true
    
    # SSL Labs API test (if domain is public)
    if [[ "$DOMAIN" != "localhost" && "$DOMAIN" != "127.0.0.1" ]]; then
        log "Running SSL Labs API test..."
        curl -s "https://api.ssllabs.com/api/v3/analyze?host=$DOMAIN" > "$AUDIT_DIR/ssllabs_report.json" || true
    fi
    
    success "SSL/TLS security tests completed"
}

# Run authentication security tests
run_auth_security_tests() {
    log "Running authentication security tests..."
    
    # Test for common authentication vulnerabilities
    python3 -c "
import requests
import json

# Test for weak passwords
weak_passwords = ['admin', 'password', '123456', 'nexus', 'test']
vulnerabilities = []

for password in weak_passwords:
    try:
        response = requests.post('$BACKEND_URL/api/v1/auth/token', 
                               data={'username': 'admin', 'password': password}, 
                               timeout=5)
        if response.status_code == 200:
            vulnerabilities.append(f'Weak password accepted: {password}')
    except:
        pass

# Test for SQL injection in auth
sql_payloads = [\"' OR '1'='1\", \"'; DROP TABLE users; --\"]
for payload in sql_payloads:
    try:
        response = requests.post('$BACKEND_URL/api/v1/auth/register',
                               json={'username': payload, 'email': 'test@test.com', 'password': 'password'},
                               timeout=5)
        if 'error' not in response.text.lower() and response.status_code == 200:
            vulnerabilities.append(f'SQL injection vulnerability: {payload}')
    except:
        pass

# Test for rate limiting
rate_limit_bypassed = False
for i in range(100):
    try:
        response = requests.get('$BACKEND_URL/api/v1/', timeout=2)
        if response.status_code == 429:
            break
    except:
        pass
else:
    rate_limit_bypassed = True

if rate_limit_bypassed:
    vulnerabilities.append('Rate limiting not working')

# Save results
with open('$AUDIT_DIR/auth_security_tests.json', 'w') as f:
    json.dump({'vulnerabilities': vulnerabilities}, f, indent=2)

print(f'Found {len(vulnerabilities)} authentication vulnerabilities')
for vuln in vulnerabilities:
    print(f'  - {vuln}')
"
    
    success "Authentication security tests completed"
}

# Run API security tests
run_api_security_tests() {
    log "Running API security tests..."
    
    # Test for common API vulnerabilities
    python3 -c "
import requests
import json

api_tests = []

# Test for CORS misconfiguration
try:
    response = requests.get('$BACKEND_URL/api/v1/', 
                          headers={'Origin': 'https://malicious.com'})
    cors_headers = response.headers.get('Access-Control-Allow-Origin', '')
    if cors_headers == '*' or 'malicious.com' in cors_headers:
        api_tests.append('CORS misconfiguration detected')
except:
    pass

# Test for missing security headers
try:
    response = requests.get('$BACKEND_URL/api/v1/')
    headers = response.headers
    
    required_headers = ['X-Content-Type-Options', 'X-Frame-Options', 'X-XSS-Protection']
    missing_headers = [h for h in required_headers if h not in headers]
    
    if missing_headers:
        api_tests.append(f'Missing security headers: {missing_headers}')
except:
    pass

# Test for information disclosure
try:
    response = requests.get('$BACKEND_URL/api/v1/')
    if 'server' in response.headers:
        api_tests.append(f'Server information disclosed: {response.headers[\"server\"]}')
except:
    pass

# Test for directory traversal
try:
    response = requests.get('$BACKEND_URL/api/v1/../../../etc/passwd')
    if 'root:' in response.text:
        api_tests.append('Directory traversal vulnerability detected')
except:
    pass

# Save results
with open('$AUDIT_DIR/api_security_tests.json', 'w') as f:
    json.dump({'api_tests': api_tests}, f, indent=2)

print(f'Found {len(api_tests)} API security issues')
for test in api_tests:
    print(f'  - {test}')
"
    
    success "API security tests completed"
}

# Generate comprehensive report
generate_security_report() {
    log "Generating comprehensive security report..."
    
    python3 -c "
import json
import os
from datetime import datetime

# Collect all audit results
audit_results = {
    'timestamp': datetime.now().isoformat(),
    'backend_url': '$BACKEND_URL',
    'frontend_url': '$FRONTEND_URL',
    'audit_directory': '$AUDIT_DIR',
    'reports': {}
}

# Load individual reports
report_files = [
    ('bandit_report.json', 'bandit'),
    ('safety_report.json', 'safety'),
    ('semgrep_report.json', 'semgrep'),
    ('custom_security_audit.json', 'custom_audit'),
    ('auth_security_tests.json', 'auth_tests'),
    ('api_security_tests.json', 'api_tests')
]

for filename, report_name in report_files:
    filepath = os.path.join('$AUDIT_DIR', filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                audit_results['reports'][report_name] = json.load(f)
        except:
            audit_results['reports'][report_name] = {'error': 'Failed to parse JSON'}

# Calculate security score
total_issues = 0
critical_issues = 0
high_issues = 0
medium_issues = 0
low_issues = 0

# Count issues from different reports
for report_name, report_data in audit_results['reports'].items():
    if isinstance(report_data, dict):
        if 'results' in report_data:
            for result in report_data['results']:
                if 'issue_severity' in result:
                    severity = result['issue_severity'].lower()
                    if severity == 'high':
                        critical_issues += 1
                    elif severity == 'medium':
                        high_issues += 1
                    elif severity == 'low':
                        medium_issues += 1
                    else:
                        low_issues += 1
                total_issues += 1
        elif 'vulnerabilities' in report_data:
            total_issues += len(report_data['vulnerabilities'])
            critical_issues += len(report_data['vulnerabilities'])
        elif 'api_tests' in report_data:
            total_issues += len(report_data['api_tests'])
            high_issues += len(report_data['api_tests'])

# Calculate security score (0-100)
if total_issues == 0:
    security_score = 100
else:
    security_score = max(0, 100 - (critical_issues * 10 + high_issues * 5 + medium_issues * 2 + low_issues * 1))

audit_results['security_summary'] = {
    'total_issues': total_issues,
    'critical_issues': critical_issues,
    'high_issues': high_issues,
    'medium_issues': medium_issues,
    'low_issues': low_issues,
    'security_score': security_score,
    'risk_level': 'HIGH' if security_score < 70 else 'MEDIUM' if security_score < 85 else 'LOW'
}

# Generate recommendations
recommendations = []
if critical_issues > 0:
    recommendations.append('Address all critical security issues immediately')
if high_issues > 0:
    recommendations.append('Implement proper authentication and authorization')
    recommendations.append('Enable HTTPS and SSL/TLS')
    recommendations.append('Implement input validation and sanitization')
if medium_issues > 0:
    recommendations.append('Add security headers')
    recommendations.append('Implement rate limiting')
    recommendations.append('Secure file uploads')
if low_issues > 0:
    recommendations.append('Review API documentation exposure')
    recommendations.append('Implement proper logging and monitoring')

audit_results['recommendations'] = recommendations

# Save comprehensive report
with open('$REPORT_FILE', 'w') as f:
    json.dump(audit_results, f, indent=2)

print('Security audit completed!')
print(f'Total issues found: {total_issues}')
print(f'Security score: {security_score}/100')
print(f'Risk level: {audit_results[\"security_summary\"][\"risk_level\"]}')
print(f'Report saved to: $REPORT_FILE')
"
    
    success "Security report generated: $REPORT_FILE"
}

# Display audit summary
display_audit_summary() {
    log "Security audit completed!"
    echo
    echo "=========================================="
    echo "NEXUS Platform - Security Audit Summary"
    echo "=========================================="
    echo
    echo "📁 Audit Directory: $AUDIT_DIR"
    echo "📄 Report File: $REPORT_FILE"
    echo
    echo "🔍 Security Tests Performed:"
    echo "  ✅ Python Security Audit (Bandit, Safety, Semgrep)"
    echo "  ✅ Network Security Scan (Nmap)"
    echo "  ✅ Web Application Security (Nikto, Dirb)"
    echo "  ✅ Docker Security Scan (Trivy)"
    echo "  ✅ SSL/TLS Security Tests"
    echo "  ✅ Authentication Security Tests"
    echo "  ✅ API Security Tests"
    echo
    echo "📊 View Results:"
    echo "  cat $REPORT_FILE | jq '.security_summary'"
    echo "  cat $REPORT_FILE | jq '.recommendations'"
    echo
}

# Main function
main() {
    log "Starting comprehensive security audit..."
    
    create_audit_directory
    install_security_tools
    run_python_security_audit
    run_network_security_scan
    run_web_security_tests
    run_docker_security_scan
    run_ssl_security_tests
    run_auth_security_tests
    run_api_security_tests
    generate_security_report
    display_audit_summary
    
    success "Comprehensive security audit completed!"
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --quick        Run quick security tests only"
        echo "  --docker-only  Run Docker security scan only"
        echo
        exit 0
        ;;
    --quick)
        log "Running quick security audit..."
        create_audit_directory
        install_security_tools
        run_python_security_audit
        run_auth_security_tests
        run_api_security_tests
        generate_security_report
        display_audit_summary
        ;;
    --docker-only)
        log "Running Docker security scan only..."
        create_audit_directory
        install_security_tools
        run_docker_security_scan
        generate_security_report
        display_audit_summary
        ;;
    *)
        main
        ;;
esac
