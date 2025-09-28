#!/usr/bin/env python3
"""
NEXUS Platform - API Registry Integration Service
Integrates all services with the SSOT API registry
"""

import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import yaml

from backend.config.settings import get_settings
from .ssot_registry import SSOTAnchor, SSOTRegistry

logger = logging.getLogger(__name__)


class APIRegistryIntegration:
    """Service for integrating all services with the SSOT API registry"""

    def __init__(self):
        self.settings = get_settings()
        self.registry = SSOTRegistry()
        self.integration_config = self._load_integration_config()
        self.http_client = httpx.AsyncClient(timeout=30.0)

    def _load_integration_config(self) -> Dict[str, Any]:
        """Load API integration configuration"""
        config_path = Path("config/api_integration.yaml")
        if config_path.exists():
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default integration configuration"""
        return {
            "services": {
                "frontend": {
                    "base_url": "http://localhost:3000",
                    "health_endpoint": "/health",
                    "api_endpoints": [
                        "/api/users",
                        "/api/accounts",
                        "/api/transactions",
                        "/api/monitoring",
                    ],
                },
                "backend": {
                    "base_url": "http://localhost:8000",
                    "health_endpoint": "/health",
                    "api_endpoints": [
                        "/api/users",
                        "/api/accounts",
                        "/api/transactions",
                        "/api/monitoring",
                        "/api/ai",
                    ],
                },
                "database": {
                    "base_url": "postgresql://localhost:5432/nexus",
                    "health_endpoint": "/health",
                    "api_endpoints": [],
                },
                "redis": {
                    "base_url": "redis://localhost:6379",
                    "health_endpoint": "/health",
                    "api_endpoints": [],
                },
            },
            "integration_rules": {
                "auto_discovery": True,
                "health_check_interval": 30,
                "retry_attempts": 3,
                "timeout_seconds": 10,
            },
        }

    async def integrate_all_services(self) -> Dict[str, Any]:
        """Integrate all services with the API registry"""
        logger.info("Starting API registry integration for all services")

        results = {
            "success": True,
            "integrated_services": [],
            "failed_services": [],
            "total_services": 0,
            "integration_time": None,
        }

        start_time = datetime.now(timezone.utc)

        try:
            # Get all services from configuration
            services = self.integration_config.get("services", {})
            results["total_services"] = len(services)

            # Integrate each service
            for service_name, service_config in services.items():
                try:
                    await self._integrate_service(service_name, service_config)
                    results["integrated_services"].append(service_name)
                    logger.info(f"Successfully integrated service: {service_name}")
                except Exception as e:
                    logger.error(
                        f"Failed to integrate service {service_name}: {str(e)}"
                    )
                    results["failed_services"].append(
                        {"service": service_name, "error": str(e)}
                    )

            # Check if any services failed
            if results["failed_services"]:
                results["success"] = False
                logger.warning(
                    f"Integration completed with {len(results['failed_services'])} failures"
                )
            else:
                logger.info("All services integrated successfully")

        except Exception as e:
            logger.error(f"API registry integration failed: {str(e)}")
            results["success"] = False
            results["error"] = str(e)

        finally:
            end_time = datetime.now(timezone.utc)
            results["integration_time"] = (end_time - start_time).total_seconds()

        return results

    async def _integrate_service(
        self, service_name: str, service_config: Dict[str, Any]
    ) -> None:
        """Integrate a single service with the API registry"""
        logger.info(f"Integrating service: {service_name}")

        # Register the service in the API registry
        await self._register_service(service_name, service_config)

        # Register API endpoints
        await self._register_api_endpoints(service_name, service_config)

        # Set up health monitoring
        await self._setup_health_monitoring(service_name, service_config)

        # Configure aliases
        await self._configure_aliases(service_name, service_config)

    async def _register_service(
        self, service_name: str, service_config: Dict[str, Any]
    ) -> None:
        """Register a service in the API registry"""
        canonical_name = f"{service_name}-api"
        base_url = service_config.get("base_url", "")

        # Check if service already exists
        existing_anchor = await self.registry.get_anchor(canonical_name)

        if existing_anchor:
            logger.info(f"Service {canonical_name} already registered, updating...")
            # Update existing anchor
            updated_anchor = SSOTAnchor(
                id=canonical_name,
                family=existing_anchor.family,
                description=f"{service_name.title()} API service",
                format="api",
                source_hint=base_url,
                owner="api_registry_integration",
                version="v1.0.0",
                centrality_score=existing_anchor.centrality_score,
                modification_policy="api_registry_integration",
                validation_rules=existing_anchor.validation_rules,
                generates=existing_anchor.generates,
                aliasing=existing_anchor.aliasing,
            )
            self.registry.anchors[canonical_name] = updated_anchor
        else:
            logger.info(f"Registering new service: {canonical_name}")
            # Create new anchor
            await self.registry.register_anchor(
                canonical_name,
                {
                    "family": "api",
                    "description": f"{service_name.title()} API service",
                    "format": "api",
                    "source_hint": base_url,
                    "owner": "api_registry_integration",
                    "version": "v1.0.0",
                    "centrality_score": 0.8,
                    "modification_policy": "api_registry_integration",
                    "validation_rules": ["api_validation"],
                    "generates": [],
                    "aliasing": {"base_url": base_url},
                },
            )

    async def _register_api_endpoints(
        self, service_name: str, service_config: Dict[str, Any]
    ) -> None:
        """Register API endpoints for a service"""
        canonical_name = f"{service_name}-api"
        api_endpoints = service_config.get("api_endpoints", [])

        for endpoint in api_endpoints:
            # Create endpoint-specific alias
            alias_name = f"{service_name}-{endpoint.replace('/', '-').strip('-')}"
            context = "api"

            try:
                from .ssot_registry import AliasType

                await self.registry.add_alias(
                    alias_name=alias_name,
                    canonical_name=canonical_name,
                    context=context,
                    alias_type=AliasType.PERMANENT,
                    description=f"API endpoint {endpoint} for {service_name}",
                    created_by="api_registry_integration",
                )
                logger.debug(f"Registered endpoint alias: {alias_name}")
            except Exception as e:
                logger.warning(
                    f"Failed to register endpoint alias {alias_name}: {str(e)}"
                )

    async def _setup_health_monitoring(
        self, service_name: str, service_config: Dict[str, Any]
    ) -> None:
        """Set up health monitoring for a service"""
        health_endpoint = service_config.get("health_endpoint", "/health")
        base_url = service_config.get("base_url", "")

        if not health_endpoint or not base_url:
            logger.warning(f"No health endpoint configured for {service_name}")
            return

        # Create health monitoring alias
        alias_name = f"{service_name}-health"
        canonical_name = f"{service_name}-api"

        try:
            from .ssot_registry import AliasType

            await self.registry.add_alias(
                alias_name=alias_name,
                canonical_name=canonical_name,
                context="monitoring",
                alias_type=AliasType.PERMANENT,
                description=f"Health monitoring endpoint for {service_name}",
                created_by="api_registry_integration",
            )
            logger.info(f"Set up health monitoring for {service_name}")
        except Exception as e:
            logger.warning(
                f"Failed to set up health monitoring for {service_name}: {str(e)}"
            )

    async def _configure_aliases(
        self, service_name: str, service_config: Dict[str, Any]
    ) -> None:
        """Configure standard aliases for a service"""
        canonical_name = f"{service_name}-api"

        # Define standard aliases based on service type
        standard_aliases = {
            "frontend": [
                {
                    "name": "web-app",
                    "context": "frontend",
                    "description": "Web application frontend",
                },
                {
                    "name": "ui-service",
                    "context": "system",
                    "description": "User interface service",
                },
            ],
            "backend": [
                {
                    "name": "api-service",
                    "context": "system",
                    "description": "Main API service",
                },
                {
                    "name": "backend-api",
                    "context": "frontend",
                    "description": "Backend API for frontend",
                },
            ],
            "database": [
                {
                    "name": "db-service",
                    "context": "system",
                    "description": "Database service",
                },
                {
                    "name": "postgres",
                    "context": "backend",
                    "description": "PostgreSQL database",
                },
            ],
            "redis": [
                {
                    "name": "cache-service",
                    "context": "system",
                    "description": "Redis cache service",
                },
                {
                    "name": "redis-cache",
                    "context": "backend",
                    "description": "Redis cache for backend",
                },
            ],
        }

        aliases = standard_aliases.get(service_name, [])

        for alias_config in aliases:
            try:
                from .ssot_registry import AliasType

                await self.registry.add_alias(
                    alias_name=alias_config["name"],
                    canonical_name=canonical_name,
                    context=alias_config["context"],
                    alias_type=AliasType.PERMANENT,
                    description=alias_config["description"],
                    created_by="api_registry_integration",
                )
                logger.debug(
                    f"Created alias: {alias_config['name']} for {service_name}"
                )
            except Exception as e:
                logger.warning(
                    f"Failed to create alias {alias_config['name']}: {str(e)}"
                )

    async def validate_integration(self) -> Dict[str, Any]:
        """Validate that all services are properly integrated"""
        logger.info("Validating API registry integration")

        validation_results = {
            "success": True,
            "validated_services": [],
            "validation_errors": [],
            "total_services": 0,
        }

        try:
            # Get all registered anchors
            anchors = list(self.registry.anchors.values())
            validation_results["total_services"] = len(anchors)

            for anchor in anchors:
                service_name = anchor.id.replace("-api", "")

                # Validate anchor
                if not anchor.source_hint:
                    validation_results["validation_errors"].append(
                        {
                            "service": service_name,
                            "error": "Missing source_hint (base_url)",
                        }
                    )
                    continue

                # Validate aliases
                aliases = []
                for context, context_aliases in self.registry.aliases.items():
                    for alias_name, alias_def in context_aliases.items():
                        if alias_def.canonical == anchor.id:
                            aliases.append(alias_def)

                if not aliases:
                    validation_results["validation_errors"].append(
                        {"service": service_name, "error": "No aliases configured"}
                    )
                    continue

                # Validate health endpoint
                health_aliases = [a for a in aliases if a.context == "monitoring"]
                if not health_aliases:
                    validation_results["validation_errors"].append(
                        {
                            "service": service_name,
                            "error": "No health monitoring configured",
                        }
                    )
                    continue

                validation_results["validated_services"].append(service_name)

            if validation_results["validation_errors"]:
                validation_results["success"] = False
                logger.warning(
                    f"Validation completed with {len(validation_results['validation_errors'])} errors"
                )
            else:
                logger.info("All services validated successfully")

        except Exception as e:
            logger.error(f"Integration validation failed: {str(e)}")
            validation_results["success"] = False
            validation_results["error"] = str(e)

        return validation_results

    async def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status"""
        try:
            anchors = list(self.registry.anchors.values())
            all_aliases = []
            for context, context_aliases in self.registry.aliases.items():
                for alias_name, alias_def in context_aliases.items():
                    all_aliases.append(alias_def)

            return {
                "total_anchors": len(anchors),
                "total_aliases": len(all_aliases),
                "active_anchors": len(
                    [a for a in anchors if a.owner == "api_registry_integration"]
                ),
                "active_aliases": len(
                    [a for a in all_aliases if a.status.value == "active"]
                ),
                "anchors": [
                    {
                        "id": a.id,
                        "family": a.family,
                        "description": a.description,
                        "source_hint": a.source_hint,
                    }
                    for a in anchors
                ],
                "aliases": [
                    {
                        "name": a.name,
                        "canonical": a.canonical,
                        "context": a.context,
                        "status": a.status.value,
                    }
                    for a in all_aliases
                ],
            }
        except Exception as e:
            logger.error(f"Failed to get integration status: {str(e)}")
            return {"error": str(e)}

    async def cleanup_integration(self) -> Dict[str, Any]:
        """Clean up integration (remove all registered services)"""
        logger.info("Cleaning up API registry integration")

        cleanup_results = {
            "success": True,
            "removed_contracts": 0,
            "removed_aliases": 0,
            "errors": [],
        }

        try:
            # Get all anchors created by this integration
            integration_anchors = [
                a
                for a in self.registry.anchors.values()
                if a.owner == "api_registry_integration"
            ]

            for anchor in integration_anchors:
                try:
                    # Remove all aliases for this anchor
                    aliases_to_remove = []
                    for context, context_aliases in self.registry.aliases.items():
                        for alias_name, alias_def in context_aliases.items():
                            if alias_def.canonical == anchor.id:
                                aliases_to_remove.append((context, alias_name))

                    for context, alias_name in aliases_to_remove:
                        del self.registry.aliases[context][alias_name]
                        cleanup_results["removed_aliases"] += 1

                    # Remove the anchor
                    del self.registry.anchors[anchor.id]
                    cleanup_results["removed_contracts"] += 1

                except Exception as e:
                    cleanup_results["errors"].append(
                        {"contract": anchor.id, "error": str(e)}
                    )

            if cleanup_results["errors"]:
                cleanup_results["success"] = False
                logger.warning(
                    f"Cleanup completed with {len(cleanup_results['errors'])} errors"
                )
            else:
                logger.info("Integration cleanup completed successfully")

        except Exception as e:
            logger.error(f"Integration cleanup failed: {str(e)}")
            cleanup_results["success"] = False
            cleanup_results["error"] = str(e)

        return cleanup_results

    async def close(self):
        """Close the integration service"""
        await self.http_client.aclose()


# Global instance
api_registry_integration = APIRegistryIntegration()
