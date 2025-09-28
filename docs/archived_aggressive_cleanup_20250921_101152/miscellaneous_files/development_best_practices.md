# Development Best Practices

## Financial Examiner POV System Development Standards

### Overview

This document outlines the development best practices, coding standards, and guidelines for the Financial Examiner POV system.

## Code Standards

### Python Development

#### Code Style

```python
# Use Black for code formatting
# Line length: 88 characters
# Use type hints for all functions
# Follow PEP 8 guidelines

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class POVRole(Enum):
    """Point of View roles for the system."""
    FINANCIAL_EXAMINER = "financial_examiner"
    PROSECUTOR = "prosecutor"
    JUDGE = "judge"
    EXECUTIVE = "executive"
    COMPLIANCE_OFFICER = "compliance_officer"
    AUDITOR = "auditor"

def process_financial_data(
    data: Dict[str, Any],
    pov_role: POVRole,
    user_id: str
) -> Dict[str, Any]:
    """
    Process financial data based on POV role.

    Args:
        data: Financial data dictionary
        pov_role: Current POV role
        user_id: User identifier

    Returns:
        Processed financial data with POV-specific analysis

    Raises:
        ValueError: If data format is invalid
        PermissionError: If user lacks required permissions
    """
    # Implementation here
    pass
```

#### Error Handling

```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def safe_process_data(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Safely process data with comprehensive error handling."""
    try:
        # Validate input data
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")

        # Process data
        result = process_financial_data(data)

        logger.info("Data processed successfully")
        return result

    except ValueError as e:
        logger.error(f"Invalid data format: {e}")
        return None

    except PermissionError as e:
        logger.error(f"Permission denied: {e}")
        return None

    except Exception as e:
        logger.error(f"Unexpected error processing data: {e}")
        return None
```

#### Logging Standards

```python
import logging
import json
from datetime import datetime

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nexus_platform.log'),
        logging.StreamHandler()
    ]
)

def log_audit_event(
    user_id: str,
    action: str,
    resource: str,
    result: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """Log audit events with structured data."""
    audit_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "action": action,
        "resource": resource,
        "result": result,
        "metadata": metadata or {}
    }

    logger.info(f"AUDIT: {json.dumps(audit_data)}")
```

### Frontend Development

#### React/TypeScript Standards

```typescript
// Use TypeScript for all components
// Follow React functional component patterns
// Use hooks for state management

import React, { useState, useEffect, useCallback } from 'react';
import { POVRole, ThemeType } from '../types';

interface POVSwitcherProps {
  currentPOV: POVRole;
  onPOVChange: (pov: POVRole) => void;
  availablePOVs: POVRole[];
}

const POVSwitcher: React.FC<POVSwitcherProps> = ({
  currentPOV,
  onPOVChange,
  availablePOVs
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const handlePOVChange = useCallback((pov: POVRole) => {
    onPOVChange(pov);
    setIsOpen(false);
  }, [onPOVChange]);

  return (
    <div className="pov-switcher">
      {/* Component implementation */}
    </div>
  );
};

export default POVSwitcher;
```

#### CSS/Styling Standards

```scss
// Use SCSS for styling
// Follow BEM methodology
// Use CSS custom properties for theming

.pov-switcher {
  position: relative;
  display: inline-block;

  &__button {
    background: var(--primary-color);
    color: var(--text-color);
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;

    &:hover {
      background: var(--primary-color-hover);
    }

    &:focus {
      outline: 2px solid var(--focus-color);
    }
  }

  &__dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    background: var(--background-color);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    box-shadow: var(--shadow-medium);
    z-index: 1000;
  }

  &__option {
    padding: 0.5rem 1rem;
    cursor: pointer;

    &:hover {
      background: var(--hover-color);
    }

    &--active {
      background: var(--active-color);
      font-weight: 600;
    }
  }
}
```

## Database Development

### Query Optimization

