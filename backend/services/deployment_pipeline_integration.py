#!/usr/bin/env python3
"""
Deployment Pipeline Integration Service
Handles CI/CD integration, automated testing, and deployment orchestration
"""

import asyncio
import json
import logging
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import git

logger = logging.getLogger(__name__)


class DeploymentStage(Enum):
    PRE_DEPLOYMENT_CHECKS = "pre_deployment_checks"
    BUILD = "build"
    TEST = "test"
    INTEGRATION_TEST = "integration_test"
    DEPLOYMENT = "deployment"
    POST_DEPLOYMENT_CHECKS = "post_deployment_checks"
    ROLLBACK = "rollback"


class DeploymentStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLED_BACK = "rolled_back"


class TestType(Enum):
    UNIT_TESTS = "unit_tests"
    INTEGRATION_TESTS = "integration_tests"
    E2E_TESTS = "e2e_tests"
    PERFORMANCE_TESTS = "performance_tests"
    SECURITY_TESTS = "security_tests"
    LOAD_TESTS = "load_tests"


@dataclass
class PipelineStep:
    """Individual step in the deployment pipeline"""

    stage: DeploymentStage
    name: str
    command: str
    timeout_seconds: int
    required: bool
    depends_on: List[str]


@dataclass
class TestResult:
    """Result of a test execution"""

    test_type: TestType
    status: DeploymentStatus
    message: str
    details: Dict[str, Any]
    duration_seconds: float
    timestamp: datetime


@dataclass
class DeploymentResult:
    """Result of a deployment"""

    deployment_id: str
    version: str
    environment: str
    status: DeploymentStatus
    start_time: datetime
    end_time: Optional[datetime]
    stages_completed: List[DeploymentStage]
    test_results: List[TestResult]
    artifacts: Dict[str, str]
    rollback_available: bool
    summary: Dict[str, Any]


