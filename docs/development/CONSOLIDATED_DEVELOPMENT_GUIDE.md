# NEXUS Platform - Consolidated Development Guide

**Status**: 🔒 **CONSOLIDATED** - Single Source of Truth for Development
**Version**: 2.0
**Last Updated**: 2025-01-27
**Source**: Consolidated from multiple development guides
**Aligned with**: [Vision & Mission](01-vision-mission.md)

---

## 🎯 **DEVELOPMENT OVERVIEW**

The NEXUS Platform development environment is designed to support the mission of **"revolutionizing financial examination through intelligent, role-based analysis"** by providing developers with comprehensive tools, standards, and processes that ensure code quality, security, and maintainability.

### **Development Philosophy**

- **Code Quality First**: Maintain 95%+ code quality standards
- **Security by Design**: Built-in security at every layer
- **Test-Driven Development**: Comprehensive testing coverage
- **Documentation as Code**: Living documentation that evolves with code
- **Continuous Integration**: Automated quality gates and deployment

---

## 🚀 **DEVELOPMENT ENVIRONMENT SETUP**

### **Prerequisites**

#### **System Requirements**

- **Python**: 3.11+ (3.12 recommended)
- **Node.js**: 18+ (20+ recommended)
- **Git**: 2.40+
- **Docker**: 24.0+ with Docker Compose 2.0+
- **PostgreSQL**: 15+ (16+ recommended)
- **Redis**: 7.0+ (7.2+ recommended)

#### **IDE Requirements**

- **VS Code**: Latest version with recommended extensions
- **PyCharm**: Professional edition (optional)
- **Docker Desktop**: For containerized development
- **kubectl**: For Kubernetes development

### **Initial Setup**

#### **1. Repository Setup**

```bash
# Clone repository
git clone https://github.com/nexus-platform/nexus.git
cd nexus

# Create virtual environment
python -m venv nexus_env
source nexus_env/bin/activate  # On Windows: nexus_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install
```

#### **2. Database Setup**

```bash
# Start PostgreSQL and Redis
docker-compose up -d db redis

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data
python manage.py loaddata fixtures/sample_data.json
```

#### **3. Frontend Setup**

```bash
# Install frontend dependencies
cd frontend
npm install

# Start development server
npm run dev
```

### **IDE Configuration**

#### **VS Code Settings**

```json
{
  "python.defaultInterpreterPath": "./nexus_env/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests/"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true
  }
}
```

#### **Recommended Extensions**

- Python
- Pylance
- Black Formatter
- Prettier
- ESLint
- Docker
- Kubernetes
- GitLens

---

## 🏗️ **PROJECT STRUCTURE**

**Note:** This project is currently undergoing a consolidation effort to improve the structure and remove legacy code. The new modular architecture is being developed in the `updated_consolidated_python/` directory.

### **Backend Structure**

```
NEXUS_nexus_backend/
├── core/                    # Core business logic
│   ├── nexus_ssot_automation_system.py
│   ├── nexus_simple.py
│   ├── frenly_meta_agent.py
│   └── nexus_task_manager.py
├── api/                     # API endpoints
│   ├── v1/                  # API version 1
│   ├── authentication.py
│   └── middleware.py
├── models/                  # Data models
│   ├── user.py
│   ├── transaction.py
│   └── pov_analysis.py
├── services/                # Business services
│   ├── reconciliation.py
│   ├── fraud_detection.py
│   └── report_generation.py
├── utils/                   # Utility functions
│   ├── validators.py
│   ├── formatters.py
│   └── security.py
├── tests/                   # Test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── config/                  # Configuration files
    ├── settings.py
    ├── database.py
    └── security.py
```

### **Frontend Structure**

```
nexus_frontend/
├── nexus_backend/
│   ├── components/          # React components
│   │   ├── common/
│   │   ├── pov/
│   │   └── themes/
│   ├── pages/               # Page components
│   │   ├── dashboard/
│   │   ├── analysis/
│   │   └── reports/
│   ├── services/            # API services
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   └── pov.ts
│   ├── hooks/               # Custom React hooks
│   ├── utils/               # Utility functions
│   ├── types/               # TypeScript types
│   └── styles/              # Styling files
├── public/                  # Static assets
└── tests/                   # Frontend tests
    ├── unit/
    ├── integration/
    └── e2e/
```

---

## 📝 **CODING STANDARDS**

