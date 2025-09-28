# NEXUS SSOT API Alias Management Documentation

This document provides comprehensive information on managing API aliases in the NEXUS Single Source of Truth (SSOT) system.

## Overview

API alias management allows you to create, update, delete, and resolve aliases for API endpoints across different contexts (frontend, backend, system). This ensures consistency and flexibility in API routing.

## Getting Started with Alias Management

This section guides users through the basic steps of managing aliases within the NEXUS SSOT system.

### Prerequisites
- Access to the NEXUS API Gateway.
- Necessary authentication credentials (if applicable).

### Basic Workflow
1.  **Understand Core Concepts**: Familiarize yourself with what aliases and contexts are.
2.  **Create Aliases**: Define new aliases for your API endpoints.
3.  **Resolve Aliases**: Use aliases in your applications to access canonical endpoints.
4.  **Monitor and Maintain**: Keep an eye on alias performance and health.

## Core Concepts

### Alias
An alias is a user-friendly name that maps to a canonical API endpoint.

### Context
Contexts define the scope of an alias:
- **frontend**: For client-side applications
- **backend**: For server-side services
- **system**: For internal system operations

### Canonical Endpoint
The actual URL that the alias resolves to. Canonical endpoints are immutable.

## API Endpoints

### Health Check
- **GET** `/api/aliases/health`
- Returns the health status of the alias registry.

### Resolve Alias
- **GET** `/api/aliases/resolve/{context}/{alias}`
- Resolves an alias to its canonical endpoint.

### Get Metrics
- **GET** `/api/aliases/metrics`
- Returns monitoring metrics for the alias registry.

### Get Status
- **GET** `/api/aliases/status`
- Returns detailed status information.

## Usage Examples

### Creating an Alias

```bash
curl -X POST http://localhost:8000/api/aliases \
  -H "Content-Type: application/json" \
  -d '{
    "alias": "user-profile",
    "canonical": "https://api.nexus.com/v1/users/profile",
    "context": "frontend",
    "description": "User profile endpoint",
    "expires_at": null
  }'
```

### Resolving an Alias

```bash
curl http://localhost:8000/api/aliases/resolve/frontend/user-profile
```

Response:
```json
{
  "canonical_name": "https://api.nexus.com/v1/users/profile"
}
```

### Updating an Alias

```bash
curl -X PUT http://localhost:8000/api/aliases/user-profile \
  -H "Content-Type: application/json" \
  -d '{
    "canonical": "https://new-api.nexus.com/v1/users/profile",
    "context": "frontend"
  }'
```

### Deleting an Alias

```bash
curl -X DELETE http://localhost:8000/api/aliases/user-profile
```

## Best Practices

### Naming Conventions
- Use descriptive, hyphen-separated names (e.g., `user-profile`, `product-list`)
- Avoid special characters and spaces
- Keep names consistent across contexts

### Context Usage
- Use `frontend` for public APIs
- Use `backend` for internal services
- Use `system` for administrative functions

### Expiration
- Set expiration dates for temporary aliases
- Use ISO 8601 format for dates (e.g., "2025-01-28T12:00:00Z")
- Monitor and clean up expired aliases regularly

### Security
- Validate all inputs
- Use HTTPS for all endpoints
- Implement rate limiting
- Log all alias operations
- Sensitive data is sanitized in audit logs
- Compliance checks are integrated into alias governance
- A penetration testing script (`scripts/run_penetration_test.sh`) is available for security assessments.

### Caching
- Redis caching is utilized for alias resolution and anchor retrieval.
- Cache TTL (Time-To-Live) is configurable via `config/caching.yaml`.
- This improves performance for frequently accessed aliases.

## Error Handling

### Common Errors

- **404 Not Found**: Alias does not exist in the specified context
- **400 Bad Request**: Invalid alias data or expired alias
- **500 Internal Server Error**: Server-side error

### Error Response Format

```json
{
  "detail": "Error description"
}
```

## Monitoring and Maintenance

### Metrics to Monitor
The SSOT Registry exposes Prometheus metrics on port `8002` at the `/metrics` endpoint. Key metrics include:

