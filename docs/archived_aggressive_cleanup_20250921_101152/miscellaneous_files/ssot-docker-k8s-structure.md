# Ssot Docker K8S Structure

**Status**: 🔒 **LOCKED** - SSOT Consolidated Document
**Version**: 1.0
**Last Updated**: 2025-01-17
**Source**: Consolidated from multiple files

## Section 1: SSOT_DOCKER_K8S_STRUCTURE.md

# 🎯 SSOT (Single Source of Truth) - Docker & Kubernetes Structure

**Created:** September 14, 2025
**Status:** ✅ ACTIVE

## 📋 SSOT Overview

This document defines the Single Source of Truth (SSOT) for all Docker and Kubernetes configurations in the Nexus Platform.

---

## 🐳 **Docker SSOT**

### **Primary Configuration**

- **File**: `infrastructure/docker/docker-compose.yml` (Root directory)
- **SSOT Copy**: `.tools/utilities/tools/utilities/nexus/ssot/docker-compose.ssot.yml`
- **Purpose**: Main production Docker Compose configuration

### **Dockerfiles (Active)**

```
infrastructure/infrastructure/infrastructure/docker/
├── ui-main.Dockerfile          # Main frontend (Port 2000)
├── ui-glassmorphism.Dockerfile # Glassmorphism theme (Port 2100)
├── ui-cyberpunk.Dockerfile     # Cyberpunk theme (Port 2200)
├── ui-modern.Dockerfile        # Modern theme (Port 2300)
├── ui.Dockerfile              # Legacy (archived)
├── nginx-ui.conf              # Nginx configuration
└── nginx/
    └── automation.conf        # Automation service config
```

### **Port Configuration (SSOT)**

| Service                                                        | External Port | Internal Port | Status    |
| -------------------------------------------------------------- | ------------- | ------------- | --------- |
| `tools/utilities/tools/utilities/nexus-frontend-main`          | 2000          | 2000          | ✅ Active |
| `tools/utilities/tools/utilities/nexus-frontend-glassmorphism` | 2100          | 2100          | ✅ Active |
| `tools/utilities/tools/utilities/nexus-frontend-cyberpunk`     | 2200          | 2200          | ✅ Active |
| `tools/utilities/tools/utilities/nexus-frontend-modern`        | 2300          | 2300          | ✅ Active |
| `tools/utilities/tools/utilities/nexus-monitoring`             | 3500          | 3500          | ✅ Active |
| `tools/utilities/tools/utilities/nexus-data`                   | 3800          | 3800          | ✅ Active |
| `tools/utilities/tools/utilities/nexus-gateway`                | 80, 443       | 80, 443       | ✅ Active |
| `tools/utilities/tools/utilities/nexus-automation`             | 4000          | 80            | ✅ Active |

---

## ☸️ **Kubernetes SSOT**

### **Primary Configuration**

- **Directory**: `k8s/tools/utilities/tools/utilities/nexus-nexus_frontend/`
- **SSOT Copy**: `.tools/utilities/tools/utilities/nexus/ssot/k8s-frontend-ssot/`
- **Purpose**: Active frontend Kubernetes manifests

### **Kubernetes Structure (Active)**

```
k8s/tools/utilities/tools/utilities/nexus-nexus_frontend/
├── namespace.yaml              # Frontend namespace
├── configmap.yaml             # Configuration
├── deployment-main.yaml        # Main frontend deployment
├── deployment-glassmorphism.yaml # Glassmorphism deployment
├── deployment-cyberpunk.yaml   # Cyberpunk deployment
├── deployment-modern.yaml      # Modern deployment
├── service-main.yaml          # Main frontend service
├── service-glassmorphism.yaml # Glassmorphism service
├── service-cyberpunk.yaml     # Cyberpunk service
├── service-modern.yaml        # Modern service
├── ingress.yaml               # Ingress configuration
└── kustomization.yaml         # Kustomize configuration
```

### **Resource Allocation (SSOT)**

- **Namespace**: `tools/utilities/tools/utilities/nexus-frontend`
- **Replicas**: 1 per theme (4 total)
- **CPU Request**: 100m per pod
- **Memory Request**: 128Mi per pod
- **CPU Limit**: 500m per pod
- **Memory Limit**: 512Mi per pod

---

## 📦 **Archived Files**

### **Archived Location**

- **Directory**: `archived/docker_kubernetes_ssot_20250914_055100/`
- **Purpose**: Non-SSOT Docker and Kubernetes files

### **Archived Contents**

