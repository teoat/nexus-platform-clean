# NEXUS Naming Conventions

This document outlines the naming conventions used throughout the NEXUS platform to ensure consistency and maintainability.

## Python Code

### General Rules

- Use `snake_case` for all identifiers (variables, functions, methods, modules)
- Use `PascalCase` for class names
- Use `UPPER_CASE` for constants
- Use descriptive, meaningful names
- Avoid abbreviations unless they are well-known (e.g., `id`, `url`, `api`)

### Files and Modules

- Module files: `snake_case.py`
- Package directories: `snake_case/`
- Test files: `test_*.py` or `*_test.py`
- Example: `user_service.py`, `database_connection.py`

### Classes

- Class names: `PascalCase`
- Abstract base classes: `AbstractPascalCase`
- Exception classes: `PascalCaseError`
- Examples: `UserService`, `DatabaseConnection`, `ValidationError`

### Functions and Methods

- Function names: `snake_case`
- Private methods: `_snake_case` (single underscore prefix)
- Protected methods: `__snake_case` (double underscore prefix)
- Examples: `get_user_profile()`, `_validate_input()`, `__setup_connection()`

### Variables

- Local variables: `snake_case`
- Instance variables: `snake_case`
- Class variables: `snake_case`
- Constants: `UPPER_CASE`
- Examples: `user_id`, `MAX_RETRIES`, `DEFAULT_TIMEOUT`

### Database

- Table names: `snake_case`
- Column names: `snake_case`
- Index names: `idx_table_column`
- Foreign key names: `fk_table_referenced_table`
- Examples: `user_profiles`, `transaction_amount`, `idx_users_email`

## TypeScript/JavaScript Code

### General Rules

- Use `camelCase` for variables, functions, and methods
- Use `PascalCase` for classes, interfaces, and types
- Use `UPPER_CASE` for constants
- Use descriptive, meaningful names

### Files

- Component files: `PascalCase.tsx`
- Utility files: `camelCase.ts`
- Test files: `*.test.tsx` or `*.spec.tsx`

### Components

- Component names: `PascalCase`
- File names: `ComponentName.tsx`
- Examples: `UserProfile.tsx`, `TransactionList.tsx`

### Functions and Variables

- Functions: `camelCase`
- Variables: `camelCase`
- Constants: `UPPER_CASE`
- Examples: `getUserData()`, `userProfile`, `API_BASE_URL`

## API Endpoints

### REST API

- Use `kebab-case` for URL paths
- Use plural nouns for resource names
- Examples:
  - `GET /api/users`
  - `POST /api/users`
  - `GET /api/users/{user-id}`
  - `PUT /api/users/{user-id}`

### GraphQL

- Type names: `PascalCase`
- Field names: `camelCase`
- Enum values: `UPPER_CASE`
- Examples: `UserProfile`, `getUserById`, `USER_STATUS`

## Configuration

### Environment Variables

- Prefix: `NEXUS_`
- Format: `NEXUS_SECTION_KEY`
- Examples: `NEXUS_DB_HOST`, `NEXUS_JWT_SECRET`, `NEXUS_REDIS_PORT`

### Configuration Files

- File names: `snake_case.ext`
- Section names: `snake_case`
- Key names: `snake_case`
- Examples: `database_config.json`, `app_settings.yaml`

## Docker and Infrastructure

### Images

- Image names: `nexus-service-name`
- Examples: `nexus-user-service`, `nexus-api-gateway`

### Containers

- Container names: `nexus-service-name`
- Examples: `nexus-postgres`, `nexus-redis`

### Kubernetes

- Resource names: `nexus-service-name`
- Label keys: `app.kubernetes.io/name`
- Label values: `nexus-service-name`

## Documentation

### Files

- Documentation files: `kebab-case.md`
- Examples: `api-reference.md`, `deployment-guide.md`

### Headings

- Use sentence case for headings
- Be descriptive and specific

## Git

### Branches

- Feature branches: `feature/description-of-feature`
- Bug fix branches: `fix/description-of-bug`
- Hotfix branches: `hotfix/description-of-issue`

### Commits

- Use imperative mood: "Add feature" not "Added feature"
- Keep first line under 50 characters
- Use detailed description for complex changes

## Testing

### Test Files

- Unit tests: `test_module.py`
- Integration tests: `test_integration_module.py`
- E2E tests: `test_e2e_feature.py`

### Test Functions

- Test functions: `test_descriptive_name`
- Examples: `test_user_creation()`, `test_transaction_validation()`

## Examples

### Python

```python
# Good
class UserService:
    def __init__(self, database_connection):
        self.db_connection = database_connection
        self.max_retries = 3

    def get_user_profile(self, user_id: str) -> UserProfile:
        """Get user profile by ID."""
        return self._fetch_user_from_database(user_id)

    def _fetch_user_from_database(self, user_id: str) -> UserProfile:
        """Private method to fetch user from database."""
        pass

# Bad
class userService:  # Wrong: not PascalCase
    def __init__(self, dbConnection):  # Wrong: not snake_case
        self.DB_CONNECTION = dbConnection  # Wrong: not snake_case

    def GetUserProfile(self, userId):  # Wrong: not snake_case
        pass
```

### TypeScript

```typescript
// Good
interface UserProfile {
  userId: string;
  emailAddress: string;
  isActive: boolean;
}

class UserService {
  private readonly apiBaseUrl: string;

  constructor(apiBaseUrl: string) {
    this.apiBaseUrl = apiBaseUrl;
  }

  public async getUserProfile(userId: string): Promise<UserProfile> {
    return this.fetchUserFromApi(userId);
  }

  private async fetchUserFromApi(userId: string): Promise<UserProfile> {
    // Implementation
  }
}

// Bad
interface userProfile {
  // Wrong: not PascalCase
  userID: string; // Wrong: inconsistent naming
  email_address: string; // Wrong: snake_case in TypeScript
}

class user_service {
  // Wrong: not PascalCase
  constructor(api_base_url: string) {
    // Wrong: snake_case
  }
}
```

## Enforcement

- Use linters and formatters (black, flake8 for Python; ESLint, Prettier for TypeScript)
- Code reviews should check for naming convention compliance
- Automated tests should validate naming patterns where possible
- Documentation should be updated when conventions change

## Exceptions

- Third-party library integrations may use their own conventions
- Legacy code being migrated can be updated gradually
- Domain-specific terms may have established naming patterns
