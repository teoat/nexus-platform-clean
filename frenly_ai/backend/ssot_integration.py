#!/usr/bin/env python3
"""
NEXUS Platform - SSOT Integration Layer
Bridge between Frenly AI and SSOT system
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


class SSOTIntegration:
    """SSOT Integration Layer for Frenly AI"""

    def __init__(self, config_path: str = "config/ssot/"):
        self.config_path = Path(config_path)
        self.registry_cache = {}
        self.alias_cache = {}

    async def get_ssot_anchor(self, anchor_id: str) -> Optional[Dict[str, Any]]:
        """Get SSOT anchor by ID"""
        try:
            if anchor_id in self.registry_cache:
                return self.registry_cache[anchor_id]

            # Load from file system
            anchor_file = self.config_path / f"{anchor_id}.yaml"
            if anchor_file.exists():
                with open(anchor_file, "r") as f:
                    anchor_data = yaml.safe_load(f)
                    self.registry_cache[anchor_id] = anchor_data
                    return anchor_data

                    return None
        except Exception as e:
            logger.error(f"Error getting SSOT anchor {anchor_id}: {e}")
            return None

    async def resolve_alias(
        self, alias_name: str, context: str = None
    ) -> Optional[Dict[str, Any]]:
        """Resolve alias to canonical name"""
        try:
            cache_key = f"{alias_name}:{context or 'default'}"
            if cache_key in self.alias_cache:
                return self.alias_cache[cache_key]

            # Load aliases from configuration
            aliases_file = self.config_path / "aliases.json"
            if aliases_file.exists():
                with open(aliases_file, "r") as f:
                    aliases = json.load(f)

                for alias in aliases:
                    if (
                        alias.get("alias_name") == alias_name
                        and alias.get("is_active", True)
                        and (not context or alias.get("context") == context)
                    ):
                        result = {
                            "canonical_name": alias.get("canonical_name"),
                            "context": alias.get("context"),
                            "description": alias.get("description"),
                        }
                        self.alias_cache[cache_key] = result
                        return result

                    return None
        except Exception as e:
            logger.error(f"Error resolving alias {alias_name}: {e}")
            return None

    async def validate_ssot_consistency(self) -> Dict[str, Any]:
        """Validate SSOT consistency across all anchors"""
        validation_results = {"valid": True, "issues": [], "recommendations": []}

        try:
            # Check for missing anchor files
            expected_anchors = [
                "env_config",
                "docker_config",
                "k8s_config",
                "monitoring_config",
            ]

            for anchor_id in expected_anchors:
                anchor_file = self.config_path / f"{anchor_id}.yaml"
                if not anchor_file.exists():
                    validation_results["valid"] = False
                    validation_results["issues"].append(
                        f"Missing anchor file: {anchor_file}"
                    )

            # Check alias consistency
            aliases_file = self.config_path / "aliases.json"
            if aliases_file.exists():
                with open(aliases_file, "r") as f:
                    aliases = json.load(f)

                for alias in aliases:
                    if alias.get("is_active", True):
                        canonical_name = alias.get("canonical_name")
                        if canonical_name not in expected_anchors:
                            validation_results["issues"].append(
                                f"Alias {alias.get('alias_name')} references unknown anchor: {canonical_name}"
                            )

            return validation_results

        except Exception as e:
            logger.error(f"Error validating SSOT consistency: {e}")
            validation_results["valid"] = False
            validation_results["issues"].append(f"Validation error: {e}")
            return validation_results

    async def get_ssot_status(self) -> Dict[str, Any]:
        """Get current SSOT system status"""
        try:
            status = {
                "anchors_count": len(self.registry_cache),
                "aliases_count": len(self.alias_cache),
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "config_path": str(self.config_path),
                "anchors": list(self.registry_cache.keys()),
                "aliases": list(self.alias_cache.keys()),
            }

            return status
        except Exception as e:
            logger.error(f"Error getting SSOT status: {e}")
            return {"error": str(e)}


# Example usage
async def main():
    integration = SSOTIntegration()

    # Test anchor retrieval
    anchor = await integration.get_ssot_anchor("env_config")
    print(f"Anchor: {anchor}")

    # Test alias resolution
    alias = await integration.resolve_alias("api_health", "api")
    print(f"Alias: {alias}")

    # Test validation
    validation = await integration.validate_ssot_consistency()
    print(f"Validation: {validation}")

    # Test status
    status = await integration.get_ssot_status()
    print(f"Status: {status}")


if __name__ == "__main__":
    asyncio.run(main())
