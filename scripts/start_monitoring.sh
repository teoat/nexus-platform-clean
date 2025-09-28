#!/bin/bash

# NEXUS Monitoring Startup Script
# Starts all monitoring services and tools

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
CONFIG_DIR="$PROJECT_ROOT/config"

# Create necessary directories
mkdir -p "$LOG_DIR"
mkdir -p "$CONFIG_DIR"

echo -e "${BLUE}🚀 Starting NEXUS Monitoring System${NC}"
echo "=================================="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to start a service in background
start_service() {
    local service_name="$1"
    local command="$2"
    local log_file="$3"
    
    echo -e "${YELLOW}Starting $service_name...${NC}"
    
    if [ -f "$log_file" ]; then
        rm "$log_file"
    fi
    
    nohup $command > "$log_file" 2>&1 &
    local pid=$!
    echo $pid > "$LOG_DIR/${service_name}.pid"
    
    # Wait a moment and check if process is still running
    sleep 2
    if kill -0 $pid 2>/dev/null; then
        echo -e "${GREEN}✅ $service_name started (PID: $pid)${NC}"
    else
        echo -e "${RED}❌ Failed to start $service_name${NC}"
        return 1
    fi
}

# Check dependencies
echo -e "${BLUE}Checking dependencies...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi

if ! command_exists psutil; then
    echo -e "${YELLOW}⚠️  Installing psutil...${NC}"
    pip3 install psutil requests
fi

# Check if monitoring is already running
if [ -f "$LOG_DIR/system_monitor.pid" ]; then
    local pid=$(cat "$LOG_DIR/system_monitor.pid")
    if kill -0 $pid 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Monitoring is already running (PID: $pid)${NC}"
        echo "Stopping existing monitoring..."
        kill $pid
        rm "$LOG_DIR/system_monitor.pid"
    fi
fi

# Start monitoring services
echo -e "${BLUE}Starting monitoring services...${NC}"

# 1. System Monitor
start_service "system_monitor" \
    "python3 $SCRIPT_DIR/system_monitor.py" \
    "$LOG_DIR/system_monitor.log"

# 2. Health Checker (run every 30 seconds)
start_service "health_checker" \
    "while true; do python3 $SCRIPT_DIR/health_checker.py --json >> $LOG_DIR/health_checker.log 2>&1; sleep 30; done" \
    "$LOG_DIR/health_checker.log"

# 3. Backup Manager (run daily at 2 AM)
start_service "backup_scheduler" \
    "while true; do python3 $SCRIPT_DIR/backup_manager.py --full >> $LOG_DIR/backup_scheduler.log 2>&1; sleep 86400; done" \
    "$LOG_DIR/backup_scheduler.log"

# 4. System Dashboard (optional, run on port 8080)
if ! port_in_use 8080; then
    start_service "system_dashboard" \
        "python3 -m http.server 8080 --directory $PROJECT_ROOT" \
        "$LOG_DIR/system_dashboard.log"
    echo -e "${GREEN}📊 System Dashboard available at: http://localhost:8080${NC}"
else
    echo -e "${YELLOW}⚠️  Port 8080 is in use, skipping dashboard server${NC}"
fi

# Create monitoring status script
cat > "$SCRIPT_DIR/monitoring_status.sh" << 'EOF'
#!/bin/bash

# NEXUS Monitoring Status Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"

echo "🔍 NEXUS Monitoring Status"
echo "=========================="

# Check system monitor
if [ -f "$LOG_DIR/system_monitor.pid" ]; then
    local pid=$(cat "$LOG_DIR/system_monitor.pid")
    if kill -0 $pid 2>/dev/null; then
        echo "✅ System Monitor: Running (PID: $pid)"
    else
        echo "❌ System Monitor: Not running"
    fi
else
    echo "❌ System Monitor: Not started"
fi

