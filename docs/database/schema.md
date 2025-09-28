# NEXUS Platform - Database Schema Documentation

## Overview

This document describes the unified database schema for the NEXUS Platform, providing a single source of truth for all database structures.

## Schema Version

- **Version**: 1.0
- **Generated**: 2025-01-27T12:30:00Z
- **Database**: PostgreSQL 15+

## Table Definitions

### Core Tables

#### users

Primary user authentication and profile table.

| Column        | Type         | Constraints      | Description               |
| ------------- | ------------ | ---------------- | ------------------------- |
| id            | UUID         | PRIMARY KEY      | Unique user identifier    |
| email         | VARCHAR(255) | UNIQUE, NOT NULL | User email address        |
| username      | VARCHAR(100) | UNIQUE, NOT NULL | Unique username           |
| password_hash | VARCHAR(255) | NOT NULL         | Hashed password           |
| first_name    | VARCHAR(100) |                  | User's first name         |
| last_name     | VARCHAR(100) |                  | User's last name          |
| is_active     | BOOLEAN      | DEFAULT true     | Account status            |
| is_verified   | BOOLEAN      | DEFAULT false    | Email verification status |
| created_at    | TIMESTAMP    | DEFAULT NOW()    | Account creation time     |
| updated_at    | TIMESTAMP    | DEFAULT NOW()    | Last update time          |
| last_login    | TIMESTAMP    |                  | Last login time           |

#### roles

User roles and permissions management.

| Column      | Type         | Constraints      | Description            |
| ----------- | ------------ | ---------------- | ---------------------- |
| id          | UUID         | PRIMARY KEY      | Unique role identifier |
| name        | VARCHAR(100) | UNIQUE, NOT NULL | Role name              |
| description | TEXT         |                  | Role description       |
| permissions | JSONB        | DEFAULT '[]'     | Permissions array      |
| created_at  | TIMESTAMP    | DEFAULT NOW()    | Role creation time     |

#### user_roles

Many-to-many relationship between users and roles.

| Column      | Type      | Constraints   | Description                |
| ----------- | --------- | ------------- | -------------------------- |
| user_id     | UUID      | FOREIGN KEY   | Reference to users.id      |
| role_id     | UUID      | FOREIGN KEY   | Reference to roles.id      |
| assigned_at | TIMESTAMP | DEFAULT NOW() | Assignment time            |
| assigned_by | UUID      | FOREIGN KEY   | User who assigned the role |

### API Management Tables

#### api_endpoints

Centralized API endpoint registry.

| Column      | Type         | Constraints      | Description                |
| ----------- | ------------ | ---------------- | -------------------------- |
| id          | UUID         | PRIMARY KEY      | Unique endpoint identifier |
| name        | VARCHAR(255) | UNIQUE, NOT NULL | Endpoint name              |
| path        | VARCHAR(500) | NOT NULL         | API path                   |
| method      | VARCHAR(10)  | NOT NULL         | HTTP method                |
| description | TEXT         |                  | Endpoint description       |
| version     | VARCHAR(20)  | DEFAULT 'v1'     | API version                |
| is_active   | BOOLEAN      | DEFAULT true     | Endpoint status            |
| created_at  | TIMESTAMP    | DEFAULT NOW()    | Creation time              |
| updated_at  | TIMESTAMP    | DEFAULT NOW()    | Last update time           |

#### api_aliases

API endpoint aliasing system for SSOT.

| Column         | Type         | Constraints   | Description             |
| -------------- | ------------ | ------------- | ----------------------- |
| id             | UUID         | PRIMARY KEY   | Unique alias identifier |
| alias_name     | VARCHAR(255) | NOT NULL      | Alias name              |
| canonical_name | VARCHAR(255) | NOT NULL      | Canonical endpoint name |
| context        | VARCHAR(100) | NOT NULL      | Alias context           |
| alias_type     | VARCHAR(50)  | NOT NULL      | Type of alias           |
| description    | TEXT         |               | Alias description       |
| created_by     | UUID         | FOREIGN KEY   | User who created alias  |
| created_at     | TIMESTAMP    | DEFAULT NOW() | Creation time           |
| expires_at     | TIMESTAMP    |               | Expiration time         |
| is_active      | BOOLEAN      | DEFAULT true  | Alias status            |

### SSOT Management Tables

#### ssot_anchors

Single Source of Truth anchor points.

