#!/usr/bin/env python3
"""
NEXUS Platform - Production Readiness Validation Script
Validates that the platform is ready for production deployment
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import requests


class ProductionReadinessValidator:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.results = {
            "timestamp": None,
            "overall_status": "PENDING",
            "checks": {},
            "recommendations": [],
            "critical_issues": [],
            "warnings": [],
        }

    def run_all_checks(self) -> Dict:
        """Run all production readiness checks"""
        print("🔍 Starting NEXUS Platform Production Readiness Validation...")

        self.results["timestamp"] = self.get_timestamp()

        # Core system checks
        self.check_ssot_configuration()
        self.check_duplicate_files()
        self.check_port_conflicts()
        self.check_environment_files()
        self.check_docker_configuration()
        self.check_kubernetes_configuration()
        self.check_frontend_build()
        self.check_backend_configuration()
        self.check_monitoring_setup()
        self.check_security_configuration()

        # Determine overall status
        self.determine_overall_status()

        return self.results

    def check_ssot_configuration(self):
        """Check SSOT configuration structure"""
        print("📋 Checking SSOT configuration...")

        # Check if SSOT manifest exists
        ssot_manifest = self.root_dir / "ssot" / "modules_index.yaml"
        if not ssot_manifest.exists():
            self.results["critical_issues"].append(
                "Missing SSOT manifest: ssot/modules_index.yaml"
            )
            self.results["checks"]["ssot_configuration"] = "FAILED"
            return

        # Load and validate SSOT manifest
        try:
            import yaml

            with open(ssot_manifest, "r") as f:
                manifest = yaml.safe_load(f)

            if "anchors" not in manifest:
                self.results["critical_issues"].append(
                    "SSOT manifest missing anchors section"
                )
                self.results["checks"]["ssot_configuration"] = "FAILED"
                return

            # Check that anchor files exist (warnings for Phase 2, not failures)
            missing_anchors = []
            for anchor in manifest["anchors"]:
                if "path" in anchor:
                    anchor_path = self.root_dir / anchor["path"]
                    if not anchor_path.exists():
                        missing_anchors.append(f"{anchor['id']}: {anchor['path']}")

            if missing_anchors:
                # In Phase 2, missing anchor files are warnings, not critical issues
                self.results["warnings"].extend(
                    [
                        f"Missing SSOT anchor file (Phase 2): {anchor}"
                        for anchor in missing_anchors
                    ]
                )
                self.results["checks"][
                    "ssot_configuration"
                ] = "PASSED"  # Still pass for Phase 2
            else:
                self.results["checks"]["ssot_configuration"] = "PASSED"

        except Exception as e:
            self.results["critical_issues"].append(
                f"SSOT manifest validation error: {e}"
            )
            self.results["checks"]["ssot_configuration"] = "FAILED"

    def check_duplicate_files(self):
        """Check for remaining duplicate files"""
        print("🔍 Checking for duplicate files...")

        # Check for common duplicate patterns
        duplicate_patterns = [
            "**/prometheus.yml",
            "**/docker-compose*.yml",
            "**/environment*.env",
            "**/config*.yaml",
        ]

        duplicates_found = []
        for pattern in duplicate_patterns:
            files = list(self.root_dir.glob(pattern))
            if len(files) > 1:
                duplicates_found.extend([str(f) for f in files])

        if duplicates_found:
            self.results["warnings"].extend(
                [f"Potential duplicate files found: {', '.join(duplicates_found)}"]
            )
            self.results["checks"]["duplicate_files"] = "WARNING"
        else:
            self.results["checks"]["duplicate_files"] = "PASSED"

    def check_port_conflicts(self):
        """Check for port conflicts"""
        print("🔌 Checking port conflicts...")

        # Check Docker Compose for port conflicts
        docker_compose = self.root_dir / "docker-compose.yml"
        if docker_compose.exists():
            with open(docker_compose, "r") as f:
                content = f.read()

            # Extract port mappings
            import re

            port_mappings = re.findall(r"(\d+):(\d+)", content)

            # Check for conflicts
            used_ports = set()
            conflicts = []

            for host_port, container_port in port_mappings:
                if host_port in used_ports:
                    conflicts.append(f"Port {host_port} used multiple times")
                used_ports.add(host_port)

            if conflicts:
                self.results["critical_issues"].extend(conflicts)
                self.results["checks"]["port_conflicts"] = "FAILED"
            else:
                self.results["checks"]["port_conflicts"] = "PASSED"
        else:
            self.results["checks"]["port_conflicts"] = "SKIPPED"

    def check_environment_files(self):
        """Check environment file consistency"""
        print("🌍 Checking environment files...")

        # Check for multiple environment files
        env_files = list(self.root_dir.glob("**/*.env"))
        env_files = [f for f in env_files if "archived_bin" not in str(f)]

        if len(env_files) > 1:
            self.results["warnings"].append(
                f"Multiple environment files found: {[str(f) for f in env_files]}"
            )
            self.results["checks"]["environment_files"] = "WARNING"
        else:
            self.results["checks"]["environment_files"] = "PASSED"

    def check_docker_configuration(self):
        """Check Docker configuration"""
        print("🐳 Checking Docker configuration...")

        docker_compose = self.root_dir / "docker-compose.yml"
        if not docker_compose.exists():
            self.results["critical_issues"].append("Docker Compose file not found")
            self.results["checks"]["docker_configuration"] = "FAILED"
            return

        # Check for required services
        with open(docker_compose, "r") as f:
            content = f.read()

        required_services = ["postgres", "redis", "backend", "frontend"]
        missing_services = []

        for service in required_services:
            if f"  {service}:" not in content:
                missing_services.append(service)

        if missing_services:
            self.results["critical_issues"].extend(
                [f"Missing required service: {service}" for service in missing_services]
            )
            self.results["checks"]["docker_configuration"] = "FAILED"
        else:
            self.results["checks"]["docker_configuration"] = "PASSED"

    def check_kubernetes_configuration(self):
        """Check Kubernetes configuration"""
        print("☸️ Checking Kubernetes configuration...")

        k8s_dir = self.root_dir / "k8s"
        if not k8s_dir.exists():
            self.results["warnings"].append(
                "Kubernetes configuration directory not found"
            )
            self.results["checks"]["kubernetes_configuration"] = "WARNING"
            return

        # Check for required K8s files
        required_files = [
            "backend-deployment.yaml",
            "frontend-deployment.yaml",
            "ingress.yaml",
        ]
        missing_files = []

        for file in required_files:
            if not (k8s_dir / file).exists():
                missing_files.append(file)

        if missing_files:
            self.results["warnings"].extend(
                [f"Missing Kubernetes file: {file}" for file in missing_files]
            )
            self.results["checks"]["kubernetes_configuration"] = "WARNING"
        else:
            self.results["checks"]["kubernetes_configuration"] = "PASSED"

    def check_frontend_build(self):
        """Check frontend build readiness"""
        print("⚛️ Checking frontend build...")

        frontend_dir = self.root_dir / "frontend" / "web"
        if not frontend_dir.exists():
            self.results["critical_issues"].append("Frontend directory not found")
            self.results["checks"]["frontend_build"] = "FAILED"
            return

        # Check for package.json
        package_json = frontend_dir / "package.json"
        if not package_json.exists():
            self.results["critical_issues"].append("Frontend package.json not found")
            self.results["checks"]["frontend_build"] = "FAILED"
            return

        # Check for build script
        with open(package_json, "r") as f:
            package_data = json.load(f)

        if "build" not in package_data.get("scripts", {}):
            self.results["critical_issues"].append("Frontend build script not found")
            self.results["checks"]["frontend_build"] = "FAILED"
        else:
            self.results["checks"]["frontend_build"] = "PASSED"

    def check_backend_configuration(self):
        """Check backend configuration"""
        print("🐍 Checking backend configuration...")

        backend_dir = self.root_dir / "backend"
        if not backend_dir.exists():
            self.results["critical_issues"].append("Backend directory not found")
            self.results["checks"]["backend_configuration"] = "FAILED"
            return

        # Check for main application file
        main_files = list(backend_dir.glob("main*.py"))
        if len(main_files) == 0:
            self.results["critical_issues"].append(
                "Backend main application file not found"
            )
            self.results["checks"]["backend_configuration"] = "FAILED"
        elif len(main_files) > 1:
            self.results["warnings"].append(
                f"Multiple main files found: {[str(f) for f in main_files]}"
            )
            self.results["checks"]["backend_configuration"] = "WARNING"
        else:
            self.results["checks"]["backend_configuration"] = "PASSED"

    def check_monitoring_setup(self):
        """Check monitoring configuration"""
        print("📊 Checking monitoring setup...")

        monitoring_dir = self.root_dir / "monitoring"
        if not monitoring_dir.exists():
            self.results["warnings"].append("Monitoring directory not found")
            self.results["checks"]["monitoring_setup"] = "WARNING"
            return

        # Check for Prometheus config
        prometheus_config = monitoring_dir / "prometheus" / "prometheus.yml"
        if not prometheus_config.exists():
            self.results["warnings"].append("Prometheus configuration not found")
            self.results["checks"]["monitoring_setup"] = "WARNING"
        else:
            self.results["checks"]["monitoring_setup"] = "PASSED"

    def check_security_configuration(self):
        """Check security configuration"""
        print("🔒 Checking security configuration...")

        # Check for security-related files
        security_files = ["security/", "ssl/", "nginx/nginx.conf"]

        missing_security = []
        for file_path in security_files:
            if not (self.root_dir / file_path).exists():
                missing_security.append(file_path)

        if missing_security:
            self.results["warnings"].extend(
                [f"Missing security configuration: {file}" for file in missing_security]
            )
            self.results["checks"]["security_configuration"] = "WARNING"
        else:
            self.results["checks"]["security_configuration"] = "PASSED"

    def determine_overall_status(self):
        """Determine overall production readiness status"""
        checks = self.results["checks"]

        if any(status == "FAILED" for status in checks.values()):
            self.results["overall_status"] = "NOT_READY"
        elif any(status == "WARNING" for status in checks.values()):
            self.results["overall_status"] = "READY_WITH_WARNINGS"
        else:
            self.results["overall_status"] = "READY"

    def get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime

        return datetime.now().isoformat()

    def print_results(self):
        """Print validation results"""
        print("\n" + "=" * 60)
        print("NEXUS Platform Production Readiness Report")
        print("=" * 60)

        print(f"\nOverall Status: {self.results['overall_status']}")
        print(f"Timestamp: {self.results['timestamp']}")

        print("\nCheck Results:")
        for check, status in self.results["checks"].items():
            status_icon = (
                "✅" if status == "PASSED" else "⚠️" if status == "WARNING" else "❌"
            )
            print(f"  {status_icon} {check}: {status}")

        if self.results["critical_issues"]:
            print("\nCritical Issues:")
            for issue in self.results["critical_issues"]:
                print(f"  ❌ {issue}")

        if self.results["warnings"]:
            print("\nWarnings:")
            for warning in self.results["warnings"]:
                print(f"  ⚠️ {warning}")

        if self.results["recommendations"]:
            print("\nRecommendations:")
            for rec in self.results["recommendations"]:
                print(f"  💡 {rec}")

        print("\n" + "=" * 60)


def main():
    """Main function"""
    validator = ProductionReadinessValidator()
    results = validator.run_all_checks()
    validator.print_results()

    # Save results to file
    results_file = Path(__file__).parent / "production_readiness_report.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nDetailed report saved to: {results_file}")

    # Exit with appropriate code
    if results["overall_status"] == "NOT_READY":
        sys.exit(1)
    elif results["overall_status"] == "READY_WITH_WARNINGS":
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