```sql
-- Use parameterized queries
-- Add appropriate indexes
-- Use EXPLAIN ANALYZE for optimization

-- Good: Parameterized query with index
SELECT e.id, e.amount, e.description, e.date
FROM expenses e
WHERE e.user_id = $1
  AND e.date BETWEEN $2 AND $3
  AND e.amount > $4
ORDER BY e.date DESC
LIMIT $5;

-- Index for the query
CREATE INDEX CONCURRENTLY idx_expenses_user_date_amount
ON expenses(user_id, date, amount);
```

### Migration Management

```python
# Use Alembic for database migrations
# Version control all schema changes
# Test migrations on staging environment

"""Add fraud detection tables

Revision ID: 001_fraud_detection
Revises: 000_initial_schema
Create Date: 2025-01-17 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('fraud_flags',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('flag_type', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('confidence', sa.Numeric(3, 2), nullable=False),
        sa.Column('amount', sa.Numeric(15, 2), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index('idx_fraud_flags_user_id', 'fraud_flags', ['user_id'])
    op.create_index('idx_fraud_flags_type', 'fraud_flags', ['flag_type'])

def downgrade():
    op.drop_table('fraud_flags')
```

## API Development

### RESTful API Design

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(
    title="NEXUS Platform Financial Examiner API",
    version="1.0.0",
    description="Financial reconciliation and fraud detection API"
)

class POVSwitchRequest(BaseModel):
    role: str = Field(..., description="POV role to switch to")
    context: Optional[str] = Field(None, description="Context for the switch")

class POVSwitchResponse(BaseModel):
    success: bool
    current_pov: str
    available_tools: List[str]
    permissions: List[str]