```
archived/docker_kubernetes_ssot_20250914_055100/
├── optimized-tools/utilities/tools/utilities/nexus-platform.yaml  # Legacy K8s config
├── k8s-unified/                   # Unified K8s manifests
├── k8s-base/                      # Base K8s configs
├── k8s-gateway/                   # Gateway K8s configs
├── k8s-infrastructure/            # Infrastructure K8s
├── k8s-istio/                     # Istio service mesh
├── k8s-monitoring/                # Monitoring K8s
├── k8s-overlays/                  # Kustomize overlays
├── k8s-services/                  # Service K8s configs
├── api-unified.Dockerfile         # Legacy API Dockerfile
├── web-launcher.Dockerfile        # Legacy web launcher
└── infrastructure/docker/docker-compose.simple.yml      # Legacy simple compose
```

---

## 🔄 **SSOT Maintenance**

### **Update Process**

1. **Modify**: Edit files in root directories (`infrastructure/docker/docker-compose.yml`, `k8s/tools/utilities/tools/utilities/nexus-nexus_frontend/`)
2. **Sync**: Copy changes to `.tools/utilities/tools/utilities/nexus/ssot/` directory
3. **Document**: Update this SSOT structure document
4. **Test**: Verify configurations work correctly

### **Version Control**

- **SSOT Files**: Always kept in sync with active files
- **Archived Files**: Moved to `archived/` when no longer needed
- **Backup**: SSOT copies serve as backup references

---

## 🚀 **Deployment Commands**

### **Docker Deployment**

```bash
# Deploy using SSOT
docker compose up -d

# Verify deployment
docker compose ps
docker compose logs tools/utilities/tools/utilities/nexus-frontend-main
```

### **Kubernetes Deployment**

```bash
# Deploy using SSOT
kubectl apply -k k8s/tools/utilities/tools/utilities/nexus-nexus_frontend/

# Verify deployment
kubectl get pods -n tools/utilities/tools/utilities/nexus-frontend
kubectl get services -n tools/utilities/tools/utilities/nexus-frontend
```

---

## ✅ **SSOT Validation**

### **Docker Validation**

- [x] Single port per service
- [x] Health checks configured
- [x] Environment variables aligned
- [x] All 4 frontend themes working

### **Kubernetes Validation**

- [x] 4 frontend deployments active
- [x] Services configured correctly
- [x] Ingress routing working
- [x] Resource limits applied

---

## 📊 **Current Status**

- **Docker**: ✅ 8 services, 8 unique ports
- **Kubernetes**: ✅ 4 frontend deployments active
- **Archived**: ✅ 10+ legacy configurations moved
- **SSOT**: ✅ Established and documented

---

**Last Updated**: September 14, 2025
**Maintainer**: Nexus Platform Team
**Status**: ✅ ACTIVE AND VERIFIED

---

## Section 2: SSOT_DOCKER_K8S_STRUCTURE.md

# 🎯 SSOT (Single Source of Truth) - Docker & Kubernetes Structure

**Created:** September 14, 2025
**Status:** ✅ ACTIVE

## 📋 SSOT Overview

This document defines the Single Source of Truth (SSOT) for all Docker and Kubernetes configurations in the Nexus Platform.

---

## 🐳 **Docker SSOT**

### **Primary Configuration**

- **File**: `infrastructure/docker/docker-compose.yml` (Root directory)
- **SSOT Copy**: `.tools/utilities/tools/utilities/nexus/ssot/docker-compose.ssot.yml`
- **Purpose**: Main production Docker Compose configuration

### **Dockerfiles (Active)**

```
infrastructure/infrastructure/infrastructure/docker/
├── ui-main.Dockerfile          # Main frontend (Port 2000)
├── ui-glassmorphism.Dockerfile # Glassmorphism theme (Port 2100)
├── ui-cyberpunk.Dockerfile     # Cyberpunk theme (Port 2200)
├── ui-modern.Dockerfile        # Modern theme (Port 2300)
├── ui.Dockerfile              # Legacy (archived)
├── nginx-ui.conf              # Nginx configuration
└── nginx/
    └── automation.conf        # Automation service config
```

### **Port Configuration (SSOT)**

| Service                                                        | External Port | Internal Port | Status    |
| -------------------------------------------------------------- | ------------- | ------------- | --------- |
| `tools/utilities/tools/utilities/nexus-frontend-main`          | 2000          | 2000          | ✅ Active |
| `tools/utilities/tools/utilities/nexus-frontend-glassmorphism` | 2100          | 2100          | ✅ Active |
| `tools/utilities/tools/utilities/nexus-frontend-cyberpunk`     | 2200          | 2200          | ✅ Active |
| `tools/utilities/tools/utilities/nexus-frontend-modern`        | 2300          | 2300          | ✅ Active |
| `tools/utilities/tools/utilities/nexus-monitoring`             | 3500          | 3500          | ✅ Active |
| `tools/utilities/tools/utilities/nexus-data`                   | 3800          | 3800          | ✅ Active |
| `tools/utilities/tools/utilities/nexus-gateway`                | 80, 443       | 80, 443       | ✅ Active |
| `tools/utilities/tools/utilities/nexus-automation`             | 4000          | 80            | ✅ Active |

