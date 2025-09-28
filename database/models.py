#!/usr/bin/env python3
"""
NEXUS Platform - Enhanced Database Models
Comprehensive database schema with proper constraints, indexes, and validation
"""

    Column, Integer, String, Text, DateTime, Boolean, Numeric,
    ForeignKey, Index, CheckConstraint, UniqueConstraint,
    Enum as SQLEnum, JSON, LargeBinary, ARRAY
)
import re
import uuid

Base = declarative_base()

# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    COMPLIANCE_OFFICER = "compliance_officer"
    FINANCIAL_ANALYST = "financial_analyst"
    AUDITOR = "auditor"
    VIEWER = "viewer"

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    REFUND = "refund"
    FEE = "fee"
    INTEREST = "interest"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REVERSED = "reversed"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    REQUIRES_ACTION = "requires_action"

class AuditAction(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    IMPORT = "import"

# Base model with common fields
class BaseModel(Base):
    """Base model with common fields and methods"""
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    version = Column(Integer, default=1, nullable=False)

    @validates('email')
    def validate_email(self, key, email):
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError("Invalid email format")
        return email

    @validates('phone')
    def validate_phone(self, key, phone):
        if phone and not re.match(r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$', phone):
            raise ValueError("Invalid phone format")
        return phone

# User Management
class User(BaseModel):
    """Enhanced user model with comprehensive fields"""
    __tablename__ = 'users'

    # Basic Information
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)

    # Authentication
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(255), nullable=False)
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String(255), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)

    # Authorization
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.VIEWER)
    permissions = Column(JSONB, nullable=True)
    department = Column(String(100), nullable=True)
    manager_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)

    # Profile
    avatar_url = Column(String(500), nullable=True)
    timezone = Column(String(50), default='UTC', nullable=False)
    language = Column(String(10), default='en', nullable=False)

    # Security
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    password_expires_at = Column(DateTime(timezone=True), nullable=True)
    two_factor_backup_codes = Column(ARRAY(String), nullable=True)

    # Relationships
    manager = relationship("User", remote_side=[id], backref="subordinates")
    audit_logs = relationship("AuditLog", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")

    # Constraints
    __table_args__ = (
        CheckConstraint('login_attempts >= 0', name='ck_users_login_attempts_positive'),
        CheckConstraint('length(username) >= 3', name='ck_users_username_length'),
        CheckConstraint('length(first_name) >= 1', name='ck_users_first_name_length'),
        CheckConstraint('length(last_name) >= 1', name='ck_users_last_name_length'),
        Index('idx_users_email_active', 'email', 'is_active'),
        Index('idx_users_role_active', 'role', 'is_active'),
        Index('idx_users_last_login', 'last_login'),
    )

    @validates('username')
    def validate_username(self, key, username):
        if not re.match(r'^[a-zA-Z0-9_-]{3,50}$', username):
            raise ValueError("Username must be 3-50 characters and contain only letters, numbers, underscores, and hyphens")
        return username.lower()

    @validates('role')
    def validate_role(self, key, role):
        if not isinstance(role, UserRole):
            raise ValueError("Invalid role")
        return role

class UserSession(BaseModel):
    """User session management"""
    __tablename__ = 'user_sessions'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_activity = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")

    # Constraints
    __table_args__ = (
        CheckConstraint('expires_at > created_at', name='ck_sessions_expires_after_created'),
        Index('idx_sessions_user_active', 'user_id', 'is_active'),
        Index('idx_sessions_expires', 'expires_at'),
    )

# Financial Models
class Account(BaseModel):
    """Financial account model"""
    __tablename__ = 'accounts'

    # Account Information
    account_number = Column(String(50), unique=True, nullable=False, index=True)
    account_name = Column(String(200), nullable=False)
    account_type = Column(String(50), nullable=False)
    currency = Column(String(3), nullable=False, default='USD')
    balance = Column(Numeric(15, 2), default=0, nullable=False)

    # Bank Information
    bank_name = Column(String(200), nullable=True)
    bank_code = Column(String(20), nullable=True)
    routing_number = Column(String(20), nullable=True)
    swift_code = Column(String(20), nullable=True)

    # Account Status
    status = Column(String(20), default='active', nullable=False)
    opened_date = Column(DateTime(timezone=True), nullable=True)
    closed_date = Column(DateTime(timezone=True), nullable=True)

    # Risk and Compliance
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.LOW, nullable=False)
    compliance_status = Column(SQLEnum(ComplianceStatus), default=ComplianceStatus.COMPLIANT, nullable=False)

    # Relationships
    transactions = relationship("Transaction", back_populates="account")
    risk_assessments = relationship("RiskAssessment", back_populates="account")

    # Constraints
    __table_args__ = (
        CheckConstraint('balance >= 0', name='ck_accounts_balance_positive'),
        CheckConstraint('length(account_number) >= 8', name='ck_accounts_account_number_length'),
        CheckConstraint('length(currency) = 3', name='ck_accounts_currency_length'),
        Index('idx_accounts_number_active', 'account_number', 'is_active'),
        Index('idx_accounts_type_status', 'account_type', 'status'),
        Index('idx_accounts_risk_level', 'risk_level'),
        Index('idx_accounts_compliance_status', 'compliance_status'),
    )

    @validates('account_number')
    def validate_account_number(self, key, account_number):
        if not re.match(r'^[0-9]{8,50}$', account_number):
            raise ValueError("Account number must be 8-50 digits")
        return account_number

    @validates('currency')
    def validate_currency(self, key, currency):
        if not re.match(r'^[A-Z]{3}$', currency):
            raise ValueError("Currency must be 3 uppercase letters")
        return currency.upper()

