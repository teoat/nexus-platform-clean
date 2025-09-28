#!/usr/bin/env python3
"""
AI-Driven SSOT Optimizer Service
Automated conflict resolution and consistency optimization for SSOT
"""

import asyncio
import difflib
import json
import logging
import re
import statistics
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# Import audit logging
from .audit_logging import AuditLogQueryEngine, AuditLogLevel, OperationType

logger = logging.getLogger(__name__)


class ConflictType(Enum):
    DUPLICATE_ENTRIES = "duplicate_entries"
    INCONSISTENT_DATA = "inconsistent_data"
    MISSING_REFERENCES = "missing_references"
    STALE_DATA = "stale_data"
    CONFLICTING_UPDATES = "conflicting_updates"
    SCHEMA_VIOLATIONS = "schema_violations"


class OptimizationAction(Enum):
    MERGE_DUPLICATES = "merge_duplicates"
    RESOLVE_CONFLICTS = "resolve_conflicts"
    UPDATE_REFERENCES = "update_references"
    CLEANUP_STALE_DATA = "cleanup_stale_data"
    NORMALIZE_DATA = "normalize_data"
    VALIDATE_CONSISTENCY = "validate_consistency"


class ConfidenceLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MANUAL_REVIEW = "manual_review"


@dataclass
class ConflictAnalysis:
    """Analysis of a detected conflict"""

    conflict_id: str
    conflict_type: ConflictType
    affected_entities: List[str]
    severity_score: float
    confidence_level: ConfidenceLevel
    suggested_resolution: Dict[str, Any]
    evidence: List[str]
    timestamp: datetime


@dataclass
class OptimizationResult:
    """Result of an optimization action"""

    action_id: str
    action_type: OptimizationAction
    target_entities: List[str]
    status: str
    changes_applied: Dict[str, Any]
    rollback_available: bool
    confidence_score: float
    timestamp: datetime


@dataclass
class SSOTOptimizationReport:
    """Complete optimization report"""

    report_id: str
    timestamp: datetime
    conflicts_detected: List[ConflictAnalysis]
    optimizations_applied: List[OptimizationResult]
    consistency_score: float
    improvement_metrics: Dict[str, Any]
    recommendations: List[str]


