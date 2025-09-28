# NEXUS Database Schema Documentation

## Overview

This document provides comprehensive documentation for the NEXUS Platform database schema, including all tables, relationships, constraints, and usage patterns.

## Database Architecture

### Core Tables

- **users**: User management and authentication
- **accounts**: Financial account management
- **transactions**: Transaction processing and history
- **audit_logs**: System audit and compliance logging
- **system_settings**: Configuration and system parameters

### SSOT Registry Tables

- **ssot_api_contracts**: API contract definitions
- **ssot_api_aliases**: API alias management
- **ssot_audit_logs**: SSOT-specific audit logging
- **ssot_governance_rules**: SSOT governance and validation rules

### Supporting Tables

- **api_keys**: API key management
- **notifications**: User notification system
- **user_sessions**: Session management

## Table Specifications

### users

**Purpose**: Central user management and authentication

| Column        | Type                     | Constraints               | Description                                       |
| ------------- | ------------------------ | ------------------------- | ------------------------------------------------- |
| id            | UUID                     | PRIMARY KEY               | Unique user identifier                            |
| username      | VARCHAR(50)              | UNIQUE, NOT NULL          | User login name                                   |
| email         | VARCHAR(255)             | UNIQUE, NOT NULL          | User email address                                |
| full_name     | VARCHAR(255)             | NOT NULL                  | User's full name                                  |
| password_hash | VARCHAR(255)             | NOT NULL                  | Hashed password                                   |
| is_active     | BOOLEAN                  | DEFAULT true              | Account status                                    |
| is_verified   | BOOLEAN                  | DEFAULT false             | Email verification status                         |
| role          | VARCHAR(50)              | CHECK constraint          | User role (admin, manager, user, viewer, auditor) |
| last_login    | TIMESTAMP WITH TIME ZONE |                           | Last login timestamp                              |
| created_at    | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Record creation time                              |
| updated_at    | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Record update time                                |
| created_by    | UUID                     | REFERENCES users(id)      | User who created this record                      |
| updated_by    | UUID                     | REFERENCES users(id)      | User who last updated this record                 |

**Indexes**:

- `idx_users_username` on username
- `idx_users_email` on email
- `idx_users_active` on is_active

### accounts

**Purpose**: Financial account management

| Column         | Type                     | Constraints                    | Description                                                |
| -------------- | ------------------------ | ------------------------------ | ---------------------------------------------------------- |
| id             | UUID                     | PRIMARY KEY                    | Unique account identifier                                  |
| user_id        | UUID                     | NOT NULL, REFERENCES users(id) | Owner of the account                                       |
| account_name   | VARCHAR(255)             | NOT NULL                       | Human-readable account name                                |
| account_type   | VARCHAR(50)              | NOT NULL, CHECK constraint     | Account type (checking, savings, investment, credit, loan) |
| account_number | VARCHAR(50)              | UNIQUE, NOT NULL               | Account number                                             |
| balance        | DECIMAL(15,2)            | DEFAULT 0.00                   | Current account balance                                    |
| currency       | VARCHAR(3)               | DEFAULT 'USD'                  | Account currency                                           |
| is_active      | BOOLEAN                  | DEFAULT true                   | Account status                                             |
| created_at     | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP      | Record creation time                                       |
| updated_at     | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP      | Record update time                                         |
| created_by     | UUID                     | REFERENCES users(id)           | User who created this record                               |
| updated_by     | UUID                     | REFERENCES users(id)           | User who last updated this record                          |

**Indexes**:

- `idx_accounts_user_id` on user_id
- `idx_accounts_type` on account_type
- `idx_accounts_active` on is_active

### transactions

**Purpose**: Transaction processing and history

| Column           | Type                     | Constraints                         | Description                                                              |
| ---------------- | ------------------------ | ----------------------------------- | ------------------------------------------------------------------------ |
| id               | UUID                     | PRIMARY KEY                         | Unique transaction identifier                                            |
| account_id       | UUID                     | NOT NULL, REFERENCES accounts(id)   | Associated account                                                       |
| transaction_type | VARCHAR(50)              | NOT NULL, CHECK constraint          | Transaction type (deposit, withdrawal, transfer, payment, fee, interest) |
| amount           | DECIMAL(15,2)            | NOT NULL                            | Transaction amount                                                       |
| description      | TEXT                     |                                     | Transaction description                                                  |
| reference_number | VARCHAR(100)             |                                     | External reference number                                                |
| status           | VARCHAR(20)              | DEFAULT 'pending', CHECK constraint | Transaction status (pending, completed, failed, cancelled)               |
| transaction_date | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP           | When transaction occurred                                                |
| processed_at     | TIMESTAMP WITH TIME ZONE |                                     | When transaction was processed                                           |
| created_at       | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP           | Record creation time                                                     |
| updated_at       | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP           | Record update time                                                       |
| created_by       | UUID                     | REFERENCES users(id)                | User who created this record                                             |
| updated_by       | UUID                     | REFERENCES users(id)                | User who last updated this record                                        |

**Indexes**:

- `idx_transactions_account_id` on account_id
- `idx_transactions_type` on transaction_type
- `idx_transactions_status` on status
- `idx_transactions_date` on transaction_date

### ssot_api_contracts

**Purpose**: SSOT API contract definitions

