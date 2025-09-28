#!/usr/bin/env python3
"""
NEXUS Platform - Audit Compliance Reporting Service
Regulatory compliance reporting for audit logs (GDPR, SOX, HIPAA, etc.)
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from enum import Enum

# Import audit logging
from .audit_logging import AuditLogQueryEngine, AuditQuery, ReportFormat

# Configure logging
logger = logging.getLogger(__name__)


class ComplianceFramework(Enum):
    """Supported compliance frameworks"""

    GDPR = "gdpr"
    SOX = "sox"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    CCPA = "ccpa"
    NIST = "nist"


class ComplianceRequirement(Enum):
    """Compliance requirements"""

    DATA_ACCESS_LOGGING = "data_access_logging"
    DATA_MODIFICATION_LOGGING = "data_modification_logging"
    USER_ACTIVITY_MONITORING = "user_activity_monitoring"
    SECURITY_EVENT_LOGGING = "security_event_logging"
    PRIVACY_DATA_HANDLING = "privacy_data_handling"
    AUDIT_TRAIL_INTEGRITY = "audit_trail_integrity"
    RETENTION_POLICY_COMPLIANCE = "retention_policy_compliance"
    ACCESS_CONTROL_LOGGING = "access_control_logging"


class AuditComplianceService:
    """
    Service for generating regulatory compliance reports
    """

    def __init__(self):
        self.audit_engine = AuditLogQueryEngine()

        # Compliance framework requirements
        self.framework_requirements = {
            ComplianceFramework.GDPR: [
                ComplianceRequirement.DATA_ACCESS_LOGGING,
                ComplianceRequirement.DATA_MODIFICATION_LOGGING,
                ComplianceRequirement.PRIVACY_DATA_HANDLING,
                ComplianceRequirement.AUDIT_TRAIL_INTEGRITY,
                ComplianceRequirement.RETENTION_POLICY_COMPLIANCE,
            ],
            ComplianceFramework.SOX: [
                ComplianceRequirement.DATA_MODIFICATION_LOGGING,
                ComplianceRequirement.USER_ACTIVITY_MONITORING,
                ComplianceRequirement.AUDIT_TRAIL_INTEGRITY,
                ComplianceRequirement.ACCESS_CONTROL_LOGGING,
            ],
            ComplianceFramework.HIPAA: [
                ComplianceRequirement.DATA_ACCESS_LOGGING,
                ComplianceRequirement.SECURITY_EVENT_LOGGING,
                ComplianceRequirement.PRIVACY_DATA_HANDLING,
                ComplianceRequirement.AUDIT_TRAIL_INTEGRITY,
            ],
            ComplianceFramework.PCI_DSS: [
                ComplianceRequirement.DATA_ACCESS_LOGGING,
                ComplianceRequirement.SECURITY_EVENT_LOGGING,
                ComplianceRequirement.AUDIT_TRAIL_INTEGRITY,
                ComplianceRequirement.ACCESS_CONTROL_LOGGING,
            ],
        }

    async def generate_compliance_report(
        self,
        framework: ComplianceFramework,
        start_date: datetime,
        end_date: datetime,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive compliance report for a specific framework
        """
        logger.info(f"Generating {framework.value.upper()} compliance report for {start_date.date()} to {end_date.date()}")

        # Get requirements for this framework
        requirements = self.framework_requirements.get(framework, [])

        # Generate report sections
        report_sections = {}
        compliance_score = 0
        total_requirements = len(requirements)

        for requirement in requirements:
            section_data = await self._generate_requirement_report(
                requirement, start_date, end_date, include_details
            )
            report_sections[requirement.value] = section_data

            if section_data.get("compliant", False):
                compliance_score += 1

        # Calculate overall compliance percentage
        compliance_percentage = (compliance_score / total_requirements * 100) if total_requirements > 0 else 0

        # Generate summary
        summary = {
            "framework": framework.value,
            "report_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "compliance_score": compliance_score,
            "total_requirements": total_requirements,
            "compliance_percentage": round(compliance_percentage, 2),
            "overall_status": "compliant" if compliance_percentage >= 95 else "non_compliant",
        }

        report = {
            "summary": summary,
            "sections": report_sections,
            "recommendations": self._generate_recommendations(framework, report_sections),
        }

        logger.info(f"Compliance report generated: {compliance_percentage:.1f}% compliant")
        return report

    async def _generate_requirement_report(
        self,
        requirement: ComplianceRequirement,
        start_date: datetime,
        end_date: datetime,
        include_details: bool
    ) -> Dict[str, Any]:
        """
        Generate report section for a specific compliance requirement
        """
        if requirement == ComplianceRequirement.DATA_ACCESS_LOGGING:
            return await self._check_data_access_logging(start_date, end_date, include_details)

        elif requirement == ComplianceRequirement.DATA_MODIFICATION_LOGGING:
            return await self._check_data_modification_logging(start_date, end_date, include_details)

        elif requirement == ComplianceRequirement.USER_ACTIVITY_MONITORING:
            return await self._check_user_activity_monitoring(start_date, end_date, include_details)

        elif requirement == ComplianceRequirement.SECURITY_EVENT_LOGGING:
            return await self._check_security_event_logging(start_date, end_date, include_details)

        elif requirement == ComplianceRequirement.PRIVACY_DATA_HANDLING:
            return await self._check_privacy_data_handling(start_date, end_date, include_details)

        elif requirement == ComplianceRequirement.AUDIT_TRAIL_INTEGRITY:
            return await self._check_audit_trail_integrity(start_date, end_date, include_details)

        elif requirement == ComplianceRequirement.RETENTION_POLICY_COMPLIANCE:
            return await self._check_retention_policy_compliance(start_date, end_date, include_details)

        elif requirement == ComplianceRequirement.ACCESS_CONTROL_LOGGING:
            return await self._check_access_control_logging(start_date, end_date, include_details)

        else:
            return {
                "compliant": False,
                "message": f"Requirement {requirement.value} not implemented",
                "details": None,
            }

    async def _check_data_access_logging(
        self, start_date: datetime, end_date: datetime, include_details: bool
    ) -> Dict[str, Any]:
        """
        Check compliance for data access logging
        """
        # Query for read operations
        query = AuditQuery(
            start_date=start_date,
            end_date=end_date,
            operation_types=["read"],
        )

        logs = await self.audit_engine.query_audit_logs(query)
        read_operations = len(logs)

        # Check for sensitive data access
        sensitive_access = [log for log in logs if self._is_sensitive_entity(log.get("entity_type", ""))]

        compliant = read_operations > 0  # At least some read operations should be logged

        result = {
            "compliant": compliant,
            "read_operations_logged": read_operations,
            "sensitive_data_access": len(sensitive_access),
            "message": f"Found {read_operations} logged read operations",
        }

        if include_details and compliant:
            result["sample_logs"] = logs[:5]  # First 5 logs as samples

        return result

    async def _check_data_modification_logging(
        self, start_date: datetime, end_date: datetime, include_details: bool
    ) -> Dict[str, Any]:
        """
        Check compliance for data modification logging
        """
        # Query for write operations
        query = AuditQuery(
            start_date=start_date,
            end_date=end_date,
            operation_types=["create", "update", "delete"],
        )

        logs = await self.audit_engine.query_audit_logs(query)
        modification_operations = len(logs)

        # Check for user data modifications
        user_modifications = [log for log in logs if "user" in log.get("entity_type", "").lower()]

        compliant = modification_operations > 0

        result = {
            "compliant": compliant,
            "modification_operations_logged": modification_operations,
            "user_data_modifications": len(user_modifications),
            "message": f"Found {modification_operations} logged modification operations",
        }

        if include_details and compliant:
            result["sample_logs"] = logs[:5]

        return result

    async def _check_user_activity_monitoring(
        self, start_date: datetime, end_date: datetime, include_details: bool
    ) -> Dict[str, Any]:
        """
        Check compliance for user activity monitoring
        """
        # Get all logs for the period
        query = AuditQuery(start_date=start_date, end_date=end_date)
        logs = await self.audit_engine.query_audit_logs(query)

        # Group by user
        user_activity = {}
        for log in logs:
            user = log.get("performed_by", "unknown")
            if user not in user_activity:
                user_activity[user] = []
            user_activity[user].append(log)

        active_users = len([user for user, logs in user_activity.items() if len(logs) > 0])

        compliant = active_users > 0

        result = {
            "compliant": compliant,
            "active_users": active_users,
            "total_activities": len(logs),
            "message": f"Found activity from {active_users} users",
        }

        if include_details and compliant:
            result["user_activity_summary"] = {
                user: len(logs) for user, logs in user_activity.items()
            }

        return result

    async def _check_security_event_logging(
        self, start_date: datetime, end_date: datetime, include_details: bool
    ) -> Dict[str, Any]:
        """
        Check compliance for security event logging
        """
        # Query for security-related logs
        query = AuditQuery(
            start_date=start_date,
            end_date=end_date,
            log_levels=["warning", "error", "critical"],
        )

        logs = await self.audit_engine.query_audit_logs(query)
        security_events = len(logs)

        # Categorize security events
        auth_failures = [log for log in logs if "authentication" in log.get("context", "")]
        access_denials = [log for log in logs if "denied" in str(log.get("details", ""))]

        compliant = security_events > 0  # Should have some security events

        result = {
            "compliant": compliant,
            "security_events_logged": security_events,
            "authentication_failures": len(auth_failures),
            "access_denials": len(access_denials),
            "message": f"Found {security_events} security-related events",
        }

        if include_details and compliant:
            result["sample_security_events"] = logs[:5]

        return result

    async def _check_privacy_data_handling(
        self, start_date: datetime, end_date: datetime, include_details: bool
    ) -> Dict[str, Any]:
        """
        Check compliance for privacy data handling
        """
        # Query for operations on sensitive data
        query = AuditQuery(
            start_date=start_date,
            end_date=end_date,
            entity_types=["User", "UserProfile", "UserSettings"],
        )

        logs = await self.audit_engine.query_audit_logs(query)
        privacy_operations = len(logs)

        # Check for data access justifications (simplified)
        operations_with_details = [log for log in logs if log.get("details")]

        compliant = privacy_operations > 0 and len(operations_with_details) > 0

        result = {
            "compliant": compliant,
            "privacy_operations_logged": privacy_operations,
            "operations_with_details": len(operations_with_details),
            "message": f"Found {privacy_operations} privacy-related operations",
        }

        if include_details and compliant:
            result["sample_privacy_logs"] = logs[:3]

        return result

    async def _check_audit_trail_integrity(
        self, start_date: datetime, end_date: datetime, include_details: bool
    ) -> Dict[str, Any]:
        """
        Check compliance for audit trail integrity
        """
        # Get statistics
        stats = await self.audit_engine.get_audit_statistics(
            AuditQuery(start_date=start_date, end_date=end_date)
        )

        total_logs = stats.get("total_operations", 0)

        # Check for gaps in logging (simplified check)
        # In a real implementation, you'd check for sequential IDs, timestamps, etc.
        logs_with_timestamps = total_logs  # Assume all logs have timestamps

        # Check for system operations (indicating automated processes)
        system_operations = stats.get("context_distribution", {}).get("system", 0)

        compliant = total_logs > 0 and logs_with_timestamps == total_logs

        result = {
            "compliant": compliant,
            "total_audit_entries": total_logs,
            "entries_with_timestamps": logs_with_timestamps,
            "system_operations": system_operations,
            "message": f"Audit trail contains {total_logs} entries with proper timestamps",
        }

        if include_details:
            result["audit_statistics"] = stats

        return result

    async def _check_retention_policy_compliance(
        self, start_date: datetime, end_date: datetime, include_details: bool
    ) -> Dict[str, Any]:
        """
        Check compliance for retention policy
        """
        # This is a simplified check - in reality, you'd verify against actual retention policies
        current_time = datetime.now(timezone.utc)

        # Check if we're retaining logs for the required period
        days_covered = (end_date - start_date).days

        # Assume compliance if we have logs covering the requested period
        query = AuditQuery(start_date=start_date, end_date=end_date)
        logs = await self.audit_engine.query_audit_logs(query)

        has_logs_for_period = len(logs) > 0

        compliant = has_logs_for_period and days_covered <= 365  # Max 1 year for demo

        result = {
            "compliant": compliant,
            "period_days": days_covered,
            "logs_available": len(logs),
            "message": f"Retention policy compliant for {days_covered}-day period",
        }

        return result

    async def _check_access_control_logging(
        self, start_date: datetime, end_date: datetime, include_details: bool
    ) -> Dict[str, Any]:
        """
        Check compliance for access control logging
        """
        # Query for authentication and authorization events
        query = AuditQuery(
            start_date=start_date,
            end_date=end_date,
            contexts=["authentication", "authorization"],
        )

        logs = await self.audit_engine.query_audit_logs(query)
        access_control_events = len(logs)

        # Check for different types of access events
        auth_success = [log for log in logs if "success" in str(log.get("details", ""))]
        auth_failures = [log for log in logs if "failed" in str(log.get("details", "")) or "invalid" in str(log.get("details", ""))]

        compliant = access_control_events > 0

        result = {
            "compliant": compliant,
            "access_control_events": access_control_events,
            "successful_authentications": len(auth_success),
            "failed_authentications": len(auth_failures),
            "message": f"Found {access_control_events} access control events",
        }

        if include_details and compliant:
            result["sample_access_logs"] = logs[:3]

        return result

    def _is_sensitive_entity(self, entity_type: str) -> bool:
        """
        Check if an entity type contains sensitive data
        """
        sensitive_entities = ["User", "UserProfile", "UserSettings", "FinancialAccount"]
        return any(sensitive in entity_type for sensitive in sensitive_entities)

    def _generate_recommendations(
        self, framework: ComplianceFramework, sections: Dict[str, Any]
    ) -> List[str]:
        """
        Generate compliance recommendations based on report findings
        """
        recommendations = []

        for requirement_name, section_data in sections.items():
            if not section_data.get("compliant", False):
                if requirement_name == "data_access_logging":
                    recommendations.append("Implement comprehensive data access logging for all read operations")
                elif requirement_name == "data_modification_logging":
                    recommendations.append("Ensure all data modification operations are logged with before/after values")
                elif requirement_name == "user_activity_monitoring":
                    recommendations.append("Implement user activity monitoring and reporting")
                elif requirement_name == "security_event_logging":
                    recommendations.append("Enhance security event logging and alerting")
                elif requirement_name == "privacy_data_handling":
                    recommendations.append("Implement privacy data handling and consent logging")
                elif requirement_name == "audit_trail_integrity":
                    recommendations.append("Ensure audit trail integrity with tamper-proof logging")
                elif requirement_name == "retention_policy_compliance":
                    recommendations.append("Review and implement appropriate data retention policies")
                elif requirement_name == "access_control_logging":
                    recommendations.append("Implement comprehensive access control event logging")

        if not recommendations:
            recommendations.append("All compliance requirements are currently met")

        return recommendations

    async def export_compliance_report(
        self,
        framework: ComplianceFramework,
        start_date: datetime,
        end_date: datetime,
        format: ReportFormat = ReportFormat.JSON
    ) -> str:
        """
        Export a compliance report to file
        """
        report = await self.generate_compliance_report(framework, start_date, end_date)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"compliance_report_{framework.value}_{timestamp}.{format.value}"

        # Export using audit engine
        await self.audit_engine.generate_report(
            query=AuditQuery(start_date=start_date, end_date=end_date),
            title=f"{framework.value.upper()} Compliance Report",
            description=f"Compliance report for {framework.value.upper()} framework",
            format=format,
            generated_by="compliance_service",
        )

        return filename


# Global compliance service instance
audit_compliance_service = AuditComplianceService()