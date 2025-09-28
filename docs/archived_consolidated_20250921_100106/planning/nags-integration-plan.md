# Nags Integration Plan

**Status**: 🔒 **LOCKED** - SSOT Consolidated Document
**Version**: 1.0
**Last Updated**: 2025-01-17
**Source**: Consolidated from multiple files

## Section 1: NAGS_INTEGRATION_PLAN.md

# 🚀 **NAGS INTEGRATION PLAN**

## **Complete System Integration & Port Configuration**

**Date**: 2025-01-15
**Status**: READY FOR IMPLEMENTATION
**Priority**: CRITICAL

---

## 🎯 **INTEGRATION OVERVIEW**

This plan integrates NAGS (NEXUS Unified Agent Governance System) into the running NEXUS platform with proper port configuration, service integration, and system-wide deployment.

---

## 🔧 **CURRENT SYSTEM STATUS**

### **Running Services Detected:**

- ✅ **NEXUS Tier5 Launcher**: Running (PID 17208)
- ✅ **Enhanced Real Continuous Automation**: Running (PID 27149)
- ✅ **File Search Process**: Running (PID 29005)

### **Available Ports:**

- **Frontend**: 2100-2400 (4 ports)
- **Backend**: 3100-3200 (2 ports)
- **Data**: 3800-3900 (2 ports)
- **Monitoring**: 3400-3700 (4 ports)
- **Automation**: 4000 (1 port)

---

## 🚀 **NAGS INTEGRATION STRATEGY**

### **Phase 1: Port Configuration & Service Setup**

#### **1.1 NAGS Service Ports**

```yaml
# Add to .nexus/ssot/master/config/ports.yml
nags_services:
  nags_api: 4100 # Main NAGS API service
  nags_websocket: 4101 # Real-time agent communication
  nags_dashboard: 4102 # NAGS management dashboard
  nags_metrics: 4103 # NAGS metrics and monitoring
```

#### **1.2 Port Conflict Resolution**

- **NAGS API**: Port 4100 (next available after automation)
- **WebSocket**: Port 4101 (for real-time communication)
- **Dashboard**: Port 4102 (web-based management)
- **Metrics**: Port 4103 (Prometheus-compatible metrics)

### **Phase 2: Service Integration**

#### **2.1 Integration with Existing Services**

- **Automation Service**: Integrate with port 4000 automation
- **Monitoring Stack**: Integrate with Grafana (3500) and Prometheus (3600)
- **Backend API**: Integrate with main API (3100)

#### **2.2 Agent Registration Points**

- **Existing Agents**: Register current running agents
- **New Agents**: Auto-register new agents on startup
- **Agent Discovery**: Automatic agent discovery and registration

---

## 🔧 **IMPLEMENTATION STEPS**

### **Step 1: Update Port Configuration**

```bash
# Update ports.yml with NAGS ports
cd /Users/Arief/Desktop/Nexus
cat >> .nexus/ssot/master/config/ports.yml << 'EOF'

# NAGS Services
nags_services:
  nags_api: 4100
  nags_websocket: 4101
  nags_dashboard: 4102
  nags_metrics: 4103
EOF
```

### **Step 2: Create NAGS Service Wrapper**

```python
# Create .nexus/ssot/master/nags/nags_service.py
class NAGSService:
    """NAGS as a service with API endpoints"""

    def __init__(self, port=4100):
        self.port = port
        self.nags = get_nags()
        self.app = FastAPI()
        self.setup_routes()

    def setup_routes(self):
        @self.app.post("/api/agents/register")
        async def register_agent(agent_data: dict):
            return self.nags.register_agent(**agent_data)

        @self.app.post("/api/files/intercept")
        async def intercept_file(file_data: dict):
            return self.nags.intercept_file_creation(**file_data)

        @self.app.get("/api/stats")
        async def get_stats():
            return self.nags.show_stats()
```

### **Step 3: Create System Integration Scripts**

#### **3.1 NAGS Systemd Service (Linux/macOS)**

```bash
# Create .nexus/ssot/master/nags/nags.service
[Unit]
Description=NAGS (NEXUS Unified Agent Governance System)
After=network.target

[Service]
Type=simple
User=arief
WorkingDirectory=/Users/Arief/Desktop/Nexus
ExecStart=/usr/bin/python3 .nexus/ssot/master/nags/launch_nags.py start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### **3.2 NAGS Docker Integration**

```dockerfile
# Create .nexus/ssot/master/nags/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install fastapi uvicorn websockets

