#!/usr/bin/env python3
"""
NEXUS Platform - Performance Monitor
Comprehensive performance monitoring and metrics collection
"""

import asyncio
import logging
import statistics
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import psutil

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""

    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    network_io_bytes: int
    operation_count: int
    average_response_time: float
    error_rate: float
    cache_hit_rate: float
    throughput: float


class PerformanceMonitor:
    """Comprehensive performance monitoring system"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.metrics_history = deque(maxlen=1000)  # Keep last 1000 metrics
        self.operation_times = defaultdict(list)
        self.error_counts = defaultdict(int)
        self.cache_hits = 0
        self.cache_misses = 0
        self.operation_counts = defaultdict(int)

        # Monitoring configuration
        self.collection_interval = self.config.get("collection_interval", 30)  # seconds
        self.alert_thresholds = self.config.get(
            "alert_thresholds",
            {
                "cpu_percent": 80.0,
                "memory_percent": 85.0,
                "response_time": 2.0,
                "error_rate": 0.05,
            },
        )

        # Performance tracking
        self.start_time = time.time()
        self.last_network_io = psutil.net_io_counters()

    async def collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Network I/O
            current_network_io = psutil.net_io_counters()
            network_io_bytes = (
                current_network_io.bytes_sent + current_network_io.bytes_recv
            )
            if self.last_network_io:
                network_io_bytes -= (
                    self.last_network_io.bytes_sent + self.last_network_io.bytes_recv
                )
            self.last_network_io = current_network_io

            # Application metrics
            total_operations = sum(self.operation_counts.values())
            all_times = []
            for times in self.operation_times.values():
                all_times.extend(times)

            average_response_time = statistics.mean(all_times) if all_times else 0.0
            total_errors = sum(self.error_counts.values())
            error_rate = (
                total_errors / total_operations if total_operations > 0 else 0.0
            )

            cache_hit_rate = (
                self.cache_hits / (self.cache_hits + self.cache_misses)
                if (self.cache_hits + self.cache_misses) > 0
                else 0.0
            )

            # Calculate throughput (operations per second)
            uptime = time.time() - self.start_time
            throughput = total_operations / uptime if uptime > 0 else 0.0

            metrics = PerformanceMetrics(
                timestamp=datetime.now(timezone.utc),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 * 1024),
                disk_usage_percent=disk.percent,
                network_io_bytes=network_io_bytes,
                operation_count=total_operations,
                average_response_time=average_response_time,
                error_rate=error_rate,
                cache_hit_rate=cache_hit_rate,
                throughput=throughput,
            )

            self.metrics_history.append(metrics)
            return metrics

        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return None

    async def start_monitoring(self):
        """Start continuous performance monitoring"""
        logger.info("Starting performance monitoring")

        while True:
            try:
                metrics = await self.collect_metrics()
                if metrics:
                    await self._check_alerts(metrics)
                    await self._log_metrics(metrics)

                await asyncio.sleep(self.collection_interval)

            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error

    async def _check_alerts(self, metrics: PerformanceMetrics):
        """Check for performance alerts"""
        alerts = []

        if metrics.cpu_percent > self.alert_thresholds["cpu_percent"]:
            alerts.append(f"High CPU usage: {metrics.cpu_percent:.1f}%")

        if metrics.memory_percent > self.alert_thresholds["memory_percent"]:
            alerts.append(f"High memory usage: {metrics.memory_percent:.1f}%")

        if metrics.average_response_time > self.alert_thresholds["response_time"]:
            alerts.append(f"Slow response time: {metrics.average_response_time:.2f}s")

        if metrics.error_rate > self.alert_thresholds["error_rate"]:
            alerts.append(f"High error rate: {metrics.error_rate:.2%}")

        for alert in alerts:
            logger.warning(f"Performance Alert: {alert}")
            # Here you would send alerts to monitoring systems

    async def _log_metrics(self, metrics: PerformanceMetrics):
        """Log performance metrics"""
        logger.info(
            f"Performance - CPU: {metrics.cpu_percent:.1f}%, "
            f"Memory: {metrics.memory_percent:.1f}%, "
            f"Response: {metrics.average_response_time:.3f}s, "
            f"Throughput: {metrics.throughput:.1f} ops/s"
        )

    def record_operation(self, operation: str, duration: float, success: bool = True):
        """Record an operation for performance tracking"""
        self.operation_times[operation].append(duration)
        self.operation_counts[operation] += 1

        if not success:
            self.error_counts[operation] += 1

        # Keep only recent data
        if len(self.operation_times[operation]) > 1000:
            self.operation_times[operation] = self.operation_times[operation][-1000:]

    def record_cache_hit(self):
        """Record a cache hit"""
        self.cache_hits += 1

    def record_cache_miss(self):
        """Record a cache miss"""
        self.cache_misses += 1

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.metrics_history:
            return {"error": "No metrics available"}

        recent_metrics = list(self.metrics_history)[-10:]  # Last 10 measurements

        return {
            "current_metrics": asdict(recent_metrics[-1]) if recent_metrics else None,
            "average_cpu": statistics.mean([m.cpu_percent for m in recent_metrics]),
            "average_memory": statistics.mean(
                [m.memory_percent for m in recent_metrics]
            ),
            "average_response_time": statistics.mean(
                [m.average_response_time for m in recent_metrics]
            ),
            "total_operations": sum(m.operation_count for m in recent_metrics),
            "uptime_seconds": time.time() - self.start_time,
        }

    def get_operation_statistics(self) -> Dict[str, Any]:
        """Get operation-specific statistics"""
        stats = {}

        for operation, times in self.operation_times.items():
            if times:
                stats[operation] = {
                    "count": len(times),
                    "average_time": statistics.mean(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "error_count": self.error_counts[operation],
                    "error_rate": self.error_counts[operation] / len(times)
                    if times
                    else 0,
                }

        return stats
