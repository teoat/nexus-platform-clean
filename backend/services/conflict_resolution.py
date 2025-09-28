# NEXUS SSOT Conflict Detection and Resolution Service

"""
This module handles conflict detection and resolution for API aliases in the SSOT system.
It ensures alias uniqueness, detects conflicts, and provides resolution strategies.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from backend.database import get_db_session
from backend.models import Alias

logger = logging.getLogger(__name__)


class ConflictDetector:
    def __init__(self):
        self.db_session = get_db_session()

    def detect_conflicts(self, alias_name: str, context: str) -> List[Dict]:
        """
        Detect conflicts for a given alias in a specific context.

        Args:
            alias_name (str): The alias name to check
            context (str): The context (frontend, backend, system)

        Returns:
            List[Dict]: List of conflicting aliases
        """
        conflicts = []
        try:
            existing_aliases = (
                self.db_session.query(Alias)
                .filter(Alias.alias == alias_name, Alias.context == context)
                .all()
            )

            for alias in existing_aliases:
                conflicts.append(
                    {
                        "id": alias.id,
                        "alias": alias.alias,
                        "context": alias.context,
                        "canonical": alias.canonical,
                        "created_at": alias.created_at.isoformat(),
                    }
                )

            logger.info(
                f"Detected {len(conflicts)} conflicts for alias '{alias_name}' in context '{context}'"
            )
        except Exception as e:
            logger.error(f"Error detecting conflicts: {str(e)}")
        return conflicts

    def resolve_conflict(self, conflict_id: int, resolution_strategy: str) -> bool:
        """
        Resolve a conflict using a specified strategy.

        Args:
            conflict_id (int): The ID of the conflicting alias
            resolution_strategy (str): Strategy ('merge', 'override', 'archive')

        Returns:
            bool: True if resolved successfully
        """
        try:
            alias = self.db_session.query(Alias).filter(Alias.id == conflict_id).first()
            if not alias:
                logger.warning(f"Alias with ID {conflict_id} not found")
                return False

            if resolution_strategy == "merge":
                # Merge with existing canonical if different
                if alias.canonical != "merged":
                    alias.canonical = "merged"
                    alias.updated_at = datetime.utcnow()
                    self.db_session.commit()
                    logger.info(f"Merged alias {conflict_id}")

            elif resolution_strategy == "override":
                # Override the existing alias
                alias.canonical = "overridden"
                alias.updated_at = datetime.utcnow()
                self.db_session.commit()
                logger.info(f"Overrode alias {conflict_id}")

            elif resolution_strategy == "archive":
                # Archive the alias
                alias.is_active = False
                alias.updated_at = datetime.utcnow()
                self.db_session.commit()
                logger.info(f"Archived alias {conflict_id}")

            else:
                logger.error(f"Unknown resolution strategy: {resolution_strategy}")
                return False

            return True
        except Exception as e:
            logger.error(f"Error resolving conflict: {str(e)}")
            self.db_session.rollback()
            return False

    def check_alias_uniqueness(self, alias_name: str, context: str) -> bool:
        """
        Check if an alias is unique in the given context.

        Args:
            alias_name (str): The alias name
            context (str): The context

        Returns:
            bool: True if unique
        """
        conflicts = self.detect_conflicts(alias_name, context)
        return len(conflicts) == 0

    def get_conflict_report(self) -> Dict:
        """
        Generate a report of all conflicts in the system.

        Returns:
            Dict: Conflict report
        """
        try:
            all_aliases = self.db_session.query(Alias).all()
            conflicts = {}

            for alias in all_aliases:
                key = f"{alias.alias}_{alias.context}"
                if key not in conflicts:
                    conflicts[key] = []
                conflicts[key].append(
                    {
                        "id": alias.id,
                        "canonical": alias.canonical,
                        "created_at": alias.created_at.isoformat(),
                    }
                )

            # Filter to only conflicts (multiple entries)
            conflict_report = {k: v for k, v in conflicts.items() if len(v) > 1}
            logger.info(
                f"Generated conflict report with {len(conflict_report)} conflicts"
            )
            return conflict_report
        except Exception as e:
            logger.error(f"Error generating conflict report: {str(e)}")
            return {}


def main():
    detector = ConflictDetector()
    # Example usage
    conflicts = detector.detect_conflicts("user-profile", "frontend")
    print(f"Conflicts: {conflicts}")

    report = detector.get_conflict_report()
    print(f"Conflict Report: {report}")


if __name__ == "__main__":
    main()