EXPOSE 4100-4103

CMD ["python", "launch_nags.py", "start", "--service"]
```

### **Step 4: Integration with Existing Services**

#### **4.1 Automation Service Integration**

```python
# Update existing automation to use NAGS
from .nexus.ssot.master.nags.agent_coordination import register_agent, register_activity

class EnhancedAutomation:
    def __init__(self):
        # Register with NAGS
        self.agent_id = "enhanced_automation"
        register_agent(
            agent_id=self.agent_id,
            capabilities=["automation", "task_processing"],
            current_task="Continuous automation",
            priority_score=10
        )

    def create_file(self, file_path, content):
        # Use NAGS interception
        result = intercept_file_creation(self.agent_id, file_path, content, "automation")
        if result['approved']:
            # Create file
            pass
```

#### **4.2 Monitoring Integration**

```python
# Integrate with Grafana dashboard
nags_metrics = {
    'nags_file_interceptions_total': 'counter',
    'nags_duplicates_prevented_total': 'counter',
    'nags_agent_conflicts_resolved_total': 'counter',
    'nags_ssot_compliance_rate': 'gauge'
}
```

---

## 🌐 **NAGS WEB DASHBOARD**

### **Dashboard Features**

- **Real-time Agent Status**: Live view of all registered agents
- **File Interception Logs**: Real-time file creation monitoring
- **Duplicate Prevention Stats**: Duplicate detection and prevention metrics
- **Conflict Resolution**: Agent conflict monitoring and resolution
- **SSOT Compliance**: Compliance monitoring and reporting

### **Dashboard Implementation**

```python
# Create .nexus/ssot/master/nags/dashboard.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="NAGS Dashboard")

@app.get("/")
async def dashboard():
    return templates.TemplateResponse("dashboard.html", {
        "agents": nags.coordinator.active_agents,
        "stats": nags.get_stats(),
        "recent_activities": nags.coordinator.activity_log[-50:]
    })
```

---

## 🔌 **INTEGRATION POINTS**

### **1. Existing Agent Integration**

```python
# For each existing agent, add NAGS integration
def integrate_agent_with_nags(agent_name, capabilities, current_task):
    # Register agent
    agent = register_agent(agent_name, capabilities, current_task)

    # Wrap file operations
    def nags_file_operation(operation_func):
        def wrapper(file_path, content, *args, **kwargs):
            result = intercept_file_creation(agent_name, file_path, content)
            if result['approved']:
                return operation_func(file_path, content, *args, **kwargs)
            else:
                raise Exception(f"File operation blocked: {result['message']}")
        return wrapper

    return nags_file_operation
```

### **2. System Startup Integration**

```python
# Update main system startup to include NAGS
def start_nexus_system():
    # Start NAGS first
    nags = get_nags()
    nags.start()

    # Start other services
    start_automation_service()
    start_monitoring_services()
    start_backend_services()

    # Register existing agents
    register_existing_agents()
```

### **3. Docker Compose Integration**

```yaml
# Add to docker-compose.optimized.yml
services:
  nags:
    build: .nexus/ssot/master/nags/
    ports:
      - "4100:4100" # API
      - "4101:4101" # WebSocket
      - "4102:4102" # Dashboard
      - "4103:4103" # Metrics
    volumes:
      - ./.nexus/ssot/master/nags/data:/nexus_backend/data
    depends_on:
      - redis
      - postgresql
```

---

## 📊 **MONITORING & METRICS**

### **NAGS Metrics Endpoints**

- **`/metrics`**: Prometheus-compatible metrics
- **`/health`**: Health check endpoint
- **`/stats`**: Detailed system statistics
- **`/agents`**: Agent status and information

### **Grafana Dashboard Integration**

```json
{
  "dashboard": {
    "title": "NAGS System Monitoring",
    "panels": [
      {
        "title": "File Interceptions",
        "type": "graph",
        "targets": [
          {
            "expr": "nags_file_interceptions_total"
          }
        ]
      },
      {
        "title": "Agent Conflicts",
        "type": "stat",
        "targets": [
          {
            "expr": "nags_agent_conflicts_resolved_total"
          }
        ]
      }
    ]
  }
}
```

---

## 🚀 **DEPLOYMENT COMMANDS**

### **Quick Start (5 minutes)**

```bash
# 1. Start NAGS system
cd /Users/Arief/Desktop/Nexus
python .nexus/ssot/master/nags/launch_nags.py start

