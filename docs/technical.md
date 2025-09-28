# NEXUS SSOT Technical Documentation

This document provides comprehensive technical documentation for the NEXUS Single Source of Truth (SSOT) system, including architecture, APIs, deployment, and maintenance.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [API Reference](#api-reference)
4. [Database Schema](#database-schema)
5. [Deployment Guide](#deployment-guide)
6. [Configuration](#configuration)
7. [Security](#security)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Troubleshooting](#troubleshooting)
10. [Development Guide](#development-guide)

## System Overview

The NEXUS SSOT system provides a centralized registry for API aliases, ensuring consistency and governance across different contexts (frontend, backend, system).

### Key Features

- **Dynamic Alias Resolution**: Resolve aliases to canonical endpoints in real-time
- **Multi-Context Support**: Different aliases for different contexts
- **Audit Logging**: Comprehensive logging of all operations
- **Conflict Detection**: Automatic detection and resolution of alias conflicts
- **Governance Rules**: Configurable rules for alias management
- **High Availability**: Scalable architecture with redundancy

### System Components

- **SSOT Registry Service**: Core service for alias management
- **Audit Service**: Handles logging and retention
- **Conflict Resolution Service**: Manages alias conflicts
- **API Gateway**: Provides RESTful interfaces
- **Database**: PostgreSQL for persistent storage
- **Monitoring**: Prometheus and Grafana for observability

## Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   System        │
│   Applications  │    │   Services      │    │   Components    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   SSOT Registry │
                    │   Service       │
                    └─────────────────┘
                             │
                    ┌─────────────────┐
                    │   Database      │
                    └─────────────────┘
```

### Component Details

#### SSOT Registry Service

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Key Modules**:
  - `backend/services/ssot_registry.py`: Core registry logic
  - `backend/services/conflict_resolution.py`: Conflict management
  - `backend/services/audit_retention.py`: Audit log management

#### Database Schema

- **Primary Tables**:
  - `aliases`: Stores alias definitions
  - `audit_logs`: Stores audit trail
  - `conflicts`: Tracks alias conflicts
  - `governance_rules`: Stores governance policies

#### API Gateway

- **Endpoints**:
  - `/api/aliases/resolve/{context}/{alias}`: Resolve alias
  - `/api/aliases/health`: Health check
  - `/api/aliases/metrics`: Monitoring metrics
  - `/api/aliases/status`: System status

## API Reference

### Base URL

```
http://localhost:8000/api/aliases
```

### Authentication

All API endpoints require authentication via Bearer token:

```
Authorization: Bearer <token>
```

### Endpoints

#### Resolve Alias

- **URL**: `/resolve/{context}/{alias}`
- **Method**: GET
- **Parameters**:
  - `context` (string): Context (frontend, backend, system)
  - `alias` (string): Alias name
- **Response**:
  ```json
  {
    "canonical_name": "https://api.nexus.com/v1/users/profile"
  }
  ```

#### Health Check

- **URL**: `/health`
- **Method**: GET
- **Response**:
  ```json
  {
    "status": "ok"
  }
  ```

#### Get Metrics

- **URL**: `/metrics`
- **Method**: GET
- **Response**:
  ```json
  {
    "metrics": {
      "total_aliases": 100,
      "active_aliases": 95,
      "response_time_ms": 50
    }
  }
  ```

#### Get Status

- **URL**: `/status`
- **Method**: GET
- **Response**:
  ```json
  {
    "status": {
      "service": "SSOT Registry",
      "version": "1.0.0",
      "health": "healthy"
    }
  }
  ```

## Database Schema

### Core Tables

#### aliases

```sql
CREATE TABLE aliases (
    id SERIAL PRIMARY KEY,
    alias VARCHAR(255) NOT NULL,
    canonical VARCHAR(500) NOT NULL,
    context VARCHAR(50) NOT NULL,
    description TEXT,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255)
);
```

#### audit_logs

```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    user VARCHAR(255) NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_archived BOOLEAN DEFAULT false,
    archived_at TIMESTAMP
);
```

#### conflicts

```sql
CREATE TABLE conflicts (
    id SERIAL PRIMARY KEY,
    alias VARCHAR(255) NOT NULL,
    context VARCHAR(50) NOT NULL,
    conflict_type VARCHAR(50) NOT NULL,
    resolution VARCHAR(100),
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes

```sql
CREATE INDEX idx_aliases_alias_context ON aliases(alias, context);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_conflicts_created_at ON conflicts(created_at);
```

## Deployment Guide

### Prerequisites

- Docker and Docker Compose
- Kubernetes (for production)
- PostgreSQL database
- Redis (for caching)

### Local Development

1. Clone the repository:

   ```bash
   git clone https://github.com/nexus/ssot.git
   cd ssot
   ```

2. Set up environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Start services:

   ```bash
   docker-compose up -d
   ```

4. Run migrations:
   ```bash
   docker-compose exec app alembic upgrade head
   ```

### Production Deployment

1. Build Docker images:

   ```bash
   docker build -t nexus-ssot .
   ```

2. Deploy to Kubernetes:

   ```bash
   kubectl apply -f k8s/
   ```

3. Configure ingress and load balancer

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/nexus_db

# API
API_HOST=0.0.0.0
API_PORT=8000

# Security
SECRET_KEY=your-secret-key
TOKEN_EXPIRATION=3600

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
```

### Configuration Files

- `config/environments.yaml`: Environment-specific settings
- `config/alias_governance.yaml`: Governance rules
- `config/logging.yaml`: Logging configuration

## Security

### Authentication

- JWT tokens for API access
- Role-based access control (RBAC)
- API key authentication for external services

### Authorization

- Context-based permissions
- Alias ownership validation
- Audit trail for all operations

### Encryption

- TLS/SSL for all communications
- Database encryption at rest
- Secure key management

### Best Practices

- Regular security audits
- Principle of least privilege
- Secure coding practices
- Regular dependency updates

## Monitoring and Logging

### Metrics

- Alias resolution times
- Error rates
- System resource usage
- Audit log volume

### Dashboards

- Grafana dashboards for real-time monitoring
- Prometheus for metrics collection
- ELK stack for log aggregation

### Alerting

- Configurable alert thresholds
- Email and webhook notifications
- Incident response procedures

## Troubleshooting

### Common Issues

#### Alias Not Found

- Check alias spelling and context
- Verify database connectivity
- Review audit logs for recent changes

#### Performance Issues

- Monitor database query performance
- Check system resource usage
- Review caching configuration

#### Authentication Failures

- Verify token validity
- Check user permissions
- Review security configuration

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python -m backend.services.ssot_registry
```

### Support

- Check logs in `logs/` directory
- Review monitoring dashboards
- Contact development team

## Development Guide

### Code Structure

```
backend/
├── services/           # Core business logic
├── routes/             # API endpoints
├── models/             # Database models
├── database/           # Database configuration
└── tests/              # Unit and integration tests

config/                 # Configuration files
docs/                   # Documentation
scripts/                # Utility scripts
```

### Testing

```bash
# Run unit tests
pytest backend/tests/

# Run integration tests
pytest backend/tests/ -m integration

# Run all tests
pytest
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Submit a pull request

### Code Style

- Follow PEP 8 for Python code
- Use type hints
- Write comprehensive docstrings
- Add unit tests for new features

## Appendices

### Glossary

- **Alias**: User-friendly name for an API endpoint
- **Canonical**: The actual endpoint URL
- **Context**: Scope of an alias (frontend, backend, system)
- **Governance**: Rules for alias management

### References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

### Version History

- **v1.0.0**: Initial release
- **v1.1.0**: Added conflict resolution
- **v1.2.0**: Enhanced monitoring

This documentation is maintained by the NEXUS development team and should be updated with each release.