| Column           | Type         | Constraints      | Description              |
| ---------------- | ------------ | ---------------- | ------------------------ |
| id               | UUID         | PRIMARY KEY      | Unique anchor identifier |
| anchor_id        | VARCHAR(255) | UNIQUE, NOT NULL | Anchor identifier        |
| family           | VARCHAR(100) | NOT NULL         | Configuration family     |
| description      | TEXT         |                  | Anchor description       |
| format           | VARCHAR(50)  | NOT NULL         | Configuration format     |
| source_hint      | VARCHAR(500) |                  | Source file hint         |
| owner            | VARCHAR(255) |                  | Configuration owner      |
| version          | VARCHAR(50)  | NOT NULL         | Configuration version    |
| centrality_score | DECIMAL(3,2) | DEFAULT 0.0      | Centrality score         |
| created_at       | TIMESTAMP    | DEFAULT NOW()    | Creation time            |
| updated_at       | TIMESTAMP    | DEFAULT NOW()    | Last update time         |

### Financial Data Tables

#### accounts

User financial accounts.

| Column         | Type          | Constraints      | Description               |
| -------------- | ------------- | ---------------- | ------------------------- |
| id             | UUID          | PRIMARY KEY      | Unique account identifier |
| user_id        | UUID          | FOREIGN KEY      | Reference to users.id     |
| account_name   | VARCHAR(255)  | NOT NULL         | Account display name      |
| account_number | VARCHAR(100)  | UNIQUE, NOT NULL | Account number            |
| account_type   | VARCHAR(50)   | NOT NULL         | Account type              |
| bank_name      | VARCHAR(255)  |                  | Bank name                 |
| balance        | DECIMAL(15,2) | DEFAULT 0.00     | Current balance           |
| currency       | VARCHAR(3)    | DEFAULT 'USD'    | Currency code             |
| is_active      | BOOLEAN       | DEFAULT true     | Account status            |
| created_at     | TIMESTAMP     | DEFAULT NOW()    | Creation time             |
| updated_at     | TIMESTAMP     | DEFAULT NOW()    | Last update time          |

#### transactions

Financial transactions.

| Column           | Type          | Constraints       | Description                   |
| ---------------- | ------------- | ----------------- | ----------------------------- |
| id               | UUID          | PRIMARY KEY       | Unique transaction identifier |
| account_id       | UUID          | FOREIGN KEY       | Reference to accounts.id      |
| amount           | DECIMAL(15,2) | NOT NULL          | Transaction amount            |
| transaction_type | VARCHAR(50)   | NOT NULL          | Transaction type              |
| category         | VARCHAR(100)  |                   | Transaction category          |
| description      | TEXT          |                   | Transaction description       |
| transaction_date | TIMESTAMP     | DEFAULT NOW()     | Transaction date              |
| status           | VARCHAR(50)   | DEFAULT 'pending' | Transaction status            |
| created_at       | TIMESTAMP     | DEFAULT NOW()     | Creation time                 |
| updated_at       | TIMESTAMP     | DEFAULT NOW()     | Last update time              |

### AI and Analytics Tables

#### ai_models

AI model registry.

| Column       | Type         | Constraints        | Description             |
| ------------ | ------------ | ------------------ | ----------------------- |
| id           | UUID         | PRIMARY KEY        | Unique model identifier |
| name         | VARCHAR(255) | NOT NULL           | Model name              |
| provider     | VARCHAR(100) | NOT NULL           | Model provider          |
| version      | VARCHAR(50)  | NOT NULL           | Model version           |
| status       | VARCHAR(50)  | DEFAULT 'inactive' | Model status            |
| capabilities | JSONB        | DEFAULT '[]'       | Model capabilities      |
| performance  | JSONB        | DEFAULT '{}'       | Performance metrics     |
| created_at   | TIMESTAMP    | DEFAULT NOW()      | Creation time           |
| updated_at   | TIMESTAMP    | DEFAULT NOW()      | Last update time        |

#### ai_insights

AI-generated insights.

| Column       | Type         | Constraints   | Description               |
| ------------ | ------------ | ------------- | ------------------------- |
| id           | UUID         | PRIMARY KEY   | Unique insight identifier |
| model_id     | UUID         | FOREIGN KEY   | Reference to ai_models.id |
| insight_type | VARCHAR(100) | NOT NULL      | Type of insight           |
| title        | VARCHAR(255) | NOT NULL      | Insight title             |
| description  | TEXT         |               | Insight description       |
| data         | JSONB        | DEFAULT '{}'  | Insight data              |
| confidence   | DECIMAL(3,2) |               | Confidence score          |
| created_at   | TIMESTAMP    | DEFAULT NOW() | Creation time             |

### Monitoring and System Tables

#### system_metrics

System performance metrics.

| Column       | Type          | Constraints   | Description              |
| ------------ | ------------- | ------------- | ------------------------ |
| id           | UUID          | PRIMARY KEY   | Unique metric identifier |
| metric_name  | VARCHAR(255)  | NOT NULL      | Metric name              |
| metric_value | DECIMAL(15,4) | NOT NULL      | Metric value             |
| metric_unit  | VARCHAR(50)   |               | Metric unit              |
| tags         | JSONB         | DEFAULT '{}'  | Metric tags              |
| timestamp    | TIMESTAMP     | DEFAULT NOW() | Metric timestamp         |