# Check health checker
if [ -f "$LOG_DIR/health_checker.pid" ]; then
    local pid=$(cat "$LOG_DIR/health_checker.pid")
    if kill -0 $pid 2>/dev/null; then
        echo "✅ Health Checker: Running (PID: $pid)"
    else
        echo "❌ Health Checker: Not running"
    fi
else
    echo "❌ Health Checker: Not started"
fi

# Check backup scheduler
if [ -f "$LOG_DIR/backup_scheduler.pid" ]; then
    local pid=$(cat "$LOG_DIR/backup_scheduler.pid")
    if kill -0 $pid 2>/dev/null; then
        echo "✅ Backup Scheduler: Running (PID: $pid)"
    else
        echo "❌ Backup Scheduler: Not running"
    fi
else
    echo "❌ Backup Scheduler: Not started"
fi

# Check system dashboard
if [ -f "$LOG_DIR/system_dashboard.pid" ]; then
    local pid=$(cat "$LOG_DIR/system_dashboard.pid")
    if kill -0 $pid 2>/dev/null; then
        echo "✅ System Dashboard: Running (PID: $pid)"
    else
        echo "❌ System Dashboard: Not running"
    fi
else
    echo "❌ System Dashboard: Not started"
fi

echo ""
echo "📊 Quick Health Check:"
python3 "$SCRIPT_DIR/health_checker.py"

echo ""
echo "📁 Log files:"
ls -la "$LOG_DIR"/*.log 2>/dev/null || echo "No log files found"
EOF

chmod +x "$SCRIPT_DIR/monitoring_status.sh"

# Create stop monitoring script
cat > "$SCRIPT_DIR/stop_monitoring.sh" << 'EOF'
#!/bin/bash

# NEXUS Monitoring Stop Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"

echo "🛑 Stopping NEXUS Monitoring System"
echo "=================================="

# Stop all monitoring services
for service in system_monitor health_checker backup_scheduler system_dashboard; do
    if [ -f "$LOG_DIR/${service}.pid" ]; then
        local pid=$(cat "$LOG_DIR/${service}.pid")
        if kill -0 $pid 2>/dev/null; then
            echo "Stopping $service (PID: $pid)..."
            kill $pid
            rm "$LOG_DIR/${service}.pid"
            echo "✅ $service stopped"
        else
            echo "⚠️  $service was not running"
            rm "$LOG_DIR/${service}.pid"
        fi
    else
        echo "⚠️  $service was not started"
    fi
done

echo "✅ All monitoring services stopped"
EOF

chmod +x "$SCRIPT_DIR/stop_monitoring.sh"

# Create monitoring configuration if it doesn't exist
if [ ! -f "$CONFIG_DIR/monitoring.json" ]; then
    echo -e "${YELLOW}Creating default monitoring configuration...${NC}"
    cp "$SCRIPT_DIR/../config/monitoring.json" "$CONFIG_DIR/monitoring.json" 2>/dev/null || true
fi

if [ ! -f "$CONFIG_DIR/backup.json" ]; then
    echo -e "${YELLOW}Creating default backup configuration...${NC}"
    cp "$SCRIPT_DIR/../config/backup.json" "$CONFIG_DIR/backup.json" 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}✅ NEXUS Monitoring System started successfully!${NC}"
echo ""
echo "📋 Available commands:"
echo "  $SCRIPT_DIR/monitoring_status.sh  - Check monitoring status"
echo "  $SCRIPT_DIR/stop_monitoring.sh    - Stop all monitoring"
echo "  python3 $SCRIPT_DIR/system_dashboard.py --once  - Show current status"
echo "  python3 $SCRIPT_DIR/health_checker.py          - Quick health check"
echo ""
echo "📁 Logs are stored in: $LOG_DIR"
echo "⚙️  Configuration: $CONFIG_DIR"
echo ""

# Show initial status
echo "🔍 Initial System Status:"
python3 "$SCRIPT_DIR/health_checker.py"
