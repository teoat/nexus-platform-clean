**Status**: 🔒 **LOCKED** - SSOT Document
**Version**: 1.0
**Last Updated**: 2025-01-17
**Source**: Consolidated from original documentation

---

# API Documentation

## Financial Examiner POV System API

### Base URL

```
https://api.nexus-platform.com/v1
```

### Authentication

All API endpoints require authentication using JWT tokens.

```http
Authorization: Bearer <jwt_token>
```

## Core Endpoints

### POV Management

#### Switch POV Role

```http
POST /pov/switch
Content-Type: application/json

{
  "role": "prosecutor",
  "context": "case_analysis"
}
```

**Response:**

```json
{
  "success": true,
  "current_pov": "prosecutor",
  "available_tools": ["evidence_collection", "case_building"],
  "permissions": ["read_evidence", "create_case"]
}
```

#### Get Available POV Roles

```http
GET /pov/roles
```

**Response:**

```json
{
  "roles": [
    {
      "id": "financial_examiner",
      "name": "Financial Examiner",
      "description": "Primary financial analysis role"
    },
    {
      "id": "prosecutor",
      "name": "Prosecutor",
      "description": "Legal evidence and case building"
    },
    {
      "id": "judge",
      "name": "Judge",
      "description": "Judicial review and decision support"
    },
    {
      "id": "executive",
      "name": "Executive",
      "description": "Strategic oversight and decision making"
    },
    {
      "id": "compliance_officer",
      "name": "Compliance Officer",
      "description": "Regulatory compliance monitoring"
    },
    {
      "id": "auditor",
      "name": "Auditor",
      "description": "Audit trail and verification"
    }
  ]
}
```

### Financial Data Processing

#### Process Financial Data

```http
POST /financial/process
Content-Type: application/json

{
  "expenses": [
    {
      "id": "exp_001",
      "amount": 100.00,
      "date": "2025-01-17T10:00:00Z",
      "description": "Office supplies",
      "category": "office",
      "vendor": "Office Depot"
    }
  ],
  "bank_statements": [
    {
      "id": "bank_001",
      "amount": 100.00,
      "date": "2025-01-17T10:05:00Z",
      "description": "Office supplies payment",
      "account": "checking_001"
    }
  ],
  "pov_role": "financial_examiner"
}
```

**Response:**

```json
{
  "success": true,
  "pov_role": "financial_examiner",
  "reconciliation": {
    "matched_transactions": 1,
    "unmatched_expenses": 0,
    "unmatched_bank": 0,
    "reconciliation_rate": 100.0,
    "details": {
      "matched": [
        {
          "expense_id": "exp_001",
          "bank_id": "bank_001",
          "match_confidence": 0.95,
          "amount_difference": 0.0
        }
      ]
    }
  },
  "fraud_analysis": {
    "fraud_flags": 0,
    "risk_score": 0.0,
    "risk_level": "low",
    "details": []
  },
  "pov_analysis": {
    "focus": "Financial reconciliation and analysis",
    "priority": "Data accuracy and fraud detection",
    "recommendations": ["Complete reconciliation", "Investigate discrepancies"]
  }
}
```

#### Get Reconciliation Results

```http
GET /financial/reconciliation/{session_id}
```

#### Export Financial Report

```http
POST /financial/reports/export
Content-Type: application/json

{
  "report_type": "reconciliation_summary",
  "format": "pdf",
  "date_range": {
    "start": "2025-01-01",
    "end": "2025-01-31"
  },
  "pov_role": "executive"
}
```

### Fraud Detection

#### Analyze Fraud Patterns

```http
POST /fraud/analyze
Content-Type: application/json

{
  "data": {
    "expenses": [...],
    "bank_statements": [...]
  },
  "analysis_type": "comprehensive",
  "pov_role": "prosecutor"
}
```

**Response:**

```json
{
  "success": true,
  "fraud_flags": [
    {
      "id": "flag_001",
      "type": "large_amount",
      "severity": "medium",
      "amount": 5000.0,
      "description": "Unusually large expense",
      "confidence": 0.85,
      "recommendations": [
        "Request additional documentation",
        "Verify vendor legitimacy"
      ]
    }
  ],
  "risk_assessment": {
    "overall_risk": "medium",
    "risk_score": 0.65,
    "factors": ["large_amounts", "suspicious_patterns"]
  },
  "pov_recommendations": {
    "prosecutor": [
      "Gather additional evidence",
      "Document suspicious patterns"
    ],
    "compliance_officer": ["Verify compliance status", "Update audit records"]
  }
}
```

### Litigation Management

#### Create Case

```http
POST /litigation/cases
Content-Type: application/json

{
  "case_title": "Financial Fraud Investigation",
  "case_type": "fraud",
  "priority": "high",
  "description": "Investigation into suspicious financial activities",
  "pov_role": "prosecutor"
}
```

#### Add Evidence

```http
POST /litigation/cases/{case_id}/evidence
Content-Type: application/json

{
  "evidence_type": "financial_document",
  "title": "Bank Statement Analysis",
  "description": "Analysis of suspicious transactions",
  "data": {...},
  "chain_of_custody": {
    "collected_by": "financial_examiner",
    "collected_at": "2025-01-17T10:00:00Z",
    "location": "secure_storage"
  }
}
```

### Theme Management

#### Get Available Themes

```http
GET /themes
```

#### Switch Theme

```http
POST /themes/switch
Content-Type: application/json

{
  "theme": "executive_dashboard",
  "pov_role": "executive"
}
```

#### Get Theme Configuration

```http
GET /themes/{theme_name}/config
```

### System Health

#### Get System Status

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-01-17T13:21:12Z",
  "components": {
    "pov_system": "running",
    "reconciliation_engine": "running",
    "fraud_detection": "running",
    "litigation_management": "running",
    "report_generation": "running",
    "frontend_themes": "running"
  },
  "metrics": {
    "uptime": "99.9%",
    "response_time": "< 100ms",
    "error_rate": "0.1%"
  }
}
```

#### Get System Metrics

```http
GET /metrics
```

## Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "INVALID_POV_ROLE",
    "message": "The specified POV role is not valid",
    "details": {
      "valid_roles": [
        "financial_examiner",
        "prosecutor",
        "judge",
        "executive",
        "compliance_officer",
        "auditor"
      ]
    }
  },
  "timestamp": "2025-01-17T13:21:12Z"
}
```

### Common Error Codes

- `INVALID_POV_ROLE`: Invalid POV role specified
- `AUTHENTICATION_REQUIRED`: Authentication token missing or invalid
- `INSUFFICIENT_PERMISSIONS`: User lacks required permissions
- `INVALID_DATA_FORMAT`: Request data format is invalid
- `PROCESSING_ERROR`: Error during data processing
- `RATE_LIMIT_EXCEEDED`: API rate limit exceeded

## Rate Limiting

- **Standard endpoints**: 1000 requests per hour
- **Financial processing**: 100 requests per hour
- **Fraud analysis**: 50 requests per hour
- **Report generation**: 20 requests per hour

## Webhooks

### Event Types

- `pov.switched`: POV role changed
- `fraud.detected`: Fraud pattern detected
- `case.created`: New litigation case created
- `report.generated`: Financial report generated

### Webhook Payload

```json
{
  "event_type": "fraud.detected",
  "timestamp": "2025-01-17T13:21:12Z",
  "data": {
    "fraud_flag_id": "flag_001",
    "severity": "high",
    "pov_role": "prosecutor"
  }
}
```
