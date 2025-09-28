# Frenly AI SSOT Operator

## Overview

The Frenly AI SSOT Operator is the core component of the NEXUS Platform's automation system. It serves as the master SSOT (Single Source of Truth) operator, providing intelligent query capabilities, change proposal management, and audit trail generation.

## Architecture

### Core Components

1. **Query Engine**: Handles SSOT queries with context-aware alias resolution
2. **Change Proposal System**: Manages change proposals with human approval workflow
3. **Audit Trail**: Comprehensive logging of all operations
4. **Performance Monitoring**: Real-time metrics and health monitoring
5. **Caching Layer**: Optimized alias and query result caching

### Key Features

- **Context-Aware Operations**: Different behavior based on operation context
- **Alias Resolution**: Dynamic resolution of aliases to canonical names
- **Change Management**: Structured change proposal and approval process
- **Audit Logging**: Complete audit trail for compliance
- **Performance Optimization**: Caching and connection pooling
- **Health Monitoring**: Real-time health checks and metrics

## API Reference

### SSOTQuery

```python
@dataclass
class SSOTQuery:
    query_type: QueryType
    context: str
    parameters: Dict[str, Any]
    timestamp: datetime
    requester: str
```

### SSOTResponse

```python
@dataclass
class SSOTResponse:
    success: bool
    data: Any
    message: str
    timestamp: datetime
    operation_id: str
```

### Query Types

- `GET_ANCHOR`: Retrieve SSOT anchor information
- `LIST_ANCHORS`: List all available anchors
- `SEARCH_ANCHORS`: Search anchors by criteria
- `GET_ALIASES`: Get aliases for an anchor
- `RESOLVE_ALIAS`: Resolve alias to canonical name

### Change Types

- `CREATE_ALIAS`: Create new alias mapping
- `UPDATE_ALIAS`: Update existing alias
- `DELETE_ALIAS`: Remove alias mapping
- `UPDATE_ANCHOR`: Update anchor data
- `DELETE_ANCHOR`: Remove anchor

## Usage Examples

### Basic Query

```python
from frenly_ai.backend.ssot_operator import FrenlyAISSOTOperator, SSOTQuery, QueryType
from datetime import datetime, timezone

# Initialize operator
operator = FrenlyAISSOTOperator(
    ssot_registry_url="http://ssot-registry:8000",
    api_key="your-api-key"
)

# Create query
query = SSOTQuery(
    query_type=QueryType.GET_ANCHOR,
    context="frenly_ai",
    parameters={"anchor_id": "user_management"},
    timestamp=datetime.now(timezone.utc),
    requester="user@example.com"
)

# Execute query
response = await operator.query_ssot(query)
if response.success:
    print(f"Anchor data: {response.data}")
else:
    print(f"Query failed: {response.message}")
```

### Change Proposal

```python
from frenly_ai.backend.ssot_operator import ChangeType

# Propose alias change
response = await operator.propose_change(
    change_type=ChangeType.UPDATE_ALIAS,
    target="user_mgmt",
    changes={"canonical_name": "user_management"},
    context="frenly_ai",
    description="Standardize alias naming",
    justification="Consistent naming convention across platform"
)

if response.success:
    print(f"Proposal ID: {response.data['id']}")
    print(f"Status: {response.data['status']}")
```

### Health Check

```python
# Check system health
health_status = await operator.health_check()
print(f"System status: {health_status['status']}")
print(f"Components: {health_status['components']}")
```

## Configuration

### Environment Variables

- `SSOT_REGISTRY_URL`: URL of the SSOT registry
- `SSOT_API_KEY`: API key for SSOT registry access
- `REDIS_URL`: Redis connection URL for caching
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `CACHE_TTL`: Cache time-to-live in seconds (default: 300)
- `MAX_RETRIES`: Maximum retry attempts (default: 3)
- `CONNECTION_POOL_SIZE`: HTTP connection pool size (default: 100)

### Context Mappings

The operator uses context mappings to determine appropriate behavior:

```python
context_mappings = {
    "frenly_ai": "ai_operations",
    "system": "system_operations",
    "migration": "migration_operations"
}
```

## Performance Optimization

### Caching Strategy

