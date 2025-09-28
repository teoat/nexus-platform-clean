#!/usr/bin/env python3
"""
NEXUS Platform - Service Registry
Centralized service discovery and registration system
"""

import asyncio
import hashlib
import json
import logging
import threading
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """Service type enumeration"""

    API_GATEWAY = "api-gateway"
    AUTHENTICATION = "authentication"
    USER_MANAGEMENT = "user-management"
    TRANSACTION = "transaction"
    ANALYTICS = "analytics"
    NOTIFICATION = "notification"
    FILE_STORAGE = "file-storage"
    MONITORING = "monitoring"
    CACHE = "cache"
    DATABASE = "database"


class ServiceState(Enum):
    """Service state enumeration"""

    REGISTERING = "registering"
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"


@dataclass
class ServiceEndpoint:
    """Service endpoint information"""

    url: str
    protocol: str = "http"
    port: int = 80
    path: str = "/"
    health_check_path: str = "/health"
    weight: int = 1
    priority: int = 0
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class ServiceDefinition:
    """Service definition structure"""

    id: str
    name: str
    version: str
    service_type: ServiceType
    state: ServiceState
    endpoints: List[ServiceEndpoint]
    dependencies: List[str] = None
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None
    last_heartbeat: datetime = None
    ttl: int = 30  # Time to live in seconds
    tags: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.metadata is None:
            self.metadata = {}
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.last_heartbeat is None:
            self.last_heartbeat = datetime.now()


