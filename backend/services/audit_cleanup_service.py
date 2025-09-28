#!/usr/bin/env python3
"""
NEXUS Platform - Audit Cleanup Service
Automated audit log retention and cleanup management
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

from .audit_logging import AuditLogQueryEngine

# Configure logging
logger = logging.getLogger(__name__)


class AuditCleanupService:
    """
    Service for managing audit log retention and automated cleanup
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.audit_engine = AuditLogQueryEngine()

        # Default retention policies
        self.retention_policies = {
            "debug": 7,      # 7 days
            "info": 90,      # 90 days
            "warning": 365,  # 1 year
            "error": 730,    # 2 years
            "critical": 2555, # 7 years (compliance requirement)
        }

        # Override with config
        if "retention_policies" in self.config:
            self.retention_policies.update(self.config["retention_policies"])

        # Cleanup schedule
        self.cleanup_interval_hours = self.config.get("cleanup_interval_hours", 24)  # Daily
        self.enabled = self.config.get("enabled", True)
        self.dry_run = self.config.get("dry_run", False)

        # Background task
        self.cleanup_task: Optional[asyncio.Task] = None

    async def start_cleanup_scheduler(self):
        """
        Start the automated cleanup scheduler
        """
        if not self.enabled:
            logger.info("Audit cleanup service is disabled")
            return

        logger.info(f"Starting audit cleanup scheduler (interval: {self.cleanup_interval_hours} hours)")

        async def cleanup_loop():
            while True:
                try:
                    await self.perform_cleanup()
                except Exception as e:
                    logger.error(f"Error during audit cleanup: {e}")

                # Wait for next cleanup
                await asyncio.sleep(self.cleanup_interval_hours * 3600)

        self.cleanup_task = asyncio.create_task(cleanup_loop())

    async def stop_cleanup_scheduler(self):
        """
        Stop the automated cleanup scheduler
        """
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("Audit cleanup scheduler stopped")

    async def perform_cleanup(self):
        """
        Perform audit log cleanup based on retention policies
        """
        if not self.enabled:
            return

        logger.info("Starting audit log cleanup")

        total_deleted = 0
        cleanup_summary = {}

        for log_level, retention_days in self.retention_policies.items():
            try:
                deleted_count = await self.cleanup_logs_by_level(log_level, retention_days)
                cleanup_summary[log_level] = deleted_count
                total_deleted += deleted_count

                logger.info(f"Cleaned up {deleted_count} {log_level} audit logs older than {retention_days} days")

            except Exception as e:
                logger.error(f"Error cleaning up {log_level} logs: {e}")

        # Log cleanup summary
        try:
            await self.audit_engine.log_operation(
                operation="system",
                entity_type="AuditCleanup",
                entity_id="cleanup_run",
                details={
                    "cleanup_summary": cleanup_summary,
                    "total_deleted": total_deleted,
                    "retention_policies": self.retention_policies,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                performed_by="cleanup_service",
                context="audit_maintenance",
                log_level="info",
            )
        except Exception as e:
            logger.error(f"Failed to log cleanup summary: {e}")

        logger.info(f"Audit cleanup completed. Total logs deleted: {total_deleted}")

        return {
            "total_deleted": total_deleted,
            "cleanup_summary": cleanup_summary,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def cleanup_logs_by_level(self, log_level: str, retention_days: int) -> int:
        """
        Clean up audit logs of a specific level older than retention period
        """
        # Calculate cutoff date
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)

        # Query logs to delete
        query = {
            "log_levels": [log_level],
            "end_date": cutoff_date,
        }

        # Get count of logs to be deleted
        try:
            logs_to_delete = await self.audit_engine.query_audit_logs(query)
            delete_count = len(logs_to_delete)

            if self.dry_run:
                logger.info(f"DRY RUN: Would delete {delete_count} {log_level} audit logs older than {retention_days} days")
                return 0

            if delete_count > 0:
                # Perform actual cleanup
                deleted_count = await self.audit_engine.cleanup_old_logs(retention_days)
                return deleted_count
            else:
                return 0

        except Exception as e:
            logger.error(f"Error during cleanup of {log_level} logs: {e}")
            return 0

    async def manual_cleanup(
        self,
        retention_days: int,
        log_levels: Optional[list] = None,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Perform manual cleanup with custom parameters
        """
        logger.info(f"Starting manual audit cleanup (retention: {retention_days} days, dry_run: {dry_run})")

        total_deleted = 0
        cleanup_summary = {}

        target_levels = log_levels or list(self.retention_policies.keys())

        for log_level in target_levels:
            try:
                deleted_count = await self.cleanup_logs_by_level(log_level, retention_days)
                cleanup_summary[log_level] = deleted_count
                total_deleted += deleted_count

            except Exception as e:
                logger.error(f"Error in manual cleanup of {log_level} logs: {e}")
                cleanup_summary[log_level] = 0

        result = {
            "total_deleted": total_deleted,
            "cleanup_summary": cleanup_summary,
            "retention_days": retention_days,
            "target_levels": target_levels,
            "dry_run": dry_run,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(f"Manual audit cleanup completed: {result}")
        return result

    def update_retention_policy(self, log_level: str, retention_days: int):
        """
        Update retention policy for a specific log level
        """
        self.retention_policies[log_level] = retention_days
        logger.info(f"Updated retention policy for {log_level}: {retention_days} days")

    def get_retention_policies(self) -> Dict[str, int]:
        """
        Get current retention policies
        """
        return self.retention_policies.copy()

    def set_cleanup_interval(self, hours: int):
        """
        Set the cleanup interval in hours
        """
        self.cleanup_interval_hours = hours
        logger.info(f"Updated cleanup interval to {hours} hours")

    def set_enabled(self, enabled: bool):
        """
        Enable or disable the cleanup service
        """
        self.enabled = enabled
        status = "enabled" if enabled else "disabled"
        logger.info(f"Audit cleanup service {status}")

    def set_dry_run(self, dry_run: bool):
        """
        Set dry run mode
        """
        self.dry_run = dry_run
        mode = "enabled" if dry_run else "disabled"
        logger.info(f"Audit cleanup dry run mode {mode}")

    async def get_cleanup_status(self) -> Dict[str, Any]:
        """
        Get the current status of the cleanup service
        """
        return {
            "enabled": self.enabled,
            "dry_run": self.dry_run,
            "cleanup_interval_hours": self.cleanup_interval_hours,
            "retention_policies": self.retention_policies,
            "scheduler_running": self.cleanup_task is not None and not self.cleanup_task.done(),
            "last_cleanup": getattr(self, '_last_cleanup', None),
        }

    async def archive_old_logs(
        self,
        archive_path: str,
        retention_days: int,
        log_levels: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Archive old logs instead of deleting them
        """
        logger.info(f"Starting audit log archiving to {archive_path}")

        # This would implement archiving logic
        # For now, just log the intent
        await self.audit_engine.log_operation(
            operation="system",
            entity_type="AuditArchive",
            entity_id="archive_operation",
            details={
                "archive_path": archive_path,
                "retention_days": retention_days,
                "log_levels": log_levels,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            performed_by="cleanup_service",
            context="audit_maintenance",
            log_level="info",
        )

        # TODO: Implement actual archiving logic
        return {
            "archived_count": 0,
            "archive_path": archive_path,
            "message": "Archiving not yet implemented",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Global audit cleanup service instance
audit_cleanup_service = AuditCleanupService()