#!/usr/bin/env python3
"""
NEXUS Platform - Advanced Monitoring System
Comprehensive monitoring, alerting, and performance tracking
"""

import asyncio
import json
import logging
import smtplib
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from email.mime.multipart import MimeMultipart
from email.mime.text import MimeText
from typing import Any, Dict, List, Optional

import aiohttp
import psutil
import redis
from prometheus_client import Counter, Gauge, Histogram, start_http_server

logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "nexus_requests_total", "Total requests", ["method", "endpoint", "status"]
)
REQUEST_DURATION = Histogram(
    "nexus_request_duration_seconds", "Request duration", ["method", "endpoint"]
)
ACTIVE_CONNECTIONS = Gauge("nexus_active_connections", "Active database connections")
MEMORY_USAGE = Gauge("nexus_memory_usage_bytes", "Memory usage in bytes")
CPU_USAGE = Gauge("nexus_cpu_usage_percent", "CPU usage percentage")
DATABASE_QUERY_DURATION = Histogram(
    "nexus_database_query_duration_seconds", "Database query duration"
)
CACHE_HIT_RATIO = Gauge("nexus_cache_hit_ratio", "Cache hit ratio")


@dataclass
class Alert:
    """Alert data structure"""

    id: str
    severity: str  # critical, warning, info
    title: str
    message: str
    timestamp: datetime
    source: str
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class Metric:
    """Metric data structure"""

    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str]