class Transaction(BaseModel):
    """Enhanced transaction model"""
    __tablename__ = 'transactions'

    # Transaction Information
    account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=False)
    transaction_id = Column(String(100), unique=True, nullable=False, index=True)
    external_id = Column(String(100), nullable=True, index=True)

    # Transaction Details
    type = Column(SQLEnum(TransactionType), nullable=False)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False, default='USD')

    # Transaction Parties
    counterparty_name = Column(String(200), nullable=True)
    counterparty_account = Column(String(50), nullable=True)
    counterparty_bank = Column(String(200), nullable=True)

    # Transaction Metadata
    description = Column(Text, nullable=True)
    reference = Column(String(100), nullable=True)
    category = Column(String(50), nullable=True)
    subcategory = Column(String(50), nullable=True)
    tags = Column(ARRAY(String), nullable=True)

    # Dates
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    posted_date = Column(DateTime(timezone=True), nullable=True)
    effective_date = Column(DateTime(timezone=True), nullable=True)

    # Risk and Compliance
    risk_score = Column(Numeric(3, 2), nullable=True)
    risk_factors = Column(JSONB, nullable=True)
    compliance_flags = Column(ARRAY(String), nullable=True)
    requires_review = Column(Boolean, default=False, nullable=False)

    # Fraud Detection
    fraud_score = Column(Numeric(3, 2), nullable=True)
    fraud_indicators = Column(JSONB, nullable=True)
    is_fraud = Column(Boolean, default=False, nullable=False)

    # Additional Data
    transaction_metadata = Column(JSONB, nullable=True)
    attachments = Column(ARRAY(String), nullable=True)

    # Relationships
    account = relationship("Account", back_populates="transactions")
    risk_assessments = relationship("RiskAssessment", back_populates="transaction")
    audit_logs = relationship("AuditLog", back_populates="transaction")

    # Constraints
    __table_args__ = (
        CheckConstraint('amount != 0', name='ck_transactions_amount_non_zero'),
        CheckConstraint('risk_score >= 0 AND risk_score <= 1', name='ck_transactions_risk_score_range'),
        CheckConstraint('fraud_score >= 0 AND fraud_score <= 1', name='ck_transactions_fraud_score_range'),
        CheckConstraint('length(currency) = 3', name='ck_transactions_currency_length'),
        Index('idx_transactions_account_date', 'account_id', 'transaction_date'),
        Index('idx_transactions_type_status', 'type', 'status'),
        Index('idx_transactions_amount', 'amount'),
        Index('idx_transactions_risk_score', 'risk_score'),
        Index('idx_transactions_fraud_score', 'fraud_score'),
        Index('idx_transactions_requires_review', 'requires_review'),
        Index('idx_transactions_is_fraud', 'is_fraud'),
        Index('idx_transactions_external_id', 'external_id'),
    )

    @validates('amount')
    def validate_amount(self, key, amount):
        if amount == 0:
            raise ValueError("Transaction amount cannot be zero")
        return amount

    @validates('risk_score')
    def validate_risk_score(self, key, risk_score):
        if risk_score is not None and (risk_score < 0 or risk_score > 1):
            raise ValueError("Risk score must be between 0 and 1")
        return risk_score

