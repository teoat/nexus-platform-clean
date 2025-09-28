#!/usr/bin/env python3
"""
🚨 NEXUS Platform - Smart Alerting System
Intelligent alerting with dynamic thresholds, correlation, and automated response
"""

import asyncio
import json
import logging
import os
import smtplib
import threading
import time
from datetime import datetime, timedelta

import redis
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import monitoring components
try:
    MONITORING_INTEGRATION = True
except ImportError:
    MONITORING_INTEGRATION = False
    logger.warning("⚠️ Monitoring components not available, running in standalone mode")


class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class AlertChannel(Enum):
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    PAGERDUTY = "pagerduty"


@dataclass
class AlertRule:
    rule_id: str
    name: str
    description: str
    metric_name: str
    condition: str
    threshold: float
    severity: AlertSeverity
    channels: List[AlertChannel]
    enabled: bool
    cooldown_minutes: int
    escalation_minutes: int
    tags: List[str]
    created_at: datetime
    updated_at: datetime


@dataclass
class Alert:
    alert_id: str
    rule_id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    metric_value: float
    threshold: float
    timestamp: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    acknowledged_by: Optional[str]
    tags: List[str]
    context: Dict[str, Any]


@dataclass
class AlertCorrelation:
    correlation_id: str
    alerts: List[str]
    pattern: str
    confidence: float
    created_at: datetime


