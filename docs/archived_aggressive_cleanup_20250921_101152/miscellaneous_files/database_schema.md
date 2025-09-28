# Database Schema

## Financial Examiner POV System Database Design

### Overview

The database schema is designed to support the Financial Examiner POV system with role-based access, financial data processing, fraud detection, and litigation management.

### Technology Stack

- **Primary Database**: PostgreSQL 14+
- **Cache Layer**: Redis 6+
- **Search Engine**: Elasticsearch 8+
- **Document Store**: MongoDB 5+

## Core Tables

### Users and Authentication

#### users

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);
```

#### user_sessions

```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    current_pov VARCHAR(50) NOT NULL,
    current_theme VARCHAR(50) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at);
```

### Financial Data

#### expenses

```sql
CREATE TABLE expenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    date DATE NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100),
    vendor VARCHAR(255),
    receipt_url TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_expenses_user_id ON expenses(user_id);
CREATE INDEX idx_expenses_date ON expenses(date);
CREATE INDEX idx_expenses_amount ON expenses(amount);
CREATE INDEX idx_expenses_category ON expenses(category);
CREATE INDEX idx_expenses_status ON expenses(status);
```

#### bank_statements

```sql
CREATE TABLE bank_statements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_id VARCHAR(100) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    date DATE NOT NULL,
    description TEXT NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    balance DECIMAL(15,2),
    reference_number VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_bank_statements_user_id ON bank_statements(user_id);
CREATE INDEX idx_bank_statements_date ON bank_statements(date);
CREATE INDEX idx_bank_statements_amount ON bank_statements(amount);
CREATE INDEX idx_bank_statements_account ON bank_statements(account_id);
```

#### reconciliation_matches

```sql
CREATE TABLE reconciliation_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expense_id UUID NOT NULL REFERENCES expenses(id) ON DELETE CASCADE,
    bank_statement_id UUID NOT NULL REFERENCES bank_statements(id) ON DELETE CASCADE,
    match_confidence DECIMAL(3,2) NOT NULL,
    amount_difference DECIMAL(15,2) DEFAULT 0,
    match_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_reconciliation_user_id ON reconciliation_matches(user_id);
CREATE INDEX idx_reconciliation_expense ON reconciliation_matches(expense_id);
CREATE INDEX idx_reconciliation_bank ON reconciliation_matches(bank_statement_id);
```

### Fraud Detection

#### fraud_flags

```sql
CREATE TABLE fraud_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    flag_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    confidence DECIMAL(3,2) NOT NULL,
    amount DECIMAL(15,2),
    description TEXT NOT NULL,
    related_expense_id UUID REFERENCES expenses(id) ON DELETE SET NULL,
    related_bank_id UUID REFERENCES bank_statements(id) ON DELETE SET NULL,
    status VARCHAR(20) DEFAULT 'open',
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_fraud_flags_user_id ON fraud_flags(user_id);
CREATE INDEX idx_fraud_flags_type ON fraud_flags(flag_type);
CREATE INDEX idx_fraud_flags_severity ON fraud_flags(severity);
CREATE INDEX idx_fraud_flags_status ON fraud_flags(status);
CREATE INDEX idx_fraud_flags_assigned ON fraud_flags(assigned_to);
```

#### fraud_patterns

```sql
CREATE TABLE fraud_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_name VARCHAR(100) NOT NULL,
    pattern_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    rules JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_fraud_patterns_type ON fraud_patterns(pattern_type);
CREATE INDEX idx_fraud_patterns_active ON fraud_patterns(is_active);
```

### Litigation Management

#### litigation_cases

```sql
CREATE TABLE litigation_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_number VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    case_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'open',
    description TEXT,
    assigned_prosecutor UUID REFERENCES users(id) ON DELETE SET NULL,
    assigned_judge UUID REFERENCES users(id) ON DELETE SET NULL,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_cases_number ON litigation_cases(case_number);
CREATE INDEX idx_cases_type ON litigation_cases(case_type);
CREATE INDEX idx_cases_status ON litigation_cases(status);
CREATE INDEX idx_cases_prosecutor ON litigation_cases(assigned_prosecutor);
CREATE INDEX idx_cases_judge ON litigation_cases(assigned_judge);
```

#### case_evidence

```sql
CREATE TABLE case_evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES litigation_cases(id) ON DELETE CASCADE,
    evidence_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    evidence_data JSONB NOT NULL,
    chain_of_custody JSONB NOT NULL,
    file_url TEXT,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_evidence_case_id ON case_evidence(case_id);
