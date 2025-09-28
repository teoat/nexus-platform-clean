#!/usr/bin/env python3
"""
NEXUS System Monitor - Comprehensive monitoring and health checking
"""

import os
import sys
import json
import time
import psutil
import requests
import logging
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    process_count: int
    load_average: List[float]
    uptime: float

@dataclass
class ServiceHealth:
    """Service health status"""
    name: str
    status: str  # 'healthy', 'degraded', 'unhealthy'
    response_time: float
    last_check: str
    error_message: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None

@dataclass
class Alert:
    """System alert"""
    id: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    category: str
    message: str
    timestamp: str
    resolved: bool = False
    resolution_time: Optional[str] = None

class SystemMonitor:
    """Comprehensive system monitoring"""
    
    def __init__(self, config_path: str = "config/monitoring.json"):
        self.config = self._load_config(config_path)
        self.alerts: List[Alert] = []
        self.metrics_history: List[SystemMetrics] = []
        self.service_health: Dict[str, ServiceHealth] = {}
        self.start_time = datetime.now()
        
        # Create logs directory
        os.makedirs("logs", exist_ok=True)
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load monitoring configuration"""
        default_config = {
            "monitoring": {
                "interval": 30,  # seconds
                "retention_days": 7,
                "alert_thresholds": {
                    "cpu_percent": 80,
                    "memory_percent": 85,
                    "disk_percent": 90,
                    "response_time": 5.0
                },
                "services": {
                    "frontend": {
                        "url": "http://localhost:3000/health",
                        "timeout": 5
                    },
                    "backend": {
                        "url": "http://localhost:8000/health",
                        "timeout": 5
                    },
                    "database": {
                        "url": "http://localhost:5432",
                        "timeout": 5
                    },
                    "redis": {
                        "url": "http://localhost:6379",
                        "timeout": 5
                    },
                    "nginx": {
                        "url": "http://localhost:80/health",
                        "timeout": 5
                    }
                }
            }
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return {**default_config, **config}
            except Exception as e:
                logger.warning(f"Failed to load config: {e}, using defaults")
        
        return default_config
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            # CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network I/O
            network_io = psutil.net_io_counters()._asdict()
            
            # Process count
            process_count = len(psutil.pids())
            
            # Load average (Unix only)
            try:
                load_average = list(psutil.getloadavg())
            except AttributeError:
                load_average = [0.0, 0.0, 0.0]
            
            # Uptime
            uptime = time.time() - psutil.boot_time()
            
            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=disk.percent,
                network_io=network_io,
                process_count=process_count,
                load_average=load_average,
                uptime=uptime
            )
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            raise
    
    def check_service_health(self, service_name: str, service_config: Dict[str, Any]) -> ServiceHealth:
        """Check health of a specific service"""
        try:
            start_time = time.time()
            
            # For database and redis, use different checks
            if service_name in ['database', 'redis']:
                status = self._check_database_health(service_name)
                response_time = time.time() - start_time
                
                return ServiceHealth(
                    name=service_name,
                    status='healthy' if status else 'unhealthy',
                    response_time=response_time,
                    last_check=datetime.now().isoformat(),
                    error_message=None if status else f"{service_name} connection failed"
                )
            else:
                # HTTP health check
                response = requests.get(
                    service_config['url'],
                    timeout=service_config['timeout']
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    return ServiceHealth(
                        name=service_name,
                        status='healthy',
                        response_time=response_time,
                        last_check=datetime.now().isoformat(),
                        metrics=response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                    )
                else:
                    return ServiceHealth(
                        name=service_name,
                        status='degraded' if response.status_code < 500 else 'unhealthy',
                        response_time=response_time,
                        last_check=datetime.now().isoformat(),
                        error_message=f"HTTP {response.status_code}"
                    )
                    
        except requests.exceptions.Timeout:
            return ServiceHealth(
                name=service_name,
                status='unhealthy',
                response_time=service_config['timeout'],
                last_check=datetime.now().isoformat(),
                error_message="Request timeout"
            )
        except Exception as e:
            return ServiceHealth(
                name=service_name,
                status='unhealthy',
                response_time=0.0,
                last_check=datetime.now().isoformat(),
                error_message=str(e)
            )
    
    def _check_database_health(self, service_name: str) -> bool:
        """Check database connectivity"""
        try:
            if service_name == 'database':
                # Check PostgreSQL
                result = subprocess.run(
                    ['pg_isready', '-h', 'localhost', '-p', '5432'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return result.returncode == 0
            elif service_name == 'redis':
                # Check Redis
                result = subprocess.run(
                    ['redis-cli', 'ping'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return result.returncode == 0 and 'PONG' in result.stdout
            return False
        except Exception:
            return False
    
    def check_alerts(self, metrics: SystemMetrics) -> List[Alert]:
        """Check for alert conditions"""
        alerts = []
        thresholds = self.config['monitoring']['alert_thresholds']
        
        # CPU alert
        if metrics.cpu_percent > thresholds['cpu_percent']:
            alerts.append(Alert(
                id=f"cpu_high_{int(time.time())}",
                severity='high' if metrics.cpu_percent > 95 else 'medium',
                category='performance',
                message=f"High CPU usage: {metrics.cpu_percent:.1f}%",
                timestamp=datetime.now().isoformat()
            ))
        
        # Memory alert
        if metrics.memory_percent > thresholds['memory_percent']:
            alerts.append(Alert(
                id=f"memory_high_{int(time.time())}",
                severity='high' if metrics.memory_percent > 95 else 'medium',
                category='performance',
                message=f"High memory usage: {metrics.memory_percent:.1f}%",
                timestamp=datetime.now().isoformat()
            ))
        
        # Disk alert
        if metrics.disk_percent > thresholds['disk_percent']:
            alerts.append(Alert(
                id=f"disk_high_{int(time.time())}",
                severity='critical' if metrics.disk_percent > 95 else 'high',
                category='storage',
                message=f"High disk usage: {metrics.disk_percent:.1f}%",
                timestamp=datetime.now().isoformat()
            ))
        
        # Service health alerts
        for service_name, health in self.service_health.items():
            if health.status == 'unhealthy':
                alerts.append(Alert(
                    id=f"service_down_{service_name}_{int(time.time())}",
                    severity='critical',
                    category='service',
                    message=f"Service {service_name} is unhealthy: {health.error_message}",
                    timestamp=datetime.now().isoformat()
                ))
            elif health.status == 'degraded':
                alerts.append(Alert(
                    id=f"service_degraded_{service_name}_{int(time.time())}",
                    severity='medium',
                    category='service',
                    message=f"Service {service_name} is degraded: {health.error_message}",
                    timestamp=datetime.now().isoformat()
                ))
        
        return alerts
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        current_time = datetime.now()
        uptime = current_time - self.start_time
        
        # Calculate averages
        if self.metrics_history:
            avg_cpu = sum(m.cpu_percent for m in self.metrics_history[-10:]) / min(10, len(self.metrics_history))
            avg_memory = sum(m.memory_percent for m in self.metrics_history[-10:]) / min(10, len(self.metrics_history))
            avg_disk = sum(m.disk_percent for m in self.metrics_history[-10:]) / min(10, len(self.metrics_history))
        else:
            avg_cpu = avg_memory = avg_disk = 0.0
        
        # Service status summary
        service_status = {}
        for name, health in self.service_health.items():
            service_status[name] = {
                'status': health.status,
                'response_time': health.response_time,
                'last_check': health.last_check
            }
        
        # Active alerts
        active_alerts = [alert for alert in self.alerts if not alert.resolved]
        alert_summary = {}
        for alert in active_alerts:
            if alert.severity not in alert_summary:
                alert_summary[alert.severity] = 0
            alert_summary[alert.severity] += 1
        
        return {
            'timestamp': current_time.isoformat(),
            'monitor_uptime': str(uptime),
            'system_metrics': {
                'current': asdict(self.metrics_history[-1]) if self.metrics_history else None,
                'averages': {
                    'cpu_percent': avg_cpu,
                    'memory_percent': avg_memory,
                    'disk_percent': avg_disk
                }
            },
            'services': service_status,
            'alerts': {
                'active_count': len(active_alerts),
                'summary': alert_summary,
                'recent': [asdict(alert) for alert in self.alerts[-10:]]
            },
            'health_score': self._calculate_health_score()
        }
    
    def _calculate_health_score(self) -> int:
        """Calculate overall system health score (0-100)"""
        score = 100
        
        # Deduct for high resource usage
        if self.metrics_history:
            latest = self.metrics_history[-1]
            if latest.cpu_percent > 80:
                score -= 20
            if latest.memory_percent > 85:
                score -= 20
            if latest.disk_percent > 90:
                score -= 30
        
        # Deduct for unhealthy services
        for health in self.service_health.values():
            if health.status == 'unhealthy':
                score -= 25
            elif health.status == 'degraded':
                score -= 10
        
        # Deduct for critical alerts
        critical_alerts = [a for a in self.alerts if a.severity == 'critical' and not a.resolved]
        score -= len(critical_alerts) * 15
        
        return max(0, score)
    
    def cleanup_old_data(self):
        """Clean up old metrics and alerts"""
        cutoff_time = datetime.now() - timedelta(days=self.config['monitoring']['retention_days'])
        
        # Clean metrics
        self.metrics_history = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m.timestamp) > cutoff_time
        ]
        
        # Clean resolved alerts older than retention period
        self.alerts = [
            a for a in self.alerts 
            if not a.resolved or datetime.fromisoformat(a.timestamp) > cutoff_time
        ]
    
    def run_monitoring_cycle(self):
        """Run a single monitoring cycle"""
        try:
            logger.info("Starting monitoring cycle")
            
            # Collect system metrics
            metrics = self.collect_system_metrics()
            self.metrics_history.append(metrics)
            
            # Check service health
            for service_name, service_config in self.config['monitoring']['services'].items():
                health = self.check_service_health(service_name, service_config)
                self.service_health[service_name] = health
            
            # Check for alerts
            new_alerts = self.check_alerts(metrics)
            self.alerts.extend(new_alerts)
            
            # Log new alerts
            for alert in new_alerts:
                logger.warning(f"ALERT [{alert.severity.upper()}]: {alert.message}")
            
            # Cleanup old data
            self.cleanup_old_data()
            
            # Generate and save report
            report = self.generate_report()
            report_path = f"logs/monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Monitoring cycle completed. Health score: {report['health_score']}")
            
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")
    
    def run_continuous(self):
        """Run continuous monitoring"""
        logger.info("Starting continuous monitoring")
        
        try:
            while True:
                self.run_monitoring_cycle()
                time.sleep(self.config['monitoring']['interval'])
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Fatal error in monitoring: {e}")
            raise

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='NEXUS System Monitor')
    parser.add_argument('--config', default='config/monitoring.json', help='Config file path')
    parser.add_argument('--once', action='store_true', help='Run once instead of continuously')
    parser.add_argument('--report', action='store_true', help='Generate report only')
    
    args = parser.parse_args()
    
    monitor = SystemMonitor(args.config)
    
    if args.report:
        report = monitor.generate_report()
        print(json.dumps(report, indent=2))
    elif args.once:
        monitor.run_monitoring_cycle()
    else:
        monitor.run_continuous()

if __name__ == "__main__":
    main()