# Risk Management
class RiskAssessment(BaseModel):
    """Risk assessment model"""
    __tablename__ = 'risk_assessments'

    # Assessment Information
    account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=True)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey('transactions.id'), nullable=True)
    assessment_type = Column(String(50), nullable=False)

    # Risk Metrics
    overall_risk_score = Column(Numeric(3, 2), nullable=False)
    credit_risk_score = Column(Numeric(3, 2), nullable=True)
    operational_risk_score = Column(Numeric(3, 2), nullable=True)
    market_risk_score = Column(Numeric(3, 2), nullable=True)
    liquidity_risk_score = Column(Numeric(3, 2), nullable=True)

    # Risk Factors
    risk_factors = Column(JSONB, nullable=True)
    mitigation_measures = Column(JSONB, nullable=True)
    recommendations = Column(JSONB, nullable=True)

    # Assessment Details
    assessment_date = Column(DateTime(timezone=True), nullable=False)
    assessor_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    next_assessment_date = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    account = relationship("Account", back_populates="risk_assessments")
    transaction = relationship("Transaction", back_populates="risk_assessments")
    assessor = relationship("User")

    # Constraints
    __table_args__ = (
        CheckConstraint('overall_risk_score >= 0 AND overall_risk_score <= 1', name='ck_risk_assessments_overall_score_range'),
        CheckConstraint('credit_risk_score >= 0 AND credit_risk_score <= 1', name='ck_risk_assessments_credit_score_range'),
        CheckConstraint('operational_risk_score >= 0 AND operational_risk_score <= 1', name='ck_risk_assessments_operational_score_range'),
        CheckConstraint('market_risk_score >= 0 AND market_risk_score <= 1', name='ck_risk_assessments_market_score_range'),
        CheckConstraint('liquidity_risk_score >= 0 AND liquidity_risk_score <= 1', name='ck_risk_assessments_liquidity_score_range'),
        Index('idx_risk_assessments_account', 'account_id'),
        Index('idx_risk_assessments_transaction', 'transaction_id'),
        Index('idx_risk_assessments_type', 'assessment_type'),
        Index('idx_risk_assessments_score', 'overall_risk_score'),
        Index('idx_risk_assessments_date', 'assessment_date'),
    )

