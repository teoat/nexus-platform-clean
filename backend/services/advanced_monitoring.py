#!/usr/bin/env python3
"""
NEXUS Platform - Advanced Monitoring & Analytics System
Phase 2: Monitoring & Analytics Implementation
"""

import asyncio
import logging
import time
import psutil
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import redis
import sqlite3
from collections import defaultdict, deque
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Metric data structure"""
    name: str
    value: Union[int, float]
    metric_type: MetricType
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """Alert data structure"""
    id: str
    name: str
    level: AlertLevel
    message: str
    timestamp: datetime
    metric_name: str
    threshold_value: float
    current_value: float
    resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceData:
    """Performance data structure"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io: Dict[str, int]
    active_connections: int
    response_time_avg: float
    error_rate: float


class AdvancedMonitoringSystem:
    """Advanced monitoring and analytics system"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None, db_path: str = "monitoring.db"):
        self.redis_client = redis_client
        self.db_path = db_path
        
        # Metrics storage
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alerts: List[Alert] = []
        self.performance_history: deque = deque(maxlen=1000)
        
        # Alert thresholds
        self.thresholds = {
            "cpu_percent": {"warning": 70, "critical": 90},
            "memory_percent": {"warning": 80, "critical": 95},
            "disk_usage_percent": {"warning": 85, "critical": 95},
            "response_time_avg": {"warning": 2.0, "critical": 5.0},
            "error_rate": {"warning": 5.0, "critical": 10.0}
        }
        
        # Monitoring configuration
        self.collection_interval = 30  # seconds
        self.alert_cooldown = 300  # 5 minutes
        self.last_alert_times: Dict[str, datetime] = {}
        
        # Initialize database
        self._init_database()
        
        # Start background monitoring
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
    
    def _init_database(self):
        """Initialize SQLite database for metrics storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                metric_type TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                tags TEXT,
                metadata TEXT
            )
        """)
        
        # Create alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                metric_name TEXT NOT NULL,
                threshold_value REAL NOT NULL,
                current_value REAL NOT NULL,
                resolved BOOLEAN DEFAULT FALSE,
                metadata TEXT
            )
        """)
        
        # Create performance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                cpu_percent REAL NOT NULL,
                memory_percent REAL NOT NULL,
                disk_usage_percent REAL NOT NULL,
                network_io TEXT NOT NULL,
                active_connections INTEGER NOT NULL,
                response_time_avg REAL NOT NULL,
                error_rate REAL NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def record_metric(self, name: str, value: Union[int, float], 
                     metric_type: MetricType = MetricType.GAUGE,
                     tags: Dict[str, str] = None, metadata: Dict[str, Any] = None):
        """Record a metric"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            timestamp=datetime.now(),
            tags=tags or {},
            metadata=metadata or {}
        )
        
        # Store in memory
        self.metrics[name].append(metric)
        
        # Store in database
        self._store_metric_to_db(metric)
        
        # Check for alerts
        self._check_metric_alerts(metric)
        
        logger.debug(f"Recorded metric: {name} = {value}")
    
    def _store_metric_to_db(self, metric: Metric):
        """Store metric to SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO metrics (name, value, metric_type, timestamp, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                metric.name,
                metric.value,
                metric.metric_type.value,
                metric.timestamp.isoformat(),
                json.dumps(metric.tags),
                json.dumps(metric.metadata)
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error storing metric to database: {e}")
    
    def _check_metric_alerts(self, metric: Metric):
        """Check if metric triggers any alerts"""
        if metric.name not in self.thresholds:
            return
        
        thresholds = self.thresholds[metric.name]
        current_time = datetime.now()
        
        # Check warning threshold
        if metric.value >= thresholds.get("warning", float('inf')):
            alert_level = AlertLevel.WARNING
            threshold_value = thresholds["warning"]
            
            # Check critical threshold
            if metric.value >= thresholds.get("critical", float('inf')):
                alert_level = AlertLevel.CRITICAL
                threshold_value = thresholds["critical"]
            
            # Check cooldown
            alert_key = f"{metric.name}_{alert_level.value}"
            if alert_key in self.last_alert_times:
                time_since_last = (current_time - self.last_alert_times[alert_key]).seconds
                if time_since_last < self.alert_cooldown:
                    return
            
            # Create alert
            alert = Alert(
                id=f"{metric.name}_{current_time.timestamp()}",
                name=f"{metric.name} threshold exceeded",
                level=alert_level,
                message=f"{metric.name} is {metric.value} (threshold: {threshold_value})",
                timestamp=current_time,
                metric_name=metric.name,
                threshold_value=threshold_value,
                current_value=metric.value,
                metadata={"tags": metric.tags}
            )
            
            self.alerts.append(alert)
            self.last_alert_times[alert_key] = current_time
            
            # Store alert in database
            self._store_alert_to_db(alert)
            
            logger.warning(f"Alert triggered: {alert.message}")
    
    def _store_alert_to_db(self, alert: Alert):
        """Store alert to SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO alerts (id, name, level, message, timestamp, metric_name, 
                                 threshold_value, current_value, resolved, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.id,
                alert.name,
                alert.level.value,
                alert.message,
                alert.timestamp.isoformat(),
                alert.metric_name,
                alert.threshold_value,
                alert.current_value,
                alert.resolved,
                json.dumps(alert.metadata)
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error storing alert to database: {e}")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                self._collect_system_metrics()
                
                # Collect performance data
                self._collect_performance_data()
                
                # Clean up old data
                self._cleanup_old_data()
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.collection_interval)
    
    def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_metric("cpu_percent", cpu_percent, tags={"host": "localhost"})
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.record_metric("memory_percent", memory.percent, tags={"host": "localhost"})
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.record_metric("disk_usage_percent", disk_percent, tags={"host": "localhost"})
            
            # Network I/O
            network = psutil.net_io_counters()
            self.record_metric("network_bytes_sent", network.bytes_sent, MetricType.COUNTER)
            self.record_metric("network_bytes_recv", network.bytes_recv, MetricType.COUNTER)
            
            # Process count
            process_count = len(psutil.pids())
            self.record_metric("process_count", process_count, tags={"host": "localhost"})
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def _collect_performance_data(self):
        """Collect application performance data"""
        try:
            # Get current metrics
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            disk_percent = (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
            
            # Network I/O
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
            
            # Calculate response time and error rate (simplified)
            response_time_avg = self._calculate_avg_response_time()
            error_rate = self._calculate_error_rate()
            
            # Create performance data
            perf_data = PerformanceData(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_usage_percent=disk_percent,
                network_io=network_io,
                active_connections=self._get_active_connections(),
                response_time_avg=response_time_avg,
                error_rate=error_rate
            )
            
            # Store in memory
            self.performance_history.append(perf_data)
            
            # Store in database
            self._store_performance_to_db(perf_data)
            
        except Exception as e:
            logger.error(f"Error collecting performance data: {e}")
    
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time (simplified)"""
        # This would typically come from your application metrics
        # For now, return a simulated value
        return 0.5 + (psutil.cpu_percent() / 100) * 2.0
    
    def _calculate_error_rate(self) -> float:
        """Calculate error rate (simplified)"""
        # This would typically come from your application metrics
        # For now, return a simulated value based on system load
        cpu_percent = psutil.cpu_percent()
        if cpu_percent > 90:
            return 5.0
        elif cpu_percent > 70:
            return 2.0
        else:
            return 0.5
    
    def _get_active_connections(self) -> int:
        """Get number of active connections (simplified)"""
        try:
            connections = psutil.net_connections()
            return len([conn for conn in connections if conn.status == 'ESTABLISHED'])
        except:
            return 0
    
    def _store_performance_to_db(self, perf_data: PerformanceData):
        """Store performance data to SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO performance (timestamp, cpu_percent, memory_percent, 
                                      disk_usage_percent, network_io, active_connections,
                                      response_time_avg, error_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                perf_data.timestamp.isoformat(),
                perf_data.cpu_percent,
                perf_data.memory_percent,
                perf_data.disk_usage_percent,
                json.dumps(perf_data.network_io),
                perf_data.active_connections,
                perf_data.response_time_avg,
                perf_data.error_rate
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error storing performance data to database: {e}")
    
    def _cleanup_old_data(self):
        """Clean up old metrics and alerts"""
        try:
            cutoff_time = datetime.now() - timedelta(days=7)
            
            # Clean up old metrics in memory
            for metric_name in list(self.metrics.keys()):
                while self.metrics[metric_name] and self.metrics[metric_name][0].timestamp < cutoff_time:
                    self.metrics[metric_name].popleft()
            
            # Clean up old alerts
            self.alerts = [alert for alert in self.alerts if alert.timestamp >= cutoff_time]
            
            # Clean up old performance data
            while self.performance_history and self.performance_history[0].timestamp < cutoff_time:
                self.performance_history.popleft()
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def get_metrics_summary(self, metric_name: str, hours: int = 24) -> Dict[str, Any]:
        """Get summary statistics for a metric"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        metric_data = [m for m in self.metrics[metric_name] if m.timestamp >= cutoff_time]
        
        if not metric_data:
            return {"count": 0, "avg": 0, "min": 0, "max": 0, "latest": 0}
        
        values = [m.value for m in metric_data]
        
        return {
            "count": len(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "latest": values[-1],
            "trend": self._calculate_trend(values)
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return "stable"
        
        recent_avg = sum(values[-5:]) / min(5, len(values))
        older_avg = sum(values[:5]) / min(5, len(values))
        
        if recent_avg > older_avg * 1.1:
            return "increasing"
        elif recent_avg < older_avg * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    def get_alerts_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get alerts summary"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_alerts = [alert for alert in self.alerts if alert.timestamp >= cutoff_time]
        
        alerts_by_level = defaultdict(int)
        unresolved_alerts = []
        
        for alert in recent_alerts:
            alerts_by_level[alert.level.value] += 1
            if not alert.resolved:
                unresolved_alerts.append(alert)
        
        return {
            "total_alerts": len(recent_alerts),
            "alerts_by_level": dict(alerts_by_level),
            "unresolved_count": len(unresolved_alerts),
            "unresolved_alerts": [
                {
                    "id": alert.id,
                    "name": alert.name,
                    "level": alert.level.value,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat()
                }
                for alert in unresolved_alerts
            ]
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        if not self.performance_history:
            return {"error": "No performance data available"}
        
        latest = self.performance_history[-1]
        
        # Calculate averages over last hour
        cutoff_time = datetime.now() - timedelta(hours=1)
        recent_data = [p for p in self.performance_history if p.timestamp >= cutoff_time]
        
        if recent_data:
            avg_cpu = sum(p.cpu_percent for p in recent_data) / len(recent_data)
            avg_memory = sum(p.memory_percent for p in recent_data) / len(recent_data)
            avg_response_time = sum(p.response_time_avg for p in recent_data) / len(recent_data)
            avg_error_rate = sum(p.error_rate for p in recent_data) / len(recent_data)
        else:
            avg_cpu = latest.cpu_percent
            avg_memory = latest.memory_percent
            avg_response_time = latest.response_time_avg
            avg_error_rate = latest.error_rate
        
        return {
            "timestamp": latest.timestamp.isoformat(),
            "current": {
                "cpu_percent": latest.cpu_percent,
                "memory_percent": latest.memory_percent,
                "disk_usage_percent": latest.disk_usage_percent,
                "active_connections": latest.active_connections,
                "response_time_avg": latest.response_time_avg,
                "error_rate": latest.error_rate
            },
            "averages_1h": {
                "cpu_percent": avg_cpu,
                "memory_percent": avg_memory,
                "response_time_avg": avg_response_time,
                "error_rate": avg_error_rate
            },
            "status": self._get_system_status(latest),
            "recommendations": self._get_performance_recommendations(latest)
        }
    
    def _get_system_status(self, perf_data: PerformanceData) -> str:
        """Get overall system status"""
        if (perf_data.cpu_percent > 90 or 
            perf_data.memory_percent > 95 or 
            perf_data.error_rate > 10):
            return "critical"
        elif (perf_data.cpu_percent > 70 or 
              perf_data.memory_percent > 80 or 
              perf_data.error_rate > 5):
            return "warning"
        else:
            return "healthy"
    
    def _get_performance_recommendations(self, perf_data: PerformanceData) -> List[str]:
        """Get performance recommendations"""
        recommendations = []
        
        if perf_data.cpu_percent > 80:
            recommendations.append("Consider scaling up CPU resources or optimizing CPU-intensive operations")
        
        if perf_data.memory_percent > 85:
            recommendations.append("Consider increasing memory allocation or optimizing memory usage")
        
        if perf_data.disk_usage_percent > 90:
            recommendations.append("Consider cleaning up disk space or expanding storage")
        
        if perf_data.response_time_avg > 3.0:
            recommendations.append("Consider optimizing database queries or implementing caching")
        
        if perf_data.error_rate > 5:
            recommendations.append("Investigate and fix application errors")
        
        if not recommendations:
            recommendations.append("System performance is optimal")
        
        return recommendations
    
    def shutdown(self):
        """Shutdown monitoring system"""
        self.monitoring_active = False
        if self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        logger.info("Monitoring system shutdown complete")


# Example usage and testing
def main():
    """Example usage of the monitoring system"""
    monitoring = AdvancedMonitoringSystem()
    
    # Record some test metrics
    monitoring.record_metric("api_requests", 100, MetricType.COUNTER)
    monitoring.record_metric("response_time", 1.5, MetricType.TIMER)
    monitoring.record_metric("active_users", 50, MetricType.GAUGE)
    
    # Wait for some data collection
    time.sleep(35)
    
    # Get metrics summary
    cpu_summary = monitoring.get_metrics_summary("cpu_percent")
    print(f"CPU Summary: {cpu_summary}")
    
    # Get alerts summary
    alerts_summary = monitoring.get_alerts_summary()
    print(f"Alerts Summary: {alerts_summary}")
    
    # Get performance report
    perf_report = monitoring.get_performance_report()
    print(f"Performance Report: {perf_report}")
    
    # Shutdown
    monitoring.shutdown()


if __name__ == "__main__":
    main()