"""
NEXUS Platform - Centralized Constants
This file contains all application constants in a single location.
"""


# Environment Types
class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


# Database Constants
class DatabaseConstants:
    CONNECTION_TIMEOUT = 30
    POOL_SIZE_MIN = 5
    POOL_SIZE_MAX = 20
    RETRY_ATTEMPTS = 3
    RETRY_DELAY = 1.0


# API Constants
class APIConstants:
    TIMEOUT = 30
    RATE_LIMIT = 1000
    MAX_REQUESTS_PER_MINUTE = 1000
    DEFAULT_PORT = 8000


# Security Constants
class SecurityConstants:
    JWT_EXPIRY_HOURS = 24
    PASSWORD_MIN_LENGTH = 12
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30


# Performance Constants
class PerformanceConstants:
    ENABLE_PROFILING = False
    PROFILE_INTERVAL = 60.0
    MEMORY_OPTIMIZATION = True
    CPU_OPTIMIZATION = True


# Monitoring Constants
class MonitoringConstants:
    INTERVAL = 3.0
    METRICS_HISTORY_SIZE = 1000
    ALERT_THRESHOLDS = {"cpu_high": 90.0, "memory_high": 85.0, "error_rate_high": 20.0}


# Logging Constants
class LoggingConstants:
    LEVELS = {
        "DEBUG": "DEBUG",
        "INFO": "INFO",
        "WARNING": "WARNING",
        "ERROR": "ERROR",
        "CRITICAL": "CRITICAL",
    }
    MAX_SIZE = "10MB"
    BACKUP_COUNT = 5


# File Management Constants
class FileConstants:
    BATCH_SIZE = 100
    UPDATE_INTERVAL = 1.0
    BACKUP_ENABLED = True
    BACKUP_INTERVAL = 300


# Worker Constants
class WorkerConstants:
    MIN_WORKERS = 6
    MAX_WORKERS = 20
    TARGET_CPU = 75.0
    SCALING = {
        "cpu_threshold_low": 60.0,
        "cpu_threshold_high": 85.0,
        "memory_threshold": 80.0,
        "scale_up_delay": 5.0,
        "scale_down_delay": 10.0,
    }


# Worker Specialization Constants
WORKER_SPECIALIZATIONS = {
    "database": {"count": 3, "priority": "high", "success_rate": 0.95},
    "api": {"count": 4, "priority": "high", "success_rate": 0.90},
    "frontend": {"count": 3, "priority": "medium", "success_rate": 0.92},
    "testing": {"count": 3, "priority": "medium", "success_rate": 0.88},
    "monitoring": {"count": 2, "priority": "high", "success_rate": 0.97},
    "general": {"count": 5, "priority": "low", "success_rate": 0.90},
}


# Task Processing Constants
class ProcessingConstants:
    CYCLE_DURATION = 2.0
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    COMPLEXITY_ANALYSIS = True
    SUBTASK_BREAKDOWN = True


# Feature Flags
class FeatureFlags:
    INTELLIGENT_SCALING = True
    TASK_PRIORITIZATION = True
    ERROR_RECOVERY = True
    HEALTH_MONITORING = True
    METRICS_COLLECTION = True
    ALERTING = True
    WEB_INTERFACE = False
    API_ENDPOINTS = False


# Default Configuration Template
DEFAULT_CONFIG = {
    "system": {"name": "NEXUS Platform", "version": "1.0.0"},
    "database": {
        "connection_timeout": DatabaseConstants.CONNECTION_TIMEOUT,
        "pool_size_min": DatabaseConstants.POOL_SIZE_MIN,
        "pool_size_max": DatabaseConstants.POOL_SIZE_MAX,
        "retry_attempts": DatabaseConstants.RETRY_ATTEMPTS,
        "retry_delay": DatabaseConstants.RETRY_DELAY,
    },
    "api": {
        "timeout": APIConstants.TIMEOUT,
        "rate_limit": APIConstants.RATE_LIMIT,
        "max_requests_per_minute": APIConstants.MAX_REQUESTS_PER_MINUTE,
        "port": APIConstants.DEFAULT_PORT,
    },
    "security": {
        "jwt_expiry_hours": SecurityConstants.JWT_EXPIRY_HOURS,
        "password_min_length": SecurityConstants.PASSWORD_MIN_LENGTH,
        "max_login_attempts": SecurityConstants.MAX_LOGIN_ATTEMPTS,
        "lockout_duration_minutes": SecurityConstants.LOCKOUT_DURATION_MINUTES,
    },
    "performance": {
        "enable_profiling": PerformanceConstants.ENABLE_PROFILING,
        "profile_interval": PerformanceConstants.PROFILE_INTERVAL,
        "memory_optimization": PerformanceConstants.MEMORY_OPTIMIZATION,
        "cpu_optimization": PerformanceConstants.CPU_OPTIMIZATION,
    },
    "monitoring": {
        "interval": MonitoringConstants.INTERVAL,
        "metrics_history_size": MonitoringConstants.METRICS_HISTORY_SIZE,
        "alert_thresholds": MonitoringConstants.ALERT_THRESHOLDS,
    },
    "logging": {
        "level": LoggingConstants.LEVELS["INFO"],
        "max_size": LoggingConstants.MAX_SIZE,
        "backup_count": LoggingConstants.BACKUP_COUNT,
    },
    "file_management": {
        "batch_size": FileConstants.BATCH_SIZE,
        "update_interval": FileConstants.UPDATE_INTERVAL,
        "backup_enabled": FileConstants.BACKUP_ENABLED,
        "backup_interval": FileConstants.BACKUP_INTERVAL,
    },
    "workers": {
        "min_workers": WorkerConstants.MIN_WORKERS,
        "max_workers": WorkerConstants.MAX_WORKERS,
        "target_cpu": WorkerConstants.TARGET_CPU,
        "scaling": WorkerConstants.SCALING,
    },
    "worker_types": WORKER_SPECIALIZATIONS,
    "processing": {
        "cycle_duration": ProcessingConstants.CYCLE_DURATION,
        "max_retries": ProcessingConstants.MAX_RETRIES,
        "retry_delay": ProcessingConstants.RETRY_DELAY,
        "complexity_analysis": ProcessingConstants.COMPLEXITY_ANALYSIS,
        "subtask_breakdown": ProcessingConstants.SUBTASK_BREAKDOWN,
    },
    "features": {
        "intelligent_scaling": FeatureFlags.INTELLIGENT_SCALING,
        "task_prioritization": FeatureFlags.TASK_PRIORITIZATION,
        "error_recovery": FeatureFlags.ERROR_RECOVERY,
        "health_monitoring": FeatureFlags.HEALTH_MONITORING,
        "metrics_collection": FeatureFlags.METRICS_COLLECTION,
        "alerting": FeatureFlags.ALERTING,
        "web_interface": FeatureFlags.WEB_INTERFACE,
        "api_endpoints": FeatureFlags.API_ENDPOINTS,
    },
}