### **Python Standards**

#### **Code Style**

- **Formatter**: Black with line length 88
- **Linter**: Flake8 with custom rules
- **Import Sorting**: isort with Black compatibility
- **Type Hints**: Required for all functions and methods

#### **Example Code**

```python
from typing import Dict, List, Optional, Union
from decimal import Decimal
from pydantic import BaseModel, Field, validator
import logging

logger = logging.getLogger(__name__)

class TransactionAnalysis(BaseModel):
    """Financial transaction analysis model."""

    transaction_id: str = Field(..., description="Unique transaction identifier")
    amount: Decimal = Field(..., gt=0, description="Transaction amount")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Analysis confidence")
    fraud_indicators: List[str] = Field(default_factory=list, description="Fraud indicators")

    @validator('amount')
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Validate transaction amount."""
        if v <= 0:
            raise ValueError('Amount must be positive')
        if v > Decimal('999999.99'):
            raise ValueError('Amount exceeds maximum limit')
        return v

    def calculate_risk_score(self) -> float:
        """Calculate overall risk score for the transaction."""
        base_score = 1.0 - self.confidence_score
        fraud_penalty = len(self.fraud_indicators) * 0.1
        return min(1.0, base_score + fraud_penalty)

class FraudDetectionService:
    """Service for detecting fraudulent transactions."""

    def __init__(self, config: Dict[str, Union[str, int]]) -> None:
        """Initialize fraud detection service."""
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def analyze_transaction(
        self,
        transaction: TransactionAnalysis
    ) -> Dict[str, Union[bool, float, List[str]]]:
        """
        Analyze transaction for fraud indicators.

        Args:
            transaction: Transaction to analyze

        Returns:
            Analysis results with fraud indicators
        """
        try:
            risk_score = transaction.calculate_risk_score()
            is_fraudulent = risk_score > self.config.get('fraud_threshold', 0.7)

            self.logger.info(
                f"Transaction {transaction.transaction_id} analyzed: "
                f"risk_score={risk_score:.2f}, is_fraudulent={is_fraudulent}"
            )

            return {
                'is_fraudulent': is_fraudulent,
                'risk_score': risk_score,
                'indicators': transaction.fraud_indicators
            }
        except Exception as e:
            self.logger.error(f"Error analyzing transaction: {e}")
            raise
```

#### **Documentation Standards**

```python
def process_financial_data(
    data: List[Dict[str, Union[str, Decimal]]],
    pov_role: str,
    analysis_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process financial data for specific POV role analysis.

    This function takes raw financial data and processes it according to the
    specified Point of View (POV) role, applying role-specific analysis rules
    and generating appropriate insights.

    Args:
        data: List of financial transaction dictionaries
        pov_role: POV role for analysis (e.g., 'financial_examiner', 'prosecutor')
        analysis_config: Optional configuration for analysis parameters

    Returns:
        Dictionary containing:
            - processed_data: Processed financial data
            - insights: Role-specific insights
            - recommendations: Actionable recommendations
            - confidence_score: Analysis confidence (0.0-1.0)

    Raises:
        ValueError: If pov_role is not supported
        ProcessingError: If data processing fails

    Example:
        >>> data = [{'amount': 1000, 'description': 'Office supplies'}]
        >>> result = process_financial_data(data, 'financial_examiner')
        >>> print(result['confidence_score'])
        0.85
    """
    # Implementation here
    pass
```

### **TypeScript/JavaScript Standards**

#### **Code Style**

- **Formatter**: Prettier with 2-space indentation
- **Linter**: ESLint with TypeScript rules
- **Type Safety**: Strict TypeScript configuration
- **Imports**: Absolute imports with path mapping

#### **Example Code**

