#!/usr/bin/env python3
"""
NEXUS Platform - Automated Dependency Management
This script manages dependencies across the entire platform with security scanning and updates.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
import yaml


class DependencyManager:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "frontend": {},
            "backend": {},
            "security": {},
            "recommendations": [],
        }

    def run_command(
        self, command: str, cwd: Optional[str] = None
    ) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr"""
        try:
            result = subprocess.run(
                command.split(),
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=300,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)

    def analyze_frontend_dependencies(self) -> Dict:
        """Analyze frontend dependencies for issues"""
        print("🔍 Analyzing frontend dependencies...")

        frontend_path = self.project_root / "frontend" / "web"
        if not frontend_path.exists():
            return {"error": "Frontend directory not found"}

        # Check package.json
        package_json_path = frontend_path / "package.json"
        if not package_json_path.exists():
            return {"error": "package.json not found"}

        with open(package_json_path) as f:
            package_data = json.load(f)

        # Run npm audit
        exit_code, stdout, stderr = self.run_command(
            "npm audit --json", cwd=str(frontend_path)
        )
        audit_data = {}
        if exit_code == 0:
            try:
                audit_data = json.loads(stdout)
            except json.JSONDecodeError:
                audit_data = {"error": "Failed to parse audit output"}

        # Check for outdated packages
        exit_code, outdated_output, _ = self.run_command(
            "npm outdated --json", cwd=str(frontend_path)
        )
        outdated_data = {}
        if exit_code != 0:  # npm outdated returns non-zero when packages are outdated
            try:
                outdated_data = json.loads(outdated_output)
            except json.JSONDecodeError:
                outdated_data = {}

        # Analyze bundle size
        exit_code, build_output, _ = self.run_command(
            "npm run build", cwd=str(frontend_path)
        )
        build_success = exit_code == 0

        return {
            "package_count": len(package_data.get("dependencies", {})),
            "dev_dependencies": len(package_data.get("devDependencies", {})),
            "vulnerabilities": audit_data.get("vulnerabilities", {}),
            "outdated_packages": outdated_data,
            "build_success": build_success,
            "audit_summary": audit_data.get("metadata", {}),
        }

    def analyze_backend_dependencies(self) -> Dict:
        """Analyze backend Python dependencies for issues"""
        print("🔍 Analyzing backend dependencies...")

        requirements_files = ["requirements.txt", "requirements-production.txt"]

        backend_analysis = {}

        for req_file in requirements_files:
            req_path = self.project_root / req_file
            if not req_path.exists():
                continue

            # Parse requirements
            with open(req_path) as f:
                requirements = f.readlines()

            # Check for conflicts
            exit_code, check_output, check_error = self.run_command("pip check")
            conflicts = []
            if exit_code != 0:
                conflicts = check_error.strip().split("\n")

            # Security scan
            exit_code, safety_output, _ = self.run_command("safety check --json")
            safety_data = {}
            if exit_code == 0:
                try:
                    safety_data = json.loads(safety_output)
                except json.JSONDecodeError:
                    safety_data = {"error": "Failed to parse safety output"}

            backend_analysis[req_file] = {
                "requirement_count": len(
                    [r for r in requirements if r.strip() and not r.startswith("#")]
                ),
                "conflicts": conflicts,
                "security_issues": safety_data,
            }

        return backend_analysis

    def check_docker_configurations(self) -> Dict:
        """Check Docker configurations for optimization opportunities"""
        print("🔍 Analyzing Docker configurations...")

        docker_files = list(self.project_root.glob("**/Dockerfile*"))
        docker_compose_files = list(self.project_root.glob("**/docker-compose*.yml"))

        docker_analysis = {
            "dockerfiles": len(docker_files),
            "compose_files": len(docker_compose_files),
            "optimization_opportunities": [],
        }

        for dockerfile in docker_files:
            with open(dockerfile) as f:
                content = f.read()

            # Check for multi-stage builds
            if "FROM" in content and content.count("FROM") > 1:
                docker_analysis["optimization_opportunities"].append(
                    f"{dockerfile.name}: Multi-stage build detected ✅"
                )
            else:
                docker_analysis["optimization_opportunities"].append(
                    f"{dockerfile.name}: Consider multi-stage build"
                )

            # Check for .dockerignore
            dockerignore_path = dockerfile.parent / ".dockerignore"
            if dockerignore_path.exists():
                docker_analysis["optimization_opportunities"].append(
                    f"{dockerfile.name}: .dockerignore present ✅"
                )
            else:
                docker_analysis["optimization_opportunities"].append(
                    f"{dockerfile.name}: Add .dockerignore file"
                )

        return docker_analysis

    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        # Frontend recommendations
        if self.report["frontend"].get("vulnerabilities"):
            vuln_count = len(self.report["frontend"]["vulnerabilities"])
            recommendations.append(
                f"🚨 Fix {vuln_count} frontend security vulnerabilities"
            )

        if self.report["frontend"].get("outdated_packages"):
            outdated_count = len(self.report["frontend"]["outdated_packages"])
            recommendations.append(
                f"📦 Update {outdated_count} outdated frontend packages"
            )

        # Backend recommendations
        for req_file, analysis in self.report["backend"].items():
            if analysis.get("conflicts"):
                recommendations.append(
                    f"⚠️ Resolve {len(analysis['conflicts'])} dependency conflicts in {req_file}"
                )

        # General recommendations
        recommendations.extend(
            [
                "🔒 Enable automated security scanning in CI/CD",
                "📊 Set up dependency monitoring with Renovate or Dependabot",
                "🚀 Implement build caching for faster CI/CD",
                "📈 Add performance monitoring to production builds",
            ]
        )

        return recommendations

    def create_dependency_report(self) -> str:
        """Create a comprehensive dependency report"""
        report_path = self.project_root / "DEPENDENCY_ANALYSIS_REPORT.md"

        with open(report_path, "w") as f:
            f.write("# NEXUS Platform - Dependency Analysis Report\n\n")
            f.write(f"**Generated:** {self.report['timestamp']}\n\n")

            # Frontend section
            f.write("## Frontend Dependencies\n\n")
            frontend = self.report["frontend"]
            if "error" not in frontend:
                f.write(
                    f"- **Total Dependencies:** {frontend.get('package_count', 0)}\n"
                )
                f.write(
                    f"- **Dev Dependencies:** {frontend.get('dev_dependencies', 0)}\n"
                )
                f.write(
                    f"- **Build Status:** {'✅ Success' if frontend.get('build_success') else '❌ Failed'}\n"
                )

                vulns = frontend.get("vulnerabilities", {})
                if vulns:
                    f.write(f"- **Security Vulnerabilities:** {len(vulns)} found\n")
                else:
                    f.write("- **Security Vulnerabilities:** ✅ None found\n")
            else:
                f.write(f"- **Error:** {frontend['error']}\n")

            # Backend section
            f.write("\n## Backend Dependencies\n\n")
            for req_file, analysis in self.report["backend"].items():
                f.write(f"### {req_file}\n")
                f.write(f"- **Requirements:** {analysis.get('requirement_count', 0)}\n")
                f.write(f"- **Conflicts:** {len(analysis.get('conflicts', []))}\n")
                f.write(
                    f"- **Security Issues:** {len(analysis.get('security_issues', {}))}\n\n"
                )

            # Recommendations
            f.write("## Recommendations\n\n")
            for i, rec in enumerate(self.report["recommendations"], 1):
                f.write(f"{i}. {rec}\n")

            f.write("\n## Next Steps\n\n")
            f.write(
                "1. Run `./scripts/optimize-production-build.sh` to apply optimizations\n"
            )
            f.write("2. Review and fix security vulnerabilities\n")
            f.write("3. Update outdated dependencies\n")
            f.write("4. Set up automated dependency monitoring\n")

        return str(report_path)

    def run_full_analysis(self) -> None:
        """Run complete dependency analysis"""
        print("🚀 Starting NEXUS Platform Dependency Analysis...")

        # Analyze frontend
        self.report["frontend"] = self.analyze_frontend_dependencies()

        # Analyze backend
        self.report["backend"] = self.analyze_backend_dependencies()

        # Check Docker configurations
        self.report["docker"] = self.check_docker_configurations()

        # Generate recommendations
        self.report["recommendations"] = self.generate_recommendations()

        # Create report
        report_path = self.create_dependency_report()

        print(f"✅ Analysis complete! Report saved to: {report_path}")
        print(f"📊 Found {len(self.report['recommendations'])} recommendations")

        # Print summary
        print("\n📋 Summary:")
        for rec in self.report["recommendations"][:5]:  # Show top 5
            print(f"  {rec}")


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = "."

    manager = DependencyManager(project_root)
    manager.run_full_analysis()


if __name__ == "__main__":
    main()
