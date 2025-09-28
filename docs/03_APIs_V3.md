# NEXUS Platform V3.0 - Comprehensive API Documentation

## 🌐 **API Overview**

The NEXUS Platform V3.0 provides a comprehensive REST API with enhanced authentication, Frenly AI capabilities, data standardization, and project-trading intersections.

## 🔗 **Base Configuration**

### **Base URL**

```
Development: http://localhost:8000
Production: https://api.nexus-platform.com
```

### **API Versioning**

```
Current Version: v3.0
Legacy Support: v1.0 (maintained for backward compatibility)
```

### **Content Types**

```
Request: application/json
Response: application/json
File Upload: multipart/form-data
```

## 🔐 **Authentication**

### **Authentication Methods**

1. **JWT Bearer Token** (Primary)
2. **OAuth 2.0** (Google, Microsoft, LinkedIn, GitHub)
3. **API Key** (Service-to-service communication)

### **JWT Token Structure**

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_id",
    "email": "user@example.com",
    "role": "user",
    "pov_role": "financial_examiner",
    "iat": 1640995200,
    "exp": 1640998800,
    "type": "access"
  }
}
```

## 📚 **API Endpoints**

## 🔑 **Enhanced Authentication API**

### **Base Path**: `/api/v3/auth`

#### **POST** `/register`

Register a new user with enhanced features.

**Request Body:**

```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "full_name": "string",
  "role": "user",
  "primary_pov_role": "financial_examiner",
  "secondary_pov_roles": ["auditor", "compliance_officer"],
  "analysis_mode": "multi_pov",
  "ai_intervention_level": "assisted"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "username": "string",
    "email": "string",
    "full_name": "string",
    "primary_pov_role": "financial_examiner",
    "secondary_pov_roles": ["auditor", "compliance_officer"],
    "analysis_mode": "multi_pov",
    "ai_intervention_level": "assisted",
    "is_active": true,
    "created_at": "2024-12-24T00:00:00Z"
  },
  "message": "User registered successfully"
}
```

#### **POST** `/login`

Login with email and password.

**Request Body:**

```json
{
  "email": "string",
  "password": "string"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "access_token": "jwt_token",
    "refresh_token": "jwt_refresh_token",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": "uuid",
      "username": "string",
      "email": "string",
      "primary_pov_role": "financial_examiner"
    }
  }
}
```

#### **POST** `/oauth/login`

Login with OAuth provider.

**Request Body:**

```json
{
  "provider": "google",
  "access_token": "oauth_access_token"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "access_token": "jwt_token",
    "refresh_token": "jwt_refresh_token",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": "uuid",
      "username": "string",
      "email": "string",
      "primary_pov_role": "financial_examiner",
      "oauth_provider": "google"
    }
  }
}
```

#### **POST** `/refresh`

Refresh access token.

**Request Body:**

```json
{
  "refresh_token": "jwt_refresh_token"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "access_token": "new_jwt_token",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

#### **POST** `/pov/configure`

Configure user's POV settings.

**Request Body:**

```json
{
  "primary_role": "financial_examiner",
  "secondary_roles": ["auditor", "compliance_officer"],
  "analysis_mode": "multi_pov",
  "evidence_retention": "extended",
  "ai_intervention": "assisted"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "message": "POV configuration updated successfully",
    "user": {
      "id": "uuid",
      "primary_pov_role": "financial_examiner",
      "secondary_pov_roles": ["auditor", "compliance_officer"],
      "analysis_mode": "multi_pov",
      "ai_intervention_level": "assisted"
    }
  }
}
```

#### **GET** `/me`

Get current user information.

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "username": "string",
    "email": "string",
    "full_name": "string",
    "primary_pov_role": "financial_examiner",
    "secondary_pov_roles": ["auditor"],
    "analysis_mode": "multi_pov",
    "ai_intervention_level": "assisted",
    "is_active": true,
    "created_at": "2024-12-24T00:00:00Z",
    "last_login_at": "2024-12-24T12:00:00Z"
  }
}
```

## 🤖 **Frenly AI API**

### **Base Path**: `/api/v3/frenly-ai`

#### **GET** `/status`

Get Frenly AI system status.

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**Response:**

```json
{
  "success": true,
  "data": {
    "status": "idle",
    "active_tasks": 2,
    "completed_tasks": 150,
    "failed_tasks": 3,
    "learning_mode": true,
    "system_health": "excellent",
    "last_activity": "2024-12-24T12:00:00Z",
    "uptime": 86400,
    "memory_usage": 0.45,
    "cpu_usage": 0.23,
    "available_tools": [
      "database_optimizer",
      "security_scanner",
      "data_reconciler",
      "fraud_detector"
    ],
    "recent_actions": [
      {
        "action": "system_maintenance",
        "timestamp": "2024-12-24T11:30:00Z",
        "status": "completed"
      }
    ]
  }
}
```

#### **POST** `/tasks`

Create a new Frenly AI task.

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**Request Body:**

```json
{
  "type": "system_maintenance",
  "title": "Database Optimization",
  "description": "Optimize database performance and clean up logs",
  "priority": "medium",
  "parameters": {
    "cleanup_logs": true,
    "optimize_indexes": true,
    "vacuum_database": true
  }
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": "task_uuid",
    "user_id": "user_uuid",
    "type": "system_maintenance",
    "title": "Database Optimization",
    "description": "Optimize database performance and clean up logs",
    "priority": "medium",
    "status": "pending",
    "progress": 0,
    "requires_approval": true,
    "estimated_duration": 5,
    "created_at": "2024-12-24T12:00:00Z"
  }
}
```

#### **POST** `/tasks/{task_id}/execute`

Execute a Frenly AI task.

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**Response:**

```json
{
  "success": true,
  "data": {
    "task_id": "task_uuid",
    "response_type": "execute_safe",
    "content": "System maintenance completed successfully. Database optimized, old logs cleaned, and statistics updated.",
    "confidence": 0.95,
    "actions": [
      {
        "type": "database_optimization",
        "status": "completed",
        "details": "Database vacuumed and analyzed",
        "logs_cleaned": 150
      }
    ],
    "requires_approval": false,
    "reasoning": "Routine system maintenance to ensure optimal performance",
    "evidence": [
      "Database optimization completed",
      "Log cleanup successful",
      "Statistics updated"
    ],
    "created_at": "2024-12-24T12:05:00Z"
  }
}
```

#### **GET** `/tasks`

Get user's Frenly AI tasks.

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**Query Parameters:**

- `limit` (optional): Number of tasks to return (default: 50)
- `offset` (optional): Number of tasks to skip (default: 0)
- `status` (optional): Filter by task status
- `type` (optional): Filter by task type

**Response:**

```json
{
  "success": true,
  "data": [
    {
      "id": "task_uuid",
      "type": "system_maintenance",
      "title": "Database Optimization",
      "status": "completed",
      "progress": 100,
      "created_at": "2024-12-24T12:00:00Z",
      "completed_at": "2024-12-24T12:05:00Z"
    }
  ],
  "pagination": {
    "total": 25,
    "limit": 50,
    "offset": 0,
    "has_next": false,
    "has_prev": false
  }
}
```

#### **POST** `/conversations`

Start a new conversation with Frenly AI.

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": "conversation_uuid",
    "user_id": "user_uuid",
    "messages": [],
    "context": {},
    "status": "active",
    "expires_at": "2024-12-25T12:00:00Z",
    "created_at": "2024-12-24T12:00:00Z"
  }
}
```