```typescript
// types/transaction.ts
export interface Transaction {
  id: string;
  amount: number;
  description: string;
  date: Date;
  category: string;
  povAnalysis?: POVAnalysis;
}

export interface POVAnalysis {
  role: POVRole;
  confidenceScore: number;
  riskLevel: "low" | "medium" | "high" | "critical";
  indicators: string[];
  recommendations: string[];
}

export type POVRole =
  | "financial_examiner"
  | "prosecutor"
  | "judge"
  | "executive"
  | "compliance_officer"
  | "auditor";

// services/analysisService.ts
import { Transaction, POVAnalysis, POVRole } from "@/types/transaction";
import { apiClient } from "./apiClient";

export class AnalysisService {
  private readonly baseUrl = "/api/v1/analysis";

  /**
   * Analyze transaction for specific POV role
   * @param transaction - Transaction to analyze
   * @param povRole - POV role for analysis
   * @returns Promise resolving to POV analysis results
   */
  async analyzeTransaction(
    transaction: Transaction,
    povRole: POVRole,
  ): Promise<POVAnalysis> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/transaction`, {
        transaction,
        povRole,
      });

      return response.data;
    } catch (error) {
      console.error("Analysis failed:", error);
      throw new Error("Failed to analyze transaction");
    }
  }

  /**
   * Get analysis history for a transaction
   * @param transactionId - Transaction ID
   * @returns Promise resolving to analysis history
   */
  async getAnalysisHistory(transactionId: string): Promise<POVAnalysis[]> {
    const response = await apiClient.get(
      `${this.baseUrl}/history/${transactionId}`,
    );
    return response.data;
  }
}
```

---

## 🧪 **TESTING STANDARDS**

### **Testing Philosophy**

- **Test-Driven Development**: Write tests before implementation
- **Comprehensive Coverage**: Aim for 90%+ code coverage
- **Fast Feedback**: Tests should run quickly
- **Reliable**: Tests should be deterministic and stable

### **Test Structure**

#### **Unit Tests**

```python
# tests/unit/test_fraud_detection.py
import pytest
from decimal import Decimal
from unittest.mock import Mock, patch

from services.fraud_detection import FraudDetectionService
from models.transaction import TransactionAnalysis

class TestFraudDetectionService:
    """Test suite for FraudDetectionService."""

    @pytest.fixture
    def fraud_service(self):
        """Create fraud detection service instance."""
        config = {'fraud_threshold': 0.7}
        return FraudDetectionService(config)

    @pytest.fixture
    def sample_transaction(self):
        """Create sample transaction for testing."""
        return TransactionAnalysis(
            transaction_id="TXN-001",
            amount=Decimal("1000.00"),
            confidence_score=0.8,
            fraud_indicators=["unusual_amount", "off_hours"]
        )

    @pytest.mark.asyncio
    async def test_analyze_transaction_fraudulent(self, fraud_service, sample_transaction):
        """Test fraud detection for fraudulent transaction."""
        result = await fraud_service.analyze_transaction(sample_transaction)

        assert result['is_fraudulent'] is True
        assert result['risk_score'] > 0.7
        assert 'unusual_amount' in result['indicators']

    @pytest.mark.asyncio
    async def test_analyze_transaction_legitimate(self, fraud_service):
        """Test fraud detection for legitimate transaction."""
        transaction = TransactionAnalysis(
            transaction_id="TXN-002",
            amount=Decimal("50.00"),
            confidence_score=0.9,
            fraud_indicators=[]
        )

        result = await fraud_service.analyze_transaction(transaction)

        assert result['is_fraudulent'] is False
        assert result['risk_score'] < 0.7

    def test_calculate_risk_score(self, sample_transaction):
        """Test risk score calculation."""
        risk_score = sample_transaction.calculate_risk_score()

        assert 0.0 <= risk_score <= 1.0
        assert risk_score == 0.2 + 0.2  # base_score + fraud_penalty
```

#### **Integration Tests**

```python
# tests/integration/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient
from decimal import Decimal

from main import app
from models.transaction import TransactionAnalysis

client = TestClient(app)

class TestTransactionAPI:
    """Integration tests for transaction API endpoints."""

    def test_create_transaction(self):
        """Test transaction creation endpoint."""
        transaction_data = {
            "transaction_id": "TXN-001",
            "amount": "1000.00",
            "description": "Office supplies",
            "category": "expenses"
        }

        response = client.post("/api/v1/transactions", json=transaction_data)

        assert response.status_code == 201
        data = response.json()
        assert data["transaction_id"] == "TXN-001"
        assert data["amount"] == "1000.00"

    def test_analyze_transaction(self):
        """Test transaction analysis endpoint."""
        # First create a transaction
        transaction_data = {
            "transaction_id": "TXN-002",
            "amount": "500.00",
            "description": "Software license",
            "category": "expenses"
        }
        client.post("/api/v1/transactions", json=transaction_data)

        # Then analyze it
        analysis_data = {
            "transaction_id": "TXN-002",
            "pov_role": "financial_examiner"
        }

        response = client.post("/api/v1/analysis", json=analysis_data)

        assert response.status_code == 200
        data = response.json()
        assert "confidence_score" in data
        assert "risk_level" in data
        assert "recommendations" in data
