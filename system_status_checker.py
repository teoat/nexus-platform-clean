#!/usr/bin/env python3
"""
NEXUS Platform - System Status Checker
Quick system health and status verification
"""

import json
import os
import sqlite3
import time
import requests
from datetime import datetime
from pathlib import Path
import psutil

def check_system_status():
    """Check overall system status"""
    print("🔍 NEXUS PLATFORM - SYSTEM STATUS CHECK")
    print("="*60)
    
    status = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "healthy",
        "checks": {}
    }
    
    # Check system resources
    print("\n💻 System Resources:")
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        print(f"  CPU Usage: {cpu_percent:.1f}%")
        print(f"  Memory Usage: {memory.percent:.1f}% ({memory.used // (1024**3)} GB / {memory.total // (1024**3)} GB)")
        print(f"  Disk Usage: {(disk.used / disk.total) * 100:.1f}% ({disk.used // (1024**3)} GB / {disk.total // (1024**3)} GB)")
        
        status["checks"]["system_resources"] = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": (disk.used / disk.total) * 100,
            "status": "healthy" if cpu_percent < 80 and memory.percent < 85 else "warning"
        }
    except Exception as e:
        print(f"  ❌ Error checking system resources: {e}")
        status["checks"]["system_resources"] = {"status": "error", "error": str(e)}
    
    # Check database files
    print("\n🗄️ Database Status:")
    db_files = ["nexus_platform.db", "nexus.db"]
    for db_file in db_files:
        if Path(db_file).exists():
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                file_size = Path(db_file).stat().st_size // (1024**2)  # MB
                conn.close()
                
                print(f"  ✅ {db_file}: {len(tables)} tables, {file_size} MB")
                status["checks"][f"database_{db_file}"] = {
                    "status": "healthy",
                    "table_count": len(tables),
                    "file_size_mb": file_size
                }
            except Exception as e:
                print(f"  ❌ {db_file}: Error - {e}")
                status["checks"][f"database_{db_file}"] = {"status": "error", "error": str(e)}
        else:
            print(f"  ⚠️ {db_file}: Not found")
            status["checks"][f"database_{db_file}"] = {"status": "missing"}
    
    # Check API endpoints
    print("\n🌐 API Endpoints:")
    endpoints = [
        "http://localhost:8000/health",
        "http://localhost:8000/api/health",
        "http://localhost:8000/api/status",
        "http://localhost:3000/"  # Frontend
    ]
    
    for endpoint in endpoints:
        try:
            start_time = time.time()
            response = requests.get(endpoint, timeout=5)
            response_time = (time.time() - start_time) * 1000  # ms
            
            if response.status_code == 200:
                print(f"  ✅ {endpoint}: {response.status_code} ({response_time:.0f}ms)")
                status["checks"][f"api_{endpoint.split('//')[1].replace('/', '_')}"] = {
                    "status": "healthy",
                    "response_code": response.status_code,
                    "response_time_ms": response_time
                }
            else:
                print(f"  ⚠️ {endpoint}: {response.status_code} ({response_time:.0f}ms)")
                status["checks"][f"api_{endpoint.split('//')[1].replace('/', '_')}"] = {
                    "status": "warning",
                    "response_code": response.status_code,
                    "response_time_ms": response_time
                }
        except Exception as e:
            print(f"  ❌ {endpoint}: Error - {e}")
            status["checks"][f"api_{endpoint.split('//')[1].replace('/', '_')}"] = {
                "status": "error",
                "error": str(e)
            }
    
    # Check critical files
    print("\n📁 Critical Files:")
    critical_files = [
        "docker-compose.yml",
        "docker-compose.prod.yml",
        "Dockerfile",
        "nginx.conf",
        "requirements.txt",
        "package.json",
        "focused_verification.py",
        "deploy_production_complete.py"
    ]
    
    for file_path in critical_files:
        if Path(file_path).exists():
            file_size = Path(file_path).stat().st_size
            print(f"  ✅ {file_path}: {file_size:,} bytes")
            status["checks"][f"file_{file_path}"] = {
                "status": "healthy",
                "file_size": file_size
            }
        else:
            print(f"  ❌ {file_path}: Missing")
            status["checks"][f"file_{file_path}"] = {"status": "missing"}
    
    # Check directories
    print("\n📂 Critical Directories:")
    critical_dirs = [
        "backend/",
        "frontend/",
        "nexus/",
        "services/",
        "monitoring/",
        "tests/",
        "docs/"
    ]
    
    for dir_path in critical_dirs:
        if Path(dir_path).exists():
            file_count = len(list(Path(dir_path).rglob('*')))
            print(f"  ✅ {dir_path}: {file_count} files")
            status["checks"][f"dir_{dir_path.replace('/', '')}"] = {
                "status": "healthy",
                "file_count": file_count
            }
        else:
            print(f"  ❌ {dir_path}: Missing")
            status["checks"][f"dir_{dir_path.replace('/', '')}"] = {"status": "missing"}
    
    # Determine overall status
    error_count = sum(1 for check in status["checks"].values() if check.get("status") == "error")
    warning_count = sum(1 for check in status["checks"].values() if check.get("status") == "warning")
    missing_count = sum(1 for check in status["checks"].values() if check.get("status") == "missing")
    
    if error_count > 0:
        status["overall_status"] = "error"
    elif warning_count > 0 or missing_count > 0:
        status["overall_status"] = "warning"
    else:
        status["overall_status"] = "healthy"
    
    # Print summary
    print("\n" + "="*60)
    print("📊 SYSTEM STATUS SUMMARY")
    print("="*60)
    print(f"Overall Status: {status['overall_status'].upper()}")
    print(f"Errors: {error_count}")
    print(f"Warnings: {warning_count}")
    print(f"Missing: {missing_count}")
    
    if status["overall_status"] == "healthy":
        print("\n🎉 SYSTEM IS HEALTHY AND READY FOR PRODUCTION!")
    elif status["overall_status"] == "warning":
        print("\n⚠️ SYSTEM HAS WARNINGS - REVIEW BEFORE PRODUCTION")
    else:
        print("\n❌ SYSTEM HAS ERRORS - FIX BEFORE PRODUCTION")
    
    # Save status report
    status_file = Path("system_status_report.json")
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2)
    
    print(f"\n📊 Status report saved to: {status_file}")
    print("="*60)
    
    return status

if __name__ == "__main__":
    check_system_status()
