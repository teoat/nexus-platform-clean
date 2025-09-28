#!/usr/bin/env python3
"""
NEXUS Platform - File System Audit Service
Audit logging for file system operations and configuration changes
"""

import asyncio
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Set

# Import audit logging
from .audit_logging import AuditLogQueryEngine, AuditLogLevel, OperationType

# Configure logging
logger = logging.getLogger(__name__)


class FileSystemAuditService:
    """
    Service for auditing file system operations and configuration changes
    """

    def __init__(self):
        self.audit_engine = AuditLogQueryEngine()
        self.enabled = True
        self.monitored_paths: Set[str] = set()
        self.sensitive_files = {
            ".env", ".env.local", ".env.production", ".env.staging",
            "secrets.json", "config/secrets.yaml", "ssl/", "keys/",
            "passwords.txt", "credentials.json", "private.key", "secret.key"
        }
        self.config_files = {
            ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg", ".conf",
            ".env", ".properties", "requirements.txt", "package.json",
            "docker-compose.yml", "Dockerfile"
        }

    async def log_file_operation(
        self,
        operation: str,
        file_path: str,
        performed_by: str = "system",
        context: str = "filesystem",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a file system operation
        """
        if not self.enabled:
            return

        try:
            file_path_obj = Path(file_path)
            file_info = self._get_file_info(file_path_obj)

            # Determine operation type
            if operation.upper() in ["CREATE", "WRITE", "COPY"]:
                op_type = OperationType.CREATE
            elif operation.upper() in ["UPDATE", "MODIFY", "EDIT"]:
                op_type = OperationType.UPDATE
            elif operation.upper() in ["DELETE", "REMOVE", "RM"]:
                op_type = OperationType.DELETE
            elif operation.upper() in ["READ", "ACCESS"]:
                op_type = OperationType.READ
            else:
                op_type = OperationType.SYSTEM

            # Determine log level based on file sensitivity
            log_level = AuditLogLevel.INFO
            if self._is_sensitive_file(file_path):
                log_level = AuditLogLevel.WARNING
            elif self._is_config_file(file_path):
                log_level = AuditLogLevel.INFO

            # Prepare audit details
            details = {
                "file_operation": operation.upper(),
                "file_path": str(file_path),
                "file_info": file_info,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            if metadata:
                details["metadata"] = metadata

            # Log the operation
            await self.audit_engine.log_operation(
                operation=op_type.value,
                entity_type="FileSystem",
                entity_id=file_path,
                details=details,
                performed_by=performed_by,
                context=context,
                log_level=log_level,
            )

        except Exception as e:
            logger.error(f"Failed to log file operation: {e}")

    async def log_config_change(
        self,
        config_file: str,
        change_type: str,
        old_value: Optional[Any] = None,
        new_value: Optional[Any] = None,
        performed_by: str = "system",
        context: str = "configuration"
    ):
        """
        Log a configuration change
        """
        if not self.enabled:
            return

        try:
            # Prepare audit details
            details = {
                "config_change_type": change_type,
                "config_file": config_file,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            if old_value is not None:
                details["old_value"] = self._sanitize_config_value(old_value)

            if new_value is not None:
                details["new_value"] = self._sanitize_config_value(new_value)

            # Log the configuration change
            await self.audit_engine.log_operation(
                operation=OperationType.UPDATE.value,
                entity_type="Configuration",
                entity_id=config_file,
                details=details,
                performed_by=performed_by,
                context=context,
                log_level=AuditLogLevel.WARNING,  # Config changes are important
            )

        except Exception as e:
            logger.error(f"Failed to log config change: {e}")

    async def log_directory_operation(
        self,
        operation: str,
        directory_path: str,
        performed_by: str = "system",
        context: str = "filesystem",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a directory operation
        """
        if not self.enabled:
            return

        try:
            dir_path_obj = Path(directory_path)
            dir_info = self._get_directory_info(dir_path_obj)

            # Determine operation type
            if operation.upper() in ["CREATE", "MKDIR"]:
                op_type = OperationType.CREATE
            elif operation.upper() in ["DELETE", "RMDIR", "REMOVE"]:
                op_type = OperationType.DELETE
            else:
                op_type = OperationType.SYSTEM

            # Prepare audit details
            details = {
                "directory_operation": operation.upper(),
                "directory_path": str(directory_path),
                "directory_info": dir_info,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            if metadata:
                details["metadata"] = metadata

            # Log the operation
            await self.audit_engine.log_operation(
                operation=op_type.value,
                entity_type="Directory",
                entity_id=directory_path,
                details=details,
                performed_by=performed_by,
                context=context,
                log_level=AuditLogLevel.INFO,
            )

        except Exception as e:
            logger.error(f"Failed to log directory operation: {e}")

    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Get information about a file
        """
        try:
            stat = file_path.stat()
            return {
                "exists": file_path.exists(),
                "size": stat.st_size if file_path.exists() else 0,
                "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat() if file_path.exists() else None,
                "permissions": oct(stat.st_mode)[-3:] if file_path.exists() else None,
                "extension": file_path.suffix,
                "is_sensitive": self._is_sensitive_file(str(file_path)),
                "is_config": self._is_config_file(str(file_path)),
            }
        except Exception as e:
            return {
                "exists": False,
                "error": str(e),
            }

    def _get_directory_info(self, dir_path: Path) -> Dict[str, Any]:
        """
        Get information about a directory
        """
        try:
            if not dir_path.exists():
                return {"exists": False}

            # Count files and subdirectories
            file_count = 0
            dir_count = 0
            total_size = 0

            for item in dir_path.rglob("*"):
                if item.is_file():
                    file_count += 1
                    try:
                        total_size += item.stat().st_size
                    except:
                        pass
                elif item.is_dir():
                    dir_count += 1

            stat = dir_path.stat()
            return {
                "exists": True,
                "file_count": file_count,
                "directory_count": dir_count,
                "total_size": total_size,
                "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                "permissions": oct(stat.st_mode)[-3:],
            }
        except Exception as e:
            return {
                "exists": False,
                "error": str(e),
            }

    def _is_sensitive_file(self, file_path: str) -> bool:
        """
        Check if a file contains sensitive information
        """
        file_path_lower = file_path.lower()
        return any(sensitive in file_path_lower for sensitive in self.sensitive_files)

    def _is_config_file(self, file_path: str) -> bool:
        """
        Check if a file is a configuration file
        """
        file_path_obj = Path(file_path)
        return file_path_obj.suffix.lower() in self.config_files or file_path_obj.name.lower() in {
            "requirements.txt", "package.json", "docker-compose.yml", "dockerfile",
            ".env", ".env.local", ".env.production", ".env.staging"
        }

    def _sanitize_config_value(self, value: Any) -> Any:
        """
        Sanitize configuration values for logging
        """
        if isinstance(value, dict):
            sanitized = {}
            sensitive_keys = {"password", "secret", "key", "token", "api_key", "database_url"}
            for k, v in value.items():
                if any(sensitive in k.lower() for sensitive in sensitive_keys):
                    sanitized[k] = "***MASKED***"
                else:
                    sanitized[k] = self._sanitize_config_value(v)
            return sanitized
        elif isinstance(value, str):
            # Mask potential secrets in strings
            if len(value) > 50 and any(indicator in value.lower() for indicator in ["password", "secret", "key", "token"]):
                return "***MASKED***"
            return value
        else:
            return value

    def add_monitored_path(self, path: str):
        """
        Add a path to be monitored for file operations
        """
        self.monitored_paths.add(path)

    def remove_monitored_path(self, path: str):
        """
        Remove a path from monitoring
        """
        self.monitored_paths.discard(path)

    def set_enabled(self, enabled: bool):
        """
        Enable or disable file system auditing
        """
        self.enabled = enabled

    async def scan_and_audit_changes(
        self,
        base_path: str,
        performed_by: str = "system",
        context: str = "filesystem_scan"
    ):
        """
        Scan a directory and audit any recent changes
        """
        if not self.enabled:
            return

        try:
            base_path_obj = Path(base_path)
            if not base_path_obj.exists():
                return

            # This is a simplified implementation
            # In a real system, you'd compare against a baseline
            change_count = 0
            for file_path in base_path_obj.rglob("*"):
                if file_path.is_file():
                    # Check if file was modified recently (last hour)
                    try:
                        stat = file_path.stat()
                        modified_time = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
                        if (datetime.now(timezone.utc) - modified_time).total_seconds() < 3600:  # 1 hour
                            await self.log_file_operation(
                                operation="MODIFY",
                                file_path=str(file_path),
                                performed_by=performed_by,
                                context=context,
                                metadata={"scan_detected": True}
                            )
                            change_count += 1
                    except Exception as e:
                        logger.debug(f"Error checking file {file_path}: {e}")

            if change_count > 0:
                logger.info(f"File system scan detected {change_count} recent changes in {base_path}")

        except Exception as e:
            logger.error(f"Error during file system scan: {e}")


# Global file system audit service instance
filesystem_audit_service = FileSystemAuditService()


# Utility functions for easy auditing
async def audit_file_create(file_path: str, performed_by: str = "system"):
    """Audit file creation"""
    await filesystem_audit_service.log_file_operation("CREATE", file_path, performed_by)


async def audit_file_modify(file_path: str, performed_by: str = "system"):
    """Audit file modification"""
    await filesystem_audit_service.log_file_operation("MODIFY", file_path, performed_by)


async def audit_file_delete(file_path: str, performed_by: str = "system"):
    """Audit file deletion"""
    await filesystem_audit_service.log_file_operation("DELETE", file_path, performed_by)


async def audit_config_change(config_file: str, change_type: str, old_value=None, new_value=None, performed_by: str = "system"):
    """Audit configuration change"""
    await filesystem_audit_service.log_config_change(config_file, change_type, old_value, new_value, performed_by)