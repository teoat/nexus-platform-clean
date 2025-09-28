#!/bin/bash

# NUC Automated Maintenance System Launcher
# Comprehensive workspace cleanup and locking system under NUC

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NEXUS_PATH="/Users/Arief/Desktop/Nexus"
BACKEND_PATH="$NEXUS_PATH/backend"
SERVICES_PATH="$BACKEND_PATH/services"
LOG_PATH="$NEXUS_PATH/logs"
PID_PATH="$NEXUS_PATH/locks"

# Create necessary directories
mkdir -p "$LOG_PATH"
mkdir -p "$PID_PATH"

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check if system is already running
check_running() {
    if [ -f "$PID_PATH/nuc_maintenance.pid" ]; then
        PID=$(cat "$PID_PATH/nuc_maintenance.pid")
        if ps -p $PID > /dev/null 2>&1; then
            error "NUC Maintenance System is already running (PID: $PID)"
            exit 1
        else
            warning "Stale PID file found, removing..."
            rm -f "$PID_PATH/nuc_maintenance.pid"
        fi
    fi
}

# Start NUC Maintenance System
start_maintenance() {
    log "Starting NUC Automated Maintenance System..."
    
    # Change to Nexus directory
    cd "$NEXUS_PATH"
    
    # Activate virtual environment if it exists
    if [ -d "nexus_env" ]; then
        log "Activating virtual environment..."
        source nexus_env/bin/activate
    fi
    
    # Start the integrated maintenance system
    log "Launching NUC Maintenance Integration..."
    nohup python3 "$SERVICES_PATH/nuc_maintenance_integration.py" > "$LOG_PATH/nuc_maintenance.log" 2>&1 &
    
    # Save PID
    echo $! > "$PID_PATH/nuc_maintenance.pid"
    
    # Wait a moment for startup
    sleep 3
    
    # Check if process is running
    if ps -p $! > /dev/null 2>&1; then
        log "NUC Maintenance System started successfully (PID: $!)"
        log "Log file: $LOG_PATH/nuc_maintenance.log"
        log "PID file: $PID_PATH/nuc_maintenance.pid"
    else
        error "Failed to start NUC Maintenance System"
        exit 1
    fi
}

# Stop NUC Maintenance System
stop_maintenance() {
    log "Stopping NUC Maintenance System..."
    
    if [ -f "$PID_PATH/nuc_maintenance.pid" ]; then
        PID=$(cat "$PID_PATH/nuc_maintenance.pid")
        if ps -p $PID > /dev/null 2>&1; then
            log "Stopping process $PID..."
            kill $PID
            
            # Wait for graceful shutdown
            for i in {1..10}; do
                if ! ps -p $PID > /dev/null 2>&1; then
                    break
                fi
                sleep 1
            done
            
            # Force kill if still running
            if ps -p $PID > /dev/null 2>&1; then
                warning "Force killing process $PID..."
                kill -9 $PID
            fi
            
            log "NUC Maintenance System stopped"
        else
            warning "Process $PID not found"
        fi
        
        rm -f "$PID_PATH/nuc_maintenance.pid"
    else
        warning "No PID file found"
    fi
}

# Show status
show_status() {
    log "NUC Maintenance System Status:"
    echo
    
    if [ -f "$PID_PATH/nuc_maintenance.pid" ]; then
        PID=$(cat "$PID_PATH/nuc_maintenance.pid")
        if ps -p $PID > /dev/null 2>&1; then
            info "Status: RUNNING (PID: $PID)"
            info "Uptime: $(ps -o etime= -p $PID | tr -d ' ')"
            info "Memory: $(ps -o rss= -p $PID | tr -d ' ') KB"
        else
            error "Status: NOT RUNNING (stale PID file)"
        fi
    else
        error "Status: NOT RUNNING (no PID file)"
    fi
    
    echo
    info "Log file: $LOG_PATH/nuc_maintenance.log"
    info "PID file: $PID_PATH/nuc_maintenance.pid"
    
    # Show recent log entries
    if [ -f "$LOG_PATH/nuc_maintenance.log" ]; then
        echo
        info "Recent log entries:"
        tail -n 10 "$LOG_PATH/nuc_maintenance.log"
    fi
}

# Show logs
show_logs() {
    if [ -f "$LOG_PATH/nuc_maintenance.log" ]; then
        log "Showing NUC Maintenance System logs:"
        echo
        tail -f "$LOG_PATH/nuc_maintenance.log"
    else
        error "Log file not found: $LOG_PATH/nuc_maintenance.log"
    fi
}

# Force cleanup
force_cleanup() {
    log "Force cleanup requested..."
    
    if [ -f "$PID_PATH/nuc_maintenance.pid" ]; then
        PID=$(cat "$PID_PATH/nuc_maintenance.pid")
        if ps -p $PID > /dev/null 2>&1; then
            info "Triggering force cleanup on running system..."
            # In a real implementation, this would send a signal or API call
            warning "Force cleanup not implemented for running system"
        else
            error "System not running"
        fi
    else
        error "System not running"
    fi
}

# Force lock
force_lock() {
    log "Force lock requested..."
    
    if [ -f "$PID_PATH/nuc_maintenance.pid" ]; then
        PID=$(cat "$PID_PATH/nuc_maintenance.pid")
        if ps -p $PID > /dev/null 2>&1; then
            info "Triggering force lock on running system..."
            # In a real implementation, this would send a signal or API call
            warning "Force lock not implemented for running system"
        else
            error "System not running"
        fi
    else
        error "System not running"
    fi
}

# Show help
show_help() {
    echo "NUC Automated Maintenance System Launcher"
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  start       Start the NUC Maintenance System"
    echo "  stop        Stop the NUC Maintenance System"
    echo "  restart     Restart the NUC Maintenance System"
    echo "  status      Show system status"
    echo "  logs        Show live logs"
    echo "  cleanup     Force immediate cleanup"
    echo "  lock        Force immediate file locking"
    echo "  help        Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 status"
    echo "  $0 logs"
    echo
}

# Main script logic
case "${1:-}" in
    start)
        check_running
        start_maintenance
        ;;
    stop)
        stop_maintenance
        ;;
    restart)
        stop_maintenance
        sleep 2
        start_maintenance
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    cleanup)
        force_cleanup
        ;;
    lock)
        force_lock
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        error "Unknown command: ${1:-}"
        echo
        show_help
        exit 1
        ;;
esac
