#!/usr/bin/env python3
"""
NEXUS Platform - Service Discovery Service
Automatically discovers and registers services in the SSOT system
"""

import asyncio
import json
import logging
import socket
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import aiohttp
import dns.resolver
import netifaces

from backend.config.settings import get_settings
from .api_registry_integration import api_registry_integration
from .ssot_registry import SSOTRegistry

logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """Service type enumeration"""

    API = "api"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGE_QUEUE = "message_queue"
    STORAGE = "storage"
    MONITORING = "monitoring"
    AUTH = "auth"


class DiscoveryMethod(Enum):
    """Service discovery method enumeration"""

    DNS = "dns"
    NETWORK_SCAN = "network_scan"
    CONFIG_FILE = "config_file"
    ENVIRONMENT = "environment"
    KUBERNETES = "kubernetes"
    DOCKER_COMPOSE = "docker_compose"


@dataclass
class DiscoveredService:
    """Represents a discovered service"""

    name: str
    type: ServiceType
    host: str
    port: int
    protocol: str = "http"
    health_endpoint: Optional[str] = None
    api_endpoints: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    discovered_at: datetime = None
    last_seen: datetime = None
    status: str = "unknown"

    def __post_init__(self):
        if self.discovered_at is None:
            self.discovered_at = datetime.now(timezone.utc)
        if self.last_seen is None:
            self.last_seen = self.discovered_at


