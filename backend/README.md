# NEXUS Platform - Backend

A robust, scalable backend infrastructure with unified services, NUC orchestration, and high-performance APIs.

## 🚀 Features

- **NUC Orchestrator**: Central service coordination and management
- **Service Registry**: Dynamic service discovery and registration
- **API Gateway**: Unified API entry point with routing, middleware, and load balancing
- **Unified Configuration**: Centralized configuration management
- **Database Normalization**: Optimized PostgreSQL schema with proper indexing
- **Circuit Breaker**: Fault tolerance and resilience patterns
- **Rate Limiting**: API protection and throttling
- **Caching**: Redis-based caching system
- **Monitoring**: Prometheus metrics and Grafana dashboards
- **Logging**: Structured logging with Elasticsearch and Kibana

## 📁 Project Structure

```
backend/
├── services/                 # Core services
│   ├── nuc_orchestrator.py  # NUC orchestration service
│   ├── service_registry.py  # Service discovery and registration
│   └── api_gateway.py       # API gateway with middleware
├── config/                  # Configuration management
│   └── unified_config.py    # Unified configuration system
├── database/                # Database layer
│   ├── schema_normalization.py  # Normalized database schema
│   └── init_nexus.sql       # Database initialization script
├── main.py                  # Main FastAPI application
├── start.py                 # Startup script
├── requirements.txt         # Python dependencies
├── config.yaml             # Configuration file
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Multi-service Docker setup
└── README.md               # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Local Development

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**

   ```bash
   # Start PostgreSQL
   # Create database and run init script
   psql -U postgres -f database/init_nexus.sql
   ```

6. **Start the application**
   ```bash
   python start.py
   ```

### Docker Deployment

1. **Build and start all services**

   ```bash
   docker-compose up -d
   ```

2. **View logs**

   ```bash
   docker-compose logs -f nexus-backend
   ```

3. **Stop services**
   ```bash
   docker-compose down
   ```

## 🔧 Configuration

Configuration is managed through the unified configuration system. Key configuration options:

### Server Configuration

- `host`: Server host (default: 0.0.0.0)
- `port`: Server port (default: 8000)
- `workers`: Number of worker processes (default: 1)
- `reload`: Enable auto-reload for development (default: false)

### Database Configuration

- `database_url`: PostgreSQL connection string
- `pool_size`: Connection pool size (default: 20)
- `max_overflow`: Maximum overflow connections (default: 30)

### Redis Configuration

- `redis_url`: Redis connection string
- `max_connections`: Maximum Redis connections (default: 20)

### Security Configuration

- `jwt_secret`: JWT signing secret
- `jwt_expiry`: JWT token expiry in seconds (default: 3600)
- `cors_origins`: Allowed CORS origins
- `trusted_hosts`: Trusted host patterns

## 📊 API Endpoints

### Health & Status

- `GET /health` - Health check
- `GET /status` - System status
- `GET /metrics` - System metrics

### Service Management

- `POST /services/register` - Register a service
- `DELETE /services/{service_name}` - Unregister a service
- `GET /services` - List all services
- `GET /services/{service_name}/health` - Check service health

### Service Discovery

- `GET /discover/{service_type}` - Discover services by type

### Configuration

- `GET /config` - Get configuration values
- `POST /config` - Set configuration values

### API Gateway

- `GET /gateway/routes` - Get API Gateway routes
- `POST /gateway/routes` - Add API Gateway route

## 🏗️ Architecture

### NUC Orchestrator

The NUC (Nexus Unified Core) Orchestrator provides:

- Service registration and discovery
- Health monitoring and circuit breaking
- Load balancing and failover
- Service metrics and performance tracking

### Service Registry

Dynamic service discovery system with:

- Service registration and heartbeat management
- Service type-based discovery
- Tag-based filtering
- Service dependency tracking

### API Gateway

Unified API entry point featuring:

- Request routing and proxying
- Middleware pipeline (CORS, logging, security, compression)
- Rate limiting and throttling
- Authentication and authorization
- Response caching
- Circuit breaker integration

### Database Schema

Normalized PostgreSQL schema with:

- Optimized indexes for performance
- Proper foreign key relationships
- JSONB support for flexible metadata
- Audit logging and soft deletes
- Database views for common queries

## 🔍 Monitoring

### Metrics

- Prometheus metrics endpoint at `/metrics`
- Service health and performance metrics
- Database connection and query metrics
- API request/response metrics

### Logging

- Structured JSON logging
- Elasticsearch integration for log aggregation
- Kibana dashboards for log analysis
- Request tracing and correlation IDs

### Health Checks

- Service-level health checks
- Database connectivity checks
- Redis connectivity checks
- External service dependency checks

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**

   ```bash
   export NEXUS_ENV=production
   export DATABASE_URL=postgresql://user:pass@host:port/db
   export REDIS_URL=redis://host:port/0
   ```

2. **Database Migration**

   ```bash
   alembic upgrade head
   ```

3. **Start Services**
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Docker Production

1. **Build production image**

   ```bash
   docker build -t nexus-backend:latest .
   ```

2. **Deploy with docker-compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## 🧪 Testing

### Run Tests

```bash
pytest tests/ -v
```

### Test Coverage

```bash
pytest --cov=backend tests/
```

### Load Testing

```bash
# Install locust
pip install locust

# Run load tests
locust -f tests/load_test.py --host=http://localhost:8000
```

## 📈 Performance

### Database Optimization

- Proper indexing strategy
- Query optimization
- Connection pooling
- Read replicas for scaling

### Caching Strategy

- Redis for session storage
- API response caching
- Database query result caching
- CDN integration for static assets

### Scaling

- Horizontal scaling with load balancers
- Database read replicas
- Redis clustering
- Microservice decomposition

## 🔒 Security

### Authentication

- JWT-based authentication
- Role-based access control (RBAC)
- OAuth2 integration support
- Multi-factor authentication (MFA)

### Authorization

- Resource-level permissions
- API endpoint protection
- Service-to-service authentication
- Audit logging

### Data Protection

- Encryption at rest and in transit
- PII data masking
- Secure configuration management
- Regular security audits

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the documentation
- Contact the development team

## 🔄 Changelog

### v1.0.0

- Initial release
- NUC Orchestrator implementation
- Service Registry
- API Gateway
- Unified Configuration
- Database normalization
- Docker support
- Monitoring and logging
