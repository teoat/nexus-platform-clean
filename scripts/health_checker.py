#!/usr/bin/env python3
"""
NEXUS Health Checker - Quick health status checker
"""

import os
import sys
import json
import time
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional

class HealthChecker:
    """Quick health status checker for all services"""
    
    def __init__(self):
        self.services = {
            'frontend': {
                'url': 'http://localhost:3000',
                'health_endpoint': '/health',
                'timeout': 5
            },
            'backend': {
                'url': 'http://localhost:8000',
                'health_endpoint': '/health',
                'timeout': 5
            },
            'database': {
                'type': 'postgresql',
                'host': 'localhost',
                'port': 5432,
                'timeout': 5
            },
            'redis': {
                'type': 'redis',
                'host': 'localhost',
                'port': 6379,
                'timeout': 5
            },
            'nginx': {
                'url': 'http://localhost:80',
                'health_endpoint': '/health',
                'timeout': 5
            },
            'frenly_ai': {
                'url': 'http://localhost:8001',
                'health_endpoint': '/health',
                'timeout': 5
            }
        }
    
    def check_http_service(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check HTTP service health"""
        try:
            url = f"{config['url']}{config.get('health_endpoint', '')}"
            start_time = time.time()
            
            response = requests.get(url, timeout=config['timeout'])
            response_time = time.time() - start_time
            
            return {
                'name': name,
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'response_time': response_time,
                'status_code': response.status_code,
                'url': url,
                'timestamp': datetime.now().isoformat()
            }
        except requests.exceptions.Timeout:
            return {
                'name': name,
                'status': 'unhealthy',
                'response_time': config['timeout'],
                'status_code': None,
                'url': url,
                'error': 'Request timeout',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'name': name,
                'status': 'unhealthy',
                'response_time': 0.0,
                'status_code': None,
                'url': url,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_database(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            if config['type'] == 'postgresql':
                result = subprocess.run([
                    'pg_isready',
                    '-h', config['host'],
                    '-p', str(config['port']),
                    '-t', str(config['timeout'])
                ], capture_output=True, text=True, timeout=config['timeout'])
                
                return {
                    'name': name,
                    'status': 'healthy' if result.returncode == 0 else 'unhealthy',
                    'response_time': 0.0,
                    'status_code': result.returncode,
                    'url': f"{config['host']}:{config['port']}",
                    'error': result.stderr if result.returncode != 0 else None,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'name': name,
                    'status': 'unknown',
                    'response_time': 0.0,
                    'status_code': None,
                    'url': f"{config['host']}:{config['port']}",
                    'error': f"Unsupported database type: {config['type']}",
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            return {
                'name': name,
                'status': 'unhealthy',
                'response_time': 0.0,
                'status_code': None,
                'url': f"{config['host']}:{config['port']}",
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_redis(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check Redis connectivity"""
        try:
            result = subprocess.run([
                'redis-cli',
                '-h', config['host'],
                '-p', str(config['port']),
                'ping'
            ], capture_output=True, text=True, timeout=config['timeout'])
            
            is_healthy = result.returncode == 0 and 'PONG' in result.stdout
            
            return {
                'name': name,
                'status': 'healthy' if is_healthy else 'unhealthy',
                'response_time': 0.0,
                'status_code': result.returncode,
                'url': f"{config['host']}:{config['port']}",
                'error': result.stderr if not is_healthy else None,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'name': name,
                'status': 'unhealthy',
                'response_time': 0.0,
                'status_code': None,
                'url': f"{config['host']}:{config['port']}",
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_all_services(self) -> Dict[str, Any]:
        """Check all services and return comprehensive status"""
        results = []
        healthy_count = 0
        total_count = len(self.services)
        
        for name, config in self.services.items():
            if 'type' in config:
                if config['type'] == 'postgresql':
                    result = self.check_database(name, config)
                elif config['type'] == 'redis':
                    result = self.check_redis(name, config)
                else:
                    result = {
                        'name': name,
                        'status': 'unknown',
                        'response_time': 0.0,
                        'status_code': None,
                        'url': 'unknown',
                        'error': f"Unsupported service type: {config['type']}",
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                result = self.check_http_service(name, config)
            
            results.append(result)
            if result['status'] == 'healthy':
                healthy_count += 1
        
        overall_status = 'healthy' if healthy_count == total_count else 'degraded' if healthy_count > 0 else 'unhealthy'
        
        return {
            'overall_status': overall_status,
            'healthy_services': healthy_count,
            'total_services': total_count,
            'health_percentage': (healthy_count / total_count) * 100,
            'timestamp': datetime.now().isoformat(),
            'services': results
        }
    
    def print_status(self, status: Dict[str, Any]):
        """Print formatted status to console"""
        print(f"\n🔍 NEXUS Health Check - {status['timestamp']}")
        print(f"Overall Status: {self._get_status_emoji(status['overall_status'])} {status['overall_status'].upper()}")
        print(f"Healthy Services: {status['healthy_services']}/{status['total_services']} ({status['health_percentage']:.1f}%)")
        print("\nService Details:")
        print("-" * 80)
        
        for service in status['services']:
            status_emoji = self._get_status_emoji(service['status'])
            print(f"{status_emoji} {service['name']:<12} | {service['status']:<10} | {service['url']}")
            
            if 'error' in service and service['error']:
                print(f"    Error: {service['error']}")
            
            if 'response_time' in service and service['response_time'] > 0:
                print(f"    Response Time: {service['response_time']:.3f}s")
        
        print("-" * 80)
    
    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for status"""
        emoji_map = {
            'healthy': '✅',
            'degraded': '⚠️',
            'unhealthy': '❌',
            'unknown': '❓'
        }
        return emoji_map.get(status, '❓')

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='NEXUS Health Checker')
    parser.add_argument('--json', action='store_true', help='Output JSON format')
    parser.add_argument('--service', help='Check specific service only')
    
    args = parser.parse_args()
    
    checker = HealthChecker()
    
    if args.service and args.service in checker.services:
        # Check specific service
        config = checker.services[args.service]
        if 'type' in config:
            if config['type'] == 'postgresql':
                result = checker.check_database(args.service, config)
            elif config['type'] == 'redis':
                result = checker.check_redis(args.service, config)
            else:
                result = {'name': args.service, 'status': 'unknown', 'error': 'Unsupported type'}
        else:
            result = checker.check_http_service(args.service, config)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            checker.print_status({'services': [result], 'overall_status': result['status']})
    else:
        # Check all services
        status = checker.check_all_services()
        
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            checker.print_status(status)

if __name__ == "__main__":
    main()