class DeploymentPipelineIntegrator:
    """Service for managing deployment pipelines and CI/CD integration"""

    def __init__(self):
        self.deployments: Dict[str, DeploymentResult] = {}
        self.pipeline_config = self._load_pipeline_config()
        self.environments = {
            "development": {"url": "http://localhost:8000", "requires_approval": False},
            "staging": {
                "url": "https://staging.nexus-platform.com",
                "requires_approval": True,
            },
            "production": {
                "url": "https://api.nexus-platform.com",
                "requires_approval": True,
            },
        }

    def _load_pipeline_config(self) -> Dict[str, Any]:
        """Load pipeline configuration"""
        return {
            "stages": [
                {
                    "stage": DeploymentStage.PRE_DEPLOYMENT_CHECKS,
                    "name": "Pre-deployment Checks",
                    "command": "python -m pytest tests/test_deployment_readiness.py -v",
                    "timeout_seconds": 300,
                    "required": True,
                    "depends_on": [],
                },
                {
                    "stage": DeploymentStage.BUILD,
                    "name": "Build Application",
                    "command": "docker build -t nexus-platform:{version} .",
                    "timeout_seconds": 600,
                    "required": True,
                    "depends_on": ["pre_deployment_checks"],
                },
                {
                    "stage": DeploymentStage.TEST,
                    "name": "Run Unit Tests",
                    "command": "python -m pytest tests/ -v --cov=backend --cov-report=xml",
                    "timeout_seconds": 300,
                    "required": True,
                    "depends_on": ["build"],
                },
                {
                    "stage": DeploymentStage.INTEGRATION_TEST,
                    "name": "Run Integration Tests",
                    "command": "python -m pytest e2e-tests/ -v",
                    "timeout_seconds": 600,
                    "required": True,
                    "depends_on": ["test"],
                },
                {
                    "stage": DeploymentStage.DEPLOYMENT,
                    "name": "Deploy to Environment",
                    "command": "kubectl apply -f k8s/{environment}/",
                    "timeout_seconds": 300,
                    "required": True,
                    "depends_on": ["integration_test"],
                },
                {
                    "stage": DeploymentStage.POST_DEPLOYMENT_CHECKS,
                    "name": "Post-deployment Health Checks",
                    "command": "python scripts/health_check.py --environment {environment}",
                    "timeout_seconds": 120,
                    "required": True,
                    "depends_on": ["deployment"],
                },
            ],
            "test_types": [
                TestType.UNIT_TESTS,
                TestType.INTEGRATION_TESTS,
                TestType.E2E_TESTS,
                TestType.PERFORMANCE_TESTS,
                TestType.SECURITY_TESTS,
            ],
        }

    async def start_deployment(
        self,
        version: str,
        environment: str,
        triggered_by: str,
        commit_hash: Optional[str] = None,
    ) -> DeploymentResult:
        """Start a new deployment pipeline"""
        if environment not in self.environments:
            raise ValueError(f"Unknown environment: {environment}")

        deployment_id = (
            f"deploy_{environment}_{version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        deployment = DeploymentResult(
            deployment_id=deployment_id,
            version=version,
            environment=environment,
            status=DeploymentStatus.RUNNING,
            start_time=datetime.now(),
            end_time=None,
            stages_completed=[],
            test_results=[],
            artifacts={},
            rollback_available=False,
            summary={},
        )

        self.deployments[deployment_id] = deployment

        logger.info(f"Starting deployment {deployment_id} to {environment}")

        # Run deployment pipeline asynchronously
        asyncio.create_task(self._run_deployment_pipeline(deployment))

        return deployment

    async def _run_deployment_pipeline(self, deployment: DeploymentResult):
        """Execute the deployment pipeline"""
        try:
            # Check if approval is required
            if self.environments[deployment.environment]["requires_approval"]:
                logger.info(f"Deployment {deployment.deployment_id} requires approval")
                # In a real system, this would wait for approval
                await asyncio.sleep(1)  # Mock approval delay

            # Execute pipeline stages
            for stage_config in self.pipeline_config["stages"]:
                stage = stage_config["stage"]

                success = await self._execute_pipeline_stage(deployment, stage_config)
                deployment.stages_completed.append(stage)

                if not success and stage_config["required"]:
                    logger.error(
                        f"Required stage {stage.value} failed for deployment {deployment.deployment_id}"
                    )
                    deployment.status = DeploymentStatus.FAILED
                    await self._handle_deployment_failure(deployment)
                    return

            # Run comprehensive tests
            test_success = await self._run_comprehensive_tests(deployment)
            if not test_success:
                logger.error(f"Tests failed for deployment {deployment.deployment_id}")
                deployment.status = DeploymentStatus.FAILED
                await self._handle_deployment_failure(deployment)
                return

            # Mark deployment as successful
            deployment.status = DeploymentStatus.SUCCESS
            deployment.end_time = datetime.now()
            deployment.rollback_available = True
            deployment.summary = self._generate_deployment_summary(deployment)

            logger.info(f"Deployment {deployment.deployment_id} completed successfully")

        except Exception as e:
            logger.error(f"Error during deployment {deployment.deployment_id}: {e}")
            deployment.status = DeploymentStatus.FAILED
            deployment.end_time = datetime.now()
            await self._handle_deployment_failure(deployment)

    async def _execute_pipeline_stage(
        self, deployment: DeploymentResult, stage_config: Dict[str, Any]
    ) -> bool:
        """Execute a single pipeline stage"""
        stage = stage_config["stage"]
        name = stage_config["name"]
        command = stage_config["command"]
        timeout = stage_config["timeout_seconds"]

        logger.info(
            f"Executing stage {stage.value} for deployment {deployment.deployment_id}"
        )

        # Format command with deployment variables
        formatted_command = command.format(
            version=deployment.version,
            environment=deployment.environment,
            deployment_id=deployment.deployment_id,
        )

        try:
            # Execute command
            process = await asyncio.create_subprocess_shell(
                formatted_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.getcwd(),
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )

            success = process.returncode == 0

            if success:
                logger.info(f"Stage {stage.value} completed successfully")
            else:
                logger.error(f"Stage {stage.value} failed: {stderr.decode()}")

            return success

        except asyncio.TimeoutError:
            logger.error(f"Stage {stage.value} timed out after {timeout} seconds")
            return False
        except Exception as e:
            logger.error(f"Error executing stage {stage.value}: {e}")
            return False

    async def _run_comprehensive_tests(self, deployment: DeploymentResult) -> bool:
        """Run comprehensive test suite"""
        logger.info(
            f"Running comprehensive tests for deployment {deployment.deployment_id}"
        )

        test_commands = {
            TestType.UNIT_TESTS: "python -m pytest tests/ -v --tb=short",
            TestType.INTEGRATION_TESTS: "python -m pytest e2e-tests/ -v --tb=short",
            TestType.E2E_TESTS: "cd e2e-tests && npm test",
            TestType.PERFORMANCE_TESTS: "python scripts/performance_test.py",
            TestType.SECURITY_TESTS: "python scripts/security_scan.py",
            TestType.LOAD_TESTS: "python scripts/load_test.py",
        }

        all_passed = True

        for test_type in self.pipeline_config["test_types"]:
            if test_type in test_commands:
                result = await self._run_test(
                    deployment, test_type, test_commands[test_type]
                )
                deployment.test_results.append(result)

                if result.status != DeploymentStatus.SUCCESS:
                    all_passed = False

        return all_passed

    async def _run_test(
        self, deployment: DeploymentResult, test_type: TestType, command: str
    ) -> TestResult:
        """Run a specific test type"""
        start_time = datetime.now()

        try:
            logger.info(
                f"Running {test_type.value} for deployment {deployment.deployment_id}"
            )

            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.getcwd(),
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=600  # 10 minutes timeout
            )

            duration = (datetime.now() - start_time).total_seconds()

            if process.returncode == 0:
                status = DeploymentStatus.SUCCESS
                message = f"{test_type.value} passed"
                details = {"stdout": stdout.decode()[:1000]}  # Truncate for storage
            else:
                status = DeploymentStatus.FAILED
                message = f"{test_type.value} failed"
                details = {
                    "stdout": stdout.decode()[:1000],
                    "stderr": stderr.decode()[:1000],
                }

            return TestResult(
                test_type=test_type,
                status=status,
                message=message,
                details=details,
                duration_seconds=duration,
                timestamp=datetime.now(),
            )

        except asyncio.TimeoutError:
            duration = (datetime.now() - start_time).total_seconds()
            return TestResult(
                test_type=test_type,
                status=DeploymentStatus.FAILED,
                message=f"{test_type.value} timed out",
                details={"timeout": True},
                duration_seconds=duration,
                timestamp=datetime.now(),
            )
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return TestResult(
                test_type=test_type,
                status=DeploymentStatus.FAILED,
                message=f"{test_type.value} error: {str(e)}",
                details={"error": str(e)},
                duration_seconds=duration,
                timestamp=datetime.now(),
            )

    async def _handle_deployment_failure(self, deployment: DeploymentResult):
        """Handle deployment failure and potential rollback"""
        logger.warning(f"Handling failure for deployment {deployment.deployment_id}")

        # Attempt automatic rollback if possible
        if (
            deployment.stages_completed
            and DeploymentStage.DEPLOYMENT in deployment.stages_completed
        ):
            logger.info(
                f"Attempting rollback for deployment {deployment.deployment_id}"
            )
            rollback_success = await self._rollback_deployment(deployment)

            if rollback_success:
                deployment.status = DeploymentStatus.ROLLED_BACK
                logger.info(
                    f"Rollback successful for deployment {deployment.deployment_id}"
                )
            else:
                logger.error(
                    f"Rollback failed for deployment {deployment.deployment_id}"
                )

    async def _rollback_deployment(self, deployment: DeploymentResult) -> bool:
        """Rollback a failed deployment"""
        try:
            # Mock rollback command
            rollback_command = f"kubectl rollout undo deployment/nexus-backend -n {deployment.environment}"

            process = await asyncio.create_subprocess_shell(
                rollback_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)

            return process.returncode == 0

        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

    def _generate_deployment_summary(
        self, deployment: DeploymentResult
    ) -> Dict[str, Any]:
        """Generate deployment summary"""
        total_tests = len(deployment.test_results)
        passed_tests = sum(
            1 for t in deployment.test_results if t.status == DeploymentStatus.SUCCESS
        )
        failed_tests = total_tests - passed_tests

        duration = (
            (deployment.end_time - deployment.start_time).total_seconds()
            if deployment.end_time
            else 0
        )

        return {
            "total_stages": len(deployment.stages_completed),
            "stages_completed": [s.value for s in deployment.stages_completed],
            "total_tests": total_tests,
            "tests_passed": passed_tests,
            "tests_failed": failed_tests,
            "test_success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "duration_seconds": duration,
            "artifacts_generated": len(deployment.artifacts),
            "rollback_available": deployment.rollback_available,
        }

    async def get_deployment_status(
        self, deployment_id: str
    ) -> Optional[DeploymentResult]:
        """Get deployment status"""
        return self.deployments.get(deployment_id)

    async def list_deployments(
        self,
        environment: Optional[str] = None,
        status: Optional[DeploymentStatus] = None,
        limit: int = 20,
    ) -> List[DeploymentResult]:
        """List deployments with optional filtering"""
        deployments = list(self.deployments.values())

        if environment:
            deployments = [d for d in deployments if d.environment == environment]

        if status:
            deployments = [d for d in deployments if d.status == status]

        return sorted(deployments, key=lambda d: d.start_time, reverse=True)[:limit]

    async def cancel_deployment(self, deployment_id: str) -> bool:
        """Cancel a running deployment"""
        deployment = self.deployments.get(deployment_id)
        if not deployment or deployment.status not in [
            DeploymentStatus.PENDING,
            DeploymentStatus.RUNNING,
        ]:
            return False

        deployment.status = DeploymentStatus.CANCELLED
        deployment.end_time = datetime.now()
        logger.info(f"Deployment {deployment_id} cancelled")
        return True

    async def trigger_rollback(self, deployment_id: str) -> bool:
        """Manually trigger rollback for a deployment"""
        deployment = self.deployments.get(deployment_id)
        if not deployment or not deployment.rollback_available:
            return False

        logger.info(f"Manual rollback triggered for deployment {deployment_id}")
        rollback_success = await self._rollback_deployment(deployment)

        if rollback_success:
            deployment.status = DeploymentStatus.ROLLED_BACK

        return rollback_success

    async def get_deployment_metrics(self) -> Dict[str, Any]:
        """Get deployment pipeline metrics"""
        deployments = list(self.deployments.values())

        if not deployments:
            return {"total_deployments": 0}

        successful = sum(1 for d in deployments if d.status == DeploymentStatus.SUCCESS)
        failed = sum(1 for d in deployments if d.status == DeploymentStatus.FAILED)

        durations = [
            d.summary.get("duration_seconds", 0) for d in deployments if d.end_time
        ]
        avg_duration = statistics.mean(durations) if durations else 0

        return {
            "total_deployments": len(deployments),
            "successful_deployments": successful,
            "failed_deployments": failed,
            "success_rate": successful / len(deployments) if deployments else 0,
            "average_duration_seconds": avg_duration,
            "deployments_by_environment": self._count_by_environment(deployments),
            "recent_deployments": len(
                [
                    d
                    for d in deployments
                    if d.start_time > datetime.now() - timedelta(days=7)
                ]
            ),
        }

    def _count_by_environment(
        self, deployments: List[DeploymentResult]
    ) -> Dict[str, int]:
        """Count deployments by environment"""
        counts = {}
        for deployment in deployments:
            counts[deployment.environment] = counts.get(deployment.environment, 0) + 1
        return counts

    async def validate_deployment_readiness(
        self, version: str, environment: str
    ) -> Dict[str, Any]:
        """Validate if deployment is ready"""
        checks = []

        # Check version format
        version_valid = len(version.split(".")) >= 3
        checks.append(
            {
                "check": "version_format",
                "passed": version_valid,
                "message": "Version format is valid"
                if version_valid
                else "Invalid version format",
            }
        )

        # Check environment exists
        env_exists = environment in self.environments
        checks.append(
            {
                "check": "environment_exists",
                "passed": env_exists,
                "message": "Environment exists"
                if env_exists
                else "Environment not found",
            }
        )

        # Check git status
        try:
            repo = git.Repo(".")
            is_clean = not repo.is_dirty()
            checks.append(
                {
                    "check": "git_status",
                    "passed": is_clean,
                    "message": "Working directory is clean"
                    if is_clean
                    else "Working directory has uncommitted changes",
                }
            )
        except:
            checks.append(
                {
                    "check": "git_status",
                    "passed": False,
                    "message": "Could not check git status",
                }
            )

        all_passed = all(check["passed"] for check in checks)

        return {
            "ready": all_passed,
            "checks": checks,
            "summary": f"{'Ready' if all_passed else 'Not ready'} for deployment to {environment}",
        }


# Global instance
deployment_pipeline_integrator = DeploymentPipelineIntegrator()
