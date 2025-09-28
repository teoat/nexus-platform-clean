#!/usr/bin/env python3
"""
NEXUS Platform - SSOT Audit Log Query and Reporting System
Advanced audit logging with query capabilities and comprehensive reporting
"""

import asyncio
import csv
import json
import logging
import re
import sqlite3
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuditLogLevel(Enum):
    """Audit log levels"""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class OperationType(Enum):
    """Types of operations that can be audited"""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    RESOLVE = "resolve"
    APPROVE = "approve"
    REJECT = "reject"
    DEPRECATE = "deprecate"
    EXPIRED = "expired"
    CONFLICT = "conflict"
    RESOLUTION = "resolution"
    SYSTEM = "system"


class ReportFormat(Enum):
    """Available report formats"""

    JSON = "json"
    CSV = "csv"
    HTML = "html"
    PDF = "pdf"
    EXCEL = "excel"


@dataclass
class AuditQuery:
    """Query parameters for audit log searches"""

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    operation_types: Optional[List[OperationType]] = None
    entity_types: Optional[List[str]] = None
    entity_ids: Optional[List[str]] = None
    performed_by: Optional[List[str]] = None
    contexts: Optional[List[str]] = None
    log_levels: Optional[List[AuditLogLevel]] = None
    search_text: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    sort_by: Optional[str] = "timestamp"
    sort_order: Optional[str] = "desc"


@dataclass
class AuditReport:
    """Audit report structure"""

    id: str
    title: str
    description: str
    generated_at: datetime
    generated_by: str
    query_params: AuditQuery
    total_records: int
    data: List[Dict[str, Any]]
    summary: Dict[str, Any]
    format: ReportFormat
    file_path: Optional[str] = None


