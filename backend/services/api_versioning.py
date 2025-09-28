#!/usr/bin/env python3
"""
NEXUS Platform - API Versioning Service
Manages API versioning and backward compatibility
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class APIVersion(Enum):
    """API Version enumeration"""

    V1 = "v1"
    V2 = "v2"
    V3 = "v3"


class CompatibilityMode(Enum):
    """API compatibility modes"""

    STRICT = "strict"  # Only exact version matches
    COMPATIBLE = "compatible"  # Allow compatible versions
    LEGACY = "legacy"  # Support legacy versions with warnings


class VersionEndpoint:
    """Represents a versioned API endpoint"""

    def __init__(
        self,
        path: str,
        methods: List[str],
        version: APIVersion,
        handler: Callable,
        deprecated: bool = False,
        deprecated_in: Optional[APIVersion] = None,
        removed_in: Optional[APIVersion] = None,
        alternatives: Optional[List[str]] = None,
    ):
        self.path = path
        self.methods = methods
        self.version = version
        self.handler = handler
        self.deprecated = deprecated
        self.deprecated_in = deprecated_in
        self.removed_in = removed_in
        self.alternatives = alternatives or []
        self.created_at = datetime.now(timezone.utc)
        self.last_used = None


class APIVersioningService:
    """Service for managing API versioning and backward compatibility"""

    def __init__(self):
        self.endpoints: Dict[str, VersionEndpoint] = {}
        self.version_mappings: Dict[str, Dict[str, str]] = {}
        self.compatibility_mode = CompatibilityMode.COMPATIBLE
        self.deprecation_warnings_enabled = True
        self.version_stats: Dict[str, Dict[str, Any]] = {}

        # Initialize version mappings for backward compatibility
        self._initialize_version_mappings()

    def _initialize_version_mappings(self):
        """Initialize version compatibility mappings"""
        # v1 to v3 mappings
        self.version_mappings["v1"] = {
            "/api/v1/ssot/aliases": "/api/v3/ssot/aliases",
            "/api/v1/ssot/resolve": "/api/v3/ssot/resolve",
        }

        # v2 to v3 mappings (if v2 existed)
        self.version_mappings["v2"] = {
            "/api/v2/auth/login": "/api/v3/auth/login",
            "/api/v2/users/profile": "/api/v3/users/profile",
        }

    def register_endpoint(
        self,
        path: str,
        methods: List[str],
        version: APIVersion,
        handler: Callable,
        deprecated: bool = False,
        deprecated_in: Optional[APIVersion] = None,
        removed_in: Optional[APIVersion] = None,
        alternatives: Optional[List[str]] = None,
    ) -> None:
        """Register a versioned API endpoint"""
        endpoint_key = f"{version.value}:{path}"

        endpoint = VersionEndpoint(
            path=path,
            methods=methods,
            version=version,
            handler=handler,
            deprecated=deprecated,
            deprecated_in=deprecated_in,
            removed_in=removed_in,
            alternatives=alternatives,
        )

        self.endpoints[endpoint_key] = endpoint
        logger.info(f"Registered endpoint: {endpoint_key}")

    def resolve_endpoint(
        self, path: str, method: str, requested_version: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Resolve an endpoint with version compatibility"""
        # Try exact version match first
        if requested_version:
            endpoint_key = f"{requested_version}:{path}"
            if endpoint_key in self.endpoints:
                endpoint = self.endpoints[endpoint_key]
                if method in endpoint.methods:
                    return self._create_resolution_result(
                        endpoint, requested_version, "exact"
                    )

        # Try compatibility mode resolution
        if self.compatibility_mode == CompatibilityMode.COMPATIBLE:
            compatible_endpoint = self._find_compatible_endpoint(
                path, method, requested_version
            )
            if compatible_endpoint:
                return self._create_resolution_result(
                    compatible_endpoint, requested_version, "compatible"
                )

        # Try legacy mode
        if self.compatibility_mode == CompatibilityMode.LEGACY:
            legacy_endpoint = self._find_legacy_endpoint(path, method)
            if legacy_endpoint:
                return self._create_resolution_result(
                    legacy_endpoint, requested_version, "legacy"
                )

        return None

    def _find_compatible_endpoint(
        self, path: str, method: str, requested_version: str
    ) -> Optional[VersionEndpoint]:
        """Find a compatible endpoint for the requested version"""
        # Check version mappings
        if requested_version in self.version_mappings:
            mappings = self.version_mappings[requested_version]
            if path in mappings:
                mapped_path = mappings[path]
                # Find the latest version of the mapped endpoint
                for version in [APIVersion.V3, APIVersion.V2, APIVersion.V1]:
                    endpoint_key = f"{version.value}:{mapped_path}"
                    if endpoint_key in self.endpoints:
                        endpoint = self.endpoints[endpoint_key]
                        if method in endpoint.methods and not endpoint.deprecated:
                            return endpoint

        # Find any non-deprecated endpoint with the same path
        for endpoint in self.endpoints.values():
            if (
                endpoint.path == path
                and method in endpoint.methods
                and not endpoint.deprecated
                and not endpoint.removed_in
            ):
                return endpoint

        return None

    def _find_legacy_endpoint(
        self, path: str, method: str
    ) -> Optional[VersionEndpoint]:
        """Find a legacy endpoint (may be deprecated)"""
        for endpoint in self.endpoints.values():
            if (
                endpoint.path == path
                and method in endpoint.methods
                and not endpoint.removed_in
            ):
                return endpoint

        return None

    def _create_resolution_result(
        self, endpoint: VersionEndpoint, requested_version: str, resolution_type: str
    ) -> Dict[str, Any]:
        """Create a resolution result dictionary"""
        result = {
            "endpoint": endpoint,
            "handler": endpoint.handler,
            "version": endpoint.version.value,
            "requested_version": requested_version,
            "resolution_type": resolution_type,
            "deprecated": endpoint.deprecated,
            "warnings": [],
        }

        # Update last used timestamp
        endpoint.last_used = datetime.now(timezone.utc)

        # Add deprecation warnings
        if endpoint.deprecated and self.deprecation_warnings_enabled:
            warning = f"Endpoint {endpoint.path} is deprecated"
            if endpoint.deprecated_in:
                warning += f" since version {endpoint.deprecated_in.value}"
            if endpoint.alternatives:
                warning += f". Use: {', '.join(endpoint.alternatives)}"
            result["warnings"].append(warning)

        # Add version compatibility warnings
        if (
            resolution_type == "compatible"
            and requested_version != endpoint.version.value
        ):
            result["warnings"].append(
                f"Requested version {requested_version} resolved to {endpoint.version.value} for compatibility"
            )

        return result

    def get_version_info(self) -> Dict[str, Any]:
        """Get comprehensive version information"""
        versions = {}
        for endpoint in self.endpoints.values():
            version_key = endpoint.version.value
            if version_key not in versions:
                versions[version_key] = {
                    "version": version_key,
                    "endpoints": [],
                    "deprecated_count": 0,
                    "total_count": 0,
                }

            endpoint_info = {
                "path": endpoint.path,
                "methods": endpoint.methods,
                "deprecated": endpoint.deprecated,
                "deprecated_in": endpoint.deprecated_in.value
                if endpoint.deprecated_in
                else None,
                "removed_in": endpoint.removed_in.value
                if endpoint.removed_in
                else None,
                "alternatives": endpoint.alternatives,
                "last_used": endpoint.last_used.isoformat()
                if endpoint.last_used
                else None,
            }

            versions[version_key]["endpoints"].append(endpoint_info)
            versions[version_key]["total_count"] += 1
            if endpoint.deprecated:
                versions[version_key]["deprecated_count"] += 1

        return {
            "versions": list(versions.values()),
            "compatibility_mode": self.compatibility_mode.value,
            "deprecation_warnings_enabled": self.deprecation_warnings_enabled,
            "total_endpoints": len(self.endpoints),
            "version_mappings": self.version_mappings,
        }

    def set_compatibility_mode(self, mode: CompatibilityMode) -> None:
        """Set the API compatibility mode"""
        self.compatibility_mode = mode
        logger.info(f"API compatibility mode set to: {mode.value}")

    def enable_deprecation_warnings(self, enabled: bool = True) -> None:
        """Enable or disable deprecation warnings"""
        self.deprecation_warnings_enabled = enabled
        logger.info(f"Deprecation warnings {'enabled' if enabled else 'disabled'}")

    def migrate_endpoint(
        self,
        old_path: str,
        old_version: APIVersion,
        new_path: str,
        new_version: APIVersion,
        migration_handler: Optional[Callable] = None,
    ) -> None:
        """Migrate an endpoint to a new version/path"""
        old_key = f"{old_version.value}:{old_path}"

        if old_key not in self.endpoints:
            logger.warning(f"Cannot migrate non-existent endpoint: {old_key}")
            return

        old_endpoint = self.endpoints[old_key]

        # Mark old endpoint as deprecated
        old_endpoint.deprecated = True
        old_endpoint.deprecated_in = new_version
        old_endpoint.alternatives = [f"{new_version.value}:{new_path}"]

        # Register new endpoint
        if migration_handler:
            self.register_endpoint(
                path=new_path,
                methods=old_endpoint.methods,
                version=new_version,
                handler=migration_handler,
            )

        # Update version mappings
        if old_version.value not in self.version_mappings:
            self.version_mappings[old_version.value] = {}
        self.version_mappings[old_version.value][old_path] = new_path

        logger.info(f"Migrated endpoint: {old_key} -> {new_version.value}:{new_path}")

    def validate_version_compatibility(self) -> Dict[str, Any]:
        """Validate version compatibility across all endpoints"""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "stats": {
                "total_endpoints": len(self.endpoints),
                "deprecated_endpoints": 0,
                "removed_endpoints": 0,
                "versions": set(),
            },
        }

        for endpoint in self.endpoints.values():
            validation_results["stats"]["versions"].add(endpoint.version.value)

            if endpoint.deprecated:
                validation_results["stats"]["deprecated_endpoints"] += 1

            if endpoint.removed_in:
                validation_results["stats"]["removed_endpoints"] += 1

            # Check for missing alternatives for deprecated endpoints
            if endpoint.deprecated and not endpoint.alternatives:
                validation_results["warnings"].append(
                    {
                        "type": "missing_alternatives",
                        "endpoint": f"{endpoint.version.value}:{endpoint.path}",
                        "message": "Deprecated endpoint missing alternative endpoints",
                    }
                )

            # Check for version consistency
            if (
                endpoint.deprecated_in
                and endpoint.version.value >= endpoint.deprecated_in.value
            ):
                validation_results["errors"].append(
                    {
                        "type": "version_inconsistency",
                        "endpoint": f"{endpoint.version.value}:{endpoint.path}",
                        "message": f"Endpoint deprecated in {endpoint.deprecated_in.value} but registered in {endpoint.version.value}",
                    }
                )

        validation_results["stats"]["versions"] = list(
            validation_results["stats"]["versions"]
        )

        if validation_results["errors"]:
            validation_results["valid"] = False

        return validation_results


# Global instance
api_versioning = APIVersioningService()
