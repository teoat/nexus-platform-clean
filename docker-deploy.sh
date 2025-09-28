#!/bin/bash

# Multi-Environment Docker Deployment Script
# Supports development, staging, and production environments

set -e

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENVIRONMENTS=("dev" "staging" "production")
DEFAULT_ENV="dev"

# Function to print status messages
print_status() {
    local status_type=$1
    local message=$2
    case "$status_type" in
        "INFO") echo -e "${BLUE}ℹ️  $message${NC}" ;;
        "PASS") echo -e "${GREEN}✅ $message${NC}" ;;
        "FAIL") echo -e "${RED}❌ $message${NC}" ;;
        "WARN") echo -e "${YELLOW}⚠️  $message${NC}" ;;
        *) echo "$message" ;;
    esac
}

# Function to show usage
show_usage() {
    echo -e "${PURPLE}NEXUS Platform - Multi-Environment Docker Deployment${NC}"
    echo ""
    echo "Usage: $0 [ENVIRONMENT] [COMMAND]"
    echo ""
    echo "Environments:"
    for env in "${ENVIRONMENTS[@]}"; do
        echo "  - $env"
    done
    echo ""
    echo "Commands:"
    echo "  build     - Build Docker images for the environment"
    echo "  up        - Start services in detached mode"
    echo "  down      - Stop and remove services"
    echo "  restart   - Restart services"
    echo "  logs      - Show logs for all services"
    echo "  status    - Show status of all services"
    echo "  clean     - Clean up containers, networks, and volumes"
    echo "  validate  - Validate configuration"
    echo ""
    echo "Examples:"
    echo "  $0 dev up"
    echo "  $0 staging build"
    echo "  $0 production restart"
    echo "  $0 dev logs"
}

# Function to validate environment
validate_environment() {
    local env=$1
    if [[ ! " ${ENVIRONMENTS[@]} " =~ " ${env} " ]]; then
        print_status "FAIL" "Invalid environment: $env"
        print_status "INFO" "Available environments: ${ENVIRONMENTS[*]}"
        exit 1
    fi
}

# Function to get compose file and env file
get_files() {
    local env=$1
    local compose_file="docker-compose.${env}.yml"
    local env_file="env.${env}"
    
    if [ ! -f "$compose_file" ]; then
        print_status "FAIL" "Docker Compose file not found: $compose_file"
        exit 1
    fi
    
    if [ ! -f "$env_file" ]; then
        print_status "WARN" "Environment file not found: $env_file, using defaults"
        env_file=""
    fi
    
    echo "$compose_file $env_file"
}

# Function to build images
build_images() {
    local env=$1
    local files=($(get_files $env))
    local compose_file=${files[0]}
    local env_file=${files[1]}
    
    print_status "INFO" "Building images for $env environment..."
    
    local cmd="docker-compose -f $compose_file"
    if [ -n "$env_file" ]; then
        cmd="$cmd --env-file $env_file"
    fi
    cmd="$cmd build --no-cache"
    
    if eval $cmd; then
        print_status "PASS" "Images built successfully for $env"
    else
        print_status "FAIL" "Failed to build images for $env"
        exit 1
    fi
}

# Function to start services
start_services() {
    local env=$1
    local files=($(get_files $env))
    local compose_file=${files[0]}
    local env_file=${files[1]}
    
    print_status "INFO" "Starting services for $env environment..."
    
    local cmd="docker-compose -f $compose_file"
    if [ -n "$env_file" ]; then
        cmd="$cmd --env-file $env_file"
    fi
    cmd="$cmd up -d"
    
    if eval $cmd; then
        print_status "PASS" "Services started successfully for $env"
    else
        print_status "FAIL" "Failed to start services for $env"
        exit 1
    fi
}

# Function to stop services
stop_services() {
    local env=$1
    local files=($(get_files $env))
    local compose_file=${files[0]}
    local env_file=${files[1]}
    
    print_status "INFO" "Stopping services for $env environment..."
    
    local cmd="docker-compose -f $compose_file"
    if [ -n "$env_file" ]; then
        cmd="$cmd --env-file $env_file"
    fi
    cmd="$cmd down"
    
    if eval $cmd; then
        print_status "PASS" "Services stopped successfully for $env"
    else
        print_status "FAIL" "Failed to stop services for $env"
        exit 1
    fi
}

# Function to restart services
restart_services() {
    local env=$1
    stop_services $env
    start_services $env
}

# Function to show logs
show_logs() {
    local env=$1
    local files=($(get_files $env))
    local compose_file=${files[0]}
    local env_file=${files[1]}
    
    print_status "INFO" "Showing logs for $env environment..."
    
    local cmd="docker-compose -f $compose_file"
    if [ -n "$env_file" ]; then
        cmd="$cmd --env-file $env_file"
    fi
    cmd="$cmd logs -f"
    
    eval $cmd
}

# Function to show status
show_status() {
    local env=$1
    local files=($(get_files $env))
    local compose_file=${files[0]}
    local env_file=${files[1]}
    
    print_status "INFO" "Showing status for $env environment..."
    
    local cmd="docker-compose -f $compose_file"
    if [ -n "$env_file" ]; then
        cmd="$cmd --env-file $env_file"
    fi
    cmd="$cmd ps"
    
    eval $cmd
}

# Function to clean up
clean_up() {
    local env=$1
    local files=($(get_files $env))
    local compose_file=${files[0]}
    local env_file=${files[1]}
    
    print_status "INFO" "Cleaning up $env environment..."
    
    local cmd="docker-compose -f $compose_file"
    if [ -n "$env_file" ]; then
        cmd="$cmd --env-file $env_file"
    fi
    cmd="$cmd down -v --remove-orphans"
    
    if eval $cmd; then
        print_status "PASS" "Cleanup completed for $env"
    else
        print_status "FAIL" "Failed to cleanup $env"
        exit 1
    fi
}

# Function to validate configuration
validate_config() {
    local env=$1
    local files=($(get_files $env))
    local compose_file=${files[0]}
    local env_file=${files[1]}
    
    print_status "INFO" "Validating configuration for $env environment..."
    
    local cmd="docker-compose -f $compose_file"
    if [ -n "$env_file" ]; then
        cmd="$cmd --env-file $env_file"
    fi
    cmd="$cmd config"
    
    if eval $cmd > /dev/null; then
        print_status "PASS" "Configuration is valid for $env"
    else
        print_status "FAIL" "Configuration validation failed for $env"
        exit 1
    fi
}

# Main execution
main() {
    local env=${1:-$DEFAULT_ENV}
    local command=${2:-"up"}
    
    # Validate environment
    validate_environment $env
    
    # Change to script directory
    cd "$SCRIPT_DIR"
    
    # Execute command
    case $command in
        "build")
            build_images $env
            ;;
        "up")
            start_services $env
            ;;
        "down")
            stop_services $env
            ;;
        "restart")
            restart_services $env
            ;;
        "logs")
            show_logs $env
            ;;
        "status")
            show_status $env
            ;;
        "clean")
            clean_up $env
            ;;
        "validate")
            validate_config $env
            ;;
        *)
            print_status "FAIL" "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Check if help is requested
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_usage
    exit 0
fi

# Run main function
main "$@"