CREATE INDEX idx_evidence_type ON case_evidence(evidence_type);
CREATE INDEX idx_evidence_created_by ON case_evidence(created_by);
```

### Reports and Analytics

#### financial_reports

```sql
CREATE TABLE financial_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    pov_role VARCHAR(50) NOT NULL,
    report_data JSONB NOT NULL,
    file_url TEXT,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_reports_user_id ON financial_reports(user_id);
CREATE INDEX idx_reports_type ON financial_reports(report_type);
CREATE INDEX idx_reports_pov ON financial_reports(pov_role);
CREATE INDEX idx_reports_generated ON financial_reports(generated_at);
```

### System Configuration

#### system_config

```sql
CREATE TABLE system_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_config_key ON system_config(config_key);
CREATE INDEX idx_config_active ON system_config(is_active);
```

#### audit_logs

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at);
```

## Redis Cache Schema

### Session Management

```
Key: session:{session_token}
Value: {
  "user_id": "uuid",
  "pov_role": "prosecutor",
  "theme": "executive_dashboard",
  "permissions": ["read_evidence", "create_case"],
  "expires_at": "2025-01-17T14:21:12Z"
}
TTL: 3600 seconds
```

### POV Context

```
Key: pov_context:{user_id}
Value: {
  "current_pov": "prosecutor",
  "available_tools": ["evidence_collection", "case_building"],
  "last_switch": "2025-01-17T13:21:12Z"
}
TTL: 1800 seconds
```

### Financial Data Cache

```
Key: financial_data:{user_id}:{date_range}
Value: {
  "expenses": [...],
  "bank_statements": [...],
  "reconciliation": {...}
}
TTL: 300 seconds
```

## Elasticsearch Indices

### Financial Documents

```json
{
  "mappings": {
    "properties": {
      "user_id": { "type": "keyword" },
      "document_type": { "type": "keyword" },
      "amount": { "type": "double" },
      "date": { "type": "date" },
      "description": { "type": "text", "analyzer": "standard" },
      "category": { "type": "keyword" },
      "vendor": { "type": "text" },
      "pov_role": { "type": "keyword" },
      "created_at": { "type": "date" }
    }
  }
}
```

### Fraud Patterns

```json
{
  "mappings": {
    "properties": {
      "pattern_name": { "type": "text" },
      "pattern_type": { "type": "keyword" },
      "description": { "type": "text" },
      "rules": { "type": "object" },
      "severity": { "type": "keyword" },
      "is_active": { "type": "boolean" }
    }
  }
}
```

## MongoDB Collections

### Case Documents

```javascript
{
  _id: ObjectId,
  case_id: String,
  document_type: String,
  title: String,
  content: String,
  metadata: {
    created_by: String,
    created_at: Date,
    version: Number,
    tags: [String]
  },
  file_data: BinData
}
```

### System Logs

```javascript
{
  _id: ObjectId,
  timestamp: Date,
  level: String,
  component: String,
  message: String,
  user_id: String,
  session_id: String,
  metadata: Object
}
```

## Data Relationships

### Entity Relationship Diagram

```
Users (1) -----> (N) Expenses
Users (1) -----> (N) Bank Statements
Users (1) -----> (N) Litigation Cases
Users (1) -----> (N) Financial Reports

Expenses (1) -----> (N) Reconciliation Matches
Bank Statements (1) -----> (N) Reconciliation Matches

Litigation Cases (1) -----> (N) Case Evidence
Users (1) -----> (N) Case Evidence

Expenses (1) -----> (N) Fraud Flags
Bank Statements (1) -----> (N) Fraud Flags
```

## Security Considerations

### Row-Level Security (RLS)

```sql
-- Enable RLS on all user-specific tables
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE bank_statements ENABLE ROW LEVEL SECURITY;
ALTER TABLE litigation_cases ENABLE ROW LEVEL SECURITY;

-- Create policies for user data access
CREATE POLICY user_expenses_policy ON expenses
    FOR ALL TO authenticated_users
    USING (user_id = current_user_id());
```

### Data Encryption

- **At Rest**: AES-256 encryption for sensitive fields
- **In Transit**: TLS 1.3 for all connections
- **Key Management**: AWS KMS or similar service

### Backup Strategy

- **Full Backup**: Daily at 2 AM UTC
- **Incremental Backup**: Every 6 hours
- **Point-in-Time Recovery**: 30-day retention
- **Cross-Region Replication**: For disaster recovery
