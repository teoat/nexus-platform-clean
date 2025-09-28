#!/usr/bin/env python3
"""
NEXUS Platform - SSOT Audit Log Query and Reporting
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ReportType(Enum):
    OPERATION_SUMMARY = "operation_summary"
    USER_ACTIVITY = "user_activity"
    SYSTEM_CHANGES = "system_changes"
    SECURITY_EVENTS = "security_events"
    PERFORMANCE_METRICS = "performance_metrics"


class TimeRange(Enum):
    LAST_HOUR = "last_hour"
    LAST_DAY = "last_day"
    LAST_WEEK = "last_week"
    LAST_MONTH = "last_month"
    CUSTOM = "custom"


@dataclass
class AuditQuery:
    query_id: str
    report_type: ReportType
    time_range: TimeRange
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    filters: Dict[str, Any]
    requester: str
    created_at: datetime


@dataclass
class AuditReport:
    report_id: str
    query_id: str
    report_type: ReportType
    generated_at: datetime
    data: Dict[str, Any]
    summary: Dict[str, Any]
    metadata: Dict[str, Any]


class AuditReporter:
    """SSOT Audit Log Query and Reporting System"""

    def __init__(self, audit_log_path: str = "logs/audit.log"):
        self.audit_log_path = audit_log_path
        self.audit_entries: List[Dict[str, Any]] = []
        self.reports: Dict[str, AuditReport] = {}

    async def load_audit_logs(self):
        """Load audit logs from file"""
        try:
            with open(self.audit_log_path, "r") as f:
                for line in f:
                    if line.strip():
                        try:
                            entry = json.loads(line.strip())
                            self.audit_entries.append(entry)
                        except json.JSONDecodeError:
                            continue
        except FileNotFoundError:
            logger.warning(f"Audit log file not found: {self.audit_log_path}")
        except Exception as e:
            logger.error(f"Error loading audit logs: {e}")

    async def generate_report(self, query: AuditQuery) -> AuditReport:
        """Generate audit report based on query"""
        try:
            # Filter audit entries based on query
            filtered_entries = await self._filter_entries(query)

            # Generate report data based on type
            if query.report_type == ReportType.OPERATION_SUMMARY:
                data = await self._generate_operation_summary(filtered_entries)
            elif query.report_type == ReportType.USER_ACTIVITY:
                data = await self._generate_user_activity_report(filtered_entries)
            elif query.report_type == ReportType.SYSTEM_CHANGES:
                data = await self._generate_system_changes_report(filtered_entries)
            elif query.report_type == ReportType.SECURITY_EVENTS:
                data = await self._generate_security_events_report(filtered_entries)
            elif query.report_type == ReportType.PERFORMANCE_METRICS:
                data = await self._generate_performance_metrics_report(filtered_entries)
            else:
                data = {"error": "Unknown report type"}

            # Generate summary
            summary = await self._generate_summary(data, query)

            # Create report
            report = AuditReport(
                report_id=f"report_{len(self.reports) + 1}",
                query_id=query.query_id,
                report_type=query.report_type,
                generated_at=datetime.now(timezone.utc),
                data=data,
                summary=summary,
                metadata={
                    "total_entries": len(filtered_entries),
                    "time_range": query.time_range.value,
                    "filters_applied": query.filters,
                },
            )

            self.reports[report.report_id] = report
            return report

        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise

    async def _filter_entries(self, query: AuditQuery) -> List[Dict[str, Any]]:
        """Filter audit entries based on query criteria"""
        filtered = []

        # Determine time range
        if query.time_range == TimeRange.LAST_HOUR:
            start_time = datetime.now(timezone.utc) - timedelta(hours=1)
        elif query.time_range == TimeRange.LAST_DAY:
            start_time = datetime.now(timezone.utc) - timedelta(days=1)
        elif query.time_range == TimeRange.LAST_WEEK:
            start_time = datetime.now(timezone.utc) - timedelta(weeks=1)
        elif query.time_range == TimeRange.LAST_MONTH:
            start_time = datetime.now(timezone.utc) - timedelta(days=30)
        elif query.time_range == TimeRange.CUSTOM:
            start_time = query.start_time or datetime.now(timezone.utc) - timedelta(
                days=1
            )
        else:
            start_time = datetime.now(timezone.utc) - timedelta(days=1)

        end_time = query.end_time or datetime.now(timezone.utc)

        for entry in self.audit_entries:
            # Check time range
            entry_time = self._parse_timestamp(entry.get("timestamp", ""))
            if entry_time and start_time <= entry_time <= end_time:
                # Apply additional filters
                if await self._matches_filters(entry, query.filters):
                    filtered.append(entry)

        return filtered

    async def _generate_operation_summary(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate operation summary report"""
        operations = {}
        users = {}
        errors = 0

        for entry in entries:
            operation = entry.get("operation", "unknown")
            user = entry.get("requester", "unknown")
            success = entry.get("success", True)

            if operation not in operations:
                operations[operation] = {"total": 0, "success": 0, "errors": 0}

            operations[operation]["total"] += 1
            if success:
                operations[operation]["success"] += 1
            else:
                operations[operation]["errors"] += 1
                errors += 1

            if user not in users:
                users[user] = 0
            users[user] += 1

        return {
            "total_operations": len(entries),
            "total_errors": errors,
            "success_rate": (len(entries) - errors) / len(entries) if entries else 0,
            "operations": operations,
            "top_users": sorted(users.items(), key=lambda x: x[1], reverse=True)[:10],
        }

    async def _generate_user_activity_report(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate user activity report"""
        user_activity = {}

        for entry in entries:
            user = entry.get("requester", "unknown")
            operation = entry.get("operation", "unknown")
            timestamp = self._parse_timestamp(entry.get("timestamp", ""))

            if user not in user_activity:
                user_activity[user] = {
                    "total_operations": 0,
                    "operations": {},
                    "first_seen": timestamp,
                    "last_seen": timestamp,
                }

            user_activity[user]["total_operations"] += 1

            if operation not in user_activity[user]["operations"]:
                user_activity[user]["operations"][operation] = 0
            user_activity[user]["operations"][operation] += 1

            if timestamp:
                if (
                    user_activity[user]["first_seen"] is None
                    or timestamp < user_activity[user]["first_seen"]
                ):
                    user_activity[user]["first_seen"] = timestamp
                if (
                    user_activity[user]["last_seen"] is None
                    or timestamp > user_activity[user]["last_seen"]
                ):
                    user_activity[user]["last_seen"] = timestamp

        return {"total_users": len(user_activity), "user_activity": user_activity}

    async def _generate_system_changes_report(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate system changes report"""
        changes = []

        for entry in entries:
            if entry.get("operation") in [
                "create_alias",
                "update_alias",
                "delete_alias",
                "create_anchor",
                "update_anchor",
            ]:
                changes.append(
                    {
                        "timestamp": entry.get("timestamp"),
                        "operation": entry.get("operation"),
                        "user": entry.get("requester"),
                        "details": entry.get("data", {}),
                    }
                )

        return {"total_changes": len(changes), "changes": changes}

    async def _generate_security_events_report(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate security events report"""
        security_events = []

        for entry in entries:
            if entry.get("operation") in [
                "unauthorized_access",
                "failed_authentication",
                "suspicious_activity",
            ]:
                security_events.append(
                    {
                        "timestamp": entry.get("timestamp"),
                        "event_type": entry.get("operation"),
                        "user": entry.get("requester"),
                        "details": entry.get("data", {}),
                    }
                )

        return {
            "total_security_events": len(security_events),
            "events": security_events,
        }

    async def _generate_performance_metrics_report(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate performance metrics report"""
        metrics = {"response_times": [], "operation_counts": {}, "error_rates": {}}

        for entry in entries:
            operation = entry.get("operation", "unknown")
            processing_time = entry.get("processing_time", 0)
            success = entry.get("success", True)

            if processing_time:
                metrics["response_times"].append(processing_time)

            if operation not in metrics["operation_counts"]:
                metrics["operation_counts"][operation] = {"total": 0, "errors": 0}

            metrics["operation_counts"][operation]["total"] += 1
            if not success:
                metrics["operation_counts"][operation]["errors"] += 1

        # Calculate averages
        if metrics["response_times"]:
            metrics["avg_response_time"] = sum(metrics["response_times"]) / len(
                metrics["response_times"]
            )
            metrics["max_response_time"] = max(metrics["response_times"])
            metrics["min_response_time"] = min(metrics["response_times"])

        # Calculate error rates
        for operation, counts in metrics["operation_counts"].items():
            if counts["total"] > 0:
                metrics["error_rates"][operation] = counts["errors"] / counts["total"]

        return metrics

    async def _generate_summary(
        self, data: Dict[str, Any], query: AuditQuery
    ) -> Dict[str, Any]:
        """Generate report summary"""
        return {
            "report_type": query.report_type.value,
            "time_range": query.time_range.value,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "key_metrics": {
                "total_entries": data.get("total_operations", 0),
                "success_rate": data.get("success_rate", 0),
                "error_count": data.get("total_errors", 0),
            },
        }

    async def _matches_filters(
        self, entry: Dict[str, Any], filters: Dict[str, Any]
    ) -> bool:
        """Check if entry matches filters"""
        for key, value in filters.items():
            if key not in entry or entry[key] != value:
                return False
        return True

    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp string to datetime"""
        try:
            if timestamp_str.endswith("Z"):
                timestamp_str = timestamp_str[:-1] + "+00:00"
            return datetime.fromisoformat(timestamp_str)
        except:
            return None

    async def export_report(self, report_id: str, format: str = "json") -> str:
        """Export report in specified format"""
        if report_id not in self.reports:
            raise ValueError(f"Report {report_id} not found")

        report = self.reports[report_id]

        if format == "json":
            return json.dumps(asdict(report), indent=2, default=str)
        elif format == "csv":
            return await self._export_csv(report)
        else:
            raise ValueError(f"Unsupported format: {format}")

    async def _export_csv(self, report: AuditReport) -> str:
        """Export report as CSV"""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Write headers
        writer.writerow(["Report ID", "Type", "Generated At", "Total Entries"])
        writer.writerow(
            [
                report.report_id,
                report.report_type.value,
                report.generated_at.isoformat(),
                report.metadata.get("total_entries", 0),
            ]
        )

        return output.getvalue()


# Example usage
async def main():
    reporter = AuditReporter()
    await reporter.load_audit_logs()

    # Create query
    query = AuditQuery(
        query_id="q1",
        report_type=ReportType.OPERATION_SUMMARY,
        time_range=TimeRange.LAST_DAY,
        start_time=None,
        end_time=None,
        filters={},
        requester="admin",
        created_at=datetime.now(timezone.utc),
    )

    # Generate report
    report = await reporter.generate_report(query)
    print(f"Generated report: {report.report_id}")
    print(f"Summary: {report.summary}")


if __name__ == "__main__":
    asyncio.run(main())
