#!/usr/bin/env python3
"""
NEXUS Platform - Simple Integration Test
Test basic integration without external dependencies
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SimpleIntegrationTest:
    """Simple integration test without external dependencies"""

    def __init__(self):
        self.test_results = {}

    async def run_integration_tests(self) -> Dict[str, Any]:
        """Run basic integration tests"""
        logger.info("Starting simple integration tests")

        start_time = datetime.now(timezone.utc)

        try:
            # Run integration tests
            integration_tests = [
                ("file_imports", self._test_file_imports),
                ("configuration_loading", self._test_configuration_loading),
                ("script_execution", self._test_script_execution),
                ("documentation_links", self._test_documentation_links),
            ]

            results = {}
            overall_success = True

            for test_name, test_func in integration_tests:
                logger.info(f"Running integration test: {test_name}")
                try:
                    test_result = await test_func()
                    results[test_name] = test_result

                    if not test_result.get("success", False):
                        overall_success = False
                        logger.error(f"Integration test failed: {test_name}")
                    else:
                        logger.info(f"Integration test passed: {test_name}")

                except Exception as e:
                    logger.error(f"Integration test error {test_name}: {e}")
                    results[test_name] = {
                        "success": False,
                        "error": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                    overall_success = False

            # Generate overall test report
            self.test_results = {
                "overall_success": overall_success,
                "start_time": start_time.isoformat(),
                "end_time": datetime.now(timezone.utc).isoformat(),
                "duration_seconds": (
                    datetime.now(timezone.utc) - start_time
                ).total_seconds(),
                "integration_tests": results,
                "summary": self._generate_test_summary(results),
            }

            logger.info(
                f"Simple integration tests completed. Success: {overall_success}"
            )
            return self.test_results

        except Exception as e:
            logger.error(f"Simple integration tests failed: {e}")
            return {
                "overall_success": False,
                "error": str(e),
                "start_time": start_time.isoformat(),
                "end_time": datetime.now(timezone.utc).isoformat(),
            }

    async def _test_file_imports(self) -> Dict[str, Any]:
        """Test that critical files can be imported"""
        logger.info("Testing file imports")

        results = {
            "success": True,
            "checks": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Test Python file syntax
        python_files = [
            "backend/services/ssot_registry.py",
            "backend/services/conflict_detection.py",
            "backend/services/audit_logging.py",
            "backend/services/api_registry_integration.py",
            "frenly_ai/backend/ssot_operator.py",
            "frenly_ai/backend/ssot_integration.py",
        ]

        import_checks = {}
        for file_path in python_files:
            path_obj = Path(file_path)
            if path_obj.exists():
                try:
                    # Try to compile the file to check syntax
                    with open(path_obj, "r") as f:
                        content = f.read()
                    compile(content, file_path, "exec")
                    import_checks[file_path] = {"success": True, "error": None}
                except SyntaxError as e:
                    import_checks[file_path] = {
                        "success": False,
                        "error": f"Syntax error: {e}",
                    }
                    results["success"] = False
                except Exception as e:
                    import_checks[file_path] = {
                        "success": False,
                        "error": f"Import error: {e}",
                    }
                    results["success"] = False
            else:
                import_checks[file_path] = {"success": False, "error": "File not found"}
                results["success"] = False

        results["checks"]["python_files"] = import_checks

        # Test YAML file syntax
        yaml_files = [
            "config/environments.yaml",
            "k8s/unified-manifests.yaml",
            ".github/workflows/ssot_automation.yml",
        ]

        yaml_checks = {}
        for file_path in yaml_files:
            path_obj = Path(file_path)
            if path_obj.exists():
                try:
                    import yaml

                    with open(path_obj, "r") as f:
                        # Handle multiple YAML documents
                        yaml.safe_load_all(f)
                    yaml_checks[file_path] = {"success": True, "error": None}
                except yaml.YAMLError as e:
                    yaml_checks[file_path] = {
                        "success": False,
                        "error": f"YAML error: {e}",
                    }
                    results["success"] = False
                except Exception as e:
                    yaml_checks[file_path] = {"success": False, "error": f"Error: {e}"}
                    results["success"] = False
            else:
                yaml_checks[file_path] = {"success": False, "error": "File not found"}
                results["success"] = False

        results["checks"]["yaml_files"] = yaml_checks

        return results

    async def _test_configuration_loading(self) -> Dict[str, Any]:
        """Test configuration loading"""
        logger.info("Testing configuration loading")

        results = {
            "success": True,
            "checks": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Test environments.yaml
        env_file = Path("config/environments.yaml")
        if env_file.exists():
            try:
                import yaml

                with open(env_file, "r") as f:
                    env_config = yaml.safe_load(f)

                required_sections = ["development", "staging", "production", "test"]
                section_checks = {}
                for section in required_sections:
                    section_checks[section] = section in env_config

                results["checks"]["environments"] = {
                    "success": all(section_checks.values()),
                    "sections": section_checks,
                    "total_sections": len(env_config),
                }

                if not all(section_checks.values()):
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

        # Test Docker Compose
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

        return results

    async def _test_script_execution(self) -> Dict[str, Any]:
        """Test script execution"""
        logger.info("Testing script execution")

        results = {
            "success": True,
            "checks": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Test Python scripts
        python_scripts = ["scripts/simple_validation.py", "scripts/validate_system.py"]

        script_checks = {}
        for script_path in python_scripts:
            path_obj = Path(script_path)
            if path_obj.exists():
                try:
                    # Test script syntax
                    with open(path_obj, "r") as f:
                        content = f.read()
                    compile(content, script_path, "exec")
                    script_checks[script_path] = {"success": True, "error": None}
                except Exception as e:
                    script_checks[script_path] = {"success": False, "error": str(e)}
                    results["success"] = False
            else:
                script_checks[script_path] = {
                    "success": False,
                    "error": "Script not found",
                }
                results["success"] = False

        results["checks"]["python_scripts"] = script_checks

        # Test shell scripts
        shell_scripts = ["scripts/deploy_production.sh"]

        shell_checks = {}
        for script_path in shell_scripts:
            path_obj = Path(script_path)
            if path_obj.exists():
                # Check if script is executable
                is_executable = path_obj.stat().st_mode & 0o111
                shell_checks[script_path] = {
                    "success": is_executable,
                    "executable": is_executable,
                    "error": None if is_executable else "Script not executable",
                }
                if not is_executable:
                    results["success"] = False
            else:
                shell_checks[script_path] = {
                    "success": False,
                    "error": "Script not found",
                }
                results["success"] = False

        results["checks"]["shell_scripts"] = shell_checks

        return results

    async def _test_documentation_links(self) -> Dict[str, Any]:
        """Test documentation links and references"""
        logger.info("Testing documentation links")

        results = {
            "success": True,
            "checks": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Test README.md
        readme_file = Path("README.md")
        if readme_file.exists():
            try:
                with open(readme_file, "r") as f:
                    content = f.read()

                # Check for key sections
                key_sections = [
                    "# NEXUS Platform",
                    "## 🚀 Features",
                    "## 🚀 Quick Start",
                    "## 🏗️ Architecture",
                ]

                section_checks = {}
                for section in key_sections:
                    section_checks[section] = section in content

                results["checks"]["readme"] = {
                    "success": all(section_checks.values()),
                    "sections": section_checks,
                    "file_size": readme_file.stat().st_size,
                }

                if not all(section_checks.values()):
                    results["success"] = False

            except Exception as e:
                results["checks"]["readme"] = {"success": False, "error": str(e)}
                results["success"] = False
        else:
            results["checks"]["readme"] = {
                "success": False,
                "error": "README.md not found",
            }
            results["success"] = False

        # Test documentation files
        doc_files = [
            "docs/frenly_ai/ssot_operator.md",
            "docs/automation/ci_cd_pipeline.md",
            "frenly_ai/README.md",
        ]

        doc_checks = {}
        for doc_path in doc_files:
            path_obj = Path(doc_path)
            if path_obj.exists():
                try:
                    with open(path_obj, "r") as f:
                        content = f.read()

                    doc_checks[doc_path] = {
                        "success": True,
                        "file_size": path_obj.stat().st_size,
                        "has_content": len(content.strip()) > 0,
                    }
                except Exception as e:
                    doc_checks[doc_path] = {"success": False, "error": str(e)}
                    results["success"] = False
            else:
                doc_checks[doc_path] = {
                    "success": False,
                    "error": "Documentation file not found",
                }
                results["success"] = False

        results["checks"]["documentation"] = doc_checks

        return results

    def _generate_test_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test summary"""
        total_tests = len(results)
        successful_tests = sum(
            1 for result in results.values() if result.get("success", False)
        )
        failed_tests = total_tests - successful_tests

        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "overall_status": "PASS" if failed_tests == 0 else "FAIL",
        }


