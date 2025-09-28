#!/usr/bin/env python3
"""
NEXUS Platform - Settings Configuration
Centralized settings management for all services
"""

import os
from typing import Optional

try:
    from pydantic import BaseSettings
except ImportError:
    from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Database settings
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql://user:password@localhost:5432/nexus"
    )
    database_pool_size: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))
    database_max_overflow: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))

    # Redis settings
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    redis_password: Optional[str] = os.getenv("REDIS_PASSWORD")

    # API settings
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_debug: bool = os.getenv("API_DEBUG", "false").lower() == "true"

    # Security settings
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiration: int = int(os.getenv("JWT_EXPIRATION", "3600"))

    # External service URLs
    ml_service_url: str = os.getenv("ML_SERVICE_URL", "http://localhost:8001")
    ai_service_url: str = os.getenv("AI_SERVICE_URL", "http://localhost:8002")

    # Workflow settings
    workflow_max_execution_time: int = int(
        os.getenv("WORKFLOW_MAX_EXECUTION_TIME", "3600")
    )
    workflow_max_parallel_nodes: int = int(
        os.getenv("WORKFLOW_MAX_PARALLEL_NODES", "10")
    )

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra environment variables


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings
