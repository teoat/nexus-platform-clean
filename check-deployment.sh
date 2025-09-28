#!/bin/bash

# NEXUS Deployment Status Checker
# Checks both Docker and Kubernetes deployments

set -e

echo "🔍 NEXUS DEPLOYMENT STATUS CHECKER"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check Docker deployment
check_docker() {
    echo ""
    print_info "🐳 DOCKER DEPLOYMENT STATUS"
    echo "----------------------------"

    if command -v docker &> /dev/null; then
        if command -v docker-compose &> /dev/null; then
            # Check if containers are running
            if docker-compose ps | grep -q "Up"; then
                print_status "Docker Compose services are running"
                echo ""
                print_info "Running containers:"
                docker-compose ps
                echo ""
                print_info "Resource usage:"
                docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
            else
                print_warning "No Docker Compose services running"
            fi
        else
            print_error "Docker Compose not installed"
        fi
    else
        print_error "Docker not installed"
    fi
}

# Check Kubernetes deployment
check_kubernetes() {
    echo ""
    print_info "☸️  KUBERNETES DEPLOYMENT STATUS"
    echo "----------------------------------"

    if command -v kubectl &> /dev/null; then
        if kubectl cluster-info &> /dev/null; then
            print_status "Connected to Kubernetes cluster"
            echo ""

            # Check if nexus namespace exists
            if kubectl get namespace nexus &> /dev/null; then
                print_status "NEXUS namespace exists"
                echo ""
                print_info "Pods status:"
                kubectl get pods -n nexus
                echo ""
                print_info "Services:"
                kubectl get services -n nexus
                echo ""
                print_info "Deployments:"
                kubectl get deployments -n nexus
                echo ""
                print_info "HPA status:"
                kubectl get hpa -n nexus 2>/dev/null || print_warning "HPA not configured"
                echo ""
                print_info "Resource usage:"
                kubectl top pods -n nexus 2>/dev/null || print_warning "Metrics server not available"
            else
                print_warning "NEXUS namespace not found"
            fi
        else
            print_error "Cannot connect to Kubernetes cluster"
        fi
    else
        print_error "kubectl not installed"
    fi
}

# Check system resources
check_system() {
    echo ""
    print_info "💻 SYSTEM RESOURCES"
    echo "-------------------"

    # CPU usage
    if command -v top &> /dev/null; then
        cpu_usage=$(top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')
        print_info "CPU Usage: ${cpu_usage}%"
    fi

    # Memory usage
    if command -v vm_stat &> /dev/null; then
        # macOS memory check
        memory_info=$(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//')
        print_info "Memory: Check system preferences for detailed info"
    fi

    # Disk usage
    if command -v df &> /dev/null; then
        disk_usage=$(df -h / | tail -1 | awk '{print $5}')
        print_info "Disk Usage: ${disk_usage}"
    fi
}

# Check network connectivity
check_network() {
    echo ""
    print_info "🌐 NETWORK CONNECTIVITY"
    echo "------------------------"

    # Check if ports are accessible
    ports=(8766 3000 5000 8080)
    for port in "${ports[@]}"; do
        if nc -z localhost $port 2>/dev/null; then
            print_status "Port $port is accessible"
        else
            print_warning "Port $port is not accessible"
        fi
    done

    # Check external connectivity
    if ping -c 1 google.com &> /dev/null; then
        print_status "External connectivity: OK"
    else
        print_warning "External connectivity: Limited"
    fi
}

# Check application health
check_application() {
    echo ""
    print_info "🏥 APPLICATION HEALTH"
    echo "----------------------"

    # Check if phase system is responding
    if curl -s http://localhost:8766/health &> /dev/null; then
        print_status "Phase System: Healthy"
    else
        print_warning "Phase System: Not responding"
    fi

    # Check if agents are running
    if ps aux | grep -E "agent_[1-4]" | grep -v grep &> /dev/null; then
        agent_count=$(ps aux | grep -E "agent_[1-4]" | grep -v grep | wc -l)
        print_status "Agents: $agent_count running"
    else
        print_warning "Agents: Not running"
    fi

    # Check if monitoring is running
    if ps aux | grep -E "(monitoring|quality)" | grep -v grep &> /dev/null; then
        print_status "Monitoring: Running"
    else
        print_warning "Monitoring: Not running"
    fi
}

# Generate summary report
generate_summary() {
    echo ""
    print_info "📊 DEPLOYMENT SUMMARY"
    echo "======================"

    # Docker status
    if docker-compose ps | grep -q "Up" 2>/dev/null; then
        docker_status="✅ Running"
    else
        docker_status="❌ Stopped"
    fi

    # Kubernetes status
    if kubectl get pods -n nexus &> /dev/null; then
        k8s_pods=$(kubectl get pods -n nexus --no-headers | wc -l)
        k8s_running=$(kubectl get pods -n nexus --no-headers | grep "Running" | wc -l)
        k8s_status="✅ $k8s_running/$k8s_pods pods running"
    else
        k8s_status="❌ Not deployed"
    fi

    # Application status
    if curl -s http://localhost:8766/health &> /dev/null; then
        app_status="✅ Healthy"
    else
        app_status="❌ Unhealthy"
    fi

    echo "Docker:     $docker_status"
    echo "Kubernetes: $k8s_status"
    echo "Application: $app_status"

    echo ""
    print_info "RECOMMENDATIONS:"
    if [[ "$docker_status" == *"Running"* ]]; then
        echo "• Docker deployment is active"
    fi
    if [[ "$k8s_status" == *"Running"* ]]; then
        echo "• Kubernetes deployment is active"
    fi
    if [[ "$app_status" == *"Healthy"* ]]; then
        echo "• Application is responding correctly"
    else
        echo "• Check application logs for issues"
        echo "• Verify all services are running"
        echo "• Check network connectivity"
    fi
}

# Main execution
main() {
    check_docker
    check_kubernetes
    check_system
    check_network
    check_application
    generate_summary

    echo ""
    print_info "🔧 USEFUL COMMANDS:"
    echo "• View Docker logs: docker-compose logs -f"
    echo "• View K8s logs: kubectl logs -f deployment/nexus-phase-system -n nexus"
    echo "• Restart Docker: docker-compose restart"
    echo "• Restart K8s: kubectl rollout restart deployment/nexus-phase-system -n nexus"
    echo "• Port forward: kubectl port-forward service/nexus-phase-system 8766:8766 -n nexus"
    echo "• Scale agents: kubectl scale deployment nexus-agents --replicas=8 -n nexus"
}

# Run main function
main
