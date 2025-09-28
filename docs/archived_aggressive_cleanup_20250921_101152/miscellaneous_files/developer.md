**Status**: 🔒 **LOCKED** - SSOT Document
**Version**: 1.0
**Last Updated**: 2025-01-17
**Source**: Consolidated from original documentation

---

# Developer Guide - Nexus Platform Financial Examiner System

## Overview

This guide provides comprehensive information for developers working on the Nexus Platform Financial Examiner POV System.

## Development Environment Setup

### Prerequisites

- Python 3.8+
- Git
- PostgreSQL 12+
- Redis 6+
- IDE (VS Code, PyCharm, etc.)

### Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd Nexus

# Create virtual environment
python -m venv nexus_env
source nexus_env/bin/activate  # On Windows: nexus_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install
```

### IDE Configuration

#### VS Code

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./nexus_env/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests/"]
}
```

#### PyCharm

- Set Python interpreter to `nexus_env/bin/python`
- Enable code inspection
- Configure run configurations for main modules

## Project Structure

```
NEXUS_nexus_backend/
├── __init__.py                 # Package initialization
├── main.py                     # Main launcher
├── config.py                   # Configuration management
├── financial_examiner_system.py # Core POV system
├── frontend_themes.py          # Theme management
├── ssot_integration.py         # SSOT integration
├── system_health_monitor.py    # Health monitoring
├── README.md                   # Main documentation
├── API_REFERENCE.md           # API documentation
├── DEPLOYMENT_GUIDE.md        # Deployment guide
├── DEVELOPER_GUIDE.md         # This file
└── config.json                # Configuration file
```

## Architecture Overview

### Core Components

#### 1. Financial Examiner System

- **Purpose**: Core POV switching and financial data processing
- **Key Classes**: `FinancialExaminerSystem`, `ReconciliationEngine`, `FraudDetectionSystem`
- **Dependencies**: None (core system)

#### 2. Frontend Theme Manager

- **Purpose**: Manage 4 specialized frontend themes
- **Key Classes**: `FrontendThemeManager`
- **Dependencies**: None (standalone)

#### 3. SSOT Integration

- **Purpose**: Integrate with existing SSOT system
- **Key Classes**: `SSOTIntegration`
- **Dependencies**: File system access

#### 4. Configuration System

- **Purpose**: Centralized configuration management
- **Key Classes**: `NexusConfig`
- **Dependencies**: JSON file handling

### Data Flow

```
User Input → POV Selection → Data Processing → Reconciliation → Fraud Detection → Report Generation → Theme Application → Output
```

## Development Guidelines

### Code Style

#### Python Style Guide

- Follow PEP 8
- Use type hints
- Write docstrings for all functions and classes
- Use meaningful variable and function names

#### Example:

```python
async def process_financial_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process financial data through the current POV.

    Args:
        data: Dictionary containing financial data (expenses, bank_statements)

    Returns:
        Dictionary with processing results including reconciliation,
        fraud analysis, and POV-specific analysis

    Raises:
        ValueError: If data format is invalid
        ProcessingError: If processing fails
    """
    # Implementation here
```

### Error Handling

#### Exception Hierarchy

```python
class NexusError(Exception):
    """Base exception for Nexus platform"""
    pass

class ConfigurationError(NexusError):
    """Configuration-related errors"""
    pass

class ProcessingError(NexusError):
    """Data processing errors"""
    pass

class IntegrationError(NexusError):
    """Integration-related errors"""
    pass
```

#### Error Handling Pattern

```python
try:
    result = await some_operation()
    return result
except SpecificError as e:
    self.logger.error(f"Specific error occurred: {e}")
    raise ProcessingError(f"Failed to process data: {e}") from e
except Exception as e:
    self.logger.error(f"Unexpected error: {e}")
    raise NexusError(f"Unexpected error occurred: {e}") from e
```

### Logging

#### Logging Configuration

```python
import logging

# Setup logger
logger = logging.getLogger(__name__)

# Log levels
logger.debug("Detailed information for debugging")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error")
```

#### Logging Best Practices

- Use appropriate log levels
- Include context information
- Log before and after important operations
- Use structured logging for complex data

### Testing

#### Test Structure

```
tests/
├── __init__.py
├── test_financial_examiner_system.py
├── test_frontend_themes.py
├── test_ssot_integration.py
├── test_config.py
└── fixtures/
    ├── sample_data.json
    └── test_config.json
```

#### Test Example

```python
import pytest
from unittest.mock import Mock, patch
from NEXUS_app.financial_examiner_system import FinancialExaminerSystem, POVRole

class TestFinancialExaminerSystem:
    def setup_method(self):
        self.system = FinancialExaminerSystem("/tmp/test_workspace")

    @pytest.mark.asyncio
    async def test_switch_pov_success(self):
        """Test successful POV switching"""
        result = await self.system.switch_pov(POVRole.PROSECUTOR)
        assert result is True
        assert self.system.current_pov == POVRole.PROSECUTOR

    @pytest.mark.asyncio
    async def test_switch_pov_failure(self):
        """Test POV switching failure"""
        with patch.object(self.system, 'current_pov', side_effect=Exception("Test error")):
            result = await self.system.switch_pov(POVRole.PROSECUTOR)
            assert result is False
```

#### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_financial_examiner_system.py

# Run with coverage
pytest --cov=NEXUS_app

# Run with verbose output
pytest -v
```

### Documentation

#### Docstring Format

```python
def function_name(param1: str, param2: int = 10) -> bool:
    """
    Brief description of the function.

    Longer description if needed, explaining the purpose,
    behavior, and any important details.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 10)

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is invalid
        RuntimeError: When operation fails

    Example:
        >>> result = function_name("test", 5)
        >>> print(result)
        True
    """
