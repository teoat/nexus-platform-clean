#!/usr/bin/env python3
"""
NEXUS Platform - NUC (Nexus Unified Core) Orchestrator
Central service coordination and management system
"""

import asyncio
import json
import logging
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Add the parent directory to the path to import unified_ssot_manager
sys.path.append(str(Path(__file__).parent.parent.parent))
from unified_ssot_manager import UnifiedSSOTManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"


class ServicePriority(Enum):
    """Service priority levels"""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class ServiceInfo:
    """Service information structure"""

    name: str
    version: str
    status: ServiceStatus
    priority: ServicePriority
    health_check_url: str
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_health_check: Optional[datetime] = None
    error_count: int = 0
    max_errors: int = 5
    circuit_breaker_threshold: int = 3
    circuit_breaker_timeout: int = 60  # seconds


@dataclass
class ServiceMetrics:
    """Service performance metrics"""

    service_name: str
    response_time: float
    throughput: float
    error_rate: float
    cpu_usage: float
    memory_usage: float
    timestamp: datetime = field(default_factory=datetime.now)


class CircuitBreaker:
    """Circuit breaker pattern implementation"""

    def __init__(self, failure_threshold: int = 3, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def can_execute(self) -> bool:
        """Check if the circuit breaker allows execution"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True

    def record_success(self):
        """Record successful execution"""
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        """Record failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class LoadBalancer:
    """Load balancing algorithms"""

    @staticmethod
    def round_robin(services: List[str], current_index: int = 0) -> str:
        """Round robin load balancing"""
        if not services:
            raise ValueError("No services available")
        return services[current_index % len(services)]

    @staticmethod
    def least_connections(services: Dict[str, int]) -> str:
        """Least connections load balancing"""
        if not services:
            raise ValueError("No services available")
        return min(services.keys(), key=lambda k: services[k])

    @staticmethod
    def weighted_round_robin(services: Dict[str, int]) -> str:
        """Weighted round robin load balancing"""
        if not services:
            raise ValueError("No services available")

        total_weight = sum(services.values())
        if total_weight == 0:
            return list(services.keys())[0]

        # Simple weighted selection
        import random

        rand = random.uniform(0, total_weight)
        cumulative = 0

        for service, weight in services.items():
            cumulative += weight
            if rand <= cumulative:
                return service

        return list(services.keys())[-1]


class NUCOrchestrator:
    """NUC Orchestrator - Central service coordination"""

    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.service_metrics: Dict[str, List[ServiceMetrics]] = {}
        self.load_balancer = LoadBalancer()
        self.health_check_interval = 30  # seconds
        self.metrics_retention_hours = 24
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.running = False
        self.health_check_task = None
        self.metrics_cleanup_task = None

        # SSOT Manager Integration
        self.ssot_manager = UnifiedSSOTManager()

        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {
            "service_registered": [],
            "service_unregistered": [],
            "service_health_changed": [],
            "service_failed": [],
            "service_recovered": [],
            "documentation_consolidated": [],
            "ssot_drift_detected": [],
        }

    async def start(self):
        """Start the NUC orchestrator"""
        logger.info("Starting NUC Orchestrator...")
        self.running = True

        # Start background tasks
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        self.metrics_cleanup_task = asyncio.create_task(self._metrics_cleanup_loop())

        logger.info("NUC Orchestrator started successfully")

    async def stop(self):
        """Stop the NUC orchestrator"""
        logger.info("Stopping NUC Orchestrator...")
        self.running = False

        if self.health_check_task:
            self.health_check_task.cancel()
        if self.metrics_cleanup_task:
            self.metrics_cleanup_task.cancel()

        self.executor.shutdown(wait=True)
        logger.info("NUC Orchestrator stopped")

    def register_service(self, service_info: ServiceInfo) -> bool:
        """Register a new service"""
        try:
            self.services[service_info.name] = service_info
            self.circuit_breakers[service_info.name] = CircuitBreaker(
                failure_threshold=service_info.circuit_breaker_threshold,
                timeout=service_info.circuit_breaker_timeout,
            )
            self.service_metrics[service_info.name] = []

            logger.info(f"Service '{service_info.name}' registered successfully")
            self._emit_event("service_registered", service_info)
            return True
        except Exception as e:
            logger.error(f"Failed to register service '{service_info.name}': {e}")
            return False

    def unregister_service(self, service_name: str) -> bool:
        """Unregister a service"""
        try:
            if service_name in self.services:
                service_info = self.services[service_name]
                del self.services[service_name]
                del self.circuit_breakers[service_name]
                del self.service_metrics[service_name]

                logger.info(f"Service '{service_name}' unregistered successfully")
                self._emit_event("service_unregistered", service_info)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to unregister service '{service_name}': {e}")
            return False

    def get_service(self, service_name: str) -> Optional[ServiceInfo]:
        """Get service information"""
        return self.services.get(service_name)

    def get_healthy_services(
        self, service_type: Optional[str] = None
    ) -> List[ServiceInfo]:
        """Get all healthy services, optionally filtered by type"""
        healthy_services = [
            service
            for service in self.services.values()
            if service.status == ServiceStatus.HEALTHY
        ]

        if service_type:
            healthy_services = [
                service
                for service in healthy_services
                if service.metadata.get("type") == service_type
            ]

        return healthy_services

    def select_service(
        self, service_type: str, algorithm: str = "round_robin"
    ) -> Optional[str]:
        """Select a service using load balancing algorithm"""
        healthy_services = self.get_healthy_services(service_type)

        if not healthy_services:
            logger.warning(f"No healthy services found for type '{service_type}'")
            return None

        service_names = [service.name for service in healthy_services]

        if algorithm == "round_robin":
            return self.load_balancer.round_robin(service_names)
        elif algorithm == "least_connections":
            # For simplicity, use round robin
            return self.load_balancer.round_robin(service_names)
        elif algorithm == "weighted_round_robin":
            weights = {
                service.name: service.metadata.get("weight", 1)
                for service in healthy_services
            }
            return self.load_balancer.weighted_round_robin(weights)
        else:
            return service_names[0]

    async def health_check_service(self, service_name: str) -> bool:
        """Perform health check on a specific service"""
        service = self.services.get(service_name)
        if not service:
            return False

        circuit_breaker = self.circuit_breakers[service_name]
        if not circuit_breaker.can_execute():
            logger.warning(f"Circuit breaker open for service '{service_name}'")
            return False

        try:
            # Simulate health check (replace with actual HTTP request)
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get(service.health_check_url, timeout=5) as response:
                    is_healthy = response.status == 200

                    if is_healthy:
                        circuit_breaker.record_success()
                        service.error_count = 0
                        if service.status != ServiceStatus.HEALTHY:
                            old_status = service.status
                            service.status = ServiceStatus.HEALTHY
                            self._emit_event(
                                "service_health_changed",
                                {
                                    "service": service,
                                    "old_status": old_status,
                                    "new_status": ServiceStatus.HEALTHY,
                                },
                            )
                    else:
                        circuit_breaker.record_failure()
                        service.error_count += 1
                        if service.error_count >= service.max_errors:
                            old_status = service.status
                            service.status = ServiceStatus.UNHEALTHY
                            self._emit_event("service_failed", service)
                            self._emit_event(
                                "service_health_changed",
                                {
                                    "service": service,
                                    "old_status": old_status,
                                    "new_status": ServiceStatus.UNHEALTHY,
                                },
                            )

                    service.last_health_check = datetime.now()
                    return is_healthy

        except Exception as e:
            logger.error(f"Health check failed for service '{service_name}': {e}")
            circuit_breaker.record_failure()
            service.error_count += 1
            return False

    async def _health_check_loop(self):
        """Background health check loop"""
        while self.running:
            try:
                tasks = []
                for service_name in self.services.keys():
                    task = asyncio.create_task(self.health_check_service(service_name))
                    tasks.append(task)

                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(5)

    async def _metrics_cleanup_loop(self):
        """Background metrics cleanup loop"""
        while self.running:
            try:
                cutoff_time = datetime.now() - timedelta(
                    hours=self.metrics_retention_hours
                )

                for service_name, metrics in self.service_metrics.items():
                    self.service_metrics[service_name] = [
                        metric for metric in metrics if metric.timestamp > cutoff_time
                    ]

                await asyncio.sleep(3600)  # Run every hour
            except Exception as e:
                logger.error(f"Error in metrics cleanup loop: {e}")
                await asyncio.sleep(300)

    def record_metrics(self, service_name: str, metrics: ServiceMetrics):
        """Record service metrics"""
        if service_name in self.service_metrics:
            self.service_metrics[service_name].append(metrics)

            # Keep only recent metrics
            cutoff_time = datetime.now() - timedelta(hours=self.metrics_retention_hours)
            self.service_metrics[service_name] = [
                metric
                for metric in self.service_metrics[service_name]
                if metric.timestamp > cutoff_time
            ]

    def get_service_metrics(
        self, service_name: str, hours: int = 1
    ) -> List[ServiceMetrics]:
        """Get service metrics for the last N hours"""
        if service_name not in self.service_metrics:
            return []

        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            metric
            for metric in self.service_metrics[service_name]
            if metric.timestamp > cutoff_time
        ]

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        total_services = len(self.services)
        healthy_services = len(self.get_healthy_services())

        health_percentage = (
            (healthy_services / total_services * 100) if total_services > 0 else 0
        )

        return {
            "overall_health": health_percentage,
            "total_services": total_services,
            "healthy_services": healthy_services,
            "unhealthy_services": total_services - healthy_services,
            "services": {
                name: {
                    "status": service.status.value,
                    "priority": service.priority.value,
                    "last_health_check": service.last_health_check.isoformat()
                    if service.last_health_check
                    else None,
                    "error_count": service.error_count,
                }
                for name, service in self.services.items()
            },
        }

    def add_event_handler(self, event_type: str, handler: Callable):
        """Add event handler"""
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)

    def remove_event_handler(self, event_type: str, handler: Callable):
        """Remove event handler"""
        if (
            event_type in self.event_handlers
            and handler in self.event_handlers[event_type]
        ):
            self.event_handlers[event_type].remove(handler)

    def _emit_event(self, event_type: str, data: Any):
        """Emit event to registered handlers"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"Error in event handler for '{event_type}': {e}")

    # SSOT Management Methods
    def add_documentation_file(
        self, file_path: str, doc_type: str, content: str
    ) -> bool:
        """Add a new documentation file through SSOT manager"""
        try:
            result = self.ssot_manager.add_documentation_file(
                file_path, doc_type, content
            )
            if result:
                self._emit_event(
                    "documentation_consolidated",
                    {
                        "file_path": file_path,
                        "doc_type": doc_type,
                        "timestamp": datetime.now().isoformat(),
                    },
                )
            return result
        except Exception as e:
            logger.error(f"Error adding documentation file: {e}")
            return False

    def get_documentation_status(self) -> Dict[str, Any]:
        """Get documentation SSOT status"""
        return self.ssot_manager.get_documentation_status()

    def trigger_documentation_consolidation(self, doc_type: str) -> bool:
        """Trigger documentation consolidation for a specific type"""
        try:
            result = self.ssot_manager.trigger_documentation_consolidation(doc_type)
            if result:
                self._emit_event(
                    "documentation_consolidated",
                    {"doc_type": doc_type, "timestamp": datetime.now().isoformat()},
                )
            return result
        except Exception as e:
            logger.error(f"Error triggering consolidation: {e}")
            return False

    def get_ssot_status(self) -> Dict[str, Any]:
        """Get comprehensive SSOT status"""
        return self.ssot_manager.get_status()

    def process_todos(self) -> Dict[str, Any]:
        """Process TODOs through SSOT manager"""
        try:
            self.ssot_manager.todos = self.ssot_manager.todo_processor.discover_todos()
            return {
                "todos_processed": len(self.ssot_manager.todos),
                "todos_by_priority": {
                    "critical": len(
                        [t for t in self.ssot_manager.todos if t.priority == "critical"]
                    ),
                    "high": len(
                        [t for t in self.ssot_manager.todos if t.priority == "high"]
                    ),
                    "medium": len(
                        [t for t in self.ssot_manager.todos if t.priority == "medium"]
                    ),
                    "low": len(
                        [t for t in self.ssot_manager.todos if t.priority == "low"]
                    ),
                },
            }
        except Exception as e:
            logger.error(f"Error processing TODOs: {e}")
            return {"error": str(e)}


# Global NUC Orchestrator instance
nuc_orchestrator = NUCOrchestrator()


# Service registration helper
def register_service(
    name: str,
    version: str,
    health_check_url: str,
    priority: ServicePriority = ServicePriority.MEDIUM,
    dependencies: List[str] = None,
    metadata: Dict[str, Any] = None,
) -> bool:
    """Helper function to register a service"""
    service_info = ServiceInfo(
        name=name,
        version=version,
        status=ServiceStatus.STARTING,
        priority=priority,
        health_check_url=health_check_url,
        dependencies=dependencies or [],
        metadata=metadata or {},
    )

    return nuc_orchestrator.register_service(service_info)


# Service discovery helper
def discover_service(
    service_type: str, algorithm: str = "round_robin"
) -> Optional[str]:
    """Helper function to discover a service"""
    return nuc_orchestrator.select_service(service_type, algorithm)


# Health check helper
def check_service_health(service_name: str) -> bool:
    """Helper function to check service health"""
    return asyncio.create_task(nuc_orchestrator.health_check_service(service_name))


if __name__ == "__main__":
    # Example usage
    async def main():
        # Start orchestrator
        await nuc_orchestrator.start()

        # Register some services
        register_service(
            name="auth-service",
            version="1.0.0",
            health_check_url="http://localhost:8001/health",
            priority=ServicePriority.CRITICAL,
            metadata={"type": "authentication", "weight": 3},
        )

        register_service(
            name="user-service",
            version="1.0.0",
            health_check_url="http://localhost:8002/health",
            priority=ServicePriority.HIGH,
            metadata={"type": "user-management", "weight": 2},
        )

        # Wait for health checks
        await asyncio.sleep(5)

        # Get system health
        health = nuc_orchestrator.get_system_health()
        print(f"System Health: {health}")

        # Discover service
        service = discover_service("authentication")
        print(f"Selected auth service: {service}")

        # Stop orchestrator
        await nuc_orchestrator.stop()

    asyncio.run(main())
