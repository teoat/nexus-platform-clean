#!/usr/bin/env python3
"""
NEXUS Platform - Deployment Automation Service
Blue-green deployment and rollback automation
"""

import asyncio
import json
import logging
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class DeploymentStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class DeploymentType(Enum):
    BLUE_GREEN = "blue_green"
    ROLLING = "rolling"
    CANARY = "canary"


@dataclass
class Deployment:
    id: str
    type: DeploymentType
    version: str
    status: DeploymentStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    rollback_at: Optional[datetime] = None
    health_checks: List[Dict[str, Any]] = None
    error_message: Optional[str] = None


class DeploymentAutomationService:
    """Blue-green deployment and rollback automation service"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.deployments = []
        self.current_environment = "blue"  # blue or green
        self.health_check_endpoints = self.config.get(
            "health_check_endpoints",
            ["http://localhost:8000/health", "http://localhost:3000/health"],
        )
        self.rollback_timeout = self.config.get("rollback_timeout", 300)  # 5 minutes

    async def deploy_blue_green(self, version: str, image_tag: str) -> Deployment:
        """Deploy using blue-green strategy"""
        logger.info(f"Starting blue-green deployment for version {version}")

        deployment = Deployment(
            id=f"deploy_{int(time.time())}",
            type=DeploymentType.BLUE_GREEN,
            version=version,
            status=DeploymentStatus.IN_PROGRESS,
            created_at=datetime.now(timezone.utc),
            started_at=datetime.now(timezone.utc),
            health_checks=[],
        )

        self.deployments.append(deployment)

        try:
            # Step 1: Deploy to inactive environment
            target_env = "green" if self.current_environment == "blue" else "blue"
            await self._deploy_to_environment(target_env, image_tag)

            # Step 2: Run health checks
            health_check_results = await self._run_health_checks(target_env)
            deployment.health_checks = health_check_results

            if not all(check["success"] for check in health_check_results):
                raise Exception("Health checks failed")

            # Step 3: Switch traffic to new environment
            await self._switch_traffic(target_env)

            # Step 4: Update current environment
            old_env = self.current_environment
            self.current_environment = target_env

            deployment.status = DeploymentStatus.COMPLETED
            deployment.completed_at = datetime.now(timezone.utc)

            logger.info(
                f"Blue-green deployment completed. Switched from {old_env} to {target_env}"
            )

        except Exception as e:
            deployment.status = DeploymentStatus.FAILED
            deployment.error_message = str(e)
            logger.error(f"Blue-green deployment failed: {e}")

            # Attempt automatic rollback
            await self._rollback_deployment(deployment)

        return deployment

    async def _deploy_to_environment(self, environment: str, image_tag: str):
        """Deploy to specific environment"""
        logger.info(f"Deploying to {environment} environment")

        # Update Docker Compose with new image tag
        compose_file = f"docker-compose.{environment}.yml"
        await self._update_docker_compose(compose_file, image_tag)

        # Deploy using Docker Compose
        cmd = ["docker-compose", "-f", compose_file, "up", "-d", "--build"]
        result = await self._run_command(cmd)

        if result.returncode != 0:
            raise Exception(f"Deployment to {environment} failed: {result.stderr}")

        # Wait for services to start
        await asyncio.sleep(30)

    async def _update_docker_compose(self, compose_file: str, image_tag: str):
        """Update Docker Compose file with new image tag"""
        # This would update the docker-compose file with the new image tag
        # For now, we'll just log the action
        logger.info(f"Updating {compose_file} with image tag {image_tag}")

    async def _run_health_checks(self, environment: str) -> List[Dict[str, Any]]:
        """Run health checks for environment"""
        results = []

        for endpoint in self.health_check_endpoints:
            # Adjust endpoint for environment
            env_endpoint = endpoint.replace("localhost", f"{environment}.nexus.local")

            try:
                response = requests.get(env_endpoint, timeout=10)
                success = response.status_code == 200
                results.append(
                    {
                        "endpoint": env_endpoint,
                        "success": success,
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds(),
                    }
                )
            except Exception as e:
                results.append(
                    {"endpoint": env_endpoint, "success": False, "error": str(e)}
                )

        return results

    async def _switch_traffic(self, target_environment: str):
        """Switch traffic to target environment"""
        logger.info(f"Switching traffic to {target_environment} environment")

        # Update load balancer configuration
        await self._update_load_balancer(target_environment)

        # Wait for traffic to stabilize
        await asyncio.sleep(10)

    async def _update_load_balancer(self, target_environment: str):
        """Update load balancer configuration"""
        # This would update nginx or other load balancer configuration
        logger.info(f"Updating load balancer to route traffic to {target_environment}")

    async def rollback_deployment(self, deployment_id: str) -> bool:
        """Rollback a specific deployment"""
        deployment = next((d for d in self.deployments if d.id == deployment_id), None)
        if not deployment:
            logger.error(f"Deployment {deployment_id} not found")
            return False

        return await self._rollback_deployment(deployment)

    async def _rollback_deployment(self, deployment: Deployment) -> bool:
        """Rollback a deployment"""
        logger.info(f"Rolling back deployment {deployment.id}")

        try:
            # Switch back to previous environment
            previous_env = "green" if self.current_environment == "blue" else "blue"
            await self._switch_traffic(previous_env)

            # Update current environment
            self.current_environment = previous_env

            deployment.status = DeploymentStatus.ROLLED_BACK
            deployment.rollback_at = datetime.now(timezone.utc)

            logger.info(f"Rollback completed for deployment {deployment.id}")
            return True

        except Exception as e:
            logger.error(f"Rollback failed for deployment {deployment.id}: {e}")
            return False

    async def _run_command(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """Run a shell command"""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300  # 5 minute timeout
            )
            return result
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {' '.join(cmd)}")
            raise Exception("Command execution timed out")
        except Exception as e:
            logger.error(f"Command failed: {e}")
            raise

    async def get_deployment_status(self, deployment_id: str) -> Optional[Deployment]:
        """Get deployment status"""
        return next((d for d in self.deployments if d.id == deployment_id), None)

    async def list_deployments(self) -> List[Deployment]:
        """List all deployments"""
        return self.deployments

    async def get_current_environment(self) -> str:
        """Get current active environment"""
        return self.current_environment

    async def cleanup_old_deployments(self, keep_count: int = 5):
        """Clean up old deployments"""
        # Keep only the most recent deployments
        self.deployments = sorted(
            self.deployments, key=lambda d: d.created_at, reverse=True
        )[:keep_count]

        logger.info(
            f"Cleaned up old deployments, keeping {len(self.deployments)} most recent"
        )

    def generate_deployment_report(self) -> Dict[str, Any]:
        """Generate deployment report"""
        total_deployments = len(self.deployments)
        successful_deployments = len(
            [d for d in self.deployments if d.status == DeploymentStatus.COMPLETED]
        )
        failed_deployments = len(
            [d for d in self.deployments if d.status == DeploymentStatus.FAILED]
        )
        rolled_back_deployments = len(
            [d for d in self.deployments if d.status == DeploymentStatus.ROLLED_BACK]
        )

        return {
            "current_environment": self.current_environment,
            "total_deployments": total_deployments,
            "successful_deployments": successful_deployments,
            "failed_deployments": failed_deployments,
            "rolled_back_deployments": rolled_back_deployments,
            "success_rate": successful_deployments / total_deployments
            if total_deployments > 0
            else 0,
            "recent_deployments": [
                {
                    "id": d.id,
                    "version": d.version,
                    "status": d.status.value,
                    "created_at": d.created_at.isoformat(),
                    "completed_at": d.completed_at.isoformat()
                    if d.completed_at
                    else None,
                }
                for d in sorted(
                    self.deployments, key=lambda d: d.created_at, reverse=True
                )[:10]
            ],
        }
