# TypeScript Guidelines & Best Practices

## Overview

This document outlines the TypeScript standards and practices for the Nexus platform. Following these guidelines ensures type safety, maintainability, and consistency across the codebase.

## Table of Contents

1. [Configuration](#configuration)
2. [File Structure](#file-structure)
3. [Naming Conventions](#naming-conventions)
4. [Type Definitions](#type-definitions)
5. [Best Practices](#best-practices)
6. [Code Review Checklist](#code-review-checklist)
7. [Migration Strategy](#migration-strategy)

## Configuration

### Base Configuration (`tsconfig.base.json`)

All projects extend from a shared base configuration:

```json
{
  "compilerOptions": {
    "target": "es2018",
    "lib": ["dom", "dom.iterable", "es2018"],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    },
    "downlevelIteration": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noImplicitReturns": true,
    "noUnusedLocals": false,
    "noUnusedParameters": false
  }
}
```

### Project-Specific Overrides

Frontend (Relaxed for Development):
```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "strict": false,
    "noImplicitAny": false,
    "strictNullChecks": false
  }
}
```

Backend (Strict):
```json
{
  "extends": "../tsconfig.base.json",
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "noEmit": false
  }
}
```

## File Structure

```
src/
├── types/              # Global type definitions
│   ├── api.ts         # API response types
│   ├── models.ts      # Data model types
│   └── index.ts       # Type exports
├── interfaces/         # Component and service interfaces
├── components/         # React components
├── services/           # Business logic services
├── hooks/             # Custom React hooks
├── utils/             # Utility functions
└── constants/         # Application constants
```

## Naming Conventions

### Interfaces & Types

```typescript
// ✅ Good: PascalCase for interfaces
interface UserProfile {
  id: string;
  email: string;
  preferences: UserPreferences;
}

// ✅ Good: PascalCase for types
type UserStatus = 'active' | 'inactive' | 'suspended';

// ✅ Good: Descriptive names
type ApiResponse<T> = {
  success: boolean;
  data: T;
  error?: string;
};
```

### Variables & Functions

```typescript
// ✅ Good: camelCase for variables and functions
const userProfile: UserProfile;
function fetchUserData(userId: string): Promise<UserProfile>;

// ✅ Good: Descriptive names
const isUserAuthenticated: boolean;
function validateUserInput(input: UserInput): ValidationResult;
```

### Generics

```typescript
// ✅ Good: Single letters for simple generics
function createList<T>(): T[];

// ✅ Good: Descriptive for complex generics
function processData<TData, TError = Error>(
  data: TData
): Result<TData, TError>;
```

## Type Definitions

### API Responses

```typescript
// ✅ Good: Typed API responses
interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: ApiError;
  meta?: PaginationMeta;
}

interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

// Usage
async function fetchUsers(): Promise<ApiResponse<User[]>> {
  const response = await api.get('/users');
  return response.data;
}
```

### Component Props

```typescript
// ✅ Good: Interface for component props
interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  onClick: (event: React.MouseEvent<HTMLButtonElement>) => void;
}

// ✅ Good: Extract complex prop types
interface DataTableProps<T> {
  data: T[];
  columns: ColumnDefinition<T>[];
  loading?: boolean;
  onRowClick?: (row: T) => void;
}
```

### State Management

```typescript
// ✅ Good: Discriminated unions for state
type LoadingState = { status: 'loading' };
type SuccessState<T> = { status: 'success'; data: T };
type ErrorState = { status: 'error'; error: string };

type AsyncState<T> = LoadingState | SuccessState<T> | ErrorState;

// Usage
function useAsyncData<T>(url: string): AsyncState<T> {
  // Implementation
}
```

### Error Handling

```typescript
// ✅ Good: Custom error classes
class ValidationError extends Error {
  constructor(
    message: string,
    public field: string,
    public code: string
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public response?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}
```

## Best Practices

### 1. Avoid `any` Type

```typescript
// ❌ Bad: Using any
function processData(data: any): any {
  return data.map((item: any) => item.value);
}

// ✅ Good: Proper typing
interface DataItem {
  id: string;
  value: number;
  metadata?: Record<string, unknown>;
}

function processData(data: DataItem[]): number[] {
  return data.map(item => item.value);
}
```

### 2. Use Utility Types

```typescript
// ✅ Good: Built-in utility types
type PartialUser = Partial<User>;
type RequiredUser = Required<User>;
type ReadonlyUser = Readonly<User>;
type UserKeys = keyof User;

// ✅ Good: Custom utility types
type NonNullableUser = NonNullable<User>;
type UserWithoutId = Omit<User, 'id'>;
type UserUpdate = Partial<Pick<User, 'name' | 'email'>>;
```

### 3. Type Guards

```typescript
// ✅ Good: Type guards for runtime checks
function isUser(obj: any): obj is User {
  return obj && typeof obj.id === 'string' && typeof obj.email === 'string';
}

function isApiError(error: unknown): error is ApiError {
  return error instanceof Error && 'statusCode' in error;
}

// Usage
if (isUser(data)) {
  console.log(data.email); // TypeScript knows this is a User
}
```

### 4. Generic Constraints

```typescript
// ✅ Good: Constrained generics
interface HasId {
  id: string;
}

function findById<T extends HasId>(items: T[], id: string): T | undefined {
  return items.find(item => item.id === id);
}

// Usage
const user = findById(users, '123'); // TypeScript knows this is User
```

### 5. Function Overloads

```typescript
// ✅ Good: Function overloads for different parameter types
function createElement(tag: string): HTMLElement;
function createElement(tag: string, props: Record<string, any>): HTMLElement;
function createElement(tag: string, children: string): HTMLElement;
function createElement(
  tag: string,
  propsOrChildren?: Record<string, any> | string
): HTMLElement {
  // Implementation
}
```

## Code Review Checklist

### Type Safety
- [ ] All functions have explicit return types
- [ ] No `any` types (except third-party libraries)
- [ ] All variables are properly typed
- [ ] Interface properties are correctly typed
- [ ] Generic constraints are appropriate

### API Design
- [ ] API responses are typed with `ApiResponse<T>`
- [ ] Error types extend `Error` class
- [ ] Async functions return `Promise<T>`
- [ ] Optional parameters use `?:` syntax

### Component Types
- [ ] Props interfaces are defined
- [ ] Event handlers are properly typed
- [ ] Children prop types are correct
- [ ] Ref types are properly forwarded

### State Management
- [ ] State types use discriminated unions
- [ ] Reducer actions are typed
- [ ] Context providers have proper types
- [ ] Store selectors return correct types

### Testing
- [ ] Test utilities have proper types
- [ ] Mock objects match real types
- [ ] Test data is properly typed

## Migration Strategy

### Phase 1: Foundation (Current)
- ✅ Base configuration established
- ✅ Critical errors fixed
- ✅ Build integration complete
- ✅ Pre-commit hooks configured

### Phase 2: Enhancement (Next 3 Months)
- [ ] Enable `strictNullChecks` in development
- [ ] Add comprehensive error boundaries
- [ ] Implement discriminated unions for state
- [ ] Add type coverage monitoring (when tool compatibility resolved)

### Phase 3: Excellence (6+ Months)
- [ ] Full strict mode enabled
- [ ] 100% type coverage achieved
- [ ] Advanced utility types implemented
- [ ] Performance optimizations with types

## Tools & Scripts

### Development Scripts

```json
{
  "scripts": {
    "type-check": "tsc --noEmit",
    "type-check:watch": "tsc --noEmit --watch",
    "type-coverage": "type-coverage",
    "build:types": "tsc --emitDeclarationOnly"
  }
}
```

### VS Code Configuration

```json
// .vscode/settings.json
{
  "typescript.preferences.includePackageJsonAutoImports": "auto",
  "typescript.suggest.autoImports": true,
  "typescript.preferences.quoteStyle": "single",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  },
  "typescript.preferences.preferTypeOnlyAutoImports": true
}
```

### ESLint Configuration

```json
// .eslintrc.js
module.exports = {
  extends: [
    'react-app',
    '@typescript-eslint/recommended'
  ],
  rules: {
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/explicit-function-return-type': 'off',
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/prefer-optional-chain': 'error',
    '@typescript-eslint/prefer-nullish-coalescing': 'error'
  }
};
```

## Common Patterns

### Higher-Order Components

```typescript
// ✅ Good: Properly typed HOC
function withLoading<T extends object>(
  Component: React.ComponentType<T>
) {
  return function WithLoadingComponent(props: T & { loading?: boolean }) {
    const { loading, ...restProps } = props;

    if (loading) return <Spinner />;

    return <Component {...(restProps as T)} />;
  };
}
```

### Custom Hooks

```typescript
// ✅ Good: Typed custom hooks
function useApi<T>(
  url: string,
  options?: RequestInit
): {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
} {
  // Implementation
}
```

### Context Providers

```typescript
// ✅ Good: Typed context
interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

const ThemeContext = React.createContext<ThemeContextType | undefined>(undefined);

function useTheme(): ThemeContextType {
  const context = React.useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
```

## Troubleshooting

### Common Issues

1. **"Cannot find module" errors**
   - Check `tsconfig.json` paths configuration
   - Ensure file extensions are correct
   - Verify module resolution settings

2. **Type inference issues**
   - Add explicit type annotations
   - Use `as const` for literal types
   - Check generic constraints

3. **Build performance**
   - Use `skipLibCheck: true`
   - Enable incremental compilation
   - Use project references for monorepos

### Getting Help

- Check existing type definitions in `src/types/`
- Review similar patterns in the codebase
- Consult TypeScript documentation
- Ask in the development channel for complex type issues

---

*This document is living and should be updated as new patterns emerge and TypeScript features evolve.*</content>
</xai:function_call">Create comprehensive TypeScript documentation