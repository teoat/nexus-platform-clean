#!/usr/bin/env python3
"""
AI Monitoring and Alerting Service
Intelligent monitoring, anomaly detection, and automated incident response
"""

import asyncio
import json
import logging
import smtplib
import socket
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import psutil

logger = logging.getLogger(__name__)


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


class AnomalyType(Enum):
    SPIKE = "spike"
    DROP = "drop"
    TREND_CHANGE = "trend_change"
    SEASONAL_DEVIATION = "seasonal_deviation"
    OUTLIER = "outlier"


class IncidentStatus(Enum):
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


@dataclass
class MetricData:
    """Time-series metric data"""

    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str]


@dataclass
class AnomalyDetection:
    """Detected anomaly"""

    anomaly_id: str
    metric_name: str
    anomaly_type: AnomalyType
    severity: AlertSeverity
    confidence_score: float
    expected_value: float
    actual_value: float
    deviation_percent: float
    timestamp: datetime
    evidence: List[str]


@dataclass
class Alert:
    """System alert"""

    alert_id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    source: str
    affected_components: List[str]
    created_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    assigned_to: Optional[str]
    tags: List[str]


@dataclass
class Incident:
    """System incident"""

    incident_id: str
    title: str
    description: str
    severity: AlertSeverity
    status: IncidentStatus
    root_cause: Optional[str]
    impact_assessment: str
    created_at: datetime
    detected_at: datetime
    resolved_at: Optional[datetime]
    alerts: List[str]
    affected_services: List[str]
    timeline: List[Dict[str, Any]]


