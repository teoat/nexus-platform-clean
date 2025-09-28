# NEXUS Platform

A comprehensive financial management platform with advanced SSOT (Single Source of Truth) architecture, Frenly AI integration, and automated deployment capabilities.

## 🚀 Features

### Core Platform

- **Financial Management**: Complete transaction tracking, budgeting, and reporting
- **User Management**: Secure authentication and user profiles
- **Real-time Monitoring**: Performance metrics and system health monitoring
- **AI Integration**: Frenly AI for intelligent automation and insights
- **API Registry**: Service discovery and integration management
- **Rate Limiting**: Advanced rate limiting with multiple strategies
- **Deployment Automation**: Blue-green deployment and rollback capabilities

### SSOT Architecture

- **Centralized Data Management**: Single source of truth for all platform data
- **Dynamic Aliasing**: Context-aware alias resolution system
- **Conflict Detection**: Automated conflict detection and resolution
- **Audit Logging**: Comprehensive audit trail with query capabilities
- **Data Validation**: Schema validation and integrity checks
- **Performance Optimization**: AI-powered database and system optimization

### Frenly AI Automation

- **SSOT Operator**: AI-powered SSOT management and optimization
- **Automated Workflows**: CI/CD pipeline with SSOT validation
- **Intelligent Monitoring**: AI-driven system monitoring and alerting
- **Security Automation**: Automated security scanning and compliance
- **Analytics Engine**: AI-powered analytics and insights
- **Cross-Service Integration**: Seamless integration between all services

## 🏗️ Architecture

### Backend Services

- **SSOT Registry**: Core SSOT management and alias resolution
- **API Integration**: Unified API registry for all services
- **Conflict Detection**: Advanced conflict detection and resolution
- **Audit Logging**: Comprehensive audit trail system
- **Frenly AI Services**: AI-powered automation and optimization

### Frontend

- **React Application**: Modern web interface
- **Real-time Updates**: WebSocket-based real-time data
- **Responsive Design**: Mobile and desktop optimized
- **Theme Support**: Light and dark mode themes

### Infrastructure

- **Docker**: Containerized deployment
- **Kubernetes**: Orchestrated container management
- **Monitoring**: Prometheus and Grafana integration
- **CI/CD**: GitHub Actions automation

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker
- Kubernetes (optional)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-org/nexus.git
   cd nexus
   ```

2. **Install dependencies**

   ```bash
   # Backend dependencies
   pip install -r backend/requirements.txt

   # Frontend dependencies
   cd frontend/web
   npm install
   cd ../..
   ```

3. **Configure environment**

   ```bash
   cp config/environments.yaml.example config/environments.yaml
   # Edit config/environments.yaml with your settings
   ```

4. **Start services**

   ```bash
   # Using Docker Compose
   docker-compose up -d

   # Or manually
   # Backend
   cd backend
   python main.py

   # Frontend
   cd frontend/web
   npm start
   ```

### Validation

Run the production validation script to ensure everything is properly configured:

```bash
python scripts/simple_validation.py
```

## 📁 Project Structure

```
nexus/
├── backend/                 # Backend services
│   ├── services/           # Core services
│   │   ├── ssot_registry.py
│   │   ├── conflict_detection.py
│   │   ├── audit_logging.py
│   │   └── api_registry_integration.py
│   └── routes/             # API routes
├── frontend/               # Frontend application
│   └── web/               # React web app
├── frenly_ai/             # Frenly AI automation
│   ├── backend/           # AI backend services
│   └── tests/             # AI tests
├── config/                # Configuration files
├── scripts/               # Utility scripts
├── k8s/                   # Kubernetes manifests
├── monitoring/            # Monitoring configuration
├── security/              # Security policies
└── docs/                  # Documentation
```

## 🔧 Configuration

### Environment Variables

- `NEXUS_ENV`: Environment (development, staging, production)
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection string
- `JWT_SECRET`: JWT signing secret

### SSOT Configuration

- `config/alias_governance.yaml`: Alias governance rules
- `config/caching.yaml`: Caching configuration
- `ssot_plan/`: SSOT planning and manifests

## 🔧 Development

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. To set up pre-commit:

```bash
pip install pre-commit
pre-commit install
```

Pre-commit will automatically run on every commit, checking for:

- Code formatting (Black, isort)
- Linting (Flake8)
- YAML/JSON validation
- Trailing whitespace and end-of-file fixes

### Continuous Auditing

Run automated audits to check system health:

```bash
python scripts/continuous_audit.py
```

This will generate an `audit_report.json` with results for:

- Python syntax
- Dependency conflicts
- YAML/JSON syntax
- Linting issues

### Scheduling Regular Audits

To schedule regular audits, add this to your crontab:

```bash
# Run audit weekly on Sundays at 2 AM
0 2 * * 0 python /path/to/nexus/scripts/continuous_audit.py
```

Or integrate into your CI/CD pipeline (already included in `.github/workflows/ci.yml`).

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend/web
npm test
```