- `ssot_alias_creations_total`: Total number of SSOT alias creation attempts (labels: `status`, `context`).
- `ssot_alias_updates_total`: Total number of SSOT alias update attempts (labels: `status`, `context`).
- `ssot_alias_deactivations_total`: Total number of SSOT alias deactivation attempts (labels: `status`, `context`).
- `ssot_alias_resolutions_total`: Total number of SSOT alias resolution attempts (labels: `status`, `context`).
- `ssot_alias_resolution_duration_seconds`: Histogram of SSOT alias resolution durations (labels: `context`).
- `ssot_active_aliases_count`: Current number of active SSOT aliases (labels: `context`).
- `ssot_expired_aliases_count`: Current number of expired SSOT aliases (labels: `context`).
- `ssot_validation_failures_total`: Total number of SSOT validation failures (labels: `rule`, `operation`).
- `ssot_audit_log_entries_total`: Total number of audit log entries recorded for SSOT operations (labels: `action`).

### Maintenance Tasks
- **Regular Alias Review:** Periodically review all active aliases for accuracy, relevance, and compliance. Update or archive as necessary.
- **System Health Monitoring:** Continuously monitor SSOT Registry service health, performance metrics (CPU, memory, alias resolution times), and error rates using Prometheus and Grafana dashboards.
- **Audit Log Review:** Regularly review audit logs for any suspicious activities, unauthorized changes, or security events.
- **Backup and Recovery:** Ensure regular backups of the SSOT Registry configuration and data are performed and tested.
- **Security Audits:** Conduct periodic security audits and penetration tests (using `scripts/run_penetration_test.sh`) to identify and address vulnerabilities.
- **Dependency Management:** Keep all SSOT Registry dependencies up-to-date to mitigate security risks and leverage performance improvements.
- **Configuration Management:** Regularly review and update `config/alias_governance.yaml` and `config/caching.yaml` to reflect evolving requirements and best practices.

## Troubleshooting

### Alias Not Resolving
1. Check if the alias exists in the correct context.
2. Verify the canonical endpoint is accessible.
3. Review audit logs for recent changes (`ssot_audit_log_entries_total` metric).
4. Check the status of the SSOT Registry service and its dependencies.

### Performance Issues
1. Monitor `ssot_alias_resolution_duration_seconds` metric for latency spikes.
2. Verify Redis cache health and hit rate.
3. Check resource utilization (CPU, memory) of the SSOT Registry service.
4. Review `config/caching.yaml` for optimal cache TTL settings.

### Conflict Detection
1. Use the conflict detection service to identify duplicates.
2. Resolve conflicts using merge, override, or archive strategies.
3. Regularly run conflict reports.

### Metrics Not Appearing
1. Ensure the Prometheus metrics server is running on port `8002`.
2. Verify that the SSOT Registry service is correctly instrumented.
3. Check Prometheus configuration for correct scraping targets.

### Security Concerns
1. Review audit logs for unauthorized access attempts or suspicious activities.
2. Run the penetration testing script (`scripts/run_penetration_test.sh`) for basic vulnerability assessment.
3. Verify compliance checks are passing during alias creation/updates.

## Integration Examples

### Python Client

```python
import requests

def resolve_alias(context, alias):
    response = requests.get(f"http://localhost:8000/api/aliases/resolve/{context}/{alias}")
    if response.status_code == 200:
        return response.json()['canonical_name']
    else:
        raise Exception(f"Error resolving alias: {response.text}")

# Usage
endpoint = resolve_alias("frontend", "user-profile")
print(endpoint)
```

### JavaScript Client

```javascript
async function resolveAlias(context, alias) {
    const response = await fetch(`/api/aliases/resolve/${context}/${alias}`);
    if (response.ok) {
        const data = await response.json();
        return data.canonical_name;
    } else {
        throw new Error(`Error resolving alias: ${response.statusText}`);
    }
}

// Usage
const endpoint = await resolveAlias('frontend', 'user-profile');
console.log(endpoint);
```

## Governance

### Approval Process
- All alias changes require approval
- Use pull requests for modifications
- Implement automated validation

### Audit Logging
- All alias operations are logged
- Logs are retained for 7 years
- Regular audits are performed

### Compliance
- Ensure aliases comply with organizational standards
- Validate canonical endpoints
- Monitor for security vulnerabilities

## Support

For issues or questions:
- Check the troubleshooting guide
- Review audit logs
- Contact the platform team
- Create a support ticket

This documentation is maintained by the NEXUS platform team and should be updated as the system evolves.
