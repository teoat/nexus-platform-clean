#!/bin/bash

# NEXUS Docker Deployment Demo
# Demonstrates the complete Docker deployment process

set -e

echo "🚀 NEXUS DOCKER DEPLOYMENT DEMO"
echo "==============================="

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

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."

    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    print_status "Prerequisites check passed"
}

# Build images
build_images() {
    print_info "Building Docker images..."

    # Build phase system
    print_info "Building Phase System image..."
    docker build -f Dockerfile.phase-system -t nexus-phase-system:latest . --quiet
    print_status "Phase System image built"

    # Build agents
    print_info "Building Agents image..."
    docker build -f Dockerfile.agents -t nexus-agents:latest . --quiet
    print_status "Agents image built"

    # Build monitoring
    print_info "Building Monitoring image..."
    docker build -f Dockerfile.monitoring -t nexus-monitoring:latest . --quiet
    print_status "Monitoring image built"

    print_status "All images built successfully"
}

# Start services
start_services() {
    print_info "Starting NEXUS services..."

    # Start with docker-compose
    docker-compose up -d

    print_status "Services started"

    # Wait for services to be ready
    print_info "Waiting for services to be ready..."
    sleep 30

    # Check service status
    print_info "Service status:"
    docker-compose ps
}

# Test connectivity
test_connectivity() {
    print_info "Testing connectivity..."

    # Test phase system
    if curl -s http://localhost:8766/health &> /dev/null; then
        print_status "Phase System: Accessible"
    else
        print_warning "Phase System: Not accessible (may still be starting)"
    fi

    # Test Redis
    if docker exec nexus-redis redis-cli ping &> /dev/null; then
        print_status "Redis: Accessible"
    else
        print_warning "Redis: Not accessible"
    fi

    # Check running containers
    print_info "Running containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

# Add sample tasks
add_sample_tasks() {
    print_info "Adding sample tasks to the system..."

    # Create a simple task addition script
    cat > add_demo_tasks.py << 'EOF'
#!/usr/bin/env python3
import asyncio
import json
import websockets
from datetime import datetime

async def add_demo_tasks():
    try:
        async with websockets.connect("ws://localhost:8766") as websocket:
            # Register
            await websocket.send(json.dumps({
                "type": "agent_registration",
                "agent_id": "demo_task_adder",
                "role": "system_intelligence_analysis",
                "capabilities": ["task_management"]
            }))
            await websocket.recv()  # Wait for welcome

            # Add demo tasks
            demo_tasks = [
                {
                    "task_id": "demo_001",
                    "phase": "Phase 1 - Demo",
                    "agent_role": "system_intelligence_analysis",
                    "title": "Docker Deployment Demo Task",
                    "description": "Demonstrate Docker deployment functionality",
                    "priority": 1,
                    "estimated_hours": 1.0,
                    "status": "pending",
                    "dependencies": [],
                    "created_at": datetime.now().isoformat(),
                    "real_execution": True
                },
                {
                    "task_id": "demo_002",
                    "phase": "Phase 1 - Demo",
                    "agent_role": "consolidation_organization",
                    "title": "Container Orchestration Demo",
                    "description": "Show container orchestration capabilities",
                    "priority": 2,
                    "estimated_hours": 2.0,
                    "status": "pending",
                    "dependencies": ["demo_001"],
                    "created_at": datetime.now().isoformat(),
                    "real_execution": True
                }
            ]

            for task in demo_tasks:
                await websocket.send(json.dumps({
                    "type": "add_task",
                    "task": task
                }))
                response = await websocket.recv()
                print(f"Added task: {task['task_id']}")

            print("Demo tasks added successfully!")

    except Exception as e:
        print(f"Error adding demo tasks: {e}")

if __name__ == "__main__":
    asyncio.run(add_demo_tasks())
EOF

    # Run the script
    python3 add_demo_tasks.py
    print_status "Demo tasks added"
}

# Show monitoring
show_monitoring() {
    print_info "Showing system monitoring..."

    echo ""
    print_info "Container Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

    echo ""
    print_info "Container Logs (last 10 lines each):"
    echo "Phase System logs:"
    docker logs nexus-phase-system --tail 10

    echo ""
    echo "Agents logs:"
    docker logs nexus-agents --tail 10

    echo ""
    echo "Monitoring logs:"
    docker logs nexus-monitoring --tail 10
}

# Cleanup function
cleanup() {
    print_info "Cleaning up demo environment..."
    docker-compose down
    docker system prune -f
    print_status "Cleanup completed"
}

# Main demo function
run_demo() {
    print_info "Starting NEXUS Docker Deployment Demo..."
    echo ""

    # Step 1: Check prerequisites
    check_prerequisites
    echo ""

    # Step 2: Build images
    build_images
    echo ""

    # Step 3: Start services
    start_services
    echo ""

    # Step 4: Test connectivity
    test_connectivity
    echo ""

    # Step 5: Add sample tasks
    add_sample_tasks
    echo ""

    # Step 6: Show monitoring
    show_monitoring
    echo ""

    print_status "Demo completed successfully!"
    echo ""
    print_info "Access URLs:"
    echo "• Phase System: http://localhost:8766"
    echo "• Nginx Proxy: http://localhost"
    echo "• Redis: localhost:6379"
    echo ""
    print_info "Useful commands:"
    echo "• View logs: docker-compose logs -f"
    echo "• Stop services: docker-compose down"
    echo "• Scale agents: docker-compose up -d --scale agents=8"
    echo "• Check status: ./check-deployment.sh"
    echo ""
    print_info "Demo will run for 2 minutes, then cleanup..."

    # Run for 2 minutes
    sleep 120

    # Ask if user wants to keep running
    echo ""
    read -p "Keep services running? (y/n): " keep_running

    if [[ $keep_running =~ ^[Yy]$ ]]; then
        print_info "Services will continue running. Use 'docker-compose down' to stop."
    else
        cleanup
    fi
}

# Handle interruption
trap cleanup SIGINT SIGTERM

# Run demo
run_demo
