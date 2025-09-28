#!/bin/bash
# NEXUS Platform - Automated Security Scan Runner
# Runs comprehensive security scans and generates reports

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
REPORTS_DIR="$PROJECT_ROOT/reports/security"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create directories
mkdir -p "$LOG_DIR"
mkdir -p "$REPORTS_DIR"

# Logging
LOG_FILE="$LOG_DIR/security_scan_$TIMESTAMP.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  NEXUS Platform - Security Scan Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo "Started at: $(date)"
echo "Log file: $LOG_FILE"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to run a security scan
run_scan() {
    local scan_name="$1"
    local scan_command="$2"
    local timeout="${3:-300}"

    echo -e "${YELLOW}Running $scan_name...${NC}"

    if eval "timeout $timeout $scan_command"; then
        echo -e "${GREEN}✓ $scan_name completed successfully${NC}"
        return 0
    else
        echo -e "${RED}✗ $scan_name failed${NC}"
        return 1
    fi
}

# Pre-scan setup
echo "Setting up security scan environment..."

# Ensure Python virtual environment is activated if it exists
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
    echo "Activated Python virtual environment"
fi

# Check for required tools
echo "Checking for required security scanning tools..."

MISSING_TOOLS=()
REQUIRED_TOOLS=("python3" "docker" "curl")

for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command_exists "$tool"; then
        MISSING_TOOLS+=("$tool")
    fi
done

# Optional tools (warnings if missing)
OPTIONAL_TOOLS=("trivy" "bandit" "semgrep" "safety" "pip-audit")

for tool in "${OPTIONAL_TOOLS[@]}"; do
    if ! command_exists "$tool"; then
        echo -e "${YELLOW}Warning: $tool not found. Some scans may be skipped.${NC}"
    fi
done

if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    echo -e "${RED}Error: Missing required tools: ${MISSING_TOOLS[*]}${NC}"
    exit 1
fi

echo -e "${GREEN}All required tools are available${NC}"
echo ""

# Run security scans
FAILED_SCANS=()
SUCCESS_COUNT=0
TOTAL_SCANS=0

# 1. Container Vulnerability Scanning
if command_exists "trivy"; then
    TOTAL_SCANS=$((TOTAL_SCANS + 1))
    if run_scan "Container Vulnerability Scan" "trivy image --format json --output $REPORTS_DIR/trivy_scan_$TIMESTAMP.json nexus-backend-staging:latest 2>/dev/null || trivy image --format json --output $REPORTS_DIR/trivy_scan_$TIMESTAMP.json python:3.11-slim"; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        FAILED_SCANS+=("Container Vulnerability Scan")
    fi
else
    echo -e "${YELLOW}Skipping container scan: trivy not available${NC}"
fi

# 2. Python Dependency Scanning
TOTAL_SCANS=$((TOTAL_SCANS + 1))
if run_scan "Python Dependency Scan" "python3 scripts/automated_security_scan.py --scan-type dependency"; then
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
else
    FAILED_SCANS+=("Python Dependency Scan")
fi

# 3. Code Security Scanning (SAST)
if command_exists "bandit"; then
    TOTAL_SCANS=$((TOTAL_SCANS + 1))
    if run_scan "Code Security Scan (Bandit)" "bandit -r nexus_backend/ nexus_backend/ -f json -o $REPORTS_DIR/bandit_scan_$TIMESTAMP.json"; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        FAILED_SCANS+=("Code Security Scan (Bandit)")
    fi
fi

if command_exists "semgrep"; then
    TOTAL_SCANS=$((TOTAL_SCANS + 1))
    if run_scan "Code Security Scan (Semgrep)" "semgrep --config auto --json --output $REPORTS_DIR/semgrep_scan_$TIMESTAMP.json nexus_backend/ nexus_backend/"; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        FAILED_SCANS+=("Code Security Scan (Semgrep)")
    fi
fi

# 4. Compliance Scanning
TOTAL_SCANS=$((TOTAL_SCANS + 1))
if run_scan "Compliance Scan" "python3 scripts/automated_security_scan.py --scan-type compliance"; then
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
else
    FAILED_SCANS+=("Compliance Scan")
fi

# 5. Infrastructure Security Scan
TOTAL_SCANS=$((TOTAL_SCANS + 1))
if run_scan "Infrastructure Security Scan" "python3 scripts/automated_security_scan.py --scan-type infrastructure"; then
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
else
    FAILED_SCANS+=("Infrastructure Security Scan")
fi

# 6. Comprehensive Security Scan
TOTAL_SCANS=$((TOTAL_SCANS + 1))
if run_scan "Comprehensive Security Scan" "python3 scripts/automated_security_scan.py"; then
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
else
    FAILED_SCANS+=("Comprehensive Security Scan")
fi

# Generate summary report
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}           SCAN SUMMARY${NC}"
echo -e "${BLUE}========================================${NC}"
echo "Total scans: $TOTAL_SCANS"
echo "Successful: $SUCCESS_COUNT"
echo "Failed: $(($TOTAL_SCANS - $SUCCESS_COUNT))"
echo ""

if [ ${#FAILED_SCANS[@]} -gt 0 ]; then
    echo -e "${RED}Failed scans:${NC}"
    for scan in "${FAILED_SCANS[@]}"; do
        echo -e "${RED}  - $scan${NC}"
    done
    echo ""
fi

# Check for critical vulnerabilities
CRITICAL_VULNS=$(find "$REPORTS_DIR" -name "*$TIMESTAMP*.json" -exec grep -l '"severity": "CRITICAL"' {} \; 2>/dev/null | wc -l)
HIGH_VULNS=$(find "$REPORTS_DIR" -name "*$TIMESTAMP*.json" -exec grep -l '"severity": "HIGH"' {} \; 2>/dev/null | wc -l)

echo "Critical vulnerabilities found: $CRITICAL_VULNS"
echo "High severity vulnerabilities found: $HIGH_VULNS"
echo ""

# Determine overall status
if [ "$CRITICAL_VULNS" -gt 0 ]; then
    echo -e "${RED}SECURITY SCAN FAILED: Critical vulnerabilities detected!${NC}"
    EXIT_CODE=1
elif [ ${#FAILED_SCANS[@]} -gt 0 ]; then
    echo -e "${YELLOW}SECURITY SCAN COMPLETED WITH WARNINGS: Some scans failed${NC}"
    EXIT_CODE=1
else
    echo -e "${GREEN}SECURITY SCAN PASSED: No critical issues found${NC}"
    EXIT_CODE=0
fi

echo ""
echo "Reports saved to: $REPORTS_DIR"
echo "Log file: $LOG_FILE"
echo "Completed at: $(date)"

# Cleanup old reports (keep last 10)
echo ""
echo "Cleaning up old reports..."
find "$REPORTS_DIR" -name "security_scan_report_*.json" -type f | head -n -10 | xargs -r rm -f
find "$REPORTS_DIR" -name "*_scan_*.json" -type f | head -n -50 | xargs -r rm -f

echo -e "${BLUE}========================================${NC}"

exit $EXIT_CODE
