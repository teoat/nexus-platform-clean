# SSOT Registry Development Guide

## Overview

The SSOT (Single Source of Truth) Registry is the core component of the NEXUS alias management system. It provides centralized management of API anchors and their aliases with support for dynamic resolution, governance, and audit logging.

## Architecture

### Core Components

1. **SSOTRegistry**: Main registry class managing anchors and aliases
2. **AliasDefinition**: Data structure for alias definitions
3. **SSOTAnchor**: Data structure for anchor definitions
4. **AuditEntry**: Audit log entries for tracking changes

### Data Flow

```
Client Request → API Alias Router → SSOT Registry → Canonical Endpoint
                     ↓
                Performance Tracker
                     ↓
                Audit Logger
```

## Getting Started

### Installation

```bash
# Install dependencies
pip install fastapi uvicorn httpx pyyaml

# Set up environment
export PYTHONPATH="${PYTHONPATH}:/path/to/nexus/backend"
```

### Basic Usage

```python
from backend.services.ssot_registry import SSOTRegistry

# Create registry instance
registry = SSOTRegistry()

# Register an anchor
registry.register_anchor("user-api", {
    "family": "api",
    "description": "User management API",
    "format": "openapi-3.0.yaml",
    "version": "1.0.0",
    "location": "/api/v1/users",
    "metadata": {"team": "backend"},
    "tags": ["users", "authentication"]
})

# Add an alias
registry.add_alias("user-management", "user-api", "frontend", {
    "alias_type": "application",
    "description": "User management endpoint",
    "created_by": "developer",
    "metadata": {"team": "frontend"}
})

# Resolve alias
canonical = registry.resolve_alias("user-management", "frontend")
print(f"Resolved to: {canonical}")  # Output: user-api
```

## Core Classes

### SSOTRegistry

The main registry class that manages all anchors and aliases.

#### Key Methods

- `register_anchor(anchor_id, config)`: Register a new anchor
- `add_alias(alias, canonical, context, config)`: Add a new alias
- `resolve_alias(alias, context)`: Resolve alias to canonical name
- `remove_alias(alias, context, removed_by)`: Remove an alias
- `list_aliases(context=None)`: List all aliases
- `get_anchor(anchor_id)`: Get anchor by ID
- `get_metrics()`: Get registry metrics

#### Configuration

```python
# Registry configuration
config = {
    "backup": {
        "directory": "backups",
        "retention_days": 30,
        "compression": "gzip"
    },
    "monitoring": {
        "interval": 30,
        "retention_days": 7
    }
}

registry = SSOTRegistry("config/ssot_registry.json")
```

### AliasDefinition

Data structure representing an alias definition.

```python
from backend.services.ssot_registry import AliasDefinition, AliasType, AliasStatus

alias_def = AliasDefinition(
    alias="user-management",
    canonical="user-api",
    context="frontend",
    alias_type=AliasType.APPLICATION,
    description="User management endpoint",
    created_by="developer",
    created_at="2025-01-27T10:00:00Z",
    expires_at=None,
    status=AliasStatus.ACTIVE,
    metadata={"team": "frontend"},
    usage_count=0,
    last_used=None
)
```

### SSOTAnchor

Data structure representing an anchor definition.

```python
from backend.services.ssot_registry import SSOTAnchor

anchor = SSOTAnchor(
    id="user-api",
    family="api",
    description="User management API",
    format="openapi-3.0.yaml",
    version="1.0.0",
    location="/api/v1/users",
    created_at="2025-01-27T10:00:00Z",
    updated_at="2025-01-27T10:00:00Z",
    metadata={"team": "backend"},
    tags=["users", "authentication"],
    status="active"
)
```

## Governance Rules

### Naming Conventions

```yaml
# config/alias_governance.yaml
rules:
  naming:
    pattern: "^[a-z0-9-]+$"
    min_length: 3
    max_length: 50
    reserved_words:
      - "api"
      - "admin"
      - "system"
```

### Context Configuration

```yaml
contexts:
  frontend:
    permissions: ["frontend_team"]
    approval_required: false
    allowed_types: ["application", "api"]
    max_ttl: "1y"
  
  system:
    permissions: ["ssot_maintainers"]
    approval_required: true
    allowed_types: ["system", "api"]
    max_ttl: "unlimited"
```

## Adding New Anchors

### 1. Define Anchor Configuration

```python
anchor_config = {
    "family": "api",  # api, service, ai, etc.
    "description": "Clear description of the anchor",
    "format": "openapi-3.0.yaml",
    "version": "1.0.0",
    "location": "/api/v1/endpoint",
    "metadata": {
        "team": "backend",
        "priority": "high",
        "documentation": "https://docs.nexus.internal/api/users"
    },
    "tags": ["users", "authentication", "management"]
}
```

### 2. Register Anchor

```python
success = registry.register_anchor("user-api", anchor_config)
if success:
    print("Anchor registered successfully")
else:
    print("Failed to register anchor")
```

### 3. Verify Registration

```python
anchor = registry.get_anchor("user-api")
if anchor:
    print(f"Anchor: {anchor.id}")
    print(f"Family: {anchor.family}")
    print(f"Description: {anchor.description}")
```

## Creating Aliases

### 1. Define Alias Configuration