@app.post("/pov/switch", response_model=POVSwitchResponse)
async def switch_pov(
    request: POVSwitchRequest,
    current_user: dict = Depends(get_current_user)
) -> POVSwitchResponse:
    """Switch the current POV role."""
    try:
        # Validate POV role
        if request.role not in VALID_POV_ROLES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid POV role. Must be one of: {VALID_POV_ROLES}"
            )

        # Switch POV
        result = await pov_service.switch_pov(
            user_id=current_user["id"],
            new_role=request.role,
            context=request.context
        )

        return POVSwitchResponse(
            success=True,
            current_pov=result["current_pov"],
            available_tools=result["available_tools"],
            permissions=result["permissions"]
        )

    except Exception as e:
        logger.error(f"Error switching POV: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Error Handling

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

class NexusAPIException(Exception):
    """Base exception for NEXUS API errors."""
    def __init__(self, message: str, error_code: str, status_code: int = 400):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(message)

@app.exception_handler(NexusAPIException)
async def nexus_exception_handler(request, exc: NexusAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

## Security Best Practices

### Input Validation

```python
from pydantic import BaseModel, validator, Field
import re

class FinancialDataRequest(BaseModel):
    amount: float = Field(..., gt=0, le=999999.99)
    date: str = Field(..., regex=r'^\d{4}-\d{2}-\d{2}$')
    description: str = Field(..., min_length=1, max_length=500)
    category: str = Field(..., regex=r'^[a-zA-Z_][a-zA-Z0-9_]*$')

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return round(v, 2)

    @validator('description')
    def validate_description(cls, v):
        # Remove potentially dangerous characters
        cleaned = re.sub(r'[<>"\']', '', v)
        if not cleaned.strip():
            raise ValueError('Description cannot be empty')
        return cleaned
```

### Authentication & Authorization

```python
from functools import wraps
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt

def require_permission(permission: str):
    """Decorator to require specific permission."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            if permission not in current_user.get('permissions', []):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission}' required"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator

@require_permission('write:financial_data')
async def create_expense(
    expense_data: FinancialDataRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new expense with permission check."""
    # Implementation here
    pass
```

## Testing Standards

### Unit Testing

```python
import pytest
from unittest.mock import Mock, patch
from NEXUS_app.financial_examiner_system import FinancialExaminerSystem, POVRole

class TestFinancialExaminerSystem:
    """Test suite for FinancialExaminerSystem."""

    @pytest.fixture
    def system(self):
        """Create system instance for testing."""
        return FinancialExaminerSystem()

    @pytest.mark.asyncio
    async def test_switch_pov_success(self, system):
        """Test successful POV switching."""
        # Arrange
        new_pov = POVRole.PROSECUTOR

        # Act
        result = await system.switch_pov(new_pov)

        # Assert
        assert result is True
        assert system.current_pov == new_pov

    @pytest.mark.asyncio
    async def test_switch_pov_invalid_role(self, system):
        """Test POV switching with invalid role."""
        # Arrange
        invalid_pov = "invalid_role"

        # Act & Assert
        with pytest.raises(ValueError):
            await system.switch_pov(invalid_pov)

    @pytest.mark.asyncio
    async def test_process_financial_data(self, system):
        """Test financial data processing."""
        # Arrange
        data = {
            'expenses': [{'amount': 100.0, 'description': 'Office supplies'}],
            'bank_statements': [{'amount': 100.0, 'description': 'Office supplies payment'}]
        }

        # Act
        result = await system.process_financial_data(data)

        # Assert
        assert result['pov'] == system.current_pov.value
        assert 'reconciliation' in result
        assert 'fraud_analysis' in result
        assert 'litigation_flags' in result
        assert 'reports' in result
```

### Integration Testing

```python
import pytest
from fastapi.testclient import TestClient
from NEXUS_app.main import app

client = TestClient(app)

class TestAPIIntegration:
    """Integration tests for API endpoints."""

    def test_pov_switch_endpoint(self):
        """Test POV switching endpoint."""
        # Arrange
        payload = {
            "role": "prosecutor",
            "context": "case_analysis"
        }
        headers = {"Authorization": "Bearer test_token"}

        # Act
        response = client.post("/pov/switch", json=payload, headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["current_pov"] == "prosecutor"
        assert "available_tools" in data
        assert "permissions" in data
```

## Performance Optimization

### Database Optimization

```python
# Use connection pooling
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)

# Use async database operations
async def get_user_expenses(user_id: str, limit: int = 100):
    """Get user expenses with pagination."""
    async with get_db_session() as session:
        result = await session.execute(
            select(Expense)
            .where(Expense.user_id == user_id)
            .order_by(Expense.date.desc())
            .limit(limit)
        )
        return result.scalars().all()
```

### Caching Strategy

```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiry: int = 300):
    """Cache function result for specified seconds."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)

            # Execute function and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(
                cache_key,
                expiry,
                json.dumps(result, default=str)
            )

            return result
        return wrapper
    return decorator

@cache_result(expiry=600)
async def get_theme_config(theme_name: str):
    """Get theme configuration with caching."""
    # Implementation here
    pass
```

## Documentation Standards

### Code Documentation

```python
def process_financial_data(
    data: Dict[str, Any],
    pov_role: POVRole,
    user_id: str
) -> Dict[str, Any]:
    """
    Process financial data based on the current POV role.

    This function takes financial data (expenses and bank statements) and
    processes it according to the specified POV role. It performs reconciliation,
    fraud detection, and generates POV-specific analysis.

    Args:
        data: Dictionary containing financial data with keys:
            - expenses: List of expense dictionaries
            - bank_statements: List of bank statement dictionaries
        pov_role: The POV role to use for processing
        user_id: Identifier for the user requesting processing

    Returns:
        Dictionary containing processed results:
            - pov: Current POV role
            - reconciliation: Reconciliation results
            - fraud_analysis: Fraud detection results
            - pov_analysis: POV-specific analysis

    Raises:
        ValueError: If data format is invalid
        PermissionError: If user lacks required permissions
        ProcessingError: If data processing fails

    Example:
        >>> data = {
        ...     'expenses': [{'amount': 100, 'description': 'Office supplies'}],
        ...     'bank_statements': [{'amount': 100, 'description': 'Office payment'}]
        ... }
        >>> result = await process_financial_data(data, POVRole.PROSECUTOR, 'user123')
        >>> print(result['reconciliation']['matched_transactions'])
        1
    """
    # Implementation here
    pass
```

## Version Control

### Git Workflow

```bash
# Feature branch workflow
git checkout -b feature/pov-switching
git add .
git commit -m "feat: implement POV switching functionality

- Add POV role enumeration
- Implement POV switching logic
- Add POV-specific permissions
- Update API endpoints for POV management

Closes #123"

git push origin feature/pov-switching
```

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes
- refactor: Code refactoring
- test: Adding tests
- chore: Maintenance tasks
```

## Code Review Process

### Review Checklist

- [ ] Code follows style guidelines
- [ ] All functions have type hints
- [ ] Error handling is comprehensive
- [ ] Security best practices are followed
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] Performance considerations addressed
- [ ] No hardcoded values
- [ ] Logging is appropriate
- [ ] Database queries are optimized

### Review Guidelines

1. **Functionality**: Does the code work as intended?
2. **Security**: Are there any security vulnerabilities?
3. **Performance**: Will this code perform well in production?
4. **Maintainability**: Is the code easy to understand and modify?
5. **Testing**: Are there adequate tests?
6. **Documentation**: Is the code well documented?

## Architecture Patterns

### Manager Pattern

```python
class FinancialDataManager:
    """Manages financial data operations."""

    def __init__(self, db_session, cache_manager):
        self.db = db_session
        self.cache = cache_manager

    async def get_expenses(self, user_id: str) -> List[Dict]:
        """Get user expenses with caching."""
        cache_key = f"expenses:{user_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        expenses = await self.db.query(Expense).filter(
            Expense.user_id == user_id
        ).all()

        await self.cache.set(cache_key, expenses, ttl=300)
        return expenses
```

### Repository Pattern

```python
class ExpenseRepository:
    """Repository for expense data access."""

    def __init__(self, db_session):
        self.db = db_session

    async def create(self, expense_data: Dict) -> Expense:
        """Create a new expense."""
        expense = Expense(**expense_data)
        self.db.add(expense)
        await self.db.commit()
        return expense

    async def get_by_user(self, user_id: str) -> List[Expense]:
        """Get expenses by user ID."""
        return await self.db.query(Expense).filter(
            Expense.user_id == user_id
        ).all()
```

### Factory Pattern

```python
class POVFactory:
    """Factory for creating POV-specific processors."""

    @staticmethod
    def create_processor(pov_role: POVRole) -> 'POVProcessor':
        """Create POV-specific processor."""
        processors = {
            POVRole.FINANCIAL_EXAMINER: FinancialExaminerProcessor,
            POVRole.PROSECUTOR: ProsecutorProcessor,
            POVRole.JUDGE: JudgeProcessor,
            POVRole.EXECUTIVE: ExecutiveProcessor,
            POVRole.COMPLIANCE_OFFICER: ComplianceProcessor,
            POVRole.AUDITOR: AuditorProcessor
        }

        processor_class = processors.get(pov_role)
        if not processor_class:
            raise ValueError(f"Unknown POV role: {pov_role}")

        return processor_class()
```

## Quality Assurance

### Code Quality Metrics

- **Test Coverage**: Minimum 90% code coverage
- **Cyclomatic Complexity**: Maximum 10 per function
- **Code Duplication**: Maximum 5% duplicate code
- **Technical Debt**: Tracked and managed
- **Security Vulnerabilities**: Zero critical vulnerabilities

### Automated Quality Checks

```yaml
# .github/workflows/quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run linting
        run: |
          flake8 NEXUS_nexus_backend/
          black --check NEXUS_nexus_backend/
          isort --check-only NEXUS_nexus_backend/

      - name: Run type checking
        run: mypy NEXUS_nexus_backend/

      - name: Run security scan
        run: bandit -r NEXUS_nexus_backend/

      - name: Run tests
        run: pytest tests/ --cov=NEXUS_app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

This comprehensive development best practices guide ensures consistent, high-quality code development for the Financial Examiner POV system.