# 2. Start NAGS API service
python .nexus/ssot/master/nags/nags_service.py --port 4100 &

# 3. Start NAGS dashboard
python .nexus/ssot/master/nags/dashboard.py --port 4102 &

# 4. Check status
curl http://localhost:4100/health
```

### **Production Deployment**

```bash
# 1. Update port configuration
./scripts/update_ports.sh

# 2. Deploy NAGS service
docker-compose up -d nags

# 3. Integrate with existing services
./scripts/integrate_nags.sh

# 4. Start monitoring
./scripts/start_nags_monitoring.sh
```

---

## 🎯 **INTEGRATION AREAS**

### **1. Critical Integration Points**

- **File System Operations**: All file creation/modification
- **Agent Registration**: All agent startup and registration
- **Configuration Management**: All config file operations
- **Documentation Updates**: All documentation changes

### **2. Monitoring Integration**

- **Grafana Dashboards**: NAGS metrics and monitoring
- **Prometheus Metrics**: System performance metrics
- **Alert Manager**: NAGS system alerts
- **Log Aggregation**: Centralized logging

### **3. API Integration**

- **REST API**: NAGS management endpoints
- **WebSocket**: Real-time agent communication
- **GraphQL**: Advanced querying capabilities
- **Webhook**: External system integration

---

## 📈 **EXPECTED RESULTS**

### **Immediate Benefits**

- **Centralized Agent Management**: All agents managed through NAGS
- **Real-time Monitoring**: Live view of system operations
- **Automated Conflict Resolution**: Intelligent conflict resolution
- **SSOT Compliance**: 100% compliance enforcement

### **Long-term Benefits**

- **Scalable Architecture**: Easy addition of new agents
- **Performance Optimization**: System-wide optimization
- **Maintenance Reduction**: Automated maintenance tasks
- **Quality Improvement**: Consistent file structures and operations

---

## 🔧 **NEXT STEPS**

1. **Update Port Configuration** (5 minutes)
2. **Deploy NAGS Service** (10 minutes)
3. **Integrate Existing Agents** (15 minutes)
4. **Setup Monitoring** (10 minutes)
5. **Test Integration** (10 minutes)
6. **Production Deployment** (30 minutes)

**Total Time**: ~80 minutes for complete integration

---

**Status**: Ready for implementation
**Priority**: Critical
**Expected Impact**: Complete system transformation

---

## Section 2: NAGS_INTEGRATION_PLAN.md

# 🚀 **NAGS INTEGRATION PLAN**

## **Complete System Integration & Port Configuration**

**Date**: 2025-01-15
**Status**: READY FOR IMPLEMENTATION
**Priority**: CRITICAL

---

## 🎯 **INTEGRATION OVERVIEW**

This plan integrates NAGS (NEXUS Unified Agent Governance System) into the running NEXUS platform with proper port configuration, service integration, and system-wide deployment.

---

## 🔧 **CURRENT SYSTEM STATUS**

### **Running Services Detected:**

- ✅ **NEXUS Tier5 Launcher**: Running (PID 17208)
- ✅ **Enhanced Real Continuous Automation**: Running (PID 27149)
- ✅ **File Search Process**: Running (PID 29005)

### **Available Ports:**

- **Frontend**: 2100-2400 (4 ports)
- **Backend**: 3100-3200 (2 ports)
- **Data**: 3800-3900 (2 ports)
- **Monitoring**: 3400-3700 (4 ports)
- **Automation**: 4000 (1 port)

---

## 🚀 **NAGS INTEGRATION STRATEGY**

### **Phase 1: Port Configuration & Service Setup**

#### **1.1 NAGS Service Ports**

```yaml
# Add to .nexus/ssot/master/config/ports.yml
nags_services:
  nags_api: 4100 # Main NAGS API service
  nags_websocket: 4101 # Real-time agent communication
  nags_dashboard: 4102 # NAGS management dashboard
  nags_metrics: 4103 # NAGS metrics and monitoring