- **Alias Cache**: Caches alias-to-canonical mappings
- **Query Cache**: Caches frequently accessed query results
- **TTL-based Expiration**: Automatic cache invalidation
- **LRU Eviction**: Least recently used cache eviction

### Connection Pooling

- **HTTP Connection Pool**: Reuses HTTP connections
- **Configurable Pool Size**: Adjustable based on load
- **Keep-Alive**: Maintains persistent connections
- **Timeout Management**: Configurable timeouts

## Monitoring and Metrics

### Health Endpoints

- `GET /health`: Overall system health
- `GET /ready`: Readiness check
- `GET /metrics`: Prometheus metrics

### Key Metrics

- `frenly_ai_operations_total`: Total operations count
- `frenly_ai_operation_duration_seconds`: Operation duration
- `frenly_ai_cache_hits_total`: Cache hit count
- `frenly_ai_cache_misses_total`: Cache miss count
- `frenly_ai_errors_total`: Error count by type

### Performance Targets

- Query response time: < 100ms
- Alias resolution: < 50ms
- Change proposal: < 200ms
- Cache hit rate: > 80%

## Error Handling

### Error Types

- `SSOTConnectionError`: Registry connection issues
- `SSOTValidationError`: Query validation failures
- `SSOTPermissionError`: Insufficient permissions
- `SSOTTimeoutError`: Operation timeouts
- `SSOTNotFoundError`: Resource not found

### Retry Logic

- **Exponential Backoff**: Increasing delay between retries
- **Max Retries**: Configurable retry limit
- **Circuit Breaker**: Prevents cascading failures
- **Dead Letter Queue**: Failed operations queuing

## Security Considerations

### Authentication

- **API Key Authentication**: Secure API key validation
- **JWT Tokens**: Optional JWT-based authentication
- **Role-Based Access**: Context-specific permissions

### Authorization

- **Operation-Level Permissions**: Fine-grained access control
- **Context-Based Access**: Different permissions per context
- **Audit Logging**: Complete operation audit trail

### Data Protection

- **Encryption in Transit**: TLS/SSL for all communications
- **Encryption at Rest**: Sensitive data encryption
- **PII Handling**: Personal data protection
- **Data Retention**: Configurable retention policies

## Troubleshooting

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

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Check Commands

```bash
# Check operator health
curl http://localhost:8000/health

# Check readiness
curl http://localhost:8000/ready

# Get metrics
curl http://localhost:8000/metrics
```

## Development

### Running Tests

```bash
# Run all tests
pytest frenly_ai/tests/test_ssot_operator.py -v

# Run with coverage
pytest frenly_ai/tests/test_ssot_operator.py --cov=frenly_ai.backend.ssot_operator

# Run specific test
pytest frenly_ai/tests/test_ssot_operator.py::TestFrenlyAISSOTOperator::test_query_ssot_success -v
```

### Local Development

```bash
# Install dependencies
pip install -r frenly_ai/backend/requirements.txt

# Run operator locally
python -m frenly_ai.backend.ssot_operator

# Run with debug mode
LOG_LEVEL=DEBUG python -m frenly_ai.backend.ssot_operator
```

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY frenly_ai/backend/requirements.txt .
RUN pip install -r requirements.txt

COPY frenly_ai/backend/ .
EXPOSE 8000

CMD ["python", "-m", "frenly_ai.backend.ssot_operator"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frenly-ai-operator
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frenly-ai-operator
  template:
    spec:
      containers:
        - name: operator
          image: nexus/frenly-ai-operator:latest
          ports:
            - containerPort: 8000
          env:
            - name: SSOT_REGISTRY_URL
              value: "http://ssot-registry:8000"
            - name: SSOT_API_KEY
              valueFrom:
                secretKeyRef:
                  name: ssot-secrets
                  key: api-key
```

## Contributing

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write comprehensive docstrings
- Include unit tests

### Pull Request Process

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request
5. Address review feedback

### Testing Requirements

- Unit test coverage > 90%
- Integration tests for all APIs
- Performance tests for critical paths
- Security tests for authentication

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Create an issue in the repository
- Contact the development team
- Check the troubleshooting guide
- Review the API documentation
