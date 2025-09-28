#!/usr/bin/env python3
"""
NEXUS Platform - Enhanced Database Models V3.0
SQLAlchemy models with POV roles, OAuth, data standardization, and Frenly AI
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, Index
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String as UUIDString
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .schema_normalization import Base
# Define User model
class User(Base):
    """User model"""
    __tablename__ = "users"
    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_username", "username"),
        Index("idx_users_role_active", "role", "is_active"),
        Index("idx_users_created_at", "created_at"),
        {'extend_existing': True}
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    role = Column(String(50), default="user", nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Additional fields
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    avatar_url = Column(String(500))
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="en")
    
    # Indexes are defined in the main __table_args__ above


# Define Frenly AI enums directly to avoid circular imports
class FrenlyAITaskType(str, Enum):
    """Frenly AI Task Types"""
    SYSTEM_MAINTENANCE = "system_maintenance"
    DATA_RECONCILIATION = "data_reconciliation"
    FRAUD_DETECTION = "fraud_detection"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    SECURITY_AUDIT = "security_audit"
    DATA_CLEANUP = "data_cleanup"
    BACKUP_MANAGEMENT = "backup_management"
    USER_ASSISTANCE = "user_assistance"
    REPORT_GENERATION = "report_generation"
    COMPLIANCE_CHECK = "compliance_check"


class FrenlyAIActionType(str, Enum):
    """Frenly AI Action Types"""
    ANALYZE = "analyze"
    OPTIMIZE = "optimize"
    CLEAN = "clean"
    BACKUP = "backup"
    MONITOR = "monitor"
    ALERT = "alert"
    REPORT = "report"
    FIX = "fix"
    PREVENT = "prevent"
    LEARN = "learn"


class FrenlyAIStatus(str, Enum):
    """Frenly AI Status"""
    IDLE = "idle"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class FrenlyAIPriority(str, Enum):
    """Frenly AI Priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FrenlyAIConfidence(str, Enum):
    """Frenly AI Confidence"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


# Enhanced Enums
class POVRole(str, Enum):
    """Point of View Roles for Financial Examination"""

    FINANCIAL_EXAMINER = "financial_examiner"
    PROSECUTOR = "prosecutor"
    JUDGE = "judge"
    EXECUTIVE = "executive"
    COMPLIANCE_OFFICER = "compliance_officer"
    AUDITOR = "auditor"
    FORENSIC_ANALYST = "forensic_analyst"
    RISK_MANAGER = "risk_manager"


class AnalysisMode(str, Enum):
    """Analysis Mode for POV Selection"""

    SINGLE_POV = "single_pov"
    MULTI_POV = "multi_pov"
    ALL_POV = "all_pov"
    CUSTOM_POV = "custom_pov"


class AIInterventionLevel(str, Enum):
    """AI Intervention Levels"""

    USER_GUIDED = "user_guided"
    ASSISTED = "assisted"
    FULL_AI = "full_ai"
    CUSTOM = "custom"


class OAuthProvider(str, Enum):
    """OAuth Provider Types"""

    GOOGLE = "google"
    MICROSOFT = "microsoft"
    LINKEDIN = "linkedin"
    GITHUB = "github"


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"


class AccountType(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT = "credit"
    INVESTMENT = "investment"
    LOAN = "loan"
    OTHER = "other"


class NotificationType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    SYSTEM = "system"


class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"






    #
    # # Note: User model is now defined in schema_normalization.py with POV support
    #     accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    #     transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    #     categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    #     budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    #     notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    #     files = relationship("File", back_populates="user", cascade="all, delete-orphan")
    #     profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    #     settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    #     preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    #     oauth_accounts = relationship("OAuthAccount", back_populates="user", cascade="all, delete-orphan")
    #     frenly_ai_config = relationship("FrenlyAIConfiguration", back_populates="user", uselist=False, cascade="all, delete-orphan")
    # projects = relationship(
    #     "Project", back_populates="user", cascade="all, delete-orphan"
    # )


# Enhanced User Profile
class UserProfile(Base):
    """Enhanced user profile model"""

    __tablename__ = "user_profiles"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    bio = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    date_of_birth = Column(DateTime(timezone=True), nullable=True)
    professional_title = Column(String(255), nullable=True)
    organization = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    # user = relationship("User", back_populates="user_preferences")


# Enhanced User Settings
class UserSettings(Base):
    """Enhanced user settings model"""

    __tablename__ = "user_settings"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    theme = Column(String(50), default="dark", nullable=False)
    notifications_enabled = Column(Boolean, default=True, nullable=False)
    language = Column(String(10), default="en", nullable=False)
    timezone = Column(String(50), default="UTC", nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    date_format = Column(String(20), default="MM/DD/YYYY", nullable=False)
    ai_intervention_level = Column(
        SQLEnum(AIInterventionLevel), default=AIInterventionLevel.ASSISTED
    )
    auto_reconciliation = Column(Boolean, default=False, nullable=False)
    fraud_detection_sensitivity = Column(Integer, default=50, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    # user = relationship("User", back_populates="settings")


# Enhanced User Preferences
class UserPreferences(Base):
    """Enhanced user preferences model"""

    __tablename__ = "user_preferences"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    currency = Column(String(10), default="USD", nullable=False)
    timezone = Column(String(50), default="UTC", nullable=False)
    data_retention_days = Column(Integer, default=365, nullable=False)
    email_notifications = Column(Boolean, default=True, nullable=False)
    sms_notifications = Column(Boolean, default=False, nullable=False)
    push_notifications = Column(Boolean, default=True, nullable=False)
    auto_backup = Column(Boolean, default=True, nullable=False)
    backup_frequency = Column(String(20), default="daily", nullable=False)
    evidence_retention_policy = Column(String(50), default="standard", nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    # user = relationship("User", back_populates="preferences")


# OAuth Account Model
class OAuthAccount(Base):
    """OAuth Account model"""

    __tablename__ = "oauth_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider = Column(SQLEnum(OAuthProvider), nullable=False)
    provider_id = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    connected_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    # user = relationship("User", back_populates="oauth_accounts")


# Data Standardization Models
class DataStandardizationRule(Base):
    """Data Standardization Rule model"""

    __tablename__ = "data_standardization_rules"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    field = Column(String(100), nullable=False)
    transformation = Column(Text, nullable=False)  # JSON string
    validation = Column(Text, nullable=False)  # JSON string
    priority = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class DataQualityMetrics(Base):
    """Data Quality Metrics model"""

    __tablename__ = "data_quality_metrics"

    id = Column(Integer, primary_key=True, index=True)
    data_source = Column(String(100), nullable=False, index=True)
    completeness = Column(Numeric(5, 2), default=0.0, nullable=False)
    accuracy = Column(Numeric(5, 2), default=0.0, nullable=False)
    consistency = Column(Numeric(5, 2), default=0.0, nullable=False)
    timeliness = Column(Numeric(5, 2), default=0.0, nullable=False)
    validity = Column(Numeric(5, 2), default=0.0, nullable=False)
    uniqueness = Column(Numeric(5, 2), default=0.0, nullable=False)
    overall_score = Column(Numeric(5, 2), default=0.0, nullable=False)
    measured_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# Project-Trading Intersection Models
class Project(Base):
    """Project model"""

    __tablename__ = "projects"

    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active", nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    total_budget = Column(Numeric(15, 2), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    # user = relationship("User", back_populates="projects")
    # milestones = relationship(
    #     "ProjectMilestone", back_populates="project", cascade="all, delete-orphan"
    # )


class ProjectMilestone(Base):
    """Project Milestone model"""

    __tablename__ = "project_milestones"

    id = Column(String(50), primary_key=True, index=True)
    project_id = Column(
        String(50),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    planned_amount = Column(Numeric(15, 2), nullable=False)
    actual_amount = Column(Numeric(15, 2), nullable=True)
    release_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), default="pending", nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    # project = relationship("Project", back_populates="milestones")
    # trading_operations = relationship("TradingOperation", back_populates="milestone")


class TradingOperation(Base):
    """Trading Operation model"""

    __tablename__ = "trading_operations"

    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    milestone_id = Column(
        String(50),
        ForeignKey("project_milestones.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    type = Column(String(50), nullable=False)  # income, expense
    amount = Column(Numeric(15, 2), nullable=False)
    description = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    linked_milestone = Column(String(50), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    # user = relationship("User")
    # milestone = relationship("ProjectMilestone", back_populates="trading_operations")


# Frenly AI Models
class FrenlyAIConfiguration(Base):
    """Frenly AI Configuration model"""

    __tablename__ = "frenly_ai_configurations"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    ai_level = Column(String(50), default="assisted", nullable=False)
    auto_approve_threshold = Column(Numeric(3, 2), default=0.8, nullable=False)
    learning_enabled = Column(Boolean, default=True, nullable=False)
    audit_mode = Column(Boolean, default=False, nullable=False)
    allowed_actions = Column(JSON, nullable=True)
    restricted_actions = Column(JSON, nullable=True)
    system_maintenance_enabled = Column(Boolean, default=True, nullable=False)
    data_reconciliation_enabled = Column(Boolean, default=True, nullable=False)
    fraud_detection_enabled = Column(Boolean, default=True, nullable=False)
    performance_optimization_enabled = Column(Boolean, default=True, nullable=False)
    security_audit_enabled = Column(Boolean, default=True, nullable=False)
    user_assistance_enabled = Column(Boolean, default=True, nullable=False)
    compliance_check_enabled = Column(Boolean, default=True, nullable=False)
    max_concurrent_tasks = Column(Integer, default=5, nullable=False)
    response_timeout = Column(Integer, default=300, nullable=False)
    learning_rate = Column(Numeric(3, 2), default=0.1, nullable=False)
    memory_retention_days = Column(Integer, default=30, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    # user = relationship("User", back_populates="frenly_ai_config")


class FrenlyAITask(Base):
    """Frenly AI Task model"""

    __tablename__ = "frenly_ai_tasks"

    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type = Column(SQLEnum(FrenlyAITaskType), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(
        SQLEnum(FrenlyAIPriority), default=FrenlyAIPriority.MEDIUM, nullable=False
    )
    status = Column(
        SQLEnum(FrenlyAIStatus), default=FrenlyAIStatus.IDLE, nullable=False
    )
    assigned_to = Column(String(100), nullable=True)
    parameters = Column(JSON, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    confidence = Column(
        SQLEnum(FrenlyAIConfidence), default=FrenlyAIConfidence.MEDIUM, nullable=False
    )
    requires_approval = Column(Boolean, default=False, nullable=False)
    estimated_duration = Column(Integer, nullable=True)
    progress = Column(Integer, default=0, nullable=False)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    # user = relationship("User")
    # responses = relationship(
    #     "FrenlyAIResponse", back_populates="task", cascade="all, delete-orphan"
    # )


class FrenlyAIResponse(Base):
    """Frenly AI Response model"""

    __tablename__ = "frenly_ai_responses"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(
        String(50),
        ForeignKey("frenly_ai_tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    response_type = Column(SQLEnum(FrenlyAIActionType), nullable=False)
    content = Column(Text, nullable=False)
    confidence = Column(
        SQLEnum(FrenlyAIConfidence), default=FrenlyAIConfidence.MEDIUM, nullable=False
    )
    actions = Column(JSON, nullable=True)
    requires_approval = Column(Boolean, default=False, nullable=False)
    reasoning = Column(Text, nullable=True)
    evidence = Column(JSON, nullable=True)
    alternatives = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    # task = relationship("FrenlyAITask", back_populates="responses")


class FrenlyAIMemory(Base):
    """Frenly AI Memory model"""

    __tablename__ = "frenly_ai_memories"

    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    context = Column(Text, nullable=False)
    action_taken = Column(String(255), nullable=False)
    outcome = Column(Text, nullable=False)
    user_feedback = Column(Text, nullable=True)
    confidence = Column(
        SQLEnum(FrenlyAIConfidence), default=FrenlyAIConfidence.MEDIUM, nullable=False
    )
    learned_pattern = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_accessed = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    # user = relationship("User")


class FrenlyAIConversation(Base):
    """Frenly AI Conversation model"""

    __tablename__ = "frenly_ai_conversations"

    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    messages = Column(JSON, nullable=True)
    context = Column(JSON, nullable=True)
    status = Column(String(20), default="active", nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    # user = relationship("User")


class FrenlyAITool(Base):
    """Frenly AI Tool model"""

    __tablename__ = "frenly_ai_tools"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)
    permissions = Column(JSON, nullable=True)
    parameters = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    usage_count = Column(Integer, default=0, nullable=False)
    last_used = Column(DateTime(timezone=True), nullable=True)
    success_rate = Column(Numeric(3, 2), default=0.0, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class FrenlyAIAuditLog(Base):
    """Frenly AI Audit Log model"""

    __tablename__ = "frenly_ai_audit_logs"

    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(String(50), nullable=True, index=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    confidence = Column(
        SQLEnum(FrenlyAIConfidence), default=FrenlyAIConfidence.MEDIUM, nullable=False
    )
    reasoning = Column(Text, nullable=True)
    evidence = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    compliance_standard = Column(String(100), nullable=True)
    court_evidence_quality = Column(String(50), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Relationships
    # user = relationship("User")


# Note: Core models (User, Account, Transaction, etc.) are defined in schema_normalization.py
