#!/usr/bin/env python3
"""
NEXUS Platform - Monitoring and Observability with SSOT Metrics
Comprehensive monitoring system with SSOT-specific metrics and observability
"""

import asyncio
import json
import logging
import queue
import signal
import sys
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union

import aiohttp
import prometheus_client
import psutil
from prometheus_client import (CollectorRegistry, Counter, Gauge, Histogram,
                               Summary)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SSOTMetrics:
    """SSOT-specific metrics"""

    total_anchors: int
    total_aliases: int
    alias_resolution_time: float
    conflict_count: int
    conflict_resolution_time: float
    cache_hit_rate: float
    validation_errors: int
    last_validation: datetime
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SystemMetrics:
    """System performance metrics"""

    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_sent_mb: float
    network_recv_mb: float
    load_average: List[float]
    timestamp: datetime


@dataclass
class ApplicationMetrics:
    """Application-specific metrics"""

    request_count: int
    request_duration: float
    error_count: int
    active_connections: int
    queue_size: int
    cache_size: int
    ssot_operations: int
    timestamp: datetime


@dataclass
class AlertRule:
    """Alert rule definition"""

    name: str
    metric: str
    condition: str
    threshold: float
    severity: str  # low, medium, high, critical
    enabled: bool
    cooldown: int  # seconds
    last_triggered: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Alert:
    """Alert instance"""

    id: str
    rule_name: str
    severity: str
    message: str
    metric_value: float
    threshold: float
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class MonitoringSystem:
    """
    Comprehensive Monitoring and Observability System
    Provides:
    - SSOT-specific metrics collection
    - System performance monitoring
    - Application metrics tracking
    - Alerting and notification
    - Prometheus metrics export
    - Health checks and status reporting
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.registry = CollectorRegistry()
        self.metrics_queue = queue.Queue()
        self.alerts_queue = queue.Queue()
        self.running = False
        self.collection_thread = None
        self.alert_thread = None

        # Initialize Prometheus metrics
        self._init_prometheus_metrics()

        # Initialize alert rules
        self.alert_rules = self._load_alert_rules()

        # Metrics storage
        self.metrics_history = {"ssot": [], "system": [], "application": []}

        # Alert storage
        self.active_alerts = {}
        self.alert_history = []

        # Performance tracking
        self.performance_data = {
            "start_time": datetime.now(timezone.utc),
            "total_requests": 0,
            "total_errors": 0,
            "average_response_time": 0.0,
        }

    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        # SSOT Metrics
        self.ssot_anchors_total = Gauge(
            "ssot_anchors_total", "Total number of SSOT anchors", registry=self.registry
        )

        self.ssot_aliases_total = Gauge(
            "ssot_aliases_total", "Total number of SSOT aliases", registry=self.registry
        )

        self.ssot_alias_resolution_duration = Histogram(
            "ssot_alias_resolution_duration_seconds",
            "Time spent resolving aliases",
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
            registry=self.registry,
        )

        self.ssot_conflicts_total = Counter(
            "ssot_conflicts_total",
            "Total number of SSOT conflicts",
            registry=self.registry,
        )

        self.ssot_cache_hit_rate = Gauge(
            "ssot_cache_hit_rate", "SSOT cache hit rate (0-1)", registry=self.registry
        )

        self.ssot_validation_errors = Counter(
            "ssot_validation_errors_total",
            "Total number of SSOT validation errors",
            registry=self.registry,
        )

        # System Metrics
        self.system_cpu_percent = Gauge(
            "system_cpu_percent", "CPU usage percentage", registry=self.registry
        )

        self.system_memory_percent = Gauge(
            "system_memory_percent", "Memory usage percentage", registry=self.registry
        )

        self.system_memory_used_bytes = Gauge(
            "system_memory_used_bytes", "Memory used in bytes", registry=self.registry
        )

        self.system_disk_usage_percent = Gauge(
            "system_disk_usage_percent", "Disk usage percentage", registry=self.registry
        )

        self.system_load_average = Gauge(
            "system_load_average",
            "System load average",
            ["period"],  # 1min, 5min, 15min
            registry=self.registry,
        )

        # Application Metrics
        self.app_requests_total = Counter(
            "app_requests_total",
            "Total number of requests",
            ["method", "endpoint", "status"],
            registry=self.registry,
        )

        self.app_request_duration = Histogram(
            "app_request_duration_seconds",
            "Request duration in seconds",
            ["method", "endpoint"],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry,
        )

        self.app_errors_total = Counter(
            "app_errors_total",
            "Total number of errors",
            ["error_type", "endpoint"],
            registry=self.registry,
        )

        self.app_active_connections = Gauge(
            "app_active_connections",
            "Number of active connections",
            registry=self.registry,
        )

        self.app_queue_size = Gauge(
            "app_queue_size", "Queue size", registry=self.registry
        )

        self.app_cache_size = Gauge(
            "app_cache_size", "Cache size", registry=self.registry
        )

        # Health check metrics
        self.health_check_status = Gauge(
            "health_check_status",
            "Health check status (1=healthy, 0=unhealthy)",
            ["service"],
            registry=self.registry,
        )

    def _load_alert_rules(self) -> List[AlertRule]:
        """Load alert rules from configuration"""
        default_rules = [
            AlertRule(
                name="high_cpu_usage",
                metric="system_cpu_percent",
                condition=">",
                threshold=80.0,
                severity="high",
                enabled=True,
                cooldown=300,
            ),
            AlertRule(
                name="high_memory_usage",
                metric="system_memory_percent",
                condition=">",
                threshold=85.0,
                severity="high",
                enabled=True,
                cooldown=300,
            ),
            AlertRule(
                name="low_disk_space",
                metric="system_disk_usage_percent",
                condition=">",
                threshold=90.0,
                severity="critical",
                enabled=True,
                cooldown=600,
            ),
            AlertRule(
                name="high_error_rate",
                metric="app_errors_total",
                condition=">",
                threshold=10.0,
                severity="medium",
                enabled=True,
                cooldown=180,
            ),
            AlertRule(
                name="ssot_validation_errors",
                metric="ssot_validation_errors_total",
                condition=">",
                threshold=5.0,
                severity="medium",
                enabled=True,
                cooldown=300,
            ),
            AlertRule(
                name="low_cache_hit_rate",
                metric="ssot_cache_hit_rate",
                condition="<",
                threshold=0.7,
                severity="low",
                enabled=True,
                cooldown=600,
            ),
        ]

        # Load custom rules from config
        custom_rules = self.config.get("alert_rules", [])
        for rule_data in custom_rules:
            rule = AlertRule(**rule_data)
            default_rules.append(rule)

        return default_rules

    async def start(self):
        """Start the monitoring system"""
        if self.running:
            logger.warning("Monitoring system already running")
            return

        self.running = True
        logger.info("Starting monitoring system")

        # Start collection thread
        self.collection_thread = threading.Thread(target=self._collection_loop)
        self.collection_thread.daemon = True
        self.collection_thread.start()

        # Start alert processing thread
        self.alert_thread = threading.Thread(target=self._alert_loop)
        self.alert_thread.daemon = True
        self.alert_thread.start()

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("Monitoring system started")

    async def stop(self):
        """Stop the monitoring system"""
        if not self.running:
            return

        logger.info("Stopping monitoring system")
        self.running = False

        # Wait for threads to finish
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        if self.alert_thread:
            self.alert_thread.join(timeout=5)

        logger.info("Monitoring system stopped")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(self.stop())
        sys.exit(0)

    def _collection_loop(self):
        """Main metrics collection loop"""
        while self.running:
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                self.metrics_queue.put(("system", system_metrics))

                # Collect application metrics
                app_metrics = self._collect_application_metrics()
                self.metrics_queue.put(("application", app_metrics))

                # Update Prometheus metrics
                self._update_prometheus_metrics(system_metrics, app_metrics)

                # Sleep for collection interval
                time.sleep(self.config.get("collection_interval", 10))

            except Exception as e:
                logger.error(f"Error in collection loop: {e}")
                time.sleep(5)

    def _alert_loop(self):
        """Alert processing loop"""
        while self.running:
            try:
                # Process metrics queue
                while not self.metrics_queue.empty():
                    metric_type, metrics = self.metrics_queue.get_nowait()
                    self._process_metrics_for_alerts(metric_type, metrics)

                # Check for resolved alerts
                self._check_resolved_alerts()

                time.sleep(1)

            except Exception as e:
                logger.error(f"Error in alert loop: {e}")
                time.sleep(5)

    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            memory_available_mb = memory.available / (1024 * 1024)

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_usage_percent = (disk.used / disk.total) * 100
            disk_free_gb = disk.free / (1024 * 1024 * 1024)

            # Network usage
            network = psutil.net_io_counters()
            network_sent_mb = network.bytes_sent / (1024 * 1024)
            network_recv_mb = network.bytes_recv / (1024 * 1024)

            # Load average
            load_average = list(psutil.getloadavg())

            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                memory_available_mb=memory_available_mb,
                disk_usage_percent=disk_usage_percent,
                disk_free_gb=disk_free_gb,
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb,
                load_average=load_average,
                timestamp=datetime.now(timezone.utc),
            )

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return SystemMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_mb=0.0,
                memory_available_mb=0.0,
                disk_usage_percent=0.0,
                disk_free_gb=0.0,
                network_sent_mb=0.0,
                network_recv_mb=0.0,
                load_average=[0.0, 0.0, 0.0],
                timestamp=datetime.now(timezone.utc),
            )

    def _collect_application_metrics(self) -> ApplicationMetrics:
        """Collect application-specific metrics"""
        try:
            # This would be implemented based on your application's metrics
            # For now, return placeholder values
            return ApplicationMetrics(
                request_count=self.performance_data["total_requests"],
                request_duration=self.performance_data["average_response_time"],
                error_count=self.performance_data["total_errors"],
                active_connections=0,  # Would be tracked by application
                queue_size=self.metrics_queue.qsize(),
                cache_size=0,  # Would be tracked by cache service
                ssot_operations=0,  # Would be tracked by SSOT integration
                timestamp=datetime.now(timezone.utc),
            )

        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
            return ApplicationMetrics(
                request_count=0,
                request_duration=0.0,
                error_count=0,
                active_connections=0,
                queue_size=0,
                cache_size=0,
                ssot_operations=0,
                timestamp=datetime.now(timezone.utc),
            )

    def _update_prometheus_metrics(
        self, system_metrics: SystemMetrics, app_metrics: ApplicationMetrics
    ):
        """Update Prometheus metrics"""
        try:
            # System metrics
            self.system_cpu_percent.set(system_metrics.cpu_percent)
            self.system_memory_percent.set(system_metrics.memory_percent)
            self.system_memory_used_bytes.set(
                system_metrics.memory_used_mb * 1024 * 1024
            )
            self.system_disk_usage_percent.set(system_metrics.disk_usage_percent)

            # Load average
            for i, period in enumerate(["1min", "5min", "15min"]):
                if i < len(system_metrics.load_average):
                    self.system_load_average.labels(period=period).set(
                        system_metrics.load_average[i]
                    )

            # Application metrics
            self.app_active_connections.set(app_metrics.active_connections)
            self.app_queue_size.set(app_metrics.queue_size)
            self.app_cache_size.set(app_metrics.cache_size)

        except Exception as e:
            logger.error(f"Error updating Prometheus metrics: {e}")

    def _process_metrics_for_alerts(self, metric_type: str, metrics: Any):
        """Process metrics to check for alert conditions"""
        try:
            for rule in self.alert_rules:
                if not rule.enabled:
                    continue

                # Check if rule is in cooldown
                if rule.last_triggered:
                    time_since_triggered = (
                        datetime.now(timezone.utc) - rule.last_triggered
                    ).total_seconds()
                    if time_since_triggered < rule.cooldown:
                        continue

                # Get metric value
                metric_value = self._get_metric_value(rule.metric, metric_type, metrics)
                if metric_value is None:
                    continue

                # Check condition
                if self._evaluate_condition(
                    metric_value, rule.condition, rule.threshold
                ):
                    self._trigger_alert(rule, metric_value)

        except Exception as e:
            logger.error(f"Error processing metrics for alerts: {e}")

    def _get_metric_value(
        self, metric_name: str, metric_type: str, metrics: Any
    ) -> Optional[float]:
        """Get metric value from metrics object"""
        try:
            if metric_type == "system" and hasattr(metrics, metric_name):
                return getattr(metrics, metric_name)
            elif metric_type == "application" and hasattr(metrics, metric_name):
                return getattr(metrics, metric_name)
            return None
        except Exception:
            return None

    def _evaluate_condition(
        self, value: float, condition: str, threshold: float
    ) -> bool:
        """Evaluate alert condition"""
        try:
            if condition == ">":
                return value > threshold
            elif condition == ">=":
                return value >= threshold
            elif condition == "<":
                return value < threshold
            elif condition == "<=":
                return value <= threshold
            elif condition == "==":
                return value == threshold
            elif condition == "!=":
                return value != threshold
            else:
                logger.warning(f"Unknown condition: {condition}")
                return False
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False

    def _trigger_alert(self, rule: AlertRule, metric_value: float):
        """Trigger an alert"""
        try:
            alert_id = f"{rule.name}_{int(time.time())}"

            alert = Alert(
                id=alert_id,
                rule_name=rule.name,
                severity=rule.severity,
                message=f"{rule.name}: {rule.metric} {rule.condition} {rule.threshold} (current: {metric_value})",
                metric_value=metric_value,
                threshold=rule.threshold,
                timestamp=datetime.now(timezone.utc),
                metadata={"rule": asdict(rule)},
            )

            # Add to active alerts
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)

            # Update rule last triggered time
            rule.last_triggered = datetime.now(timezone.utc)

            # Send notification
            self._send_alert_notification(alert)

            logger.warning(f"Alert triggered: {alert.message}")

        except Exception as e:
            logger.error(f"Error triggering alert: {e}")

    def _check_resolved_alerts(self):
        """Check for resolved alerts"""
        try:
            current_time = datetime.now(timezone.utc)
            resolved_alerts = []

            for alert_id, alert in self.active_alerts.items():
                if alert.resolved:
                    continue

                # Check if alert should be resolved based on current metrics
                # This is a simplified implementation
                time_since_alert = (current_time - alert.timestamp).total_seconds()
                if time_since_alert > 300:  # 5 minutes
                    alert.resolved = True
                    alert.resolved_at = current_time
                    resolved_alerts.append(alert_id)

            # Remove resolved alerts from active alerts
            for alert_id in resolved_alerts:
                del self.active_alerts[alert_id]
                logger.info(f"Alert resolved: {alert_id}")

        except Exception as e:
            logger.error(f"Error checking resolved alerts: {e}")

    def _send_alert_notification(self, alert: Alert):
        """Send alert notification"""
        try:
            # This would integrate with notification services
            # For now, just log the alert
            logger.warning(f"ALERT: {alert.severity.upper()} - {alert.message}")

            # Could send to Slack, email, PagerDuty, etc.
            if self.config.get("notifications", {}).get("enabled", False):
                self._send_to_notification_service(alert)

        except Exception as e:
            logger.error(f"Error sending alert notification: {e}")

    def _send_to_notification_service(self, alert: Alert):
        """Send alert to notification service"""
        # Implementation would depend on the notification service
        pass

    def record_ssot_metrics(self, ssot_metrics: SSOTMetrics):
        """Record SSOT-specific metrics"""
        try:
            # Update Prometheus metrics
            self.ssot_anchors_total.set(ssot_metrics.total_anchors)
            self.ssot_aliases_total.set(ssot_metrics.total_aliases)
            self.ssot_alias_resolution_duration.observe(
                ssot_metrics.alias_resolution_time
            )
            self.ssot_conflicts_total.inc(ssot_metrics.conflict_count)
            self.ssot_cache_hit_rate.set(ssot_metrics.cache_hit_rate)
            self.ssot_validation_errors.inc(ssot_metrics.validation_errors)

            # Store in history
            self.metrics_history["ssot"].append(ssot_metrics)

            # Keep only last 1000 entries
            if len(self.metrics_history["ssot"]) > 1000:
                self.metrics_history["ssot"] = self.metrics_history["ssot"][-1000:]

        except Exception as e:
            logger.error(f"Error recording SSOT metrics: {e}")

    def record_request(
        self, method: str, endpoint: str, status_code: int, duration: float
    ):
        """Record HTTP request metrics"""
        try:
            # Update Prometheus metrics
            self.app_requests_total.labels(
                method=method, endpoint=endpoint, status=status_code
            ).inc()

            self.app_request_duration.labels(method=method, endpoint=endpoint).observe(
                duration
            )

            # Update performance data
            self.performance_data["total_requests"] += 1
            if status_code >= 400:
                self.performance_data["total_errors"] += 1

            # Update average response time
            total_requests = self.performance_data["total_requests"]
            current_avg = self.performance_data["average_response_time"]
            self.performance_data["average_response_time"] = (
                current_avg * (total_requests - 1) + duration
            ) / total_requests

        except Exception as e:
            logger.error(f"Error recording request: {e}")

    def record_error(self, error_type: str, endpoint: str):
        """Record error metrics"""
        try:
            self.app_errors_total.labels(error_type=error_type, endpoint=endpoint).inc()

        except Exception as e:
            logger.error(f"Error recording error: {e}")

    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        try:
            current_time = datetime.now(timezone.utc)
            uptime = (
                current_time - self.performance_data["start_time"]
            ).total_seconds()

            # Calculate health score
            health_score = 100.0

            # Deduct points for errors
            error_rate = self.performance_data["total_errors"] / max(
                self.performance_data["total_requests"], 1
            )
            health_score -= min(
                error_rate * 100, 50
            )  # Max 50 points deduction for errors

            # Deduct points for active alerts
            critical_alerts = sum(
                1
                for alert in self.active_alerts.values()
                if alert.severity == "critical"
            )
            high_alerts = sum(
                1 for alert in self.active_alerts.values() if alert.severity == "high"
            )

            health_score -= critical_alerts * 20
            health_score -= high_alerts * 10

            health_score = max(0, health_score)

            return {
                "status": "healthy"
                if health_score >= 80
                else "degraded"
                if health_score >= 50
                else "unhealthy",
                "health_score": health_score,
                "uptime_seconds": uptime,
                "total_requests": self.performance_data["total_requests"],
                "total_errors": self.performance_data["total_errors"],
                "error_rate": error_rate,
                "average_response_time": self.performance_data["average_response_time"],
                "active_alerts": len(self.active_alerts),
                "critical_alerts": critical_alerts,
                "high_alerts": high_alerts,
                "timestamp": current_time.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        try:
            return {
                "system": {
                    "cpu_percent": self.system_cpu_percent._value._value,
                    "memory_percent": self.system_memory_percent._value._value,
                    "disk_usage_percent": self.system_disk_usage_percent._value._value,
                },
                "application": {
                    "total_requests": self.performance_data["total_requests"],
                    "total_errors": self.performance_data["total_errors"],
                    "average_response_time": self.performance_data[
                        "average_response_time"
                    ],
                    "active_connections": self.app_active_connections._value._value,
                    "queue_size": self.app_queue_size._value._value,
                },
                "ssot": {
                    "total_anchors": self.ssot_anchors_total._value._value,
                    "total_aliases": self.ssot_aliases_total._value._value,
                    "cache_hit_rate": self.ssot_cache_hit_rate._value._value,
                    "conflicts_total": self.ssot_conflicts_total._value._value,
                    "validation_errors": self.ssot_validation_errors._value._value,
                },
                "alerts": {
                    "active": len(self.active_alerts),
                    "total_history": len(self.alert_history),
                },
            }

        except Exception as e:
            logger.error(f"Error getting metrics summary: {e}")
            return {"error": str(e)}

    def export_prometheus_metrics(self) -> str:
        """Export Prometheus metrics in text format"""
        try:
            from prometheus_client import generate_latest

            return generate_latest(self.registry).decode("utf-8")
        except Exception as e:
            logger.error(f"Error exporting Prometheus metrics: {e}")
            return ""


# Example usage and testing
async def main():
    """
    Example usage of MonitoringSystem
    """
    # Initialize monitoring system
    config = {
        "collection_interval": 10,
        "alert_rules": [
            {
                "name": "test_alert",
                "metric": "system_cpu_percent",
                "condition": ">",
                "threshold": 50.0,
                "severity": "low",
                "enabled": True,
                "cooldown": 60,
            }
        ],
        "notifications": {"enabled": True},
    }

    monitoring = MonitoringSystem(config)

    # Start monitoring
    await monitoring.start()

    try:
        # Simulate some activity
        for i in range(10):
            # Record some requests
            monitoring.record_request("GET", "/api/test", 200, 0.1)
            monitoring.record_request("POST", "/api/data", 201, 0.2)

            # Record some errors
            if i % 3 == 0:
                monitoring.record_error("validation_error", "/api/data")

            # Record SSOT metrics
            ssot_metrics = SSOTMetrics(
                total_anchors=100 + i,
                total_aliases=500 + i * 10,
                alias_resolution_time=0.05 + i * 0.001,
                conflict_count=i,
                conflict_resolution_time=0.1 + i * 0.01,
                cache_hit_rate=0.8 + i * 0.01,
                validation_errors=i,
                last_validation=datetime.now(timezone.utc),
            )
            monitoring.record_ssot_metrics(ssot_metrics)

            # Wait a bit
            await asyncio.sleep(2)

        # Get health status
        health = monitoring.get_health_status()
        print(f"Health status: {health}")

        # Get metrics summary
        summary = monitoring.get_metrics_summary()
        print(f"Metrics summary: {summary}")

        # Export Prometheus metrics
        prometheus_metrics = monitoring.export_prometheus_metrics()
        print(f"Prometheus metrics:\n{prometheus_metrics}")

    finally:
        # Stop monitoring
        await monitoring.stop()


if __name__ == "__main__":
    asyncio.run(main())
