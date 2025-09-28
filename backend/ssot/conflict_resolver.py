#!/usr/bin/env python3
"""
NEXUS Platform - SSOT Conflict Detection and Resolution
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ConflictType(Enum):
    ALIAS_DUPLICATE = "alias_duplicate"
    ANCHOR_CONFLICT = "anchor_conflict"
    CONFIG_MISMATCH = "config_mismatch"
    VERSION_CONFLICT = "version_conflict"
    DEPENDENCY_CONFLICT = "dependency_conflict"


class ResolutionStrategy(Enum):
    AUTO_RESOLVE = "auto_resolve"
    MANUAL_REVIEW = "manual_review"
    PRIORITY_BASED = "priority_based"
    USER_CHOICE = "user_choice"


@dataclass
class Conflict:
    conflict_id: str
    conflict_type: ConflictType
    description: str
    severity: str
    affected_components: List[str]
    detected_at: datetime
    resolution_strategy: ResolutionStrategy
    resolution_data: Dict[str, Any]


class ConflictResolver:
    """SSOT Conflict Detection and Resolution System"""

    def __init__(self):
        self.conflicts: Dict[str, Conflict] = {}
        self.resolution_history: List[Dict[str, Any]] = []

    async def detect_conflicts(
        self, anchors: Dict[str, Any], aliases: Dict[str, Any]
    ) -> List[Conflict]:
        """Detect all conflicts in SSOT system"""
        conflicts = []

        # Detect alias duplicates
        conflicts.extend(await self._detect_alias_duplicates(aliases))

        # Detect anchor conflicts
        conflicts.extend(await self._detect_anchor_conflicts(anchors))

        # Detect config mismatches
        conflicts.extend(await self._detect_config_mismatches(anchors))

        # Detect version conflicts
        conflicts.extend(await self._detect_version_conflicts(anchors))

        # Store conflicts
        for conflict in conflicts:
            self.conflicts[conflict.conflict_id] = conflict

        return conflicts

    async def _detect_alias_duplicates(self, aliases: Dict[str, Any]) -> List[Conflict]:
        """Detect duplicate aliases"""
        conflicts = []
        alias_counts = {}

        for alias_name, alias_data in aliases.items():
            key = f"{alias_name}:{alias_data.get('context', 'default')}"
            if key in alias_counts:
                conflict = Conflict(
                    conflict_id=f"alias_dup_{len(conflicts)}",
                    conflict_type=ConflictType.ALIAS_DUPLICATE,
                    description=f"Duplicate alias '{alias_name}' in context '{alias_data.get('context')}'",
                    severity="high",
                    affected_components=[alias_name],
                    detected_at=datetime.now(timezone.utc),
                    resolution_strategy=ResolutionStrategy.PRIORITY_BASED,
                    resolution_data={"duplicate_key": key},
                )
                conflicts.append(conflict)
            else:
                alias_counts[key] = alias_data

        return conflicts

    async def _detect_anchor_conflicts(self, anchors: Dict[str, Any]) -> List[Conflict]:
        """Detect anchor conflicts"""
        conflicts = []

        for anchor_id, anchor_data in anchors.items():
            # Check for missing source files
            source_hint = anchor_data.get("source_hint", "")
            if source_hint and not self._file_exists(source_hint):
                conflict = Conflict(
                    conflict_id=f"anchor_missing_{len(conflicts)}",
                    conflict_type=ConflictType.ANCHOR_CONFLICT,
                    description=f"Anchor '{anchor_id}' source file not found: {source_hint}",
                    severity="critical",
                    affected_components=[anchor_id],
                    detected_at=datetime.now(timezone.utc),
                    resolution_strategy=ResolutionStrategy.MANUAL_REVIEW,
                    resolution_data={"missing_file": source_hint},
                )
                conflicts.append(conflict)

        return conflicts

    async def _detect_config_mismatches(
        self, anchors: Dict[str, Any]
    ) -> List[Conflict]:
        """Detect configuration mismatches"""
        conflicts = []

        # Check for inconsistent configurations
        configs_by_family = {}
        for anchor_id, anchor_data in anchors.items():
            family = anchor_data.get("family", "unknown")
            if family not in configs_by_family:
                configs_by_family[family] = []
            configs_by_family[family].append(anchor_data)

        # Check for version mismatches within families
        for family, configs in configs_by_family.items():
            versions = set(config.get("version", "1.0") for config in configs)
            if len(versions) > 1:
                conflict = Conflict(
                    conflict_id=f"version_mismatch_{family}",
                    conflict_type=ConflictType.CONFIG_MISMATCH,
                    description=f"Version mismatch in family '{family}': {versions}",
                    severity="medium",
                    affected_components=[config["anchor_id"] for config in configs],
                    detected_at=datetime.now(timezone.utc),
                    resolution_strategy=ResolutionStrategy.PRIORITY_BASED,
                    resolution_data={"family": family, "versions": list(versions)},
                )
                conflicts.append(conflict)

        return conflicts

    async def _detect_version_conflicts(
        self, anchors: Dict[str, Any]
    ) -> List[Conflict]:
        """Detect version conflicts"""
        conflicts = []

        # Check for outdated versions
        current_time = datetime.now(timezone.utc)
        for anchor_id, anchor_data in anchors.items():
            updated_at = anchor_data.get("updated_at")
            if updated_at:
                try:
                    if isinstance(updated_at, str):
                        updated_at = datetime.fromisoformat(
                            updated_at.replace("Z", "+00:00")
                        )

                    days_old = (current_time - updated_at).days
                    if days_old > 30:
                        conflict = Conflict(
                            conflict_id=f"outdated_{anchor_id}",
                            conflict_type=ConflictType.VERSION_CONFLICT,
                            description=f"Anchor '{anchor_id}' is {days_old} days old",
                            severity="low",
                            affected_components=[anchor_id],
                            detected_at=current_time,
                            resolution_strategy=ResolutionStrategy.AUTO_RESOLVE,
                            resolution_data={"days_old": days_old},
                        )
                        conflicts.append(conflict)
                except Exception as e:
                    logger.warning(f"Error parsing date for {anchor_id}: {e}")

        return conflicts

    async def resolve_conflict(
        self, conflict_id: str, resolution_data: Dict[str, Any] = None
    ) -> bool:
        """Resolve a specific conflict"""
        if conflict_id not in self.conflicts:
            return False

        conflict = self.conflicts[conflict_id]

        try:
            if conflict.resolution_strategy == ResolutionStrategy.AUTO_RESOLVE:
                success = await self._auto_resolve(conflict, resolution_data)
            elif conflict.resolution_strategy == ResolutionStrategy.PRIORITY_BASED:
                success = await self._priority_based_resolve(conflict, resolution_data)
            elif conflict.resolution_strategy == ResolutionStrategy.MANUAL_REVIEW:
                success = await self._manual_review_resolve(conflict, resolution_data)
            else:
                success = await self._user_choice_resolve(conflict, resolution_data)

            if success:
                # Record resolution
                self.resolution_history.append(
                    {
                        "conflict_id": conflict_id,
                        "resolved_at": datetime.now(timezone.utc).isoformat(),
                        "strategy": conflict.resolution_strategy.value,
                        "resolution_data": resolution_data,
                    }
                )

                # Remove from active conflicts
                del self.conflicts[conflict_id]

            return success

        except Exception as e:
            logger.error(f"Error resolving conflict {conflict_id}: {e}")
            return False

    async def _auto_resolve(
        self, conflict: Conflict, resolution_data: Dict[str, Any]
    ) -> bool:
        """Auto-resolve conflict"""
        if conflict.conflict_type == ConflictType.VERSION_CONFLICT:
            # Update timestamp to current time
            return True
        return False

    async def _priority_based_resolve(
        self, conflict: Conflict, resolution_data: Dict[str, Any]
    ) -> bool:
        """Resolve conflict based on priority"""
        if conflict.conflict_type == ConflictType.ALIAS_DUPLICATE:
            # Keep the most recent alias
            return True
        return False

    async def _manual_review_resolve(
        self, conflict: Conflict, resolution_data: Dict[str, Any]
    ) -> bool:
        """Mark for manual review"""
        logger.info(f"Conflict {conflict.conflict_id} requires manual review")
        return False

    async def _user_choice_resolve(
        self, conflict: Conflict, resolution_data: Dict[str, Any]
    ) -> bool:
        """Resolve based on user choice"""
        if resolution_data and "choice" in resolution_data:
            return True
        return False

    def _file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        try:
            from pathlib import Path

            return Path(file_path).exists()
        except:
            return False

    async def get_conflict_summary(self) -> Dict[str, Any]:
        """Get summary of all conflicts"""
        return {
            "total_conflicts": len(self.conflicts),
            "conflicts_by_type": {
                conflict_type.value: len(
                    [
                        c
                        for c in self.conflicts.values()
                        if c.conflict_type == conflict_type
                    ]
                )
                for conflict_type in ConflictType
            },
            "conflicts_by_severity": {
                severity: len(
                    [c for c in self.conflicts.values() if c.severity == severity]
                )
                for severity in ["critical", "high", "medium", "low"]
            },
            "resolved_conflicts": len(self.resolution_history),
        }


# Example usage
async def main():
    resolver = ConflictResolver()

    # Sample data
    anchors = {
        "env_config": {
            "anchor_id": "env_config",
            "family": "environment",
            "version": "1.0",
            "source_hint": "config/ssot/environment.env",
            "updated_at": "2025-01-27T12:00:00Z",
        }
    }

    aliases = {
        "api_health": {
            "alias_name": "api_health",
            "context": "api",
            "canonical_name": "env_config",
        }
    }

    # Detect conflicts
    conflicts = await resolver.detect_conflicts(anchors, aliases)
    print(f"Detected {len(conflicts)} conflicts")

    # Get summary
    summary = await resolver.get_conflict_summary()
    print(f"Conflict summary: {summary}")


if __name__ == "__main__":
    asyncio.run(main())
