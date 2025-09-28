# NEXUS Platform - Naming Conventions

## Overview

This document defines the naming conventions for the NEXUS platform to ensure consistency, readability, and maintainability across the entire codebase.

## General Principles

1. **Consistency**: Use the same naming convention throughout the project
2. **Readability**: Choose names that clearly describe the purpose
3. **Brevity**: Keep names concise but descriptive
4. **Standards Compliance**: Follow language-specific conventions

## Python Naming Conventions

### Files and Directories

- **Modules**: `snake_case.py` (e.g., `user_service.py`, `data_processor.py`)
- **Packages**: `snake_case` (e.g., `user_management/`, `data_processing/`)
- **Test Files**: `test_snake_case.py` (e.g., `test_user_service.py`)
- **Configuration Files**: `snake_case.yaml` or `snake_case.json`

### Classes

- **Class Names**: `PascalCase` (e.g., `UserService`, `DataProcessor`, `ConfigurationManager`)
- **Exception Classes**: `PascalCase` ending with `Error` or `Exception` (e.g., `ValidationError`, `ConfigurationException`)

### Functions and Methods

- **Functions**: `snake_case` (e.g., `process_data`, `validate_input`, `create_user`)
- **Methods**: `snake_case` (e.g., `get_user_data`, `update_configuration`)
- **Private Methods**: `_snake_case` (prefixed with single underscore)
- **Special Methods**: `__dunder_case__` (e.g., `__init__`, `__str__`)

### Variables

- **Variables**: `snake_case` (e.g., `user_data`, `config_file`, `error_message`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_CONNECTIONS`, `DEFAULT_TIMEOUT`)
- **Private Variables**: `_snake_case` (prefixed with single underscore)
- **Type Hints**: `snake_case` (e.g., `user_id: int`, `config_data: Dict[str, Any]`)

### Imports

```python
# Preferred order:
# 1. Standard library imports
# 2. Third-party imports
# 3. Local imports

import os
import sys
from typing import Dict, List, Optional

import requests
from fastapi import FastAPI

from config.config_manager import ConfigManager
from services.user_service import UserService
```

## TypeScript/JavaScript Naming Conventions

### Files and Directories

- **Components**: `PascalCase.tsx` (e.g., `UserProfile.tsx`, `DataTable.tsx`)
- **Pages**: `PascalCase.tsx` (e.g., `DashboardPage.tsx`, `SettingsPage.tsx`)
- **Services**: `camelCase.service.ts` (e.g., `userService.ts`, `apiClient.ts`)
- **Hooks**: `useCamelCase.ts` (e.g., `useAuth.ts`, `useApi.ts`)
- **Utils**: `camelCase.utils.ts` (e.g., `dateUtils.ts`, `stringUtils.ts`)
- **Types**: `PascalCase.types.ts` (e.g., `User.types.ts`, `ApiResponse.types.ts`)

### Components

- **Component Names**: `PascalCase` (e.g., `UserProfile`, `DataTable`, `NavigationBar`)
- **Props Interface**: `PascalCaseProps` (e.g., `UserProfileProps`, `DataTableProps`)

### Functions and Methods

- **Functions**: `camelCase` (e.g., `processData`, `validateInput`, `createUser`)
- **Methods**: `camelCase` (e.g., `getUserData`, `updateConfiguration`)
- **Private Methods**: `_camelCase` (prefixed with underscore)
- **Event Handlers**: `handleCamelCase` (e.g., `handleSubmit`, `handleClick`)

### Variables

- **Variables**: `camelCase` (e.g., `userData`, `configFile`, `errorMessage`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_CONNECTIONS`, `DEFAULT_TIMEOUT`)
- **Private Variables**: `_camelCase` (prefixed with underscore)

### Types and Interfaces

- **Types**: `PascalCase` (e.g., `UserData`, `ApiResponse`, `Configuration`)
- **Interfaces**: `IPascalCase` (e.g., `IUserService`, `IDataProcessor`)
- **Enums**: `PascalCase` (e.g., `UserRole`, `RequestStatus`)

## Database Naming Conventions

### Tables

- **Table Names**: `snake_case` (e.g., `user_accounts`, `financial_transactions`, `audit_logs`)
- **Primary Keys**: `table_name_id` (e.g., `user_id`, `transaction_id`)
- **Foreign Keys**: `referenced_table_id` (e.g., `user_id`, `account_id`)

### Columns

- **Column Names**: `snake_case` (e.g., `first_name`, `created_at`, `is_active`)
- **Boolean Columns**: `is_` or `has_` prefix (e.g., `is_active`, `has_permission`)
- **Timestamp Columns**: `_at` suffix (e.g., `created_at`, `updated_at`)
- **Relationship Columns**: `_id` suffix (e.g., `user_id`, `account_id`)

### Indexes

- **Index Names**: `idx_table_column` (e.g., `idx_users_email`, `idx_transactions_date`)

## API Naming Conventions

### Endpoints

- **Resource Names**: `kebab-case` (e.g., `/user-accounts`, `/financial-transactions`)
- **Actions**: `kebab-case` (e.g., `/users/:id/activate`, `/transactions/:id/cancel`)

### HTTP Methods