class AIMonitoringAlertingService:
    """AI-powered monitoring and alerting service"""

    def __init__(self):
        self.metrics_buffer: Dict[str, List[MetricData]] = {}
        self.anomalies: Dict[str, AnomalyDetection] = {}
        self.alerts: Dict[str, Alert] = {}
        self.incidents: Dict[str, Incident] = {}

        # Configuration
        self.monitoring_config = {
            "metrics_collection_interval": 30,  # seconds
            "anomaly_detection_window": 10,  # data points
            "alert_cooldown_minutes": 5,
            "auto_resolve_threshold_minutes": 10,
            "escalation_threshold_minutes": 30,
        }

        self.alert_rules = {
            "cpu_usage_high": {
                "metric": "system.cpu.usage",
                "condition": "value > 90",
                "severity": AlertSeverity.HIGH,
                "description": "CPU usage above 90%",
            },
            "memory_usage_critical": {
                "metric": "system.memory.usage",
                "condition": "value > 95",
                "severity": AlertSeverity.CRITICAL,
                "description": "Memory usage above 95%",
            },
            "error_rate_spike": {
                "metric": "application.error_rate",
                "condition": "anomaly_type == 'SPIKE' and deviation_percent > 200",
                "severity": AlertSeverity.HIGH,
                "description": "Error rate spike detected",
            },
            "response_time_degraded": {
                "metric": "application.response_time",
                "condition": "value > 5000",  # 5 seconds
                "severity": AlertSeverity.MEDIUM,
                "description": "Response time degraded",
            },
        }

        self.baseline_metrics: Dict[str, Dict[str, Any]] = {}
        self.active_alerts: Dict[str, datetime] = {}  # alert_id -> last_triggered

        # Start monitoring loop only if event loop is running (not during testing)
        try:
            asyncio.get_running_loop()
            asyncio.create_task(self._monitoring_loop())
        except RuntimeError:
            # No event loop running (e.g., during testing), skip background tasks
            pass

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while True:
            try:
                await self._collect_system_metrics()
                await self._detect_anomalies()
                await self._evaluate_alert_rules()
                await self._manage_incidents()
                await self._cleanup_old_data()
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")

            await asyncio.sleep(self.monitoring_config["metrics_collection_interval"])

    async def _collect_system_metrics(self):
        """Collect system and application metrics"""
        timestamp = datetime.now()

        # System metrics
        system_metrics = [
            MetricData(
                "system.cpu.usage", psutil.cpu_percent(), timestamp, {"type": "system"}
            ),
            MetricData(
                "system.memory.usage",
                psutil.virtual_memory().percent,
                timestamp,
                {"type": "system"},
            ),
            MetricData(
                "system.disk.usage",
                psutil.disk_usage("/").percent,
                timestamp,
                {"type": "system"},
            ),
            MetricData(
                "system.network.connections",
                len(psutil.net_connections()),
                timestamp,
                {"type": "system"},
            ),
        ]

        # Application metrics (mock data - would come from actual app metrics)
        app_metrics = [
            MetricData(
                "application.response_time",
                150.0,
                timestamp,
                {"endpoint": "/api/health"},
            ),
            MetricData("application.error_rate", 0.02, timestamp, {"service": "api"}),
            MetricData(
                "application.requests_per_second", 125.0, timestamp, {"service": "api"}
            ),
            MetricData(
                "application.active_connections",
                45,
                timestamp,
                {"service": "websocket"},
            ),
        ]

        # Store metrics
        for metric in system_metrics + app_metrics:
            if metric.name not in self.metrics_buffer:
                self.metrics_buffer[metric.name] = []
            self.metrics_buffer[metric.name].append(metric)

            # Keep only recent data (last 24 hours)
            cutoff = timestamp - timedelta(hours=24)
            self.metrics_buffer[metric.name] = [
                m for m in self.metrics_buffer[metric.name] if m.timestamp > cutoff
            ]

    async def _detect_anomalies(self):
        """Detect anomalies in metrics using statistical analysis"""
        for metric_name, metrics in self.metrics_buffer.items():
            if len(metrics) < self.monitoring_config["anomaly_detection_window"]:
                continue

            # Get recent values
            recent_values = [
                m.value
                for m in metrics[-self.monitoring_config["anomaly_detection_window"] :]
            ]
            current_value = recent_values[-1]

            # Calculate baseline statistics
            if len(recent_values) >= 5:
                mean = statistics.mean(recent_values[:-1])  # Exclude current value
                stdev = (
                    statistics.stdev(recent_values[:-1])
                    if len(recent_values) > 1
                    else 0
                )

                if stdev > 0:
                    z_score = abs(current_value - mean) / stdev

                    # Detect different types of anomalies
                    anomaly_type = None
                    deviation_percent = 0

                    if z_score > 3:  # 3 standard deviations
                        if current_value > mean:
                            anomaly_type = AnomalyType.SPIKE
                        else:
                            anomaly_type = AnomalyType.DROP
                        deviation_percent = ((current_value - mean) / mean) * 100

                    elif z_score > 2:  # 2 standard deviations
                        anomaly_type = AnomalyType.OUTLIER
                        deviation_percent = ((current_value - mean) / mean) * 100

                    if anomaly_type:
                        confidence_score = min(z_score / 3, 1.0)  # Normalize confidence

                        # Determine severity
                        if z_score > 4:
                            severity = AlertSeverity.CRITICAL
                        elif z_score > 3:
                            severity = AlertSeverity.HIGH
                        elif z_score > 2:
                            severity = AlertSeverity.MEDIUM
                        else:
                            severity = AlertSeverity.LOW

                        anomaly = AnomalyDetection(
                            anomaly_id=f"anomaly_{metric_name}_{datetime.now().strftime('%H%M%S')}",
                            metric_name=metric_name,
                            anomaly_type=anomaly_type,
                            severity=severity,
                            confidence_score=confidence_score,
                            expected_value=mean,
                            actual_value=current_value,
                            deviation_percent=deviation_percent,
                            timestamp=datetime.now(),
                            evidence=[
                                f"Z-score: {z_score:.2f}",
                                f"Expected: {mean:.2f}, Actual: {current_value:.2f}",
                                f"Deviation: {deviation_percent:.1f}%",
                            ],
                        )

                        self.anomalies[anomaly.anomaly_id] = anomaly

                        # Create alert for significant anomalies
                        if confidence_score > 0.7:
                            await self._create_anomaly_alert(anomaly)

    async def _evaluate_alert_rules(self):
        """Evaluate alert rules against current metrics"""
        for rule_name, rule_config in self.alert_rules.items():
            metric_name = rule_config["metric"]

            if metric_name not in self.metrics_buffer:
                continue

            latest_metric = (
                self.metrics_buffer[metric_name][-1]
                if self.metrics_buffer[metric_name]
                else None
            )
            if not latest_metric:
                continue

            # Check cooldown
            last_triggered = self.active_alerts.get(rule_name)
            if last_triggered and (datetime.now() - last_triggered) < timedelta(
                minutes=self.monitoring_config["alert_cooldown_minutes"]
            ):
                continue

            # Evaluate condition
            condition = rule_config["condition"]
            if self._evaluate_condition(condition, latest_metric.value, latest_metric):
                await self._trigger_alert(rule_name, rule_config, latest_metric)
                self.active_alerts[rule_name] = datetime.now()

    def _evaluate_condition(
        self, condition: str, value: float, metric: MetricData
    ) -> bool:
        """Evaluate alert condition"""
        try:
            # Simple condition evaluation (in production, use a proper expression evaluator)
            if "value >" in condition:
                threshold = float(condition.split(">")[-1].strip())
                return value > threshold
            elif "value <" in condition:
                threshold = float(condition.split("<")[-1].strip())
                return value < threshold
            elif "anomaly_type ==" in condition:
                # Check for recent anomalies
                recent_anomalies = [
                    a
                    for a in self.anomalies.values()
                    if a.metric_name == metric.name
                    and (datetime.now() - a.timestamp) < timedelta(minutes=5)
                ]
                if recent_anomalies:
                    anomaly_type_str = condition.split("==")[-1].strip().strip("'\"")
                    return any(
                        a.anomaly_type.value == anomaly_type_str
                        for a in recent_anomalies
                    )
        except:
            pass
        return False

    async def _trigger_alert(
        self, rule_name: str, rule_config: Dict[str, Any], metric: MetricData
    ):
        """Trigger an alert"""
        alert_id = f"alert_{rule_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        alert = Alert(
            alert_id=alert_id,
            title=f"Alert: {rule_config['description']}",
            description=f"{rule_config['description']} - Current value: {metric.value:.2f}",
            severity=rule_config["severity"],
            status=AlertStatus.ACTIVE,
            source="ai_monitoring",
            affected_components=[metric.labels.get("service", "system")],
            created_at=datetime.now(),
            acknowledged_at=None,
            resolved_at=None,
            assigned_to=None,
            tags=["automated", rule_name],
        )

        self.alerts[alert_id] = alert

        logger.warning(f"Alert triggered: {alert.title}")

        # Send notifications
        await self._send_alert_notifications(alert)

        # Auto-escalate critical alerts
        if alert.severity == AlertSeverity.CRITICAL:
            await self._escalate_alert(alert)

    async def _create_anomaly_alert(self, anomaly: AnomalyDetection):
        """Create alert for detected anomaly"""
        alert_id = f"anomaly_alert_{anomaly.anomaly_id}"

        alert = Alert(
            alert_id=alert_id,
            title=f"Anomaly Detected: {anomaly.metric_name}",
            description=f"{anomaly.anomaly_type.value.title()} anomaly in {anomaly.metric_name} "
            f"(deviation: {anomaly.deviation_percent:.1f}%)",
            severity=anomaly.severity,
            status=AlertStatus.ACTIVE,
            source="anomaly_detection",
            affected_components=["monitoring"],
            created_at=datetime.now(),
            acknowledged_at=None,
            resolved_at=None,
            assigned_to=None,
            tags=["anomaly", "ai_detected", anomaly.metric_name],
        )

        self.alerts[alert_id] = alert

        # Create incident for high-severity anomalies
        if anomaly.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            await self._create_incident_from_anomaly(anomaly, alert)

    async def _create_incident_from_anomaly(
        self, anomaly: AnomalyDetection, alert: Alert
    ):
        """Create incident from anomaly"""
        incident_id = f"incident_{anomaly.anomaly_id}"

        incident = Incident(
            incident_id=incident_id,
            title=f"Performance Anomaly: {anomaly.metric_name}",
            description=f"AI detected {anomaly.anomaly_type.value} in {anomaly.metric_name} "
            f"with {anomaly.deviation_percent:.1f}% deviation",
            severity=anomaly.severity,
            status=IncidentStatus.DETECTED,
            root_cause=None,
            impact_assessment="Investigating potential performance impact",
            created_at=datetime.now(),
            detected_at=anomaly.timestamp,
            resolved_at=None,
            alerts=[alert.alert_id],
            affected_services=["monitoring"],
            timeline=[
                {
                    "timestamp": datetime.now().isoformat(),
                    "event": "Incident created from anomaly detection",
                    "details": f"Anomaly confidence: {anomaly.confidence_score:.2f}",
                }
            ],
        )

        self.incidents[incident_id] = incident
        logger.error(f"Incident created: {incident.title}")

    async def _manage_incidents(self):
        """Manage active incidents"""
        for incident in list(self.incidents.values()):
            if incident.status == IncidentStatus.DETECTED:
                # Auto-escalate if not acknowledged within threshold
                if (datetime.now() - incident.created_at) > timedelta(
                    minutes=self.monitoring_config["escalation_threshold_minutes"]
                ):
                    incident.status = IncidentStatus.ESCALATED
                    incident.timeline.append(
                        {
                            "timestamp": datetime.now().isoformat(),
                            "event": "Incident auto-escalated",
                            "details": "No response within escalation threshold",
                        }
                    )
                    await self._escalate_incident(incident)

            elif incident.status == IncidentStatus.INVESTIGATING:
                # Auto-resolve if all alerts are resolved
                related_alerts = [
                    self.alerts.get(aid)
                    for aid in incident.alerts
                    if aid in self.alerts
                ]
                if all(a.status == AlertStatus.RESOLVED for a in related_alerts if a):
                    incident.status = IncidentStatus.RESOLVED
                    incident.resolved_at = datetime.now()
                    incident.timeline.append(
                        {
                            "timestamp": datetime.now().isoformat(),
                            "event": "Incident auto-resolved",
                            "details": "All related alerts resolved",
                        }
                    )

    async def _send_alert_notifications(self, alert: Alert):
        """Send alert notifications"""
        # Email notification
        await self._send_email_alert(alert)

        # Slack notification (mock)
        await self._send_slack_alert(alert)

        # PagerDuty for critical alerts
        if alert.severity == AlertSeverity.CRITICAL:
            await self._send_pagerduty_alert(alert)

    async def _send_email_alert(self, alert: Alert):
        """Send email alert"""
        try:
            # Mock email sending
            logger.info(f"Email alert sent: {alert.title}")
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")

    async def _send_slack_alert(self, alert: Alert):
        """Send Slack alert"""
        try:
            # Mock Slack sending
            logger.info(f"Slack alert sent: {alert.title}")
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")

    async def _send_pagerduty_alert(self, alert: Alert):
        """Send PagerDuty alert"""
        try:
            # Mock PagerDuty sending
            logger.info(f"PagerDuty alert sent: {alert.title}")
        except Exception as e:
            logger.error(f"Failed to send PagerDuty alert: {e}")

    async def _escalate_alert(self, alert: Alert):
        """Escalate alert"""
        logger.warning(f"Alert escalated: {alert.title}")

        # Additional notifications for escalation
        await self._send_escalation_notifications(alert)

    async def _escalate_incident(self, incident: Incident):
        """Escalate incident"""
        logger.error(f"Incident escalated: {incident.title}")

        # Notify incident response team
        await self._notify_incident_response_team(incident)

    async def _send_escalation_notifications(self, alert: Alert):
        """Send escalation notifications"""
        # Additional email to escalation contacts
        pass

    async def _notify_incident_response_team(self, incident: Incident):
        """Notify incident response team"""
        # Call incident response team
        pass

    async def acknowledge_alert(self, alert_id: str, user: str) -> bool:
        """Acknowledge an alert"""
        alert = self.alerts.get(alert_id)
        if not alert or alert.status != AlertStatus.ACTIVE:
            return False

        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.now()
        alert.assigned_to = user

        logger.info(f"Alert acknowledged by {user}: {alert.title}")
        return True

    async def resolve_alert(self, alert_id: str, user: str) -> bool:
        """Resolve an alert"""
        alert = self.alerts.get(alert_id)
        if not alert:
            return False

        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.now()

        logger.info(f"Alert resolved by {user}: {alert.title}")
        return True

    async def update_incident_status(
        self, incident_id: str, status: IncidentStatus, user: str, notes: str = ""
    ) -> bool:
        """Update incident status"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return False

        old_status = incident.status
        incident.status = status

        if status == IncidentStatus.RESOLVED:
            incident.resolved_at = datetime.now()

        incident.timeline.append(
            {
                "timestamp": datetime.now().isoformat(),
                "event": f"Status changed from {old_status.value} to {status.value}",
                "user": user,
                "notes": notes,
            }
        )

        logger.info(
            f"Incident {incident_id} status updated to {status.value} by {user}"
        )
        return True

    async def get_system_health_score(self) -> float:
        """Get overall system health score"""
        # Calculate health score based on active alerts and incidents
        active_alerts = [
            a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE
        ]
        active_incidents = [
            i
            for i in self.incidents.values()
            if i.status in [IncidentStatus.DETECTED, IncidentStatus.INVESTIGATING]
        ]

        # Base score
        health_score = 1.0

        # Deduct for active alerts
        alert_penalty = len(active_alerts) * 0.05  # 5% per alert
        health_score -= min(alert_penalty, 0.3)  # Max 30% deduction

        # Deduct for active incidents
        incident_penalty = len(active_incidents) * 0.1  # 10% per incident
        health_score -= min(incident_penalty, 0.4)  # Max 40% deduction

        # Deduct for critical severity
        critical_penalty = (
            sum(1 for a in active_alerts if a.severity == AlertSeverity.CRITICAL) * 0.15
        )
        health_score -= min(critical_penalty, 0.3)  # Max 30% deduction

        return max(0.0, health_score)

    async def get_monitoring_dashboard_data(self) -> Dict[str, Any]:
        """Get data for monitoring dashboard"""
        # Current metrics
        current_metrics = {}
        for metric_name, metrics in self.metrics_buffer.items():
            if metrics:
                current_metrics[metric_name] = metrics[-1].value

        # Recent alerts (last 24 hours)
        recent_alerts = [
            asdict(alert)
            for alert in self.alerts.values()
            if alert.created_at > datetime.now() - timedelta(hours=24)
        ]

        # Active incidents
        active_incidents = [
            asdict(incident)
            for incident in self.incidents.values()
            if incident.status
            in [
                IncidentStatus.DETECTED,
                IncidentStatus.INVESTIGATING,
                IncidentStatus.ESCALATED,
            ]
        ]

        # Anomaly summary (last hour)
        recent_anomalies = [
            asdict(anomaly)
            for anomaly in self.anomalies.values()
            if anomaly.timestamp > datetime.now() - timedelta(hours=1)
        ]

        return {
            "current_metrics": current_metrics,
            "system_health_score": await self.get_system_health_score(),
            "active_alerts_count": len(
                [a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE]
            ),
            "active_incidents_count": len(active_incidents),
            "recent_alerts": recent_alerts[-10:],  # Last 10
            "active_incidents": active_incidents,
            "recent_anomalies": recent_anomalies[-20:],  # Last 20
            "timestamp": datetime.now().isoformat(),
        }

    async def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        cutoff_date = datetime.now() - timedelta(days=7)

        # Clean old metrics (keep only last 24 hours in buffer, but clean old anomalies/alerts)
        self.anomalies = {
            aid: anomaly
            for aid, anomaly in self.anomalies.items()
            if anomaly.timestamp > cutoff_date
        }

        # Keep resolved alerts for 7 days, active alerts indefinitely
        self.alerts = {
            aid: alert
            for aid, alert in self.alerts.items()
            if alert.status != AlertStatus.RESOLVED or alert.resolved_at > cutoff_date
        }

        # Keep resolved incidents for 30 days
        incident_cutoff = datetime.now() - timedelta(days=30)
        self.incidents = {
            iid: incident
            for iid, incident in self.incidents.items()
            if incident.status != IncidentStatus.RESOLVED
            or incident.resolved_at > incident_cutoff
        }

    async def predict_incidents(self) -> List[Dict[str, Any]]:
        """Predict potential incidents based on trends"""
        predictions = []

        # Analyze trends in key metrics
        for metric_name in [
            "system.cpu.usage",
            "application.error_rate",
            "application.response_time",
        ]:
            if metric_name not in self.metrics_buffer:
                continue

            metrics = self.metrics_buffer[metric_name]
            if len(metrics) < 10:
                continue

            # Simple trend analysis
            recent_values = [m.value for m in metrics[-10:]]
            trend = self._calculate_trend(recent_values)

            if (
                trend == "worsening"
                and recent_values[-1] > statistics.mean(recent_values[:-1]) * 1.2
            ):
                predictions.append(
                    {
                        "metric": metric_name,
                        "prediction": "potential_incident",
                        "confidence": 0.75,
                        "timeframe": "next_2_hours",
                        "description": f"{metric_name} showing worsening trend",
                        "recommended_action": "Increase monitoring frequency",
                    }
                )

        return predictions

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from values"""
        if len(values) < 3:
            return "stable"

        # Simple linear regression slope
        n = len(values)
        x = list(range(n))
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)

        numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, values))
        denominator = sum((xi - x_mean) ** 2 for xi in x)

        if denominator == 0:
            return "stable"

        slope = numerator / denominator

        if slope > 0.1:
            return "improving" if values[0] < values[-1] else "worsening"
        elif slope < -0.1:
            return "worsening" if values[0] > values[-1] else "improving"
        else:
            return "stable"


# Global instance
ai_monitoring_alerting_service = AIMonitoringAlertingService()
