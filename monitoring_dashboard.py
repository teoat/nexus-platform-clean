#!/usr/bin/env python3
"""
NEXUS Platform - Comprehensive Monitoring Dashboard
Real-time monitoring, metrics, and alerting system
"""

import asyncio
import json
import logging
import time
import psutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class NexusMonitoringDashboard:
    """Comprehensive monitoring dashboard for NEXUS Platform"""
    
    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        self.base_path = Path(base_path)
        self.monitoring_data = {}
        self.alerts = []
        self.metrics_history = []
        self.dashboard_data = {}
        
        # Monitoring thresholds
        self.thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "disk_usage": 90.0,
            "response_time": 2.0,
            "error_rate": 5.0,
            "database_size": 1000,  # MB
            "log_size": 100  # MB
        }
        
        # API endpoints to monitor
        self.api_endpoints = [
            "http://localhost:8000/health",
            "http://localhost:8000/api/health",
            "http://localhost:8000/api/status",
            "http://localhost:3000/",  # Frontend
        ]
    
    async def run_monitoring_dashboard(self):
        """Run the comprehensive monitoring dashboard"""
        logger.info("📊 Starting NEXUS Platform Monitoring Dashboard...")
        print("\n" + "="*80)
        print("📊 NEXUS PLATFORM - MONITORING DASHBOARD")
        print("="*80)
        
        try:
            # Initialize monitoring
            await self._initialize_monitoring()
            
            # Run monitoring loop
            await self._monitoring_loop()
            
        except KeyboardInterrupt:
            print("\n🛑 Monitoring dashboard stopped by user")
        except Exception as e:
            logger.error(f"Monitoring dashboard failed: {e}")
            print(f"\n❌ MONITORING FAILED: {e}")
    
    async def _initialize_monitoring(self):
        """Initialize monitoring systems"""
        print("\n🔧 Initializing monitoring systems...")
        
        # Check system requirements
        await self._check_system_requirements()
        
        # Initialize database monitoring
        await self._initialize_database_monitoring()
        
        # Initialize API monitoring
        await self._initialize_api_monitoring()
        
        # Initialize file system monitoring
        await self._initialize_filesystem_monitoring()
        
        print("✅ Monitoring systems initialized")
    
    async def _check_system_requirements(self):
        """Check system requirements and dependencies"""
        print("  🔍 Checking system requirements...")
        
        # Check Python packages
        required_packages = ['psutil', 'requests', 'sqlite3']
        for package in required_packages:
            try:
                __import__(package)
                print(f"    ✅ {package}")
            except ImportError:
                print(f"    ❌ {package} - Please install: pip install {package}")
        
        # Check system resources
        cpu_count = psutil.cpu_count()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        print(f"    💻 CPU Cores: {cpu_count}")
        print(f"    🧠 Memory: {memory.total // (1024**3)} GB")
        print(f"    💾 Disk Space: {disk.total // (1024**3)} GB")
    
    async def _initialize_database_monitoring(self):
        """Initialize database monitoring"""
        print("  🗄️ Initializing database monitoring...")
        
        # Check database files
        db_files = [
            self.base_path / "nexus_platform.db",
            self.base_path / "nexus.db"
        ]
        
        for db_file in db_files:
            if db_file.exists():
                try:
                    conn = sqlite3.connect(str(db_file))
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    conn.close()
                    print(f"    ✅ {db_file.name}: {len(tables)} tables")
                except Exception as e:
                    print(f"    ❌ {db_file.name}: {e}")
            else:
                print(f"    ⚠️ {db_file.name}: Not found")
    
    async def _initialize_api_monitoring(self):
        """Initialize API monitoring"""
        print("  🌐 Initializing API monitoring...")
        
        for endpoint in self.api_endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code == 200:
                    print(f"    ✅ {endpoint}")
                else:
                    print(f"    ⚠️ {endpoint}: Status {response.status_code}")
            except Exception as e:
                print(f"    ❌ {endpoint}: {e}")
    
    async def _initialize_filesystem_monitoring(self):
        """Initialize file system monitoring"""
        print("  📁 Initializing filesystem monitoring...")
        
        # Check critical directories
        critical_dirs = [
            "backend/",
            "frontend/",
            "nexus/",
            "services/",
            "monitoring/",
            "logs/",
            "data/"
        ]
        
        for dir_path in critical_dirs:
            full_path = self.base_path / dir_path
            if full_path.exists():
                file_count = len(list(full_path.rglob('*')))
                print(f"    ✅ {dir_path}: {file_count} files")
            else:
                print(f"    ⚠️ {dir_path}: Not found")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        print("\n🔄 Starting monitoring loop...")
        print("Press Ctrl+C to stop monitoring")
        
        iteration = 0
        while True:
            try:
                iteration += 1
                print(f"\n📊 Monitoring Cycle #{iteration} - {datetime.now().strftime('%H:%M:%S')}")
                
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Collect application metrics
                await self._collect_application_metrics()
                
                # Check for alerts
                await self._check_alerts()
                
                # Display dashboard
                self._display_dashboard()
                
                # Save metrics
                await self._save_metrics()
                
                # Wait before next cycle
                await asyncio.sleep(30)  # 30-second intervals
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(5)
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used // (1024**2)  # MB
            memory_total = memory.total // (1024**2)  # MB
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_used = disk.used // (1024**2)  # MB
            disk_total = disk.total // (1024**2)  # MB
            
            # Process metrics
            processes = list(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']))
            nexus_processes = [p for p in processes if 'nexus' in p.info['name'].lower() or 'python' in p.info['name'].lower()]
            
            self.monitoring_data['system'] = {
                'cpu_percent': cpu_percent,
                'cpu_count': cpu_count,
                'memory_percent': memory_percent,
                'memory_used_mb': memory_used,
                'memory_total_mb': memory_total,
                'disk_percent': disk_percent,
                'disk_used_mb': disk_used,
                'disk_total_mb': disk_total,
                'process_count': len(processes),
                'nexus_processes': len(nexus_processes),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def _collect_application_metrics(self):
        """Collect application-level metrics"""
        try:
            # API response times
            api_metrics = {}
            for endpoint in self.api_endpoints:
                try:
                    start_time = time.time()
                    response = requests.get(endpoint, timeout=5)
                    response_time = (time.time() - start_time) * 1000  # ms
                    
                    api_metrics[endpoint] = {
                        'status_code': response.status_code,
                        'response_time_ms': response_time,
                        'success': response.status_code == 200
                    }
                except Exception as e:
                    api_metrics[endpoint] = {
                        'status_code': 0,
                        'response_time_ms': 0,
                        'success': False,
                        'error': str(e)
                    }
            
            # Database metrics
            db_metrics = {}
            db_files = [
                self.base_path / "nexus_platform.db",
                self.base_path / "nexus.db"
            ]
            
            for db_file in db_files:
                if db_file.exists():
                    try:
                        file_size = db_file.stat().st_size // (1024**2)  # MB
                        conn = sqlite3.connect(str(db_file))
                        cursor = conn.cursor()
                        
                        # Get table count
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                        table_count = len(cursor.fetchall())
                        
                        # Get row count for main tables
                        cursor.execute("SELECT COUNT(*) FROM users") if 'users' in [t[0] for t in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()] else None
                        user_count = cursor.fetchone()[0] if cursor.fetchone() else 0
                        
                        conn.close()
                        
                        db_metrics[db_file.name] = {
                            'file_size_mb': file_size,
                            'table_count': table_count,
                            'user_count': user_count,
                            'status': 'healthy'
                        }
                    except Exception as e:
                        db_metrics[db_file.name] = {
                            'file_size_mb': 0,
                            'table_count': 0,
                            'user_count': 0,
                            'status': 'error',
                            'error': str(e)
                        }
            
            # File system metrics
            fs_metrics = {}
            critical_dirs = ['backend/', 'frontend/', 'nexus/', 'services/', 'logs/', 'data/']
            
            for dir_path in critical_dirs:
                full_path = self.base_path / dir_path
                if full_path.exists():
                    try:
                        file_count = len(list(full_path.rglob('*')))
                        total_size = sum(f.stat().st_size for f in full_path.rglob('*') if f.is_file()) // (1024**2)  # MB
                        
                        fs_metrics[dir_path] = {
                            'file_count': file_count,
                            'total_size_mb': total_size,
                            'status': 'healthy'
                        }
                    except Exception as e:
                        fs_metrics[dir_path] = {
                            'file_count': 0,
                            'total_size_mb': 0,
                            'status': 'error',
                            'error': str(e)
                        }
            
            self.monitoring_data['application'] = {
                'api_metrics': api_metrics,
                'database_metrics': db_metrics,
                'filesystem_metrics': fs_metrics,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
    
    async def _check_alerts(self):
        """Check for alert conditions"""
        try:
            current_alerts = []
            
            if 'system' in self.monitoring_data:
                sys_data = self.monitoring_data['system']
                
                # CPU alert
                if sys_data['cpu_percent'] > self.thresholds['cpu_usage']:
                    current_alerts.append({
                        'type': 'cpu_high',
                        'message': f"CPU usage is {sys_data['cpu_percent']:.1f}% (threshold: {self.thresholds['cpu_usage']}%)",
                        'severity': 'warning',
                        'timestamp': datetime.now().isoformat()
                    })
                
                # Memory alert
                if sys_data['memory_percent'] > self.thresholds['memory_usage']:
                    current_alerts.append({
                        'type': 'memory_high',
                        'message': f"Memory usage is {sys_data['memory_percent']:.1f}% (threshold: {self.thresholds['memory_usage']}%)",
                        'severity': 'warning',
                        'timestamp': datetime.now().isoformat()
                    })
                
                # Disk alert
                if sys_data['disk_percent'] > self.thresholds['disk_usage']:
                    current_alerts.append({
                        'type': 'disk_high',
                        'message': f"Disk usage is {sys_data['disk_percent']:.1f}% (threshold: {self.thresholds['disk_usage']}%)",
                        'severity': 'critical',
                        'timestamp': datetime.now().isoformat()
                    })
            
            if 'application' in self.monitoring_data:
                app_data = self.monitoring_data['application']
                
                # API response time alerts
                for endpoint, metrics in app_data['api_metrics'].items():
                    if not metrics['success']:
                        current_alerts.append({
                            'type': 'api_down',
                            'message': f"API endpoint {endpoint} is not responding",
                            'severity': 'critical',
                            'timestamp': datetime.now().isoformat()
                        })
                    elif metrics['response_time_ms'] > self.thresholds['response_time'] * 1000:
                        current_alerts.append({
                            'type': 'api_slow',
                            'message': f"API endpoint {endpoint} is slow: {metrics['response_time_ms']:.0f}ms",
                            'severity': 'warning',
                            'timestamp': datetime.now().isoformat()
                        })
            
            self.alerts = current_alerts
            
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
    
    def _display_dashboard(self):
        """Display the monitoring dashboard"""
        print("\n" + "="*60)
        print("📊 NEXUS PLATFORM MONITORING DASHBOARD")
        print("="*60)
        
        # System metrics
        if 'system' in self.monitoring_data:
            sys_data = self.monitoring_data['system']
            print(f"\n💻 SYSTEM METRICS:")
            print(f"  CPU Usage: {sys_data['cpu_percent']:.1f}% ({sys_data['cpu_count']} cores)")
            print(f"  Memory: {sys_data['memory_percent']:.1f}% ({sys_data['memory_used_mb']:,} MB / {sys_data['memory_total_mb']:,} MB)")
            print(f"  Disk: {sys_data['disk_percent']:.1f}% ({sys_data['disk_used_mb']:,} MB / {sys_data['disk_total_mb']:,} MB)")
            print(f"  Processes: {sys_data['process_count']} total, {sys_data['nexus_processes']} NEXUS-related")
        
        # Application metrics
        if 'application' in self.monitoring_data:
            app_data = self.monitoring_data['application']
            print(f"\n🌐 APPLICATION METRICS:")
            
            # API status
            print("  API Endpoints:")
            for endpoint, metrics in app_data['api_metrics'].items():
                status = "✅" if metrics['success'] else "❌"
                response_time = f"{metrics['response_time_ms']:.0f}ms" if metrics['response_time_ms'] > 0 else "N/A"
                print(f"    {status} {endpoint} - {response_time}")
            
            # Database status
            print("  Databases:")
            for db_name, metrics in app_data['database_metrics'].items():
                status = "✅" if metrics['status'] == 'healthy' else "❌"
                print(f"    {status} {db_name}: {metrics['file_size_mb']} MB, {metrics['table_count']} tables")
        
        # Alerts
        if self.alerts:
            print(f"\n🚨 ACTIVE ALERTS ({len(self.alerts)}):")
            for alert in self.alerts:
                severity_icon = "🔴" if alert['severity'] == 'critical' else "🟡"
                print(f"  {severity_icon} {alert['message']}")
        else:
            print(f"\n✅ NO ACTIVE ALERTS")
        
        print("="*60)
    
    async def _save_metrics(self):
        """Save metrics to file"""
        try:
            metrics_data = {
                'timestamp': datetime.now().isoformat(),
                'system': self.monitoring_data.get('system', {}),
                'application': self.monitoring_data.get('application', {}),
                'alerts': self.alerts
            }
            
            self.metrics_history.append(metrics_data)
            
            # Keep only last 100 entries
            if len(self.metrics_history) > 100:
                self.metrics_history = self.metrics_history[-100:]
            
            # Save to file
            metrics_file = self.base_path / "monitoring_metrics.json"
            with open(metrics_file, 'w') as f:
                json.dump(self.metrics_history, f, indent=2)
            
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")


# Main execution
async def main():
    """Main execution function"""
    dashboard = NexusMonitoringDashboard()
    await dashboard.run_monitoring_dashboard()


if __name__ == "__main__":
    asyncio.run(main())