class AuditLogQueryEngine:
    """
    Advanced audit log query engine with comprehensive reporting capabilities
    """

    def __init__(
        self, db_path: str = "data/audit_logs.db", config: Dict[str, Any] = None
    ):
        self.db_path = Path(db_path)
        self.config = config or {}
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

        # Query optimization settings
        self.enable_caching = self.config.get("enable_caching", True)
        self.cache_ttl = self.config.get("cache_ttl", 300)  # 5 minutes
        self.query_cache = {}

        # Report generation settings
        self.report_output_dir = Path(self.config.get("report_output_dir", "reports"))
        self.report_output_dir.mkdir(parents=True, exist_ok=True)

    def _init_database(self):
        """Initialize SQLite database for audit logs"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create audit_logs table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    details TEXT NOT NULL,
                    performed_by TEXT NOT NULL,
                    context TEXT NOT NULL,
                    log_level TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    session_id TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create indexes for better query performance
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_logs(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_operation ON audit_logs(operation)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_entity_type ON audit_logs(entity_type)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_entity_id ON audit_logs(entity_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_performed_by ON audit_logs(performed_by)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_context ON audit_logs(context)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_log_level ON audit_logs(log_level)"
            )

            # Create composite indexes for common queries
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_timestamp_operation ON audit_logs(timestamp, operation)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_entity_context ON audit_logs(entity_type, context)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_user_context ON audit_logs(performed_by, context)"
            )

            conn.commit()
            logger.info(f"Audit log database initialized at {self.db_path}")

    async def log_operation(
        self,
        operation: str,
        entity_type: str,
        entity_id: str,
        details: Dict[str, Any],
        performed_by: str,
        context: str = "system",
        log_level: AuditLogLevel = AuditLogLevel.INFO,
        ip_address: str = None,
        user_agent: str = None,
        session_id: str = None,
    ) -> int:
        """
        Log an operation to the audit database
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO audit_logs
                (timestamp, operation, entity_type, entity_id, details, performed_by,
                 context, log_level, ip_address, user_agent, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    operation,
                    entity_type,
                    entity_id,
                    json.dumps(details),
                    performed_by,
                    context,
                    log_level.value,
                    ip_address,
                    user_agent,
                    session_id,
                ),
            )
            log_id = cursor.lastrowid
            conn.commit()

        logger.debug(
            f"Logged operation {operation} for {entity_type}:{entity_id} by {performed_by}"
        )
        return log_id

    async def query_audit_logs(self, query: AuditQuery) -> List[Dict[str, Any]]:
        """
        Query audit logs with advanced filtering and pagination
        """
        # Build SQL query
        sql_parts = ["SELECT * FROM audit_logs WHERE 1=1"]
        params = []

        # Date range filtering
        if query.start_date:
            sql_parts.append("AND timestamp >= ?")
            params.append(query.start_date.isoformat())

        if query.end_date:
            sql_parts.append("AND timestamp <= ?")
            params.append(query.end_date.isoformat())

        # Operation type filtering
        if query.operation_types:
            placeholders = ",".join(["?" for _ in query.operation_types])
            sql_parts.append(f"AND operation IN ({placeholders})")
            params.extend([op.value for op in query.operation_types])

        # Entity type filtering
        if query.entity_types:
            placeholders = ",".join(["?" for _ in query.entity_types])
            sql_parts.append(f"AND entity_type IN ({placeholders})")
            params.extend(query.entity_types)

        # Entity ID filtering
        if query.entity_ids:
            placeholders = ",".join(["?" for _ in query.entity_ids])
            sql_parts.append(f"AND entity_id IN ({placeholders})")
            params.extend(query.entity_ids)

        # Performed by filtering
        if query.performed_by:
            placeholders = ",".join(["?" for _ in query.performed_by])
            sql_parts.append(f"AND performed_by IN ({placeholders})")
            params.extend(query.performed_by)

        # Context filtering
        if query.contexts:
            placeholders = ",".join(["?" for _ in query.contexts])
            sql_parts.append(f"AND context IN ({placeholders})")
            params.extend(query.contexts)

        # Log level filtering
        if query.log_levels:
            placeholders = ",".join(["?" for _ in query.log_levels])
            sql_parts.append(f"AND log_level IN ({placeholders})")
            params.extend([level.value for level in query.log_levels])

        # Text search
        if query.search_text:
            sql_parts.append(
                "AND (details LIKE ? OR entity_id LIKE ? OR context LIKE ?)"
            )
            search_pattern = f"%{query.search_text}%"
            params.extend([search_pattern, search_pattern, search_pattern])

        # Sorting
        sort_order = "DESC" if query.sort_order == "desc" else "ASC"
        sql_parts.append(f"ORDER BY {query.sort_by} {sort_order}")

        # Pagination
        if query.limit:
            sql_parts.append(f"LIMIT {query.limit}")
            if query.offset:
                sql_parts.append(f"OFFSET {query.offset}")

        # Execute query
        sql = " ".join(sql_parts)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()

            # Convert to list of dictionaries
            results = []
            for row in rows:
                result = dict(row)
                # Parse JSON details
                result["details"] = json.loads(result["details"])
                results.append(result)

            return results

    async def get_audit_statistics(self, query: AuditQuery = None) -> Dict[str, Any]:
        """
        Get comprehensive audit statistics
        """
        if query is None:
            query = AuditQuery()

        # Get basic counts
        basic_query = AuditQuery(
            start_date=query.start_date,
            end_date=query.end_date,
            contexts=query.contexts,
        )

        all_logs = await self.query_audit_logs(basic_query)

        # Calculate statistics
        total_operations = len(all_logs)

        # Operation type distribution
        operation_counts = defaultdict(int)
        for log in all_logs:
            operation_counts[log["operation"]] += 1

        # Entity type distribution
        entity_type_counts = defaultdict(int)
        for log in all_logs:
            entity_type_counts[log["entity_type"]] += 1

        # User activity
        user_activity = defaultdict(int)
        for log in all_logs:
            user_activity[log["performed_by"]] += 1

        # Context distribution
        context_counts = defaultdict(int)
        for log in all_logs:
            context_counts[log["context"]] += 1

        # Log level distribution
        log_level_counts = defaultdict(int)
        for log in all_logs:
            log_level_counts[log["log_level"]] += 1

        # Time-based analysis
        hourly_activity = defaultdict(int)
        daily_activity = defaultdict(int)

        for log in all_logs:
            timestamp = datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00"))
            hour_key = timestamp.strftime("%Y-%m-%d %H:00")
            day_key = timestamp.strftime("%Y-%m-%d")
            hourly_activity[hour_key] += 1
            daily_activity[day_key] += 1

        # Most active users
        most_active_users = sorted(
            user_activity.items(), key=lambda x: x[1], reverse=True
        )[:10]

        # Most common operations
        most_common_operations = sorted(
            operation_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]

        # Most modified entities
        entity_modification_counts = defaultdict(int)
        for log in all_logs:
            if log["operation"] in ["create", "update", "delete"]:
                entity_modification_counts[
                    f"{log['entity_type']}:{log['entity_id']}"
                ] += 1

        most_modified_entities = sorted(
            entity_modification_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]

        return {
            "total_operations": total_operations,
            "operation_distribution": dict(operation_counts),
            "entity_type_distribution": dict(entity_type_counts),
            "user_activity": dict(user_activity),
            "context_distribution": dict(context_counts),
            "log_level_distribution": dict(log_level_counts),
            "hourly_activity": dict(hourly_activity),
            "daily_activity": dict(daily_activity),
            "most_active_users": most_active_users,
            "most_common_operations": most_common_operations,
            "most_modified_entities": most_modified_entities,
            "query_period": {
                "start_date": query.start_date.isoformat()
                if query.start_date
                else None,
                "end_date": query.end_date.isoformat() if query.end_date else None,
            },
        }

    async def generate_report(
        self,
        query: AuditQuery,
        title: str,
        description: str,
        format: ReportFormat,
        generated_by: str = "system",
    ) -> AuditReport:
        """
        Generate a comprehensive audit report
        """
        # Query audit logs
        logs = await self.query_audit_logs(query)

        # Get statistics
        stats = await self.get_audit_statistics(query)

        # Create report
        report_id = f"audit_report_{int(datetime.now().timestamp())}"
        report = AuditReport(
            id=report_id,
            title=title,
            description=description,
            generated_at=datetime.now(timezone.utc),
            generated_by=generated_by,
            query_params=query,
            total_records=len(logs),
            data=logs,
            summary=stats,
            format=format,
        )

        # Generate file based on format
        if format == ReportFormat.JSON:
            report.file_path = await self._generate_json_report(report)
        elif format == ReportFormat.CSV:
            report.file_path = await self._generate_csv_report(report)
        elif format == ReportFormat.HTML:
            report.file_path = await self._generate_html_report(report)
        elif format == ReportFormat.EXCEL:
            report.file_path = await self._generate_excel_report(report)

        return report

    async def _generate_json_report(self, report: AuditReport) -> str:
        """Generate JSON report"""
        file_path = self.report_output_dir / f"{report.id}.json"

        report_data = {
            "report_metadata": {
                "id": report.id,
                "title": report.title,
                "description": report.description,
                "generated_at": report.generated_at.isoformat(),
                "generated_by": report.generated_by,
                "total_records": report.total_records,
            },
            "query_parameters": asdict(report.query_params),
            "summary": report.summary,
            "data": report.data,
        }

        with open(file_path, "w") as f:
            json.dump(report_data, f, indent=2, default=str)

        return str(file_path)

    async def _generate_csv_report(self, report: AuditReport) -> str:
        """Generate CSV report"""
        file_path = self.report_output_dir / f"{report.id}.csv"

        if not report.data:
            # Create empty CSV with headers
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "timestamp",
                        "operation",
                        "entity_type",
                        "entity_id",
                        "performed_by",
                        "context",
                        "log_level",
                        "details",
                    ]
                )
            return str(file_path)

        # Flatten data for CSV
        flattened_data = []
        for log in report.data:
            flat_log = {
                "timestamp": log["timestamp"],
                "operation": log["operation"],
                "entity_type": log["entity_type"],
                "entity_id": log["entity_id"],
                "performed_by": log["performed_by"],
                "context": log["context"],
                "log_level": log["log_level"],
                "details": json.dumps(log["details"]),
            }
            flattened_data.append(flat_log)

        # Write CSV
        with open(file_path, "w", newline="") as f:
            if flattened_data:
                writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys())
                writer.writeheader()
                writer.writerows(flattened_data)

        return str(file_path)

    async def _generate_html_report(self, report: AuditReport) -> str:
        """Generate HTML report"""
        file_path = self.report_output_dir / f"{report.id}.html"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{report.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .summary {{ background-color: #e8f4f8; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                .data-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .data-table th, .data-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .data-table th {{ background-color: #f2f2f2; }}
                .stats {{ display: flex; flex-wrap: wrap; gap: 20px; }}
                .stat-box {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; min-width: 200px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{report.title}</h1>
                <p>{report.description}</p>
                <p><strong>Generated:</strong> {report.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                <p><strong>Generated by:</strong> {report.generated_by}</p>
                <p><strong>Total Records:</strong> {report.total_records}</p>
            </div>

            <div class="summary">
                <h2>Summary Statistics</h2>
                <div class="stats">
                    <div class="stat-box">
                        <h3>Total Operations</h3>
                        <p>{report.summary.get('total_operations', 0)}</p>
                    </div>
                    <div class="stat-box">
                        <h3>Most Active User</h3>
                        <p>{report.summary.get('most_active_users', [['N/A', 0]])[0][0] if report.summary.get('most_active_users') else 'N/A'}</p>
                    </div>
                    <div class="stat-box">
                        <h3>Most Common Operation</h3>
                        <p>{report.summary.get('most_common_operations', [['N/A', 0]])[0][0] if report.summary.get('most_common_operations') else 'N/A'}</p>
                    </div>
                </div>
            </div>

            <h2>Audit Log Data</h2>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Operation</th>
                        <th>Entity Type</th>
                        <th>Entity ID</th>
                        <th>Performed By</th>
                        <th>Context</th>
                        <th>Log Level</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
        """

        for log in report.data[:100]:  # Limit to first 100 records for HTML
            html_content += f"""
                    <tr>
                        <td>{log['timestamp']}</td>
                        <td>{log['operation']}</td>
                        <td>{log['entity_type']}</td>
                        <td>{log['entity_id']}</td>
                        <td>{log['performed_by']}</td>
                        <td>{log['context']}</td>
                        <td>{log['log_level']}</td>
                        <td>{json.dumps(log['details'], indent=2)}</td>
                    </tr>
            """

        html_content += """
                </tbody>
            </table>
        </body>
        </html>
        """

        with open(file_path, "w") as f:
            f.write(html_content)

        return str(file_path)

    async def _generate_excel_report(self, report: AuditReport) -> str:
        """Generate Excel report using pandas"""
        try:
            import pandas as pd
        except ImportError:
            logger.error("pandas not available for Excel report generation")
            return await self._generate_csv_report(report)

        file_path = self.report_output_dir / f"{report.id}.xlsx"

        # Create DataFrame
        df = pd.DataFrame(report.data)

        # Flatten details column
        if "details" in df.columns:
            df["details"] = df["details"].apply(
                lambda x: json.dumps(x) if isinstance(x, dict) else str(x)
            )

        # Write to Excel with multiple sheets
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            # Main data sheet
            df.to_excel(writer, sheet_name="Audit Logs", index=False)

            # Summary sheet
            summary_data = []
            for key, value in report.summary.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        summary_data.append(
                            {"Category": key, "Item": sub_key, "Value": sub_value}
                        )
                else:
                    summary_data.append(
                        {"Category": "General", "Item": key, "Value": value}
                    )

            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name="Summary", index=False)

        return str(file_path)

    async def cleanup_old_logs(self, retention_days: int = 365):
        """
        Clean up audit logs older than specified retention period
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM audit_logs WHERE timestamp < ?", (cutoff_date.isoformat(),)
            )
            deleted_count = cursor.rowcount
            conn.commit()

        logger.info(
            f"Cleaned up {deleted_count} audit logs older than {retention_days} days"
        )
        return deleted_count

    async def export_audit_logs(
        self,
        query: AuditQuery,
        output_path: str,
        format: ReportFormat = ReportFormat.JSON,
    ):
        """
        Export audit logs to a file
        """
        logs = await self.query_audit_logs(query)

        if format == ReportFormat.JSON:
            with open(output_path, "w") as f:
                json.dump(logs, f, indent=2, default=str)
        elif format == ReportFormat.CSV:
            with open(output_path, "w", newline="") as f:
                if logs:
                    writer = csv.DictWriter(f, fieldnames=logs[0].keys())
                    writer.writeheader()
                    writer.writerows(logs)
        else:
            raise ValueError(f"Unsupported export format: {format}")

        logger.info(f"Exported {len(logs)} audit logs to {output_path}")
        return len(logs)


# Example usage and testing
async def main():
    """
    Example usage of AuditLogQueryEngine
    """
    # Initialize query engine
    query_engine = AuditLogQueryEngine()

    # Log some sample operations
    await query_engine.log_operation(
        operation="create",
        entity_type="SSOTAnchor",
        entity_id="user_profile",
        details={"description": "User profile anchor created"},
        performed_by="admin",
        context="user_management",
    )

    await query_engine.log_operation(
        operation="add_alias",
        entity_type="AliasDefinition",
        entity_id="user_profile_alias",
        details={"alias": "profile", "canonical": "user_profile"},
        performed_by="admin",
        context="user_management",
    )

    # Query audit logs
    query = AuditQuery(
        start_date=datetime.now(timezone.utc) - timedelta(days=1),
        operation_types=[OperationType.CREATE, OperationType.UPDATE],
        limit=10,
    )

    logs = await query_engine.query_audit_logs(query)
    print(f"Found {len(logs)} audit log entries")

    # Get statistics
    stats = await query_engine.get_audit_statistics()
    print(f"Audit statistics: {stats}")

    # Generate report
    report = await query_engine.generate_report(
        query=query,
        title="Daily Audit Report",
        description="Audit log report for the last 24 hours",
        format=ReportFormat.HTML,
    )
    print(f"Generated report: {report.file_path}")


if __name__ == "__main__":
    asyncio.run(main())
