# Getting Started with NEXUS Platform Development

Welcome to the NEXUS Platform! This guide will help you set up your development environment and get started with contributing to the platform.

## Prerequisites

Before you begin, ensure you have the following installed:

### System Requirements

- **Operating System**: macOS 10.15+, Ubuntu 18.04+, or Windows 10+ with WSL2
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 20GB free space

### Required Software

- **Python**: 3.11 or later
- **Node.js**: 18.x or later
- **Docker**: 20.10 or later
- **Docker Compose**: 2.0 or later
- **Git**: 2.30 or later
- **PostgreSQL**: 15.x (for local development)
- **Redis**: 7.x (for local development)

### Development Tools

- **VS Code** or **PyCharm** (recommended IDEs)
- **Postman** or **Insomnia** (API testing)
- **pgAdmin** or **DBeaver** (database management)
- **Redis Commander** (Redis management)

## Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/nexus-platform.git
cd nexus-platform
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Set Up Node.js Environment

```bash
cd NEXUS_nexus_backend/frontend
npm install
```

### 4. Set Up Docker Environment

```bash
# Start development services
docker-compose -f docker-compose.dev.yml up -d

# Verify services are running
docker ps
```

### 5. Environment Configuration

Create environment files:

```bash
# Copy environment templates
cp env.example .env
cp NEXUS_nexus_backend/.env.example NEXUS_nexus_backend/.env
cp NEXUS_nexus_backend/nexus_frontend/.env.example NEXUS_nexus_backend/nexus_frontend/.env
```

Edit `.env` files with your local configuration:

```bash
# .env
DATABASE_URL=postgresql://nexus:nexus@localhost:5432/nexus_dev
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=your-super-secret-jwt-key-here
ENCRYPTION_KEY=your-32-character-encryption-key
```

### 6. Database Setup

```bash
# Run database migrations
alembic upgrade head

# Seed initial data (optional)
python scripts/seed_database.py
```

## Project Structure

```
nexus-platform/
├── .github/                 # GitHub Actions CI/CD
├── .nexus/                  # Platform-specific tools
│   ├── monitoring/          # Monitoring components
│   └── scripts/            # Utility scripts
├── NEXUS_nexus_backend/              # Main application
│   ├── nexus_backend/            # Python backend services
│   ├── nexus_frontend/           # React frontend
│   ├── database/           # Database models and migrations
│   └── tests/              # Test suites
├── config/                 # Configuration files
├── docs/                   # Documentation
├── scripts/                # Build and utility scripts
├── services/               # Microservices
│   ├── user-service/
│   ├── transaction-service/
│   ├── analytics-service/
│   └── audit-service/
└── requirements.txt        # Python dependencies
```

## Development Workflow

### 1. Start Development Services

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# Or start individual services
docker-compose -f docker-compose.dev.yml up postgres redis -d
```

### 2. Run Backend Services

```bash
# Start API gateway
cd NEXUS_nexus_backend/backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start user service
cd services/user-service
python main.py

# Start transaction service
cd services/transaction-service
python main.py
```

### 3. Run Frontend

```bash
cd NEXUS_nexus_backend/frontend
npm start
```

### 4. Run Tests

```bash
# Run all tests
python scripts/run_tests.py --all

# Run specific test categories
python scripts/run_tests.py --unit
python scripts/run_tests.py --integration
python scripts/run_tests.py --e2e

# Run with coverage
python scripts/run_tests.py --coverage
```

### 5. Code Quality Checks

```bash
# Linting and type checking
python scripts/run_tests.py --lint
python scripts/run_tests.py --type-check

# Validate naming conventions
python scripts/validate_naming.py

# Security scanning
python scripts/security_scan.py
```

## API Development

### Creating a New Endpoint

1. **Define the endpoint** in the appropriate service
2. **Add request/response models** in `schemas/`
3. **Implement business logic** in service layer
4. **Add database operations** if needed
5. **Write tests** for the endpoint
6. **Update API documentation**

Example endpoint implementation:

```python
# services/user-service/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..schemas import UserCreate, UserResponse
from ..services import UserService

router = APIRouter()

@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    user_service = UserService(db)
    return user_service.create_user(user)
```

### Database Operations

```python
# services/user-service/models.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Testing

