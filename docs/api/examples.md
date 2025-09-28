# API Registry Examples and Samples

This document provides examples and samples for using the NEXUS SSOT API Registry.

## Basic API Alias Creation

### Example 1: Creating a Simple Alias

```json
{
  "alias": "user-profile",
  "canonical": "https://api.nexus.com/v1/users/profile",
  "context": "frontend",
  "description": "Alias for user profile endpoint"
}
```

### Example 2: Temporary Alias with Expiration

```json
{
  "alias": "temp-login",
  "canonical": "https://api.nexus.com/v1/auth/login",
  "context": "backend",
  "expires_at": "2025-01-28T12:00:00Z",
  "description": "Temporary login alias for testing"
}
```

## Alias Resolution Examples

### Frontend Context Resolution

```python
from ssot_registry import resolve_alias

# Resolve alias in frontend context
endpoint = resolve_alias("user-profile", context="frontend")
print(endpoint)  # https://api.nexus.com/v1/users/profile
```

### Backend Context Resolution

```python
from ssot_registry import resolve_alias

# Resolve alias in backend context
endpoint = resolve_alias("user-profile", context="backend")
print(endpoint)  # https://internal-api.nexus.com/v1/users/profile
```

## Configuration Samples

### Sample Governance Configuration

```yaml
# config/alias_governance.yaml
rules:
  - name: "alias_uniqueness"
    description: "Ensure alias names are unique across contexts"
    enabled: true
  - name: "canonical_immutability"
    description: "Canonical endpoints cannot be changed"
    enabled: true
```

### Sample API Registry Data

```json
[
  {
    "id": "1",
    "alias": "product-list",
    "canonical": "https://api.nexus.com/v1/products",
    "context": "frontend",
    "created_at": "2025-01-27T10:00:00Z",
    "created_by": "admin"
  },
  {
    "id": "2",
    "alias": "product-list",
    "canonical": "https://internal-api.nexus.com/v1/products",
    "context": "backend",
    "created_at": "2025-01-27T10:00:00Z",
    "created_by": "admin"
  }
]
```

## Usage Patterns

### Pattern 1: Versioned APIs

```json
{
  "alias": "product-v1",
  "canonical": "https://api.nexus.com/v1/products",
  "context": "frontend",
  "version": "1.0"
}
```

### Pattern 2: Environment-Specific Aliases

```json
{
  "alias": "api-base",
  "canonical": "https://staging-api.nexus.com",
  "context": "staging",
  "environment": "staging"
}
```

## Best Practices

1. Use descriptive alias names that indicate the purpose
2. Always specify the context (frontend, backend, system)
3. Include expiration for temporary aliases
4. Document the purpose and usage of each alias
5. Follow naming conventions for consistency

## Troubleshooting

If you encounter issues with alias resolution:

1. Check the context parameter
2. Verify the alias exists in the registry
3. Ensure the canonical endpoint is accessible
4. Review audit logs for recent changes