# Compliance Models
class ComplianceRule(BaseModel):
    """Compliance rule model"""
    __tablename__ = 'compliance_rules'

    # Rule Information
    rule_name = Column(String(200), unique=True, nullable=False)
    rule_description = Column(Text, nullable=True)
    rule_type = Column(String(50), nullable=False)
    standard = Column(String(50), nullable=False)  # PCI_DSS, GDPR, SOX, etc.

    # Rule Configuration
    rule_config = Column(JSONB, nullable=False)
    severity = Column(SQLEnum(RiskLevel), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Enforcement
    auto_remediate = Column(Boolean, default=False, nullable=False)
    notification_required = Column(Boolean, default=True, nullable=False)
    escalation_threshold = Column(Integer, default=3, nullable=False)

    # Relationships
    violations = relationship("ComplianceViolation", back_populates="rule")

    # Constraints
    __table_args__ = (
        CheckConstraint('escalation_threshold > 0', name='ck_compliance_rules_escalation_threshold_positive'),
        Index('idx_compliance_rules_type', 'rule_type'),
        Index('idx_compliance_rules_standard', 'standard'),
        Index('idx_compliance_rules_severity', 'severity'),
        Index('idx_compliance_rules_active', 'is_active'),
    )

class ComplianceViolation(BaseModel):
    """Compliance violation model"""
    __tablename__ = 'compliance_violations'

    # Violation Information
    rule_id = Column(UUID(as_uuid=True), ForeignKey('compliance_rules.id'), nullable=False)
    entity_type = Column(String(50), nullable=False)  # account, transaction, user
    entity_id = Column(UUID(as_uuid=True), nullable=False)

    # Violation Details
    violation_description = Column(Text, nullable=False)
    severity = Column(SQLEnum(RiskLevel), nullable=False)
    status = Column(String(20), default='open', nullable=False)

    # Resolution
    resolution_notes = Column(Text, nullable=True)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    rule = relationship("ComplianceRule", back_populates="violations")
    resolver = relationship("User")

    # Constraints
    __table_args__ = (
        CheckConstraint('status IN (\'open\', \'resolved\', \'false_positive\', \'escalated\')', name='ck_compliance_violations_status'),
        Index('idx_compliance_violations_rule', 'rule_id'),
        Index('idx_compliance_violations_entity', 'entity_type', 'entity_id'),
        Index('idx_compliance_violations_severity', 'severity'),
        Index('idx_compliance_violations_status', 'status'),
        Index('idx_compliance_violations_resolved', 'resolved_at'),
    )

# Audit and Logging
class AuditLog(BaseModel):
    """Enhanced audit log model"""
    __tablename__ = 'audit_logs'

    # Audit Information
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    session_id = Column(String(255), nullable=True)
    action = Column(SQLEnum(AuditAction), nullable=False)

    # Resource Information
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey('transactions.id'), nullable=True)

    # Request Information
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    endpoint = Column(String(500), nullable=True)
    method = Column(String(10), nullable=True)

    # Audit Details
    description = Column(Text, nullable=False)
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    audit_metadata = Column(JSONB, nullable=True)

    # Security
    risk_score = Column(Numeric(3, 2), nullable=True)
    is_suspicious = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
    transaction = relationship("Transaction", back_populates="audit_logs")

    # Constraints
    __table_args__ = (
        CheckConstraint('risk_score >= 0 AND risk_score <= 1', name='ck_audit_logs_risk_score_range'),
        Index('idx_audit_logs_user', 'user_id'),
        Index('idx_audit_logs_action', 'action'),
        Index('idx_audit_logs_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_logs_timestamp', 'created_at'),
        Index('idx_audit_logs_risk_score', 'risk_score'),
        Index('idx_audit_logs_suspicious', 'is_suspicious'),
        Index('idx_audit_logs_ip', 'ip_address'),
    )

# System Configuration
class SystemConfig(BaseModel):
    """System configuration model"""
    __tablename__ = 'system_config'

    # Configuration Information
    config_key = Column(String(100), unique=True, nullable=False, index=True)
    config_value = Column(Text, nullable=False)
    config_type = Column(String(20), nullable=False)  # string, number, boolean, json
    category = Column(String(50), nullable=False)

    # Configuration Metadata
    description = Column(Text, nullable=True)
    is_encrypted = Column(Boolean, default=False, nullable=False)
    is_sensitive = Column(Boolean, default=False, nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint('config_type IN (\'string\', \'number\', \'boolean\', \'json\')', name='ck_system_config_type'),
        Index('idx_system_config_category', 'category'),
        Index('idx_system_config_sensitive', 'is_sensitive'),
    )

