#!/usr/bin/env python3
"""
NEXUS Platform - Frenly AI Schemas V3.0
Pydantic models for Frenly AI operations and capabilities
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


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

    SUGGEST = "suggest"
    EXECUTE_SAFE = "execute_safe"
    EXECUTE_WITH_APPROVAL = "execute_with_approval"
    MONITOR = "monitor"
    ALERT = "alert"
    LEARN = "learn"


class FrenlyAIStatus(str, Enum):
    """Frenly AI Status"""

    IDLE = "idle"
    THINKING = "thinking"
    WORKING = "working"
    WAITING_APPROVAL = "waiting_approval"
    LEARNING = "learning"
    ERROR = "error"


class FrenlyAIPriority(str, Enum):
    """Frenly AI Priority Levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class FrenlyAIConfidence(str, Enum):
    """Frenly AI Confidence Levels"""

    LOW = "low"  # 0-40%
    MEDIUM = "medium"  # 40-70%
    HIGH = "high"  # 70-90%
    VERY_HIGH = "very_high"  # 90-100%


class FrenlyAITask(BaseModel):
    """Frenly AI Task"""

    id: str
    type: FrenlyAITaskType
    title: str
    description: str
    priority: FrenlyAIPriority = FrenlyAIPriority.MEDIUM
    status: FrenlyAIStatus = FrenlyAIStatus.IDLE
    assigned_to: Optional[str] = None
    created_at: datetime
    due_date: Optional[datetime] = None
    parameters: Dict[str, Any] = {}
    confidence: FrenlyAIConfidence = FrenlyAIConfidence.MEDIUM
    requires_approval: bool = False
    estimated_duration: Optional[int] = None  # minutes
    progress: int = Field(0, ge=0, le=100)
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class FrenlyAIResponse(BaseModel):
    """Frenly AI Response"""

    task_id: str
    response_type: FrenlyAIActionType
    content: str
    confidence: FrenlyAIConfidence
    actions: List[Dict[str, Any]] = []
    requires_approval: bool = False
    reasoning: str = ""
    evidence: List[str] = []
    alternatives: List[Dict[str, Any]] = []
    created_at: datetime
    expires_at: Optional[datetime] = None


class FrenlyAIConfiguration(BaseModel):
    """Frenly AI Configuration"""

    user_id: int
    ai_level: str = "assisted"  # user_guided, assisted, full_ai, custom
    auto_approve_threshold: float = Field(0.8, ge=0.0, le=1.0)
    learning_enabled: bool = True
    audit_mode: bool = False
    allowed_actions: List[FrenlyAIActionType] = [
        FrenlyAIActionType.SUGGEST,
        FrenlyAIActionType.MONITOR,
        FrenlyAIActionType.ALERT,
    ]
    restricted_actions: List[FrenlyAIActionType] = [
        FrenlyAIActionType.EXECUTE_SAFE,
        FrenlyAIActionType.EXECUTE_WITH_APPROVAL,
    ]
    system_maintenance_enabled: bool = True
    data_reconciliation_enabled: bool = True
    fraud_detection_enabled: bool = True
    performance_optimization_enabled: bool = True
    security_audit_enabled: bool = True
    user_assistance_enabled: bool = True
    compliance_check_enabled: bool = True
    max_concurrent_tasks: int = 5
    response_timeout: int = 300  # seconds
    learning_rate: float = Field(0.1, ge=0.0, le=1.0)
    memory_retention_days: int = 30


class FrenlyAIMemory(BaseModel):
    """Frenly AI Memory for Learning"""

    id: str
    user_id: int
    context: str
    action_taken: str
    outcome: str
    user_feedback: Optional[str] = None
    confidence: FrenlyAIConfidence
    learned_pattern: Optional[Dict[str, Any]] = None
    created_at: datetime
    last_accessed: datetime


class FrenlyAIConversation(BaseModel):
    """Frenly AI Conversation"""

    id: str
    user_id: int
    messages: List[Dict[str, Any]] = []
    context: Dict[str, Any] = {}
    status: str = "active"  # active, paused, completed
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None


class FrenlyAISystemStatus(BaseModel):
    """Frenly AI System Status"""

    status: FrenlyAIStatus
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    learning_mode: bool
    system_health: str  # excellent, good, fair, poor, critical
    last_activity: datetime
    uptime: int  # seconds
    memory_usage: float  # percentage
    cpu_usage: float  # percentage
    available_tools: List[str] = []
    recent_actions: List[Dict[str, Any]] = []


class FrenlyAITool(BaseModel):
    """Frenly AI Tool"""

    id: str
    name: str
    description: str
    category: str
    permissions: List[str] = []
    parameters: Dict[str, Any] = {}
    is_active: bool = True
    usage_count: int = 0
    last_used: Optional[datetime] = None
    success_rate: float = Field(0.0, ge=0.0, le=1.0)


class FrenlyAIAuditLog(BaseModel):
    """Frenly AI Audit Log"""

    id: str
    user_id: int
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    confidence: FrenlyAIConfidence
    reasoning: str
    evidence: List[str] = []
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    compliance_standard: Optional[str] = None
    court_evidence_quality: Optional[str] = None