#### **POST** `/conversations/{conversation_id}/messages`

Send a message to Frenly AI.

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**Request Body:**

```json
{
  "message": "Help me analyze this financial data for potential fraud indicators"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "task_id": "response_uuid",
    "response_type": "suggest",
    "content": "I'll help you analyze the financial data for fraud indicators. Let me examine the patterns and identify potential red flags.",
    "confidence": 0.87,
    "actions": [
      {
        "type": "fraud_analysis",
        "status": "pending",
        "description": "Analyze financial patterns for fraud indicators"
      }
    ],
    "requires_approval": true,
    "reasoning": "Fraud analysis requires careful examination of financial patterns",
    "evidence": [
      "Transaction pattern analysis",
      "Anomaly detection results",
      "Historical comparison data"
    ],
    "created_at": "2024-12-24T12:00:00Z"
  }
}
```

## 📊 **Data Standardization API**

### **Base Path**: `/api/v3/data`

#### **POST** `/standardize`

Standardize data before reconciliation.

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**Request Body:**

```json
{
  "raw_data": [
    {
      "date": "2024-12-01",
      "amount": "$1,234.56",
      "description": "Office Supplies",
      "category": "expenses"
    }
  ],
  "data_source": "bank_statement"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "standardized_data": [
      {
        "date": "2024-12-01T00:00:00Z",
        "amount": 1234.56,
        "description": "Office Supplies",
        "category": "office_supplies"
      }
    ],
    "quality_metrics": {
      "completeness": 95.0,
      "accuracy": 98.0,
      "consistency": 92.0,
      "timeliness": 100.0,
      "validity": 96.0,
      "uniqueness": 100.0
    },
    "rules_applied": [
      "date_format_standardization",
      "currency_format_standardization",
      "text_cleanup",
      "category_normalization"
    ],
    "processed_at": "2024-12-24T12:00:00Z"
  }
}
```

#### **GET** `/quality-metrics/{data_source}`

Get data quality metrics for a data source.

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**Response:**

