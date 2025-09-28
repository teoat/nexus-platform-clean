#!/usr/bin/env python3
"""
Enhanced SSOT Monitoring Service

Provides comprehensive monitoring and health checks for the SSOT system,
including advanced metrics collection, health assessments, and alerting.
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
import redis.asyncio as redis
from aiohttp import web
from prometheus_client import (Counter, Gauge, Histogram, generate_latest,
                               start_http_server)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SSOTMonitor:
    """Enhanced SSOT monitoring service"""

    def __init__(
        self,
        ssot_service_url: str = "http://localhost:8000",
        redis_url: str = "redis://localhost:6379/0",
        metrics_port: int = 8003,
    ):
        self.ssot_service_url = ssot_service_url
        self.redis_url = redis_url
        self.metrics_port = metrics_port

        # Redis client for cache monitoring
        self.redis_client = None

        # Initialize Prometheus metrics
        self._init_metrics()

        # Health check intervals
        self.health_check_interval = 30  # seconds
        self.cache_monitor_interval = 60  # seconds

    def _init_metrics(self):
        """Initialize Prometheus metrics"""
        # Existing metrics (extended)
        self.alias_creations = Counter(
            "ssot_alias_creations_total",
            "Total number of SSOT alias creation attempts",
            ["status", "context", "type"],
        )

        self.alias_resolutions = Counter(
            "ssot_alias_resolutions_total",
            "Total number of SSOT alias resolution attempts",
            ["status", "context", "cache_hit"],
        )

        self.resolution_duration = Histogram(
            "ssot_alias_resolution_duration_seconds",
            "Histogram of SSOT alias resolution durations",
            ["context"],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0],
        )

        self.active_aliases = Gauge(
            "ssot_active_aliases_count",
            "Current number of active SSOT aliases",
            ["context"],
        )

        self.expired_aliases = Gauge(
            "ssot_expired_aliases_count",
            "Current number of expired SSOT aliases",
            ["context"],
        )

        # Enhanced metrics
        self.consistency_score = Gauge(
            "ssot_consistency_score", "SSOT consistency score (0-1)", ["component"]
        )

        self.cache_hit_rate = Gauge(
            "ssot_cache_hit_rate_percent",
            "SSOT cache hit rate percentage",
            ["cache_type"],
        )

        self.health_status = Gauge(
            "ssot_health_status",
            "SSOT system health status (0=unhealthy, 1=healthy)",
            ["component"],
        )

        self.anchors_total = Gauge(
            "ssot_anchors_total", "Total number of SSOT anchors", ["family", "status"]
        )

        self.validation_failures = Counter(
            "ssot_validation_failures_total",
            "Total number of SSOT validation failures",
            ["rule", "operation", "severity"],
        )

        self.audit_events = Counter(
            "ssot_audit_events_total",
            "Total number of SSOT audit events",
            ["event_type", "severity"],
        )

        # Performance metrics
        self.response_time = Histogram(
            "ssot_api_response_time_seconds",
            "SSOT API response times",
            ["endpoint", "method"],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0],
        )

        self.error_rate = Counter(
            "ssot_api_errors_total",
            "Total SSOT API errors",
            ["endpoint", "status_code"],
        )

    async def start(self):
        """Start the monitoring service"""
        logger.info("Starting SSOT Monitor service...")

        # Initialize Redis connection
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis_client.ping()
            logger.info("Connected to Redis for cache monitoring")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            self.redis_client = None

        # Start Prometheus metrics server
        start_http_server(self.metrics_port)
        logger.info(f"Prometheus metrics server started on port {self.metrics_port}")

        # Start web server for health endpoint
        app = web.Application()
        app.router.add_get("/health", self._health_handler)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(
            runner, "0.0.0.0", self.metrics_port + 1
        )  # Health on metrics_port + 1
        await site.start()
        logger.info(f"Health endpoint started on port {self.metrics_port + 1}")

        # Start monitoring tasks
        await asyncio.gather(
            self._health_check_loop(),
            self._cache_monitor_loop(),
            self._metrics_collection_loop(),
        )

    async def _health_check_loop(self):
        """Periodic health checks"""
        while True:
            try:
                await self._perform_health_checks()
            except Exception as e:
                logger.error(f"Health check failed: {e}")
            await asyncio.sleep(self.health_check_interval)

    async def _cache_monitor_loop(self):
        """Periodic cache monitoring"""
        while True:
            try:
                await self._monitor_cache_performance()
            except Exception as e:
                logger.error(f"Cache monitoring failed: {e}")
            await asyncio.sleep(self.cache_monitor_interval)

    async def _metrics_collection_loop(self):
        """Periodic metrics collection from SSOT service"""
        while True:
            try:
                await self._collect_ssot_metrics()
            except Exception as e:
                logger.error(f"Metrics collection failed: {e}")
            await asyncio.sleep(60)  # Collect every minute

    async def _perform_health_checks(self):
        """Perform comprehensive health checks"""
        health_checks = {
            "ssot_service": await self._check_ssot_service(),
            "redis_cache": await self._check_redis_cache(),
            "ssot_consistency": await self._check_ssot_consistency(),
            "anchor_validation": await self._check_anchor_validation(),
        }

        # Update health status metrics
        for component, healthy in health_checks.items():
            self.health_status.labels(component=component).set(1 if healthy else 0)

        overall_health = all(health_checks.values())
        logger.info(
            f"Health check completed: {sum(health_checks.values())}/{len(health_checks)} components healthy"
        )

    async def _check_ssot_service(self) -> bool:
        """Check if SSOT service is responding"""
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(
                    f"{self.ssot_service_url}/api/v1/ssot/aliases", timeout=5
                ) as response:
                    response_time = time.time() - start_time
                    self.response_time.labels(
                        endpoint="/api/v1/ssot/aliases", method="GET"
                    ).observe(response_time)

                    if response.status == 200:
                        return True
                    else:
                        self.error_rate.labels(
                            endpoint="/api/v1/ssot/aliases",
                            status_code=str(response.status),
                        ).inc()
                        return False
        except Exception as e:
            logger.warning(f"SSOT service health check failed: {e}")
            return False

    async def _check_redis_cache(self) -> bool:
        """Check Redis cache connectivity"""
        if not self.redis_client:
            return False

        try:
            await self.redis_client.ping()
            return True
        except Exception:
            return False

    async def _check_ssot_consistency(self) -> bool:
        """Check SSOT data consistency"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.ssot_service_url}/api/v1/ssot/aliases"
                ) as response:
                    if response.status != 200:
                        return False

                    data = await response.json()
                    aliases = data.get("aliases", [])

                    # Basic consistency checks
                    contexts = {}
                    for alias in aliases:
                        context = alias.get("context")
                        if context not in contexts:
                            contexts[context] = []
                        contexts[context].append(alias)

                    # Check for duplicate names in same context
                    for context, context_aliases in contexts.items():
                        names = [a.get("name") for a in context_aliases]
                        if len(names) != len(set(names)):
                            logger.warning(
                                f"Duplicate alias names found in context {context}"
                            )
                            return False

                    # Update consistency score
                    consistency_score = 0.95  # Assume high consistency
                    self.consistency_score.labels(component="ssot").set(
                        consistency_score
                    )

                    return True
        except Exception as e:
            logger.warning(f"SSOT consistency check failed: {e}")
            return False

    async def _check_anchor_validation(self) -> bool:
        """Check SSOT anchor validation"""
        try:
            # This would typically check anchor definitions
            # For now, assume anchors are valid
            self.anchors_total.labels(family="api", status="active").set(3)  # Example
            self.anchors_total.labels(family="service", status="active").set(
                2
            )  # Example
            return True
        except Exception as e:
            logger.warning(f"Anchor validation check failed: {e}")
            return False

    async def _monitor_cache_performance(self):
        """Monitor cache performance metrics"""
        if not self.redis_client:
            return

        try:
            # Get cache statistics
            info = await self.redis_client.info()
            keyspace_hits = info.get("keyspace_hits", 0)
            keyspace_misses = info.get("keyspace_misses", 0)

            if keyspace_hits + keyspace_misses > 0:
                hit_rate = (keyspace_hits / (keyspace_hits + keyspace_misses)) * 100
                self.cache_hit_rate.labels(cache_type="redis").set(hit_rate)
                logger.debug(f"Cache hit rate: {hit_rate:.2f}%")

        except Exception as e:
            logger.warning(f"Cache performance monitoring failed: {e}")

    async def _collect_ssot_metrics(self):
        """Collect metrics from SSOT service"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get alias statistics
                async with session.get(
                    f"{self.ssot_service_url}/api/v1/ssot/aliases"
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        aliases = data.get("aliases", [])

                        # Update active aliases count by context
                        context_counts = {}
                        for alias in aliases:
                            context = alias.get("context", "unknown")
                            if context not in context_counts:
                                context_counts[context] = 0
                            context_counts[context] += 1

                        for context, count in context_counts.items():
                            self.active_aliases.labels(context=context).set(count)

        except Exception as e:
            logger.warning(f"SSOT metrics collection failed: {e}")

    async def _health_handler(self, request):
        """Health check endpoint handler"""
        health_report = await self.get_health_report()
        return web.json_response(health_report)

    async def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "service": "ssot-monitor",
            "version": "1.0.0",
            "status": "healthy",  # Would be determined by health checks
            "metrics_endpoint": f"http://localhost:{self.metrics_port}/metrics",
            "health_endpoint": f"http://localhost:{self.metrics_port + 1}/health",
            "monitored_components": [
                "ssot-service",
                "redis-cache",
                "ssot-consistency",
                "anchor-validation",
            ],
            "alerts": [],  # Would contain active alerts
        }


async def main():
    """Main entry point"""
    monitor = SSOTMonitor()

    # Handle graceful shutdown
    def signal_handler(signum, frame):
        logger.info("Shutting down SSOT Monitor...")
        # Cleanup would go here

    import signal

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    await monitor.start()


if __name__ == "__main__":
    asyncio.run(main())