```

#### **1.2 Port Conflict Resolution**

- **NAGS API**: Port 4100 (next available after automation)
- **WebSocket**: Port 4101 (for real-time communication)
- **Dashboard**: Port 4102 (web-based management)
- **Metrics**: Port 4103 (Prometheus-compatible metrics)

### **Phase 2: Service Integration**

#### **2.1 Integration with Existing Services**

- **Automation Service**: Integrate with port 4000 automation
- **Monitoring Stack**: Integrate with Grafana (3500) and Prometheus (3600)
- **Backend API**: Integrate with main API (3100)

#### **2.2 Agent Registration Points**

- **Existing Agents**: Register current running agents
- **New Agents**: Auto-register new agents on startup
- **Agent Discovery**: Automatic agent discovery and registration

---

## 🔧 **IMPLEMENTATION STEPS**

### **Step 1: Update Port Configuration**

```bash
# Update ports.yml with NAGS ports
cd /Users/Arief/Desktop/Nexus
cat >> .nexus/ssot/master/config/ports.yml << 'EOF'

# NAGS Services
nags_services:
  nags_api: 4100
  nags_websocket: 4101
  nags_dashboard: 4102
  nags_metrics: 4103
EOF
```

### **Step 2: Create NAGS Service Wrapper**

```python
# Create .nexus/ssot/master/nags/nags_service.py
class NAGSService:
    """NAGS as a service with API endpoints"""

    def __init__(self, port=4100):
        self.port = port
        self.nags = get_nags()
        self.app = FastAPI()
        self.setup_routes()

    def setup_routes(self):
        @self.app.post("/api/agents/register")
        async def register_agent(agent_data: dict):
            return self.nags.register_agent(**agent_data)

        @self.app.post("/api/files/intercept")
        async def intercept_file(file_data: dict):
            return self.nags.intercept_file_creation(**file_data)

        @self.app.get("/api/stats")
        async def get_stats():
            return self.nags.show_stats()
```

### **Step 3: Create System Integration Scripts**

#### **3.1 NAGS Systemd Service (Linux/macOS)**

```bash
# Create .nexus/ssot/master/nags/nags.service
[Unit]
Description=NAGS (NEXUS Unified Agent Governance System)
After=network.target

[Service]
Type=simple
User=arief
WorkingDirectory=/Users/Arief/Desktop/Nexus
ExecStart=/usr/bin/python3 .nexus/ssot/master/nags/launch_nags.py start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### **3.2 NAGS Docker Integration**

```dockerfile
# Create .nexus/ssot/master/nags/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install fastapi uvicorn websockets

EXPOSE 4100-4103

CMD ["python", "launch_nags.py", "start", "--service"]
```

### **Step 4: Integration with Existing Services**

#### **4.1 Automation Service Integration**

```python
# Update existing automation to use NAGS
from .nexus.ssot.master.nags.agent_coordination import register_agent, register_activity

class EnhancedAutomation:
    def __init__(self):
        # Register with NAGS
        self.agent_id = "enhanced_automation"
        register_agent(
            agent_id=self.agent_id,
            capabilities=["automation", "task_processing"],
            current_task="Continuous automation",
            priority_score=10
        )

    def create_file(self, file_path, content):
        # Use NAGS interception
        result = intercept_file_creation(self.agent_id, file_path, content, "automation")
        if result['approved']:
            # Create file
            pass
```

#### **4.2 Monitoring Integration**

```python
# Integrate with Grafana dashboard
nags_metrics = {
    'nags_file_interceptions_total': 'counter',
    'nags_duplicates_prevented_total': 'counter',
    'nags_agent_conflicts_resolved_total': 'counter',
    'nags_ssot_compliance_rate': 'gauge'
}
```

---

## 🌐 **NAGS WEB DASHBOARD**

### **Dashboard Features**

- **Real-time Agent Status**: Live view of all registered agents
- **File Interception Logs**: Real-time file creation monitoring
- **Duplicate Prevention Stats**: Duplicate detection and prevention metrics
- **Conflict Resolution**: Agent conflict monitoring and resolution
- **SSOT Compliance**: Compliance monitoring and reporting

### **Dashboard Implementation**

```python
# Create .nexus/ssot/master/nags/dashboard.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="NAGS Dashboard")

@app.get("/")
async def dashboard():
    return templates.TemplateResponse("dashboard.html", {
        "agents": nags.coordinator.active_agents,
        "stats": nags.get_stats(),
        "recent_activities": nags.coordinator.activity_log[-50:]
    })
```

---

## 🔌 **INTEGRATION POINTS**

### **1. Existing Agent Integration**

```python
# For each existing agent, add NAGS integration
def integrate_agent_with_nags(agent_name, capabilities, current_task):
    # Register agent
    agent = register_agent(agent_name, capabilities, current_task)

    # Wrap file operations
    def nags_file_operation(operation_func):
        def wrapper(file_path, content, *args, **kwargs):
            result = intercept_file_creation(agent_name, file_path, content)
            if result['approved']:
                return operation_func(file_path, content, *args, **kwargs)
            else:
                raise Exception(f"File operation blocked: {result['message']}")
        return wrapper

    return nags_file_operation
```

