#!/usr/bin/env python3
"""
NEXUS Platform - Database Audit Service
Audit logging for database operations and data modifications
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

# Import audit logging
from .audit_logging import AuditLogQueryEngine, AuditLogLevel, OperationType

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseAuditService:
    """
    Service for auditing database operations and data modifications
    """

    def __init__(self):
        self.audit_engine = AuditLogQueryEngine()
        self.enabled = True
        self.audit_tables = {
            "users", "user_profiles", "user_settings", "user_preferences",
            "ssot_anchors", "ssot_aliases", "audit_logs",
            "financial_accounts", "financial_transactions",
            "ai_models", "ai_predictions", "ai_training_data"
        }

    async def log_database_operation(
        self,
        operation: str,
        table_name: str,
        record_id: Any,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        performed_by: str = "system",
        context: str = "database",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a database operation
        """
        if not self.enabled or table_name not in self.audit_tables:
            return

        try:
            # Determine operation type
            if operation.upper() == "INSERT":
                op_type = OperationType.CREATE
            elif operation.upper() == "UPDATE":
                op_type = OperationType.UPDATE
            elif operation.upper() == "DELETE":
                op_type = OperationType.DELETE
            else:
                op_type = OperationType.SYSTEM

            # Prepare audit details
            details = {
                "database_operation": operation.upper(),
                "table_name": table_name,
                "record_id": str(record_id) if record_id is not None else None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            if old_values:
                # Sanitize sensitive data
                details["old_values"] = self._sanitize_database_values(old_values)

            if new_values:
                # Sanitize sensitive data
                details["new_values"] = self._sanitize_database_values(new_values)

            if metadata:
                details["metadata"] = metadata

            # Determine log level based on operation and data
            log_level = AuditLogLevel.INFO
            if operation.upper() == "DELETE":
                log_level = AuditLogLevel.WARNING
            elif self._contains_sensitive_data(table_name, new_values or old_values or {}):
                log_level = AuditLogLevel.WARNING

            # Log the operation
            await self.audit_engine.log_operation(
                operation=op_type.value,
                entity_type=f"DatabaseTable:{table_name}",
                entity_id=str(record_id) if record_id is not None else f"{table_name}_operation",
                details=details,
                performed_by=performed_by,
                context=context,
                log_level=log_level,
            )

        except Exception as e:
            logger.error(f"Failed to log database operation: {e}")

    def _sanitize_database_values(self, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize sensitive data from database values
        """
        sensitive_fields = {
            "password", "hashed_password", "password_hash",
            "secret", "token", "api_key", "apikey", "access_token", "refresh_token",
            "credit_card", "card_number", "cvv", "ssn", "social_security",
            "private_key", "secret_key", "encryption_key"
        }

        sanitized = {}
        for key, value in values.items():
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                sanitized[key] = "***MASKED***"
            else:
                # Truncate large values
                if isinstance(value, str) and len(value) > 500:
                    sanitized[key] = value[:500] + "..."
                else:
                    sanitized[key] = value

        return sanitized

    def _contains_sensitive_data(self, table_name: str, values: Dict[str, Any]) -> bool:
        """
        Check if the values contain sensitive data
        """
        sensitive_tables = {"users", "user_settings", "ai_models"}
        sensitive_fields = {
            "password", "email", "phone", "address", "ssn",
            "credit_card", "api_key", "token", "secret"
        }

        if table_name in sensitive_tables:
            return True

        return any(
            any(sensitive in key.lower() for sensitive in sensitive_fields)
            for key in values.keys()
        )

    def enable_audit_for_table(self, table_name: str):
        """
        Enable audit logging for a specific table
        """
        self.audit_tables.add(table_name)

    def disable_audit_for_table(self, table_name: str):
        """
        Disable audit logging for a specific table
        """
        self.audit_tables.discard(table_name)

    def set_audit_enabled(self, enabled: bool):
        """
        Enable or disable audit logging globally
        """
        self.enabled = enabled

    async def log_bulk_operation(
        self,
        operation: str,
        table_name: str,
        record_count: int,
        performed_by: str = "system",
        context: str = "database",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a bulk database operation
        """
        if not self.enabled or table_name not in self.audit_tables:
            return

        try:
            details = {
                "bulk_operation": operation.upper(),
                "table_name": table_name,
                "record_count": record_count,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            if metadata:
                details["metadata"] = metadata

            await self.audit_engine.log_operation(
                operation=OperationType.SYSTEM.value,
                entity_type=f"DatabaseTable:{table_name}",
                entity_id=f"bulk_{operation}_{int(datetime.now().timestamp())}",
                details=details,
                performed_by=performed_by,
                context=context,
                log_level=AuditLogLevel.INFO,
            )

        except Exception as e:
            logger.error(f"Failed to log bulk database operation: {e}")


# Global database audit service instance
database_audit_service = DatabaseAuditService()


def setup_database_audit_hooks(engine: Engine):
    """
    Setup SQLAlchemy event hooks for database auditing
    """

    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """Hook called before SQL execution"""
        # Store query information in connection info
        conn.info['audit_query'] = {
            'statement': statement,
            'parameters': parameters,
            'executemany': executemany,
            'timestamp': datetime.now(timezone.utc),
        }

    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """Hook called after SQL execution"""
        try:
            # Get query information
            query_info = conn.info.get('audit_query')
            if not query_info:
                return

            # Parse the SQL statement to determine operation type
            sql_upper = statement.upper().strip()

            if sql_upper.startswith(('INSERT', 'REPLACE')):
                operation = 'INSERT'
            elif sql_upper.startswith('UPDATE'):
                operation = 'UPDATE'
            elif sql_upper.startswith('DELETE'):
                operation = 'DELETE'
            elif sql_upper.startswith('SELECT'):
                # Skip SELECT operations for audit logging
                return
            else:
                operation = 'OTHER'

            # Extract table name (simplified parsing)
            table_name = _extract_table_name(statement)
            if not table_name:
                return

            # Log the operation asynchronously
            audit_data = {
                'operation': operation,
                'table_name': table_name,
                'statement': statement[:500] if len(statement) > 500 else statement,
                'parameters': str(parameters)[:500] if parameters else None,
                'executemany': executemany,
                'rowcount': cursor.rowcount,
                'timestamp': query_info['timestamp'].isoformat(),
            }

            # Schedule async audit logging
            asyncio.create_task(
                database_audit_service.log_database_operation(
                    operation=operation,
                    table_name=table_name,
                    record_id=None,  # Not available at this level
                    performed_by="database_engine",
                    context="sql_execution",
                    metadata=audit_data
                )
            )

        except Exception as e:
            logger.error(f"Error in database audit hook: {e}")


def _extract_table_name(sql: str) -> Optional[str]:
    """
    Extract table name from SQL statement (simplified)
    """
    import re

    # Simple regex patterns for common SQL operations
    patterns = [
        r'INSERT\s+INTO\s+(\w+)',
        r'UPDATE\s+(\w+)',
        r'DELETE\s+FROM\s+(\w+)',
        r'FROM\s+(\w+)',
        r'INTO\s+(\w+)',
    ]

    sql_upper = sql.upper()
    for pattern in patterns:
        match = re.search(pattern, sql_upper)
        if match:
            return match.group(1).lower()

    return None


# SQLAlchemy event listeners for ORM operations
@event.listens_for(Session, "before_flush")
def before_flush(session, flush_context, instances):
    """Hook called before session flush"""
    try:
        # Store original state for comparison
        for obj in session.new:
            session.info[f'audit_new_{id(obj)}'] = None  # New object

        for obj in session.dirty:
            session.info[f'audit_dirty_{id(obj)}'] = _get_object_state(obj)

        for obj in session.deleted:
            session.info[f'audit_deleted_{id(obj)}'] = _get_object_state(obj)

    except Exception as e:
        logger.error(f"Error in before_flush audit hook: {e}")


@event.listens_for(Session, "after_flush")
def after_flush(session, flush_context):
    """Hook called after session flush"""
    try:
        # Log changes
        for obj in session.new:
            key = f'audit_new_{id(obj)}'
            if key in session.info:
                asyncio.create_task(
                    database_audit_service.log_database_operation(
                        operation='INSERT',
                        table_name=obj.__tablename__,
                        record_id=getattr(obj, 'id', None),
                        new_values=_get_object_state(obj),
                        performed_by="orm_session",
                        context="orm_operation"
                    )
                )
                del session.info[key]

        for obj in session.dirty:
            key = f'audit_dirty_{id(obj)}'
            if key in session.info:
                old_values = session.info[key]
                new_values = _get_object_state(obj)
                asyncio.create_task(
                    database_audit_service.log_database_operation(
                        operation='UPDATE',
                        table_name=obj.__tablename__,
                        record_id=getattr(obj, 'id', None),
                        old_values=old_values,
                        new_values=new_values,
                        performed_by="orm_session",
                        context="orm_operation"
                    )
                )
                del session.info[key]

        for obj in session.deleted:
            key = f'audit_deleted_{id(obj)}'
            if key in session.info:
                old_values = session.info[key]
                asyncio.create_task(
                    database_audit_service.log_database_operation(
                        operation='DELETE',
                        table_name=obj.__tablename__,
                        record_id=getattr(obj, 'id', None),
                        old_values=old_values,
                        performed_by="orm_session",
                        context="orm_operation"
                    )
                )
                del session.info[key]

    except Exception as e:
        logger.error(f"Error in after_flush audit hook: {e}")


def _get_object_state(obj) -> Dict[str, Any]:
    """
    Get the current state of a SQLAlchemy object
    """
    try:
        state = {}
        for column in obj.__table__.columns:
            value = getattr(obj, column.name, None)
            if value is not None:
                state[column.name] = value
        return state
    except Exception as e:
        logger.error(f"Error getting object state: {e}")
        return {}