class ServiceRegistry:
    """Central service registry for discovery and management"""

    def __init__(self):
        self.services: Dict[str, ServiceDefinition] = {}
        self.service_index: Dict[ServiceType, Set[str]] = {}
        self.endpoint_index: Dict[str, str] = {}  # endpoint_url -> service_id
        self.heartbeat_interval = 10  # seconds
        self.cleanup_interval = 60  # seconds
        self.running = False
        self.cleanup_task = None
        self.lock = threading.RLock()

        # Initialize service type index
        for service_type in ServiceType:
            self.service_index[service_type] = set()

    async def start(self):
        """Start the service registry"""
        logger.info("Starting Service Registry...")
        self.running = True

        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_expired_services())

        logger.info("Service Registry started successfully")

    async def stop(self):
        """Stop the service registry"""
        logger.info("Stopping Service Registry...")
        self.running = False

        if self.cleanup_task:
            self.cleanup_task.cancel()

        logger.info("Service Registry stopped")

    def register_service(self, service_definition: ServiceDefinition) -> bool:
        """Register a new service"""
        try:
            with self.lock:
                # Generate unique ID if not provided
                if not service_definition.id:
                    service_definition.id = self._generate_service_id(
                        service_definition
                    )

                # Validate service definition
                if not self._validate_service_definition(service_definition):
                    return False

                # Check for conflicts
                if service_definition.id in self.services:
                    logger.warning(
                        f"Service with ID '{service_definition.id}' already exists"
                    )
                    return False

                # Register service
                self.services[service_definition.id] = service_definition

                # Update indexes
                self.service_index[service_definition.service_type].add(
                    service_definition.id
                )
                for endpoint in service_definition.endpoints:
                    self.endpoint_index[endpoint.url] = service_definition.id

                logger.info(
                    f"Service '{service_definition.name}' registered with ID '{service_definition.id}'"
                )
                return True

        except Exception as e:
            logger.error(f"Failed to register service: {e}")
            return False

    def unregister_service(self, service_id: str) -> bool:
        """Unregister a service"""
        try:
            with self.lock:
                if service_id not in self.services:
                    logger.warning(f"Service with ID '{service_id}' not found")
                    return False

                service = self.services[service_id]

                # Remove from indexes
                self.service_index[service.service_type].discard(service_id)
                for endpoint in service.endpoints:
                    self.endpoint_index.pop(endpoint.url, None)

                # Remove service
                del self.services[service_id]

                logger.info(f"Service '{service.name}' unregistered")
                return True

        except Exception as e:
            logger.error(f"Failed to unregister service: {e}")
            return False

    def update_service(self, service_id: str, updates: Dict[str, Any]) -> bool:
        """Update service information"""
        try:
            with self.lock:
                if service_id not in self.services:
                    logger.warning(f"Service with ID '{service_id}' not found")
                    return False

                service = self.services[service_id]

                # Update allowed fields
                allowed_fields = ["endpoints", "metadata", "tags", "state"]
                for field, value in updates.items():
                    if field in allowed_fields and hasattr(service, field):
                        setattr(service, field, value)

                service.updated_at = datetime.now()
                logger.info(f"Service '{service.name}' updated")
                return True

        except Exception as e:
            logger.error(f"Failed to update service: {e}")
            return False

    def heartbeat(self, service_id: str) -> bool:
        """Update service heartbeat"""
        try:
            with self.lock:
                if service_id not in self.services:
                    return False

                service = self.services[service_id]
                service.last_heartbeat = datetime.now()
                return True

        except Exception as e:
            logger.error(f"Failed to update heartbeat for service '{service_id}': {e}")
            return False

    def get_service(self, service_id: str) -> Optional[ServiceDefinition]:
        """Get service by ID"""
        with self.lock:
            return self.services.get(service_id)

    def get_services_by_type(
        self, service_type: ServiceType
    ) -> List[ServiceDefinition]:
        """Get all services of a specific type"""
        with self.lock:
            service_ids = self.service_index.get(service_type, set())
            return [
                self.services[service_id]
                for service_id in service_ids
                if service_id in self.services
            ]

    def get_services_by_name(self, name: str) -> List[ServiceDefinition]:
        """Get all services with a specific name"""
        with self.lock:
            return [
                service for service in self.services.values() if service.name == name
            ]

    def discover_service(
        self, service_type: ServiceType, tags: List[str] = None
    ) -> Optional[ServiceDefinition]:
        """Discover a service by type and optional tags"""
        with self.lock:
            services = self.get_services_by_type(service_type)

            # Filter by tags if provided
            if tags:
                services = [
                    service
                    for service in services
                    if any(tag in service.tags for tag in tags)
                ]

            # Filter active services only
            active_services = [
                service for service in services if service.state == ServiceState.ACTIVE
            ]

            if not active_services:
                return None

            # Simple load balancing - return first available
            # In production, implement more sophisticated algorithms
            return active_services[0]

    def discover_services(
        self, service_type: ServiceType, tags: List[str] = None
    ) -> List[ServiceDefinition]:
        """Discover all services by type and optional tags"""
        with self.lock:
            services = self.get_services_by_type(service_type)

            # Filter by tags if provided
            if tags:
                services = [
                    service
                    for service in services
                    if any(tag in service.tags for tag in tags)
                ]

            # Filter active services only
            return [
                service for service in services if service.state == ServiceState.ACTIVE
            ]

    def get_service_by_endpoint(self, endpoint_url: str) -> Optional[ServiceDefinition]:
        """Get service by endpoint URL"""
        with self.lock:
            service_id = self.endpoint_index.get(endpoint_url)
            if service_id:
                return self.services.get(service_id)
            return None

    def get_all_services(self) -> List[ServiceDefinition]:
        """Get all registered services"""
        with self.lock:
            return list(self.services.values())

    def get_service_dependencies(self, service_id: str) -> List[ServiceDefinition]:
        """Get service dependencies"""
        with self.lock:
            if service_id not in self.services:
                return []

            service = self.services[service_id]
            dependencies = []

            for dep_name in service.dependencies:
                # Find services with matching name
                matching_services = self.get_services_by_name(dep_name)
                dependencies.extend(matching_services)

            return dependencies

    def get_dependent_services(self, service_id: str) -> List[ServiceDefinition]:
        """Get services that depend on the given service"""
        with self.lock:
            if service_id not in self.services:
                return []

            service = self.services[service_id]
            dependents = []

            for other_service in self.services.values():
                if service.name in other_service.dependencies:
                    dependents.append(other_service)

            return dependents

    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        with self.lock:
            total_services = len(self.services)
            active_services = len(
                [
                    service
                    for service in self.services.values()
                    if service.state == ServiceState.ACTIVE
                ]
            )

            service_types_count = {
                service_type.value: len(service_ids)
                for service_type, service_ids in self.service_index.items()
            }

            return {
                "total_services": total_services,
                "active_services": active_services,
                "inactive_services": total_services - active_services,
                "service_types": service_types_count,
                "endpoints_registered": len(self.endpoint_index),
            }

    async def _cleanup_expired_services(self):
        """Cleanup expired services based on TTL"""
        while self.running:
            try:
                current_time = datetime.now()
                expired_services = []

                with self.lock:
                    for service_id, service in self.services.items():
                        if service.last_heartbeat:
                            time_since_heartbeat = (
                                current_time - service.last_heartbeat
                            ).total_seconds()
                            if time_since_heartbeat > service.ttl:
                                expired_services.append(service_id)

                # Remove expired services
                for service_id in expired_services:
                    logger.warning(
                        f"Service '{service_id}' expired, removing from registry"
                    )
                    self.unregister_service(service_id)

                await asyncio.sleep(self.cleanup_interval)

            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(10)

    def _validate_service_definition(
        self, service_definition: ServiceDefinition
    ) -> bool:
        """Validate service definition"""
        try:
            # Check required fields
            if not service_definition.name or not service_definition.version:
                logger.error("Service name and version are required")
                return False

            # Check endpoints
            if not service_definition.endpoints:
                logger.error("At least one endpoint is required")
                return False

            # Validate endpoints
            for endpoint in service_definition.endpoints:
                if not endpoint.url:
                    logger.error("Endpoint URL is required")
                    return False

            return True

        except Exception as e:
            logger.error(f"Service validation failed: {e}")
            return False

    def _generate_service_id(self, service_definition: ServiceDefinition) -> str:
        """Generate unique service ID"""
        # Create a hash based on service name, version, and timestamp
        content = (
            f"{service_definition.name}:{service_definition.version}:{time.time()}"
        )
        hash_object = hashlib.md5(content.encode())
        return hash_object.hexdigest()[:12]