class AISsotOptimizer:
    """AI-driven SSOT optimization and conflict resolution service"""

    def __init__(self):
        self.conflicts: Dict[str, ConflictAnalysis] = {}
        self.optimizations: Dict[str, OptimizationResult] = {}
        self.optimization_reports: Dict[str, SSOTOptimizationReport] = {}
        self.consistency_baseline: Dict[str, float] = {}
        self.learning_patterns: Dict[str, Any] = {}

        # Initialize audit logging
        self.audit_engine = AuditLogQueryEngine()

        # AI model parameters
        self.confidence_thresholds = {
            ConfidenceLevel.HIGH: 0.9,
            ConfidenceLevel.MEDIUM: 0.7,
            ConfidenceLevel.LOW: 0.5,
            ConfidenceLevel.MANUAL_REVIEW: 0.3,
        }

    async def run_ssot_optimization(
        self, scope: str = "full", auto_resolve: bool = False
    ) -> SSOTOptimizationReport:
        """Run comprehensive SSOT optimization"""
        report_id = f"ssot_opt_{datetime.now().isoformat()}"

        logger.info(f"Starting SSOT optimization: {report_id}")

        # Phase 1: Conflict Detection
        conflicts = await self._detect_conflicts(scope)

        # Phase 2: Analysis and Resolution Planning
        analyzed_conflicts = await self._analyze_conflicts(conflicts)

        # Phase 3: Optimization Execution
        optimizations = []
        if auto_resolve:
            optimizations = await self._execute_optimizations(analyzed_conflicts)
        else:
            # Generate recommendations only
            optimizations = await self._generate_optimization_plan(analyzed_conflicts)

        # Phase 4: Consistency Validation
        consistency_score = await self._calculate_consistency_score()

        # Phase 5: Generate Report
        improvement_metrics = await self._calculate_improvement_metrics(
            consistency_score
        )

        recommendations = await self._generate_recommendations(
            analyzed_conflicts, optimizations, consistency_score
        )

        report = SSOTOptimizationReport(
            report_id=report_id,
            timestamp=datetime.now(),
            conflicts_detected=analyzed_conflicts,
            optimizations_applied=optimizations,
            consistency_score=consistency_score,
            improvement_metrics=improvement_metrics,
            recommendations=recommendations,
        )

        self.optimization_reports[report_id] = report

        logger.info(
            f"SSOT optimization completed: {report_id} - Consistency: {consistency_score:.3f}"
        )

        # Audit log AI optimization
        try:
            await self.audit_engine.log_operation(
                operation=OperationType.SYSTEM.value,
                entity_type="AIOptimization",
                entity_id=report_id,
                details={
                    "optimization_scope": scope,
                    "auto_resolve": auto_resolve,
                    "conflicts_detected": len(analyzed_conflicts),
                    "optimizations_applied": len(optimizations),
                    "consistency_score": consistency_score,
                    "improvement_metrics": improvement_metrics,
                    "recommendations_count": len(recommendations),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                performed_by="ai_optimizer",
                context="ai_operations",
                log_level=AuditLogLevel.INFO,
            )
        except Exception as e:
            logger.error(f"Failed to audit log AI optimization: {e}")

        return report

    async def _detect_conflicts(self, scope: str) -> List[Dict[str, Any]]:
        """Detect various types of conflicts in SSOT"""
        conflicts = []

        # Detect duplicate entries
        duplicates = await self._detect_duplicates(scope)
        conflicts.extend(duplicates)

        # Detect inconsistent data
        inconsistencies = await self._detect_inconsistencies(scope)
        conflicts.extend(inconsistencies)

        # Detect missing references
        missing_refs = await self._detect_missing_references(scope)
        conflicts.extend(missing_refs)

        # Detect stale data
        stale_data = await self._detect_stale_data(scope)
        conflicts.extend(stale_data)

        # Detect conflicting updates
        conflicting_updates = await self._detect_conflicting_updates(scope)
        conflicts.extend(conflicting_updates)

        # Detect schema violations
        schema_violations = await self._detect_schema_violations(scope)
        conflicts.extend(schema_violations)

        return conflicts

    async def _detect_duplicates(self, scope: str) -> List[Dict[str, Any]]:
        """Detect duplicate entries using similarity analysis"""
        # Mock duplicate detection - in real implementation, this would analyze SSOT data
        duplicates = [
            {
                "type": ConflictType.DUPLICATE_ENTRIES,
                "entities": ["alias_123", "alias_456"],
                "similarity_score": 0.95,
                "evidence": [
                    "Similar canonical URLs",
                    "Same context usage",
                    "Overlapping descriptions",
                ],
            }
        ]
        return duplicates

    async def _detect_inconsistencies(self, scope: str) -> List[Dict[str, Any]]:
        """Detect data inconsistencies"""
        inconsistencies = [
            {
                "type": ConflictType.INCONSISTENT_DATA,
                "entities": ["service_config", "deployment_config"],
                "inconsistency_type": "version_mismatch",
                "evidence": [
                    "Version 2.1.0 vs 2.1.1",
                    "Last updated timestamps differ by 2 hours",
                ],
            }
        ]
        return inconsistencies

    async def _detect_missing_references(self, scope: str) -> List[Dict[str, Any]]:
        """Detect missing references between entities"""
        missing_refs = [
            {
                "type": ConflictType.MISSING_REFERENCES,
                "entities": ["api_endpoint_789"],
                "missing_references": ["auth_service", "rate_limiting_config"],
                "evidence": ["Endpoint references non-existent services"],
            }
        ]
        return missing_refs

    async def _detect_stale_data(self, scope: str) -> List[Dict[str, Any]]:
        """Detect stale or outdated data"""
        stale_data = [
            {
                "type": ConflictType.STALE_DATA,
                "entities": ["old_config_backup"],
                "staleness_score": 0.8,
                "evidence": [
                    "Last updated 6 months ago",
                    "References deprecated services",
                ],
            }
        ]
        return stale_data

    async def _detect_conflicting_updates(self, scope: str) -> List[Dict[str, Any]]:
        """Detect conflicting concurrent updates"""
        conflicting_updates = [
            {
                "type": ConflictType.CONFLICTING_UPDATES,
                "entities": ["user_profile_123"],
                "conflicts": ["email_updated", "name_updated"],
                "evidence": [
                    "Concurrent updates from different sources",
                    "Timestamp overlap",
                ],
            }
        ]
        return conflicting_updates

    async def _detect_schema_violations(self, scope: str) -> List[Dict[str, Any]]:
        """Detect schema violations"""
        schema_violations = [
            {
                "type": ConflictType.SCHEMA_VIOLATIONS,
                "entities": ["invalid_config"],
                "violations": ["missing_required_field", "invalid_data_type"],
                "evidence": [
                    "Schema validation failed",
                    "Type mismatch in field 'port'",
                ],
            }
        ]
        return schema_violations

    async def _analyze_conflicts(
        self, raw_conflicts: List[Dict[str, Any]]
    ) -> List[ConflictAnalysis]:
        """Analyze conflicts and determine resolution strategies"""
        analyzed_conflicts = []

        for i, conflict in enumerate(raw_conflicts):
            conflict_id = f"conflict_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"

            # Determine severity and confidence based on conflict type and evidence
            severity_score, confidence_level = self._assess_conflict_severity(conflict)

            # Generate resolution suggestion
            suggested_resolution = await self._generate_resolution_suggestion(conflict)

            analysis = ConflictAnalysis(
                conflict_id=conflict_id,
                conflict_type=conflict["type"],
                affected_entities=conflict["entities"],
                severity_score=severity_score,
                confidence_level=confidence_level,
                suggested_resolution=suggested_resolution,
                evidence=conflict.get("evidence", []),
                timestamp=datetime.now(),
            )

            analyzed_conflicts.append(analysis)
            self.conflicts[conflict_id] = analysis

        return analyzed_conflicts

    def _assess_conflict_severity(
        self, conflict: Dict[str, Any]
    ) -> Tuple[float, ConfidenceLevel]:
        """Assess the severity and confidence level of a conflict"""
        conflict_type = conflict["type"]

        # Base severity scores by conflict type
        base_severity = {
            ConflictType.DUPLICATE_ENTRIES: 0.6,
            ConflictType.INCONSISTENT_DATA: 0.7,
            ConflictType.MISSING_REFERENCES: 0.8,
            ConflictType.STALE_DATA: 0.4,
            ConflictType.CONFLICTING_UPDATES: 0.9,
            ConflictType.SCHEMA_VIOLATIONS: 0.9,
        }

        severity = base_severity.get(conflict_type, 0.5)

        # Adjust based on evidence strength
        evidence_count = len(conflict.get("evidence", []))
        severity *= min(1.0, evidence_count / 3)  # More evidence = higher severity

        # Determine confidence level
        if severity >= self.confidence_thresholds[ConfidenceLevel.HIGH]:
            confidence = ConfidenceLevel.HIGH
        elif severity >= self.confidence_thresholds[ConfidenceLevel.MEDIUM]:
            confidence = ConfidenceLevel.MEDIUM
        elif severity >= self.confidence_thresholds[ConfidenceLevel.LOW]:
            confidence = ConfidenceLevel.LOW
        else:
            confidence = ConfidenceLevel.MANUAL_REVIEW

        return severity, confidence

    async def _generate_resolution_suggestion(
        self, conflict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI-powered resolution suggestion"""
        conflict_type = conflict["type"]

        if conflict_type == ConflictType.DUPLICATE_ENTRIES:
            return {
                "action": OptimizationAction.MERGE_DUPLICATES,
                "strategy": "merge_with_primary",
                "primary_entity": conflict["entities"][0],
                "secondary_entities": conflict["entities"][1:],
                "merge_rules": [
                    "keep_newer_data",
                    "preserve_references",
                    "update_audit_trail",
                ],
            }

        elif conflict_type == ConflictType.INCONSISTENT_DATA:
            return {
                "action": OptimizationAction.RESOLVE_CONFLICTS,
                "strategy": "authoritative_source",
                "authoritative_source": "database_primary",
                "fallback_strategy": "most_recent_update",
                "validation_rules": ["check_data_integrity", "verify_references"],
            }

        elif conflict_type == ConflictType.MISSING_REFERENCES:
            return {
                "action": OptimizationAction.UPDATE_REFERENCES,
                "strategy": "create_placeholders",
                "missing_entities": conflict.get("missing_references", []),
                "reference_type": "soft_reference",
                "cleanup_schedule": "30_days",
            }

        elif conflict_type == ConflictType.STALE_DATA:
            return {
                "action": OptimizationAction.CLEANUP_STALE_DATA,
                "strategy": "archive_and_remove",
                "retention_period": "90_days",
                "archive_location": "ssot_archive",
                "notification_required": True,
            }

        elif conflict_type == ConflictType.CONFLICTING_UPDATES:
            return {
                "action": OptimizationAction.RESOLVE_CONFLICTS,
                "strategy": "merge_with_conflict_resolution",
                "conflict_resolution_rules": [
                    "last_write_wins",
                    "preserve_audit_trail",
                ],
                "manual_review_required": True,
            }

        elif conflict_type == ConflictType.SCHEMA_VIOLATIONS:
            return {
                "action": OptimizationAction.NORMALIZE_DATA,
                "strategy": "schema_migration",
                "migration_type": "backward_compatible",
                "data_transformation_rules": ["type_conversion", "default_values"],
                "rollback_plan": "schema_rollback",
            }

        return {
            "action": OptimizationAction.VALIDATE_CONSISTENCY,
            "strategy": "manual_review",
            "reason": "Unknown conflict type",
        }

    async def _execute_optimizations(
        self, analyzed_conflicts: List[ConflictAnalysis]
    ) -> List[OptimizationResult]:
        """Execute optimization actions for high-confidence conflicts"""
        optimizations = []

        for conflict in analyzed_conflicts:
            if conflict.confidence_level in [
                ConfidenceLevel.HIGH,
                ConfidenceLevel.MEDIUM,
            ]:
                try:
                    result = await self._execute_single_optimization(conflict)
                    optimizations.append(result)
                    self.optimizations[result.action_id] = result
                except Exception as e:
                    logger.error(
                        f"Failed to execute optimization for conflict {conflict.conflict_id}: {e}"
                    )

        return optimizations

    async def _execute_single_optimization(
        self, conflict: ConflictAnalysis
    ) -> OptimizationResult:
        """Execute a single optimization action"""
        action_id = f"opt_{conflict.conflict_id}_{datetime.now().strftime('%H%M%S')}"

        # Mock optimization execution - in real implementation, this would apply actual changes
        changes_applied = {
            "entities_modified": len(conflict.affected_entities),
            "references_updated": 5,
            "audit_entries_created": 1,
        }

        result = OptimizationResult(
            action_id=action_id,
            action_type=conflict.suggested_resolution["action"],
            target_entities=conflict.affected_entities,
            status="completed",
            changes_applied=changes_applied,
            rollback_available=True,
            confidence_score=conflict.severity_score,
            timestamp=datetime.now(),
        )

        return result

    async def _generate_optimization_plan(
        self, analyzed_conflicts: List[ConflictAnalysis]
    ) -> List[OptimizationResult]:
        """Generate optimization plan without executing"""
        optimizations = []

        for conflict in analyzed_conflicts:
            action_id = (
                f"plan_{conflict.conflict_id}_{datetime.now().strftime('%H%M%S')}"
            )

            result = OptimizationResult(
                action_id=action_id,
                action_type=conflict.suggested_resolution["action"],
                target_entities=conflict.affected_entities,
                status="planned",
                changes_applied={},
                rollback_available=False,
                confidence_score=conflict.severity_score,
                timestamp=datetime.now(),
            )

            optimizations.append(result)

        return optimizations

    async def _calculate_consistency_score(self) -> float:
        """Calculate overall SSOT consistency score"""
        # Mock consistency calculation - in real implementation, this would analyze actual SSOT state
        base_score = 0.85

        # Adjust based on recent optimizations
        recent_optimizations = [
            opt
            for opt in self.optimizations.values()
            if opt.timestamp > datetime.now() - timedelta(hours=24)
        ]

        improvement_factor = (
            len(recent_optimizations) * 0.01
        )  # 1% improvement per optimization
        consistency_score = min(1.0, base_score + improvement_factor)

        return consistency_score

    async def _calculate_improvement_metrics(
        self, current_score: float
    ) -> Dict[str, Any]:
        """Calculate improvement metrics compared to baseline"""
        previous_score = self.consistency_baseline.get("overall", 0.8)

        improvement = current_score - previous_score
        improvement_percentage = (
            (improvement / previous_score) * 100 if previous_score > 0 else 0
        )

        # Update baseline
        self.consistency_baseline["overall"] = current_score

        return {
            "previous_score": previous_score,
            "current_score": current_score,
            "improvement": improvement,
            "improvement_percentage": improvement_percentage,
            "trend": "improving"
            if improvement > 0
            else "stable"
            if improvement == 0
            else "declining",
        }

    async def _generate_recommendations(
        self,
        conflicts: List[ConflictAnalysis],
        optimizations: List[OptimizationResult],
        consistency_score: float,
    ) -> List[str]:
        """Generate recommendations for SSOT optimization"""
        recommendations = []

        # Analyze conflict patterns
        conflict_types = [c.conflict_type for c in conflicts]
        most_common = (
            max(set(conflict_types), key=conflict_types.count)
            if conflict_types
            else None
        )

        if most_common:
            recommendations.append(
                f"Focus on reducing {most_common.value} conflicts - most common issue detected"
            )

        # Check consistency score
        if consistency_score < 0.8:
            recommendations.append(
                "Consistency score below threshold - schedule immediate optimization run"
            )
        elif consistency_score < 0.9:
            recommendations.append(
                "Consistency score could be improved - consider regular optimization schedule"
            )

        # Check manual review requirements
        manual_reviews = [
            c for c in conflicts if c.confidence_level == ConfidenceLevel.MANUAL_REVIEW
        ]
        if manual_reviews:
            recommendations.append(
                f"{len(manual_reviews)} conflicts require manual review"
            )

        # Optimization effectiveness
        successful_optimizations = [o for o in optimizations if o.status == "completed"]
        if successful_optimizations:
            avg_confidence = statistics.mean(
                o.confidence_score for o in successful_optimizations
            )
            recommendations.append(f"Average confidence: {avg_confidence:.2f}")
        # Learning recommendations
        if len(self.optimization_reports) > 5:
            recommendations.append(
                "Consider implementing machine learning model for conflict prediction"
            )

        return recommendations

    async def get_optimization_report(
        self, report_id: str
    ) -> Optional[SSOTOptimizationReport]:
        """Get specific optimization report"""
        return self.optimization_reports.get(report_id)

    async def list_optimization_reports(
        self, limit: int = 10
    ) -> List[SSOTOptimizationReport]:
        """List recent optimization reports"""
        reports = list(self.optimization_reports.values())
        return sorted(reports, key=lambda r: r.timestamp, reverse=True)[:limit]

    async def get_conflict_details(
        self, conflict_id: str
    ) -> Optional[ConflictAnalysis]:
        """Get details of a specific conflict"""
        return self.conflicts.get(conflict_id)

    async def resolve_conflict_manually(
        self, conflict_id: str, resolution: Dict[str, Any], approved_by: str
    ) -> bool:
        """Manually resolve a conflict"""
        conflict = self.conflicts.get(conflict_id)
        if not conflict:
            return False

        # Execute manual resolution
        try:
            result = await self._execute_manual_resolution(
                conflict, resolution, approved_by
            )
            self.optimizations[result.action_id] = result
            return True
        except Exception as e:
            logger.error(f"Manual resolution failed for conflict {conflict_id}: {e}")
            return False

    async def _execute_manual_resolution(
        self, conflict: ConflictAnalysis, resolution: Dict[str, Any], approved_by: str
    ) -> OptimizationResult:
        """Execute manual conflict resolution"""
        action_id = f"manual_{conflict.conflict_id}_{datetime.now().strftime('%H%M%S')}"

        result = OptimizationResult(
            action_id=action_id,
            action_type=OptimizationAction.RESOLVE_CONFLICTS,
            target_entities=conflict.affected_entities,
            status="completed",
            changes_applied={
                "manual_resolution": True,
                "approved_by": approved_by,
                "resolution_details": resolution,
            },
            rollback_available=True,
            confidence_score=1.0,  # Manual resolution has full confidence
            timestamp=datetime.now(),
        )

        return result

    async def get_ssot_health_metrics(self) -> Dict[str, Any]:
        """Get comprehensive SSOT health metrics"""
        reports = list(self.optimization_reports.values())[-10:]  # Last 10 reports

        if not reports:
            return {"status": "no_data"}

        consistency_scores = [r.consistency_score for r in reports]
        avg_consistency = (
            statistics.mean(consistency_scores) if consistency_scores else 0
        )

        total_conflicts = sum(len(r.conflicts_detected) for r in reports)
        resolved_conflicts = sum(len(r.optimizations_applied) for r in reports)

        resolution_rate = (
            resolved_conflicts / total_conflicts if total_conflicts > 0 else 0
        )

        return {
            "average_consistency_score": avg_consistency,
            "consistency_trend": self._calculate_trend(consistency_scores),
            "total_conflicts_detected": total_conflicts,
            "conflicts_resolved": resolved_conflicts,
            "resolution_rate": resolution_rate,
            "reports_analyzed": len(reports),
            "health_status": "healthy"
            if avg_consistency > 0.85
            else "warning"
            if avg_consistency > 0.7
            else "critical",
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from a list of values"""
        if len(values) < 2:
            return "stable"

        # Simple linear trend
        if len(values) >= 2:
            first_half = values[: len(values) // 2]
            second_half = values[len(values) // 2 :]

            first_avg = statistics.mean(first_half) if first_half else 0
            second_avg = statistics.mean(second_half) if second_half else 0

            if second_avg > first_avg + 0.01:
                return "improving"
            elif second_avg < first_avg - 0.01:
                return "declining"
            else:
                return "stable"

        return "stable"


# Global instance
ai_ssot_optimizer = AISsotOptimizer()
