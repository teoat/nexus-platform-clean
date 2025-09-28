#!/bin/bash

# NEXUS System Stopper
# Stops all running NEXUS systems

echo "🛑 NEXUS SYSTEM STOPPER"
echo "======================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Stop all NEXUS processes
echo "Stopping all NEXUS systems..."

# Stop phase system
pkill -f "simple_phase_system" 2>/dev/null
if [ $? -eq 0 ]; then
    print_status "Phase System stopped"
else
    print_warning "Phase System was not running"
fi

# Stop all agents
pkill -f "agent_" 2>/dev/null
if [ $? -eq 0 ]; then
    print_status "All agents stopped"
else
    print_warning "No agents were running"
fi

# Stop monitoring system
pkill -f "monitoring_system" 2>/dev/null
if [ $? -eq 0 ]; then
    print_status "Monitoring System stopped"
else
    print_warning "Monitoring System was not running"
fi

# Stop quality checker
pkill -f "quality_checker" 2>/dev/null
if [ $? -eq 0 ]; then
    print_status "Quality Checker stopped"
else
    print_warning "Quality Checker was not running"
fi

# Stop dual system launcher
pkill -f "launch_dual_systems" 2>/dev/null
if [ $? -eq 0 ]; then
    print_status "Dual System Launcher stopped"
else
    print_warning "Dual System Launcher was not running"
fi

# Stop any other NEXUS processes
pkill -f "nexus" 2>/dev/null
pkill -f "comprehensive_task_manager" 2>/dev/null
pkill -f "monitor_system" 2>/dev/null

# Wait a moment
sleep 2

# Check if any processes are still running
REMAINING=$(ps aux | grep -E "(simple_phase_system|agent_|monitoring_system|quality_checker|launch_dual_systems)" | grep -v grep | wc -l)

if [ $REMAINING -gt 0 ]; then
    print_warning "Force killing remaining processes..."
    pkill -9 -f "simple_phase_system" 2>/dev/null
    pkill -9 -f "agent_" 2>/dev/null
    pkill -9 -f "monitoring_system" 2>/dev/null
    pkill -9 -f "quality_checker" 2>/dev/null
    pkill -9 -f "launch_dual_systems" 2>/dev/null
    sleep 1
fi

# Final check
FINAL_CHECK=$(ps aux | grep -E "(simple_phase_system|agent_|monitoring_system|quality_checker|launch_dual_systems)" | grep -v grep | wc -l)

if [ $FINAL_CHECK -eq 0 ]; then
    print_status "All NEXUS systems stopped successfully"
else
    print_error "Some processes may still be running"
    echo "Remaining processes:"
    ps aux | grep -E "(simple_phase_system|agent_|monitoring_system|quality_checker|launch_dual_systems)" | grep -v grep
fi

echo ""
echo "🛑 All NEXUS systems have been stopped"
