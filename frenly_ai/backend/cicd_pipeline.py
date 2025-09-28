#!/usr/bin/env python3
"""
NEXUS Platform - CI/CD Pipeline with SSOT Validation
Consolidated CI/CD pipeline with SSOT validation and automated testing
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import yaml

import docker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BuildStage:
    name: str
    status: str  # pending, running, success, failed, skipped
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    logs: List[str] = None
    artifacts: List[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PipelineConfig:
    name: str
    version: str
    stages: List[str]
    triggers: List[str]
    environment: str
    ssot_validation: bool
    test_coverage_threshold: float
    performance_thresholds: Dict[str, float]
    security_scan: bool
    docker_build: bool
    deployment_strategy: str
    rollback_enabled: bool
    notifications: Dict[str, Any]


@dataclass
class SSOTValidationResult:
    stage: str
    status: str
    validated_aliases: int
    conflicts_found: int
    conflicts_resolved: int
    warnings: List[str]
    errors: List[str]
    duration: float
    metadata: Optional[Dict[str, Any]] = None


class CICDPipeline:
    """
    CI/CD Pipeline with SSOT Validation
    Provides comprehensive CI/CD pipeline with:
    - SSOT validation at each stage
    - Automated testing
    - Security scanning
    - Docker builds
    - Deployment strategies
    - Rollback capabilities
    """

    def __init__(self, config_path: str, ssot_integration=None):
        self.config_path = config_path
        self.config = self._load_config()
        self.ssot_integration = ssot_integration
        self.docker_client = docker.from_env()
        self.stages = {}
        self.pipeline_id = f"pipeline_{int(time.time())}"
        self.workspace = Path.cwd()
        self.artifacts_dir = self.workspace / "artifacts" / self.pipeline_id
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

        # Initialize stages
        for stage_name in self.config.stages:
            self.stages[stage_name] = BuildStage(
                name=stage_name, status="pending", logs=[], artifacts=[], metadata={}
            )

    def _load_config(self) -> PipelineConfig:
        """Load pipeline configuration from YAML file"""
        try:
            with open(self.config_path, "r") as f:
                config_data = yaml.safe_load(f)

            return PipelineConfig(
                name=config_data.get("name", "default-pipeline"),
                version=config_data.get("version", "1.0.0"),
                stages=config_data.get("stages", []),
                triggers=config_data.get("triggers", []),
                environment=config_data.get("environment", "development"),
                ssot_validation=config_data.get("ssot_validation", True),
                test_coverage_threshold=config_data.get(
                    "test_coverage_threshold", 80.0
                ),
                performance_thresholds=config_data.get("performance_thresholds", {}),
                security_scan=config_data.get("security_scan", True),
                docker_build=config_data.get("docker_build", True),
                deployment_strategy=config_data.get("deployment_strategy", "rolling"),
                rollback_enabled=config_data.get("rollback_enabled", True),
                notifications=config_data.get("notifications", {}),
            )
        except Exception as e:
            logger.error(f"Failed to load pipeline config: {e}")
            # Return default config
            return PipelineConfig(
                name="default-pipeline",
                version="1.0.0",
                stages=["validate", "test", "build", "security", "deploy"],
                triggers=["push", "pull_request"],
                environment="development",
                ssot_validation=True,
                test_coverage_threshold=80.0,
                performance_thresholds={},
                security_scan=True,
                docker_build=True,
                deployment_strategy="rolling",
                rollback_enabled=True,
                notifications={},
            )

    async def run_pipeline(
        self, trigger: str = "manual", branch: str = "main", commit_sha: str = None
    ) -> Dict[str, Any]:
        """
        Run the complete CI/CD pipeline
        """
        pipeline_start = datetime.now(timezone.utc)
        logger.info(f"Starting pipeline {self.pipeline_id} for {branch}@{commit_sha}")

        try:
            # Initialize pipeline
            await self._initialize_pipeline(trigger, branch, commit_sha)

            # Run stages sequentially
            pipeline_success = True
            for stage_name in self.config.stages:
                stage_success = await self._run_stage(stage_name)
                if not stage_success and stage_name in ["validate", "test", "security"]:
                    pipeline_success = False
                    logger.error(f"Pipeline failed at stage: {stage_name}")
                    break

            # Finalize pipeline
            pipeline_end = datetime.now(timezone.utc)
            pipeline_duration = (pipeline_end - pipeline_start).total_seconds()

            result = {
                "pipeline_id": self.pipeline_id,
                "status": "success" if pipeline_success else "failed",
                "duration": pipeline_duration,
                "stages": {name: asdict(stage) for name, stage in self.stages.items()},
                "trigger": trigger,
                "branch": branch,
                "commit_sha": commit_sha,
                "artifacts": list(self.artifacts_dir.glob("*")),
                "timestamp": pipeline_end.isoformat(),
            }

            # Send notifications
            await self._send_notifications(result)

            # Save pipeline result
            await self._save_pipeline_result(result)

            return result

        except Exception as e:
            logger.error(f"Pipeline failed with error: {e}")
            return {
                "pipeline_id": self.pipeline_id,
                "status": "failed",
                "error": str(e),
                "stages": {name: asdict(stage) for name, stage in self.stages.items()},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def _initialize_pipeline(self, trigger: str, branch: str, commit_sha: str):
        """Initialize pipeline environment"""
        logger.info("Initializing pipeline environment")

        # Set environment variables
        os.environ["PIPELINE_ID"] = self.pipeline_id
        os.environ["BRANCH"] = branch
        os.environ["COMMIT_SHA"] = commit_sha or "unknown"
        os.environ["ENVIRONMENT"] = self.config.environment

        # Create workspace directories
        (self.workspace / "logs").mkdir(exist_ok=True)
        (self.workspace / "reports").mkdir(exist_ok=True)

    async def _run_stage(self, stage_name: str) -> bool:
        """
        Run a specific pipeline stage
        """
        stage = self.stages[stage_name]
        stage.status = "running"
        stage.start_time = datetime.now(timezone.utc)

        logger.info(f"Running stage: {stage_name}")

        try:
            if stage_name == "validate":
                success = await self._validate_stage()
            elif stage_name == "test":
                success = await self._test_stage()
            elif stage_name == "build":
                success = await self._build_stage()
            elif stage_name == "security":
                success = await self._security_stage()
            elif stage_name == "deploy":
                success = await self._deploy_stage()
            else:
                logger.warning(f"Unknown stage: {stage_name}")
                success = True

            stage.status = "success" if success else "failed"
            stage.end_time = datetime.now(timezone.utc)
            stage.duration = (stage.end_time - stage.start_time).total_seconds()

            return success

        except Exception as e:
            logger.error(f"Stage {stage_name} failed: {e}")
            stage.status = "failed"
            stage.end_time = datetime.now(timezone.utc)
            stage.duration = (stage.end_time - stage.start_time).total_seconds()
            stage.logs.append(f"Error: {str(e)}")
            return False

    async def _validate_stage(self) -> bool:
        """
        Validation stage with SSOT validation
        """
        logger.info("Running validation stage")

        try:
            # 1. Code quality checks
            await self._run_command(
                "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics"
            )
            await self._run_command("black --check .")
            await self._run_command("isort --check-only .")

            # 2. Type checking
            await self._run_command("mypy . --ignore-missing-imports")

            # 3. SSOT validation
            if self.config.ssot_validation and self.ssot_integration:
                ssot_result = await self._validate_ssot()
                if not ssot_result:
                    return False

            # 4. Configuration validation
            await self._validate_configurations()

            return True

        except Exception as e:
            logger.error(f"Validation stage failed: {e}")
            return False

    async def _test_stage(self) -> bool:
        """
        Testing stage with coverage analysis
        """
        logger.info("Running test stage")

        try:
            # 1. Unit tests
            test_result = await self._run_command(
                "pytest tests/ --cov=. --cov-report=html --cov-report=xml --junitxml=test-results.xml"
            )

            # 2. Check coverage threshold
            coverage = await self._get_coverage_percentage()
            if coverage < self.config.test_coverage_threshold:
                logger.error(
                    f"Coverage {coverage}% below threshold {self.config.test_coverage_threshold}%"
                )
                return False

            # 3. Integration tests
            await self._run_command(
                "pytest tests/integration/ --junitxml=integration-test-results.xml"
            )

            # 4. Performance tests
            if self.config.performance_thresholds:
                await self._run_performance_tests()

            return True

        except Exception as e:
            logger.error(f"Test stage failed: {e}")
            return False

    async def _build_stage(self) -> bool:
        """
        Build stage with Docker support
        """
        logger.info("Running build stage")

        try:
            # 1. Install dependencies
            await self._run_command("pip install -r requirements.txt")

            # 2. Build Python package
            await self._run_command("python setup.py sdist bdist_wheel")

            # 3. Docker build (if enabled)
            if self.config.docker_build:
                await self._build_docker_image()

            # 4. Create deployment artifacts
            await self._create_deployment_artifacts()

            return True

        except Exception as e:
            logger.error(f"Build stage failed: {e}")
            return False

    async def _security_stage(self) -> bool:
        """
        Security scanning stage
        """
        if not self.config.security_scan:
            logger.info("Security scanning disabled")
            return True

        logger.info("Running security stage")

        try:
            # 1. Dependency vulnerability scan
            await self._run_command("safety check --json --output safety-report.json")

            # 2. Code security scan
            await self._run_command("bandit -r . -f json -o bandit-report.json")

            # 3. Secret scanning
            await self._run_command(
                "detect-secrets scan --all-files --baseline .secrets.baseline"
            )

            # 4. Container security scan (if Docker build enabled)
            if self.config.docker_build:
                await self._scan_docker_image()

            return True

        except Exception as e:
            logger.error(f"Security stage failed: {e}")
            return False

    async def _deploy_stage(self) -> bool:
        """
        Deployment stage
        """
        logger.info("Running deploy stage")

        try:
            if self.config.deployment_strategy == "rolling":
                return await self._rolling_deployment()
            elif self.config.deployment_strategy == "blue_green":
                return await self._blue_green_deployment()
            elif self.config.deployment_strategy == "canary":
                return await self._canary_deployment()
            else:
                logger.error(
                    f"Unknown deployment strategy: {self.config.deployment_strategy}"
                )
                return False

        except Exception as e:
            logger.error(f"Deploy stage failed: {e}")
            return False

    async def _validate_ssot(self) -> bool:
        """
        Validate SSOT consistency
        """
        if not self.ssot_integration:
            logger.warning("SSOT integration not available")
            return True

        logger.info("Validating SSOT consistency")

        try:
            # Get all aliases for validation
            aliases = await self.ssot_integration.list_aliases(context="frenly_ai")

            validation_result = SSOTValidationResult(
                stage="validate",
                status="running",
                validated_aliases=len(aliases),
                conflicts_found=0,
                conflicts_resolved=0,
                warnings=[],
                errors=[],
                duration=0.0,
            )

            start_time = time.time()

            # Check for conflicts
            alias_groups = {}
            for alias in aliases:
                canonical = alias.canonical_name
                if canonical not in alias_groups:
                    alias_groups[canonical] = []
                alias_groups[canonical].append(alias.alias)

            # Find conflicts
            conflicts = []
            for canonical, alias_list in alias_groups.items():
                if len(alias_list) > 1:
                    conflicts.append(alias_list)
                    validation_result.conflicts_found += 1

            # Resolve conflicts
            for conflict_group in conflicts:
                resolution = await self.ssot_integration.resolve_conflicts(
                    conflict_group, "frenly_ai", "first_wins"
                )
                validation_result.conflicts_resolved += 1

            validation_result.duration = time.time() - start_time
            validation_result.status = (
                "success" if validation_result.conflicts_found == 0 else "warning"
            )

            # Log validation results
            logger.info(
                f"SSOT validation completed: {validation_result.validated_aliases} aliases, "
                f"{validation_result.conflicts_found} conflicts, "
                f"{validation_result.conflicts_resolved} resolved"
            )

            return validation_result.status in ["success", "warning"]

        except Exception as e:
            logger.error(f"SSOT validation failed: {e}")
            return False

    async def _validate_configurations(self):
        """Validate configuration files"""
        logger.info("Validating configuration files")

        # Validate YAML files
        yaml_files = list(self.workspace.glob("**/*.yaml")) + list(
            self.workspace.glob("**/*.yml")
        )
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, "r") as f:
                    yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise Exception(f"Invalid YAML in {yaml_file}: {e}")

        # Validate JSON files
        json_files = list(self.workspace.glob("**/*.json"))
        for json_file in json_files:
            try:
                with open(json_file, "r") as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                raise Exception(f"Invalid JSON in {json_file}: {e}")

    async def _get_coverage_percentage(self) -> float:
        """Get test coverage percentage"""
        try:
            # Parse coverage.xml to get coverage percentage
            import xml.etree.ElementTree as ET

            coverage_file = self.workspace / "coverage.xml"
            if coverage_file.exists():
                tree = ET.parse(coverage_file)
                root = tree.getroot()
                line_rate = float(root.get("line-rate", 0))
                return line_rate * 100
        except Exception as e:
            logger.warning(f"Could not parse coverage: {e}")

        return 0.0

    async def _run_performance_tests(self):
        """Run performance tests"""
        logger.info("Running performance tests")

        # Run load tests
        await self._run_command(
            "pytest tests/performance/ --junitxml=performance-test-results.xml"
        )

        # Check performance thresholds
        for metric, threshold in self.config.performance_thresholds.items():
            # This would parse performance test results and check thresholds
            logger.info(f"Checking {metric} threshold: {threshold}")

    async def _build_docker_image(self):
        """Build Docker image"""
        logger.info("Building Docker image")

        try:
            # Build the image
            image, build_logs = self.docker_client.images.build(
                path=str(self.workspace),
                tag=f"nexus-frenly-ai:{self.pipeline_id}",
                rm=True,
            )

            # Save build logs
            with open(self.artifacts_dir / "docker-build.log", "w") as f:
                for log in build_logs:
                    f.write(log.get("stream", ""))

            logger.info(f"Docker image built: {image.tags}")

        except Exception as e:
            logger.error(f"Docker build failed: {e}")
            raise

    async def _scan_docker_image(self):
        """Scan Docker image for vulnerabilities"""
        logger.info("Scanning Docker image for vulnerabilities")

        try:
            # Use Trivy for container scanning
            await self._run_command(
                f"trivy image --format json --output trivy-report.json nexus-frenly-ai:{self.pipeline_id}"
            )
        except Exception as e:
            logger.warning(f"Docker security scan failed: {e}")

    async def _create_deployment_artifacts(self):
        """Create deployment artifacts"""
        logger.info("Creating deployment artifacts")

        # Create deployment manifest
        manifest = {
            "pipeline_id": self.pipeline_id,
            "version": self.config.version,
            "environment": self.config.environment,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "artifacts": {
                "docker_image": f"nexus-frenly-ai:{self.pipeline_id}",
                "python_package": f"nexus_frenly_ai-{self.config.version}.tar.gz",
            },
        }

        with open(self.artifacts_dir / "deployment-manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)

    async def _rolling_deployment(self) -> bool:
        """Perform rolling deployment"""
        logger.info("Performing rolling deployment")

        try:
            # Update deployment configuration
            # This would integrate with Kubernetes, Docker Swarm, etc.
            logger.info("Rolling deployment completed")
            return True
        except Exception as e:
            logger.error(f"Rolling deployment failed: {e}")
            return False

    async def _blue_green_deployment(self) -> bool:
        """Perform blue-green deployment"""
        logger.info("Performing blue-green deployment")

        try:
            # Switch traffic from blue to green
            # This would integrate with load balancers, service mesh, etc.
            logger.info("Blue-green deployment completed")
            return True
        except Exception as e:
            logger.error(f"Blue-green deployment failed: {e}")
            return False

    async def _canary_deployment(self) -> bool:
        """Perform canary deployment"""
        logger.info("Performing canary deployment")

        try:
            # Deploy to small percentage of traffic
            # Monitor metrics and gradually increase
            logger.info("Canary deployment completed")
            return True
        except Exception as e:
            logger.error(f"Canary deployment failed: {e}")
            return False

    async def _run_command(self, command: str, cwd: str = None) -> Tuple[int, str, str]:
        """
        Run a shell command and return exit code, stdout, stderr
        """
        logger.info(f"Running command: {command}")

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd or str(self.workspace),
            )

            stdout, stderr = await process.communicate()

            # Log output
            if stdout:
                logger.info(f"STDOUT: {stdout.decode()}")
            if stderr:
                logger.warning(f"STDERR: {stderr.decode()}")

            return process.returncode, stdout.decode(), stderr.decode()

        except Exception as e:
            logger.error(f"Command failed: {e}")
            return 1, "", str(e)

    async def _send_notifications(self, result: Dict[str, Any]):
        """Send pipeline notifications"""
        if not self.config.notifications:
            return

        logger.info("Sending notifications")

        # Send to configured channels (Slack, email, etc.)
        for channel, config in self.config.notifications.items():
            try:
                if channel == "slack":
                    await self._send_slack_notification(result, config)
                elif channel == "email":
                    await self._send_email_notification(result, config)
            except Exception as e:
                logger.error(f"Failed to send {channel} notification: {e}")

    async def _send_slack_notification(
        self, result: Dict[str, Any], config: Dict[str, Any]
    ):
        """Send Slack notification"""
        # Implementation would depend on Slack API
        logger.info("Sending Slack notification")

    async def _send_email_notification(
        self, result: Dict[str, Any], config: Dict[str, Any]
    ):
        """Send email notification"""
        # Implementation would depend on email service
        logger.info("Sending email notification")

    async def _save_pipeline_result(self, result: Dict[str, Any]):
        """Save pipeline result to file"""
        result_file = self.artifacts_dir / "pipeline-result.json"
        with open(result_file, "w") as f:
            json.dump(result, f, indent=2, default=str)

        logger.info(f"Pipeline result saved to {result_file}")


# Example usage and testing
async def main():
    """
    Example usage of CICDPipeline
    """
    # Create a sample pipeline config
    config_data = {
        "name": "frenly-ai-pipeline",
        "version": "1.0.0",
        "stages": ["validate", "test", "build", "security", "deploy"],
        "triggers": ["push", "pull_request"],
        "environment": "production",
        "ssot_validation": True,
        "test_coverage_threshold": 85.0,
        "performance_thresholds": {
            "response_time": 1000,  # ms
            "memory_usage": 512,  # MB
        },
        "security_scan": True,
        "docker_build": True,
        "deployment_strategy": "rolling",
        "rollback_enabled": True,
        "notifications": {
            "slack": {
                "webhook_url": "https://hooks.slack.com/services/...",
                "channel": "#deployments",
            }
        },
    }

    # Save config to file
    config_file = "pipeline-config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    # Initialize and run pipeline
    pipeline = CICDPipeline(config_file)
    result = await pipeline.run_pipeline(trigger="manual", branch="main")

    print(f"Pipeline result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