### **2. System Startup Integration**

```python
# Update main system startup to include NAGS
def start_nexus_system():
    # Start NAGS first
    nags = get_nags()
    nags.start()

    # Start other services
    start_automation_service()
    start_monitoring_services()
    start_backend_services()

    # Register existing agents
    register_existing_agents()
```

### **3. Docker Compose Integration**

```yaml
# Add to docker-compose.optimized.yml
services:
  nags:
    build: .nexus/ssot/master/nags/
    ports:
      - "4100:4100" # API
      - "4101:4101" # WebSocket
      - "4102:4102" # Dashboard
      - "4103:4103" # Metrics
    volumes:
      - ./.nexus/ssot/master/nags/data:/nexus_backend/data
    depends_on:
      - redis
      - postgresql
```

---

## 📊 **MONITORING & METRICS**

### **NAGS Metrics Endpoints**

- **`/metrics`**: Prometheus-compatible metrics
- **`/health`**: Health check endpoint
- **`/stats`**: Detailed system statistics
- **`/agents`**: Agent status and information

### **Grafana Dashboard Integration**

```json
{
  "dashboard": {
    "title": "NAGS System Monitoring",
    "panels": [
      {
        "title": "File Interceptions",
        "type": "graph",
        "targets": [
          {
            "expr": "nags_file_interceptions_total"
          }
        ]
      },
      {
        "title": "Agent Conflicts",
        "type": "stat",
        "targets": [
          {
            "expr": "nags_agent_conflicts_resolved_total"
          }
        ]
      }
    ]
  }
}
```

---

## 🚀 **DEPLOYMENT COMMANDS**

### **Quick Start (5 minutes)**

```bash
# 1. Start NAGS system
cd /Users/Arief/Desktop/Nexus
python .nexus/ssot/master/nags/launch_nags.py start

# 2. Start NAGS API service
python .nexus/ssot/master/nags/nags_service.py --port 4100 &

# 3. Start NAGS dashboard
python .nexus/ssot/master/nags/dashboard.py --port 4102 &

# 4. Check status
curl http://localhost:4100/health
```

### **Production Deployment**

```bash
# 1. Update port configuration
./scripts/update_ports.sh

# 2. Deploy NAGS service
docker-compose up -d nags

# 3. Integrate with existing services
./scripts/integrate_nags.sh

# 4. Start monitoring
./scripts/start_nags_monitoring.sh
```

---

## 🎯 **INTEGRATION AREAS**

### **1. Critical Integration Points**

- **File System Operations**: All file creation/modification
- **Agent Registration**: All agent startup and registration
- **Configuration Management**: All config file operations
- **Documentation Updates**: All documentation changes

### **2. Monitoring Integration**

- **Grafana Dashboards**: NAGS metrics and monitoring
- **Prometheus Metrics**: System performance metrics
- **Alert Manager**: NAGS system alerts
- **Log Aggregation**: Centralized logging

### **3. API Integration**

- **REST API**: NAGS management endpoints
- **WebSocket**: Real-time agent communication
- **GraphQL**: Advanced querying capabilities
- **Webhook**: External system integration

---

## 📈 **EXPECTED RESULTS**

### **Immediate Benefits**

- **Centralized Agent Management**: All agents managed through NAGS
- **Real-time Monitoring**: Live view of system operations
- **Automated Conflict Resolution**: Intelligent conflict resolution
- **SSOT Compliance**: 100% compliance enforcement

### **Long-term Benefits**

- **Scalable Architecture**: Easy addition of new agents
- **Performance Optimization**: System-wide optimization
- **Maintenance Reduction**: Automated maintenance tasks
- **Quality Improvement**: Consistent file structures and operations

---

## 🔧 **NEXT STEPS**

1. **Update Port Configuration** (5 minutes)
2. **Deploy NAGS Service** (10 minutes)
3. **Integrate Existing Agents** (15 minutes)
4. **Setup Monitoring** (10 minutes)
5. **Test Integration** (10 minutes)
6. **Production Deployment** (30 minutes)

**Total Time**: ~80 minutes for complete integration

---

**Status**: Ready for implementation
**Priority**: Critical
**Expected Impact**: Complete system transformation

---
