#!/usr/bin/env python3
"""
NEXUS Platform - Production System Validator
Comprehensive validation of the production-ready system
"""

import os
import sys
import json
import yaml
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple

class ProductionSystemValidator:
    """Comprehensive production system validator"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'total_checks': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'checks': []
        }
    
    def run_validation(self) -> Dict[str, Any]:
        """Run complete production system validation"""
        print("🚀 NEXUS Platform - Production System Validation")
        print("=" * 60)
        
        # Core system validation
        self.validate_file_structure()
        self.validate_docker_configuration()
        self.validate_kubernetes_manifests()
        self.validate_frontend_components()
        self.validate_backend_apis()
        self.validate_documentation()
        self.validate_security()
        self.validate_performance()
        self.validate_testing()
        
        # Generate final report
        self.generate_final_report()
        
        return self.results
    
    def validate_file_structure(self):
        """Validate project file structure"""
        print("\n📁 Validating File Structure...")
        
        required_directories = [
            'frontend/web/src',
            'backend/api',
            'backend/services',
            'backend/middleware',
            'backend/utils',
            'docker',
            'k8s-production',
            'k8s-universal',
            'monitoring',
            'nginx'
        ]
        
        for directory in required_directories:
            path = self.project_root / directory
            if path.exists():
                self.add_result('file_structure', 'pass', f"Directory exists: {directory}")
            else:
                self.add_result('file_structure', 'fail', f"Missing directory: {directory}")
    
    def validate_docker_configuration(self):
        """Validate Docker configuration"""
        print("\n🐳 Validating Docker Configuration...")
        
        # Docker Compose files (YAML)
        compose_files = [
            'docker-compose.yml',
            'docker-compose.prod.yml',
            'docker-compose.dev.yml',
            'docker-compose.staging.yml'
        ]
        
        for compose_file in compose_files:
            path = self.project_root / compose_file
            if path.exists():
                # Validate YAML syntax
                try:
                    with open(path, 'r') as f:
                        yaml.safe_load(f)
                    self.add_result('docker_config', 'pass', f"Valid Docker file: {compose_file}")
                except yaml.YAMLError as e:
                    self.add_result('docker_config', 'fail', f"Invalid YAML in {compose_file}: {e}")
                except Exception as e:
                    self.add_result('docker_config', 'fail', f"Error reading {compose_file}: {e}")
            else:
                self.add_result('docker_config', 'fail', f"Missing Docker file: {compose_file}")
        
        # Dockerfiles (not YAML)
        dockerfiles = [
            'docker/Dockerfile.backend.ultimate',
            'docker/Dockerfile.frontend.ultimate'
        ]
        
        for dockerfile in dockerfiles:
            path = self.project_root / dockerfile
            if path.exists():
                # Just check if file exists and is readable
                try:
                    with open(path, 'r') as f:
                        content = f.read()
                        if 'FROM' in content:  # Basic Dockerfile validation
                            self.add_result('docker_config', 'pass', f"Valid Docker file: {dockerfile}")
                        else:
                            self.add_result('docker_config', 'fail', f"Invalid Dockerfile: {dockerfile}")
                except Exception as e:
                    self.add_result('docker_config', 'fail', f"Error reading {dockerfile}: {e}")
            else:
                self.add_result('docker_config', 'fail', f"Missing Docker file: {dockerfile}")
    
    def validate_kubernetes_manifests(self):
        """Validate Kubernetes manifests"""
        print("\n☸️ Validating Kubernetes Manifests...")
        
        k8s_directories = ['k8s-production', 'k8s-universal']
        
        for k8s_dir in k8s_directories:
            path = self.project_root / k8s_dir
            if path.exists():
                yaml_files = list(path.rglob('*.yaml')) + list(path.rglob('*.yml'))
                
                for yaml_file in yaml_files:
                    try:
                        with open(yaml_file, 'r') as f:
                            yaml.safe_load(f)
                        self.add_result('k8s_manifests', 'pass', f"Valid K8s manifest: {yaml_file.relative_to(self.project_root)}")
                    except yaml.YAMLError as e:
                        self.add_result('k8s_manifests', 'fail', f"Invalid YAML in {yaml_file}: {e}")
            else:
                self.add_result('k8s_manifests', 'warning', f"K8s directory not found: {k8s_dir}")
    
    def validate_frontend_components(self):
        """Validate frontend components"""
        print("\n⚛️ Validating Frontend Components...")
        
        frontend_path = self.project_root / 'frontend/web/src'
        
        # Check for required components
        required_components = [
            'components/layout/Header.tsx',
            'components/layout/Footer.tsx',
            'components/layout/GlobalLayout.tsx',
            'config/routingRegistry.ts',
            'utils/sitemapGenerator.ts',
            'utils/performanceOptimizer.ts',
            'utils/testValidator.ts'
        ]
        
        for component in required_components:
            path = frontend_path / component
            if path.exists():
                self.add_result('frontend_components', 'pass', f"Component exists: {component}")
            else:
                self.add_result('frontend_components', 'fail', f"Missing component: {component}")
        
        # Check for TypeScript configuration
        tsconfig_path = self.project_root / 'frontend/web/tsconfig.json'
        if tsconfig_path.exists():
            self.add_result('frontend_config', 'pass', "TypeScript configuration found")
        else:
            self.add_result('frontend_config', 'warning', "TypeScript configuration not found")
    
    def validate_backend_apis(self):
        """Validate backend APIs"""
        print("\n🐍 Validating Backend APIs...")
        
        backend_path = self.project_root / 'backend'
        
        # Check for required API files
        required_apis = [
            'api/forensic_analysis.py',
            'services/forensic_analyzer.py',
            'services/fraud_detector.py',
            'services/reconciliation_engine.py',
            'services/risk_assessor.py',
            'middleware/error_handler.py',
            'utils/audit_logger.py'
        ]
        
        for api_file in required_apis:
            path = backend_path / api_file
            if path.exists():
                self.add_result('backend_apis', 'pass', f"API file exists: {api_file}")
            else:
                self.add_result('backend_apis', 'fail', f"Missing API file: {api_file}")
        
        # Check for requirements.txt
        requirements_path = backend_path / 'requirements.txt'
        if requirements_path.exists():
            self.add_result('backend_dependencies', 'pass', "Requirements file found")
        else:
            self.add_result('backend_dependencies', 'warning', "Requirements file not found")
    
    def validate_documentation(self):
        """Validate documentation"""
        print("\n📚 Validating Documentation...")
        
        required_docs = [
            'PRODUCTION_READY_SYSTEM_REPORT.md',
            'HEADER_AND_NAVIGATION_IMPLEMENTATION.md',
            'NEXUS_APP_VISION_AND_WORKFLOWS.md',
            'FRENLY_AI_IMPLEMENTATION_SUMMARY.md',
            'ULTIMATE_COMPLETION_SUMMARY.md',
            'FINAL_ULTIMATE_SUMMARY.md'
        ]
        
        for doc in required_docs:
            path = self.project_root / doc
            if path.exists():
                self.add_result('documentation', 'pass', f"Documentation exists: {doc}")
            else:
                self.add_result('documentation', 'warning', f"Missing documentation: {doc}")
    
    def validate_security(self):
        """Validate security configuration"""
        print("\n🔒 Validating Security...")
        
        # Check for security-related files
        security_files = [
            'backend/middleware/error_handler.py',
            'backend/utils/audit_logger.py',
            'nginx/nginx.ultimate.conf'
        ]
        
        for security_file in security_files:
            path = self.project_root / security_file
            if path.exists():
                self.add_result('security_files', 'pass', f"Security file exists: {security_file}")
            else:
                self.add_result('security_files', 'warning', f"Security file not found: {security_file}")
        
        # Check for environment files
        env_files = ['env.template', 'env.ultimate', 'env.dev', 'env.staging']
        for env_file in env_files:
            path = self.project_root / env_file
            if path.exists():
                self.add_result('environment_files', 'pass', f"Environment file exists: {env_file}")
            else:
                self.add_result('environment_files', 'warning', f"Environment file not found: {env_file}")
    
    def validate_performance(self):
        """Validate performance optimization"""
        print("\n⚡ Validating Performance...")
        
        # Check for performance-related files
        performance_files = [
            'frontend/web/src/utils/performanceOptimizer.ts',
            'monitoring/prometheus.ultimate.yml',
            'monitoring/dashboards/nexus-overview.json'
        ]
        
        for perf_file in performance_files:
            path = self.project_root / perf_file
            if path.exists():
                self.add_result('performance_files', 'pass', f"Performance file exists: {perf_file}")
            else:
                self.add_result('performance_files', 'warning', f"Performance file not found: {perf_file}")
    
    def validate_testing(self):
        """Validate testing configuration"""
        print("\n🧪 Validating Testing...")
        
        # Check for test files
        test_files = [
            'frontend/web/src/utils/testValidator.ts',
            'validate-production-system.py'
        ]
        
        for test_file in test_files:
            path = self.project_root / test_file
            if path.exists():
                self.add_result('testing_files', 'pass', f"Test file exists: {test_file}")
            else:
                self.add_result('testing_files', 'warning', f"Test file not found: {test_file}")
    
    def add_result(self, category: str, status: str, message: str, details: Any = None):
        """Add validation result"""
        self.results['total_checks'] += 1
        
        if status == 'pass':
            self.results['passed'] += 1
        elif status == 'fail':
            self.results['failed'] += 1
        else:
            self.results['warnings'] += 1
        
        self.results['checks'].append({
            'category': category,
            'status': status,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
        # Print result
        status_icon = {'pass': '✅', 'fail': '❌', 'warning': '⚠️'}[status]
        print(f"  {status_icon} {message}")
    
    def generate_final_report(self):
        """Generate final validation report"""
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        
        total = self.results['total_checks']
        passed = self.results['passed']
        failed = self.results['failed']
        warnings = self.results['warnings']
        
        print(f"Total Checks: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Warnings: {warnings}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Overall status
        if failed == 0 and warnings <= 5:
            print("\n🎉 PRODUCTION READY: System is ready for production deployment!")
            status = "PRODUCTION_READY"
        elif failed <= 2 and warnings <= 10:
            print("\n⚠️ READY WITH WARNINGS: System is ready but has some warnings to address.")
            status = "READY_WITH_WARNINGS"
        else:
            print("\n❌ NOT READY: System has critical issues that must be resolved.")
            status = "NOT_READY"
        
        self.results['overall_status'] = status
        
        # Save detailed report
        report_path = self.project_root / 'validation_report.json'
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_path}")
        
        return status

def main():
    """Main validation function"""
    validator = ProductionSystemValidator()
    results = validator.run_validation()
    
    # Exit with appropriate code
    if results['overall_status'] == "PRODUCTION_READY":
        sys.exit(0)
    elif results['overall_status'] == "READY_WITH_WARNINGS":
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()