| Column         | Type                     | Constraints                        | Description                                    |
| -------------- | ------------------------ | ---------------------------------- | ---------------------------------------------- |
| id             | UUID                     | PRIMARY KEY                        | Unique contract identifier                     |
| canonical_name | VARCHAR(255)             | UNIQUE, NOT NULL                   | Canonical API name                             |
| version        | VARCHAR(50)              | NOT NULL                           | API version                                    |
| description    | TEXT                     |                                    | API description                                |
| base_url       | VARCHAR(500)             | NOT NULL                           | Base URL for the API                           |
| status         | VARCHAR(20)              | DEFAULT 'active', CHECK constraint | Contract status (active, deprecated, archived) |
| created_at     | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP          | Record creation time                           |
| updated_at     | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP          | Record update time                             |
| created_by     | VARCHAR(255)             | NOT NULL                           | User who created this record                   |
| updated_by     | VARCHAR(255)             | NOT NULL                           | User who last updated this record              |

**Indexes**:

- `idx_ssot_api_contracts_canonical_name` on canonical_name
- `idx_ssot_api_contracts_status` on status

### ssot_api_aliases

**Purpose**: API alias management for SSOT

| Column      | Type                     | Constraints                                 | Description                           |
| ----------- | ------------------------ | ------------------------------------------- | ------------------------------------- |
| id          | UUID                     | PRIMARY KEY                                 | Unique alias identifier               |
| contract_id | UUID                     | NOT NULL, REFERENCES ssot_api_contracts(id) | Associated API contract               |
| alias_name  | VARCHAR(255)             | NOT NULL                                    | Alias name                            |
| context     | VARCHAR(100)             | NOT NULL                                    | Context where alias is used           |
| alias_type  | VARCHAR(20)              | DEFAULT 'permanent', CHECK constraint       | Alias type (permanent, temporary)     |
| expires_at  | TIMESTAMP WITH TIME ZONE |                                             | Expiration time for temporary aliases |
| description | TEXT                     |                                             | Alias description                     |
| is_active   | BOOLEAN                  | DEFAULT true                                | Alias status                          |
| created_at  | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP                   | Record creation time                  |
| updated_at  | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP                   | Record update time                    |
| created_by  | VARCHAR(255)             | NOT NULL                                    | User who created this record          |
| updated_by  | VARCHAR(255)             | NOT NULL                                    | User who last updated this record     |

**Indexes**:

- `idx_ssot_api_aliases_contract_id` on contract_id
- `idx_ssot_api_aliases_alias_name` on alias_name
- `idx_ssot_api_aliases_context` on context
- `idx_ssot_api_aliases_active` on is_active

**Unique Constraints**:

- `UNIQUE(alias_name, context)` - Ensures alias uniqueness within context

## Relationships

### Primary Relationships

1. **users** → **accounts** (1:many)
   - One user can have multiple accounts
   - Foreign key: accounts.user_id → users.id

2. **accounts** → **transactions** (1:many)
   - One account can have multiple transactions
   - Foreign key: transactions.account_id → accounts.id

3. **ssot_api_contracts** → **ssot_api_aliases** (1:many)
   - One API contract can have multiple aliases
   - Foreign key: ssot_api_aliases.contract_id → ssot_api_contracts.id

### Audit Relationships

- All main tables have audit relationships through **audit_logs**
- **created_by** and **updated_by** fields reference **users.id**

## Constraints and Validation

### Check Constraints

- **users.role**: Must be one of (admin, manager, user, viewer, auditor)
- **accounts.account_type**: Must be one of (checking, savings, investment, credit, loan)
- **transactions.transaction_type**: Must be one of (deposit, withdrawal, transfer, payment, fee, interest)
- **transactions.status**: Must be one of (pending, completed, failed, cancelled)
- **ssot_api_contracts.status**: Must be one of (active, deprecated, archived)
- **ssot_api_aliases.alias_type**: Must be one of (permanent, temporary)

### Unique Constraints

- **users.username**: Must be unique
- **users.email**: Must be unique
- **accounts.account_number**: Must be unique
- **ssot_api_contracts.canonical_name**: Must be unique
- **ssot_api_aliases(alias_name, context)**: Must be unique within context

## Triggers and Functions

### Updated At Triggers

All tables have triggers that automatically update the `updated_at` field when records are modified.

### Audit Triggers

All main tables have audit triggers that log changes to the **audit_logs** table.

### Functions

- **update_updated_at_column()**: Updates the updated_at timestamp
- **log_ssot_changes()**: Logs changes for audit purposes

## Performance Considerations

### Indexing Strategy

- Primary keys are automatically indexed
- Foreign keys are indexed for join performance
- Frequently queried columns are indexed
- Composite indexes for multi-column queries

### Query Optimization

- Use appropriate indexes for WHERE clauses
- Consider partitioning for large tables (transactions, audit_logs)
- Regular VACUUM and ANALYZE operations
- Monitor query performance with EXPLAIN ANALYZE

## Security Considerations

### Data Protection

- Sensitive data (passwords) is hashed
- API keys are hashed before storage
- Audit logs capture all changes
- Row-level security can be implemented

### Access Control

- Database users should have minimal required permissions
- Use connection pooling for application connections
- Implement proper backup and recovery procedures

## Migration Strategy

### Version Control

- All schema changes are versioned
- Migration scripts are numbered sequentially
- Rollback scripts are provided for each migration

### Data Migration

- Existing data is preserved during migrations
- Data validation is performed after each migration
- Backup is created before major schema changes

## Monitoring and Maintenance

### Health Checks

- Regular monitoring of table sizes
- Index usage analysis
- Query performance monitoring
- Connection pool monitoring

### Maintenance Tasks

- Regular VACUUM operations
- Index rebuilding when necessary
- Statistics updates
- Log file rotation

## Backup and Recovery

### Backup Strategy

- Daily full backups
- Transaction log backups every 15 minutes
- Point-in-time recovery capability
- Offsite backup storage

### Recovery Procedures

- Documented recovery procedures
- Regular recovery testing
- Disaster recovery planning
- Business continuity planning

---

**Last Updated**: 2025-01-27
**Version**: 3.0.0
**Maintainer**: NEXUS Platform Team