class ServiceDiscoveryService:
    """Service for automatic discovery and registration of services"""

    def __init__(self):
        self.settings = get_settings()
        self.ssot_registry = SSOTRegistry()
        self.discovery_config = self._load_discovery_config()
        self.discovered_services: Dict[str, DiscoveredService] = {}
        self.discovery_methods: List[DiscoveryMethod] = [
            DiscoveryMethod.CONFIG_FILE,
            DiscoveryMethod.ENVIRONMENT,
            DiscoveryMethod.DNS,
            DiscoveryMethod.NETWORK_SCAN,
        ]
        self.scan_interval = 300  # 5 minutes
        self.health_check_interval = 60  # 1 minute
        self.is_running = False

    def _load_discovery_config(self) -> Dict[str, Any]:
        """Load service discovery configuration"""
        config_path = Path("config/service_discovery.yaml")
        if config_path.exists():
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default discovery configuration"""
        return {
            "scan_ports": [8000, 8001, 8002, 5432, 6379, 9090, 3000],
            "scan_timeout": 5,
            "health_check_timeout": 10,
            "dns_domains": ["nexus.local", "nexus-platform.local"],
            "service_patterns": {
                "api": ["api", "backend", "service"],
                "database": ["postgres", "mysql", "mongodb"],
                "cache": ["redis", "memcached"],
                "monitoring": ["grafana", "prometheus", "monitoring"],
            },
            "auto_register": True,
            "health_checks_enabled": True,
        }

    async def start_discovery(self) -> None:
        """Start the service discovery process"""
        logger.info("Starting service discovery...")
        self.is_running = True

        # Initial discovery
        await self.discover_services()

        # Start periodic discovery and health checks
        asyncio.create_task(self._periodic_discovery())
        asyncio.create_task(self._periodic_health_checks())

        logger.info("Service discovery started")

    async def stop_discovery(self) -> None:
        """Stop the service discovery process"""
        logger.info("Stopping service discovery...")
        self.is_running = False
        logger.info("Service discovery stopped")

    async def discover_services(self) -> Dict[str, Any]:
        """Discover services using all configured methods"""
        logger.info("Discovering services...")
        discovery_results = {
            "total_discovered": 0,
            "new_services": 0,
            "updated_services": 0,
            "failed_discoveries": 0,
            "methods_used": [],
        }

        for method in self.discovery_methods:
            try:
                method_results = await self._discover_with_method(method)
                discovery_results["total_discovered"] += method_results["discovered"]
                discovery_results["new_services"] += method_results["new"]
                discovery_results["updated_services"] += method_results["updated"]
                discovery_results["methods_used"].append(method.value)

                logger.info(
                    f"Discovery method {method.value}: {method_results['discovered']} services found"
                )
            except Exception as e:
                logger.error(f"Discovery method {method.value} failed: {str(e)}")
                discovery_results["failed_discoveries"] += 1

        # Register discovered services with SSOT
        if self.discovery_config.get("auto_register", True):
            await self._register_discovered_services()

        logger.info(
            f"Service discovery completed: {discovery_results['total_discovered']} services discovered"
        )
        return discovery_results

    async def _discover_with_method(self, method: DiscoveryMethod) -> Dict[str, int]:
        """Discover services using a specific method"""
        results = {"discovered": 0, "new": 0, "updated": 0}

        if method == DiscoveryMethod.CONFIG_FILE:
            results = await self._discover_from_config()
        elif method == DiscoveryMethod.ENVIRONMENT:
            results = await self._discover_from_environment()
        elif method == DiscoveryMethod.DNS:
            results = await self._discover_from_dns()
        elif method == DiscoveryMethod.NETWORK_SCAN:
            results = await self._discover_from_network_scan()

        return results

    async def _discover_from_config(self) -> Dict[str, int]:
        """Discover services from configuration files"""
        results = {"discovered": 0, "new": 0, "updated": 0}

        # Check docker-compose file
        compose_file = Path("docker-compose.yml")
        if compose_file.exists():
            try:
                with open(compose_file, "r") as f:
                    compose_config = yaml.safe_load(f)

                services = compose_config.get("services", {})
                for service_name, service_config in services.items():
                    ports = service_config.get("ports", [])
                    if ports:
                        # Extract port mapping
                        port_mapping = (
                            ports[0] if isinstance(ports[0], str) else str(ports[0])
                        )
                        host_port = port_mapping.split(":")[0]

                        service = DiscoveredService(
                            name=service_name,
                            type=self._infer_service_type(service_name),
                            host="localhost",
                            port=int(host_port),
                            metadata={"source": "docker-compose"},
                        )

                        results = self._update_discovered_service(service, results)

            except Exception as e:
                logger.error(f"Failed to parse docker-compose.yml: {str(e)}")

        return results

    async def _discover_from_environment(self) -> Dict[str, int]:
        """Discover services from environment variables"""
        results = {"discovered": 0, "new": 0, "updated": 0}

        # Common environment variables for service URLs
        service_env_vars = {
            "DATABASE_URL": ("database", ServiceType.DATABASE, "postgresql://"),
            "REDIS_URL": ("redis", ServiceType.CACHE, "redis://"),
            "API_BASE_URL": ("api", ServiceType.API, "http://"),
            "MONITORING_URL": ("monitoring", ServiceType.MONITORING, "http://"),
        }

        for env_var, (service_name, service_type, protocol) in service_env_vars.items():
            url = os.getenv(env_var)
            if url:
                try:
                    # Parse URL to extract host and port
                    if "://" in url:
                        protocol_part, rest = url.split("://", 1)
                        host_port = rest.split("/")[0]
                        if ":" in host_port:
                            host, port_str = host_port.split(":", 1)
                            port = int(port_str)
                        else:
                            host = host_port
                            port = 80 if protocol_part == "http" else 443

                        service = DiscoveredService(
                            name=service_name,
                            type=service_type,
                            host=host,
                            port=port,
                            protocol=protocol_part,
                            metadata={"source": "environment", "env_var": env_var},
                        )

                        results = self._update_discovered_service(service, results)

                except Exception as e:
                    logger.error(f"Failed to parse {env_var}={url}: {str(e)}")

        return results

    async def _discover_from_dns(self) -> Dict[str, int]:
        """Discover services using DNS resolution"""
        results = {"discovered": 0, "new": 0, "updated": 0}

        domains = self.discovery_config.get("dns_domains", ["nexus.local"])

        for domain in domains:
            try:
                # Try to resolve common service names
                service_names = ["api", "backend", "database", "redis", "monitoring"]

                for service_name in service_names:
                    fqdn = f"{service_name}.{domain}"
                    try:
                        answers = dns.resolver.resolve(fqdn, "A")
                        for answer in answers:
                            service = DiscoveredService(
                                name=service_name,
                                type=self._infer_service_type(service_name),
                                host=str(answer),
                                port=self._get_default_port(service_name),
                                metadata={
                                    "source": "dns",
                                    "domain": domain,
                                    "fqdn": fqdn,
                                },
                            )

                            results = self._update_discovered_service(service, results)

                    except dns.resolver.NXDOMAIN:
                        continue
                    except Exception as e:
                        logger.error(f"DNS resolution failed for {fqdn}: {str(e)}")

            except Exception as e:
                logger.error(f"DNS discovery failed for domain {domain}: {str(e)}")

        return results

    async def _discover_from_network_scan(self) -> Dict[str, int]:
        """Discover services by scanning network ports"""
        results = {"discovered": 0, "new": 0, "updated": 0}

        # Get local network interfaces
        try:
            interfaces = netifaces.interfaces()
            local_ips = []

            for interface in interfaces:
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        ip = addr["addr"]
                        if not ip.startswith("127."):
                            local_ips.append(ip)

            # Scan localhost and local network
            scan_ips = ["localhost"] + local_ips[:2]  # Limit to avoid long scans
            scan_ports = self.discovery_config.get(
                "scan_ports", [8000, 8001, 5432, 6379]
            )

            for ip in scan_ips:
                for port in scan_ports:
                    try:
                        # Quick port scan
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(self.discovery_config.get("scan_timeout", 1))
                        result = sock.connect_ex(
                            (ip if ip != "localhost" else "127.0.0.1", port)
                        )

                        if result == 0:
                            # Port is open, try to identify service
                            service_name = await self._identify_service(ip, port)
                            if service_name:
                                service = DiscoveredService(
                                    name=service_name,
                                    type=self._infer_service_type(service_name),
                                    host=ip,
                                    port=port,
                                    metadata={"source": "network_scan"},
                                )

                                results = self._update_discovered_service(
                                    service, results
                                )

                        sock.close()

                    except Exception as e:
                        logger.debug(f"Port scan failed for {ip}:{port}: {str(e)}")

        except Exception as e:
            logger.error(f"Network scan discovery failed: {str(e)}")

        return results

    async def _identify_service(self, host: str, port: int) -> Optional[str]:
        """Try to identify what service is running on a port"""
        try:
            # Try HTTP health check
            url = f"http://{host}:{port}/health"
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=2)
            ) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        service_name = data.get("service", f"service-{port}")
                        return service_name

        except Exception:
            pass

        # Fallback to port-based identification
        port_service_map = {
            5432: "database",
            6379: "redis",
            9090: "monitoring",
            3000: "frontend",
            8000: "api",
            8001: "ai-service",
            8002: "auth-service",
        }

        return port_service_map.get(port, f"unknown-service-{port}")

    def _update_discovered_service(
        self, service: DiscoveredService, results: Dict[str, int]
    ) -> Dict[str, int]:
        """Update or add a discovered service"""
        service_key = f"{service.name}:{service.host}:{service.port}"

        if service_key in self.discovered_services:
            # Update existing service
            existing = self.discovered_services[service_key]
            existing.last_seen = datetime.now(timezone.utc)
            existing.status = "active"
            results["updated"] += 1
        else:
            # Add new service
            self.discovered_services[service_key] = service
            results["new"] += 1

        results["discovered"] += 1
        return results

    def _infer_service_type(self, service_name: str) -> ServiceType:
        """Infer service type from service name"""
        name_lower = service_name.lower()

        if any(pattern in name_lower for pattern in ["api", "backend", "service"]):
            return ServiceType.API
        elif any(
            pattern in name_lower for pattern in ["postgres", "mysql", "mongo", "db"]
        ):
            return ServiceType.DATABASE
        elif any(pattern in name_lower for pattern in ["redis", "cache", "memcached"]):
            return ServiceType.CACHE
        elif any(
            pattern in name_lower for pattern in ["grafana", "prometheus", "monitor"]
        ):
            return ServiceType.MONITORING
        elif any(pattern in name_lower for pattern in ["auth", "login"]):
            return ServiceType.AUTH
        else:
            return ServiceType.API  # Default to API

    def _get_default_port(self, service_name: str) -> int:
        """Get default port for a service type"""
        defaults = {
            "api": 8000,
            "backend": 8000,
            "database": 5432,
            "redis": 6379,
            "monitoring": 9090,
            "frontend": 3000,
        }
        return defaults.get(service_name.lower(), 8000)

    async def _register_discovered_services(self) -> None:
        """Register discovered services with SSOT"""
        logger.info("Registering discovered services with SSOT...")

        for service in self.discovered_services.values():
            try:
                # Register with API registry integration
                service_config = {
                    "base_url": f"{service.protocol}://{service.host}:{service.port}",
                    "health_endpoint": service.health_endpoint or "/health",
                    "api_endpoints": service.api_endpoints or ["/api/health"],
                }

                await api_registry_integration._register_service(
                    service.name, service_config
                )
                logger.info(f"Registered service: {service.name}")

            except Exception as e:
                logger.error(f"Failed to register service {service.name}: {str(e)}")

    async def _periodic_discovery(self) -> None:
        """Run periodic service discovery"""
        while self.is_running:
            try:
                await asyncio.sleep(self.scan_interval)
                if self.is_running:
                    await self.discover_services()
            except Exception as e:
                logger.error(f"Periodic discovery failed: {str(e)}")

    async def _periodic_health_checks(self) -> None:
        """Run periodic health checks on discovered services"""
        while self.is_running:
            try:
                await asyncio.sleep(self.health_check_interval)
                if self.is_running and self.discovery_config.get(
                    "health_checks_enabled", True
                ):
                    await self._check_service_health()
            except Exception as e:
                logger.error(f"Periodic health check failed: {str(e)}")

    async def _check_service_health(self) -> None:
        """Check health of all discovered services"""
        for service in self.discovered_services.values():
            try:
                health_url = f"{service.protocol}://{service.host}:{service.port}{service.health_endpoint or '/health'}"

                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as session:
                    async with session.get(health_url) as response:
                        if response.status == 200:
                            service.status = "healthy"
                        else:
                            service.status = "unhealthy"

            except Exception:
                service.status = "unreachable"

    def get_discovered_services(self) -> Dict[str, Any]:
        """Get all discovered services"""
        services = {}
        for key, service in self.discovered_services.items():
            services[key] = {
                "name": service.name,
                "type": service.type.value,
                "host": service.host,
                "port": service.port,
                "protocol": service.protocol,
                "status": service.status,
                "discovered_at": service.discovered_at.isoformat(),
                "last_seen": service.last_seen.isoformat(),
                "metadata": service.metadata,
            }

        return {
            "services": services,
            "total_count": len(services),
            "healthy_count": len(
                [s for s in self.discovered_services.values() if s.status == "healthy"]
            ),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def get_service_endpoints(
        self, service_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get endpoints for a specific service"""
        for service in self.discovered_services.values():
            if service.name == service_name:
                return {
                    "name": service.name,
                    "base_url": f"{service.protocol}://{service.host}:{service.port}",
                    "health_endpoint": service.health_endpoint,
                    "api_endpoints": service.api_endpoints,
                    "status": service.status,
                }

        return None


# Global instance
service_discovery = ServiceDiscoveryService()