```json
{
  "success": true,
  "data": {
    "data_source": "bank_statement",
    "completeness": 95.0,
    "accuracy": 98.0,
    "consistency": 92.0,
    "timeliness": 100.0,
    "validity": 96.0,
    "uniqueness": 100.0,
    "overall_score": 96.8,
    "measured_at": "2024-12-24T12:00:00Z",
    "recommendations": [
      "Improve data consistency by standardizing date formats",
      "Enhance accuracy by validating currency amounts"
    ]
  }
}
```

## 🏗️ **Project-Trading Intersection API**

### **Base Path**: `/api/v3/projects`

#### **POST** `/`

Create a new project.

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**Request Body:**

```json
{
  "name": "Q1 2024 Financial Audit",
  "description": "Comprehensive financial audit for Q1 2024",
  "total_budget": 50000.0,
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-03-31T23:59:59Z"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": "project_uuid",
    "user_id": "user_uuid",
    "name": "Q1 2024 Financial Audit",
    "description": "Comprehensive financial audit for Q1 2024",
    "total_budget": 50000.0,
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-03-31T23:59:59Z",
    "status": "active",
    "created_at": "2024-12-24T12:00:00Z"
  }
}
```

#### **POST** `/{project_id}/milestones`

Create a new project milestone.

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**Request Body:**

```json
{
  "name": "Phase 1: Data Collection",
  "description": "Collect and organize all financial documents",
  "planned_amount": 15000.0,
  "release_date": "2024-01-15T00:00:00Z"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": "milestone_uuid",
    "project_id": "project_uuid",
    "name": "Phase 1: Data Collection",
    "description": "Collect and organize all financial documents",
    "planned_amount": 15000.0,
    "actual_amount": null,
    "release_date": "2024-01-15T00:00:00Z",
    "status": "pending",
    "created_at": "2024-12-24T12:00:00Z"
  }
}
```

#### **POST** `/trading-operations`

Create a new trading operation.

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**Request Body:**

```json
{
  "operation_type": "income",
  "amount": 2500.0,
  "description": "Investment returns from portfolio",
  "category": "investment_income",
  "date": "2024-12-24T00:00:00Z",
  "milestone_id": "milestone_uuid"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": "operation_uuid",
    "user_id": "user_uuid",
    "milestone_id": "milestone_uuid",
    "type": "income",
    "amount": 2500.0,
    "description": "Investment returns from portfolio",
    "category": "investment_income",
    "date": "2024-12-24T00:00:00Z",
    "linked_milestone": "milestone_uuid",
    "created_at": "2024-12-24T12:00:00Z"
  }
}
```

#### **GET** `/dashboard/unified-finance`

Get unified finance dashboard data.

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**Response:**

```json
{
  "success": true,
  "data": {
    "summary": {
      "total_project_budget": 50000.0,
      "total_milestone_releases": 30000.0,
      "total_trading_income": 15000.0,
      "total_trading_expenses": 5000.0,
      "net_trading": 10000.0,
      "utilization_rate": 80.0
    },
    "projects": [
      {
        "id": "project_uuid",
        "name": "Q1 2024 Financial Audit",
        "status": "active"
      }
    ],
    "milestones": [
      {
        "id": "milestone_uuid",
        "name": "Phase 1: Data Collection",
        "status": "completed"
      }
    ],
    "recent_activities": [
      {
        "type": "milestone",
        "title": "Phase 1: Data Collection",
        "amount": 15000.0,
        "date": "2024-12-24T00:00:00Z",
        "status": "completed"
      }
    ],
    "risk_alerts": [
      {
        "type": "budget_overrun",
        "severity": "medium",
        "message": "Project 'Q1 2024 Financial Audit' has exceeded 80% of budget",
        "action": "Review project expenses and adjust budget"
      }
    ],
    "recommendations": [
      {
        "type": "pov_configuration",
        "priority": "high",
        "message": "Configure your POV role to get specialized tools",
        "action": "Go to profile settings and select your professional role"
      }
    ]
  }
}
```

#### **GET** `/{project_id}/intersection/{milestone_id}`

Analyze project-trading intersection.

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**Response:**

```json
{
  "success": true,
  "data": {
    "project_id": "project_uuid",
    "milestone_id": "milestone_uuid",
    "milestone": {
      "id": "milestone_uuid",
      "name": "Phase 1: Data Collection",
      "planned_amount": 15000.0,
      "actual_amount": 12000.0,
      "status": "completed"
    },
    "trading_operations": [
      {
        "id": "operation_uuid",
        "type": "income",
        "amount": 2500.0,
        "description": "Investment returns",
        "date": "2024-12-24T00:00:00Z"
      }
    ],
    "allocation": {
      "project_percentage": 80.0,
      "trading_percentage": 16.7,
      "remaining_percentage": 3.3,
      "project_amount": 12000.0,
      "trading_amount": 2500.0,
      "remaining_amount": 500.0
    },
    "intersection_analysis": {
      "milestone_status": "completed",
      "funding_efficiency": 80.0,
      "trading_performance": 2500.0,
      "timeline_alignment": 100.0,
      "risk_indicators": [],
      "recommendations": [
        "Consider increasing project funding allocation",
        "Review trading strategy for better returns"
      ]
    },
    "variance": -5.0,
    "risk_level": "low"
  }
}
```