```

#### **Frontend Tests**

```typescript
// tests/unit/analysisService.test.ts
import { AnalysisService } from "@/services/analysisService";
import { Transaction, POVRole } from "@/types/transaction";
import { apiClient } from "@/services/apiClient";

// Mock the API client
jest.mock("@/services/apiClient");
const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

describe("AnalysisService", () => {
  let analysisService: AnalysisService;

  beforeEach(() => {
    analysisService = new AnalysisService();
    jest.clearAllMocks();
  });

  describe("analyzeTransaction", () => {
    it("should analyze transaction successfully", async () => {
      const transaction: Transaction = {
        id: "TXN-001",
        amount: 1000,
        description: "Office supplies",
        date: new Date("2025-01-27"),
        category: "expenses",
      };

      const povRole: POVRole = "financial_examiner";
      const expectedResult = {
        role: povRole,
        confidenceScore: 0.85,
        riskLevel: "medium",
        indicators: ["unusual_amount"],
        recommendations: ["Review transaction details"],
      };

      mockedApiClient.post.mockResolvedValueOnce({
        data: expectedResult,
      });

      const result = await analysisService.analyzeTransaction(
        transaction,
        povRole,
      );

      expect(mockedApiClient.post).toHaveBeenCalledWith(
        "/api/v1/analysis/transaction",
        { transaction, povRole },
      );
      expect(result).toEqual(expectedResult);
    });

    it("should handle analysis errors", async () => {
      const transaction: Transaction = {
        id: "TXN-002",
        amount: 500,
        description: "Software license",
        date: new Date("2025-01-27"),
        category: "expenses",
      };

      mockedApiClient.post.mockRejectedValueOnce(new Error("API Error"));

      await expect(
        analysisService.analyzeTransaction(transaction, "financial_examiner"),
      ).rejects.toThrow("Failed to analyze transaction");
    });
  });
});
```

---

## 🔒 **SECURITY STANDARDS**

### **Input Validation**

#### **Pydantic Models**

```python
from pydantic import BaseModel, Field, validator, EmailStr
from decimal import Decimal
import re
from typing import Optional, List

class UserRegistration(BaseModel):
    """User registration model with comprehensive validation."""

    email: EmailStr = Field(..., description="Valid email address")
    username: str = Field(..., min_length=3, max_length=50, regex=r'^[a-zA-Z0-9_-]+$')
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., regex=r'^(financial_examiner|prosecutor|judge|executive|compliance_officer|auditor)$')

    @validator('password')
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain special character')
        return v

    @validator('username')
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if v.lower() in ['admin', 'root', 'system', 'nexus']:
            raise ValueError('Username not allowed')
        return v.lower()

