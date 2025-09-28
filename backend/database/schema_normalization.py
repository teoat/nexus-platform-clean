#!/usr/bin/env python3
"""
NEXUS Platform - Database Schema Normalization
Unified database schema with optimized relationships and indexes
"""

import asyncio
import json
import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import asyncpg
from asyncpg import Pool
from sqlalchemy import ARRAY, JSON, Boolean, CheckConstraint, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import (Float, ForeignKey, Index, Integer, String, Text,
                        UniqueConstraint, create_engine)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import (DeclarativeBase, Session, relationship,
                            sessionmaker, validates)
from sqlalchemy.sql import func

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Database base
class Base(DeclarativeBase):
    pass


class UserRole(Enum):
    """User role enumeration"""

    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    GUEST = "guest"


class AccountType(Enum):
    """Account type enumeration"""

    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT = "credit"
    INVESTMENT = "investment"
    LOAN = "loan"


class TransactionType(Enum):
    """Transaction type enumeration"""

    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    INVESTMENT = "investment"
    LOAN_PAYMENT = "loan_payment"


class TransactionStatus(Enum):
    """Transaction status enumeration"""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationType(Enum):
    """Notification type enumeration"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    ALERT = "alert"


class UserRole(Enum):
    ADMIN = "admin"
    COMPLIANCE_OFFICER = "compliance_officer"
    FINANCIAL_ANALYST = "financial_analyst"
    AUDITOR = "auditor"
    VIEWER = "viewer"
    MANAGER = "manager"
    USER = "user"
    GUEST = "guest"


class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    REFUND = "refund"
    FEE = "fee"
    INTEREST = "interest"
    INCOME = "income"
    EXPENSE = "expense"
    INVESTMENT = "investment"
    LOAN_PAYMENT = "loan_payment"


class TransactionStatus(Enum):
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


class AuditAction(Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    ACCESS = "access"
    EXPORT = "export"
    IMPORT = "import"


# Base model with common fields
class BaseModel(Base):
    """Base model with common fields and methods"""

    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    version = Column(Integer, default=1, nullable=False)

    @validates("email")
    def validate_email(self, key, email):
        if email and not re.match(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email
        ):
            raise ValueError("Invalid email format")
        return email


# Core User Management
class User(Base):
    """Enhanced user table with POV support"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    full_name = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth users
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.USER)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    email_verified_at = Column(DateTime(timezone=True))
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
    extra_metadata = Column(JSONB, default=dict)

    # POV Configuration
    primary_pov_role = Column(String(50), nullable=True)
    secondary_pov_roles = Column(JSON, nullable=True)  # List of POV roles
    analysis_mode = Column(String(20), default="single_pov")
    ai_intervention_level = Column(String(20), default="assisted")

    # OAuth Support
    oauth_provider = Column(String(50), nullable=True)
    oauth_provider_id = Column(String(255), nullable=True)

    # Relationships
    accounts = relationship(
        "Account", back_populates="user", cascade="all, delete-orphan"
    )
    transactions = relationship(
        "Transaction", back_populates="user", cascade="all, delete-orphan"
    )
    notifications = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    audit_logs = relationship(
        "AuditLog", back_populates="user", cascade="all, delete-orphan"
    )
    # user_preferences relationship removed - using enhanced_models.py version instead
    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    settings = relationship(
        "UserSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    preferences = relationship(
        "UserPreferences",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    oauth_accounts = relationship(
        "OAuthAccount", back_populates="user", cascade="all, delete-orphan"
    )
    frenly_ai_config = relationship(
        "FrenlyAIConfiguration",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    projects = relationship(
        "Project", back_populates="user", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_users_email_active", "email", "is_active"),
        Index("idx_users_username_active", "username", "is_active"),
        Index("idx_users_role_active", "role", "is_active"),
        Index("idx_users_created_at", "created_at"),
    )


# UserPreference class removed - using enhanced_models.py version instead


# Financial Management
class Account(Base):
    """Normalized account table"""

    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(100), nullable=False)
    account_type = Column(SQLEnum(AccountType), nullable=False)
    account_number = Column(String(50), nullable=True, index=True)
    balance = Column(Float, default=0.0, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
    extra_metadata = Column(JSONB, default=dict)

    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship(
        "Transaction", back_populates="account", cascade="all, delete-orphan"
    )

    # Constraints and Indexes
    __table_args__ = (
        CheckConstraint("balance >= 0", name="check_balance_positive"),
        Index("idx_accounts_user_id", "user_id"),
        Index("idx_accounts_type_active", "account_type", "is_active"),
        Index("idx_accounts_user_type", "user_id", "account_type"),
        UniqueConstraint("user_id", "name", name="unique_user_account_name"),
    )


class Category(Base):
    """Transaction categories"""

    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
    extra_metadata = Column(JSONB, default=dict)

    # Relationships
    parent = relationship("Category", remote_side=[id])
    children = relationship("Category", back_populates="parent")
    transactions = relationship("Transaction", back_populates="category")

    # Indexes
    __table_args__ = (
        Index("idx_categories_parent_id", "parent_id"),
        Index("idx_categories_active", "is_active"),
    )


class Transaction(Base):
    """Normalized transaction table"""

    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    status = Column(
        SQLEnum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False
    )
    description = Column(Text, nullable=True)
    reference_number = Column(String(100), nullable=True, index=True)
    transaction_date = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
    extra_metadata = Column(JSONB, default=dict)

    # Relationships
    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

    # Constraints and Indexes
    __table_args__ = (
        CheckConstraint("amount != 0", name="check_amount_non_zero"),
        Index("idx_transactions_user_id", "user_id"),
        Index("idx_transactions_account_id", "account_id"),
        Index("idx_transactions_category_id", "category_id"),
        Index("idx_transactions_type_status", "transaction_type", "status"),
        Index("idx_transactions_date", "transaction_date"),
        Index("idx_transactions_user_date", "user_id", "transaction_date"),
        Index("idx_transactions_account_date", "account_id", "transaction_date"),
    )


# Notification System
class Notification(Base):
    """User notifications"""

    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(SQLEnum(NotificationType), nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    extra_metadata = Column(JSONB, default=dict)

    # Relationships
    user = relationship("User", back_populates="notifications")

    # Indexes
    __table_args__ = (
        Index("idx_notifications_user_id", "user_id"),
        Index("idx_notifications_type", "notification_type"),
        Index("idx_notifications_read", "is_read"),
        Index("idx_notifications_created_at", "created_at"),
        Index("idx_notifications_user_read", "user_id", "is_read"),
    )


# Audit and Logging
class AuditLog(Base):
    """Audit trail for all actions"""

    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action = Column(SQLEnum(AuditAction), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=True)
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    extra_metadata = Column(JSONB, default=dict)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    # Indexes
    __table_args__ = (
        Index("idx_audit_logs_user_id", "user_id"),
        Index("idx_audit_logs_action", "action"),
        Index("idx_audit_logs_resource", "resource_type", "resource_id"),
        Index("idx_audit_logs_created_at", "created_at"),
        Index("idx_audit_logs_user_action", "user_id", "action"),
    )


# System Configuration
class SystemConfig(Base):
    """System-wide configuration"""

    __tablename__ = "system_config"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    value_type = Column(String(20), nullable=False)  # string, int, float, bool, json
    description = Column(Text, nullable=True)
    is_encrypted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    updated_by_user = relationship("User")


# File Management
class File(Base):
    """File storage metadata"""

    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
    extra_metadata = Column(JSONB, default=dict)

    # Relationships
    user = relationship("User")

    # Indexes
    __table_args__ = (
        Index("idx_files_user_id", "user_id"),
        Index("idx_files_content_type", "content_type"),
        Index("idx_files_created_at", "created_at"),
        Index("idx_files_public", "is_public"),
    )


class DatabaseManager:
    """Database connection and management"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.session_factory = None
        self.pool = None

    async def initialize(self):
        """Initialize database connections"""
        try:
            # SQLAlchemy engine
            self.engine = create_engine(
                self.database_url,
                pool_size=20,
                max_overflow=30,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False,
            )

            # Session factory
            self.session_factory = sessionmaker(bind=self.engine)

            # AsyncPG pool for raw queries
            if "postgresql" in self.database_url:
                self.pool = await asyncpg.create_pool(
                    self.database_url, min_size=10, max_size=20, command_timeout=60
                )

            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    async def create_tables(self):
        """Create all tables"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise

    async def drop_tables(self):
        """Drop all tables"""
        try:
            Base.metadata.drop_all(self.engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise

    def get_session(self) -> Session:
        """Get database session"""
        return self.session_factory()

    async def execute_raw_query(self, query: str, *args) -> List[Dict]:
        """Execute raw SQL query"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]

    async def close(self):
        """Close database connections"""
        if self.engine:
            self.engine.dispose()

        if self.pool:
            await self.pool.close()

        logger.info("Database connections closed")


class SchemaOptimizer:
    """Database schema optimization utilities"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    async def analyze_performance(self) -> Dict[str, Any]:
        """Analyze database performance"""
        if not self.db_manager.pool:
            return {}

        queries = [
            "SELECT schemaname, tablename, attname, n_distinct, correlation FROM pg_stats WHERE schemaname = 'public'",
            "SELECT schemaname, tablename, indexname, indexdef FROM pg_indexes WHERE schemaname = 'public'",
            "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10",
        ]

        results = {}
        for i, query in enumerate(queries):
            try:
                results[f"query_{i}"] = await self.db_manager.execute_raw_query(query)
            except Exception as e:
                logger.error(f"Failed to execute performance query {i}: {e}")

        return results

    async def optimize_indexes(self) -> List[str]:
        """Suggest index optimizations"""
        suggestions = []

        # Analyze missing indexes
        missing_indexes_query = """
        SELECT
            schemaname,
            tablename,
            attname,
            n_distinct,
            correlation
        FROM pg_stats
        WHERE schemaname = 'public'
        AND n_distinct > 100
        AND correlation < 0.1
        ORDER BY n_distinct DESC
        """

        try:
            results = await self.db_manager.execute_raw_query(missing_indexes_query)
            for row in results:
                suggestions.append(
                    f"Consider adding index on {row['tablename']}.{row['attname']} "
                    f"(distinct values: {row['n_distinct']}, correlation: {row['correlation']})"
                )
        except Exception as e:
            logger.error(f"Failed to analyze missing indexes: {e}")

        return suggestions

    async def get_table_stats(self) -> Dict[str, Any]:
        """Get table statistics"""
        stats_query = """
        SELECT
            schemaname,
            tablename,
            n_tup_ins as inserts,
            n_tup_upd as updates,
            n_tup_del as deletes,
            n_live_tup as live_tuples,
            n_dead_tup as dead_tuples
        FROM pg_stat_user_tables
        ORDER BY n_live_tup DESC
        """

        try:
            return await self.db_manager.execute_raw_query(stats_query)
        except Exception as e:
            logger.error(f"Failed to get table stats: {e}")
            return []


# Global database manager
db_manager = None


async def initialize_database(database_url: str):
    """Initialize global database manager"""
    global db_manager
    db_manager = DatabaseManager(database_url)
    await db_manager.initialize()
    await db_manager.create_tables()


async def get_database_session() -> Session:
    """Get database session"""
    if not db_manager:
        raise RuntimeError("Database not initialized")
    return db_manager.get_session()


if __name__ == "__main__":
    # Example usage
    async def main():
        # Initialize database
        database_url = "postgresql://user:password@localhost:5432/nexus"
        await initialize_database(database_url)

        # Get session and create some data
        session = get_database_session()

        try:
            # Create a user
            user = User(
                email="test@example.com",
                username="testuser",
                first_name="Test",
                last_name="User",
                password_hash="hashed_password",
                role=UserRole.USER,
            )
            session.add(user)
            session.commit()

            # Create user preferences
            preferences = UserPreference(
                user_id=user.id, theme="dark", language="en", currency="USD"
            )
            session.add(preferences)

            # Create an account
            account = Account(
                user_id=user.id,
                name="Checking Account",
                account_type=AccountType.CHECKING,
                balance=1000.0,
            )
            session.add(account)

            # Create a category
            category = Category(
                name="Food & Dining", description="Restaurants and food expenses"
            )
            session.add(category)

            # Create a transaction
            transaction = Transaction(
                user_id=user.id,
                account_id=account.id,
                category_id=category.id,
                amount=25.50,
                transaction_type=TransactionType.EXPENSE,
                description="Lunch at restaurant",
                transaction_date=datetime.now(timezone.utc),
            )
            session.add(transaction)

            session.commit()

            print("Sample data created successfully")

            # Analyze performance
            optimizer = SchemaOptimizer(db_manager)
            suggestions = await optimizer.optimize_indexes()
            print(f"Index optimization suggestions: {suggestions}")

        except Exception as e:
            session.rollback()
            print(f"Error: {e}")
        finally:
            session.close()
            await db_manager.close()

    asyncio.run(main())

    @validates("email")
    def validate_email(self, key, email):
        if email and not re.match(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email
        ):
            raise ValueError("Invalid email format")
        return email

    @validates("phone")
    def validate_phone(self, key, phone):
        if phone and not re.match(
            r"^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$", phone
        ):
            raise ValueError("Invalid phone format")
# Notification System
    # Relationships
    user = relationship("User", back_populates="notifications")

    # Indexes
    __table_args__ = (
        Index("idx_notifications_user_id", "user_id"),
        Index("idx_notifications_type", "notification_type"),
        Index("idx_notifications_read", "is_read"),
        Index("idx_notifications_created_at", "created_at"),
        Index("idx_notifications_user_read", "user_id", "is_read"),
    )


# Audit and Logging
    # Relationships
    user = relationship("User", back_populates="audit_logs")

    # Indexes
    __table_args__ = (
        Index("idx_audit_logs_user_id", "user_id"),
        Index("idx_audit_logs_action", "action"),
        Index("idx_audit_logs_resource", "resource_type", "resource_id"),
        Index("idx_audit_logs_created_at", "created_at"),
        Index("idx_audit_logs_user_action", "user_id", "action"),
    )


# System Configuration
    # Relationships
    updated_by_user = relationship("User")


# File Management
    # Relationships
    user = relationship("User")

    # Indexes
    __table_args__ = (
        Index("idx_files_user_id", "user_id"),
        Index("idx_files_content_type", "content_type"),
        Index("idx_files_created_at", "created_at"),
        Index("idx_files_public", "is_public"),
    )


class DatabaseManager:
    """Database connection and management"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.session_factory = None
        self.pool = None

    async def initialize(self):
        """Initialize database connections"""
        try:
            # SQLAlchemy engine
            self.engine = create_engine(
                self.database_url,
                pool_size=20,
                max_overflow=30,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False,
            )

            # Session factory
            self.session_factory = sessionmaker(bind=self.engine)

            # AsyncPG pool for raw queries
            if "postgresql" in self.database_url:
                self.pool = await asyncpg.create_pool(
                    self.database_url, min_size=10, max_size=20, command_timeout=60
                )

            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    async def create_tables(self):
        """Create all tables"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise

    async def drop_tables(self):
        """Drop all tables"""
        try:
            Base.metadata.drop_all(self.engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise

    def get_session(self) -> Session:
        """Get database session"""
        return self.session_factory()

    async def execute_raw_query(self, query: str, *args) -> List[Dict]:
        """Execute raw SQL query"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]

    async def close(self):
        """Close database connections"""
        if self.engine:
            self.engine.dispose()

        if self.pool:
            await self.pool.close()

        logger.info("Database connections closed")


class SchemaOptimizer:
    """Database schema optimization utilities"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    async def analyze_performance(self) -> Dict[str, Any]:
        """Analyze database performance"""
        if not self.db_manager.pool:
            return {}

        queries = [
            "SELECT schemaname, tablename, attname, n_distinct, correlation FROM pg_stats WHERE schemaname = 'public'",
            "SELECT schemaname, tablename, indexname, indexdef FROM pg_indexes WHERE schemaname = 'public'",
            "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10",
        ]

        results = {}
        for i, query in enumerate(queries):
            try:
                results[f"query_{i}"] = await self.db_manager.execute_raw_query(query)
            except Exception as e:
                logger.error(f"Failed to execute performance query {i}: {e}")

        return results

    async def optimize_indexes(self) -> List[str]:
        """Suggest index optimizations"""
        suggestions = []

        # Analyze missing indexes
        missing_indexes_query = """
        SELECT
            schemaname,
            tablename,
            attname,
            n_distinct,
            correlation
        FROM pg_stats
        WHERE schemaname = 'public'
        AND n_distinct > 100
        AND correlation < 0.1
        ORDER BY n_distinct DESC
        """

        try:
            results = await self.db_manager.execute_raw_query(missing_indexes_query)
            for row in results:
                suggestions.append(
                    f"Consider adding index on {row['tablename']}.{row['attname']} "
                    f"(distinct values: {row['n_distinct']}, correlation: {row['correlation']})"
                )
        except Exception as e:
            logger.error(f"Failed to analyze missing indexes: {e}")

        return suggestions

    async def get_table_stats(self) -> Dict[str, Any]:
        """Get table statistics"""
        stats_query = """
        SELECT
            schemaname,
            tablename,
            n_tup_ins as inserts,
            n_tup_upd as updates,
            n_tup_del as deletes,
            n_live_tup as live_tuples,
            n_dead_tup as dead_tuples
        FROM pg_stat_user_tables
        ORDER BY n_live_tup DESC
        """

        try:
            return await self.db_manager.execute_raw_query(stats_query)
        except Exception as e:
            logger.error(f"Failed to get table stats: {e}")
            return []


# Global database manager
db_manager = None


async def initialize_database(database_url: str):
    """Initialize global database manager"""
    global db_manager
    db_manager = DatabaseManager(database_url)
    await db_manager.initialize()
    await db_manager.create_tables()


async def get_database_session() -> Session:
    """Get database session"""
    if not db_manager:
        raise RuntimeError("Database not initialized")
    return db_manager.get_session()


if __name__ == "__main__":
    # Example usage
    async def main():
        # Initialize database
        database_url = "postgresql://user:password@localhost:5432/nexus"
        await initialize_database(database_url)

        # Get session and create some data
        session = get_database_session()

        try:
            # Create a user
            user = User(
                email="test@example.com",
                username="testuser",
                first_name="Test",
                last_name="User",
                password_hash="hashed_password",
                role=UserRole.USER,
            )
            session.add(user)
            session.commit()

            # Create user preferences
            preferences = UserPreference(
                user_id=user.id, theme="dark", language="en", currency="USD"
            )
            session.add(preferences)

            # Create an account
            account = Account(
                user_id=user.id,
                name="Checking Account",
                account_type=AccountType.CHECKING,
                balance=1000.0,
            )
            session.add(account)

            # Create a category
            category = Category(
                name="Food & Dining", description="Restaurants and food expenses"
            )
            session.add(category)

            # Create a transaction
            transaction = Transaction(
                user_id=user.id,
                account_id=account.id,
                category_id=category.id,
                amount=25.50,
                transaction_type=TransactionType.EXPENSE,
                description="Lunch at restaurant",
                transaction_date=datetime.now(timezone.utc),
            )
            session.add(transaction)

            session.commit()

            print("Sample data created successfully")

            # Analyze performance
            optimizer = SchemaOptimizer(db_manager)
            suggestions = await optimizer.optimize_indexes()
            print(f"Index optimization suggestions: {suggestions}")

        except Exception as e:
            session.rollback()
            print(f"Error: {e}")
        finally:
            session.close()
            await db_manager.close()

    asyncio.run(main())


# Core User Management
    # POV Configuration
    primary_pov_role = Column(String(50), nullable=True)
    secondary_pov_roles = Column(JSON, nullable=True)  # List of POV roles
    analysis_mode = Column(String(20), default="single_pov")
    ai_intervention_level = Column(String(20), default="assisted")

    # OAuth Support
    oauth_provider = Column(String(50), nullable=True)
    oauth_provider_id = Column(String(255), nullable=True)

    # Relationships
    accounts = relationship(
        "Account", back_populates="user", cascade="all, delete-orphan"
    )
    transactions = relationship(
        "Transaction", back_populates="user", cascade="all, delete-orphan"
    )
    notifications = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    audit_logs = relationship(
        "AuditLog", back_populates="user", cascade="all, delete-orphan"
    )
    # user_preferences relationship removed - using enhanced_models.py version instead
    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    settings = relationship(
        "UserSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    preferences = relationship(
        "UserPreferences",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    oauth_accounts = relationship(
        "OAuthAccount", back_populates="user", cascade="all, delete-orphan"
    )
    frenly_ai_config = relationship(
        "FrenlyAIConfiguration",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    projects = relationship(
        "Project", back_populates="user", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_users_email_active", "email", "is_active"),
        Index("idx_users_username_active", "username", "is_active"),
        Index("idx_users_role_active", "role", "is_active"),
        Index("idx_users_created_at", "created_at"),
    )


    # Relationships
    # user relationship removed - using enhanced_models.py version instead


# Financial Management
# Notification System
    # Relationships
    user = relationship("User", back_populates="notifications")

    # Indexes
    __table_args__ = (
        Index("idx_notifications_user_id", "user_id"),
        Index("idx_notifications_type", "notification_type"),
        Index("idx_notifications_read", "is_read"),
        Index("idx_notifications_created_at", "created_at"),
        Index("idx_notifications_user_read", "user_id", "is_read"),
    )


# Audit and Logging
    # Relationships
    user = relationship("User", back_populates="audit_logs")

    # Indexes
    __table_args__ = (
        Index("idx_audit_logs_user_id", "user_id"),
        Index("idx_audit_logs_action", "action"),
        Index("idx_audit_logs_resource", "resource_type", "resource_id"),
        Index("idx_audit_logs_created_at", "created_at"),
        Index("idx_audit_logs_user_action", "user_id", "action"),
    )


# System Configuration
    # Relationships
    updated_by_user = relationship("User")


# File Management
    # Relationships
    user = relationship("User")

    # Indexes
    __table_args__ = (
        Index("idx_files_user_id", "user_id"),
        Index("idx_files_content_type", "content_type"),
        Index("idx_files_created_at", "created_at"),
        Index("idx_files_public", "is_public"),
    )


class DatabaseManager:
    """Database connection and management"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.session_factory = None
        self.pool = None

    async def initialize(self):
        """Initialize database connections"""
        try:
            # SQLAlchemy engine
            self.engine = create_engine(
                self.database_url,
                pool_size=20,
                max_overflow=30,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False,
            )

            # Session factory
            self.session_factory = sessionmaker(bind=self.engine)

            # AsyncPG pool for raw queries
            if "postgresql" in self.database_url:
                self.pool = await asyncpg.create_pool(
                    self.database_url, min_size=10, max_size=20, command_timeout=60
                )

            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    async def create_tables(self):
        """Create all tables"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise

    async def drop_tables(self):
        """Drop all tables"""
        try:
            Base.metadata.drop_all(self.engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise

    def get_session(self) -> Session:
        """Get database session"""
        return self.session_factory()

    async def execute_raw_query(self, query: str, *args) -> List[Dict]:
        """Execute raw SQL query"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]

    async def close(self):
        """Close database connections"""
        if self.engine:
            self.engine.dispose()

        if self.pool:
            await self.pool.close()

        logger.info("Database connections closed")


class SchemaOptimizer:
    """Database schema optimization utilities"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    async def analyze_performance(self) -> Dict[str, Any]:
        """Analyze database performance"""
        if not self.db_manager.pool:
            return {}

        queries = [
            "SELECT schemaname, tablename, attname, n_distinct, correlation FROM pg_stats WHERE schemaname = 'public'",
            "SELECT schemaname, tablename, indexname, indexdef FROM pg_indexes WHERE schemaname = 'public'",
            "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10",
        ]

        results = {}
        for i, query in enumerate(queries):
            try:
                results[f"query_{i}"] = await self.db_manager.execute_raw_query(query)
            except Exception as e:
                logger.error(f"Failed to execute performance query {i}: {e}")

        return results

    async def optimize_indexes(self) -> List[str]:
        """Suggest index optimizations"""
        suggestions = []

        # Analyze missing indexes
        missing_indexes_query = """
        SELECT
            schemaname,
            tablename,
            attname,
            n_distinct,
            correlation
        FROM pg_stats
        WHERE schemaname = 'public'
        AND n_distinct > 100
        AND correlation < 0.1
        ORDER BY n_distinct DESC
        """

        try:
            results = await self.db_manager.execute_raw_query(missing_indexes_query)
            for row in results:
                suggestions.append(
                    f"Consider adding index on {row['tablename']}.{row['attname']} "
                    f"(distinct values: {row['n_distinct']}, correlation: {row['correlation']})"
                )
        except Exception as e:
            logger.error(f"Failed to analyze missing indexes: {e}")

        return suggestions

    async def get_table_stats(self) -> Dict[str, Any]:
        """Get table statistics"""
        stats_query = """
        SELECT
            schemaname,
            tablename,
            n_tup_ins as inserts,
            n_tup_upd as updates,
            n_tup_del as deletes,
            n_live_tup as live_tuples,
            n_dead_tup as dead_tuples
        FROM pg_stat_user_tables
        ORDER BY n_live_tup DESC
        """

        try:
            return await self.db_manager.execute_raw_query(stats_query)
        except Exception as e:
            logger.error(f"Failed to get table stats: {e}")
            return []


# Global database manager
db_manager = None


async def initialize_database(database_url: str):
    """Initialize global database manager"""
    global db_manager
    db_manager = DatabaseManager(database_url)
    await db_manager.initialize()
    await db_manager.create_tables()


async def get_database_session() -> Session:
    """Get database session"""
    if not db_manager:
        raise RuntimeError("Database not initialized")
    return db_manager.get_session()


if __name__ == "__main__":
    # Example usage
    async def main():
        # Initialize database
        database_url = "postgresql://user:password@localhost:5432/nexus"
        await initialize_database(database_url)

        # Get session and create some data
        session = get_database_session()

        try:
            # Create a user
            user = User(
                email="test@example.com",
                username="testuser",
                first_name="Test",
                last_name="User",
                password_hash="hashed_password",
                role=UserRole.USER,
            )
            session.add(user)
            session.commit()

            # Create user preferences
            preferences = UserPreference(
                user_id=user.id, theme="dark", language="en", currency="USD"
            )
            session.add(preferences)

            # Create an account
            account = Account(
                user_id=user.id,
                name="Checking Account",
                account_type=AccountType.CHECKING,
                balance=1000.0,
            )
            session.add(account)

            # Create a category
            category = Category(
                name="Food & Dining", description="Restaurants and food expenses"
            )
            session.add(category)

            # Create a transaction
            transaction = Transaction(
                user_id=user.id,
                account_id=account.id,
                category_id=category.id,
                amount=25.50,
                transaction_type=TransactionType.EXPENSE,
                description="Lunch at restaurant",
                transaction_date=datetime.now(timezone.utc),
            )
            session.add(transaction)

            session.commit()

            print("Sample data created successfully")

            # Analyze performance
            optimizer = SchemaOptimizer(db_manager)
            suggestions = await optimizer.optimize_indexes()
            print(f"Index optimization suggestions: {suggestions}")

        except Exception as e:
            session.rollback()
            print(f"Error: {e}")
        finally:
            session.close()
            await db_manager.close()

    asyncio.run(main())