# Performance Monitoring
class PerformanceMetric(BaseModel):
    """Performance metric model"""
    __tablename__ = 'performance_metrics'

    # Metric Information
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Numeric(15, 4), nullable=False)
    metric_unit = Column(String(20), nullable=True)

    # Context
    service_name = Column(String(50), nullable=False)
    operation = Column(String(100), nullable=True)
    endpoint = Column(String(500), nullable=True)

    # Timing
    duration_ms = Column(Integer, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    # Additional Data
    performance_metadata = Column(JSONB, nullable=True)

    # Constraints
    __table_args__ = (
        CheckConstraint('metric_value >= 0', name='ck_performance_metrics_value_positive'),
        CheckConstraint('duration_ms >= 0', name='ck_performance_metrics_duration_positive'),
        Index('idx_performance_metrics_name', 'metric_name'),
        Index('idx_performance_metrics_service', 'service_name'),
        Index('idx_performance_metrics_timestamp', 'timestamp'),
        Index('idx_performance_metrics_operation', 'operation'),
    )

# Budget Management
class BudgetCategory(BaseModel):
    """Budget category model"""
    __tablename__ = 'budget_categories'

    # Category Information
    category_name = Column(String(100), nullable=False)
    category_description = Column(Text, nullable=True)
    parent_category_id = Column(UUID(as_uuid=True), ForeignKey('budget_categories.id'), nullable=True)

    # Budget Configuration
    budget_type = Column(String(20), nullable=False)  # monthly, yearly, weekly, custom
    budget_period = Column(String(20), nullable=False)  # month, year, week, custom
    budget_amount = Column(Numeric(15, 2), nullable=False)

    # Tracking
    spent_amount = Column(Numeric(15, 2), default=0, nullable=False)
    remaining_amount = Column(Numeric(15, 2), default=0, nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    alert_threshold = Column(Numeric(3, 2), default=0.8, nullable=False)  # 80% alert

    # Relationships
    parent_category = relationship("BudgetCategory", remote_side=[id], backref="subcategories")
    budgets = relationship("Budget", back_populates="category")
    transactions = relationship("BudgetTransaction", back_populates="category")

    # Constraints
    __table_args__ = (
        CheckConstraint('budget_amount >= 0', name='ck_budget_categories_amount_positive'),
        CheckConstraint('spent_amount >= 0', name='ck_budget_categories_spent_positive'),
        CheckConstraint('remaining_amount >= 0', name='ck_budget_categories_remaining_positive'),
        CheckConstraint('alert_threshold >= 0 AND alert_threshold <= 1', name='ck_budget_categories_threshold_range'),
        CheckConstraint('budget_type IN (\'monthly\', \'yearly\', \'weekly\', \'custom\')', name='ck_budget_categories_type'),
        CheckConstraint('budget_period IN (\'month\', \'year\', \'week\', \'custom\')', name='ck_budget_categories_period'),
        Index('idx_budget_categories_parent', 'parent_category_id'),
        Index('idx_budget_categories_type', 'budget_type'),
        Index('idx_budget_categories_active', 'is_active'),
    )

    @validates('budget_amount')
    def validate_budget_amount(self, key, amount):
        if amount < 0:
            raise ValueError("Budget amount cannot be negative")
        return amount

    @validates('alert_threshold')
    def validate_alert_threshold(self, key, threshold):
        if threshold < 0 or threshold > 1:
            raise ValueError("Alert threshold must be between 0 and 1")
        return threshold

class Budget(BaseModel):
    """Budget model for tracking financial budgets"""
    __tablename__ = 'budgets'

    # Budget Information
    budget_name = Column(String(200), nullable=False)
    budget_description = Column(Text, nullable=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey('budget_categories.id'), nullable=False)

    # Budget Configuration
    budget_type = Column(String(20), nullable=False)  # monthly, yearly, weekly, custom
    budget_period = Column(String(20), nullable=False)  # month, year, week, custom
    budget_amount = Column(Numeric(15, 2), nullable=False)

    # Time Period
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    is_recurring = Column(Boolean, default=False, nullable=False)

    # Tracking
    spent_amount = Column(Numeric(15, 2), default=0, nullable=False)
    remaining_amount = Column(Numeric(15, 2), default=0, nullable=False)
    alert_threshold = Column(Numeric(3, 2), default=0.8, nullable=False)

    # Status
    status = Column(String(20), default='active', nullable=False)  # active, paused, completed, cancelled
    is_template = Column(Boolean, default=False, nullable=False)

    # Relationships
    category = relationship("BudgetCategory", back_populates="budgets")
    transactions = relationship("BudgetTransaction", back_populates="budget")
    alerts = relationship("BudgetAlert", back_populates="budget")

    # Constraints
    __table_args__ = (
        CheckConstraint('budget_amount >= 0', name='ck_budgets_amount_positive'),
        CheckConstraint('spent_amount >= 0', name='ck_budgets_spent_positive'),
        CheckConstraint('remaining_amount >= 0', name='ck_budgets_remaining_positive'),
        CheckConstraint('alert_threshold >= 0 AND alert_threshold <= 1', name='ck_budgets_threshold_range'),
        CheckConstraint('budget_type IN (\'monthly\', \'yearly\', \'weekly\', \'custom\')', name='ck_budgets_type'),
        CheckConstraint('budget_period IN (\'month\', \'year\', \'week\', \'custom\')', name='ck_budgets_period'),
        CheckConstraint('status IN (\'active\', \'paused\', \'completed\', \'cancelled\')', name='ck_budgets_status'),
        CheckConstraint('end_date > start_date', name='ck_budgets_date_range'),
        Index('idx_budgets_category', 'category_id'),
        Index('idx_budgets_type', 'budget_type'),
        Index('idx_budgets_period', 'budget_period'),
        Index('idx_budgets_status', 'status'),
        Index('idx_budgets_date_range', 'start_date', 'end_date'),
        Index('idx_budgets_template', 'is_template'),
    )

    @validates('budget_amount')
    def validate_budget_amount(self, key, amount):
        if amount < 0:
            raise ValueError("Budget amount cannot be negative")
        return amount

    @validates('alert_threshold')
    def validate_alert_threshold(self, key, threshold):
        if threshold < 0 or threshold > 1:
            raise ValueError("Alert threshold must be between 0 and 1")
        return threshold

class BudgetTransaction(BaseModel):
    """Budget transaction model"""
    __tablename__ = 'budget_transactions'

    # Transaction Information
    budget_id = Column(UUID(as_uuid=True), ForeignKey('budgets.id'), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey('budget_categories.id'), nullable=False)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey('transactions.id'), nullable=True)

    # Transaction Details
    amount = Column(Numeric(15, 2), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # expense, income, transfer
    description = Column(Text, nullable=True)

    # Metadata
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    budget_metadata = Column(JSONB, nullable=True)

    # Relationships
    budget = relationship("Budget", back_populates="transactions")
    category = relationship("BudgetCategory", back_populates="transactions")
    transaction = relationship("Transaction")

    # Constraints
    __table_args__ = (
        CheckConstraint('amount != 0', name='ck_budget_transactions_amount_non_zero'),
        CheckConstraint('transaction_type IN (\'expense\', \'income\', \'transfer\')', name='ck_budget_transactions_type'),
        Index('idx_budget_transactions_budget', 'budget_id'),
        Index('idx_budget_transactions_category', 'category_id'),
        Index('idx_budget_transactions_transaction', 'transaction_id'),
        Index('idx_budget_transactions_type', 'transaction_type'),
        Index('idx_budget_transactions_date', 'transaction_date'),
    )

    @validates('amount')
    def validate_amount(self, key, amount):
        if amount == 0:
            raise ValueError("Transaction amount cannot be zero")
        return amount

class BudgetAlert(BaseModel):
    """Budget alert model"""
    __tablename__ = 'budget_alerts'

    # Alert Information
    budget_id = Column(UUID(as_uuid=True), ForeignKey('budgets.id'), nullable=False)
    alert_type = Column(String(50), nullable=False)  # threshold_exceeded, budget_completed, etc.

    # Alert Details
    alert_message = Column(Text, nullable=False)
    alert_threshold = Column(Numeric(3, 2), nullable=True)
    current_amount = Column(Numeric(15, 2), nullable=True)
    budget_amount = Column(Numeric(15, 2), nullable=True)

    # Status
    status = Column(String(20), default='active', nullable=False)  # active, acknowledged, resolved
    severity = Column(String(20), default='medium', nullable=False)  # low, medium, high, critical

    # Notification
    notification_sent = Column(Boolean, default=False, nullable=False)
    acknowledged_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    budget = relationship("Budget", back_populates="alerts")
    acknowledger = relationship("User")

    # Constraints
    __table_args__ = (
        CheckConstraint('alert_threshold >= 0 AND alert_threshold <= 1', name='ck_budget_alerts_threshold_range'),
        CheckConstraint('current_amount >= 0', name='ck_budget_alerts_current_positive'),
        CheckConstraint('budget_amount >= 0', name='ck_budget_alerts_budget_positive'),
        CheckConstraint('status IN (\'active\', \'acknowledged\', \'resolved\')', name='ck_budget_alerts_status'),
        CheckConstraint('severity IN (\'low\', \'medium\', \'high\', \'critical\')', name='ck_budget_alerts_severity'),
        Index('idx_budget_alerts_budget', 'budget_id'),
        Index('idx_budget_alerts_type', 'alert_type'),
        Index('idx_budget_alerts_status', 'status'),
        Index('idx_budget_alerts_severity', 'severity'),
    )

# Analytics and Reporting
class AnalyticsReport(BaseModel):
    """Analytics report model"""
    __tablename__ = 'analytics_reports'

    # Report Information
    report_name = Column(String(200), nullable=False)
    report_description = Column(Text, nullable=True)
    report_type = Column(String(50), nullable=False)  # spending, income, budget, investment, etc.

    # Report Configuration
    report_config = Column(JSONB, nullable=False)
    data_source = Column(String(50), nullable=False)  # transactions, accounts, budgets, etc.
    date_range = Column(String(20), nullable=False)  # last_30_days, last_90_days, last_year, custom

    # Report Results
    report_data = Column(JSONB, nullable=True)
    summary_stats = Column(JSONB, nullable=True)
    insights = Column(JSONB, nullable=True)

    # Scheduling
    is_scheduled = Column(Boolean, default=False, nullable=False)
    schedule_config = Column(JSONB, nullable=True)
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True)

    # Status
    status = Column(String(20), default='active', nullable=False)  # active, paused, draft, archived
    is_template = Column(Boolean, default=False, nullable=False)

    # Relationships
    created_by_user = relationship("User")
    report_executions = relationship("ReportExecution", back_populates="report")

    # Constraints
    __table_args__ = (
        CheckConstraint('report_type IN (\'spending\', \'income\', \'budget\', \'investment\', \'tax\', \'custom\')', name='ck_analytics_reports_type'),
        CheckConstraint('data_source IN (\'transactions\', \'accounts\', \'budgets\', \'users\', \'custom\')', name='ck_analytics_reports_source'),
        CheckConstraint('date_range IN (\'last_7_days\', \'last_30_days\', \'last_90_days\', \'last_year\', \'custom\')', name='ck_analytics_reports_range'),
        CheckConstraint('status IN (\'active\', \'paused\', \'draft\', \'archived\')', name='ck_analytics_reports_status'),
        Index('idx_analytics_reports_type', 'report_type'),
        Index('idx_analytics_reports_source', 'data_source'),
        Index('idx_analytics_reports_status', 'status'),
        Index('idx_analytics_reports_template', 'is_template'),
        Index('idx_analytics_reports_scheduled', 'is_scheduled'),
    )

class ReportExecution(BaseModel):
    """Report execution history model"""
    __tablename__ = 'report_executions'

    # Execution Information
    report_id = Column(UUID(as_uuid=True), ForeignKey('analytics_reports.id'), nullable=False)
    execution_type = Column(String(20), nullable=False)  # manual, scheduled, api

    # Execution Details
    execution_status = Column(String(20), nullable=False)  # running, completed, failed, cancelled
    execution_time = Column(Integer, nullable=True)  # execution time in seconds
    records_processed = Column(Integer, default=0, nullable=False)

    # Results
    result_data = Column(JSONB, nullable=True)
    summary_stats = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)

    # Metadata
    execution_metadata = Column(JSONB, nullable=True)
    parameters_used = Column(JSONB, nullable=True)

    # Relationships
    report = relationship("AnalyticsReport", back_populates="report_executions")

    # Constraints
    __table_args__ = (
        CheckConstraint('records_processed >= 0', name='ck_report_executions_records_positive'),
        CheckConstraint('execution_time >= 0', name='ck_report_executions_time_positive'),
        CheckConstraint('execution_type IN (\'manual\', \'scheduled\', \'api\')', name='ck_report_executions_type'),
        CheckConstraint('execution_status IN (\'running\', \'completed\', \'failed\', \'cancelled\')', name='ck_report_executions_status'),
        Index('idx_report_executions_report', 'report_id'),
        Index('idx_report_executions_status', 'execution_status'),
        Index('idx_report_executions_type', 'execution_type'),
    )