class TransactionCreate(BaseModel):
    """Transaction creation model with financial validation."""

    amount: Decimal = Field(..., gt=0, le=Decimal('999999.99'), description="Transaction amount")
    description: str = Field(..., min_length=1, max_length=255, strip_whitespace=True)
    category: str = Field(..., regex=r'^[a-zA-Z0-9\s\-_]+$', max_length=100)
    vendor: Optional[str] = Field(None, max_length=100, regex=r'^[a-zA-Z0-9\s\-_.,&]+$')
    date: str = Field(..., regex=r'^\d{4}-\d{2}-\d{2}$')

    @validator('amount')
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Validate transaction amount."""
        if v <= 0:
            raise ValueError('Amount must be positive')
        if v > Decimal('999999.99'):
            raise ValueError('Amount exceeds maximum limit')
        return v.quantize(Decimal('0.01'))

    @validator('description')
    def sanitize_description(cls, v: str) -> str:
        """Sanitize description to prevent injection attacks."""
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', v)
        return sanitized.strip()
```

### **Authentication & Authorization**

#### **JWT Token Management**

```python
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

class AuthService:
    """Authentication service with JWT token management."""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> dict:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
```

---

## 📊 **PERFORMANCE STANDARDS**

### **Database Optimization**

#### **Query Optimization**

```python
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional

class TransactionRepository:
    """Optimized transaction repository with query optimization."""

    def __init__(self, db_session):
        self.db = db_session

    async def get_transactions_with_analysis(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Transaction]:
        """Get transactions with POV analysis using optimized query."""
        query = (
            select(Transaction)
            .options(
                selectinload(Transaction.pov_analysis),
                joinedload(Transaction.user)
            )
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_transaction_statistics(self, user_id: str) -> dict:
        """Get transaction statistics using aggregation."""
        query = (
            select(
                func.count(Transaction.id).label('total_transactions'),
                func.sum(Transaction.amount).label('total_amount'),
                func.avg(Transaction.amount).label('average_amount'),
                func.max(Transaction.amount).label('max_amount'),
                func.min(Transaction.amount).label('min_amount')
            )
            .where(Transaction.user_id == user_id)
        )

        result = await self.db.execute(query)
        return result.first()._asdict()
```

### **Caching Strategy**

#### **Redis Caching**

```python
import redis
import json
from typing import Optional, Any
from functools import wraps

class CacheService:
    """Redis caching service with TTL and invalidation."""

    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses=True)

    def cache_result(self, ttl: int = 300):
        """Decorator to cache function results."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Create cache key from function name and arguments
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

                # Try to get from cache
                cached_result = self.redis.get(cache_key)
                if cached_result:
                    return json.loads(cached_result)

                # Execute function and cache result
                result = await func(*args, **kwargs)
                self.redis.setex(
                    cache_key,
                    ttl,
                    json.dumps(result, default=str)
                )
                return result
            return wrapper
        return decorator

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache keys matching pattern."""
        keys = self.redis.keys(pattern)
        if keys:
            return self.redis.delete(*keys)
        return 0

# Usage example
cache_service = CacheService("redis://localhost:6379")

@cache_service.cache_result(ttl=600)  # Cache for 10 minutes
async def get_analysis_results(transaction_id: str, pov_role: str) -> dict:
    """Get analysis results with caching."""
    # Expensive analysis operation
    return await perform_analysis(transaction_id, pov_role)
```

---

## 🔄 **CI/CD INTEGRATION**

### **Pre-commit Hooks**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11
        args: [--line-length=88]

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: [--profile=black]

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/pycqa/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, ., -f, json, -o, bandit-report.json]

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.1.0
    hooks:
      - id: prettier
        files: \.(js|ts|jsx|tsx|json|css|md)$

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.56.0
    hooks:
      - id: eslint
        files: \.(js|ts|jsx|tsx)$
        additional_dependencies: [eslint@8.56.0]
```

### **GitHub Actions Workflow**

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: nexus_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7.2
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Install Python dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Install Node.js dependencies
        run: |
          cd frontend
          npm ci

      - name: Run Python tests
        run: |
          pytest tests/ --cov=nexus_backend/ --cov-report=xml --cov-report=html
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/nexus_test
          REDIS_URL: redis://localhost:6379

      - name: Run frontend tests
        run: |
          cd frontend
          npm run test:ci

      - name: Run security scan
        run: |
          bandit -r . -f json -o bandit-report.json
          safety check --json --output safety-report.json

      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
```

---

## 📚 **DOCUMENTATION STANDARDS**

### **Code Documentation**

- **Docstrings**: Required for all public functions and classes
- **Type Hints**: Required for all function parameters and return values
- **Comments**: Explain complex business logic and algorithms
- **README**: Comprehensive setup and usage instructions

### **API Documentation**

- **OpenAPI/Swagger**: Auto-generated from code annotations
- **Examples**: Include request/response examples
- **Error Codes**: Document all possible error responses
- **Authentication**: Clear authentication requirements

---

## 🎯 **DEVELOPMENT WORKFLOW**

### **Git Workflow**

1. **Feature Branch**: Create feature branch from `develop`
2. **Development**: Implement feature with tests
3. **Code Review**: Submit pull request for review
4. **Testing**: Automated tests must pass
5. **Merge**: Merge to `develop` after approval
6. **Release**: Deploy to production from `main`

### **Code Review Checklist**

- [ ] Code follows style guidelines
- [ ] Tests are comprehensive and passing
- [ ] Documentation is updated
- [ ] Security considerations addressed
- [ ] Performance impact evaluated
- [ ] Error handling is appropriate

---

**Last Updated**: 2025-01-27
**Version**: 2.0
**Maintainer**: NEXUS Development Team
**Next Review**: 2025-02-27
**Aligned with**: [Vision & Mission](01-vision-mission.md)
