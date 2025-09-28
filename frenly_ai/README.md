# Frenly AI - NEXUS Platform Automation System

## 🚀 Overview

Frenly AI is the intelligent automation system for the NEXUS Platform, serving as the master SSOT (Single Source of Truth) operator. It provides comprehensive automation capabilities including SSOT management, CI/CD orchestration, monitoring, and security compliance.

## 🏗️ Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Frenly AI System                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │  SSOT Operator  │  │ SSOT Integration│  │ Monitoring  │  │
│  │                 │  │     Layer       │  │   System    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │  CI/CD Pipeline │  │ Security &      │  │ Orchestrator│  │
│  │                 │  │ Compliance      │  │             │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

- **🤖 Intelligent SSOT Operations**: Context-aware query engine and change management
- **🔄 Automated CI/CD**: Comprehensive pipeline with SSOT validation
- **📊 Real-time Monitoring**: Advanced observability with SSOT-specific metrics
- **🔒 Security & Compliance**: Automated security scanning and compliance checking
- **⚡ High Performance**: Optimized caching and connection pooling
- **🛡️ Fault Tolerance**: Robust error handling and auto-healing capabilities

## 📁 Project Structure

```
frenly_ai/
├── backend/
│   ├── ssot_operator.py          # Core SSOT operator
│   ├── ssot_integration.py       # SSOT integration layer
│   ├── cicd_pipeline.py          # CI/CD pipeline automation
│   ├── monitoring.py             # Monitoring and observability
│   ├── security_compliance.py    # Security and compliance
│   ├── frenly_ai_orchestrator.py # Main orchestrator
│   └── requirements.txt          # Python dependencies
├── tests/
│   ├── test_ssot_operator.py     # SSOT operator tests
│   ├── test_ssot_integration.py  # Integration layer tests
│   └── test_*.py                 # Additional test files
├── docker/
│   ├── Dockerfile.operator       # SSOT operator container
│   ├── Dockerfile.integration    # Integration layer container
│   ├── Dockerfile.monitoring     # Monitoring system container
│   └── Dockerfile.security       # Security system container
├── k8s/
│   └── frenly-ai-deployment.yaml # Kubernetes deployment
└── README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional)
- Kubernetes (optional)
- Redis (for caching)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/nexus-platform/frenly-ai.git
   cd frenly-ai
   ```

2. **Install dependencies**

   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run tests**
   ```bash
   pytest tests/ -v
   ```

### Docker Deployment

1. **Build images**

   ```bash
   docker build -f docker/Dockerfile.operator -t frenly-ai-operator .
   docker build -f docker/Dockerfile.integration -t frenly-ai-integration .
   docker build -f docker/Dockerfile.monitoring -t frenly-ai-monitoring .
   docker build -f docker/Dockerfile.security -t frenly-ai-security .
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

### Kubernetes Deployment

1. **Apply Kubernetes manifests**

   ```bash
   kubectl apply -f k8s/frenly-ai-deployment.yaml
   ```

2. **Verify deployment**
   ```bash
   kubectl get pods -n frenly-ai
   kubectl get services -n frenly-ai
   ```

## 📖 Usage

### Basic SSOT Operations

```python
from frenly_ai.backend.ssot_operator import FrenlyAISSOTOperator, SSOTQuery, QueryType
from datetime import datetime, timezone

# Initialize operator
operator = FrenlyAISSOTOperator(
    ssot_registry_url="http://ssot-registry:8000",
    api_key="your-api-key"
)

# Query SSOT
query = SSOTQuery(
    query_type=QueryType.GET_ANCHOR,
    context="frenly_ai",
    parameters={"anchor_id": "user_management"},
    timestamp=datetime.now(timezone.utc),
    requester="user@example.com"
)

response = await operator.query_ssot(query)
if response.success:
    print(f"Anchor data: {response.data}")
```

### Change Proposals

```python
from frenly_ai.backend.ssot_operator import ChangeType

# Propose alias change
response = await operator.propose_change(
    change_type=ChangeType.UPDATE_ALIAS,
    target="user_mgmt",
    changes={"canonical_name": "user_management"},
    context="frenly_ai",
    description="Standardize alias naming",
    justification="Consistent naming convention"
)
```

### Monitoring

```python
from frenly_ai.backend.monitoring import MonitoringSystem

# Initialize monitoring
monitoring = MonitoringSystem({
    "collection_interval": 10,
    "alert_rules": []
})

# Start monitoring
await monitoring.start()

# Get health status
health = monitoring.get_health_status()
print(f"System health: {health['status']}")
```

## 🔧 Configuration

### Environment Variables

| Variable               | Description                  | Default                  |
| ---------------------- | ---------------------------- | ------------------------ |
| `SSOT_REGISTRY_URL`    | SSOT registry URL            | `http://localhost:8000`  |
| `SSOT_API_KEY`         | API key for SSOT access      | Required                 |
| `REDIS_URL`            | Redis connection URL         | `redis://localhost:6379` |
| `LOG_LEVEL`            | Logging level                | `INFO`                   |
| `CACHE_TTL`            | Cache time-to-live (seconds) | `300`                    |
| `MAX_RETRIES`          | Maximum retry attempts       | `3`                      |
| `CONNECTION_POOL_SIZE` | HTTP connection pool size    | `100`                    |

### Configuration Files

- **`config.yaml`**: Main configuration file
- **`pipeline-config.yaml`**: CI/CD pipeline configuration
- **`monitoring-config.yaml`**: Monitoring configuration
- **`security-policies.yaml`**: Security policies

