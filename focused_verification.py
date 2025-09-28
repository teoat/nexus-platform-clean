#!/usr/bin/env python3
"""
NEXUS Platform - Focused Verification System
Focused verification excluding backup directories and virtual environments
"""

import json
import logging
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FocusedVerifier:
    """Focused verification system for production-ready files only"""
    
    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        self.base_path = Path(base_path)
        self.results = []
        self.errors = []
        self.warnings = []
        self.todos = []
        self.critical_issues = []
        
        # Focus on production-ready directories only
        self.focus_directories = [
            "backend",
            "frontend",
            "scripts",
            "docker",
            "k8s",
            "monitoring",
            "security",
            "tests",
            "docs"
        ]
    
    def run_focused_verification(self):
        """Run focused verification on production files only"""
        logger.info("🔍 Starting focused verification...")
        print("\n" + "="*60)
        print("🔍 NEXUS PLATFORM - FOCUSED VERIFICATION")
        print("="*60)
        
        try:
            # Check 1: Core backend files
            self._check_backend_core()
            
            # Check 2: Frontend core files
            self._check_frontend_core()
            
            # Check 3: Docker configuration
            self._check_docker_config()
            
            # Check 4: Critical security issues
            self._check_critical_security()
            
            # Check 5: API endpoints
            self._check_api_endpoints()
            
            # Check 6: Database connections
            self._check_database_config()
            
            # Check 7: Production readiness
            self._check_production_readiness()
            
            # Generate report
            self._generate_focused_report()
            
            # Print summary
            self._print_focused_summary()
            
        except Exception as e:
            logger.error(f"Focused verification failed: {e}")
            print(f"\n❌ FOCUSED VERIFICATION FAILED: {e}")
    
    def _check_backend_core(self):
        """Check core backend files"""
        print("\n🔧 Checking backend core files...")
        
        backend_files = [
            "backend/main_unified.py",
            "backend/enhanced_api.py",
            "backend/requirements.txt",
            "backend/services/database.py",
            "backend/services/ssot_file_marker.py",
            "backend/routes/security_routes.py",
            "backend/routes/audit_routes.py"
        ]
        
        for file_path in backend_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Only check Python syntax for .py files
                    if file_path.endswith('.py'):
                        compile(content, str(full_path), 'exec')
                    
                    self.results.append({
                        'type': 'backend_core',
                        'status': 'pass',
                        'file': file_path,
                        'message': 'Backend core file OK'
                    })
                    
                    # Check for critical issues
                    self._check_file_critical_issues(full_path, content)
                    
                except SyntaxError as e:
                    self.errors.append({
                        'type': 'backend_syntax',
                        'file': file_path,
                        'line': e.lineno,
                        'message': f"Syntax error: {e.msg}"
                    })
                    print(f"❌ Syntax error in {file_path}:{e.lineno} - {e.msg}")
                
                except Exception as e:
                    self.warnings.append({
                        'type': 'backend_check',
                        'file': file_path,
                        'message': f"Could not check: {e}"
                    })
                    print(f"⚠️ Could not check {file_path}: {e}")
            else:
                self.warnings.append({
                    'type': 'backend_missing',
                    'file': file_path,
                    'message': 'Backend core file missing'
                })
                print(f"⚠️ Missing backend file: {file_path}")
    
    def _check_frontend_core(self):
        """Check core frontend files"""
        print("\n🌐 Checking frontend core files...")
        
        frontend_files = [
            "frontend/web/package.json",
            "frontend/web/src/App.tsx",
            "frontend/web/src/components/dashboard/UnifiedFinanceDashboard.tsx",
            "frontend/web/src/services/integrationService.ts",
            "frontend/web/webpack.unified.js"
        ]
        
        for file_path in frontend_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    self.results.append({
                        'type': 'frontend_core',
                        'status': 'pass',
                        'file': file_path,
                        'message': 'Frontend core file OK'
                    })
                    
                    # Check for critical issues
                    self._check_file_critical_issues(full_path, content)
                    
                except Exception as e:
                    self.warnings.append({
                        'type': 'frontend_check',
                        'file': file_path,
                        'message': f"Could not check: {e}"
                    })
                    print(f"⚠️ Could not check {file_path}: {e}")
            else:
                self.warnings.append({
                    'type': 'frontend_missing',
                    'file': file_path,
                    'message': 'Frontend core file missing'
                })
                print(f"⚠️ Missing frontend file: {file_path}")
    
    def _check_docker_config(self):
        """Check Docker configuration"""
        print("\n🐳 Checking Docker configuration...")
        
        docker_files = [
            "docker-compose.yml",
            "docker-compose.prod.yml",
            "Dockerfile",
            "Dockerfile.backend",
            "Dockerfile.frontend"
        ]
        
        for file_path in docker_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    self.results.append({
                        'type': 'docker_config',
                        'status': 'pass',
                        'file': file_path,
                        'message': 'Docker file OK'
                    })
                    
                    # Check for common Docker issues
                    if 'FROM' not in content and file_path.startswith('Dockerfile'):
                        self.warnings.append({
                            'type': 'docker_issue',
                            'file': file_path,
                            'message': 'Dockerfile missing FROM instruction'
                        })
                    
                except Exception as e:
                    self.warnings.append({
                        'type': 'docker_check',
                        'file': file_path,
                        'message': f"Could not check: {e}"
                    })
            else:
                self.warnings.append({
                    'type': 'docker_missing',
                    'file': file_path,
                    'message': 'Docker file missing'
                })
    
    def _check_critical_security(self):
        """Check for critical security issues"""
        print("\n🔒 Checking critical security issues...")
        
        security_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password", "critical"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret", "critical"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key", "critical"),
            (r'token\s*=\s*["\'][^"\']+["\']', "Hardcoded token", "critical"),
            (r'innerHTML\s*=', "XSS vulnerability", "high"),
            (r'eval\s*\(', "Code injection risk", "high"),
            (r'execute\s*\(\s*["\'].*%s.*["\']', "SQL injection risk", "critical")
        ]
        
        for directory in self.focus_directories:
            dir_path = self.base_path / directory
            if dir_path.exists():
                for file_path in dir_path.rglob("*.{py,ts,tsx,js,jsx}"):
                    if self._should_skip_file(file_path):
                        continue
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        lines = content.split('\n')
                        for i, line in enumerate(lines, 1):
                            for pattern, description, severity in security_patterns:
                                if re.search(pattern, line, re.IGNORECASE):
                                    issue = {
                                        'type': 'security',
                                        'file': str(file_path.relative_to(self.base_path)),
                                        'line': i,
                                        'message': f"{description}: {line.strip()}",
                                        'severity': severity
                                    }
                                    
                                    if severity == "critical":
                                        self.critical_issues.append(issue)
                                        print(f"🚨 CRITICAL: {description} in {file_path}:{i}")
                                    else:
                                        self.warnings.append(issue)
                                        print(f"⚠️ {description} in {file_path}:{i}")
                    
                    except Exception as e:
                        logger.debug(f"Could not check security in {file_path}: {e}")
    
    def _check_api_endpoints(self):
        """Check API endpoints"""
        print("\n🔗 Checking API endpoints...")
        
        # Check if backend is running
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                self.results.append({
                    'type': 'api_health',
                    'status': 'pass',
                    'message': 'Backend health endpoint responding'
                })
                print("✅ Backend health endpoint responding")
            else:
                self.warnings.append({
                    'type': 'api_health',
                    'message': f'Backend health endpoint returned {response.status_code}'
                })
                print(f"⚠️ Backend health endpoint returned {response.status_code}")
        except Exception as e:
            self.warnings.append({
                'type': 'api_health',
                'message': f'Backend health endpoint not accessible: {e}'
            })
            print(f"⚠️ Backend health endpoint not accessible: {e}")
        
        # Check frontend
        try:
            response = requests.get("http://localhost:3000", timeout=5)
            if response.status_code == 200:
                self.results.append({
                    'type': 'frontend_health',
                    'status': 'pass',
                    'message': 'Frontend responding'
                })
                print("✅ Frontend responding")
            else:
                self.warnings.append({
                    'type': 'frontend_health',
                    'message': f'Frontend returned {response.status_code}'
                })
                print(f"⚠️ Frontend returned {response.status_code}")
        except Exception as e:
            self.warnings.append({
                'type': 'frontend_health',
                'message': f'Frontend not accessible: {e}'
            })
            print(f"⚠️ Frontend not accessible: {e}")
    
    def _check_database_config(self):
        """Check database configuration"""
        print("\n🗄️ Checking database configuration...")
        
        # Check if database files exist
        db_files = [
            "nexus_platform.db",
            "nexus.db"
        ]
        
        for db_file in db_files:
            db_path = self.base_path / db_file
            if db_path.exists():
                self.results.append({
                    'type': 'database',
                    'status': 'pass',
                    'file': db_file,
                    'message': 'Database file exists'
                })
                print(f"✅ Database file exists: {db_file}")
            else:
                self.warnings.append({
                    'type': 'database',
                    'file': db_file,
                    'message': 'Database file missing'
                })
                print(f"⚠️ Database file missing: {db_file}")
    
    def _check_production_readiness(self):
        """Check production readiness"""
        print("\n🚀 Checking production readiness...")
        
        # Check for production configuration files
        prod_files = [
            "docker-compose.prod.yml",
            "Dockerfile.prod",
            "nginx.conf",
            "gunicorn.conf.py"
        ]
        
        for prod_file in prod_files:
            prod_path = self.base_path / prod_file
            if prod_path.exists():
                self.results.append({
                    'type': 'production',
                    'status': 'pass',
                    'file': prod_file,
                    'message': 'Production file exists'
                })
                print(f"✅ Production file exists: {prod_file}")
            else:
                self.warnings.append({
                    'type': 'production',
                    'file': prod_file,
                    'message': 'Production file missing'
                })
                print(f"⚠️ Production file missing: {prod_file}")
    
    def _check_file_critical_issues(self, file_path: Path, content: str):
        """Check file for critical issues"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for TODO comments
            if re.search(r'TODO[:\s]*(.+)', line, re.IGNORECASE):
                match = re.search(r'TODO[:\s]*(.+)', line, re.IGNORECASE)
                todo_text = match.group(1).strip()
                self.todos.append({
                    'file': str(file_path.relative_to(self.base_path)),
                    'line': i,
                    'text': todo_text
                })
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Determine if file should be skipped"""
        skip_patterns = {
            ".git", "node_modules", "__pycache__", ".pytest_cache",
            "venv", "env", ".venv", ".env", "archived_optimization",
            "locks", "ssot_registry", ".DS_Store", "Thumbs.db",
            "build", "dist", "coverage", "backup", "nexus_env"
        }
        
        return any(part in skip_patterns for part in file_path.parts)
    
    def _generate_focused_report(self):
        """Generate focused verification report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_checks": len(self.results),
                "errors": len(self.errors),
                "warnings": len(self.warnings),
                "critical_issues": len(self.critical_issues),
                "todos": len(self.todos)
            },
            "results": self.results,
            "errors": self.errors,
            "warnings": self.warnings,
            "critical_issues": self.critical_issues,
            "todos": self.todos
        }
        
        # Save report
        report_path = self.base_path / "focused_verification_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Focused verification report saved to {report_path}")
    
    def _print_focused_summary(self):
        """Print focused verification summary"""
        print("\n" + "="*60)
        print("🎯 FOCUSED VERIFICATION COMPLETE")
        print("="*60)
        print(f"✅ Checks Passed: {len(self.results)}")
        print(f"❌ Errors: {len(self.errors)}")
        print(f"⚠️ Warnings: {len(self.warnings)}")
        print(f"🚨 Critical Issues: {len(self.critical_issues)}")
        print(f"📝 TODOs: {len(self.todos)}")
        print("="*60)
        
        if self.critical_issues:
            print("\n🚨 CRITICAL ISSUES FOUND:")
            for issue in self.critical_issues[:10]:  # Show first 10
                print(f"  - {issue['file']}:{issue['line']} - {issue['message']}")
            if len(self.critical_issues) > 10:
                print(f"  ... and {len(self.critical_issues) - 10} more critical issues")
        
        if self.errors:
            print("\n❌ ERRORS FOUND:")
            for error in self.errors[:10]:  # Show first 10
                print(f"  - {error['file']}:{error.get('line', '?')} - {error['message']}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more errors")
        
        if self.warnings:
            print("\n⚠️ WARNINGS FOUND:")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"  - {warning['file']}:{warning.get('line', '?')} - {warning['message']}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more warnings")
        
        if self.todos:
            print("\n📝 TODOs FOUND:")
            for todo in self.todos[:10]:  # Show first 10
                print(f"  - {todo['file']}:{todo['line']} - {todo['text']}")
            if len(self.todos) > 10:
                print(f"  ... and {len(self.todos) - 10} more TODOs")
        
        print("="*60)
        
        # Production readiness assessment
        if self.critical_issues:
            print("\n🚨 NOT PRODUCTION READY - Critical issues must be fixed!")
        elif self.errors:
            print("\n❌ NOT PRODUCTION READY - Errors must be fixed!")
        elif self.warnings:
            print("\n⚠️ PRODUCTION READY WITH WARNINGS - Consider fixing warnings")
        else:
            print("\n🎉 PRODUCTION READY - No critical issues found!")


# Main execution
def main():
    """Main execution function"""
    verifier = FocusedVerifier()
    verifier.run_focused_verification()


if __name__ == "__main__":
    main()
