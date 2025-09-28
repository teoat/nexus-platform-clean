# NEXUS Platform Testing Guide

## Overview

The NEXUS Platform employs a comprehensive testing strategy that ensures code quality, prevents regressions, and validates the API-first development approach. This guide covers all testing levels and best practices.

## Testing Pyramid

```
End-to-End Tests (E2E)
    ↕️
Integration Tests
    ↕️
Unit Tests
    ↕️
Static Analysis
```

## Testing Levels

### 1. Static Analysis

#### TypeScript Type Checking

```bash
# Run TypeScript compiler
npm run type-check

# Check specific files
npx tsc --noEmit --project tsconfig.json
```

#### ESLint

```bash
# Run ESLint
npm run lint

# Fix auto-fixable issues
npm run lint:fix
```

#### Python Type Checking

```bash
# Run mypy
mypy nexus_backend/ --ignore-missing-imports

# Run with stricter settings
mypy nexus_backend/ --strict --ignore-missing-imports
```

### 2. Unit Tests

#### Frontend Unit Tests

```bash
# Run all unit tests
npm test

# Run specific test file
npm test Button.test.tsx

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

**Test Structure:**

```tsx
// nexus_backend/components/__tests__/Button.test.tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { Button } from "../Button";

describe("Button", () => {
  it("renders with correct text", () => {
    render(<Button>Click me</Button>);
    expect(
      screen.getByRole("button", { name: /click me/i }),
    ).toBeInTheDocument();
  });

  it("handles click events", () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByRole("button"));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("shows loading state", () => {
    render(<Button loading>Loading...</Button>);
    expect(screen.getByRole("button")).toBeDisabled();
  });
});
```

#### Backend Unit Tests

```bash
# Run pytest
pytest