## 📊 Monitoring

### Health Endpoints

- `GET /health`: Overall system health
- `GET /ready`: Readiness check
- `GET /metrics`: Prometheus metrics

### Key Metrics

- `frenly_ai_operations_total`: Total operations count
- `frenly_ai_operation_duration_seconds`: Operation duration
- `frenly_ai_cache_hits_total`: Cache hit count
- `frenly_ai_errors_total`: Error count by type
- `ssot_anchors_total`: Total SSOT anchors
- `ssot_aliases_total`: Total SSOT aliases

### Dashboards

- **Grafana Dashboard**: Comprehensive system overview
- **Prometheus Metrics**: Detailed metrics collection
- **Alert Manager**: Intelligent alerting system

## 🔒 Security

### Security Features

- **API Key Authentication**: Secure API access
- **Role-Based Access Control**: Fine-grained permissions
- **Audit Logging**: Complete operation audit trail
- **Encryption**: Data encryption in transit and at rest
- **Vulnerability Scanning**: Automated security scanning
- **Compliance Checking**: Regulatory compliance validation

### Security Scanning

- **Bandit**: Python security linter
- **Safety**: Dependency vulnerability scanner
- **Semgrep**: Static analysis security scanner
- **Container Scanning**: Image security analysis

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=frenly_ai.backend --cov-report=html

# Run specific test file
pytest tests/test_ssot_operator.py -v

# Run specific test
pytest tests/test_ssot_operator.py::TestFrenlyAISSOTOperator::test_query_ssot_success -v
```

### Test Coverage

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end testing
- **Performance Tests**: Load and stress testing
- **Security Tests**: Security vulnerability testing

## 🚀 CI/CD Pipeline

### Pipeline Features

- **SSOT Validation**: Automated SSOT manifest validation
- **Security Scanning**: Comprehensive security checks
- **Automated Testing**: Full test suite execution
- **Container Building**: Multi-platform image builds
- **Kubernetes Deployment**: Automated deployment
- **Monitoring Setup**: Observability configuration

### Pipeline Triggers

- **Push Events**: Automatic on code changes
- **Pull Requests**: Validation on PRs
- **Scheduled Runs**: Daily maintenance
- **Manual Dispatch**: On-demand execution

## 📈 Performance

### Performance Targets

- **Query Response Time**: < 100ms
- **Alias Resolution**: < 50ms
- **Change Proposal**: < 200ms
- **Cache Hit Rate**: > 80%
- **Uptime**: > 99.9%

### Optimization Features

- **Connection Pooling**: HTTP connection reuse
- **Intelligent Caching**: Multi-level caching strategy
- **Async Operations**: Non-blocking I/O
- **Resource Management**: Efficient resource utilization

## 🛠️ Development

### Development Setup

1. **Fork the repository**
2. **Create feature branch**
3. **Install development dependencies**
   ```bash
   pip install -r backend/requirements.txt
   pip install -r requirements-dev.txt
   ```
4. **Run pre-commit hooks**
   ```bash
   pre-commit install
   ```

### Code Style

- **PEP 8**: Python code style guidelines
- **Type Hints**: Comprehensive type annotations
- **Docstrings**: Detailed documentation
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting

### Contributing

1. **Fork the repository**
2. **Create feature branch**
3. **Make changes with tests**
4. **Submit pull request**
5. **Address review feedback**

## 📚 Documentation

### API Documentation

- **SSOT Operator API**: [docs/frenly_ai/ssot_operator.md](docs/frenly_ai/ssot_operator.md)
- **CI/CD Pipeline**: [docs/automation/ci_cd_pipeline.md](docs/automation/ci_cd_pipeline.md)
- **Monitoring Guide**: [docs/monitoring/ssot_metrics.md](docs/monitoring/ssot_metrics.md)

### Additional Resources

- **Architecture Overview**: [docs/architecture.md](docs/architecture.md)
- **Deployment Guide**: [docs/deployment.md](docs/deployment.md)
- **Troubleshooting**: [docs/troubleshooting.md](docs/troubleshooting.md)

## 🐛 Troubleshooting

### Common Issues

1. **Connection Timeouts**
   - Check network connectivity
   - Verify SSOT registry URL
   - Increase timeout values

2. **Authentication Failures**
   - Verify API key validity
   - Check permission levels
   - Review context mappings

3. **Cache Issues**
   - Clear cache if stale data
   - Check Redis connectivity
   - Verify TTL settings

4. **Performance Issues**
   - Monitor cache hit rates
   - Check connection pool usage
   - Review query patterns

### Debug Commands

```bash
# Check system health
curl http://localhost:8000/health

# Check readiness
curl http://localhost:8000/ready

# Get metrics
curl http://localhost:8000/metrics

# Check logs
kubectl logs -f deployment/frenly-ai-operator -n frenly-ai
```

## 📞 Support

### Getting Help

- **Documentation**: Comprehensive guides and API docs
- **Issues**: GitHub issue tracker
- **Discussions**: GitHub discussions
- **Community**: Open source community

### Contact Information

- **Development Team**: dev-team@nexus-platform.com
- **Platform Team**: platform-team@nexus-platform.com
- **Security Team**: security-team@nexus-platform.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **NEXUS Platform Team**: Core platform development
- **Open Source Community**: Contributing libraries and tools
- **Contributors**: All code contributors and reviewers

---

**Ready to get started? Check out the [Quick Start Guide](#-quick-start) and [API Documentation](docs/frenly_ai/ssot_operator.md)!** 🚀