```python
alias_config = {
    "alias_type": "application",  # application, system, ai, etc.
    "description": "User management endpoint for frontend",
    "created_by": "developer",
    "metadata": {
        "team": "frontend",
        "project": "user-portal"
    },
    "ttl": "90d"  # Optional: time to live
}
```

### 2. Add Alias

```python
success = registry.add_alias(
    alias="user-management",
    canonical="user-api",
    context="frontend",
    config=alias_config
)

if success:
    print("Alias created successfully")
else:
    print("Failed to create alias")
```

### 3. Test Alias Resolution

```python
try:
    canonical = registry.resolve_alias("user-management", "frontend")
    print(f"Alias resolves to: {canonical}")
except KeyError as e:
    print(f"Alias not found: {e}")
except ValueError as e:
    print(f"Alias error: {e}")
```

## Error Handling

### Common Exceptions

```python
from backend.services.ssot_registry import ValidationError, AliasNotFoundError

try:
    canonical = registry.resolve_alias("invalid-alias", "frontend")
except KeyError:
    print("Alias not found")
except ValueError as e:
    print(f"Alias error: {e}")
except ValidationError as e:
    print(f"Validation error: {e}")
```

### Error Types

1. **KeyError**: Alias or context not found
2. **ValueError**: Alias expired or invalid status
3. **ValidationError**: Alias violates governance rules
4. **ConflictError**: Alias conflicts with existing alias

## Performance Optimization

### Caching

The registry implements automatic caching for alias resolutions:

```python
# Cache is automatically managed
# Check cache statistics
metrics = registry.get_metrics()
print(f"Cache hits: {metrics['cache_hits']}")
print(f"Cache misses: {metrics['cache_misses']}")
print(f"Cache size: {metrics['cache_size']}")
```

### Batch Operations

```python
# Register multiple anchors
anchors = [
    ("user-api", {"family": "api", "description": "User API"}),
    ("transaction-api", {"family": "api", "description": "Transaction API"}),
    ("frenly-ai-api", {"family": "ai", "description": "AI API"})
]

for anchor_id, config in anchors:
    registry.register_anchor(anchor_id, config)
```

## Monitoring and Metrics

### Registry Metrics

```python
metrics = registry.get_metrics()
print(f"Total anchors: {metrics['total_anchors']}")
print(f"Total aliases: {metrics['total_aliases']}")
print(f"Active aliases: {metrics['active_aliases']}")
print(f"Alias resolutions: {metrics['alias_resolutions']}")
print(f"Anchor registrations: {metrics['anchor_registrations']}")
```

### Performance Monitoring

```python
# Monitor response times
import time

start_time = time.time()
canonical = registry.resolve_alias("user-management", "frontend")
response_time = time.time() - start_time

print(f"Resolution time: {response_time:.3f}s")
```

## Testing

### Unit Tests

```python
import pytest
from backend.services.ssot_registry import SSOTRegistry

def test_register_anchor():
    registry = SSOTRegistry()
    config = {
        "family": "api",
        "description": "Test API",
        "format": "openapi-3.0.yaml",
        "version": "1.0.0",
        "location": "/api/v1/test"
    }
    
    result = registry.register_anchor("test-api", config)
    assert result == True
    assert "test-api" in registry.anchors

def test_resolve_alias():
    registry = SSOTRegistry()
    # Setup test data...
    
    canonical = registry.resolve_alias("test-alias", "frontend")
    assert canonical == "test-api"
```

### Integration Tests

```python
def test_full_workflow():
    registry = SSOTRegistry()
    
    # Register anchor
    registry.register_anchor("user-api", {...})
    
    # Add alias
    registry.add_alias("user-management", "user-api", "frontend", {...})
    
    # Resolve alias
    canonical = registry.resolve_alias("user-management", "frontend")
    assert canonical == "user-api"
```

## Best Practices

### 1. Naming Conventions

- Use kebab-case for aliases: `user-management`, `transaction-processing`
- Use descriptive names: `user-management` instead of `um`
- Avoid abbreviations: `user-management` instead of `usr-mgmt`

### 2. Context Organization

- Use logical contexts: `frontend`, `backend`, `mobile`, `ai`
- Group related aliases in the same context
- Avoid too many contexts (aim for 5-10)

### 3. Metadata Usage

- Include team information: `{"team": "frontend"}`
- Add project context: `{"project": "user-portal"}`
- Include documentation links: `{"docs": "https://..."}`

### 4. Error Handling

- Always handle KeyError and ValueError exceptions
- Implement proper logging for debugging
- Use try-catch blocks around alias resolution

### 5. Performance

- Monitor cache hit rates
- Use batch operations when possible
- Implement proper cleanup for expired aliases

## Troubleshooting

### Common Issues

1. **Alias not found**: Check context and alias name spelling
2. **Validation errors**: Verify alias follows naming conventions
3. **Performance issues**: Check cache configuration and metrics
4. **Permission errors**: Verify user has required permissions

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug logging for registry
registry = SSOTRegistry()
# Debug information will be logged
```

### Health Checks

```python
# Check registry health
metrics = registry.get_metrics()
if metrics['total_anchors'] == 0:
    print("Warning: No anchors registered")

if metrics['active_aliases'] == 0:
    print("Warning: No active aliases")
```

## Support

For additional help and support:

- **Documentation**: Check the API documentation
- **Issues**: Report issues in the project repository
- **Team**: Contact the NEXUS development team
- **Slack**: #nexus-ssot channel