class FinancialInsight(BaseModel):
    """Financial insights model"""
    __tablename__ = 'financial_insights'

    # Insight Information
    insight_type = Column(String(50), nullable=False)  # spending_pattern, income_trend, budget_variance, etc.
    insight_title = Column(String(200), nullable=False)
    insight_description = Column(Text, nullable=False)

    # Insight Data
    insight_data = Column(JSONB, nullable=False)
    confidence_score = Column(Numeric(3, 2), nullable=True)
    data_points = Column(Integer, nullable=True)

    # Context
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey('budget_categories.id'), nullable=True)

    # Time Period
    insight_period_start = Column(DateTime(timezone=True), nullable=True)
    insight_period_end = Column(DateTime(timezone), nullable=True)

    # Status
    is_actionable = Column(Boolean, default=False, nullable=False)
    priority = Column(String(20), default='medium', nullable=False)  # low, medium, high
    status = Column(String(20), default='active', nullable=False)  # active, dismissed, applied

    # Relationships
    user = relationship("User")
    account = relationship("Account")
    category = relationship("BudgetCategory")

    # Constraints
    __table_args__ = (
        CheckConstraint('confidence_score >= 0 AND confidence_score <= 1', name='ck_financial_insights_confidence_range'),
        CheckConstraint('data_points >= 0', name='ck_financial_insights_points_positive'),
        CheckConstraint('insight_type IN (\'spending_pattern\', \'income_trend\', \'budget_variance\', \'investment_opportunity\', \'tax_optimization\', \'custom\')', name='ck_financial_insights_type'),
        CheckConstraint('priority IN (\'low\', \'medium\', \'high\')', name='ck_financial_insights_priority'),
        CheckConstraint('status IN (\'active\', \'dismissed\', \'applied\')', name='ck_financial_insights_status'),
        Index('idx_financial_insights_type', 'insight_type'),
        Index('idx_financial_insights_user', 'user_id'),
        Index('idx_financial_insights_account', 'account_id'),
        Index('idx_financial_insights_category', 'category_id'),
        Index('idx_financial_insights_priority', 'priority'),
        Index('idx_financial_insights_status', 'status'),
        Index('idx_financial_insights_actionable', 'is_actionable'),
    )