# Global service registry instance
service_registry = ServiceRegistry()


# Helper functions
def register_service(
    name: str,
    version: str,
    service_type: ServiceType,
    endpoints: List[ServiceEndpoint],
    dependencies: List[str] = None,
    metadata: Dict[str, Any] = None,
    tags: List[str] = None,
) -> str:
    """Helper function to register a service"""
    service_definition = ServiceDefinition(
        id="",
        name=name,
        version=version,
        service_type=service_type,
        state=ServiceState.REGISTERING,
        endpoints=endpoints,
        dependencies=dependencies,
        metadata=metadata,
        tags=tags,
    )

    if service_registry.register_service(service_definition):
        return service_definition.id
    return None


def discover_service(
    service_type: ServiceType, tags: List[str] = None
) -> Optional[ServiceDefinition]:
    """Helper function to discover a service"""
    return service_registry.discover_service(service_type, tags)


def discover_services(
    service_type: ServiceType, tags: List[str] = None
) -> List[ServiceDefinition]:
    """Helper function to discover all services of a type"""
    return service_registry.discover_services(service_type, tags)


def update_service_heartbeat(service_id: str) -> bool:
    """Helper function to update service heartbeat"""
    return service_registry.heartbeat(service_id)


if __name__ == "__main__":
    # Example usage
    async def main():
        # Start registry
        await service_registry.start()

        # Register some services
        auth_service_id = register_service(
            name="auth-service",
            version="1.0.0",
            service_type=ServiceType.AUTHENTICATION,
            endpoints=[
                ServiceEndpoint(
                    url="http://localhost:8001",
                    port=8001,
                    health_check_path="/health",
                    weight=3,
                    tags=["production", "primary"],
                )
            ],
            metadata={"environment": "production"},
            tags=["authentication", "security"],
        )

        user_service_id = register_service(
            name="user-service",
            version="1.0.0",
            service_type=ServiceType.USER_MANAGEMENT,
            endpoints=[
                ServiceEndpoint(
                    url="http://localhost:8002",
                    port=8002,
                    health_check_path="/health",
                    weight=2,
                    tags=["production"],
                )
            ],
            dependencies=["auth-service"],
            tags=["user-management", "crud"],
        )

        print(f"Registered services: {auth_service_id}, {user_service_id}")

        # Discover services
        auth_service = discover_service(ServiceType.AUTHENTICATION)
        if auth_service:
            print(
                f"Discovered auth service: {auth_service.name} at {auth_service.endpoints[0].url}"
            )

        # Get registry stats
        stats = service_registry.get_registry_stats()
        print(f"Registry stats: {stats}")

        # Update heartbeats
        service_registry.heartbeat(auth_service_id)
        service_registry.heartbeat(user_service_id)

        # Wait for cleanup cycle
        await asyncio.sleep(5)

        # Stop registry
        await service_registry.stop()

    asyncio.run(main())
