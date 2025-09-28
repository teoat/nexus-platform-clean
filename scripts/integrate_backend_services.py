#!/usr/bin/env python3
"""
NEXUS Platform - Backend Services Integration Script
Integrates all backend services with the SSOT API registry
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from services.api_registry_integration import APIRegistryIntegration
from services.ssot_registry import SSOTRegistry

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BackendServicesIntegrator:
    """Comprehensive backend services integrator"""

    def __init__(self):
        self.api_integration = APIRegistryIntegration()
        self.ssot_registry = SSOTRegistry()
        self.integration_results = {}

    async def integrate_all_backend_services(self) -> Dict[str, Any]:
        """Integrate all backend services with SSOT"""
        logger.info("Starting comprehensive backend services integration")

        start_time = datetime.now(timezone.utc)

        try:
            # Define all backend services to integrate
            backend_services = self._get_backend_services_config()

            # Step 1: Register core SSOT anchors
            await self._register_core_anchors()

            # Step 2: Integrate each backend service
            for service_name, service_config in backend_services.items():
                await self._integrate_backend_service(service_name, service_config)

            # Step 3: Set up cross-service aliases
            await self._setup_cross_service_aliases()

            # Step 4: Validate integration
            validation_results = await self.api_integration.validate_integration()

            # Step 5: Generate integration report
            integration_report = await self._generate_integration_report()

            self.integration_results = {
                "success": True,
                "start_time": start_time.isoformat(),
                "end_time": datetime.now(timezone.utc).isoformat(),
                "duration_seconds": (
                    datetime.now(timezone.utc) - start_time
                ).total_seconds(),
                "services_integrated": list(backend_services.keys()),
                "validation_results": validation_results,
                "integration_report": integration_report,
            }

            logger.info("Backend services integration completed successfully")
            return self.integration_results

        except Exception as e:
            logger.error(f"Backend services integration failed: {e}")
            self.integration_results = {
                "success": False,
                "error": str(e),
                "start_time": start_time.isoformat(),
                "end_time": datetime.now(timezone.utc).isoformat(),
            }
            return self.integration_results

    def _get_backend_services_config(self) -> Dict[str, Dict[str, Any]]:
        """Get configuration for all backend services"""
        return {
            "auth_service": {
                "base_url": "http://localhost:8000/api/auth",
                "health_endpoint": "/health",
                "api_endpoints": [
                    "/login",
                    "/logout",
                    "/register",
                    "/refresh",
                    "/profile",
                    "/permissions",
                ],
                "description": "Authentication and authorization service",
                "priority": "high",
            },
            "user_service": {
                "base_url": "http://localhost:8000/api/users",
                "health_endpoint": "/health",
                "api_endpoints": [
                    "/profile",
                    "/preferences",
                    "/settings",
                    "/notifications",
                ],
                "description": "User management service",
                "priority": "high",
            },
            "transaction_service": {
                "base_url": "http://localhost:8000/api/transactions",
                "health_endpoint": "/health",
                "api_endpoints": [
                    "/create",
                    "/update",
                    "/delete",
                    "/list",
                    "/search",
                    "/categories",
                    "/reports",
                ],
                "description": "Transaction management service",
                "priority": "high",
            },
            "budget_service": {
                "base_url": "http://localhost:8000/api/budgets",
                "health_endpoint": "/health",
                "api_endpoints": [
                    "/create",
                    "/update",
                    "/delete",
                    "/list",
                    "/analysis",
                    "/alerts",
                ],
                "description": "Budget management service",
                "priority": "high",
            },
            "category_service": {
                "base_url": "http://localhost:8000/api/categories",
                "health_endpoint": "/health",
                "api_endpoints": [
                    "/create",
                    "/update",
                    "/delete",
                    "/list",
                    "/hierarchy",
                ],
                "description": "Category management service",
                "priority": "medium",
            },
            "monitoring_service": {
                "base_url": "http://localhost:8000/api/monitoring",
                "health_endpoint": "/health",
                "api_endpoints": [
                    "/metrics",
                    "/alerts",
                    "/health",
                    "/performance",
                    "/logs",
                ],
                "description": "System monitoring service",
                "priority": "high",
            },
            "ai_service": {
                "base_url": "http://localhost:8000/api/ai",
                "health_endpoint": "/health",
                "api_endpoints": [
                    "/insights",
                    "/recommendations",
                    "/predictions",
                    "/analysis",
                    "/frenly",
                ],
                "description": "AI and machine learning service",
                "priority": "medium",
            },
            "notification_service": {
                "base_url": "http://localhost:8000/api/notifications",
                "health_endpoint": "/health",
                "api_endpoints": [
                    "/send",
                    "/list",
                    "/mark_read",
                    "/preferences",
                    "/templates",
                ],
                "description": "Notification service",
                "priority": "medium",
            },
            "reporting_service": {
                "base_url": "http://localhost:8000/api/reports",
                "health_endpoint": "/health",
                "api_endpoints": [
                    "/generate",
                    "/list",
                    "/download",
                    "/schedule",
                    "/templates",
                ],
                "description": "Reporting service",
                "priority": "medium",
            },
            "data_service": {
                "base_url": "http://localhost:8000/api/data",
                "health_endpoint": "/health",
                "api_endpoints": [
                    "/export",
                    "/import",
                    "/backup",
                    "/restore",
                    "/validation",
                ],
                "description": "Data management service",
                "priority": "high",
            },
        }

    async def _register_core_anchors(self):
        """Register core SSOT anchors for the platform"""
        logger.info("Registering core SSOT anchors")

        core_anchors = {
            "nexus-platform": {
                "family": "platform",
                "description": "NEXUS Platform core system",
                "format": "system",
                "source_hint": "platform",
                "owner": "system",
                "version": "3.0.0",
                "centrality_score": 1.0,
                "modification_policy": "system",
                "validation_rules": ["platform_validation"],
                "generates": ["user-data", "transaction-data", "budget-data"],
                "aliasing": {"type": "platform"},
            },
            "nexus-database": {
                "family": "database",
                "description": "NEXUS Platform database",
                "format": "database",
                "source_hint": "postgresql://localhost:5432/nexus",
                "owner": "system",
                "version": "15.4",
                "centrality_score": 0.9,
                "modification_policy": "system",
                "validation_rules": ["database_validation"],
                "generates": ["data-schema", "data-models"],
                "aliasing": {"type": "database"},
            },
            "nexus-cache": {
                "family": "cache",
                "description": "NEXUS Platform cache",
                "format": "cache",
                "source_hint": "redis://localhost:6379",
                "owner": "system",
                "version": "7.0",
                "centrality_score": 0.8,
                "modification_policy": "system",
                "validation_rules": ["cache_validation"],
                "generates": ["cache-keys", "cache-data"],
                "aliasing": {"type": "cache"},
            },
        }

        for anchor_id, anchor_config in core_anchors.items():
            try:
                await self.ssot_registry.register_anchor(anchor_id, anchor_config)
                logger.info(f"Registered core anchor: {anchor_id}")
            except Exception as e:
                logger.error(f"Failed to register core anchor {anchor_id}: {e}")

    async def _integrate_backend_service(
        self, service_name: str, service_config: Dict[str, Any]
    ):
        """Integrate a single backend service"""
        logger.info(f"Integrating backend service: {service_name}")

        try:
            # Register the service anchor
            await self._register_service_anchor(service_name, service_config)

            # Register API endpoints
            await self._register_service_endpoints(service_name, service_config)

            # Set up health monitoring
            await self._setup_service_health_monitoring(service_name, service_config)

            # Configure service aliases
            await self._configure_service_aliases(service_name, service_config)

            logger.info(f"Successfully integrated service: {service_name}")

        except Exception as e:
            logger.error(f"Failed to integrate service {service_name}: {e}")
            raise

    async def _register_service_anchor(
        self, service_name: str, service_config: Dict[str, Any]
    ):
        """Register a service anchor in SSOT"""
        anchor_id = f"{service_name}-service"

        anchor_config = {
            "family": "backend-service",
            "description": service_config.get(
                "description", f"{service_name.title()} service"
            ),
            "format": "api",
            "source_hint": service_config.get("base_url", ""),
            "owner": "backend_integration",
            "version": "1.0.0",
            "centrality_score": 0.8
            if service_config.get("priority") == "high"
            else 0.6,
            "modification_policy": "backend_integration",
            "validation_rules": ["api_validation", "service_validation"],
            "generates": [f"{service_name}-data"],
            "aliasing": {
                "base_url": service_config.get("base_url", ""),
                "priority": service_config.get("priority", "medium"),
                "service_type": "backend",
            },
        }

        await self.ssot_registry.register_anchor(anchor_id, anchor_config)
        logger.debug(f"Registered service anchor: {anchor_id}")

    async def _register_service_endpoints(
        self, service_name: str, service_config: Dict[str, Any]
    ):
        """Register API endpoints for a service"""
        anchor_id = f"{service_name}-service"
        api_endpoints = service_config.get("api_endpoints", [])

        for endpoint in api_endpoints:
            alias_name = f"{service_name}-{endpoint.replace('/', '-').strip('-')}"

            try:
                from services.ssot_registry import AliasType

                await self.ssot_registry.add_alias(
                    alias_name=alias_name,
                    canonical_name=anchor_id,
                    context="api",
                    alias_type=AliasType.PERMANENT,
                    description=f"API endpoint {endpoint} for {service_name}",
                    created_by="backend_integration",
                )
                logger.debug(f"Registered endpoint alias: {alias_name}")
            except Exception as e:
                logger.warning(f"Failed to register endpoint alias {alias_name}: {e}")

    async def _setup_service_health_monitoring(
        self, service_name: str, service_config: Dict[str, Any]
    ):
        """Set up health monitoring for a service"""
        anchor_id = f"{service_name}-service"
        health_endpoint = service_config.get("health_endpoint", "/health")

        if health_endpoint:
            alias_name = f"{service_name}-health"

            try:
                from services.ssot_registry import AliasType

                await self.ssot_registry.add_alias(
                    alias_name=alias_name,
                    canonical_name=anchor_id,
                    context="monitoring",
                    alias_type=AliasType.PERMANENT,
                    description=f"Health monitoring for {service_name}",
                    created_by="backend_integration",
                )
                logger.debug(f"Set up health monitoring: {alias_name}")
            except Exception as e:
                logger.warning(
                    f"Failed to set up health monitoring for {service_name}: {e}"
                )

    async def _configure_service_aliases(
        self, service_name: str, service_config: Dict[str, Any]
    ):
        """Configure standard aliases for a service"""
        anchor_id = f"{service_name}-service"

        # Define standard aliases based on service type
        standard_aliases = {
            "auth_service": [
                {
                    "name": "authentication",
                    "context": "system",
                    "description": "Authentication service",
                },
                {"name": "auth", "context": "api", "description": "Auth API service"},
            ],
            "user_service": [
                {
                    "name": "users",
                    "context": "system",
                    "description": "User management service",
                },
                {
                    "name": "user-management",
                    "context": "api",
                    "description": "User management API",
                },
            ],
            "transaction_service": [
                {
                    "name": "transactions",
                    "context": "system",
                    "description": "Transaction service",
                },
                {"name": "txn", "context": "api", "description": "Transaction API"},
            ],
            "budget_service": [
                {
                    "name": "budgets",
                    "context": "system",
                    "description": "Budget service",
                },
                {
                    "name": "budget-management",
                    "context": "api",
                    "description": "Budget API",
                },
            ],
            "monitoring_service": [
                {
                    "name": "monitoring",
                    "context": "system",
                    "description": "Monitoring service",
                },
                {"name": "metrics", "context": "api", "description": "Metrics API"},
            ],
            "ai_service": [
                {"name": "ai", "context": "system", "description": "AI service"},
                {
                    "name": "machine-learning",
                    "context": "api",
                    "description": "AI/ML API",
                },
            ],
        }

        aliases = standard_aliases.get(service_name, [])

        for alias_config in aliases:
            try:
                from services.ssot_registry import AliasType

                await self.ssot_registry.add_alias(
                    alias_name=alias_config["name"],
                    canonical_name=anchor_id,
                    context=alias_config["context"],
                    alias_type=AliasType.PERMANENT,
                    description=alias_config["description"],
                    created_by="backend_integration",
                )
                logger.debug(f"Created service alias: {alias_config['name']}")
            except Exception as e:
                logger.warning(f"Failed to create alias {alias_config['name']}: {e}")

    async def _setup_cross_service_aliases(self):
        """Set up aliases that span multiple services"""
        logger.info("Setting up cross-service aliases")

        cross_service_aliases = [
            {
                "name": "nexus-api",
                "canonical": "nexus-platform",
                "context": "system",
                "description": "Main NEXUS API gateway",
            },
            {
                "name": "platform-db",
                "canonical": "nexus-database",
                "context": "backend",
                "description": "Platform database",
            },
            {
                "name": "platform-cache",
                "canonical": "nexus-cache",
                "context": "backend",
                "description": "Platform cache",
            },
        ]

        for alias_config in cross_service_aliases:
            try:
                from services.ssot_registry import AliasType

                await self.ssot_registry.add_alias(
                    alias_name=alias_config["name"],
                    canonical_name=alias_config["canonical"],
                    context=alias_config["context"],
                    alias_type=AliasType.PERMANENT,
                    description=alias_config["description"],
                    created_by="backend_integration",
                )
                logger.debug(f"Created cross-service alias: {alias_config['name']}")
            except Exception as e:
                logger.warning(
                    f"Failed to create cross-service alias {alias_config['name']}: {e}"
                )

    async def _generate_integration_report(self) -> Dict[str, Any]:
        """Generate comprehensive integration report"""
        try:
            # Get integration status
            status = await self.api_integration.get_integration_status()

            # Get conflict statistics
            conflict_stats = await self.ssot_registry.get_conflict_statistics()

            # Get audit statistics
            audit_stats = await self.ssot_registry.get_audit_statistics()

            return {
                "integration_status": status,
                "conflict_statistics": conflict_stats,
                "audit_statistics": audit_stats,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to generate integration report: {e}")
            return {"error": str(e)}

    async def cleanup_integration(self):
        """Clean up the integration"""
        logger.info("Cleaning up backend services integration")
        try:
            await self.api_integration.cleanup_integration()
            logger.info("Integration cleanup completed")
        except Exception as e:
            logger.error(f"Integration cleanup failed: {e}")


async def main():
    """Main function to run the integration"""
    integrator = BackendServicesIntegrator()

    try:
        # Run integration
        results = await integrator.integrate_all_backend_services()

        # Print results
        print("\n" + "=" * 60)
        print("BACKEND SERVICES INTEGRATION RESULTS")
        print("=" * 60)
        print(f"Success: {results['success']}")
        print(f"Duration: {results.get('duration_seconds', 0):.2f} seconds")

        if results["success"]:
            print(f"Services integrated: {len(results['services_integrated'])}")
            for service in results["services_integrated"]:
                print(f"  - {service}")

            if "validation_results" in results:
                validation = results["validation_results"]
                print(f"Validation: {validation['success']}")
                print(f"Validated services: {len(validation['validated_services'])}")
                if validation["validation_errors"]:
                    print(f"Validation errors: {len(validation['validation_errors'])}")
                    for error in validation["validation_errors"]:
                        print(f"  - {error['service']}: {error['error']}")
        else:
            print(f"Error: {results.get('error', 'Unknown error')}")

        print("=" * 60)

        # Save results to file
        results_file = Path("backend_integration_results.json")
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to: {results_file}")

    except KeyboardInterrupt:
        print("\nIntegration interrupted by user")
    except Exception as e:
        print(f"Integration failed: {e}")
        logger.exception("Integration failed with exception")


if __name__ == "__main__":
    asyncio.run(main())