#### alerts

System alerts and notifications.

| Column          | Type         | Constraints      | Description             |
| --------------- | ------------ | ---------------- | ----------------------- |
| id              | UUID         | PRIMARY KEY      | Unique alert identifier |
| alert_name      | VARCHAR(255) | NOT NULL         | Alert name              |
| severity        | VARCHAR(50)  | NOT NULL         | Alert severity          |
| message         | TEXT         | NOT NULL         | Alert message           |
| status          | VARCHAR(50)  | DEFAULT 'active' | Alert status            |
| acknowledged_by | UUID         | FOREIGN KEY      | User who acknowledged   |
| acknowledged_at | TIMESTAMP    |                  | Acknowledgment time     |
| created_at      | TIMESTAMP    | DEFAULT NOW()    | Creation time           |
| resolved_at     | TIMESTAMP    |                  | Resolution time         |

### Audit Logging

#### audit_logs

Comprehensive audit trail.

| Column     | Type         | Constraints   | Description           |
| ---------- | ------------ | ------------- | --------------------- |
| id         | UUID         | PRIMARY KEY   | Unique log identifier |
| table_name | VARCHAR(255) | NOT NULL      | Table name            |
| record_id  | UUID         | NOT NULL      | Record identifier     |
| action     | VARCHAR(50)  | NOT NULL      | Action performed      |
| old_values | JSONB        |               | Previous values       |
| new_values | JSONB        |               | New values            |
| changed_by | UUID         | FOREIGN KEY   | User who made change  |
| changed_at | TIMESTAMP    | DEFAULT NOW() | Change time           |
| ip_address | INET         |               | IP address            |
| user_agent | TEXT         |               | User agent string     |

## Indexes

### Performance Indexes

- `idx_users_email` - Fast email lookups
- `idx_users_username` - Fast username lookups
- `idx_api_endpoints_name` - Fast endpoint name lookups
- `idx_api_aliases_alias` - Fast alias lookups
- `idx_api_aliases_context` - Context-based alias lookups
- `idx_ssot_anchors_family` - Family-based anchor lookups
- `idx_audit_logs_table_record` - Audit log lookups
- `idx_audit_logs_changed_at` - Time-based audit queries
- `idx_accounts_user_id` - User account lookups
- `idx_transactions_account_id` - Account transaction lookups
- `idx_transactions_date` - Date-based transaction queries
- `idx_ai_insights_model_id` - Model insight lookups
- `idx_system_metrics_name` - Metric name lookups
- `idx_system_metrics_timestamp` - Time-based metric queries
- `idx_alerts_status` - Alert status filtering
- `idx_alerts_severity` - Alert severity filtering

## Triggers

### Updated_at Triggers

All tables with `updated_at` columns have triggers that automatically update the timestamp when records are modified:

- `update_users_updated_at`
- `update_api_endpoints_updated_at`
- `update_ssot_anchors_updated_at`
- `update_accounts_updated_at`
- `update_transactions_updated_at`
- `update_ai_models_updated_at`

## Default Data

### Roles

- **admin**: Administrator with full access
- **user**: Standard user with basic access
- **viewer**: Read-only access
- **manager**: Manager with team access

### API Endpoints

- Health check endpoints
- User profile management
- Account management
- Transaction management
- AI chat endpoints
- Analytics endpoints

### SSOT Anchors

- Environment configuration
- Docker configuration
- Kubernetes configuration
- Monitoring configuration
- API configuration

## Migration Procedures

### Creating New Tables

1. Add table definition to schema.sql
2. Create appropriate indexes
3. Add triggers if needed
4. Update documentation
5. Test in development environment

### Modifying Existing Tables

1. Create migration script
2. Test migration on development data
3. Backup production data
4. Apply migration
5. Verify data integrity
6. Update documentation

### Adding New Indexes

1. Analyze query performance
2. Create index definition
3. Test index creation on development
4. Monitor performance impact
5. Apply to production during maintenance window

## Performance Considerations

### Query Optimization

- Use appropriate indexes
- Avoid SELECT \* queries
- Use LIMIT for large result sets
- Optimize JOIN operations
- Use EXPLAIN ANALYZE for query analysis

### Connection Management

- Use connection pooling
- Set appropriate timeouts
- Monitor connection usage
- Implement connection health checks

### Backup Strategy

- Daily full backups
- Transaction log backups
- Point-in-time recovery capability
- Test restore procedures regularly

## Security Considerations

### Access Control

- Role-based permissions
- Principle of least privilege
- Regular access reviews
- Audit trail maintenance

### Data Protection

- Encrypt sensitive data
- Use parameterized queries
- Implement input validation
- Regular security audits

### Compliance

- GDPR compliance for EU data
- SOX compliance for financial data
- HIPAA compliance for health data
- Regular compliance audits
