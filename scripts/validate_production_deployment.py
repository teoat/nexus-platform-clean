#!/usr/bin/env python3
"""
NEXUS Platform - Production Deployment Validation Script
Comprehensive validation of production deployment readiness
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

try:
    import docker
except ImportError:
    docker = None

try:
    import kubernetes
    from kubernetes import client, config
except ImportError:
    kubernetes = None
    client = None
    config = None

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from services.api_registry_integration import APIRegistryIntegration
from services.audit_logging import AuditLogQueryEngine
from services.conflict_detection import ConflictDetector
from services.ssot_registry import SSOTRegistry

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProductionValidator:
    """Comprehensive production deployment validator"""

    def __init__(self):
        self.ssot_registry = SSOTRegistry()
        self.api_integration = APIRegistryIntegration()
        self.conflict_detector = ConflictDetector(self.ssot_registry)
        self.audit_engine = AuditLogQueryEngine()
        self.validation_results = {}
        self.docker_client = None
        self.k8s_client = None

        # Initialize clients
        self._init_docker_client()
        self._init_k8s_client()

    def _init_docker_client(self):
        """Initialize Docker client"""
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Docker client: {e}")

    def _init_k8s_client(self):
        """Initialize Kubernetes client"""
        try:
            config.load_incluster_config()
            self.k8s_client = client.ApiClient()
            logger.info("Kubernetes client initialized")
        except Exception as e:
            try:
                config.load_kube_config()
                self.k8s_client = client.ApiClient()
                logger.info("Kubernetes client initialized (local config)")
            except Exception as e2:
                logger.warning(f"Failed to initialize Kubernetes client: {e2}")

    async def validate_production_readiness(self) -> Dict[str, Any]:
        """Run comprehensive production readiness validation"""
        logger.info("Starting production readiness validation")

        start_time = datetime.now(timezone.utc)

        try:
            # Run all validation checks
            validation_checks = [
                ("infrastructure", self._validate_infrastructure),
                ("ssot_system", self._validate_ssot_system),
                ("api_integration", self._validate_api_integration),
                ("conflict_detection", self._validate_conflict_detection),
                ("audit_logging", self._validate_audit_logging),
                ("security", self._validate_security),
                ("monitoring", self._validate_monitoring),
                ("performance", self._validate_performance),
                ("data_integrity", self._validate_data_integrity),
                ("deployment", self._validate_deployment),
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

            logger.info(f"Production validation completed. Success: {overall_success}")
            return self.validation_results

        except Exception as e:
            logger.error(f"Production validation failed: {e}")
            return {
                "overall_success": False,
                "error": str(e),
                "start_time": start_time.isoformat(),
                "end_time": datetime.now(timezone.utc).isoformat(),
            }

    async def _validate_infrastructure(self) -> Dict[str, Any]:
        """Validate infrastructure components"""
        logger.info("Validating infrastructure")

        results = {
            "success": True,
            "checks": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Check Docker
        if self.docker_client:
            try:
                docker_info = self.docker_client.info()
                results["checks"]["docker"] = {
                    "success": True,
                    "version": docker_info.get("ServerVersion", "unknown"),
                    "containers_running": len(self.docker_client.containers.list()),
                }
            except Exception as e:
                results["checks"]["docker"] = {"success": False, "error": str(e)}
                results["success"] = False
        else:
            results["checks"]["docker"] = {
                "success": False,
                "error": "Docker client not available",
            }
            results["success"] = False

        # Check Kubernetes
        if self.k8s_client:
            try:
                v1 = client.CoreV1Api(self.k8s_client)
                nodes = v1.list_node()
                results["checks"]["kubernetes"] = {
                    "success": True,
                    "nodes": len(nodes.items),
                    "node_statuses": [node.status.conditions for node in nodes.items],
                }
            except Exception as e:
                results["checks"]["kubernetes"] = {"success": False, "error": str(e)}
                results["success"] = False
        else:
            results["checks"]["kubernetes"] = {
                "success": False,
                "error": "Kubernetes client not available",
            }
            results["success"] = False

        # Check system resources
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            results["checks"]["system_resources"] = {
                "success": True,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_available_gb": disk.free / (1024**3),
            }

            # Check if resources are within acceptable limits
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
                results["success"] = False
                results["checks"]["system_resources"][
                    "warning"
                ] = "High resource usage detected"

        except ImportError:
            results["checks"]["system_resources"] = {
                "success": False,
                "error": "psutil not available",
            }
            results["success"] = False
        except Exception as e:
            results["checks"]["system_resources"] = {"success": False, "error": str(e)}
            results["success"] = False

        return results

    async def _validate_ssot_system(self) -> Dict[str, Any]:
        """Validate SSOT system functionality"""
        logger.info("Validating SSOT system")

        results = {
            "success": True,
            "checks": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            # Check SSOT registry
            anchors_count = len(self.ssot_registry.anchors)
            aliases_count = sum(
                len(aliases) for aliases in self.ssot_registry.aliases.values()
            )

            results["checks"]["ssot_registry"] = {
                "success": True,
                "anchors_count": anchors_count,
                "aliases_count": aliases_count,
                "contexts": list(self.ssot_registry.aliases.keys()),
            }

            # Test alias resolution
            test_alias = "test-alias"
            test_canonical = "test-canonical"

            try:
                # Create a test alias
                from services.ssot_registry import AliasType

                await self.ssot_registry.add_alias(
                    alias_name=test_alias,
                    canonical_name=test_canonical,
                    context="test",
                    alias_type=AliasType.TEMPORARY,
                    description="Test alias for validation",
                    created_by="production_validator",
                    expires_in_days=1,
                )

                # Test resolution
                resolved = await self.ssot_registry.resolve_alias(test_alias, "test")

                results["checks"]["alias_resolution"] = {
                    "success": resolved == test_canonical,
                    "resolved_value": resolved,
                }

                # Clean up test alias
                if (
                    "test" in self.ssot_registry.aliases
                    and test_alias in self.ssot_registry.aliases["test"]
                ):
                    del self.ssot_registry.aliases["test"][test_alias]

            except Exception as e:
                results["checks"]["alias_resolution"] = {
                    "success": False,
                    "error": str(e),
                }
                results["success"] = False

            # Check conflict detection
            try:
                conflicts = await self.conflict_detector.detect_all_conflicts()
                conflict_stats = self.conflict_detector.get_conflict_statistics()

                results["checks"]["conflict_detection"] = {
                    "success": True,
                    "conflicts_detected": len(conflicts),
                    "conflict_statistics": conflict_stats,
                }

                if len(conflicts) > 0:
                    results["checks"]["conflict_detection"][
                        "warning"
                    ] = f"{len(conflicts)} conflicts detected"

            except Exception as e:
                results["checks"]["conflict_detection"] = {
                    "success": False,
                    "error": str(e),
                }
                results["success"] = False

        except Exception as e:
            results["success"] = False
            results["error"] = str(e)

        return results

    async def _validate_api_integration(self) -> Dict[str, Any]:
        """Validate API integration"""
        logger.info("Validating API integration")

        results = {
            "success": True,
            "checks": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            # Get integration status
            integration_status = await self.api_integration.get_integration_status()

            results["checks"]["integration_status"] = {
                "success": True,
                "total_anchors": integration_status.get("total_anchors", 0),
                "total_aliases": integration_status.get("total_aliases", 0),
                "active_anchors": integration_status.get("active_anchors", 0),
                "active_aliases": integration_status.get("active_aliases", 0),
            }

            # Validate integration
            validation_results = await self.api_integration.validate_integration()

            results["checks"]["integration_validation"] = {
                "success": validation_results.get("success", False),
                "validated_services": validation_results.get("validated_services", []),
                "validation_errors": validation_results.get("validation_errors", []),
            }

            if not validation_results.get("success", False):
                results["success"] = False

        except Exception as e:
            results["success"] = False
            results["error"] = str(e)

        return results

    async def _validate_conflict_detection(self) -> Dict[str, Any]:
        """Validate conflict detection system"""
        logger.info("Validating conflict detection system")

        results = {
            "success": True,
            "checks": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            # Test conflict detection
            conflicts = await self.conflict_detector.detect_all_conflicts()
            conflict_stats = self.conflict_detector.get_conflict_statistics()

            results["checks"]["conflict_detection"] = {
                "success": True,
                "conflicts_detected": len(conflicts),
                "total_conflicts": conflict_stats.get("total_conflicts", 0),
                "resolved_conflicts": conflict_stats.get("resolved_conflicts", 0),
                "unresolved_conflicts": conflict_stats.get("unresolved_conflicts", 0),
                "resolution_rate": conflict_stats.get("resolution_rate", 0),
            }

            # Test auto-resolution
            try:
                auto_resolutions = await self.conflict_detector.auto_resolve_conflicts()
                results["checks"]["auto_resolution"] = {
                    "success": True,
                    "auto_resolved": len(auto_resolutions),
                }
            except Exception as e:
                results["checks"]["auto_resolution"] = {
                    "success": False,
                    "error": str(e),
                }
                results["success"] = False

        except Exception as e:
            results["success"] = False
            results["error"] = str(e)

        return results

    async def _validate_audit_logging(self) -> Dict[str, Any]:
        """Validate audit logging system"""
        logger.info("Validating audit logging system")

        results = {
            "success": True,
            "checks": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            # Test audit logging
            test_log_id = await self.audit_engine.log_operation(
                operation="test_validation",
                entity_type="ProductionValidator",
                entity_id="test_entity",
                details={"test": "validation"},
                performed_by="production_validator",
                context="validation",
            )

            results["checks"]["audit_logging"] = {
                "success": True,
                "test_log_id": test_log_id,
            }

            # Test audit query
            from services.audit_logging import AuditQuery, OperationType

            query = AuditQuery(operation_types=[OperationType.CREATE], limit=10)

            audit_logs = await self.audit_engine.query_audit_logs(query)

            results["checks"]["audit_query"] = {
                "success": True,
                "logs_found": len(audit_logs),
            }

            # Test audit statistics
            audit_stats = await self.audit_engine.get_audit_statistics()

            results["checks"]["audit_statistics"] = {
                "success": True,
                "total_operations": audit_stats.get("total_operations", 0),
                "operation_distribution": audit_stats.get("operation_distribution", {}),
            }

        except Exception as e:
            results["success"] = False
            results["error"] = str(e)

        return results

    async def _validate_security(self) -> Dict[str, Any]:
        """Validate security configuration"""
        logger.info("Validating security configuration")

        results = {
            "success": True,
            "checks": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            # Check for sensitive data in SSOT
            sensitive_keys = ["password", "secret", "key", "token"]
            sensitive_found = []

            for anchor_id, anchor in self.ssot_registry.anchors.items():
                for key, value in anchor.aliasing.items():
                    if any(sensitive in key.lower() for sensitive in sensitive_keys):
                        sensitive_found.append(f"{anchor_id}.{key}")

            results["checks"]["sensitive_data"] = {
                "success": len(sensitive_found) == 0,
                "sensitive_fields_found": sensitive_found,
            }

            if sensitive_found:
                results["success"] = False
                results["checks"]["sensitive_data"][
                    "warning"
                ] = "Sensitive data found in SSOT"

            # Check audit log security
            try:
                from services.audit_logging import AuditQuery, OperationType

                query = AuditQuery(operation_types=[OperationType.DELETE], limit=100)

                delete_logs = await self.audit_engine.query_audit_logs(query)

                results["checks"]["audit_security"] = {
                    "success": True,
                    "delete_operations_logged": len(delete_logs),
                }

            except Exception as e:
                results["checks"]["audit_security"] = {
                    "success": False,
                    "error": str(e),
                }
                results["success"] = False

        except Exception as e:
            results["success"] = False
            results["error"] = str(e)

        return results

    async def _validate_monitoring(self) -> Dict[str, Any]:
        """Validate monitoring setup"""
        logger.info("Validating monitoring setup")

        results = {
            "success": True,
            "checks": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            # Check if monitoring endpoints are accessible
            monitoring_endpoints = [
                "http://localhost:8000/health",
                "http://localhost:8000/metrics",
                "http://localhost:3000/health",
            ]

            endpoint_results = {}
            for endpoint in monitoring_endpoints:
                try:
                    response = requests.get(endpoint, timeout=5)
                    endpoint_results[endpoint] = {
                        "success": response.status_code == 200,
                        "status_code": response.status_code,
                    }
                except Exception as e:
                    endpoint_results[endpoint] = {"success": False, "error": str(e)}

            results["checks"]["monitoring_endpoints"] = {
                "success": all(ep["success"] for ep in endpoint_results.values()),
                "endpoints": endpoint_results,
            }

            if not all(ep["success"] for ep in endpoint_results.values()):
                results["success"] = False

        except Exception as e:
            results["success"] = False
            results["error"] = str(e)

        return results

    async def _validate_performance(self) -> Dict[str, Any]:
        """Validate performance characteristics"""
        logger.info("Validating performance")

        results = {
            "success": True,
            "checks": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            # Test alias resolution performance
            start_time = time.time()

            # Create test aliases for performance testing
            test_aliases = []
            for i in range(100):
                alias_name = f"perf_test_{i}"
                try:
                    from services.ssot_registry import AliasType

                    await self.ssot_registry.add_alias(
                        alias_name=alias_name,
                        canonical_name="test-canonical",
                        context="performance_test",
                        alias_type=AliasType.TEMPORARY,
                        description="Performance test alias",
                        created_by="production_validator",
                        expires_in_days=1,
                    )
                    test_aliases.append(alias_name)
                except:
                    pass  # Alias might already exist

            # Test resolution performance
            resolution_times = []
            for alias_name in test_aliases[:10]:  # Test first 10
                try:
                    start = time.time()
                    await self.ssot_registry.resolve_alias(
                        alias_name, "performance_test"
                    )
                    resolution_times.append(time.time() - start)
                except:
                    pass

            # Clean up test aliases
            for alias_name in test_aliases:
                try:
                    if (
                        "performance_test" in self.ssot_registry.aliases
                        and alias_name in self.ssot_registry.aliases["performance_test"]
                    ):
                        del self.ssot_registry.aliases["performance_test"][alias_name]
                except:
                    pass

            avg_resolution_time = (
                sum(resolution_times) / len(resolution_times) if resolution_times else 0
            )

            results["checks"]["alias_resolution_performance"] = {
                "success": avg_resolution_time < 0.1,  # Should be under 100ms
                "average_resolution_time_ms": avg_resolution_time * 1000,
                "test_count": len(resolution_times),
            }

            if avg_resolution_time >= 0.1:
                results["success"] = False
                results["checks"]["alias_resolution_performance"][
                    "warning"
                ] = "Slow alias resolution detected"

        except Exception as e:
            results["success"] = False
            results["error"] = str(e)

        return results

    async def _validate_data_integrity(self) -> Dict[str, Any]:
        """Validate data integrity"""
        logger.info("Validating data integrity")

        results = {
            "success": True,
            "checks": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            # Check for orphaned aliases
            orphaned_aliases = []
            for context, aliases in self.ssot_registry.aliases.items():
                for alias_name, alias_def in aliases.items():
                    if alias_def.canonical not in self.ssot_registry.anchors:
                        orphaned_aliases.append(f"{context}.{alias_name}")

            results["checks"]["orphaned_aliases"] = {
                "success": len(orphaned_aliases) == 0,
                "orphaned_count": len(orphaned_aliases),
                "orphaned_aliases": orphaned_aliases,
            }

            if orphaned_aliases:
                results["success"] = False
                results["checks"]["orphaned_aliases"][
                    "warning"
                ] = "Orphaned aliases found"

            # Check for circular references
            circular_refs = []
            for anchor_id, anchor in self.ssot_registry.anchors.items():
                if "generates" in anchor.aliasing:
                    generates = anchor.aliasing["generates"]
                    if isinstance(generates, list) and anchor_id in generates:
                        circular_refs.append(anchor_id)

            results["checks"]["circular_references"] = {
                "success": len(circular_refs) == 0,
                "circular_refs": circular_refs,
            }

            if circular_refs:
                results["success"] = False
                results["checks"]["circular_references"][
                    "warning"
                ] = "Circular references found"

        except Exception as e:
            results["success"] = False
            results["error"] = str(e)

        return results

    async def _validate_deployment(self) -> Dict[str, Any]:
        """Validate deployment configuration"""
        logger.info("Validating deployment configuration")

        results = {
            "success": True,
            "checks": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            # Check if deployment files exist
            deployment_files = [
                "docker-compose.yml",
                "k8s/unified-manifests.yaml",
                "scripts/deploy_production.sh",
                "config/environments.yaml",
            ]

            file_checks = {}
            for file_path in deployment_files:
                file_exists = Path(file_path).exists()
                file_checks[file_path] = {
                    "exists": file_exists,
                    "size": Path(file_path).stat().st_size if file_exists else 0,
                }

            results["checks"]["deployment_files"] = {
                "success": all(check["exists"] for check in file_checks.values()),
                "files": file_checks,
            }

            if not all(check["exists"] for check in file_checks.values()):
                results["success"] = False

            # Check Docker Compose configuration
            if Path("docker-compose.yml").exists():
                try:
                    import yaml

                    with open("docker-compose.yml", "r") as f:
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

        except Exception as e:
            results["success"] = False
            results["error"] = str(e)

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
    """Main function to run production validation"""
    validator = ProductionValidator()

    try:
        # Run validation
        results = await validator.validate_production_readiness()

        # Print results
        print("\n" + "=" * 60)
        print("PRODUCTION DEPLOYMENT VALIDATION RESULTS")
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
        results_file = Path("production_validation_results.json")
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