```python
# tests/test_user_service.py
import pytest
from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

def test_create_user():
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "securepassword"
    }

    response = client.post("/api/v1/users", json=user_data)
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]
```

## Frontend Development

### Component Structure

```typescript
// nexus_backend/components/UserProfile.tsx
import React, { useState, useEffect } from 'react';
import { useApi } from '../hooks/useApi';

interface UserProfileProps {
  userId: string;
}

export const UserProfile: React.FC<UserProfileProps> = ({ userId }) => {
  const [user, setUser] = useState(null);
  const { get } = useApi();

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await get(`/users/${userId}`);
        setUser(response.data);
      } catch (error) {
        console.error('Failed to fetch user:', error);
      }
    };

    fetchUser();
  }, [userId, get]);

  if (!user) return <div>Loading...</div>;

  return (
    <div className="user-profile">
      <h2>{user.full_name}</h2>
      <p>{user.email}</p>
    </div>
  );
};
```

### State Management

```typescript
// nexus_backend/stores/useUserStore.ts
import { create } from "zustand";

interface UserState {
  currentUser: any | null;
  setCurrentUser: (user: any) => void;
  clearCurrentUser: () => void;
}

export const useUserStore = create<UserState>((set) => ({
  currentUser: null,
  setCurrentUser: (user) => set({ currentUser: user }),
  clearCurrentUser: () => set({ currentUser: null }),
}));
```

## Debugging and Troubleshooting

### Common Issues

#### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check database logs
docker logs nexus-postgres

# Test connection
psql -h localhost -U nexus -d nexus_dev
```

#### Redis Connection Issues

```bash
# Check if Redis is running
docker ps | grep redis

# Test Redis connection
redis-cli ping
```

#### Service Startup Issues

```bash
# Check service logs
docker logs nexus-user-service

# Check environment variables
echo $DATABASE_URL
echo $REDIS_URL

# Validate configuration
python -c "import os; print(os.environ.get('DATABASE_URL'))"
```

### Debugging Tools

#### API Debugging

```bash
# Use curl for API testing
curl -X GET "http://localhost:8000/api/v1/health" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Use httpie for better formatting
http GET http://localhost:8000/api/v1/health \
  Authorization:"Bearer YOUR_JWT_TOKEN"
```

#### Database Debugging

```sql
-- Check active connections
SELECT * FROM pg_stat_activity;

-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

#### Performance Monitoring

```bash
# Monitor system resources
top -p $(pgrep -f "python.*main.py" | tr '\n' ',' | sed 's/,$//')

# Check memory usage
ps aux --sort=-%mem | head -10

# Monitor network connections
netstat -tlnp | grep :8000
```

## Contributing Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use TypeScript strict mode
- Run linters before committing
- Write descriptive commit messages

### Testing

- Write tests for all new features
- Maintain >80% code coverage
- Run full test suite before pushing
- Test both happy path and error scenarios

### Documentation

- Update API documentation for new endpoints
- Add docstrings to all functions
- Update README for significant changes
- Document breaking changes

### Pull Request Process

1. Create a feature branch from `develop`
2. Write tests for your changes
3. Ensure all tests pass
4. Update documentation
5. Create a pull request with a clear description
6. Wait for code review and approval

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Maintenance

## Deployment

### Local Deployment

```bash
# Build and start all services
docker-compose up --build

# Or deploy specific service
docker-compose up user-service --build
```

### Staging Deployment

```bash
# Deploy to staging environment
kubectl apply -f k8s/staging/
kubectl rollout status deployment/nexus-backend -n nexus-staging
```

### Production Deployment

```bash
# Deploy to production (via CI/CD)
# This is handled automatically by GitHub Actions
```

## Support and Resources

### Documentation

- [API Documentation](./api/openapi.yaml)
- [Architecture Overview](./architecture/overview.md)
- [Security Guidelines](./security/guidelines.md)

### Getting Help

- **Slack**: #nexus-dev (internal)
- **Issues**: GitHub Issues for bugs and features
- **Wiki**: Internal wiki for detailed guides

### Key Contacts

- **Tech Lead**: tech-lead@nexusplatform.com
- **DevOps**: devops@nexusplatform.com
- **Security**: security@nexusplatform.com

---

Happy coding! 🚀
