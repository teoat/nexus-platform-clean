#!/bin/bash

# NEXUS Docker Security Scanning Script
# This script performs security scanning on Docker images

set -e

# Configuration
DOCKER_IMAGES=(
    "nexus-backend:latest"
    "nexus-frontend:latest"
    "nexus-postgres:latest"
    "nexus-redis:latest"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to scan a single image
scan_image() {
    local image=$1
    print_status "Scanning image: $image"

    # Check if image exists
    if ! docker image inspect "$image" > /dev/null 2>&1; then
        print_error "Image $image not found"
        return 1
    fi

    # Use Trivy for vulnerability scanning
    if command -v trivy &> /dev/null; then
        print_status "Running Trivy scan on $image"
        trivy image --format json --output "security-reports/trivy-$(echo $image | tr '/' '-').json" "$image"
    else
        print_warning "Trivy not installed. Skipping vulnerability scan."
    fi

    # Use Docker scan (if available)
    if command -v docker &> /dev/null && docker scan --help &> /dev/null; then
        print_status "Running Docker scan on $image"
        docker scan "$image" > "security-reports/docker-scan-$(echo $image | tr '/' '-').txt" 2>&1 || true
    fi

    # Use Snyk (if available)
    if command -v snyk &> /dev/null; then
        print_status "Running Snyk scan on $image"
        snyk container test "$image" --json > "security-reports/snyk-$(echo $image | tr '/' '-').json" 2>&1 || true
    fi

    print_status "Scan completed for $image"
}

# Function to generate summary report
generate_report() {
    print_status "Generating security report summary"

    cat > security-reports/summary.md << EOF
# Docker Security Scan Summary

## Scan Date
$(date)

## Images Scanned
$(printf "- %s\n" "${DOCKER_IMAGES[@]}")

## Summary
- Total images scanned: ${#DOCKER_IMAGES[@]}
- Security reports generated in: security-reports/

## Recommendations
1. Review all generated reports for vulnerabilities
2. Update base images to latest secure versions
3. Apply security patches to application dependencies
4. Use multi-stage builds to minimize attack surface
5. Implement image signing and verification

## Next Steps
- Address high and critical vulnerabilities
- Update security policies
- Implement automated scanning in CI/CD pipeline
EOF

    print_status "Summary report generated: security-reports/summary.md"
}

# Main execution
main() {
    print_status "Starting Docker security scan"

    # Create reports directory
    mkdir -p security-reports

    # Scan all images
    for image in "${DOCKER_IMAGES[@]}"; do
        scan_image "$image"
    done

    # Generate summary report
    generate_report

    print_status "Docker security scan completed successfully"
    print_status "Reports available in: security-reports/"
}

# Check if running in Docker environment
if [ -f /.dockerenv ]; then
    print_warning "Running inside Docker container"
fi

# Run main function
main "$@"