- **GET**: Read operations (e.g., `GET /users`, `GET /users/:id`)
- **POST**: Create operations (e.g., `POST /users`, `POST /transactions`)
- **PUT**: Update operations (e.g., `PUT /users/:id`, `PUT /transactions/:id`)
- **PATCH**: Partial update operations (e.g., `PATCH /users/:id`)
- **DELETE**: Delete operations (e.g., `DELETE /users/:id`)

### Response Fields

- **Field Names**: `camelCase` (e.g., `userId`, `createdAt`, `isActive`)
- **Error Fields**: `camelCase` (e.g., `errorCode`, `errorMessage`)

## Docker Naming Conventions

### Images

- **Image Names**: `kebab-case` (e.g., `nexus-backend`, `nexus-frontend`, `nexus-database`)
- **Tags**: `semantic-version` (e.g., `1.0.0`, `1.1.0-alpha`)

### Containers

- **Container Names**: `kebab-case` (e.g., `nexus-backend-dev`, `nexus-frontend-prod`)

### Services

- **Service Names**: `kebab-case` (e.g., `backend`, `frontend`, `database`, `redis`)

## Environment Variables

### Naming

- **Environment Variables**: `UPPER_SNAKE_CASE` (e.g., `DATABASE_URL`, `API_PORT`, `JWT_SECRET`)
- **Feature Flags**: `FEATURE_` prefix (e.g., `FEATURE_NEW_UI`, `FEATURE_ADVANCED_ANALYTICS`)

## File Paths and URLs

### File Paths

- **Configuration Files**: `config/` directory with `snake_case` names
- **Documentation**: `docs/` directory with `kebab-case` names
- **Scripts**: `scripts/` directory with `kebab-case` names

### URLs

- **API Routes**: `kebab-case` (e.g., `/api/user-accounts`, `/api/financial-reports`)
- **Web Routes**: `kebab-case` (e.g., `/dashboard`, `/user-profile`, `/settings`)

## Testing Conventions

### Test Files

- **Unit Tests**: `test_*.py` or `*.test.ts`
- **Integration Tests**: `test_integration_*.py` or `*integration.test.ts`
- **E2E Tests**: `test_e2e_*.py` or `*e2e.test.ts`

### Test Functions

- **Test Names**: `test_*` (e.g., `test_user_creation`, `test_data_validation`)
- **Test Classes**: `TestPascalCase` (e.g., `TestUserService`, `TestDataProcessor`)

## Configuration Files

### YAML Files

- **File Names**: `kebab-case.yaml` (e.g., `base-config.yaml`, `development-config.yaml`)
- **Keys**: `kebab-case` (e.g., `database-config`, `api-settings`)

### JSON Files

- **File Names**: `camelCase.json` (e.g., `package.json`, `tsconfig.json`)
- **Keys**: `camelCase` (e.g., `databaseConfig`, `apiSettings`)

## Git Conventions

### Branches

- **Main Branches**: `main`, `develop`
- **Feature Branches**: `feature/short-description` (e.g., `feature/user-authentication`)
- **Bug Fix Branches**: `bugfix/short-description` (e.g., `bugfix/fix-login-issue`)
- **Release Branches**: `release/version-number` (e.g., `release/1.0.0`)

### Commits

- **Commit Messages**: Imperative mood (e.g., "Add user authentication", "Fix login validation")
- **Types**: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`

## Enforcement Tools

### Python

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

### TypeScript/JavaScript

- **ESLint**: Linting
- **Prettier**: Code formatting
- **TypeScript Compiler**: Type checking

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 22.10.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 5.0.4
    hooks:
      - id: flake8
```

## Migration Strategy

### 1. Automated Tools

- Use automated tools to rename files and update imports
- Run formatters to standardize code style
- Use linters to identify violations

### 2. Gradual Migration

- Start with new code following conventions
- Gradually update existing code during refactoring
- Use CI/CD to enforce conventions on new changes

### 3. Documentation

- Update all documentation to reflect new conventions
- Create migration guides for developers
- Provide examples of correct naming

## Examples

### Python Example

```python
# Good
class UserService:
    MAX_CONNECTIONS = 100

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self._user_cache = {}

    def get_user_data(self, user_id: int) -> Optional[UserData]:
        if user_id in self._user_cache:
            return self._user_cache[user_id]

        user_data = self._fetch_user_from_database(user_id)
        self._user_cache[user_id] = user_data
        return user_data

    def _fetch_user_from_database(self, user_id: int) -> Optional[UserData]:
        # Implementation
        pass
```

### TypeScript Example

```typescript
// Good
interface UserService {
  getUserData(userId: number): Promise<UserData | null>;
  updateUserProfile(userId: number, profile: UserProfile): Promise<void>;
}

class UserProfileService implements UserService {
  private readonly maxConnections = 100;
  private userCache: Map<number, UserData> = new Map();

  public async getUserData(userId: number): Promise<UserData | null> {
    if (this.userCache.has(userId)) {
      return this.userCache.get(userId)!;
    }

    const userData = await this.fetchUserFromDatabase(userId);
    this.userCache.set(userId, userData);
    return userData;
  }

  private async fetchUserFromDatabase(
    userId: number,
  ): Promise<UserData | null> {
    // Implementation
    return null;
  }
}
```

This naming convention standard ensures consistency across the entire NEXUS platform codebase.
