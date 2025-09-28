# NEXUS Platform API Documentation

## Overview

The NEXUS Platform API is a comprehensive financial management and compliance platform built with FastAPI. This documentation provides complete information about all available endpoints, authentication, data models, and usage examples.

## Table of Contents

- [Authentication](#authentication)
- [Base URL](#base-url)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [API Endpoints](#api-endpoints)
  - [Authentication Endpoints](#authentication-endpoints)
  - [User Management](#user-management)
  - [Account Management](#account-management)
  - [Transaction Management](#transaction-management)
  - [Analytics Endpoints](#analytics-endpoints)
  - [Monitoring Endpoints](#monitoring-endpoints)
- [Data Models](#data-models)
- [Response Formats](#response-formats)
- [SDK Examples](#sdk-examples)
- [Webhooks](#webhooks)
- [Rate Limits](#rate-limits)
- [Changelog](#changelog)

## Authentication

The NEXUS Platform API uses JWT (JSON Web Tokens) for authentication. All API requests must include a valid JWT token in the Authorization header.

### Getting an Access Token

```bash
curl -X POST "https://api.nexus-platform.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your_password"
  }'
```

### Using the Access Token

```bash
curl -X GET "https://api.nexus-platform.com/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Base URL

- **Production**: `https://api.nexus-platform.com`
- **Staging**: `https://staging-api.nexus-platform.com`
- **Development**: `http://localhost:8000`

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Authenticated users**: 1000 requests per hour
- **Unauthenticated users**: 100 requests per hour
- **Burst limit**: 20 requests per minute

Rate limit headers are included in all responses:

- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

## Error Handling

The API uses standard HTTP status codes and returns detailed error information:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  }
}
```

### Common Error Codes

| Code               | Status | Description              |
| ------------------ | ------ | ------------------------ |
| `VALIDATION_ERROR` | 400    | Invalid input data       |
| `UNAUTHORIZED`     | 401    | Authentication required  |
| `FORBIDDEN`        | 403    | Insufficient permissions |
| `NOT_FOUND`        | 404    | Resource not found       |
| `RATE_LIMITED`     | 429    | Rate limit exceeded      |
| `INTERNAL_ERROR`   | 500    | Server error             |

## API Endpoints

### Authentication Endpoints

#### POST /api/v1/auth/login

Authenticate user and get access token.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### POST /api/v1/auth/register

Register a new user account.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### POST /api/v1/auth/refresh

Refresh access token using refresh token.

#### POST /api/v1/auth/logout

Logout and invalidate tokens.

### User Management

#### GET /api/v1/users/me

Get current user profile.

**Response:**

```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "created_at": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-15T10:30:00Z",
  "status": "active"
}
```

#### PUT /api/v1/users/me

Update current user profile.

#### GET /api/v1/users/{user_id}

Get user by ID (admin only).

#### PUT /api/v1/users/{user_id}

Update user by ID (admin only).

### Account Management

#### GET /api/v1/accounts

Get user's accounts.

**Query Parameters:**

- `type`: Filter by account type (checking, savings, credit, investment)
- `status`: Filter by account status (active, inactive, closed)
- `limit`: Number of results per page (default: 20)
- `offset`: Number of results to skip (default: 0)

**Response:**

```json
{
  "accounts": [
    {
      "id": 1,
      "name": "Primary Checking",
      "type": "checking",
      "balance": 2500.0,
      "currency": "USD",
      "status": "active",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

#### POST /api/v1/accounts

Create new account.

#### GET /api/v1/accounts/{account_id}

Get account details.

#### PUT /api/v1/accounts/{account_id}

Update account.

#### DELETE /api/v1/accounts/{account_id}

Delete account.

### Transaction Management

#### GET /api/v1/transactions

Get user's transactions.

**Query Parameters:**

- `account_id`: Filter by account ID
- `type`: Filter by transaction type (income, expense, transfer)
- `category_id`: Filter by category ID
- `start_date`: Start date (ISO 8601)
- `end_date`: End date (ISO 8601)
- `min_amount`: Minimum amount
- `max_amount`: Maximum amount
- `limit`: Number of results per page (default: 20)
- `offset`: Number of results to skip (default: 0)

**Response:**

```json
{
  "transactions": [
    {
      "id": 1,
      "account_id": 1,
      "amount": -50.0,
      "type": "expense",
      "description": "Grocery shopping",
      "category": "Food & Dining",
      "date": "2024-01-15T10:30:00Z",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

#### POST /api/v1/transactions

Create new transaction.

#### GET /api/v1/transactions/{transaction_id}

Get transaction details.

#### PUT /api/v1/transactions/{transaction_id}

Update transaction.

#### DELETE /api/v1/transactions/{transaction_id}

Delete transaction.

### Analytics Endpoints

#### GET /api/v1/analytics/dashboard

Get dashboard analytics data.

**Response:**

```json
{
  "total_balance": 2500.0,
  "monthly_income": 5000.0,
  "monthly_expenses": 3500.0,
  "savings_rate": 0.3,
  "top_categories": [
    {
      "category": "Food & Dining",
      "amount": 800.0,
      "percentage": 22.86
    }
  ],
  "monthly_trend": [
    {
      "month": "2024-01",
      "income": 5000.0,
      "expenses": 3500.0
    }
  ]
}
```

#### GET /api/v1/analytics/expenses

Get expense analytics.

#### GET /api/v1/analytics/income

Get income analytics.

#### GET /api/v1/analytics/categories

Get category analytics.

### Monitoring Endpoints

#### GET /api/v1/monitoring/health

Get system health status.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "2.0.0",
  "dependencies": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

#### GET /api/v1/monitoring/metrics

Get system metrics.

## Data Models

### User

```json
{
  "id": "integer",
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "created_at": "datetime",
  "last_login": "datetime",
  "status": "string (active, inactive, suspended)",
  "role": "string (user, admin, super_admin)"
}
```

### Account

```json
{
  "id": "integer",
  "user_id": "integer",
  "name": "string",
  "type": "string (checking, savings, credit, investment)",
  "balance": "decimal",
  "currency": "string",
  "status": "string (active, inactive, closed)",
  "created_at": "datetime"
}
```

### Transaction

```json
{
  "id": "integer",
  "account_id": "integer",
  "amount": "decimal",
  "type": "string (income, expense, transfer)",
  "description": "string",
  "category_id": "integer",
  "date": "datetime",
  "created_at": "datetime"
}
```

## Response Formats

All API responses follow a consistent format:

### Success Response

```json
{
  "data": { ... },
  "message": "Success",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": { ... }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## SDK Examples

### Python SDK

```python
from nexus_sdk import NexusClient

client = NexusClient(api_key="your_api_key")

# Get user profile
user = client.users.get_me()

# Get transactions
transactions = client.transactions.list(
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Create transaction
transaction = client.transactions.create({
    "account_id": 1,
    "amount": -50.00,
    "type": "expense",
    "description": "Coffee"
})
```

### JavaScript SDK

```javascript
import { NexusClient } from "@nexus/sdk";

const client = new NexusClient({ apiKey: "your_api_key" });

// Get user profile
const user = await client.users.getMe();

// Get transactions
const transactions = await client.transactions.list({
  startDate: "2024-01-01",
  endDate: "2024-01-31",
});

// Create transaction
const transaction = await client.transactions.create({
  accountId: 1,
  amount: -50.0,
  type: "expense",
  description: "Coffee",
});
```

## Webhooks

The API supports webhooks for real-time notifications:

### Webhook Events

- `transaction.created`
- `transaction.updated`
- `transaction.deleted`
- `account.created`
- `account.updated`
- `user.updated`

### Webhook Payload

```json
{
  "event": "transaction.created",
  "data": {
    "id": 1,
    "account_id": 1,
    "amount": -50.0,
    "type": "expense",
    "description": "Coffee"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Rate Limits

| Endpoint Type          | Limit         | Window   |
| ---------------------- | ------------- | -------- |
| Authentication         | 10 requests   | 1 minute |
| User Management        | 100 requests  | 1 hour   |
| Account Management     | 200 requests  | 1 hour   |
| Transaction Management | 500 requests  | 1 hour   |
| Analytics              | 50 requests   | 1 hour   |
| Monitoring             | 1000 requests | 1 hour   |

## Changelog

### Version 2.0.0 (2024-01-15)

- Added comprehensive analytics endpoints
- Implemented advanced monitoring
- Added webhook support
- Enhanced error handling
- Improved rate limiting

### Version 1.0.0 (2024-01-01)

- Initial API release
- Basic CRUD operations
- JWT authentication
- User and transaction management
