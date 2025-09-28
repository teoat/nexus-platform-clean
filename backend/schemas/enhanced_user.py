#!/usr/bin/env python3
"""
NEXUS Platform - Enhanced User Schemas V3.0
Pydantic models for user-related data with POV roles and OAuth support
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, validator


# Enhanced POV Role System
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
    """System User Roles"""

    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


# Enhanced User Schemas
class POVConfiguration(BaseModel):
    """POV Configuration for Users"""

    primary_role: POVRole
    secondary_roles: List[POVRole] = []
    analysis_mode: AnalysisMode = AnalysisMode.SINGLE_POV
    evidence_retention: str = "standard"  # standard, extended, maximum
    ai_intervention: AIInterventionLevel = AIInterventionLevel.ASSISTED


class OAuthAccount(BaseModel):
    """OAuth Account Information"""

    provider: OAuthProvider
    provider_id: str
    email: str
    name: str
    avatar_url: Optional[str] = None
    connected_at: datetime


class UserBase(BaseModel):
    """Base user schema"""

    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    pov_configuration: Optional[POVConfiguration] = None


class UserCreate(BaseModel):
    """User creation schema"""

    username: str
    email: EmailStr
    password: Optional[str] = None  # Optional for OAuth users
    full_name: Optional[str] = None
    pov_configuration: Optional[POVConfiguration] = None
    oauth_provider: Optional[OAuthProvider] = None


class UserUpdate(BaseModel):
    """User update schema"""

    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    pov_configuration: Optional[POVConfiguration] = None


class OAuthLoginRequest(BaseModel):
    """OAuth Login Request"""

    provider: OAuthProvider
    access_token: str
    id_token: Optional[str] = None


class POVSelectionRequest(BaseModel):
    """POV Selection Request"""

    primary_role: POVRole
    secondary_roles: List[POVRole] = []
    analysis_mode: AnalysisMode = AnalysisMode.SINGLE_POV
    ai_intervention: AIInterventionLevel = AIInterventionLevel.ASSISTED


class UserProfile(BaseModel):
    """Enhanced user profile schema"""

    full_name: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    professional_title: Optional[str] = None
    organization: Optional[str] = None
    pov_configuration: Optional[POVConfiguration] = None


class UserProfileUpdate(BaseModel):
    """User profile update schema"""

    full_name: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    professional_title: Optional[str] = None
    organization: Optional[str] = None
    pov_configuration: Optional[POVConfiguration] = None


class UserSettings(BaseModel):
    """Enhanced user settings schema"""

    theme: str = "dark"
    notifications_enabled: bool = True
    language: str = "en"
    timezone: str = "UTC"
    currency: str = "USD"
    date_format: str = "MM/DD/YYYY"
    ai_intervention_level: AIInterventionLevel = AIInterventionLevel.ASSISTED
    auto_reconciliation: bool = False
    fraud_detection_sensitivity: int = Field(50, ge=0, le=100)


class UserSettingsUpdate(BaseModel):
    """User settings update schema"""

    theme: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    date_format: Optional[str] = None
    ai_intervention_level: Optional[AIInterventionLevel] = None
    auto_reconciliation: Optional[bool] = None
    fraud_detection_sensitivity: Optional[int] = Field(None, ge=0, le=100)


class UserPreferences(BaseModel):
    """Enhanced user preferences schema"""

    currency: str = "USD"
    timezone: str = "UTC"
    data_retention_days: int = 365
    email_notifications: bool = True
    sms_notifications: bool = False
    push_notifications: bool = True
    auto_backup: bool = True
    backup_frequency: str = "daily"  # daily, weekly, monthly
    evidence_retention_policy: str = "standard"


class UserPreferencesUpdate(BaseModel):
    """User preferences update schema"""

    currency: Optional[str] = None
    timezone: Optional[str] = None
    data_retention_days: Optional[int] = None
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    auto_backup: Optional[bool] = None
    backup_frequency: Optional[str] = None
    evidence_retention_policy: Optional[str] = None


class UserResponse(BaseModel):
    """Enhanced user response schema"""

    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    role: UserRole
    pov_configuration: Optional[POVConfiguration] = None
    oauth_accounts: List[OAuthAccount] = []
    created_at: datetime
    updated_at: Optional[datetime] = None


class User(BaseModel):
    """Complete user schema"""

    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    role: UserRole
    pov_configuration: Optional[POVConfiguration] = None
    oauth_accounts: List[OAuthAccount] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Data Standardization Schemas
class DataStandardizationRule(BaseModel):
    """Data Standardization Rule"""

    id: str
    name: str
    description: str
    field: str
    transformation: str
    validation: str
    priority: int = 1


class DataQualityMetrics(BaseModel):
    """Data Quality Metrics"""

    completeness: float = Field(0.0, ge=0.0, le=100.0)
    accuracy: float = Field(0.0, ge=0.0, le=100.0)
    consistency: float = Field(0.0, ge=0.0, le=100.0)
    timeliness: float = Field(0.0, ge=0.0, le=100.0)
    validity: float = Field(0.0, ge=0.0, le=100.0)
    uniqueness: float = Field(0.0, ge=0.0, le=100.0)


class StandardizedData(BaseModel):
    """Standardized Data Format"""

    id: str
    source: str
    original_data: Dict[str, Any]
    standardized_data: Dict[str, Any]
    quality_metrics: DataQualityMetrics
    standardization_rules: List[str]
    processed_at: datetime


# Project-Trading Intersection Schemas
class ProjectMilestone(BaseModel):
    """Project Milestone"""

    id: str
    project_id: str
    name: str
    planned_amount: float
    actual_amount: Optional[float] = None
    release_date: datetime
    status: str = "pending"  # pending, released, delayed, cancelled


class TradingOperation(BaseModel):
    """Trading Operation"""

    id: str
    type: str  # income, expense
    amount: float
    description: str
    date: datetime
    category: str
    linked_milestone: Optional[str] = None


class ProjectTradingIntersection(BaseModel):
    """Project-Trading Intersection Data"""

    project_id: str
    milestone_id: str
    milestone: ProjectMilestone
    trading_operations: List[TradingOperation]
    allocation: Dict[str, float]
    intersection_analysis: Dict[str, Any]
    variance: float
    risk_level: str  # low, medium, high, critical