## 📝 **Error Handling**

### **Error Response Format**

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    },
    "timestamp": "2024-12-24T12:00:00Z",
    "request_id": "req_uuid"
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
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error

### **Error Codes**

- `VALIDATION_ERROR` - Input validation failed
- `AUTHENTICATION_ERROR` - Authentication failed
- `AUTHORIZATION_ERROR` - Insufficient permissions
- `NOT_FOUND` - Resource not found
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INTERNAL_ERROR` - Internal server error

## 🔒 **Rate Limiting**

### **Rate Limits**

- **Authentication endpoints**: 10 requests per minute
- **General API endpoints**: 100 requests per minute
- **Frenly AI endpoints**: 50 requests per minute
- **Data processing endpoints**: 20 requests per minute

### **Rate Limit Headers**

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640998800
```

## 📊 **Pagination**

### **Pagination Parameters**

- `limit` - Number of items per page (default: 50, max: 100)
- `offset` - Number of items to skip (default: 0)

### **Pagination Response**

```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "total": 150,
    "limit": 50,
    "offset": 0,
    "has_next": true,
    "has_prev": false,
    "next_url": "/api/v3/endpoint?limit=50&offset=50",
    "prev_url": null
  }
}
```

## 🔍 **Filtering and Sorting**

### **Query Parameters**

- `sort` - Sort field (e.g., `created_at`, `-created_at` for descending)
- `filter` - Filter by field (e.g., `status=completed`)
- `search` - Search in text fields

### **Example**

```
GET /api/v3/frenly-ai/tasks?sort=-created_at&filter=status=completed&limit=20
```

## 📈 **Webhooks**

### **Webhook Events**

- `user.registered` - User registration
- `user.pov_configured` - POV configuration updated
- `frenly_ai.task_completed` - Frenly AI task completed
- `data.standardized` - Data standardization completed
- `project.milestone_created` - Project milestone created

### **Webhook Payload**

```json
{
  "event": "frenly_ai.task_completed",
  "timestamp": "2024-12-24T12:00:00Z",
  "data": {
    "task_id": "task_uuid",
    "user_id": "user_uuid",
    "status": "completed",
    "result": {...}
  }
}
```

## 🧪 **Testing**

### **Test Environment**

```
Base URL: https://api-test.nexus-platform.com
API Key: test_api_key_here
```

### **Test Data**

- Test users with different POV roles
- Sample financial data for testing
- Mock OAuth providers for testing

## 📚 **SDK Examples**

### **JavaScript/TypeScript**

```typescript
import { NexusAPI } from "@nexus-platform/api-client";

const api = new NexusAPI({
  baseURL: "https://api.nexus-platform.com",
  apiKey: "your_api_key",
});

// Login
const auth = await api.auth.login({
  email: "user@example.com",
  password: "password",
});

// Create Frenly AI task
const task = await api.frenlyAI.createTask({
  type: "system_maintenance",
  title: "Database Optimization",
  description: "Optimize database performance",
});

// Get unified finance dashboard
const dashboard = await api.projects.getUnifiedFinanceDashboard();
```

### **Python**

```python
from nexus_platform import NexusAPI

api = NexusAPI(
    base_url='https://api.nexus-platform.com',
    api_key='your_api_key'
)

# Login
auth = api.auth.login(
    email='user@example.com',
    password='password'
)

# Create Frenly AI task
task = api.frenly_ai.create_task(
    type='system_maintenance',
    title='Database Optimization',
    description='Optimize database performance'
)

# Get unified finance dashboard
dashboard = api.projects.get_unified_finance_dashboard()
```

## 🔧 **Configuration**

### **Environment Variables**

```bash
# API Configuration
NEXUS_API_URL=https://api.nexus-platform.com
NEXUS_API_VERSION=v3.0
NEXUS_API_TIMEOUT=30

# Authentication
JWT_SECRET_KEY=your_jwt_secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# OAuth Providers
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret

# Database
DATABASE_URL=postgresql://user:pass@localhost/nexus
REDIS_URL=redis://localhost:6379

# Frenly AI
FRENLY_AI_LEARNING_RATE=0.1
FRENLY_AI_MEMORY_RETENTION_DAYS=30
FRENLY_AI_MAX_CONCURRENT_TASKS=5
```

---

**API Documentation Version**: 3.0.0
**Last Updated**: December 2024
**Status**: Production Ready
