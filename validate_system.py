#!/usr/bin/env python3
"""
NEXUS Platform - System Validation Script
Comprehensive validation of frontend ↔ backend ↔ DB linkage
"""

import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SystemValidator:
    """Comprehensive system validation"""

    def __init__(self, root_path: str = "/Users/Arief/Desktop/Nexus"):
        self.root_path = Path(root_path)
        self.results = {
            "frontend": {"status": "pending", "issues": [], "warnings": []},
            "backend": {"status": "pending", "issues": [], "warnings": []},
            "database": {"status": "pending", "issues": [], "warnings": []},
            "integration": {"status": "pending", "issues": [], "warnings": []},
            "configuration": {"status": "pending", "issues": [], "warnings": []},
        }
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"

    def validate_configuration(self) -> bool:
        """Validate configuration consistency"""
        logger.info("🔧 Validating configuration consistency...")

        issues = []
        warnings = []

        # Check for duplicate main files
        main_files = list(self.root_path.rglob("main*.py"))
        if len(main_files) > 1:
            issues.append(f"Multiple main files found: {[f.name for f in main_files]}")

        # Check package.json consistency
        package_files = list(self.root_path.rglob("package.json"))
        if len(package_files) > 2:  # Allow frontend and mobile
            warnings.append(f"Multiple package.json files: {len(package_files)}")

        # Check Docker configuration
        docker_files = list(self.root_path.rglob("docker-compose*.yml"))
        if len(docker_files) > 3:  # Allow main, staging, production
            warnings.append(f"Multiple docker-compose files: {len(docker_files)}")

        # Check for .env files
        env_files = list(self.root_path.rglob(".env*"))
        if len(env_files) > 1:
            warnings.append(f"Multiple .env files: {len(env_files)}")

        self.results["configuration"]["issues"] = issues
        self.results["configuration"]["warnings"] = warnings
        self.results["configuration"]["status"] = "passed" if not issues else "failed"

        return len(issues) == 0

    def validate_frontend(self) -> bool:
        """Validate frontend build and configuration"""
        logger.info("🎨 Validating frontend...")

        issues = []
        warnings = []

        frontend_path = self.root_path / "frontend" / "web"

        # Check if package.json exists
        package_json = frontend_path / "package.json"
        if not package_json.exists():
            issues.append("package.json not found in frontend")
            return False

        # Check API configuration
        api_config = frontend_path / "src" / "config" / "api.ts"
        if api_config.exists():
            with open(api_config, "r") as f:
                content = f.read()
                if "localhost:8001" in content:
                    issues.append("Frontend API config still points to port 8001")
                if "/api/auth/" in content and "/api/v3/auth/" not in content:
                    issues.append("Frontend API endpoints not updated to v3")
        else:
            issues.append("API configuration file not found")

        # Check for duplicate components
        components = list(frontend_path.rglob("*.tsx"))
        component_names = [c.stem for c in components]
        duplicates = [
            name for name in set(component_names) if component_names.count(name) > 1
        ]
        if duplicates:
            warnings.append(f"Duplicate components found: {duplicates}")

        # Try to build frontend
        try:
            logger.info("Building frontend...")
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=frontend_path,
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode != 0:
                issues.append(f"Frontend build failed: {result.stderr}")
            else:
                logger.info("✅ Frontend build successful")
        except subprocess.TimeoutExpired:
            issues.append("Frontend build timed out")
        except FileNotFoundError:
            issues.append("npm not found - cannot build frontend")

        self.results["frontend"]["issues"] = issues
        self.results["frontend"]["warnings"] = warnings
        self.results["frontend"]["status"] = "passed" if not issues else "failed"

        return len(issues) == 0

    def validate_backend(self) -> bool:
        """Validate backend configuration and startup"""
        logger.info("⚙️ Validating backend...")

        issues = []
        warnings = []

        backend_path = self.root_path / "backend"

        # Check if main_unified.py exists
        main_file = backend_path / "main_unified.py"
        if not main_file.exists():
            issues.append("main_unified.py not found")
            return False

        # Check requirements.txt
        requirements = backend_path / "requirements.txt"
        if not requirements.exists():
            issues.append("requirements.txt not found")
        else:
            # Check for critical dependencies
            with open(requirements, "r") as f:
                content = f.read()
                critical_deps = ["fastapi", "uvicorn", "sqlalchemy", "psycopg2"]
                missing_deps = [dep for dep in critical_deps if dep not in content]
                if missing_deps:
                    issues.append(f"Missing critical dependencies: {missing_deps}")

        # Check database configuration
        db_config = backend_path / "database"
        if not db_config.exists():
            issues.append("Database configuration directory not found")

        # Try to start backend (if not already running)
        try:
            logger.info("Testing backend startup...")
            result = subprocess.run(
                ["python", "main_unified.py", "--help"],
                cwd=backend_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                issues.append(f"Backend startup test failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            issues.append("Backend startup test timed out")
        except FileNotFoundError:
            issues.append("Python not found - cannot test backend")

        self.results["backend"]["issues"] = issues
        self.results["backend"]["warnings"] = warnings
        self.results["backend"]["status"] = "passed" if not issues else "failed"

        return len(issues) == 0

    def validate_database(self) -> bool:
        """Validate database configuration"""
        logger.info("🗄️ Validating database configuration...")

        issues = []
        warnings = []

        backend_path = self.root_path / "backend" / "database"

        # Check for schema files
        schema_files = list(backend_path.rglob("*.sql"))
        if not schema_files:
            issues.append("No database schema files found")

        # Check for model files
        model_files = list(backend_path.rglob("models.py"))
        if not model_files:
            issues.append("No database model files found")

        # Check for migration files
        migration_files = list(backend_path.rglob("migration*"))
        if not migration_files:
            warnings.append("No database migration files found")

        # Check for duplicate schemas
        if len(schema_files) > 2:
            warnings.append(f"Multiple schema files found: {len(schema_files)}")

        self.results["database"]["issues"] = issues
        self.results["database"]["warnings"] = warnings
        self.results["database"]["status"] = "passed" if not issues else "failed"

        return len(issues) == 0

    def validate_integration(self) -> bool:
        """Validate frontend ↔ backend integration"""
        logger.info("🔗 Validating frontend ↔ backend integration...")

        issues = []
        warnings = []

        # Check if backend is running
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code != 200:
                issues.append(f"Backend health check failed: {response.status_code}")
            else:
                logger.info("✅ Backend is running")
        except requests.exceptions.RequestException:
            issues.append("Backend is not running or not accessible")
            return False

        # Test API endpoints
        endpoints_to_test = ["/api/health", "/api/status", "/api/metrics"]

        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                if response.status_code != 200:
                    issues.append(
                        f"Endpoint {endpoint} returned {response.status_code}"
                    )
                else:
                    logger.info(f"✅ Endpoint {endpoint} working")
            except requests.exceptions.RequestException as e:
                issues.append(f"Endpoint {endpoint} failed: {str(e)}")

        # Check CORS configuration
        try:
            headers = {
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type",
            }
            response = requests.options(
                f"{self.backend_url}/api/health", headers=headers, timeout=5
            )
            if "Access-Control-Allow-Origin" not in response.headers:
                warnings.append("CORS headers not properly configured")
        except requests.exceptions.RequestException:
            warnings.append("Could not test CORS configuration")

        self.results["integration"]["issues"] = issues
        self.results["integration"]["warnings"] = warnings
        self.results["integration"]["status"] = "passed" if not issues else "failed"

        return len(issues) == 0

    def run_full_validation(self) -> Dict[str, Any]:
        """Run complete system validation"""
        logger.info("🚀 Starting comprehensive system validation...")

        start_time = time.time()

        # Run all validations
        config_ok = self.validate_configuration()
        frontend_ok = self.validate_frontend()
        backend_ok = self.validate_backend()
        database_ok = self.validate_database()
        integration_ok = self.validate_integration()

        end_time = time.time()

        # Calculate overall status
        all_passed = all(
            [config_ok, frontend_ok, backend_ok, database_ok, integration_ok]
        )

        # Generate summary
        summary = {
            "overall_status": "PASSED" if all_passed else "FAILED",
            "validation_time": round(end_time - start_time, 2),
            "components": self.results,
            "total_issues": sum(
                len(result["issues"]) for result in self.results.values()
            ),
            "total_warnings": sum(
                len(result["warnings"]) for result in self.results.values()
            ),
            "recommendations": self._generate_recommendations(),
        }

        return summary

    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []

        # Configuration recommendations
        if self.results["configuration"]["issues"]:
            recommendations.append(
                "Fix configuration inconsistencies - consolidate duplicate files"
            )

        # Frontend recommendations
        if self.results["frontend"]["issues"]:
            recommendations.append(
                "Fix frontend build issues and API endpoint mismatches"
            )

        # Backend recommendations
        if self.results["backend"]["issues"]:
            recommendations.append(
                "Fix backend startup issues and missing dependencies"
            )

        # Database recommendations
        if self.results["database"]["issues"]:
            recommendations.append("Fix database configuration and schema issues")

        # Integration recommendations
        if self.results["integration"]["issues"]:
            recommendations.append("Fix frontend ↔ backend integration issues")

        # General recommendations
        if self.results["configuration"]["warnings"]:
            recommendations.append(
                "Consider consolidating duplicate configuration files"
            )

        if not recommendations:
            recommendations.append(
                "System validation passed - ready for production deployment"
            )

        return recommendations

    def print_results(self, summary: Dict[str, Any]):
        """Print validation results"""
        print("\n" + "=" * 80)
        print("🎯 NEXUS PLATFORM - SYSTEM VALIDATION RESULTS")
        print("=" * 80)

        print(f"\n📊 Overall Status: {summary['overall_status']}")
        print(f"⏱️  Validation Time: {summary['validation_time']}s")
        print(f"❌ Total Issues: {summary['total_issues']}")
        print(f"⚠️  Total Warnings: {summary['total_warnings']}")

        print("\n📋 Component Status:")
        for component, result in summary["components"].items():
            status_icon = "✅" if result["status"] == "passed" else "❌"
            print(f"  {status_icon} {component.title()}: {result['status'].upper()}")

            if result["issues"]:
                print("    Issues:")
                for issue in result["issues"]:
                    print(f"      • {issue}")

            if result["warnings"]:
                print("    Warnings:")
                for warning in result["warnings"]:
                    print(f"      • {warning}")

        print("\n💡 Recommendations:")
        for i, rec in enumerate(summary["recommendations"], 1):
            print(f"  {i}. {rec}")

        print("\n" + "=" * 80)


def main():
    """Main validation function"""
    validator = SystemValidator()

    try:
        summary = validator.run_full_validation()
        validator.print_results(summary)

        # Save results to file
        results_file = Path("/Users/Arief/Desktop/Nexus/validation_results.json")
        with open(results_file, "w") as f:
            json.dump(summary, f, indent=2)

        print(f"\n📄 Detailed results saved to: {results_file}")

        # Exit with appropriate code
        sys.exit(0 if summary["overall_status"] == "PASSED" else 1)

    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Validation failed with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
