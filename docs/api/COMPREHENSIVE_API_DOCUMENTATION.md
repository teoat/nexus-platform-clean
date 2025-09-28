# NEXUS Platform - Comprehensive API Documentation

## 🚀 **API OVERVIEW**

The NEXUS Platform provides a comprehensive RESTful API for financial management, compliance, and analytics. This documentation covers all endpoints, authentication, data models, and integration examples.

## 📋 **TABLE OF CONTENTS**

1. [Authentication](#authentication)
2. [Base URL & Versioning](#base-url--versioning)
3. [Error Handling](#error-handling)
4. [Rate Limiting](#rate-limiting)
5. [API Endpoints](#api-endpoints)
6. [Data Models](#data-models)
7. [SDK Examples](#sdk-examples)
8. [Webhooks](#webhooks)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)

## 🔐 **AUTHENTICATION**

### **JWT Token Authentication**

All API requests require authentication using JWT tokens.

```http
Authorization: Bearer <your_jwt_token>
```

### **Token Types**

- **Access Token**: Short-lived (30 minutes), used for API requests
- **Refresh Token**: Long-lived (7 days), used to obtain new access tokens

### **Authentication Endpoints**

#### **Login**

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "your_password"
}
```

**Response:**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "user@example.com",
    "role": "user",
    "is_active": true
  }
}
```

#### **Refresh Token**

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "your_refresh_token"
}
```

#### **Logout**

```http
POST /api/v1/auth/logout
Authorization: Bearer <your_access_token>
```

## 🌐 **BASE URL & VERSIONING**

### **Base URLs**

- **Production**: `https://api.nexus-platform.com`
- **Staging**: `https://staging-api.nexus-platform.com`
- **Development**: `http://localhost:8000`

### **API Versioning**

- **Current Version**: v1
- **Version Header**: `Accept: application/vnd.nexus.v1+json`
- **URL Versioning**: `/api/v1/`

## ⚠️ **ERROR HANDLING**

### **Error Response Format**

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789"
  }
}
```

### **HTTP Status Codes**

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error

## 🚦 **RATE LIMITING**

- **Limit**: 100 requests per minute per user
- **Headers**:
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

## 📡 **API ENDPOINTS**

### **User Management**

#### **Get Users**

```http
GET /api/v1/users
Authorization: Bearer <token>
```

**Query Parameters:**

- `skip` (int): Number of users to skip (default: 0)
- `limit` (int): Number of users to return (default: 100, max: 1000)
- `search` (string): Search term for username or email
- `role` (string): Filter by user role
- `is_active` (boolean): Filter by active status

**Response:**

```json
{
  "users": [
    {
      "id": 1,
      "username": "user@example.com",
      "full_name": "John Doe",
      "role": "user",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "last_login": "2024-01-15T09:15:00Z"
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 100
}
```

#### **Get User by ID**

```http
GET /api/v1/users/{user_id}
Authorization: Bearer <token>
```

#### **Create User**

```http
POST /api/v1/users
Authorization: Bearer <token>
Content-Type: application/json

{
  "username": "newuser@example.com",
  "password": "secure_password",
  "full_name": "Jane Doe",
  "role": "user"
}
```

#### **Update User**

```http
PUT /api/v1/users/{user_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "Jane Smith",
  "is_active": true
}
```

#### **Delete User**

```http
DELETE /api/v1/users/{user_id}
Authorization: Bearer <token>
```

### **Transaction Management**

#### **Get Transactions**

```http
GET /api/v1/transactions
Authorization: Bearer <token>
```

**Query Parameters:**

- `skip` (int): Number of transactions to skip
- `limit` (int): Number of transactions to return
- `type` (string): Transaction type (deposit, withdrawal, transfer, payment)
- `status` (string): Transaction status (pending, completed, failed)
- `start_date` (string): Start date (ISO 8601)
- `end_date` (string): End date (ISO 8601)
- `min_amount` (float): Minimum amount
- `max_amount` (float): Maximum amount

**Response:**

```json
{
  "transactions": [
    {
      "id": 1,
      "user_id": 1,
      "type": "deposit",
      "amount": 1000.0,
      "description": "Salary deposit",
      "status": "completed",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 50,
  "skip": 0,
  "limit": 100
}
```

#### **Create Transaction**

```http
POST /api/v1/transactions
Authorization: Bearer <token>
Content-Type: application/json

{
  "type": "deposit",
  "amount": 500.00,
  "description": "Cash deposit",
  "category_id": 1
}
```

#### **Update Transaction**

```http
PUT /api/v1/transactions/{transaction_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "description": "Updated description",
  "status": "completed"
}
```

### **Analytics**

#### **Get Financial Analytics**

```http
GET /api/v1/analytics/financial
Authorization: Bearer <token>
```

**Query Parameters:**

- `period` (string): Time period (daily, weekly, monthly, quarterly, yearly)
- `start_date` (string): Start date (ISO 8601)
- `end_date` (string): End date (ISO 8601)

**Response:**

```json
{
  "period": "monthly",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-31T23:59:59Z",
  "metrics": {
    "total_income": 5000.0,
    "total_expenses": 3500.0,
    "net_income": 1500.0,
    "savings_rate": 0.3,
    "transaction_count": 45
  },
  "breakdown": {
    "by_category": [
      {
        "category": "Food & Dining",
        "amount": 800.0,
        "percentage": 22.86
      }
    ],
    "by_type": [
      {
        "type": "deposit",
        "amount": 5000.0,
        "count": 2
      }
    ]
  }
}
```

#### **Get Spending Trends**

```http
GET /api/v1/analytics/trends
Authorization: Bearer <token>
```

#### **Get Budget Analysis**

```http
GET /api/v1/analytics/budget
Authorization: Bearer <token>
```

### **Dashboard**

#### **Get Dashboard Data**

```http
GET /api/v1/dashboard
Authorization: Bearer <token>
```

**Response:**

```json
{
  "financial_summary": {
    "total_balance": 125000.0,
    "monthly_income": 8500.0,
    "monthly_expenses": 6200.0,
    "net_worth": 118800.0
  },
  "recent_transactions": [
    {
      "id": 1,
      "type": "deposit",
      "amount": 1000.0,
      "description": "Salary deposit",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "alerts": [
    {
      "type": "budget_warning",
      "message": "You've spent 80% of your monthly budget",
      "severity": "warning"
    }
  ]
}
```

## 📊 **DATA MODELS**

### **User Model**

```json
{
  "id": "integer",
  "username": "string (email)",
  "password": "string (hashed)",
  "full_name": "string",
  "role": "enum (admin, compliance_officer, financial_analyst, auditor, viewer)",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime",
  "last_login": "datetime"
}
```

### **Transaction Model**

```json
{
  "id": "integer",
  "user_id": "integer",
  "type": "enum (deposit, withdrawal, transfer, payment, refund, fee, interest)",
  "amount": "decimal",
  "description": "string",
  "status": "enum (pending, completed, failed, cancelled, reversed)",
  "category_id": "integer",
  "account_id": "integer",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### **Account Model**

```json
{
  "id": "integer",
  "user_id": "integer",
  "name": "string",
  "type": "enum (checking, savings, investment, credit, loan)",
  "balance": "decimal",
  "currency": "string (ISO 4217)",
  "status": "enum (active, inactive, closed)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## 🛠️ **SDK EXAMPLES**

### **Python SDK Example**

```python
import requests
from datetime import datetime, timedelta

class NexusAPI:
    def __init__(self, base_url, access_token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

    def get_transactions(self, limit=100, skip=0):
        url = f"{self.base_url}/api/v1/transactions"
        params = {'limit': limit, 'skip': skip}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def create_transaction(self, transaction_data):
        url = f"{self.base_url}/api/v1/transactions"
        response = requests.post(url, headers=self.headers, json=transaction_data)
        return response.json()

    def get_analytics(self, period='monthly'):
        url = f"{self.base_url}/api/v1/analytics/financial"
        params = {'period': period}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

# Usage
api = NexusAPI('https://api.nexus-platform.com', 'your_access_token')
transactions = api.get_transactions(limit=50)
analytics = api.get_analytics(period='monthly')
```

### **JavaScript SDK Example**

```javascript
class NexusAPI {
  constructor(baseUrl, accessToken) {
    this.baseUrl = baseUrl;
    this.headers = {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    };
  }

  async getTransactions(limit = 100, skip = 0) {
    const url = `${this.baseUrl}/api/v1/transactions`;
    const params = new URLSearchParams({ limit, skip });
    const response = await fetch(`${url}?${params}`, {
      headers: this.headers,
    });
    return await response.json();
  }

  async createTransaction(transactionData) {
    const url = `${this.baseUrl}/api/v1/transactions`;
    const response = await fetch(url, {
      method: "POST",
      headers: this.headers,
      body: JSON.stringify(transactionData),
    });
    return await response.json();
  }

  async getAnalytics(period = "monthly") {
    const url = `${this.baseUrl}/api/v1/analytics/financial`;
    const params = new URLSearchParams({ period });
    const response = await fetch(`${url}?${params}`, {
      headers: this.headers,
    });
    return await response.json();
  }
}

// Usage
const api = new NexusAPI("https://api.nexus-platform.com", "your_access_token");
const transactions = await api.getTransactions(50);
const analytics = await api.getAnalytics("monthly");
```

## 🔗 **WEBHOOKS**

### **Webhook Configuration**

```http
POST /api/v1/webhooks
Authorization: Bearer <token>
Content-Type: application/json

{
  "url": "https://your-app.com/webhooks/nexus",
  "events": ["transaction.created", "transaction.updated", "user.created"],
  "secret": "your_webhook_secret"
}
```

### **Webhook Events**

- `transaction.created` - New transaction created
- `transaction.updated` - Transaction updated
- `transaction.deleted` - Transaction deleted
- `user.created` - New user created
- `user.updated` - User updated
- `budget.exceeded` - Budget limit exceeded

### **Webhook Payload**

```json
{
  "event": "transaction.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "id": 1,
    "type": "deposit",
    "amount": 1000.0,
    "user_id": 1
  }
}
```

## 🧪 **TESTING**

### **API Testing with cURL**

#### **Authentication Test**

```bash
curl -X POST https://api.nexus-platform.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test@example.com", "password": "test123"}'
```

#### **Get Transactions Test**

```bash
curl -X GET https://api.nexus-platform.com/api/v1/transactions \
  -H "Authorization: Bearer your_access_token"
```

#### **Create Transaction Test**

```bash
curl -X POST https://api.nexus-platform.com/api/v1/transactions \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json" \
  -d '{"type": "deposit", "amount": 500.00, "description": "Test deposit"}'
```

### **Postman Collection**

Import the NEXUS API Postman collection for comprehensive API testing.

## 🔧 **TROUBLESHOOTING**

### **Common Issues**

#### **401 Unauthorized**

- Check if the access token is valid and not expired
- Verify the Authorization header format: `Bearer <token>`
- Try refreshing the token using the refresh endpoint

#### **403 Forbidden**

- Verify that your user role has permission for the requested resource
- Check if the user account is active

#### **429 Rate Limited**

- Wait for the rate limit window to reset
- Implement exponential backoff in your client
- Consider upgrading to a higher rate limit tier

#### **422 Validation Error**

- Check the error details for specific field validation issues
- Ensure all required fields are provided
- Verify data types and formats match the API specification

### **Debug Headers**

Include these headers in your requests for better debugging:

- `X-Debug-Mode: true` - Enable detailed error responses
- `X-Request-ID: your-request-id` - Track requests across logs

### **Support**

- **Documentation**: https://docs.nexus-platform.com
- **Status Page**: https://status.nexus-platform.com
- **Support Email**: api-support@nexus-platform.com
- **GitHub Issues**: https://github.com/nexus-platform/api/issues

---

**Last Updated**: January 15, 2024
**API Version**: v1.0.0
**Documentation Version**: 1.0.0