# Run specific test file
pytest tests/test_accounts.py

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test class/method
pytest tests/test_accounts.py::TestAccountAPI::test_create_account
```

**Test Structure:**

```python
# tests/test_accounts.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAccountAPI:
    def test_create_account_success(self):
        account_data = {
            "name": "Test Account",
            "account_type": "checking",
            "balance": 100.00
        }

        response = client.post("/api/v1/accounts", json=account_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == account_data["name"]
        assert data["account_type"] == account_data["account_type"]

    def test_create_account_validation_error(self):
        # Missing required field
        account_data = {"name": "Test Account"}

        response = client.post("/api/v1/accounts", json=account_data)
        assert response.status_code == 422  # Validation error

    def test_get_account_not_found(self):
        response = client.get("/api/v1/accounts/999")
        assert response.status_code == 404
```

### 3. Integration Tests

#### API Integration Tests

```python
# tests/integration/test_api_integration.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_account_workflow():
    """Test complete account creation, update, and deletion workflow"""

    # Create account
    account_data = {
        "name": "Integration Test Account",
        "account_type": "checking",
        "balance": 500.00
    }

    create_response = client.post("/api/v1/accounts", json=account_data)
    assert create_response.status_code == 200
    account = create_response.json()

    # Verify account was created
    get_response = client.get(f"/api/v1/accounts/{account['id']}")
    assert get_response.status_code == 200
    retrieved_account = get_response.json()
    assert retrieved_account["name"] == account_data["name"]

    # Update account
    update_data = {"name": "Updated Integration Test Account"}
    update_response = client.put(f"/api/v1/accounts/{account['id']}", json=update_data)
    assert update_response.status_code == 200

    # Delete account
    delete_response = client.delete(f"/api/v1/accounts/{account['id']}")
    assert delete_response.status_code == 200

    # Verify account was deleted
    get_after_delete = client.get(f"/api/v1/accounts/{account['id']}")
    assert get_after_delete.status_code == 404
```

#### Database Integration Tests

```python
# tests/integration/test_database_integration.py
import pytest
from sqlalchemy.orm import sessionmaker
from database.connection import get_db
from models.account import Account

def test_account_database_operations(db_session):
    """Test database operations for accounts"""

    # Create account
    account = Account(
        name="DB Test Account",
        account_type="checking",
        balance=1000.00,
        user_id=1
    )

    db_session.add(account)
    db_session.commit()

    # Query account
    retrieved = db_session.query(Account).filter_by(id=account.id).first()
    assert retrieved.name == "DB Test Account"
    assert retrieved.balance == 1000.00

    # Update account
    retrieved.balance = 1500.00
    db_session.commit()

    # Verify update
    updated = db_session.query(Account).filter_by(id=account.id).first()
    assert updated.balance == 1500.00

    # Delete account
    db_session.delete(account)
    db_session.commit()

    # Verify deletion
    deleted = db_session.query(Account).filter_by(id=account.id).first()
    assert deleted is None
```

### 4. End-to-End Tests

#### Playwright E2E Tests

```typescript
// e2e/account-management.spec.ts
import { test, expect } from "@playwright/test";

test.describe("Account Management", () => {
  test.beforeEach(async ({ page }) => {
    // Login and navigate to accounts page
    await page.goto("/login");
    await page.fill('[data-testid="email"]', "test@example.com");
    await page.fill('[data-testid="password"]', "password");
    await page.click('[data-testid="login-button"]');
    await page.waitForURL("/dashboard");
  });

  test("should create new account", async ({ page }) => {
    // Navigate to accounts page
    await page.click('[data-testid="accounts-nav"]');
    await page.waitForURL("/accounts");

    // Click create account button
    await page.click('[data-testid="create-account-button"]');

    // Fill account form
    await page.fill('[data-testid="account-name"]', "E2E Test Account");
    await page.selectOption('[data-testid="account-type"]', "checking");
    await page.fill('[data-testid="initial-balance"]', "1000");

    // Submit form
    await page.click('[data-testid="submit-account"]');

    // Verify account was created
    await expect(page.locator('[data-testid="account-list"]')).toContainText(
      "E2E Test Account",
    );
    await expect(page.locator('[data-testid="account-balance"]')).toContainText(
      "$1,000.00",
    );
  });

  test("should display account details", async ({ page }) => {
    await page.click('[data-testid="accounts-nav"]');

    // Click on first account
    await page.click('[data-testid="account-item"]:first-child');

    // Verify account details are displayed
    await expect(
      page.locator('[data-testid="account-detail-name"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="account-detail-balance"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="account-detail-type"]'),
    ).toBeVisible();
  });

  test("should update account information", async ({ page }) => {
    await page.click('[data-testid="accounts-nav"]');
    await page.click('[data-testid="account-item"]:first-child');
    await page.click('[data-testid="edit-account-button"]');

    // Update account name
    await page.fill('[data-testid="account-name"]', "Updated Account Name");
    await page.click('[data-testid="save-account"]');

    // Verify update
    await expect(
      page.locator('[data-testid="account-detail-name"]'),
    ).toContainText("Updated Account Name");
  });
});
```

## Testing Best Practices

### Unit Testing

#### Arrange-Act-Assert Pattern

```typescript
it("should calculate total correctly", () => {
  // Arrange
  const items = [
    { price: 10, quantity: 2 },
    { price: 5, quantity: 3 },
  ];

  // Act
  const total = calculateTotal(items);

  // Expect
  expect(total).toBe(35); // (10*2) + (5*3) = 35
});
```

#### Test Naming Conventions

```typescript
// Good
describe('AccountService', () => {
  describe('createAccount', () => {
    it('should create account with valid data', () => { ... });
    it('should throw error for invalid account type', () => { ... });
    it('should emit accountCreated event', () => { ... });
  });
});

// Bad
describe('Account tests', () => {
  it('test account creation', () => { ... });
  it('account creation error', () => { ... });
});
```

#### Mocking External Dependencies

```typescript
import { render, screen } from '@testing-library/react';
import { AccountList } from '../AccountList';

// Mock API client
jest.mock('../../services/apiClient', () => ({
  apiClient: {
    get: jest.fn()
  }
}));

const mockApiClient = require('../../services/apiClient').apiClient;

describe('AccountList', () => {
  beforeEach(() => {
    mockApiClient.get.mockClear();
  });

  it('should fetch and display accounts', async () => {
    // Mock API response
    mockApiClient.get.mockResolvedValue({
      data: [
        { id: 1, name: 'Checking Account', balance: 1000 }
      ],
      meta: { total: 1 }
    });

    render(<AccountList />);

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Checking Account')).toBeInTheDocument();
    });

    expect(mockApiClient.get).toHaveBeenCalledWith('/api/v1/accounts');
  });
});
```

### Integration Testing

#### Test Data Management

```python
@pytest.fixture
def test_user(db_session):
    """Create a test user for integration tests"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_account(db_session, test_user):
    """Create a test account for integration tests"""
    account = Account(
        name="Test Account",
        account_type="checking",
        balance=1000.00,
        user_id=test_user.id
    )
    db_session.add(account)
    db_session.commit()
    return account

def test_account_transaction_workflow(db_session, test_account):
    """Test account and transaction integration"""
    # Create transaction
    transaction = Transaction(
        account_id=test_account.id,
        amount=100.00,
        description="Test transaction",
        transaction_type="expense"
    )
    db_session.add(transaction)
    db_session.commit()

    # Verify account balance updated
    updated_account = db_session.query(Account).get(test_account.id)
    assert updated_account.balance == 900.00  # 1000 - 100
```

### E2E Testing

#### Page Object Pattern

```typescript
// e2e/pages/LoginPage.ts
export class LoginPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto("/login");
  }

  async login(email: string, password: string) {
    await this.page.fill('[data-testid="email"]', email);
    await this.page.fill('[data-testid="password"]', password);
    await this.page.click('[data-testid="login-button"]');
  }

  async getErrorMessage() {
    return this.page.textContent('[data-testid="error-message"]');
  }
}

// e2e/auth.spec.ts
test("should login successfully", async ({ page }) => {
  const loginPage = new LoginPage(page);

  await loginPage.goto();
  await loginPage.login("user@example.com", "password");

  await expect(page).toHaveURL("/dashboard");
});
```

## Test Automation

### CI/CD Integration

#### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: "18"

      - name: Install dependencies
        run: npm ci

      - name: Run type checking
        run: npm run type-check

      - name: Run linting
        run: npm run lint

      - name: Run unit tests
        run: npm test -- --coverage --watchAll=false

      - name: Run integration tests
        run: npm run test:integration

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.9"

      - name: Install Python dependencies
        run: pip install -r requirements.txt

      - name: Run backend tests
        run: pytest --cov=backend --cov-report=xml

      - name: Run E2E tests
        run: npx playwright test

      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
```

### Test Data Management

#### Factory Pattern for Test Data

```python
# tests/factories.py
from faker import Faker
from models.account import Account
from models.user import User

fake = Faker()

class UserFactory:
    @staticmethod
    def create(db_session, **overrides):
        user_data = {
            'username': fake.user_name(),
            'email': fake.email(),
            'hashed_password': 'hashed_password',
            **overrides
        }
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        return user

class AccountFactory:
    @staticmethod
    def create(db_session, user_id=None, **overrides):
        if user_id is None:
            user = UserFactory.create(db_session)
            user_id = user.id

        account_data = {
            'name': fake.company() + ' Account',
            'account_type': 'checking',
            'balance': fake.pydecimal(left_digits=4, right_digits=2, positive=True),
            'user_id': user_id,
            **overrides
        }
        account = Account(**account_data)
        db_session.add(account)
        db_session.commit()
        return account
```

## Performance Testing

### Load Testing with Artillery

```yaml
# performance/load-test.yml
config:
  target: "http://localhost:8000"
  phases:
    - duration: 60
      arrivalRate: 10
      name: "Warm up"
    - duration: 120
      arrivalRate: 50
      name: "Load test"
    - duration: 60
      arrivalRate: 100
      name: "Spike test"

scenarios:
  - name: "Get accounts"
    weight: 70
    requests:
      - get:
          url: "/api/v1/accounts"
          headers:
            Authorization: "Bearer {{token}}"

  - name: "Create transaction"
    weight: 30
    requests:
      - post:
          url: "/api/v1/transactions"
          headers:
            Authorization: "Bearer {{token}}"
            Content-Type: "application/json"
          json:
            account_id: 1
            amount: 50.00
            description: "Load test transaction"
            transaction_type: "expense"
```

### Lighthouse Performance Testing

```javascript
// performance/lighthouse-test.js
const lighthouse = require("lighthouse");
const chromeLauncher = require("chrome-launcher");

async function runLighthouse(url) {
  const chrome = await chromeLauncher.launch({ chromeFlags: ["--headless"] });

  const options = {
    logLevel: "info",
    output: "html",
    onlyCategories: ["performance", "accessibility", "best-practices", "seo"],
    port: chrome.port,
  };

  const runnerResult = await lighthouse(url, options);

  console.log("Report is done for", runnerResult.lhr.finalUrl);
  console.log(
    "Performance score was",
    runnerResult.lhr.categories.performance.score * 100,
  );

  await chrome.kill();
}

runLighthouse("http://localhost:3000");
```

## Accessibility Testing

### Automated Accessibility Testing

```typescript
// tests/accessibility.test.ts
import { test, expect } from "@playwright/test";

test.describe("Accessibility", () => {
  test("should pass accessibility audit", async ({ page }) => {
    await page.goto("/");

    // Run axe accessibility audit
    const accessibilityScanResults = await page.accessibility.snapshot();

    // Check for critical accessibility issues
    const criticalViolations = accessibilityScanResults.violations.filter(
      (violation) => violation.impact === "critical",
    );

    expect(criticalViolations).toHaveLength(0);
  });

  test("should have proper heading hierarchy", async ({ page }) => {
    await page.goto("/dashboard");

    const headings = await page.$$eval("h1, h2, h3, h4, h5, h6", (elements) =>
      elements.map((el) => ({
        tag: el.tagName,
        text: el.textContent?.trim(),
      })),
    );

    // Verify heading hierarchy
    expect(headings[0].tag).toBe("H1");
    expect(headings[0].text).toBeTruthy();
  });

  test("should support keyboard navigation", async ({ page }) => {
    await page.goto("/accounts");

    // Tab through interactive elements
    await page.keyboard.press("Tab");
    let focusedElement = await page.evaluate(
      () => document.activeElement?.tagName,
    );
    expect(["BUTTON", "A", "INPUT", "SELECT", "TEXTAREA"]).toContain(
      focusedElement,
    );

    await page.keyboard.press("Tab");
    focusedElement = await page.evaluate(() => document.activeElement?.tagName);
    expect(["BUTTON", "A", "INPUT", "SELECT", "TEXTAREA"]).toContain(
      focusedElement,
    );
  });
});
```

## Test Coverage Goals

### Coverage Targets

- **Unit Tests**: > 80% coverage
- **Integration Tests**: > 70% coverage
- **E2E Tests**: Key user journeys covered
- **Accessibility**: WCAG 2.1 AA compliance

### Coverage Reporting

```bash
# Frontend coverage
npm test -- --coverage --coverageReporters="html,text"

# Backend coverage
pytest --cov=backend --cov-report=html --cov-report=term

# Combined coverage report
# Use tools like codecov or coveralls for CI/CD
```

## Debugging Test Failures

### Common Issues and Solutions

#### Async Test Issues

```typescript
// Problem: Test completes before async operation
it('should load data', async () => {
  render(<DataComponent />);

  // Wait for data to load
  await waitFor(() => {
    expect(screen.getByText('Data loaded')).toBeInTheDocument();
  });
});

// Solution: Use waitFor or findBy queries
it('should load data', async () => {
  render(<DataComponent />);

  const dataElement = await screen.findByText('Data loaded');
  expect(dataElement).toBeInTheDocument();
});
```

#### Mock Issues

```typescript
// Problem: Mock not reset between tests
describe("API Service", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should call API", () => {
    // Test implementation
  });
});
```

#### Database Test Cleanup

```python
@pytest.fixture(autouse=True)
def clean_database(db_session):
    """Clean database before each test"""
    # Delete all data in reverse dependency order
    db_session.query(Transaction).delete()
    db_session.query(Account).delete()
    db_session.query(User).delete()
    db_session.commit()
```

## Continuous Testing

### Pre-commit Hooks

```bash
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: local
    hooks:
      - id: type-check
        name: TypeScript type check
        entry: npm run type-check
        language: system
        files: \.(ts|tsx)$
        pass_filenames: false

      - id: lint
        name: ESLint
        entry: npm run lint
        language: system
        files: \.(ts|tsx)$
        pass_filenames: false

      - id: test
        name: Unit tests
        entry: npm test -- --watchAll=false
        language: system
        files: \.(ts|tsx)$
        pass_filenames: false
```

### Test-Driven Development (TDD)

#### Red-Green-Refactor Cycle

1. **Red**: Write failing test
2. **Green**: Write minimal code to pass test
3. **Refactor**: Improve code while keeping tests passing

```typescript
// 1. Red: Write failing test
it("should format currency correctly", () => {
  expect(formatCurrency(1234.56)).toBe("$1,234.56");
});

// 2. Green: Implement minimal solution
function formatCurrency(amount: number): string {
  return `$${amount.toFixed(2)}`;
}

// 3. Refactor: Improve implementation
function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
}
```

## Resources

- [Testing Library Documentation](https://testing-library.com/)
- [Jest Documentation](https://jestjs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Playwright Documentation](https://playwright.dev/)
- [React Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
