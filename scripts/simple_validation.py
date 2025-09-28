#!/usr/bin/env python3
"""
NEXUS Platform - Simple Production Validation Script
Basic validation without external dependencies
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SimpleValidator:
    """Simple production validator without external dependencies"""

    def __init__(self):
        self.validation_results = {}

    async def validate_production_readiness(self) -> Dict[str, Any]:
        """Run basic production readiness validation"""
        logger.info("Starting simple production readiness validation")

        start_time = datetime.now(timezone.utc)

        try:
            # Run basic validation checks
            validation_checks = [
                ("file_structure", self._validate_file_structure),
                ("configuration", self._validate_configuration),
                ("scripts", self._validate_scripts),
                ("documentation", self._validate_documentation),
            ]

            results = {}
            overall_success = True

            for check_name, check_func in validation_checks:
                logger.info(f"Running validation check: {check_name}")
                try:
                    check_result = await check_func()
                    results[check_name] = check_result

                    if not check_result.get("success", False):
                        overall_success = False
                        logger.error(f"Validation check failed: {check_name}")
                    else:
                        logger.info(f"Validation check passed: {check_name}")

                except Exception as e:
                    logger.error(f"Validation check error {check_name}: {e}")
                    results[check_name] = {
                        "success": False,
                        "error": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                    overall_success = False

            # Generate overall validation report
            self.validation_results = {
                "overall_success": overall_success,
                "start_time": start_time.isoformat(),
                "end_time": datetime.now(timezone.utc).isoformat(),
                "duration_seconds": (
                    datetime.now(timezone.utc) - start_time
                ).total_seconds(),
                "validation_checks": results,
                "summary": self._generate_validation_summary(results),
            }

            logger.info(f"Simple validation completed. Success: {overall_success}")
            return self.validation_results

        except Exception as e:
            logger.error(f"Simple validation failed: {e}")
            return {
                "overall_success": False,
                "error": str(e),
                "start_time": start_time.isoformat(),
                "end_time": datetime.now(timezone.utc).isoformat(),
            }

    async def _validate_file_structure(self) -> Dict[str, Any]:
        """Validate file structure"""
        logger.info("Validating file structure")

        results = {
            "success": True,
            "checks": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Check critical directories
        critical_dirs = [
            "backend",
            "frontend",
            "config",
            "scripts",
            "k8s",
            "monitoring",
            "security",
            "docs",
            "frenly_ai",
        ]

        dir_checks = {}
        for dir_name in critical_dirs:
            dir_path = Path(dir_name)
            dir_checks[dir_name] = {
                "exists": dir_path.exists(),
                "is_directory": dir_path.is_dir() if dir_path.exists() else False,
            }

        results["checks"]["directories"] = dir_checks

        # Check if all critical directories exist
        missing_dirs = [
            name for name, check in dir_checks.items() if not check["exists"]
        ]
        if missing_dirs:
            results["success"] = False
            results["checks"]["missing_directories"] = missing_dirs

        # Check critical files
        critical_files = [
            "backend/services/ssot_registry.py",
            "backend/services/conflict_detection.py",
            "backend/services/audit_logging.py",
            "backend/services/api_registry_integration.py",
            "config/environments.yaml",
            "scripts/deploy_production.sh",
            "scripts/validate_system.py",
            "scripts/integrate_backend_services.py",
            "k8s/unified-manifests.yaml",
            "frenly_ai/backend/ssot_operator.py",
            "frenly_ai/backend/ssot_integration.py",
            ".github/workflows/ssot_automation.yml",
        ]

        file_checks = {}
        for file_path in critical_files:
            path_obj = Path(file_path)
            file_checks[file_path] = {
                "exists": path_obj.exists(),
                "size": path_obj.stat().st_size if path_obj.exists() else 0,
                "is_file": path_obj.is_file() if path_obj.exists() else False,
            }

        results["checks"]["files"] = file_checks

        # Check if all critical files exist
        missing_files = [
            path for path, check in file_checks.items() if not check["exists"]
        ]
        if missing_files:
            results["success"] = False
            results["checks"]["missing_files"] = missing_files

        return results

    async def _validate_configuration(self) -> Dict[str, Any]:
        """Validate configuration files"""
        logger.info("Validating configuration")

        results = {
            "success": True,
            "checks": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Check environments.yaml
        env_file = Path("config/environments.yaml")
        if env_file.exists():
            try:
                import yaml

                with open(env_file, "r") as f:
                    env_config = yaml.safe_load(f)

                required_envs = ["development", "staging", "production", "test"]
                env_checks = {}
                for env in required_envs:
                    env_checks[env] = env in env_config

                results["checks"]["environments"] = {
                    "success": all(env_checks.values()),
                    "environments": env_checks,
                }

                if not all(env_checks.values()):
                    results["success"] = False

            except Exception as e:
                results["checks"]["environments"] = {"success": False, "error": str(e)}
                results["success"] = False
        else:
            results["checks"]["environments"] = {
                "success": False,
                "error": "environments.yaml not found",
            }
            results["success"] = False

        # Check Docker Compose
        compose_file = Path("docker-compose.yml")
        if compose_file.exists():
            try:
                import yaml

                with open(compose_file, "r") as f:
                    compose_config = yaml.safe_load(f)

                services = compose_config.get("services", {})
                results["checks"]["docker_compose"] = {
                    "success": len(services) > 0,
                    "services_count": len(services),
                    "services": list(services.keys()),
                }

            except Exception as e:
                results["checks"]["docker_compose"] = {
                    "success": False,
                    "error": str(e),
                }
                results["success"] = False
        else:
            results["checks"]["docker_compose"] = {
                "success": False,
                "error": "docker-compose.yml not found",
            }
            results["success"] = False

        # Check Kubernetes manifests
        k8s_file = Path("k8s/unified-manifests.yaml")
        if k8s_file.exists():
            try:
                import yaml

                with open(k8s_file, "r") as f:
                    k8s_config = yaml.safe_load_all(f)
                    manifests = list(k8s_config)

                results["checks"]["kubernetes"] = {
                    "success": len(manifests) > 0,
                    "manifests_count": len(manifests),
                }

            except Exception as e:
                results["checks"]["kubernetes"] = {"success": False, "error": str(e)}
                results["success"] = False
        else:
            results["checks"]["kubernetes"] = {
                "success": False,
                "error": "k8s/unified-manifests.yaml not found",
            }
            results["success"] = False

        return results

    async def _validate_scripts(self) -> Dict[str, Any]:
        """Validate scripts"""
        logger.info("Validating scripts")

        results = {
            "success": True,
            "checks": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Check script files
        script_files = [
            "scripts/deploy_production.sh",
            "scripts/validate_system.py",
            "scripts/integrate_backend_services.py",
            "scripts/validate_production_deployment.py",
        ]

        script_checks = {}
        for script_path in script_files:
            path_obj = Path(script_path)
            script_checks[script_path] = {
                "exists": path_obj.exists(),
                "executable": path_obj.stat().st_mode & 0o111
                if path_obj.exists()
                else False,
                "size": path_obj.stat().st_size if path_obj.exists() else 0,
            }

        results["checks"]["scripts"] = script_checks

        # Check if all scripts exist and are executable
        missing_scripts = [
            path for path, check in script_checks.items() if not check["exists"]
        ]
        non_executable = [
            path
            for path, check in script_checks.items()
            if check["exists"] and not check["executable"]
        ]

        if missing_scripts:
            results["success"] = False
            results["checks"]["missing_scripts"] = missing_scripts

        if non_executable:
            results["checks"]["non_executable_scripts"] = non_executable

        return results

    async def _validate_documentation(self) -> Dict[str, Any]:
        """Validate documentation"""
        logger.info("Validating documentation")

        results = {
            "success": True,
            "checks": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Check documentation files
        doc_files = [
            "README.md",
            "docs/frenly_ai/ssot_operator.md",
            "docs/automation/ci_cd_pipeline.md",
            "frenly_ai/README.md",
        ]

        doc_checks = {}
        for doc_path in doc_files:
            path_obj = Path(doc_path)
            doc_checks[doc_path] = {
                "exists": path_obj.exists(),
                "size": path_obj.stat().st_size if path_obj.exists() else 0,
            }

        results["checks"]["documentation"] = doc_checks

        # Check if all documentation exists
        missing_docs = [
            path for path, check in doc_checks.items() if not check["exists"]
        ]
        if missing_docs:
            results["success"] = False
            results["checks"]["missing_documentation"] = missing_docs

        return results

    def _generate_validation_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate validation summary"""
        total_checks = len(results)
        successful_checks = sum(
            1 for result in results.values() if result.get("success", False)
        )
        failed_checks = total_checks - successful_checks

        return {
            "total_checks": total_checks,
            "successful_checks": successful_checks,
            "failed_checks": failed_checks,
            "success_rate": successful_checks / total_checks if total_checks > 0 else 0,
            "overall_status": "PASS" if failed_checks == 0 else "FAIL",
        }