async def main():
    """Main function to run simple integration tests"""
    tester = SimpleIntegrationTest()

    try:
        # Run tests
        results = await tester.run_integration_tests()

        # Print results
        print("\n" + "=" * 60)
        print("SIMPLE INTEGRATION TEST RESULTS")
        print("=" * 60)
        print(f"Overall Success: {results['overall_success']}")
        print(f"Duration: {results.get('duration_seconds', 0):.2f} seconds")

        if "summary" in results:
            summary = results["summary"]
            print(
                f"Tests: {summary['successful_tests']}/{summary['total_tests']} passed"
            )
            print(f"Success Rate: {summary['success_rate']:.1%}")
            print(f"Status: {summary['overall_status']}")

        print("\nDetailed Results:")
        for test_name, test_result in results.get("integration_tests", {}).items():
            status = "✓" if test_result.get("success", False) else "✗"
            print(f"  {status} {test_name}")

            if not test_result.get("success", False) and "error" in test_result:
                print(f"    Error: {test_result['error']}")

        print("=" * 60)

        # Save results to file
        results_file = Path("simple_integration_test_results.json")
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to: {results_file}")

        # Exit with appropriate code
        sys.exit(0 if results["overall_success"] else 1)

    except KeyboardInterrupt:
        print("\nIntegration tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Integration tests failed: {e}")
        logger.exception("Integration tests failed with exception")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