class SmartAlertingSystem:
    """Intelligent Alerting System with Dynamic Thresholds and Correlation"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

        # Initialize Redis for alert storage and caching
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            decode_responses=True,
        )

        # Alert storage
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []

        # Alert correlation
        self.alert_correlations: List[AlertCorrelation] = []
        self.alert_patterns: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))

        # Dynamic threshold calculation
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.baseline_metrics: Dict[str, Dict[str, float]] = {}

        # Notification channels
        self.notification_channels = self._setup_notification_channels()

        # Alert processing
        self.alert_queue = asyncio.Queue()
        self.processing_active = False

        # Start background processing
        self._start_background_processing()

        logger.info("🚨 Smart Alerting System initialized")

        # Auto-create monitoring-based alert rules if integration available
        if MONITORING_INTEGRATION:
            self._create_monitoring_alert_rules()

    def _create_monitoring_alert_rules(self):
        """Create alert rules based on monitoring components"""
        try:
            # System health alerts
            self.create_alert_rule(
                name="System Unhealthy",
                description="Overall system health is degraded or unhealthy",
                metric_name="system_health",
                condition="equals",
                threshold=0,  # 0 = unhealthy
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_minutes=5,
                tags=["system", "health"],
            )

            # High CPU usage
            self.create_alert_rule(
                name="High CPU Usage",
                description="CPU usage exceeds safe threshold",
                metric_name="cpu_usage_percent",
                condition="greater_than",
                threshold=85.0,
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.EMAIL],
                cooldown_minutes=10,
                tags=["system", "performance"],
            )

            # High memory usage
            self.create_alert_rule(
                name="High Memory Usage",
                description="Memory usage exceeds safe threshold",
                metric_name="memory_usage_percent",
                condition="greater_than",
                threshold=90.0,
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_minutes=5,
                tags=["system", "performance"],
            )

            # Service health alerts
            services = [
                "user-service",
                "transaction-service",
                "analytics-service",
                "api-gateway",
            ]
            for service in services:
                self.create_alert_rule(
                    name=f"{service.title()} Unhealthy",
                    description=f"{service} health check failed",
                    metric_name=f"{service}_health",
                    condition="equals",
                    threshold=0,
                    severity=AlertSeverity.HIGH,
                    channels=[AlertChannel.EMAIL],
                    cooldown_minutes=2,
                    tags=["service", service],
                )

        except Exception as e:
            logger.error(f"❌ Failed to create monitoring alert rules: {e}")

    def _setup_notification_channels(self) -> Dict[AlertChannel, Dict[str, Any]]:
        """Setup notification channels"""
        return {
            AlertChannel.EMAIL: {
                "smtp_server": self.config.get("smtp_server", "smtp.gmail.com"),
                "smtp_port": self.config.get("smtp_port", 587),
                "username": self.config.get("email_username"),
                "password": self.config.get("email_password"),
                "from_email": self.config.get("from_email", "alerts@nexus.com"),
            },
            AlertChannel.SLACK: {
                "webhook_url": self.config.get("slack_webhook_url"),
                "channel": self.config.get("slack_channel", "#alerts"),
            },
            AlertChannel.WEBHOOK: {
                "url": self.config.get("webhook_url"),
                "headers": self.config.get("webhook_headers", {}),
            },
            AlertChannel.SMS: {
                "api_key": self.config.get("sms_api_key"),
                "from_number": self.config.get("sms_from_number"),
            },
            AlertChannel.PAGERDUTY: {
                "integration_key": self.config.get("pagerduty_integration_key")
            },
        }

    def _start_background_processing(self):
        """Start background alert processing"""

        processor_thread = threading.Thread(target=run_processor, daemon=True)
        processor_thread.start()
        self.processing_active = True

    async def _process_alerts(self):
        """Process alerts in background"""
        while self.processing_active:
            try:
                # Process alert queue
                while not self.alert_queue.empty():
                    alert = await self.alert_queue.get()
                    await self._handle_alert(alert)

                # Check for alert correlations
                await self._check_alert_correlations()

                # Update dynamic thresholds
                await self._update_dynamic_thresholds()

                # Integrate with monitoring systems
                if MONITORING_INTEGRATION:
                    await self._integrate_monitoring_data()

                await asyncio.sleep(1)  # Check every second

            except Exception as e:
                logger.error(f"❌ Alert processing error: {e}")
                await asyncio.sleep(5)

    def create_alert_rule(
        self,
        name: str,
        description: str,
        metric_name: str,
        condition: str,
        threshold: float,
        severity: AlertSeverity,
        channels: List[AlertChannel],
        cooldown_minutes: int = 5,
        escalation_minutes: int = 30,
        tags: List[str] = None,
    ) -> AlertRule:
        """Create new alert rule"""
        rule_id = f"rule_{int(time.time())}_{name.lower().replace(' ', '_')}"

        rule = AlertRule(
            rule_id=rule_id,
            name=name,
            description=description,
            metric_name=metric_name,
            condition=condition,
            threshold=threshold,
            severity=severity,
            channels=channels,
            enabled=True,
            cooldown_minutes=cooldown_minutes,
            escalation_minutes=escalation_minutes,
            tags=tags or [],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.alert_rules[rule_id] = rule

        # Store in Redis
        self.redis_client.hset(f"alert_rule:{rule_id}", mapping=asdict(rule))

        logger.info(f"📋 Alert rule created: {name}")
        return rule

    def evaluate_metric(
        self, metric_name: str, value: float, context: Dict[str, Any] = None
    ) -> List[Alert]:
        """Evaluate metric against alert rules"""
        triggered_alerts = []

        # Store metric in history
        self.metric_history[metric_name].append(
            {"value": value, "timestamp": datetime.now(), "context": context or {}}
        )

        # Check each rule for this metric
        for rule_id, rule in self.alert_rules.items():
            if not rule.enabled or rule.metric_name != metric_name:
                continue

            # Check if rule should trigger
            if self._should_trigger_alert(rule, value, context):
                # Check cooldown
                if self._is_in_cooldown(rule_id):
                    continue

                # Create alert
                alert = self._create_alert(rule, value, context)
                triggered_alerts.append(alert)

                # Add to processing queue
                asyncio.create_task(self.alert_queue.put(alert))

        return triggered_alerts

    def _should_trigger_alert(
        self, rule: AlertRule, value: float, context: Dict[str, Any]
    ) -> bool:
        """Check if alert rule should trigger"""
        # Use dynamic threshold if available
        threshold = self._get_dynamic_threshold(rule.metric_name, rule.threshold)

        if rule.condition == "greater_than":
            return value > threshold
        elif rule.condition == "less_than":
            return value < threshold
        elif rule.condition == "equals":
            return abs(value - threshold) < 0.01
        elif rule.condition == "not_equals":
            return abs(value - threshold) >= 0.01
        elif rule.condition == "anomaly":
            return self._detect_anomaly(rule.metric_name, value)

        return False

    def _get_dynamic_threshold(
        self, metric_name: str, default_threshold: float
    ) -> float:
        """Get dynamic threshold based on historical data"""
        if metric_name not in self.baseline_metrics:
            return default_threshold

        baseline = self.baseline_metrics[metric_name]

        # Calculate dynamic threshold based on baseline + 2 standard deviations
        mean = baseline.get("mean", default_threshold)
        std = baseline.get("std", 0)

        return mean + (2 * std)

    def _detect_anomaly(self, metric_name: str, value: float) -> bool:
        """Detect anomaly using statistical methods"""
        if metric_name not in self.metric_history:
            return False

        history = list(self.metric_history[metric_name])
        if len(history) < 10:
            return False

        values = [h["value"] for h in history[-50:]]  # Last 50 values
        mean = np.mean(values)
        std = np.std(values)

        if std == 0:
            return False

        # Z-score anomaly detection
        z_score = abs(value - mean) / std
        return z_score > 3  # 3-sigma rule

    def _is_in_cooldown(self, rule_id: str) -> bool:
        """Check if rule is in cooldown period"""
        cooldown_key = f"alert_cooldown:{rule_id}"
        cooldown_end = self.redis_client.get(cooldown_key)

        if cooldown_end:
            cooldown_time = datetime.fromisoformat(cooldown_end)
            return datetime.now() < cooldown_time

        return False

    def _create_alert(
        self, rule: AlertRule, value: float, context: Dict[str, Any]
    ) -> Alert:
        """Create new alert"""
        alert_id = f"alert_{int(time.time())}_{rule.rule_id}"

        alert = Alert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            title=f"{rule.name} - {rule.severity.value.upper()}",
            description=f"{rule.description}\nCurrent value: {value:.2f}, Threshold: {rule.threshold:.2f}",
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            metric_value=value,
            threshold=rule.threshold,
            timestamp=datetime.now(),
            acknowledged_at=None,
            resolved_at=None,
            acknowledged_by=None,
            tags=rule.tags.copy(),
            context=context or {},
        )

        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)

        # Set cooldown
        cooldown_end = datetime.now() + timedelta(minutes=rule.cooldown_minutes)
        self.redis_client.setex(
            f"alert_cooldown:{rule.rule_id}",
            rule.cooldown_minutes * 60,
            cooldown_end.isoformat(),
        )

        return alert

    async def _handle_alert(self, alert: Alert):
        """Handle alert processing and notifications"""
        try:
            # Send notifications
            await self._send_notifications(alert)

            # Store in Redis
            self.redis_client.hset(f"alert:{alert.alert_id}", mapping=asdict(alert))

            # Add to alert patterns for correlation
            self.alert_patterns[alert.rule_id].append(alert)

            logger.info(f"🚨 Alert processed: {alert.title}")

        except Exception as e:
            logger.error(f"❌ Alert handling error: {e}")

    async def _send_notifications(self, alert: Alert):
        """Send notifications through configured channels"""
        rule = self.alert_rules[alert.rule_id]

        for channel in rule.channels:
            try:
                if channel == AlertChannel.EMAIL:
                    await self._send_email_notification(alert)
                elif channel == AlertChannel.SLACK:
                    await self._send_slack_notification(alert)
                elif channel == AlertChannel.WEBHOOK:
                    await self._send_webhook_notification(alert)
                elif channel == AlertChannel.SMS:
                    await self._send_sms_notification(alert)
                elif channel == AlertChannel.PAGERDUTY:
                    await self._send_pagerduty_notification(alert)

            except Exception as e:
                logger.error(f"❌ Notification failed for {channel.value}: {e}")

    async def _send_email_notification(self, alert: Alert):
        """Send email notification"""
        config = self.notification_channels[AlertChannel.EMAIL]

        if not config["username"] or not config["password"]:
            logger.warning("⚠️ Email credentials not configured")
            return

        msg = MIMEMultipart()
        msg["From"] = config["from_email"]
        msg["To"] = self.config.get("alert_email_recipients", "admin@nexus.com")
        msg["Subject"] = f"🚨 {alert.title}"

        body = f"""
        Alert Details:
        - Title: {alert.title}
        - Description: {alert.description}
        - Severity: {alert.severity.value.upper()}
        - Timestamp: {alert.timestamp.isoformat()}
        - Metric Value: {alert.metric_value:.2f}
        - Threshold: {alert.threshold:.2f}

        Context: {json.dumps(alert.context, indent=2)}
        """

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(config["smtp_server"], config["smtp_port"]) as server:
            server.starttls()
            server.login(config["username"], config["password"])
            server.send_message(msg)

    async def _send_slack_notification(self, alert: Alert):
        """Send Slack notification"""
        config = self.notification_channels[AlertChannel.SLACK]

        if not config["webhook_url"]:
            logger.warning("⚠️ Slack webhook not configured")
            return

        severity_colors = {
            AlertSeverity.LOW: "#36a64f",
            AlertSeverity.MEDIUM: "#ffaa00",
            AlertSeverity.HIGH: "#ff6b6b",
            AlertSeverity.CRITICAL: "#8b0000",
        }

        payload = {
            "channel": config["channel"],
            "username": "NEXUS Alerts",
            "icon_emoji": ":warning:",
            "attachments": [
                {
                    "color": severity_colors[alert.severity],
                    "title": alert.title,
                    "text": alert.description,
                    "fields": [
                        {
                            "title": "Severity",
                            "value": alert.severity.value.upper(),
                            "short": True,
                        },
                        {
                            "title": "Metric Value",
                            "value": f"{alert.metric_value:.2f}",
                            "short": True,
                        },
                        {
                            "title": "Threshold",
                            "value": f"{alert.threshold:.2f}",
                            "short": True,
                        },
                        {
                            "title": "Timestamp",
                            "value": alert.timestamp.isoformat(),
                            "short": True,
                        },
                    ],
                    "footer": "NEXUS Platform",
                    "ts": int(alert.timestamp.timestamp()),
                }
            ],
        }

        requests.post(config["webhook_url"], json=payload)

    async def _send_webhook_notification(self, alert: Alert):
        """Send webhook notification"""
        config = self.notification_channels[AlertChannel.WEBHOOK]

        if not config["url"]:
            logger.warning("⚠️ Webhook URL not configured")
            return

        payload = {
            "alert_id": alert.alert_id,
            "title": alert.title,
            "description": alert.description,
            "severity": alert.severity.value,
            "status": alert.status.value,
            "metric_value": alert.metric_value,
            "threshold": alert.threshold,
            "timestamp": alert.timestamp.isoformat(),
            "context": alert.context,
        }

        requests.post(config["url"], json=payload, headers=config["headers"])

    async def _send_sms_notification(self, alert: Alert):
        """Send SMS notification"""
        config = self.notification_channels[AlertChannel.SMS]

        if not config["api_key"]:
            logger.warning("⚠️ SMS API key not configured")
            return

        # Simplified SMS sending (would use actual SMS service)
        message = f"ALERT: {alert.title} - {alert.description}"
        logger.info(f"📱 SMS: {message}")

    async def _send_pagerduty_notification(self, alert: Alert):
        """Send PagerDuty notification"""
        config = self.notification_channels[AlertChannel.PAGERDUTY]

        if not config["integration_key"]:
            logger.warning("⚠️ PagerDuty integration key not configured")
            return

        payload = {
            "routing_key": config["integration_key"],
            "event_action": "trigger",
            "dedup_key": alert.alert_id,
            "payload": {
                "summary": alert.title,
                "source": "NEXUS Platform",
                "severity": alert.severity.value,
                "custom_details": {
                    "description": alert.description,
                    "metric_value": alert.metric_value,
                    "threshold": alert.threshold,
                    "context": alert.context,
                },
            },
        }

        requests.post("https://events.pagerduty.com/v2/enqueue", json=payload)

    async def _check_alert_correlations(self):
        """Check for alert correlations and patterns"""
        # Group alerts by time window
        recent_alerts = [
            alert
            for alert in self.alert_history
            if (datetime.now() - alert.timestamp).minutes < 5
        ]

        if len(recent_alerts) < 2:
            return

        # Look for correlation patterns
        correlation_patterns = self._find_correlation_patterns(recent_alerts)

        for pattern in correlation_patterns:
            correlation = AlertCorrelation(
                correlation_id=f"corr_{int(time.time())}",
                alerts=[alert.alert_id for alert in pattern["alerts"]],
                pattern=pattern["pattern"],
                confidence=pattern["confidence"],
                created_at=datetime.now(),
            )

            self.alert_correlations.append(correlation)
            logger.info(f"🔗 Alert correlation detected: {pattern['pattern']}")

    def _find_correlation_patterns(self, alerts: List[Alert]) -> List[Dict[str, Any]]:
        """Find correlation patterns in alerts"""
        patterns = []

        # Group by service/component
        service_groups = defaultdict(list)
        for alert in alerts:
            service = alert.context.get("service", "unknown")
            service_groups[service].append(alert)

        # Check for service-wide issues
        for service, service_alerts in service_groups.items():
            if len(service_alerts) >= 3:
                patterns.append(
                    {
                        "alerts": service_alerts,
                        "pattern": f"Service-wide issue in {service}",
                        "confidence": min(0.9, len(service_alerts) / 10),
                    }
                )

        # Check for severity escalation
        severity_escalation = []
        for alert in alerts:
            if alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                severity_escalation.append(alert)

        if len(severity_escalation) >= 2:
            patterns.append(
                {
                    "alerts": severity_escalation,
                    "pattern": "Severity escalation detected",
                    "confidence": 0.8,
                }
            )

        return patterns

    async def _update_dynamic_thresholds(self):
        """Update dynamic thresholds based on historical data"""
        for metric_name, history in self.metric_history.items():
            if len(history) < 20:  # Need at least 20 data points
                continue

            values = [h["value"] for h in history]

            self.baseline_metrics[metric_name] = {
                "mean": np.mean(values),
                "std": np.std(values),
                "min": np.min(values),
                "max": np.max(values),
                "updated_at": datetime.now().isoformat(),
            }

    async def _integrate_monitoring_data(self):
        """Integrate data from monitoring systems"""
        try:
            # Check system health from health manager
            if hasattr(health_manager, "get_health_report"):
                health_report = health_manager.get_health_report()
                if health_report.overall_status == "unhealthy":
                    self.evaluate_metric(
                        "system_health",
                        0,
                        context={"health_report": health_report.summary},
                    )
                elif health_report.overall_status == "degraded":
                    self.evaluate_metric(
                        "system_health",
                        1,
                        context={"health_report": health_report.summary},
                    )

            # Check metrics from Prometheus collector
            if hasattr(metrics_collector, "get_metrics_summary"):
                metrics_summary = metrics_collector.get_metrics_summary()
                system_metrics = metrics_summary.get("system_metrics", {})

                # Evaluate CPU usage
                cpu_usage = system_metrics.get("cpu_usage", 0)
                self.evaluate_metric(
                    "cpu_usage_percent", cpu_usage, context={"source": "prometheus"}
                )

                # Evaluate memory usage
                memory_usage = system_metrics.get("memory_usage", 0)
                self.evaluate_metric(
                    "memory_usage_percent",
                    memory_usage,
                    context={"source": "prometheus"},
                )

            # Check APM anomalies
            try:
                apm_monitor = get_apm_monitor("nexus-platform")
                anomalies = apm_monitor.detect_anomalies()

                for anomaly in anomalies:
                    anomaly_type = anomaly["type"]
                    severity_map = {
                        "cpu_spike": AlertSeverity.HIGH,
                        "memory_leak": AlertSeverity.CRITICAL,
                        "slow_operations": AlertSeverity.MEDIUM,
                    }

                    severity = severity_map.get(anomaly_type, AlertSeverity.MEDIUM)

                    # Create dynamic alert rule if it doesn't exist
                    rule_name = f"APM {anomaly_type.replace('_', ' ').title()}"
                    if not any(
                        rule.name == rule_name for rule in self.alert_rules.values()
                    ):
                        self.create_alert_rule(
                            name=rule_name,
                            description=anomaly["message"],
                            metric_name=f"apm_{anomaly_type}",
                            condition="greater_than",
                            threshold=0,
                            severity=severity,
                            channels=[AlertChannel.EMAIL],
                            cooldown_minutes=15,
                            tags=["apm", "anomaly", anomaly_type],
                        )

                    # Trigger alert
                    self.evaluate_metric(
                        f"apm_{anomaly_type}", 1, context={"anomaly_details": anomaly}
                    )

            except Exception as e:
                logger.debug(f"APM integration not available: {e}")

        except Exception as e:
            logger.error(f"❌ Monitoring integration error: {e}")

    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert system summary"""
        return {
            "total_rules": len(self.alert_rules),
            "active_alerts": len(self.active_alerts),
            "total_alerts": len(self.alert_history),
            "alert_correlations": len(self.alert_correlations),
            "metrics_monitored": len(self.metric_history),
            "baseline_metrics": len(self.baseline_metrics),
            "severity_distribution": {
                severity.value: len(
                    [a for a in self.active_alerts.values() if a.severity == severity]
                )
                for severity in AlertSeverity
            },
            "recent_alerts": [
                {
                    "alert_id": alert.alert_id,
                    "title": alert.title,
                    "severity": alert.severity.value,
                    "status": alert.status.value,
                    "timestamp": alert.timestamp.isoformat(),
                }
                for alert in list(self.active_alerts.values())[-10:]
            ],
        }

    def get_alert_analytics(self, time_range: str = "24h") -> Dict[str, Any]:
        """Get alert analytics for time range"""
        # Calculate time range
        now = datetime.now()
        if time_range == "1h":
            start_time = now - timedelta(hours=1)
        elif time_range == "24h":
            start_time = now - timedelta(days=1)
        elif time_range == "7d":
            start_time = now - timedelta(days=7)
        else:
            start_time = now - timedelta(hours=1)

        # Filter alerts by time range
        recent_alerts = [
            alert for alert in self.alert_history if alert.timestamp >= start_time
        ]

        # Calculate statistics
        total_alerts = len(recent_alerts)
        resolved_alerts = len(
            [a for a in recent_alerts if a.status == AlertStatus.RESOLVED]
        )
        acknowledged_alerts = len(
            [a for a in recent_alerts if a.status == AlertStatus.ACKNOWLEDGED]
        )

        # Severity distribution
        severity_dist = {}
        for severity in AlertSeverity:
            severity_dist[severity.value] = len(
                [a for a in recent_alerts if a.severity == severity]
            )

        # Rule distribution
        rule_dist = {}
        for alert in recent_alerts:
            rule_id = alert.rule_id
            rule_dist[rule_id] = rule_dist.get(rule_id, 0) + 1

        return {
            "time_range": time_range,
            "total_alerts": total_alerts,
            "resolved_alerts": resolved_alerts,
            "acknowledged_alerts": acknowledged_alerts,
            "resolution_rate": resolved_alerts / max(1, total_alerts),
            "severity_distribution": severity_dist,
            "top_rules": dict(
                sorted(rule_dist.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
            "average_resolution_time": self._calculate_avg_resolution_time(
                recent_alerts
            ),
        }

    def _calculate_avg_resolution_time(self, alerts: List[Alert]) -> float:
        """Calculate average resolution time in minutes"""
        resolved_alerts = [
            alert
            for alert in alerts
            if alert.status == AlertStatus.RESOLVED and alert.resolved_at
        ]

        if not resolved_alerts:
            return 0.0

        total_time = 0.0
        for alert in resolved_alerts:
            resolution_time = (alert.resolved_at - alert.timestamp).total_seconds() / 60
            total_time += resolution_time

        return total_time / len(resolved_alerts)


# Configuration
ALERTING_CONFIG = {
    "redis_host": "localhost",
    "redis_port": 6379,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "email_username": os.getenv("EMAIL_USERNAME"),
    "email_password": os.getenv("EMAIL_PASSWORD"),
    "from_email": "alerts@nexus.com",
    "alert_email_recipients": "admin@nexus.com",
    "slack_webhook_url": os.getenv("SLACK_WEBHOOK_URL"),
    "slack_channel": "#alerts",
    "webhook_url": os.getenv("WEBHOOK_URL"),
    "webhook_headers": {"Content-Type": "application/json"},
    "sms_api_key": os.getenv("SMS_API_KEY"),
    "sms_from_number": os.getenv("SMS_FROM_NUMBER"),
    "pagerduty_integration_key": os.getenv("PAGERDUTY_INTEGRATION_KEY"),
}

# Initialize Smart Alerting System
alerting_system = SmartAlertingSystem(ALERTING_CONFIG)

if __name__ == "__main__":
    # Example usage
    async def main():
        # Create alert rules
        cpu_rule = alerting_system.create_alert_rule(
            name="High CPU Usage",
            description="CPU usage exceeds threshold",
            metric_name="cpu_usage",
            condition="greater_than",
            threshold=80.0,
            severity=AlertSeverity.HIGH,
            channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
            cooldown_minutes=5,
            tags=["infrastructure", "performance"],
        )

        memory_rule = alerting_system.create_alert_rule(
            name="High Memory Usage",
            description="Memory usage exceeds threshold",
            metric_name="memory_usage",
            condition="greater_than",
            threshold=90.0,
            severity=AlertSeverity.CRITICAL,
            channels=[AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.PAGERDUTY],
            cooldown_minutes=2,
            tags=["infrastructure", "performance"],
        )

        # Simulate metric evaluation
        alerts = alerting_system.evaluate_metric(
            "cpu_usage", 85.5, context={"host": "server1", "service": "api"}
        )

        print(f"🚨 Triggered alerts: {len(alerts)}")

        # Get alert summary
        summary = alerting_system.get_alert_summary()
        print(f"📊 Alert Summary: {json.dumps(summary, indent=2)}")

        # Get analytics
        analytics = alerting_system.get_alert_analytics("1h")
        print(f"📈 Analytics: {json.dumps(analytics, indent=2)}")

    asyncio.run(main())