### Code Quality

```bash
# Run linting
flake8 .

# Format code
black .
isort .
```

## 🚀 Deployment

### Docker Deployment

```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/unified-manifests.yaml

# Check deployment status
kubectl get pods -n nexus

# Access services
kubectl port-forward svc/nexus-frontend 3000:80
kubectl port-forward svc/nexus-backend 8000:80
```

### Production Deployment

```bash
# Run production deployment script
./scripts/deploy_production.sh

# Validate deployment
python scripts/validate_production_deployment.py
```

## 🔍 Monitoring

### Health Checks

- Backend: `http://localhost:8000/health`
- Frontend: `http://localhost:3000/health`
- Metrics: `http://localhost:8000/metrics`

### Monitoring Dashboards

- Grafana: `http://localhost:3001`
- Prometheus: `http://localhost:9090`

## 🤖 Frenly AI

### SSOT Operator

The Frenly AI SSOT Operator provides intelligent management of the Single Source of Truth:

```python
from frenly_ai.backend.ssot_operator import FrenlySSOTOperator

# Initialize operator
operator = FrenlySSOTOperator(
    ssot_registry_url="http://localhost:8000",
    api_key="your-api-key"
)

# Query SSOT
response = await operator.query_ssot(query)

# Propose changes
response = await operator.propose_change(
    change_type="update_alias",
    target="old_alias",
    changes={"new_alias": "canonical_name"}
)
```

### AI Integration

- **Automated Conflict Resolution**: AI-powered conflict detection and resolution
- **Intelligent Monitoring**: AI-driven system monitoring and alerting
- **Optimization**: AI-powered performance optimization
- **Security**: Automated security scanning and compliance

## 📊 API Documentation

### SSOT Registry API

- `GET /api/v1/ssot/anchors` - List all SSOT anchors
- `GET /api/v1/ssot/aliases` - List all aliases
- `POST /api/v1/ssot/aliases` - Create new alias
- `GET /api/v1/ssot/resolve/{alias}` - Resolve alias to canonical name

### Conflict Detection API

- `GET /api/v1/conflicts` - List all conflicts
- `POST /api/v1/conflicts/{id}/resolve` - Resolve conflict
- `GET /api/v1/conflicts/statistics` - Get conflict statistics

### Audit Logging API

- `GET /api/v1/audit/logs` - Query audit logs
- `GET /api/v1/audit/reports` - Generate audit reports
- `GET /api/v1/audit/statistics` - Get audit statistics

## 🧪 Testing

### Run Tests

```bash
# Backend tests
cd backend
python -m pytest tests/

# Frenly AI tests
cd frenly_ai
python -m pytest tests/

# Integration tests
python scripts/integrate_backend_services.py
```

### Validation

```bash
# System validation
python scripts/validate_system.py

# Production validation
python scripts/simple_validation.py
```

## 📚 Documentation

- [SSOT Operator Documentation](docs/frenly_ai/ssot_operator.md)
- [CI/CD Pipeline Documentation](docs/automation/ci_cd_pipeline.md)
- [Frenly AI README](frenly_ai/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and validation
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/nexus/issues)
- **Documentation**: [Project Wiki](https://github.com/your-org/nexus/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/nexus/discussions)

## 🎯 Roadmap

- [ ] Enhanced AI capabilities
- [ ] Multi-tenant support
- [ ] Advanced analytics
- [ ] Mobile applications
- [ ] API marketplace

---

**NEXUS Platform** - Empowering financial management with AI-driven automation and SSOT architecture.