```

#### Code Comments

```python
# Single line comment explaining the next line
result = complex_calculation()

# Multi-line comment for complex logic
# This section handles the reconciliation of expenses
# with bank statements using fuzzy matching algorithm
# to account for minor discrepancies in amounts and dates
matched_transactions = await self._fuzzy_match(expenses, bank_statements)
```

## Adding New Features

### 1. POV Roles

#### Adding a New POV Role

```python
# In financial_examiner_system.py
class POVRole(Enum):
    # ... existing roles ...
    NEW_ROLE = "new_role"

# Add POV-specific analysis
async def _generate_pov_analysis(self, data, reconciliation, fraud):
    # ... existing code ...
    elif self.current_pov == POVRole.NEW_ROLE:
        return {
            'focus': 'New role specific focus',
            'priority': 'New role priority',
            'recommendations': ['New role recommendation']
        }
```

### 2. Frontend Themes

#### Adding a New Theme

```python
# In frontend_themes.py
class ThemeType(Enum):
    # ... existing themes ...
    NEW_THEME = "new_theme"

# Add theme configuration
self.theme_configs = {
    # ... existing themes ...
    ThemeType.NEW_THEME: {
        'name': 'New Theme',
        'description': 'Description of new theme',
        'colors': {
            'primary': '#color',
            'secondary': '#color',
            'background': '#color',
            'text': '#color'
        },
        # ... other configuration
    }
}
```

### 3. New Components

#### Component Template

```python
#!/usr/bin/env python3
"""
New Component
Description of the component's purpose
"""

import asyncio
import logging
from typing import Dict, Any, Optional

class NewComponent:
    """New component class"""

    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.logger = logging.getLogger(__name__)

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data"""
        try:
            # Implementation here
            return {"status": "success", "data": data}
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            return {"status": "error", "error": str(e)}
```

### 4. Integration Points

#### Adding SSOT Integration

```python
# In ssot_integration.py
async def integrate_new_component(self):
    """Integrate new component with SSOT"""
    try:
        # Add component to SSOT config
        if "new_component" not in self.ssot_config:
            self.ssot_config["new_component"] = {
                "enabled": True,
                "last_updated": datetime.now().isoformat()
            }

        # Save updated config
        with open(self.config_path, 'w') as f:
            json.dump(self.ssot_config, f, indent=2)

        self.logger.info("✅ New component integrated with SSOT")
        return True

    except Exception as e:
        self.logger.error(f"❌ Failed to integrate new component: {e}")
        return False
```

## Debugging

### Debug Mode

```python
# Enable debug mode in config
config.set('system.debug_mode', True)
config.set('system.log_level', 'DEBUG')
```

### Debugging Tools

#### VS Code Debugging

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Nexus Main",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/NEXUS_nexus_backend/main.py",
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}"
    }
  ]
}
```

#### PyCharm Debugging

- Set breakpoints in code
- Use "Debug" instead of "Run"
- Use debugger console for inspection

### Common Debugging Techniques

#### Logging

```python
# Add debug logging
self.logger.debug(f"Processing data: {data}")
self.logger.debug(f"Current POV: {self.current_pov}")
self.logger.debug(f"Result: {result}")
```

#### Assertions

```python
# Add assertions for debugging
assert data is not None, "Data cannot be None"
assert len(expenses) > 0, "Expenses list cannot be empty"
```

#### Exception Handling

```python
try:
    result = await some_operation()
except Exception as e:
    self.logger.error(f"Operation failed: {e}")
    self.logger.error(f"Data: {data}")
    self.logger.error(f"Stack trace: {traceback.format_exc()}")
    raise
```

## Performance Optimization

### Profiling

```python
import cProfile
import pstats

# Profile code
profiler = cProfile.Profile()
profiler.enable()

# Run code
await some_operation()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats()
```

### Memory Profiling

```python
from memory_profiler import profile

@profile
def memory_intensive_function():
    # Function implementation
    pass
```

### Database Optimization

```python
# Use connection pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

## Security Considerations

### Input Validation

```python
def validate_financial_data(data: Dict[str, Any]) -> bool:
    """Validate financial data input"""
    required_fields = ['expenses', 'bank_statements']

    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    if not isinstance(data['expenses'], list):
        raise ValueError("Expenses must be a list")

    return True
```

### SQL Injection Prevention

```python
# Use parameterized queries
query = "SELECT * FROM expenses WHERE amount > %s AND date > %s"
cursor.execute(query, (min_amount, start_date))
```

### Data Encryption

```python
from cryptography.fernet import Fernet

def encrypt_sensitive_data(data: str, key: bytes) -> str:
    """Encrypt sensitive data"""
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()

def decrypt_sensitive_data(encrypted_data: str, key: bytes) -> str:
    """Decrypt sensitive data"""
    f = Fernet(key)
    return f.decrypt(encrypted_data.encode()).decode()
```

## Contributing

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes
git add .
git commit -m "Add new feature"

# Push branch
git push origin feature/new-feature

# Create pull request
```

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] Error handling is appropriate
- [ ] Performance considerations addressed
- [ ] Security implications reviewed

### Pull Request Template

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## Resources

### Documentation

- [Python Documentation](https://docs.python.org/3/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)

### Tools

- [Pytest](https://docs.pytest.org/)
- [Black](https://black.readthedocs.io/)
- [Pylint](https://pylint.pycqa.org/)
- [Pre-commit](https://pre-commit.com/)

### Best Practices

- [Python Best Practices](https://docs.python-guide.org/)
- [Async Python](https://docs.python.org/3/library/asyncio.html)
- [Database Best Practices](https://www.postgresql.org/docs/current/ddl.html)
