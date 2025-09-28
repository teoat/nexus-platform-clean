#!/usr/bin/env python3
"""
NEXUS System Dashboard - Real-time system status and metrics
"""

import os
import sys
import json
import time
import psutil
import requests
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class SystemStatus:
    """System status information"""
    timestamp: str
    overall_health: str
    services: Dict[str, Any]
    metrics: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    uptime: str

class SystemDashboard:
    """Real-time system dashboard"""
    
    def __init__(self):
        self.services = {
            'frontend': {'url': 'http://localhost:3000', 'port': 3000},
            'backend': {'url': 'http://localhost:8000', 'port': 8000},
            'database': {'type': 'postgresql', 'port': 5432},
            'redis': {'type': 'redis', 'port': 6379},
            'nginx': {'url': 'http://localhost:80', 'port': 80},
            'frenly_ai': {'url': 'http://localhost:8001', 'port': 8001}
        }
        
        self.start_time = datetime.now()
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            # CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network
            network = psutil.net_io_counters()
            
            # Processes
            processes = list(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']))
            
            # Load average
            try:
                load_avg = list(psutil.getloadavg())
            except AttributeError:
                load_avg = [0.0, 0.0, 0.0]
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count(),
                    'load_average': load_avg
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'processes': {
                    'total': len(processes),
                    'top_cpu': sorted(processes, key=lambda x: x.info['cpu_percent'] or 0, reverse=True)[:5],
                    'top_memory': sorted(processes, key=lambda x: x.info['memory_percent'] or 0, reverse=True)[:5]
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    def check_service_status(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check individual service status"""
        try:
            if 'type' in config:
                # Database or Redis
                if config['type'] == 'postgresql':
                    result = subprocess.run(
                        ['pg_isready', '-h', 'localhost', '-p', str(config['port'])],
                        capture_output=True, text=True, timeout=5
                    )
                    status = 'healthy' if result.returncode == 0 else 'unhealthy'
                    response_time = 0.0
                    error = result.stderr if result.returncode != 0 else None
                elif config['type'] == 'redis':
                    result = subprocess.run(
                        ['redis-cli', 'ping'],
                        capture_output=True, text=True, timeout=5
                    )
                    status = 'healthy' if result.returncode == 0 and 'PONG' in result.stdout else 'unhealthy'
                    response_time = 0.0
                    error = result.stderr if result.returncode != 0 else None
                else:
                    status = 'unknown'
                    response_time = 0.0
                    error = f"Unsupported type: {config['type']}"
            else:
                # HTTP service
                start_time = time.time()
                try:
                    response = requests.get(f"{config['url']}/health", timeout=5)
                    response_time = time.time() - start_time
                    status = 'healthy' if response.status_code == 200 else 'degraded'
                    error = None
                except requests.exceptions.Timeout:
                    response_time = 5.0
                    status = 'unhealthy'
                    error = 'Request timeout'
                except Exception as e:
                    response_time = 0.0
                    status = 'unhealthy'
                    error = str(e)
            
            return {
                'name': name,
                'status': status,
                'response_time': response_time,
                'port': config.get('port', 'unknown'),
                'error': error,
                'last_check': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'name': name,
                'status': 'unhealthy',
                'response_time': 0.0,
                'port': config.get('port', 'unknown'),
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
    
    def check_all_services(self) -> Dict[str, Any]:
        """Check all services"""
        services_status = {}
        healthy_count = 0
        total_count = len(self.services)
        
        for name, config in self.services.items():
            status = self.check_service_status(name, config)
            services_status[name] = status
            if status['status'] == 'healthy':
                healthy_count += 1
        
        overall_status = 'healthy' if healthy_count == total_count else 'degraded' if healthy_count > 0 else 'unhealthy'
        
        return {
            'overall': overall_status,
            'healthy_count': healthy_count,
            'total_count': total_count,
            'health_percentage': (healthy_count / total_count) * 100,
            'services': services_status
        }
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get current system alerts"""
        alerts = []
        metrics = self.get_system_metrics()
        
        if 'error' in metrics:
            alerts.append({
                'severity': 'critical',
                'category': 'system',
                'message': f"System metrics error: {metrics['error']}",
                'timestamp': datetime.now().isoformat()
            })
            return alerts
        
        # CPU alerts
        if metrics['cpu']['percent'] > 90:
            alerts.append({
                'severity': 'critical',
                'category': 'performance',
                'message': f"Critical CPU usage: {metrics['cpu']['percent']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
        elif metrics['cpu']['percent'] > 80:
            alerts.append({
                'severity': 'warning',
                'category': 'performance',
                'message': f"High CPU usage: {metrics['cpu']['percent']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
        
        # Memory alerts
        if metrics['memory']['percent'] > 95:
            alerts.append({
                'severity': 'critical',
                'category': 'performance',
                'message': f"Critical memory usage: {metrics['memory']['percent']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
        elif metrics['memory']['percent'] > 85:
            alerts.append({
                'severity': 'warning',
                'category': 'performance',
                'message': f"High memory usage: {metrics['memory']['percent']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
        
        # Disk alerts
        if metrics['disk']['percent'] > 95:
            alerts.append({
                'severity': 'critical',
                'category': 'storage',
                'message': f"Critical disk usage: {metrics['disk']['percent']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
        elif metrics['disk']['percent'] > 90:
            alerts.append({
                'severity': 'warning',
                'category': 'storage',
                'message': f"High disk usage: {metrics['disk']['percent']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts
    
    def get_system_status(self) -> SystemStatus:
        """Get comprehensive system status"""
        metrics = self.get_system_metrics()
        services = self.check_all_services()
        alerts = self.get_alerts()
        
        # Calculate overall health
        overall_health = services['overall']
        if alerts:
            critical_alerts = [a for a in alerts if a['severity'] == 'critical']
            if critical_alerts:
                overall_health = 'critical'
            elif overall_health == 'healthy':
                overall_health = 'warning'
        
        uptime = datetime.now() - self.start_time
        
        return SystemStatus(
            timestamp=datetime.now().isoformat(),
            overall_health=overall_health,
            services=services,
            metrics=metrics,
            alerts=alerts,
            uptime=str(uptime)
        )
    
    def print_dashboard(self, status: SystemStatus):
        """Print formatted dashboard to console"""
        print("\n" + "="*80)
        print(f"🚀 NEXUS SYSTEM DASHBOARD - {status.timestamp}")
        print("="*80)
        
        # Overall status
        health_emoji = {
            'healthy': '✅',
            'warning': '⚠️',
            'degraded': '⚠️',
            'unhealthy': '❌',
            'critical': '🚨'
        }
        
        print(f"\n📊 OVERALL STATUS: {health_emoji.get(status.overall_health, '❓')} {status.overall_health.upper()}")
        print(f"⏱️  UPTIME: {status.uptime}")
        
        # Services status
        print(f"\n🔧 SERVICES ({status.services['healthy_count']}/{status.services['total_count']} healthy):")
        print("-" * 60)
        for name, service in status.services['services'].items():
            status_emoji = {
                'healthy': '✅',
                'degraded': '⚠️',
                'unhealthy': '❌',
                'unknown': '❓'
            }
            print(f"{status_emoji.get(service['status'], '❓')} {name:<12} | {service['status']:<10} | Port {service['port']}")
            if service['error']:
                print(f"    Error: {service['error']}")
        
        # System metrics
        if 'error' not in status.metrics:
            print(f"\n💻 SYSTEM METRICS:")
            print("-" * 60)
            print(f"CPU:  {status.metrics['cpu']['percent']:>6.1f}% | Memory: {status.metrics['memory']['percent']:>6.1f}% | Disk: {status.metrics['disk']['percent']:>6.1f}%")
            print(f"Load: {status.metrics['cpu']['load_average'][0]:>6.2f} | Processes: {status.metrics['processes']['total']:>6d}")
            
            # Top processes
            if status.metrics['processes']['top_cpu']:
                print(f"\n🔥 TOP CPU PROCESSES:")
                for proc in status.metrics['processes']['top_cpu'][:3]:
                    if proc.info['cpu_percent']:
                        print(f"  {proc.info['name']:<20} | {proc.info['cpu_percent']:>6.1f}%")
        
        # Alerts
        if status.alerts:
            print(f"\n🚨 ALERTS ({len(status.alerts)}):")
            print("-" * 60)
            for alert in status.alerts:
                severity_emoji = {
                    'critical': '🚨',
                    'warning': '⚠️',
                    'info': 'ℹ️'
                }
                print(f"{severity_emoji.get(alert['severity'], '❓')} [{alert['severity'].upper()}] {alert['message']}")
        else:
            print(f"\n✅ NO ACTIVE ALERTS")
        
        print("="*80)
    
    def run_dashboard(self, refresh_interval: int = 5):
        """Run interactive dashboard with refresh"""
        try:
            while True:
                # Clear screen
                os.system('clear' if os.name == 'posix' else 'cls')
                
                # Get and display status
                status = self.get_system_status()
                self.print_dashboard(status)
                
                # Wait for next refresh
                print(f"\n🔄 Refreshing in {refresh_interval} seconds... (Ctrl+C to exit)")
                time.sleep(refresh_interval)
                
        except KeyboardInterrupt:
            print("\n👋 Dashboard stopped by user")
        except Exception as e:
            print(f"\n❌ Dashboard error: {e}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='NEXUS System Dashboard')
    parser.add_argument('--once', action='store_true', help='Show status once and exit')
    parser.add_argument('--refresh', type=int, default=5, help='Refresh interval in seconds')
    parser.add_argument('--json', action='store_true', help='Output JSON format')
    
    args = parser.parse_args()
    
    dashboard = SystemDashboard()
    
    if args.once:
        status = dashboard.get_system_status()
        if args.json:
            print(json.dumps(asdict(status), indent=2))
        else:
            dashboard.print_dashboard(status)
    else:
        dashboard.run_dashboard(args.refresh)

if __name__ == "__main__":
    main()
