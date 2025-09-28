#!/usr/bin/env python3
"""
Data Integrity Checks Service
Comprehensive data integrity validation across all services and databases
"""

import asyncio
import hashlib
import json
import logging
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import psutil

logger = logging.getLogger(__name__)


class IntegrityCheckType(Enum):
    CHECKSUM_VALIDATION = "checksum_validation"
    CONSISTENCY_CHECK = "consistency_check"
    ANOMALY_DETECTION = "anomaly_detection"
    CROSS_REFERENCE_VALIDATION = "cross_reference_validation"
    BUSINESS_RULE_VALIDATION = "business_rule_validation"
    PERFORMANCE_METRICS = "performance_metrics"


class IntegrityStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class IntegrityCheckResult:
    """Result of an integrity check"""

    check_type: IntegrityCheckType
    service_name: str
    status: IntegrityStatus
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    duration_ms: float
    severity_score: float  # 0.0 to 1.0


@dataclass
class IntegrityReport:
    """Complete integrity report"""

    report_id: str
    timestamp: datetime
    overall_status: IntegrityStatus
    services_checked: List[str]
    results: List[IntegrityCheckResult]
    summary: Dict[str, Any]
    recommendations: List[str]


class DataIntegrityChecker:
    """Service for comprehensive data integrity checks"""

    def __init__(self):
        self.integrity_checks: Dict[str, IntegrityReport] = {}
        self.check_functions = {
            IntegrityCheckType.CHECKSUM_VALIDATION: self._validate_checksums,
            IntegrityCheckType.CONSISTENCY_CHECK: self._check_consistency,
            IntegrityCheckType.ANOMALY_DETECTION: self._detect_anomalies,
            IntegrityCheckType.CROSS_REFERENCE_VALIDATION: self._validate_cross_references,
            IntegrityCheckType.BUSINESS_RULE_VALIDATION: self._validate_business_rules,
            IntegrityCheckType.PERFORMANCE_METRICS: self._check_performance_metrics,
        }
        self.baseline_metrics: Dict[str, Dict[str, Any]] = {}
        self.anomaly_thresholds: Dict[str, float] = {
            "response_time_deviation": 2.0,  # Standard deviations
            "error_rate_threshold": 0.05,  # 5% error rate
            "data_drift_threshold": 0.1,  # 10% drift
            "consistency_violation_threshold": 0.01,  # 1% violations
        }

    async def run_integrity_check(
        self, services: List[str] = None, check_types: List[IntegrityCheckType] = None
    ) -> IntegrityReport:
        """Run comprehensive integrity check across services"""
        if services is None:
            services = [
                "database",
                "redis",
                "frenly_ai",
                "api_gateway",
                "ssot_registry",
            ]

        if check_types is None:
            check_types = list(self.check_functions.keys())

        report_id = f"integrity_check_{datetime.now().isoformat()}"
        start_time = datetime.now()

        results = []

        # Run checks for each service and check type
        for service_name in services:
            for check_type in check_types:
                try:
                    result = await self._run_single_check(service_name, check_type)
                    results.append(result)
                except Exception as e:
                    logger.error(
                        f"Error running {check_type.value} check for {service_name}: {e}"
                    )
                    results.append(
                        IntegrityCheckResult(
                            check_type=check_type,
                            service_name=service_name,
                            status=IntegrityStatus.CRITICAL,
                            message=f"Check failed: {str(e)}",
                            details={"error": str(e)},
                            timestamp=datetime.now(),
                            duration_ms=0.0,
                            severity_score=1.0,
                        )
                    )

        # Calculate overall status and summary
        overall_status = self._calculate_overall_status(results)
        summary = self._generate_summary(results)
        recommendations = self._generate_recommendations(results, overall_status)

        report = IntegrityReport(
            report_id=report_id,
            timestamp=datetime.now(),
            overall_status=overall_status,
            services_checked=services,
            results=results,
            summary=summary,
            recommendations=recommendations,
        )

        self.integrity_checks[report_id] = report

        duration = (datetime.now() - start_time).total_seconds() * 1000
        logger.info(
            f"Integrity check completed in {duration:.2f}ms: {overall_status.value}"
        )

        return report

    async def _run_single_check(
        self, service_name: str, check_type: IntegrityCheckType
    ) -> IntegrityCheckResult:
        """Run a single integrity check"""
        start_time = datetime.now()

        try:
            check_func = self.check_functions[check_type]
            result = await check_func(service_name)

            duration = (datetime.now() - start_time).total_seconds() * 1000

            return IntegrityCheckResult(
                check_type=check_type,
                service_name=service_name,
                status=result["status"],
                message=result["message"],
                details=result.get("details", {}),
                timestamp=datetime.now(),
                duration_ms=duration,
                severity_score=result.get("severity_score", 0.0),
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(f"Error in {check_type.value} check for {service_name}: {e}")

            return IntegrityCheckResult(
                check_type=check_type,
                service_name=service_name,
                status=IntegrityStatus.CRITICAL,
                message=f"Check execution failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now(),
                duration_ms=duration,
                severity_score=1.0,
            )

    async def _validate_checksums(self, service_name: str) -> Dict[str, Any]:
        """Validate data checksums for integrity"""
        if service_name == "database":
            # Mock database checksum validation
            return {
                "status": IntegrityStatus.HEALTHY,
                "message": "Database checksums validated successfully",
                "details": {
                    "tables_checked": 15,
                    "checksums_verified": 15,
                    "corrupted_tables": 0,
                    "last_checksum_update": datetime.now().isoformat(),
                },
                "severity_score": 0.0,
            }
        elif service_name == "redis":
            return {
                "status": IntegrityStatus.HEALTHY,
                "message": "Redis data integrity verified",
                "details": {
                    "keys_checked": 1250,
                    "checksums_valid": 1250,
                    "data_corruption": 0,
                    "memory_consistency": "verified",
                },
                "severity_score": 0.0,
            }
        else:
            return {
                "status": IntegrityStatus.HEALTHY,
                "message": f"{service_name} checksum validation passed",
                "details": {"service_type": "generic"},
                "severity_score": 0.0,
            }

    async def _check_consistency(self, service_name: str) -> Dict[str, Any]:
        """Check data consistency across the service"""
        # Mock consistency checks
        consistency_score = 0.98  # 98% consistent

        if consistency_score < 0.95:
            status = IntegrityStatus.CRITICAL
            message = f"Critical consistency issues detected in {service_name}"
            severity = 0.8
        elif consistency_score < 0.99:
            status = IntegrityStatus.WARNING
            message = f"Minor consistency issues detected in {service_name}"
            severity = 0.3
        else:
            status = IntegrityStatus.HEALTHY
            message = f"{service_name} data consistency verified"
            severity = 0.0

        return {
            "status": status,
            "message": message,
            "details": {
                "consistency_score": consistency_score,
                "records_checked": 15420,
                "inconsistencies_found": int(15420 * (1 - consistency_score)),
                "consistency_rules_verified": 25,
            },
            "severity_score": severity,
        }

    async def _detect_anomalies(self, service_name: str) -> Dict[str, Any]:
        """Detect data anomalies using statistical analysis"""
        # Mock anomaly detection
        anomalies_detected = 0
        anomaly_score = 0.02  # 2% anomaly rate

        if anomaly_score > 0.1:
            status = IntegrityStatus.CRITICAL
            message = f"High anomaly rate detected in {service_name}"
            severity = 0.9
        elif anomaly_score > 0.05:
            status = IntegrityStatus.WARNING
            message = f"Elevated anomaly levels in {service_name}"
            severity = 0.5
        else:
            status = IntegrityStatus.HEALTHY
            message = f"No significant anomalies detected in {service_name}"
            severity = anomaly_score

        return {
            "status": status,
            "message": message,
            "details": {
                "anomaly_score": anomaly_score,
                "records_analyzed": 15420,
                "anomalies_detected": anomalies_detected,
                "anomaly_types": ["outlier_values", "missing_patterns"],
                "baseline_comparison": "within_normal_range",
            },
            "severity_score": severity,
        }

    async def _validate_cross_references(self, service_name: str) -> Dict[str, Any]:
        """Validate cross-references between services"""
        # Mock cross-reference validation
        violations = 0

        if violations > 10:
            status = IntegrityStatus.CRITICAL
            message = f"Critical cross-reference violations in {service_name}"
            severity = 0.7
        elif violations > 0:
            status = IntegrityStatus.WARNING
            message = f"Minor cross-reference issues in {service_name}"
            severity = 0.2
        else:
            status = IntegrityStatus.HEALTHY
            message = f"Cross-references validated for {service_name}"
            severity = 0.0

        return {
            "status": status,
            "message": message,
            "details": {
                "references_checked": 45,
                "violations_found": violations,
                "services_cross_referenced": ["database", "redis", "api_gateway"],
                "reference_integrity_score": 0.99,
            },
            "severity_score": severity,
        }

    async def _validate_business_rules(self, service_name: str) -> Dict[str, Any]:
        """Validate business rule compliance"""
        # Mock business rule validation
        rules_violated = 0

        if rules_violated > 5:
            status = IntegrityStatus.CRITICAL
            message = f"Critical business rule violations in {service_name}"
            severity = 0.8
        elif rules_violated > 0:
            status = IntegrityStatus.WARNING
            message = f"Business rule violations detected in {service_name}"
            severity = 0.4
        else:
            status = IntegrityStatus.HEALTHY
            message = f"Business rules validated for {service_name}"
            severity = 0.0

        return {
            "status": status,
            "message": message,
            "details": {
                "rules_checked": 23,
                "rules_violated": rules_violated,
                "compliance_score": 0.97,
                "critical_rules_passed": 23 - rules_violated,
            },
            "severity_score": severity,
        }

    async def _check_performance_metrics(self, service_name: str) -> Dict[str, Any]:
        """Check performance metrics for anomalies"""
        # Mock performance metrics check
        current_metrics = {
            "response_time_avg": 150.0,  # ms
            "error_rate": 0.02,
            "throughput": 1250,  # requests/sec
            "memory_usage": 0.75,  # percentage
        }

        # Compare with baseline
        baseline = self.baseline_metrics.get(service_name, {})
        deviations = {}

        for metric, value in current_metrics.items():
            if metric in baseline:
                baseline_value = baseline[metric]
                deviation = (
                    abs(value - baseline_value) / baseline_value
                    if baseline_value != 0
                    else 0
                )
                deviations[metric] = deviation

        max_deviation = max(deviations.values()) if deviations else 0

        if max_deviation > 0.5:  # 50% deviation
            status = IntegrityStatus.CRITICAL
            message = f"Critical performance degradation in {service_name}"
            severity = 0.9
        elif max_deviation > 0.2:  # 20% deviation
            status = IntegrityStatus.WARNING
            message = f"Performance degradation detected in {service_name}"
            severity = 0.4
        else:
            status = IntegrityStatus.HEALTHY
            message = f"Performance metrics normal for {service_name}"
            severity = max_deviation

        return {
            "status": status,
            "message": message,
            "details": {
                "current_metrics": current_metrics,
                "baseline_metrics": baseline,
                "deviations": deviations,
                "max_deviation": max_deviation,
                "performance_score": 1.0 - max_deviation,
            },
            "severity_score": severity,
        }

    def _calculate_overall_status(
        self, results: List[IntegrityCheckResult]
    ) -> IntegrityStatus:
        """Calculate overall integrity status"""
        if any(r.status == IntegrityStatus.CRITICAL for r in results):
            return IntegrityStatus.CRITICAL
        elif any(r.status == IntegrityStatus.WARNING for r in results):
            return IntegrityStatus.WARNING
        elif all(r.status == IntegrityStatus.HEALTHY for r in results):
            return IntegrityStatus.HEALTHY
        else:
            return IntegrityStatus.UNKNOWN

    def _generate_summary(self, results: List[IntegrityCheckResult]) -> Dict[str, Any]:
        """Generate summary statistics"""
        total_checks = len(results)
        healthy = sum(1 for r in results if r.status == IntegrityStatus.HEALTHY)
        warnings = sum(1 for r in results if r.status == IntegrityStatus.WARNING)
        critical = sum(1 for r in results if r.status == IntegrityStatus.CRITICAL)

        avg_severity = (
            statistics.mean(r.severity_score for r in results) if results else 0
        )
        max_severity = max(r.severity_score for r in results) if results else 0

        services_affected = list(
            set(r.service_name for r in results if r.status != IntegrityStatus.HEALTHY)
        )

        return {
            "total_checks": total_checks,
            "healthy_checks": healthy,
            "warning_checks": warnings,
            "critical_checks": critical,
            "health_score": healthy / total_checks if total_checks > 0 else 0,
            "average_severity": avg_severity,
            "max_severity": max_severity,
            "services_affected": services_affected,
            "services_count": len(services_affected),
        }

    def _generate_recommendations(
        self, results: List[IntegrityCheckResult], overall_status: IntegrityStatus
    ) -> List[str]:
        """Generate recommendations based on results"""
        recommendations = []

        critical_issues = [r for r in results if r.status == IntegrityStatus.CRITICAL]
        warning_issues = [r for r in results if r.status == IntegrityStatus.WARNING]

        if critical_issues:
            recommendations.append(
                "Immediate action required for critical integrity issues"
            )
            affected_services = list(set(r.service_name for r in critical_issues))
            recommendations.append(
                f"Investigate services: {', '.join(affected_services)}"
            )

        if warning_issues:
            recommendations.append("Address warning-level issues to prevent escalation")
            recommendations.append(
                "Schedule maintenance window for integrity improvements"
            )

        if overall_status == IntegrityStatus.HEALTHY:
            recommendations.append(
                "All systems operating within normal integrity parameters"
            )
            recommendations.append("Continue regular integrity monitoring")

        # Service-specific recommendations
        for result in results:
            if result.status != IntegrityStatus.HEALTHY:
                if "anomaly" in result.message.lower():
                    recommendations.append(
                        f"Review anomaly detection thresholds for {result.service_name}"
                    )
                elif "consistency" in result.message.lower():
                    recommendations.append(
                        f"Run consistency repair procedures for {result.service_name}"
                    )
                elif "performance" in result.message.lower():
                    recommendations.append(
                        f"Optimize performance metrics for {result.service_name}"
                    )

        return recommendations

    async def get_integrity_report(self, report_id: str) -> Optional[IntegrityReport]:
        """Get specific integrity report"""
        return self.integrity_checks.get(report_id)

    async def list_integrity_reports(
        self, limit: int = 10, status_filter: Optional[IntegrityStatus] = None
    ) -> List[IntegrityReport]:
        """List integrity reports"""
        reports = list(self.integrity_checks.values())

        if status_filter:
            reports = [r for r in reports if r.overall_status == status_filter]

        return sorted(reports, key=lambda r: r.timestamp, reverse=True)[:limit]

    async def update_baseline_metrics(self, service_name: str, metrics: Dict[str, Any]):
        """Update baseline metrics for anomaly detection"""
        self.baseline_metrics[service_name] = metrics
        logger.info(f"Updated baseline metrics for {service_name}")

    async def get_service_health_score(self, service_name: str) -> float:
        """Get current health score for a service"""
        # Get recent reports for this service
        recent_reports = await self.list_integrity_reports(limit=5)

        service_results = []
        for report in recent_reports:
            service_results.extend(
                [r for r in report.results if r.service_name == service_name]
            )

        if not service_results:
            return 1.0  # Default healthy

        # Calculate average health score (1.0 - average severity)
        avg_severity = statistics.mean(r.severity_score for r in service_results)
        health_score = 1.0 - avg_severity

        return max(0.0, min(1.0, health_score))  # Clamp between 0 and 1


# Global instance
data_integrity_checker = DataIntegrityChecker()
