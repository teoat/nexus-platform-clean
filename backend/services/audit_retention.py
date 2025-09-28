# NEXUS SSOT Audit Log Retention and Storage Service

"""
This module handles audit log retention, storage, and management for the SSOT system.
It ensures logs are retained for 7 years and stored securely.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List

from backend.database import get_db_session
from backend.models import AuditLog

logger = logging.getLogger(__name__)


class AuditRetentionManager:
    def __init__(self):
        self.db_session = get_db_session()
        self.retention_period = timedelta(days=7 * 365)  # 7 years

    def archive_old_logs(self) -> int:
        """
        Archive audit logs older than the retention period.

        Returns:
            int: Number of logs archived
        """
        try:
            cutoff_date = datetime.utcnow() - self.retention_period
            old_logs = (
                self.db_session.query(AuditLog)
                .filter(AuditLog.created_at < cutoff_date)
                .all()
            )

            archived_count = 0
            for log in old_logs:
                log.is_archived = True
                log.archived_at = datetime.utcnow()
                archived_count += 1

            self.db_session.commit()
            logger.info(f"Archived {archived_count} old audit logs")
            return archived_count
        except Exception as e:
            logger.error(f"Error archiving old logs: {str(e)}")
            self.db_session.rollback()
            return 0

    def store_audit_log(self, action: str, user: str, details: Dict) -> bool:
        """
        Store a new audit log entry.

        Args:
            action (str): The action performed
            user (str): The user who performed the action
            details (Dict): Additional details

        Returns:
            bool: True if stored successfully
        """
        try:
            audit_log = AuditLog(
                action=action,
                user=user,
                details=str(details),
                created_at=datetime.utcnow(),
            )
            self.db_session.add(audit_log)
            self.db_session.commit()
            logger.info(f"Stored audit log for action '{action}' by user '{user}'")
            return True
        except Exception as e:
            logger.error(f"Error storing audit log: {str(e)}")
            self.db_session.rollback()
            return False

    def get_audit_logs(
        self, start_date: datetime = None, end_date: datetime = None, limit: int = 100
    ) -> List[Dict]:
        """
        Retrieve audit logs within a date range.

        Args:
            start_date (datetime): Start date for query
            end_date (datetime): End date for query
            limit (int): Maximum number of logs to return

        Returns:
            List[Dict]: List of audit logs
        """
        try:
            query = self.db_session.query(AuditLog).filter(
                AuditLog.is_archived == False
            )

            if start_date:
                query = query.filter(AuditLog.created_at >= start_date)
            if end_date:
                query = query.filter(AuditLog.created_at <= end_date)

            logs = query.order_by(AuditLog.created_at.desc()).limit(limit).all()

            log_list = []
            for log in logs:
                log_list.append(
                    {
                        "id": log.id,
                        "action": log.action,
                        "user": log.user,
                        "details": log.details,
                        "created_at": log.created_at.isoformat(),
                        "is_archived": log.is_archived,
                    }
                )

            logger.info(f"Retrieved {len(log_list)} audit logs")
            return log_list
        except Exception as e:
            logger.error(f"Error retrieving audit logs: {str(e)}")
            return []

    def export_audit_logs(self, filename: str) -> bool:
        """
        Export audit logs to external storage.

        Args:
            filename (str): The filename for export

        Returns:
            bool: True if exported successfully
        """
        try:
            logs = self.get_audit_logs(limit=10000)  # Export up to 10k logs

            with open(filename, "w") as f:
                for log in logs:
                    f.write(
                        f"{log['created_at']}: {log['user']} - {log['action']} - {log['details']}\n"
                    )

            logger.info(f"Exported {len(logs)} audit logs to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error exporting audit logs: {str(e)}")
            return False

    def cleanup_archived_logs(self) -> int:
        """
        Permanently delete archived logs older than retention period.

        Returns:
            int: Number of logs deleted
        """
        try:
            cutoff_date = datetime.utcnow() - self.retention_period
            old_archived_logs = (
                self.db_session.query(AuditLog)
                .filter(
                    AuditLog.is_archived == True, AuditLog.archived_at < cutoff_date
                )
                .all()
            )

            deleted_count = 0
            for log in old_archived_logs:
                self.db_session.delete(log)
                deleted_count += 1

            self.db_session.commit()
            logger.info(f"Deleted {deleted_count} old archived audit logs")
            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up archived logs: {str(e)}")
            self.db_session.rollback()
            return 0

    def get_storage_usage(self) -> Dict:
        """
        Get storage usage statistics for audit logs.

        Returns:
            Dict: Storage usage stats
        """
        try:
            total_logs = self.db_session.query(AuditLog).count()
            archived_logs = (
                self.db_session.query(AuditLog)
                .filter(AuditLog.is_archived == True)
                .count()
            )
            active_logs = total_logs - archived_logs

            # Estimate storage size (assuming average log size of 1KB)
            estimated_size_mb = total_logs * 0.001

            stats = {
                "total_logs": total_logs,
                "active_logs": active_logs,
                "archived_logs": archived_logs,
                "estimated_size_mb": round(estimated_size_mb, 2),
            }

            logger.info(f"Audit log storage usage: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Error getting storage usage: {str(e)}")
            return {}


def main():
    manager = AuditRetentionManager()
    # Example usage
    manager.store_audit_log("CREATE_ALIAS", "admin", {"alias": "test"})
    logs = manager.get_audit_logs(limit=5)
    print(f"Recent logs: {logs}")

    usage = manager.get_storage_usage()
    print(f"Storage usage: {usage}")


if __name__ == "__main__":
    main()