---

## ☸️ **Kubernetes SSOT**

### **Primary Configuration**

- **Directory**: `k8s/tools/utilities/tools/utilities/nexus-nexus_frontend/`
- **SSOT Copy**: `.tools/utilities/tools/utilities/nexus/ssot/k8s-frontend-ssot/`
- **Purpose**: Active frontend Kubernetes manifests

### **Kubernetes Structure (Active)**

```
k8s/tools/utilities/tools/utilities/nexus-nexus_frontend/
├── namespace.yaml              # Frontend namespace
├── configmap.yaml             # Configuration
├── deployment-main.yaml        # Main frontend deployment
├── deployment-glassmorphism.yaml # Glassmorphism deployment
├── deployment-cyberpunk.yaml   # Cyberpunk deployment
├── deployment-modern.yaml      # Modern deployment
├── service-main.yaml          # Main frontend service
├── service-glassmorphism.yaml # Glassmorphism service
├── service-cyberpunk.yaml     # Cyberpunk service
├── service-modern.yaml        # Modern service
├── ingress.yaml               # Ingress configuration
└── kustomization.yaml         # Kustomize configuration
```

### **Resource Allocation (SSOT)**

- **Namespace**: `tools/utilities/tools/utilities/nexus-frontend`
- **Replicas**: 1 per theme (4 total)
- **CPU Request**: 100m per pod
- **Memory Request**: 128Mi per pod
- **CPU Limit**: 500m per pod
- **Memory Limit**: 512Mi per pod

---

## 📦 **Archived Files**

### **Archived Location**

- **Directory**: `archived/docker_kubernetes_ssot_20250914_055100/`
- **Purpose**: Non-SSOT Docker and Kubernetes files

### **Archived Contents**

```
archived/docker_kubernetes_ssot_20250914_055100/
├── optimized-tools/utilities/tools/utilities/nexus-platform.yaml  # Legacy K8s config
├── k8s-unified/                   # Unified K8s manifests
├── k8s-base/                      # Base K8s configs
├── k8s-gateway/                   # Gateway K8s configs
├── k8s-infrastructure/            # Infrastructure K8s
├── k8s-istio/                     # Istio service mesh
├── k8s-monitoring/                # Monitoring K8s
├── k8s-overlays/                  # Kustomize overlays
├── k8s-services/                  # Service K8s configs
├── api-unified.Dockerfile         # Legacy API Dockerfile
├── web-launcher.Dockerfile        # Legacy web launcher
└── infrastructure/docker/docker-compose.simple.yml      # Legacy simple compose
```

---

## 🔄 **SSOT Maintenance**

### **Update Process**

1. **Modify**: Edit files in root directories (`infrastructure/docker/docker-compose.yml`, `k8s/tools/utilities/tools/utilities/nexus-nexus_frontend/`)
2. **Sync**: Copy changes to `.tools/utilities/tools/utilities/nexus/ssot/` directory
3. **Document**: Update this SSOT structure document
4. **Test**: Verify configurations work correctly

### **Version Control**

- **SSOT Files**: Always kept in sync with active files
- **Archived Files**: Moved to `archived/` when no longer needed
- **Backup**: SSOT copies serve as backup references

---

## 🚀 **Deployment Commands**

### **Docker Deployment**

```bash
# Deploy using SSOT
docker compose up -d

# Verify deployment
docker compose ps
docker compose logs tools/utilities/tools/utilities/nexus-frontend-main
```

### **Kubernetes Deployment**

```bash
# Deploy using SSOT
kubectl apply -k k8s/tools/utilities/tools/utilities/nexus-nexus_frontend/

# Verify deployment
kubectl get pods -n tools/utilities/tools/utilities/nexus-frontend
kubectl get services -n tools/utilities/tools/utilities/nexus-frontend
```

---

## ✅ **SSOT Validation**

### **Docker Validation**

- [x] Single port per service
- [x] Health checks configured
- [x] Environment variables aligned
- [x] All 4 frontend themes working

### **Kubernetes Validation**

- [x] 4 frontend deployments active
- [x] Services configured correctly
- [x] Ingress routing working
- [x] Resource limits applied

---

## 📊 **Current Status**

- **Docker**: ✅ 8 services, 8 unique ports
- **Kubernetes**: ✅ 4 frontend deployments active
- **Archived**: ✅ 10+ legacy configurations moved
- **SSOT**: ✅ Established and documented

---

**Last Updated**: September 14, 2025
**Maintainer**: Nexus Platform Team
**Status**: ✅ ACTIVE AND VERIFIED

---
