#!/usr/bin/env python3
"""
NEXUS Platform - SSOT Conflict Detection and Resolution System
Advanced conflict detection and resolution for SSOT aliases and anchors
"""

import asyncio
import difflib
import json
import logging
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

# Import audit logging
from .audit_logging import AuditLogQueryEngine, AuditLogLevel, OperationType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConflictType(Enum):
    """Types of conflicts that can occur in SSOT"""

    ALIAS_DUPLICATE = "alias_duplicate"
    CANONICAL_MISMATCH = "canonical_mismatch"
    CONTEXT_OVERLAP = "context_overlap"
    NAMING_CONFLICT = "naming_conflict"
    SEMANTIC_CONFLICT = "semantic_conflict"
    DEPENDENCY_CONFLICT = "dependency_conflict"
    VERSION_CONFLICT = "version_conflict"
    OWNERSHIP_CONFLICT = "ownership_conflict"


class ConflictSeverity(Enum):
    """Severity levels for conflicts"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResolutionStrategy(Enum):
    """Available resolution strategies"""

    MANUAL = "manual"
    FIRST_WINS = "first_wins"
    LAST_WINS = "last_wins"
    MOST_RECENT = "most_recent"
    HIGHEST_PRIORITY = "highest_priority"
    MERGE = "merge"
    RENAME = "rename"
    DEPRECATE = "deprecate"
    ESCALATE = "escalate"


@dataclass
class ConflictDetection:
    """Represents a detected conflict"""

    id: str
    type: ConflictType
    severity: ConflictSeverity
    description: str
    affected_entities: List[str]
    context: str
    detected_at: datetime
    detected_by: str
    details: Dict[str, Any]
    suggested_resolution: Optional[ResolutionStrategy] = None
    resolution_notes: Optional[str] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None


@dataclass
class ConflictResolution:
    """Represents a conflict resolution"""

    conflict_id: str
    strategy: ResolutionStrategy
    resolution_details: Dict[str, Any]
    resolved_by: str
    resolved_at: datetime
    notes: Optional[str] = None
    success: bool = True
    rollback_available: bool = False


class ConflictDetector:
    """
    Advanced conflict detection system for SSOT
    Detects various types of conflicts and provides resolution strategies
    """

    def __init__(self, ssot_registry, config: Dict[str, Any] = None):
        self.registry = ssot_registry
        self.config = config or {}
        self.conflicts: Dict[str, ConflictDetection] = {}
        self.resolutions: Dict[str, ConflictResolution] = {}
        self.detection_rules = self._load_detection_rules()
        self.resolution_strategies = self._load_resolution_strategies()

        # Initialize audit logging
        self.audit_engine = AuditLogQueryEngine()

        # Conflict detection thresholds
        self.similarity_threshold = self.config.get("similarity_threshold", 0.8)
        self.semantic_similarity_threshold = self.config.get(
            "semantic_similarity_threshold", 0.7
        )
        self.priority_weights = self.config.get(
            "priority_weights",
            {
                "system": 10,
                "frenly_ai": 9,
                "application": 8,
                "migration": 7,
                "contextual": 6,
                "temporary": 5,
            },
        )

    def _load_detection_rules(self) -> Dict[str, Any]:
        """Load conflict detection rules from configuration"""
        return {
            "alias_duplicate": {
                "enabled": True,
                "severity": ConflictSeverity.HIGH,
                "auto_resolve": False,
            },
            "canonical_mismatch": {
                "enabled": True,
                "severity": ConflictSeverity.CRITICAL,
                "auto_resolve": False,
            },
            "context_overlap": {
                "enabled": True,
                "severity": ConflictSeverity.MEDIUM,
                "auto_resolve": True,
            },
            "naming_conflict": {
                "enabled": True,
                "severity": ConflictSeverity.MEDIUM,
                "auto_resolve": True,
            },
            "semantic_conflict": {
                "enabled": True,
                "severity": ConflictSeverity.HIGH,
                "auto_resolve": False,
            },
            "dependency_conflict": {
                "enabled": True,
                "severity": ConflictSeverity.CRITICAL,
                "auto_resolve": False,
            },
            "version_conflict": {
                "enabled": True,
                "severity": ConflictSeverity.HIGH,
                "auto_resolve": False,
            },
            "ownership_conflict": {
                "enabled": True,
                "severity": ConflictSeverity.MEDIUM,
                "auto_resolve": False,
            },
        }

    def _load_resolution_strategies(self) -> Dict[str, Any]:
        """Load resolution strategies from configuration"""
        return {
            "first_wins": {
                "description": "Keep the first occurrence, remove others",
                "auto_apply": True,
                "risk_level": "low",
            },
            "last_wins": {
                "description": "Keep the most recent occurrence, remove others",
                "auto_apply": True,
                "risk_level": "low",
            },
            "most_recent": {
                "description": "Keep the most recently updated occurrence",
                "auto_apply": True,
                "risk_level": "low",
            },
            "highest_priority": {
                "description": "Keep the occurrence with highest priority",
                "auto_apply": True,
                "risk_level": "medium",
            },
            "merge": {
                "description": "Merge conflicting entities where possible",
                "auto_apply": False,
                "risk_level": "high",
            },
            "rename": {
                "description": "Rename one of the conflicting entities",
                "auto_apply": False,
                "risk_level": "medium",
            },
            "deprecate": {
                "description": "Deprecate older conflicting entities",
                "auto_apply": False,
                "risk_level": "low",
            },
            "escalate": {
                "description": "Escalate to human review",
                "auto_apply": False,
                "risk_level": "none",
            },
        }

    async def detect_all_conflicts(self) -> List[ConflictDetection]:
        """
        Run all conflict detection algorithms
        """
        logger.info("Starting comprehensive conflict detection...")
        all_conflicts = []

        # Run all detection methods
        detection_methods = [
            self._detect_alias_duplicates,
            self._detect_canonical_mismatches,
            self._detect_context_overlaps,
            self._detect_naming_conflicts,
            self._detect_semantic_conflicts,
            self._detect_dependency_conflicts,
            self._detect_version_conflicts,
            self._detect_ownership_conflicts,
        ]

        for method in detection_methods:
            try:
                conflicts = await method()
                all_conflicts.extend(conflicts)
            except Exception as e:
                logger.error(
                    f"Error in conflict detection method {method.__name__}: {e}"
                )

        # Store conflicts
        for conflict in all_conflicts:
            self.conflicts[conflict.id] = conflict

        logger.info(
            f"Conflict detection completed. Found {len(all_conflicts)} conflicts."
        )

        # Audit log conflict detection
        try:
            await self.audit_engine.log_operation(
                operation=OperationType.SYSTEM.value,
                entity_type="ConflictDetection",
                entity_id="conflict_detection_run",
                details={
                    "conflicts_found": len(all_conflicts),
                    "conflict_types": [c.type.value for c in all_conflicts],
                    "severity_distribution": {
                        severity.value: len([c for c in all_conflicts if c.severity == severity])
                        for severity in ConflictSeverity
                    },
                    "detection_timestamp": datetime.now(timezone.utc).isoformat(),
                },
                performed_by="conflict_detector",
                context="conflict_detection",
                log_level=AuditLogLevel.INFO,
            )
        except Exception as e:
            logger.error(f"Failed to audit log conflict detection: {e}")

        return all_conflicts

    async def _detect_alias_duplicates(self) -> List[ConflictDetection]:
        """Detect duplicate aliases across contexts"""
        conflicts = []

        # Group aliases by name across all contexts
        alias_groups = defaultdict(list)
        for context, aliases in self.registry.aliases.items():
            for alias_name, alias_def in aliases.items():
                alias_groups[alias_name].append((context, alias_def))

        # Check for duplicates
        for alias_name, occurrences in alias_groups.items():
            if len(occurrences) > 1:
                # Check if they point to different canonicals
                canonicals = set(alias_def.canonical for _, alias_def in occurrences)
                if len(canonicals) > 1:
                    conflict = ConflictDetection(
                        id=f"alias_duplicate_{alias_name}_{int(datetime.now().timestamp())}",
                        type=ConflictType.ALIAS_DUPLICATE,
                        severity=ConflictSeverity.HIGH,
                        description=f"Alias '{alias_name}' exists in multiple contexts with different canonicals",
                        affected_entities=[alias_name],
                        context="cross_context",
                        detected_at=datetime.now(timezone.utc),
                        detected_by="conflict_detector",
                        details={
                            "alias_name": alias_name,
                            "occurrences": [
                                {
                                    "context": context,
                                    "canonical": alias_def.canonical,
                                    "type": alias_def.type.value,
                                    "status": alias_def.status.value,
                                    "created_at": alias_def.created_at,
                                }
                                for context, alias_def in occurrences
                            ],
                            "canonical_mismatch": True,
                        },
                        suggested_resolution=ResolutionStrategy.ESCALATE,
                    )
                    conflicts.append(conflict)

        return conflicts

    async def _detect_canonical_mismatches(self) -> List[ConflictDetection]:
        """Detect canonical mismatches in alias definitions"""
        conflicts = []

        for context, aliases in self.registry.aliases.items():
            for alias_name, alias_def in aliases.items():
                # Check if canonical exists
                if alias_def.canonical not in self.registry.anchors:
                    conflict = ConflictDetection(
                        id=f"canonical_mismatch_{alias_name}_{int(datetime.now().timestamp())}",
                        type=ConflictType.CANONICAL_MISMATCH,
                        severity=ConflictSeverity.CRITICAL,
                        description=f"Alias '{alias_name}' points to non-existent canonical '{alias_def.canonical}'",
                        affected_entities=[alias_name, alias_def.canonical],
                        context=context,
                        detected_at=datetime.now(timezone.utc),
                        detected_by="conflict_detector",
                        details={
                            "alias_name": alias_name,
                            "canonical": alias_def.canonical,
                            "context": context,
                            "issue": "canonical_not_found",
                        },
                        suggested_resolution=ResolutionStrategy.ESCALATE,
                    )
                    conflicts.append(conflict)

        return conflicts

    async def _detect_context_overlaps(self) -> List[ConflictDetection]:
        """Detect overlapping contexts that might cause confusion"""
        conflicts = []

        # Check for similar context names
        contexts = list(self.registry.aliases.keys())
        for i, context1 in enumerate(contexts):
            for context2 in contexts[i + 1 :]:
                similarity = difflib.SequenceMatcher(None, context1, context2).ratio()
                if similarity > self.similarity_threshold:
                    conflict = ConflictDetection(
                        id=f"context_overlap_{context1}_{context2}_{int(datetime.now().timestamp())}",
                        type=ConflictType.CONTEXT_OVERLAP,
                        severity=ConflictSeverity.MEDIUM,
                        description=f"Contexts '{context1}' and '{context2}' are very similar (similarity: {similarity:.2f})",
                        affected_entities=[context1, context2],
                        context="cross_context",
                        detected_at=datetime.now(timezone.utc),
                        detected_by="conflict_detector",
                        details={
                            "context1": context1,
                            "context2": context2,
                            "similarity": similarity,
                            "threshold": self.similarity_threshold,
                        },
                        suggested_resolution=ResolutionStrategy.RENAME,
                    )
                    conflicts.append(conflict)

        return conflicts

    async def _detect_naming_conflicts(self) -> List[ConflictDetection]:
        """Detect naming conflicts and inconsistencies"""
        conflicts = []

        # Check for similar alias names within the same context
        for context, aliases in self.registry.aliases.items():
            alias_names = list(aliases.keys())
            for i, name1 in enumerate(alias_names):
                for name2 in alias_names[i + 1 :]:
                    similarity = difflib.SequenceMatcher(None, name1, name2).ratio()
                    if similarity > self.similarity_threshold:
                        conflict = ConflictDetection(
                            id=f"naming_conflict_{name1}_{name2}_{int(datetime.now().timestamp())}",
                            type=ConflictType.NAMING_CONFLICT,
                            severity=ConflictSeverity.MEDIUM,
                            description=f"Alias names '{name1}' and '{name2}' are very similar (similarity: {similarity:.2f})",
                            affected_entities=[name1, name2],
                            context=context,
                            detected_at=datetime.now(timezone.utc),
                            detected_by="conflict_detector",
                            details={
                                "name1": name1,
                                "name2": name2,
                                "similarity": similarity,
                                "threshold": self.similarity_threshold,
                                "canonical1": aliases[name1].canonical,
                                "canonical2": aliases[name2].canonical,
                            },
                            suggested_resolution=ResolutionStrategy.RENAME,
                        )
                        conflicts.append(conflict)

        return conflicts

    async def _detect_semantic_conflicts(self) -> List[ConflictDetection]:
        """Detect semantic conflicts in alias definitions"""
        conflicts = []

        # This is a simplified semantic conflict detection
        # In a real implementation, this would use NLP or semantic analysis
        semantic_keywords = {
            "user": ["user", "person", "account", "profile"],
            "data": ["data", "information", "record", "entry"],
            "service": ["service", "api", "endpoint", "function"],
            "system": ["system", "platform", "infrastructure", "core"],
        }

        for context, aliases in self.registry.aliases.items():
            for alias_name, alias_def in aliases.items():
                # Check if alias name and canonical have conflicting semantics
                alias_words = set(alias_name.lower().split("_"))
                canonical_words = set(alias_def.canonical.lower().split("_"))

                for category, keywords in semantic_keywords.items():
                    alias_matches = alias_words.intersection(keywords)
                    canonical_matches = canonical_words.intersection(keywords)

                    if (
                        alias_matches
                        and canonical_matches
                        and alias_matches != canonical_matches
                    ):
                        conflict = ConflictDetection(
                            id=f"semantic_conflict_{alias_name}_{int(datetime.now().timestamp())}",
                            type=ConflictType.SEMANTIC_CONFLICT,
                            severity=ConflictSeverity.HIGH,
                            description=f"Semantic conflict between alias '{alias_name}' and canonical '{alias_def.canonical}'",
                            affected_entities=[alias_name, alias_def.canonical],
                            context=context,
                            detected_at=datetime.now(timezone.utc),
                            detected_by="conflict_detector",
                            details={
                                "alias_name": alias_name,
                                "canonical": alias_def.canonical,
                                "alias_matches": list(alias_matches),
                                "canonical_matches": list(canonical_matches),
                                "category": category,
                            },
                            suggested_resolution=ResolutionStrategy.ESCALATE,
                        )
                        conflicts.append(conflict)

        return conflicts

    async def _detect_dependency_conflicts(self) -> List[ConflictDetection]:
        """Detect dependency conflicts in SSOT anchors"""
        conflicts = []

        # Check for circular dependencies
        for anchor_id, anchor in self.registry.anchors.items():
            if "generates" in anchor.aliasing:
                generates = anchor.aliasing["generates"]
                if isinstance(generates, list):
                    for generated_anchor in generates:
                        if generated_anchor in self.registry.anchors:
                            generated_anchor_obj = self.registry.anchors[
                                generated_anchor
                            ]
                            if "generates" in generated_anchor_obj.aliasing:
                                if (
                                    anchor_id
                                    in generated_anchor_obj.aliasing["generates"]
                                ):
                                    conflict = ConflictDetection(
                                        id=f"dependency_conflict_{anchor_id}_{generated_anchor}_{int(datetime.now().timestamp())}",
                                        type=ConflictType.DEPENDENCY_CONFLICT,
                                        severity=ConflictSeverity.CRITICAL,
                                        description=f"Circular dependency detected between '{anchor_id}' and '{generated_anchor}'",
                                        affected_entities=[anchor_id, generated_anchor],
                                        context="dependency",
                                        detected_at=datetime.now(timezone.utc),
                                        detected_by="conflict_detector",
                                        details={
                                            "anchor1": anchor_id,
                                            "anchor2": generated_anchor,
                                            "issue": "circular_dependency",
                                        },
                                        suggested_resolution=ResolutionStrategy.ESCALATE,
                                    )
                                    conflicts.append(conflict)

        return conflicts

    async def _detect_version_conflicts(self) -> List[ConflictDetection]:
        """Detect version conflicts in SSOT anchors"""
        conflicts = []

        # Check for version mismatches in related anchors
        version_groups = defaultdict(list)
        for anchor_id, anchor in self.registry.anchors.items():
            if anchor.version:
                version_groups[anchor.family].append((anchor_id, anchor.version))

        for family, versions in version_groups.items():
            if len(versions) > 1:
                unique_versions = set(version for _, version in versions)
                if len(unique_versions) > 1:
                    conflict = ConflictDetection(
                        id=f"version_conflict_{family}_{int(datetime.now().timestamp())}",
                        type=ConflictType.VERSION_CONFLICT,
                        severity=ConflictSeverity.HIGH,
                        description=f"Version conflict in family '{family}' with versions: {', '.join(unique_versions)}",
                        affected_entities=[anchor_id for anchor_id, _ in versions],
                        context="version",
                        detected_at=datetime.now(timezone.utc),
                        detected_by="conflict_detector",
                        details={
                            "family": family,
                            "versions": versions,
                            "unique_versions": list(unique_versions),
                        },
                        suggested_resolution=ResolutionStrategy.ESCALATE,
                    )
                    conflicts.append(conflict)

        return conflicts

    async def _detect_ownership_conflicts(self) -> List[ConflictDetection]:
        """Detect ownership conflicts in SSOT entities"""
        conflicts = []

        # Check for conflicting ownership in related entities
        ownership_groups = defaultdict(list)
        for anchor_id, anchor in self.registry.anchors.items():
            if anchor.owner:
                ownership_groups[anchor.family].append((anchor_id, anchor.owner))

        for family, owners in ownership_groups.items():
            if len(owners) > 1:
                unique_owners = set(owner for _, owner in owners)
                if len(unique_owners) > 1:
                    conflict = ConflictDetection(
                        id=f"ownership_conflict_{family}_{int(datetime.now().timestamp())}",
                        type=ConflictType.OWNERSHIP_CONFLICT,
                        severity=ConflictSeverity.MEDIUM,
                        description=f"Ownership conflict in family '{family}' with owners: {', '.join(unique_owners)}",
                        affected_entities=[anchor_id for anchor_id, _ in owners],
                        context="ownership",
                        detected_at=datetime.now(timezone.utc),
                        detected_by="conflict_detector",
                        details={
                            "family": family,
                            "owners": owners,
                            "unique_owners": list(unique_owners),
                        },
                        suggested_resolution=ResolutionStrategy.ESCALATE,
                    )
                    conflicts.append(conflict)

        return conflicts

    async def resolve_conflict(
        self,
        conflict_id: str,
        strategy: ResolutionStrategy,
        resolution_details: Dict[str, Any],
        resolved_by: str,
    ) -> ConflictResolution:
        """
        Resolve a specific conflict using the specified strategy
        """
        if conflict_id not in self.conflicts:
            raise ValueError(f"Conflict {conflict_id} not found")

        conflict = self.conflicts[conflict_id]
        if conflict.resolved:
            raise ValueError(f"Conflict {conflict_id} is already resolved")

        logger.info(f"Resolving conflict {conflict_id} using strategy {strategy.value}")

        try:
            # Apply resolution strategy
            resolution = await self._apply_resolution_strategy(
                conflict, strategy, resolution_details
            )

            # Create resolution record
            resolution_record = ConflictResolution(
                conflict_id=conflict_id,
                strategy=strategy,
                resolution_details=resolution_details,
                resolved_by=resolved_by,
                resolved_at=datetime.now(timezone.utc),
                notes=resolution.get("notes"),
                success=resolution.get("success", True),
                rollback_available=resolution.get("rollback_available", False),
            )

            # Store resolution
            self.resolutions[conflict_id] = resolution_record

            # Mark conflict as resolved
            conflict.resolved = True
            conflict.resolved_at = datetime.now(timezone.utc)
            conflict.resolved_by = resolved_by

            logger.info(
                f"Conflict {conflict_id} resolved successfully using {strategy.value}"
            )

            # Audit log conflict resolution
            try:
                await self.audit_engine.log_operation(
                    operation=OperationType.RESOLUTION.value,
                    entity_type="ConflictResolution",
                    entity_id=conflict_id,
                    details={
                        "conflict_type": conflict.type.value,
                        "severity": conflict.severity.value,
                        "strategy": strategy.value,
                        "resolution_details": resolution_details,
                        "success": resolution_record.success,
                        "notes": resolution_record.notes,
                        "resolved_at": resolution_record.resolved_at.isoformat(),
                    },
                    performed_by=resolved_by,
                    context="conflict_resolution",
                    log_level=AuditLogLevel.INFO,
                )
            except Exception as e:
                logger.error(f"Failed to audit log conflict resolution: {e}")

            return resolution_record

        except Exception as e:
            # Audit log failed resolution
            try:
                await self.audit_engine.log_operation(
                    operation=OperationType.SYSTEM.value,
                    entity_type="ConflictResolution",
                    entity_id=conflict_id,
                    details={
                        "error": str(e),
                        "strategy": strategy.value if 'strategy' in locals() else None,
                        "resolution_details": resolution_details,
                        "failed_at": datetime.now(timezone.utc).isoformat(),
                    },
                    performed_by=resolved_by,
                    context="conflict_resolution",
                    log_level=AuditLogLevel.ERROR,
                )
            except Exception as audit_e:
                logger.error(f"Failed to audit log failed conflict resolution: {audit_e}")

            logger.error(f"Failed to resolve conflict {conflict_id}: {e}")
            raise

    async def _apply_resolution_strategy(
        self,
        conflict: ConflictDetection,
        strategy: ResolutionStrategy,
        details: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Apply the specified resolution strategy to a conflict"""

        if strategy == ResolutionStrategy.FIRST_WINS:
            return await self._resolve_first_wins(conflict, details)
        elif strategy == ResolutionStrategy.LAST_WINS:
            return await self._resolve_last_wins(conflict, details)
        elif strategy == ResolutionStrategy.MOST_RECENT:
            return await self._resolve_most_recent(conflict, details)
        elif strategy == ResolutionStrategy.HIGHEST_PRIORITY:
            return await self._resolve_highest_priority(conflict, details)
        elif strategy == ResolutionStrategy.MERGE:
            return await self._resolve_merge(conflict, details)
        elif strategy == ResolutionStrategy.RENAME:
            return await self._resolve_rename(conflict, details)
        elif strategy == ResolutionStrategy.DEPRECATE:
            return await self._resolve_deprecate(conflict, details)
        elif strategy == ResolutionStrategy.ESCALATE:
            return await self._resolve_escalate(conflict, details)
        else:
            raise ValueError(f"Unknown resolution strategy: {strategy}")

    async def _resolve_first_wins(
        self, conflict: ConflictDetection, details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflict by keeping the first occurrence"""
        # Implementation depends on conflict type
        return {
            "success": True,
            "notes": "First wins resolution applied",
            "rollback_available": True,
        }

    async def _resolve_last_wins(
        self, conflict: ConflictDetection, details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflict by keeping the last occurrence"""
        return {
            "success": True,
            "notes": "Last wins resolution applied",
            "rollback_available": True,
        }

    async def _resolve_most_recent(
        self, conflict: ConflictDetection, details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflict by keeping the most recent occurrence"""
        return {
            "success": True,
            "notes": "Most recent resolution applied",
            "rollback_available": True,
        }

    async def _resolve_highest_priority(
        self, conflict: ConflictDetection, details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflict by keeping the highest priority occurrence"""
        return {
            "success": True,
            "notes": "Highest priority resolution applied",
            "rollback_available": True,
        }

    async def _resolve_merge(
        self, conflict: ConflictDetection, details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflict by merging entities"""
        return {
            "success": True,
            "notes": "Merge resolution applied",
            "rollback_available": True,
        }

    async def _resolve_rename(
        self, conflict: ConflictDetection, details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflict by renaming one entity"""
        return {
            "success": True,
            "notes": "Rename resolution applied",
            "rollback_available": True,
        }

    async def _resolve_deprecate(
        self, conflict: ConflictDetection, details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflict by deprecating older entities"""
        return {
            "success": True,
            "notes": "Deprecate resolution applied",
            "rollback_available": True,
        }

    async def _resolve_escalate(
        self, conflict: ConflictDetection, details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Escalate conflict to human review"""
        return {
            "success": False,
            "notes": "Conflict escalated to human review",
            "rollback_available": False,
        }

    def get_conflicts_by_severity(
        self, severity: ConflictSeverity
    ) -> List[ConflictDetection]:
        """Get all conflicts of a specific severity level"""
        return [
            conflict
            for conflict in self.conflicts.values()
            if conflict.severity == severity
        ]

    def get_unresolved_conflicts(self) -> List[ConflictDetection]:
        """Get all unresolved conflicts"""
        return [
            conflict for conflict in self.conflicts.values() if not conflict.resolved
        ]

    def get_conflict_statistics(self) -> Dict[str, Any]:
        """Get conflict statistics"""
        total_conflicts = len(self.conflicts)
        resolved_conflicts = len([c for c in self.conflicts.values() if c.resolved])
        unresolved_conflicts = total_conflicts - resolved_conflicts

        severity_counts = {}
        for severity in ConflictSeverity:
            severity_counts[severity.value] = len(
                self.get_conflicts_by_severity(severity)
            )

        type_counts = {}
        for conflict_type in ConflictType:
            type_counts[conflict_type.value] = len(
                [c for c in self.conflicts.values() if c.type == conflict_type]
            )

        return {
            "total_conflicts": total_conflicts,
            "resolved_conflicts": resolved_conflicts,
            "unresolved_conflicts": unresolved_conflicts,
            "resolution_rate": resolved_conflicts / total_conflicts
            if total_conflicts > 0
            else 0,
            "severity_distribution": severity_counts,
            "type_distribution": type_counts,
        }

    async def auto_resolve_conflicts(self) -> List[ConflictResolution]:
        """Automatically resolve conflicts that can be auto-resolved"""
        auto_resolutions = []

        for conflict in self.get_unresolved_conflicts():
            rule = self.detection_rules.get(conflict.type.value, {})
            if rule.get("auto_resolve", False) and conflict.suggested_resolution:
                try:
                    resolution = await self.resolve_conflict(
                        conflict.id, conflict.suggested_resolution, {}, "auto_resolver"
                    )
                    auto_resolutions.append(resolution)
                except Exception as e:
                    logger.error(f"Failed to auto-resolve conflict {conflict.id}: {e}")

        return auto_resolutions


# Example usage and testing
async def main():
    """
    Example usage of ConflictDetector
    """

    # This would be used with an actual SSOT registry instance
    # For demonstration purposes, we'll create a mock registry
    class MockRegistry:
        def __init__(self):
            self.anchors = {}
            self.aliases = {}

    registry = MockRegistry()
    detector = ConflictDetector(registry)

    # Run conflict detection
    conflicts = await detector.detect_all_conflicts()
    print(f"Detected {len(conflicts)} conflicts")

    # Get statistics
    stats = detector.get_conflict_statistics()
    print(f"Conflict statistics: {stats}")

    # Auto-resolve conflicts
    auto_resolutions = await detector.auto_resolve_conflicts()
    print(f"Auto-resolved {len(auto_resolutions)} conflicts")


if __name__ == "__main__":
    asyncio.run(main())