class PredictiveModel(BaseModel):
    """Predictive model results model"""
    __tablename__ = 'predictive_models'

    # Model Information
    model_name = Column(String(100), nullable=False)
    model_type = Column(String(50), nullable=False)  # spending_forecast, income_prediction, budget_optimization, etc.
    model_version = Column(String(20), nullable=False)

    # Model Configuration
    model_config = Column(JSONB, nullable=False)
    training_data_range = Column(String(20), nullable=False)
    features_used = Column(ARRAY(String), nullable=False)

    # Model Results
    predictions = Column(JSONB, nullable=False)
    accuracy_metrics = Column(JSONB, nullable=True)
    confidence_intervals = Column(JSONB, nullable=True)

    # Time Period
    prediction_start = Column(DateTime(timezone=True), nullable=False)
    prediction_end = Column(DateTime(timezone=True), nullable=False)

    # Context
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=True)

    # Status
    status = Column(String(20), default='active', nullable=False)  # active, deprecated, retraining
    is_current = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("User")
    account = relationship("Account")

    # Constraints
    __table_args__ = (
        CheckConstraint('model_type IN (\'spending_forecast\', \'income_prediction\', \'budget_optimization\', \'investment_strategy\', \'risk_assessment\')', name='ck_predictive_models_type'),
        CheckConstraint('training_data_range IN (\'last_30_days\', \'last_90_days\', \'last_year\', \'all_time\')', name='ck_predictive_models_range'),
        CheckConstraint('status IN (\'active\', \'deprecated\', \'retraining\')', name='ck_predictive_models_status'),
        CheckConstraint('prediction_end > prediction_start', name='ck_predictive_models_date_range'),
        Index('idx_predictive_models_type', 'model_type'),
        Index('idx_predictive_models_user', 'user_id'),
        Index('idx_predictive_models_account', 'account_id'),
        Index('idx_predictive_models_status', 'status'),
        Index('idx_predictive_models_current', 'is_current'),
        Index('idx_predictive_models_date_range', 'prediction_start', 'prediction_end'),
    )