class MonitoringSystem:
    """Advanced monitoring system with alerting"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.alerts: List[Alert] = []
        self.metrics: List[Metric] = []
        self.alert_thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "disk_usage": 90.0,
            "response_time": 2.0,
            "error_rate": 5.0,
            "database_connections": 80,
        }
        self.monitoring_active = False

    async def start_monitoring(self, port: int = 8001):
        """Start monitoring system"""
        logger.info("Starting advanced monitoring system...")

        # Start Prometheus metrics server
        start_http_server(port)
        logger.info(f"Prometheus metrics server started on port {port}")

        self.monitoring_active = True

        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self._monitor_system_metrics()),
            asyncio.create_task(self._monitor_application_metrics()),
            asyncio.create_task(self._monitor_database_metrics()),
            asyncio.create_task(self._monitor_cache_metrics()),
            asyncio.create_task(self._check_alerts()),
            asyncio.create_task(self._cleanup_old_metrics()),
        ]

        await asyncio.gather(*tasks)

    async def _monitor_system_metrics(self):
        """Monitor system-level metrics"""
        while self.monitoring_active:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                CPU_USAGE.set(cpu_percent)

                # Memory usage
                memory = psutil.virtual_memory()
                MEMORY_USAGE.set(memory.used)

                # Disk usage
                disk = psutil.disk_usage("/")
                disk_percent = (disk.used / disk.total) * 100

                # Check thresholds
                if cpu_percent > self.alert_thresholds["cpu_usage"]:
                    await self._create_alert(
                        "high_cpu_usage",
                        "critical",
                        "High CPU Usage",
                        f"CPU usage is {cpu_percent:.1f}% (threshold: {self.alert_thresholds['cpu_usage']}%)",
                        "system",
                    )

                if memory.percent > self.alert_thresholds["memory_usage"]:
                    await self._create_alert(
                        "high_memory_usage",
                        "critical",
                        "High Memory Usage",
                        f"Memory usage is {memory.percent:.1f}% (threshold: {self.alert_thresholds['memory_usage']}%)",
                        "system",
                    )

                if disk_percent > self.alert_thresholds["disk_usage"]:
                    await self._create_alert(
                        "high_disk_usage",
                        "warning",
                        "High Disk Usage",
                        f"Disk usage is {disk_percent:.1f}% (threshold: {self.alert_thresholds['disk_usage']}%)",
                        "system",
                    )

                # Store metrics
                await self._store_metric("cpu_usage", cpu_percent, {"type": "system"})
                await self._store_metric(
                    "memory_usage", memory.percent, {"type": "system"}
                )
                await self._store_metric("disk_usage", disk_percent, {"type": "system"})

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"System metrics monitoring error: {e}")
                await asyncio.sleep(60)

    async def _monitor_application_metrics(self):
        """Monitor application-level metrics"""
        while self.monitoring_active:
            try:
                # Get application metrics from Redis
                app_metrics = await self._get_application_metrics()

                for metric_name, value in app_metrics.items():
                    await self._store_metric(
                        metric_name, value, {"type": "application"}
                    )

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Application metrics monitoring error: {e}")
                await asyncio.sleep(60)

    async def _monitor_database_metrics(self):
        """Monitor database metrics"""
        while self.monitoring_active:
            try:
                # Get database connection count
                db_connections = await self._get_database_connections()
                ACTIVE_CONNECTIONS.set(db_connections)

                # Check database connection threshold
                if db_connections > self.alert_thresholds["database_connections"]:
                    await self._create_alert(
                        "high_db_connections",
                        "warning",
                        "High Database Connections",
                        f"Database connections: {db_connections} (threshold: {self.alert_thresholds['database_connections']})",
                        "database",
                    )

                # Get database query performance
                query_metrics = await self._get_database_query_metrics()
                for query_name, duration in query_metrics.items():
                    DATABASE_QUERY_DURATION.labels(query=query_name).observe(duration)

                await self._store_metric(
                    "database_connections", db_connections, {"type": "database"}
                )

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Database metrics monitoring error: {e}")
                await asyncio.sleep(60)

    async def _monitor_cache_metrics(self):
        """Monitor cache metrics"""
        while self.monitoring_active:
            try:
                # Get cache statistics
                cache_stats = await self._get_cache_statistics()

                if cache_stats:
                    hit_rate = cache_stats.get("hit_rate", 0)
                    CACHE_HIT_RATIO.set(hit_rate)

                    await self._store_metric(
                        "cache_hit_ratio", hit_rate, {"type": "cache"}
                    )
                    await self._store_metric(
                        "cache_memory_usage",
                        cache_stats.get("used_memory", 0),
                        {"type": "cache"},
                    )

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Cache metrics monitoring error: {e}")
                await asyncio.sleep(60)

    async def _check_alerts(self):
        """Check and process alerts"""
        while self.monitoring_active:
            try:
                # Process unresolved alerts
                unresolved_alerts = [
                    alert for alert in self.alerts if not alert.resolved
                ]

                for alert in unresolved_alerts:
                    # Send alert notifications
                    await self._send_alert_notification(alert)

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.error(f"Alert checking error: {e}")
                await asyncio.sleep(60)

    async def _cleanup_old_metrics(self):
        """Clean up old metrics to prevent memory issues"""
        while self.monitoring_active:
            try:
                # Remove metrics older than 24 hours
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.metrics = [m for m in self.metrics if m.timestamp > cutoff_time]

                # Remove resolved alerts older than 7 days
                cutoff_time = datetime.now() - timedelta(days=7)
                self.alerts = [
                    a
                    for a in self.alerts
                    if not (
                        a.resolved and a.resolved_at and a.resolved_at < cutoff_time
                    )
                ]

                await asyncio.sleep(3600)  # Cleanup every hour

            except Exception as e:
                logger.error(f"Metrics cleanup error: {e}")
                await asyncio.sleep(60)

    async def _create_alert(
        self, alert_id: str, severity: str, title: str, message: str, source: str
    ):
        """Create a new alert"""
        # Check if alert already exists and is unresolved
        existing_alert = next(
            (a for a in self.alerts if a.id == alert_id and not a.resolved), None
        )
        if existing_alert:
            return  # Alert already exists

        alert = Alert(
            id=alert_id,
            severity=severity,
            title=title,
            message=message,
            timestamp=datetime.now(),
            source=source,
        )

        self.alerts.append(alert)
        logger.warning(f"Alert created: {title} - {message}")

    async def _store_metric(self, name: str, value: float, tags: Dict[str, str]):
        """Store metric data"""
        metric = Metric(name=name, value=value, timestamp=datetime.now(), tags=tags)

        self.metrics.append(metric)

        # Store in Redis for persistence
        try:
            key = f"metrics:{name}:{int(time.time())}"
            self.redis_client.setex(
                key, 86400, json.dumps(asdict(metric), default=str)
            )  # 24 hour TTL
        except Exception as e:
            logger.error(f"Error storing metric in Redis: {e}")

    async def _get_application_metrics(self) -> Dict[str, float]:
        """Get application-specific metrics"""
        try:
            # This would typically come from your application
            return {
                "request_rate": 100.0,
                "error_rate": 2.5,
                "response_time": 0.5,
                "active_users": 150.0,
            }
        except Exception as e:
            logger.error(f"Error getting application metrics: {e}")
            return {}

    async def _get_database_connections(self) -> int:
        """Get current database connection count"""
        try:
            # This would typically query your database
            return 25  # Example value
        except Exception as e:
            logger.error(f"Error getting database connections: {e}")
            return 0

    async def _get_database_query_metrics(self) -> Dict[str, float]:
        """Get database query performance metrics"""
        try:
            # This would typically come from your database monitoring
            return {
                "user_queries": 0.1,
                "transaction_queries": 0.2,
                "analytics_queries": 0.5,
            }
        except Exception as e:
            logger.error(f"Error getting database query metrics: {e}")
            return {}

    async def _get_cache_statistics(self) -> Optional[Dict[str, Any]]:
        """Get cache statistics"""
        try:
            info = self.redis_client.info()
            hits = info.get("keyspace_hits", 0)
            misses = info.get("keyspace_misses", 0)
            hit_rate = hits / max(hits + misses, 1)

            return {
                "hit_rate": hit_rate,
                "used_memory": info.get("used_memory", 0),
                "connected_clients": info.get("connected_clients", 0),
            }
        except Exception as e:
            logger.error(f"Error getting cache statistics: {e}")
            return None

    async def _send_alert_notification(self, alert: Alert):
        """Send alert notification via email/SMS/etc."""
        try:
            # Email notification
            await self._send_email_alert(alert)

            # Log alert
            logger.warning(f"Alert notification sent: {alert.title}")

        except Exception as e:
            logger.error(f"Error sending alert notification: {e}")

    async def _send_email_alert(self, alert: Alert):
        """Send email alert notification"""
        try:
            # This would typically use your email service
            subject = f"[NEXUS ALERT] {alert.severity.upper()}: {alert.title}"
            body = f"""
            Alert Details:
            - Severity: {alert.severity}
            - Source: {alert.source}
            - Time: {alert.timestamp}
            - Message: {alert.message}
            """

            # In a real implementation, you would send the email here
            logger.info(f"Email alert would be sent: {subject}")

        except Exception as e:
            logger.error(f"Error sending email alert: {e}")

    async def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status"""
        try:
            # Get recent metrics
            recent_metrics = [
                m
                for m in self.metrics
                if m.timestamp > datetime.now() - timedelta(minutes=5)
            ]

            # Get active alerts
            active_alerts = [a for a in self.alerts if not a.resolved]

            # Calculate health score
            health_score = 100
            if any(a.severity == "critical" for a in active_alerts):
                health_score -= 50
            if any(a.severity == "warning" for a in active_alerts):
                health_score -= 20

            return {
                "status": "healthy"
                if health_score > 80
                else "degraded"
                if health_score > 50
                else "unhealthy",
                "health_score": health_score,
                "active_alerts": len(active_alerts),
                "critical_alerts": len(
                    [a for a in active_alerts if a.severity == "critical"]
                ),
                "warning_alerts": len(
                    [a for a in active_alerts if a.severity == "warning"]
                ),
                "metrics_count": len(recent_metrics),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {"status": "error", "error": str(e)}

    async def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.id == alert_id and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                logger.info(f"Alert resolved: {alert.title}")
                break


# Global monitoring instance
monitoring_system = MonitoringSystem()


# Usage example
async def main():
    """Example usage of monitoring system"""
    try:
        # Start monitoring
        await monitoring_system.start_monitoring(port=8001)
    except KeyboardInterrupt:
        logger.info("Monitoring system stopped")
    except Exception as e:
        logger.error(f"Monitoring system error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
