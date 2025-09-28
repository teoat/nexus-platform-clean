"""
System Service - Basic implementation
"""

from datetime import datetime

from schemas.system import HealthCheckResponse, SystemStatus, SystemVersion


class SystemService:
    def get_system_status(self):
        return SystemStatus(
            status="healthy",
            timestamp=datetime.utcnow(),
            version="3.0.0",
            environment="staging",
        )

    def get_system_version(self):
        return SystemVersion(
            version="3.0.0", build_date=datetime.utcnow(), commit_hash="staging"
        )

    def health_check(self):
        return HealthCheckResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            services={"database": "unknown", "redis": "unknown", "api": "healthy"},
            version="3.0.0",
        )


# Create service instance
system_service = SystemService()