async def main():
    """Main function to run simple validation"""
    validator = SimpleValidator()

    try:
        # Run validation
        results = await validator.validate_production_readiness()

        # Print results
        print("\n" + "=" * 60)
        print("SIMPLE PRODUCTION VALIDATION RESULTS")
        print("=" * 60)
        print(f"Overall Success: {results['overall_success']}")
        print(f"Duration: {results.get('duration_seconds', 0):.2f} seconds")

        if "summary" in results:
            summary = results["summary"]
            print(
                f"Checks: {summary['successful_checks']}/{summary['total_checks']} passed"
            )
            print(f"Success Rate: {summary['success_rate']:.1%}")
            print(f"Status: {summary['overall_status']}")

        print("\nDetailed Results:")
        for check_name, check_result in results.get("validation_checks", {}).items():
            status = "✓" if check_result.get("success", False) else "✗"
            print(f"  {status} {check_name}")

            if not check_result.get("success", False) and "error" in check_result:
                print(f"    Error: {check_result['error']}")

        print("=" * 60)

        # Save results to file
        results_file = Path("simple_validation_results.json")
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to: {results_file}")

        # Exit with appropriate code
        sys.exit(0 if results["overall_success"] else 1)

    except KeyboardInterrupt:
        print("\nValidation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Validation failed: {e}")
        logger.exception("Validation failed with exception")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
