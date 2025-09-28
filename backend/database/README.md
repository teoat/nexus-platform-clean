# NEXUS Database Documentation

## Overview

This directory contains all database-related files for the NEXUS platform, including schemas, migrations, models, and utilities.

## Directory Structure

```
backend/database/
├── migrations/           # Alembic migration files
│   ├── versions/        # Migration scripts
│   ├── env.py          # Migration environment
│   └── script.py.mako  # Migration template
├── models/             # SQLAlchemy models
│   ├── __init__.py
│   └── ssot_models.py  # SSOT-specific models
├── __init__.py
├── alembic.ini        # Alembic configuration
├── base.py           # Base SQLAlchemy configuration
├── connection.py     # Database connection utilities
├── database.py       # Database session management
├── database_schema.sql # Main database schema
├── enhanced_models.py # Enhanced models for advanced features
├── init_nexus.sql    # Initial database setup
├── models.py         # Main SQLAlchemy models
├── optimization_indexes.sql # Performance optimization indexes
├── postgresql_migration.py # PostgreSQL-specific migrations
├── query_optimizer.py # Query optimization utilities
├── schema.sql        # Legacy schema file
├── schema_audit_report.md # Schema audit report
└── schema_normalization.py # Schema normalization utilities
```

## Database Schema

### Core Tables

#### Users and Authentication

- **users**: Main user table with authentication information
- **roles**: User roles and permissions
- **user_roles**: Many-to-many relationship between users and roles

#### API Management

- **api_endpoints**: API endpoint definitions
- **alias_definitions**: SSOT alias definitions
- **ssot_anchors**: SSOT anchor points

#### Financial Services

- **financial_accounts**: User financial accounts
- **transactions**: Financial transactions
- **budgets**: Budget management
- **budget_alerts**: Budget monitoring alerts

#### Analytics and Monitoring

- **analytics**: Event tracking and analytics data
- **performance_metrics**: System performance metrics
- **data_quality_metrics**: Data quality tracking

#### Security and Compliance

- **security_events**: Security event logging
- **compliance_violations**: Compliance violation tracking
- **audit_log**: Comprehensive audit logging

### Key Relationships

```
users (1) ─── (N) user_roles (N) ─── (1) roles
users (1) ─── (N) financial_accounts (N) ─── (1) transactions
users (1) ─── (N) budgets (N) ─── (1) budget_alerts
users (1) ─── (N) security_events
users (1) ─── (N) compliance_violations
```

### Indexes and Performance

#### Primary Indexes

- All tables have UUID primary keys with indexes
- Unique constraints on email, username, and other unique fields

#### Performance Indexes

- `ix_users_email`, `ix_users_username` on users table
- `ix_api_endpoints_name` on API endpoints
- `ix_analytics_event_type`, `ix_analytics_timestamp` on analytics
- `ix_performance_metrics_service_name` on performance metrics

### Data Types and Constraints

#### Common Data Types

- **UUID**: Used for all primary keys
- **VARCHAR(n)**: For text fields with length limits
- **TEXT**: For long-form text content
- **JSONB**: For flexible metadata storage
- **TIMESTAMP WITH TIME ZONE**: For all datetime fields
- **NUMERIC(15,2)**: For financial amounts
- **BOOLEAN**: For status flags

#### Constraints

- Foreign key constraints on all relationships
- Check constraints for status fields
- Unique constraints on identifying fields
- NOT NULL constraints on required fields

## Migration Strategy

### Alembic Migrations

The project uses Alembic for database migrations. Key migration files:

1. **3f58f4ec6ef4_create_ssot_tables.py**: Creates SSOT-specific tables
2. **4a1b2c3d4e5f_create_main_schema.py**: Creates main application schema
3. **5b2c3d4e5f6g_create_enhanced_models.py**: Creates enhanced models

### Migration Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1

# Check migration status
alembic current
alembic history
```

## Models

### SQLAlchemy Models

Models are defined in `models.py` and `enhanced_models.py`:

- **Base Model**: Inherits from `database.base.Base`
- **User Model**: Complete user management
- **Financial Models**: Account and transaction management
- **SSOT Models**: Alias and anchor management

### Model Relationships

All models use SQLAlchemy relationships for proper ORM functionality.

## Database Connection

### Configuration

Database connection is configured in `database.py`:

```python
DATABASE_URL = "postgresql://user:password@localhost/nexus"
```

### Connection Management

- Connection pooling is configured for performance
- Session management handles transactions
- Error handling for connection issues

## Performance Optimization

### Query Optimization

- Use of indexes on frequently queried columns
- Query optimization utilities in `query_optimizer.py`
- Database-specific optimizations in `postgresql_migration.py`

### Monitoring

- Performance metrics collection
- Slow query logging
- Database health monitoring

## Security Considerations

### Data Protection

- UUIDs used instead of sequential IDs
- Row-level security policies recommended
- Audit logging for all changes

### Access Control

- Role-based access control (RBAC)
- API key authentication
- SSL/TLS encryption for connections

## Backup and Recovery

### Backup Strategy

- Regular automated backups
- Point-in-time recovery support
- Backup validation procedures

### Recovery Procedures

- Database restoration from backups
- Migration rollback capabilities
- Disaster recovery planning

## Development Guidelines

### Schema Changes

1. Create migration script using Alembic
2. Test migration in development environment
3. Update model definitions
4. Update documentation

### Best Practices

- Always use transactions for data changes
- Implement proper error handling
- Use database constraints instead of application logic
- Document all schema changes

## Troubleshooting

### Common Issues

- Connection timeout: Check database server status
- Migration conflicts: Use Alembic properly
- Performance issues: Review indexes and queries

### Monitoring Tools

- Database performance dashboards
- Slow query analysis
- Connection pool monitoring

## Future Enhancements

### Planned Improvements

- Database sharding for scalability
- Advanced analytics tables
- Machine learning model storage
- Enhanced security features

### Scalability Considerations

- Table partitioning for large datasets
- Read replicas for analytics
- Caching strategies for frequently accessed data

---

_Last updated: 2025-09-26_
_Version: 1.0_
