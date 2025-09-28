#!/usr/bin/env python3
"""
Blue-Green Deployment Service
Zero-downtime deployment strategy with traffic switching and rollback capabilities
"""

import asyncio
import json
import logging
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import kubernetes.client
from kubernetes import config

logger = logging.getLogger(__name__)


class DeploymentColor(Enum):
    BLUE = "blue"
    GREEN = "green"


class TrafficDistribution(Enum):
    BLUE_ONLY = "blue_only"
    GREEN_ONLY = "green_only"
    BLUE_90_GREEN_10 = "blue_90_green_10"
    BLUE_75_GREEN_25 = "blue_75_green_25"
    BLUE_50_GREEN_50 = "blue_50_green_50"
    BLUE_25_GREEN_75 = "blue_25_green_75"
    BLUE_10_GREEN_90 = "blue_10_green_90"


class DeploymentPhase(Enum):
    PREPARATION = "preparation"
    DEPLOYMENT = "deployment"
    HEALTH_CHECKS = "health_checks"
    TRAFFIC_SWITCHING = "traffic_switching"
    VALIDATION = "validation"
    FULL_TRAFFIC = "full_traffic"
    CLEANUP = "cleanup"
    ROLLBACK = "rollback"


@dataclass
class BlueGreenDeployment:
    """Blue-green deployment instance"""

    deployment_id: str
    version: str
    environment: str
    active_color: DeploymentColor
    inactive_color: DeploymentColor
    current_traffic: TrafficDistribution
    phases_completed: List[DeploymentPhase]
    health_checks: Dict[str, Any]
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    rollback_available: bool


@dataclass
class HealthCheckResult:
    """Result of a health check"""

    service_name: str
    endpoint: str
    status: str
    response_time_ms: float
    error_message: Optional[str]
    timestamp: datetime


@dataclass
class TrafficSwitchResult:
    """Result of a traffic switching operation"""

    from_distribution: TrafficDistribution
    to_distribution: TrafficDistribution
    success: bool
    traffic_shifted_percent: float
    duration_ms: float
    timestamp: datetime


class BlueGreenDeploymentService:
    """Service for managing blue-green deployments"""

    def __init__(self):
        self.deployments: Dict[str, BlueGreenDeployment] = {}
        self.health_check_results: Dict[str, List[HealthCheckResult]] = {}
        self.traffic_switch_history: Dict[str, List[TrafficSwitchResult]] = {}

        # Configuration
        self.health_check_config = {
            "endpoints": [
                "/health",
                "/api/health",
                "/api/v3/ssot/aliases",
                "/api/v3/auth/login",
            ],
            "timeout_seconds": 30,
            "retries": 3,
            "success_threshold": 0.95,  # 95% of checks must pass
        }

        self.traffic_switch_config = {
            "gradual_steps": [
                TrafficDistribution.BLUE_90_GREEN_10,
                TrafficDistribution.BLUE_75_GREEN_25,
                TrafficDistribution.BLUE_50_GREEN_50,
                TrafficDistribution.BLUE_25_GREEN_75,
                TrafficDistribution.BLUE_10_GREEN_90,
                TrafficDistribution.GREEN_ONLY,
            ],
            "step_duration_minutes": 5,
            "validation_duration_minutes": 2,
        }

        # Kubernetes client
        try:
            config.load_incluster_config()
            self.k8s_client = kubernetes.client.AppsV1Api()
        except:
            logger.warning(
                "Could not initialize Kubernetes client - running in local mode"
            )
            self.k8s_client = None

    async def start_blue_green_deployment(
        self, version: str, environment: str, initial_traffic_percent: int = 10
    ) -> BlueGreenDeployment:
        """Start a blue-green deployment"""
        deployment_id = f"bg_deploy_{environment}_{version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Determine colors - blue is typically active, green is new
        active_color = DeploymentColor.BLUE
        inactive_color = DeploymentColor.GREEN

        # Set initial traffic distribution
        if initial_traffic_percent <= 10:
            current_traffic = TrafficDistribution.BLUE_90_GREEN_10
        elif initial_traffic_percent <= 25:
            current_traffic = TrafficDistribution.BLUE_75_GREEN_25
        else:
            current_traffic = TrafficDistribution.BLUE_50_GREEN_50

        deployment = BlueGreenDeployment(
            deployment_id=deployment_id,
            version=version,
            environment=environment,
            active_color=active_color,
            inactive_color=inactive_color,
            current_traffic=current_traffic,
            phases_completed=[],
            health_checks={},
            start_time=datetime.now(),
            end_time=None,
            status="starting",
            rollback_available=False,
        )

        self.deployments[deployment_id] = deployment
        self.health_check_results[deployment_id] = []
        self.traffic_switch_history[deployment_id] = []

        logger.info(f"Started blue-green deployment {deployment_id}")

        # Start deployment process
        asyncio.create_task(self._run_deployment_process(deployment))

        return deployment

    async def _run_deployment_process(self, deployment: BlueGreenDeployment):
        """Execute the blue-green deployment process"""
        try:
            # Phase 1: Preparation
            deployment.phases_completed.append(DeploymentPhase.PREPARATION)
            deployment.status = "preparing"
            await self._prepare_deployment(deployment)

            # Phase 2: Deploy to inactive environment
            deployment.phases_completed.append(DeploymentPhase.DEPLOYMENT)
            deployment.status = "deploying"
            await self._deploy_to_inactive_environment(deployment)

            # Phase 3: Health checks
            deployment.phases_completed.append(DeploymentPhase.HEALTH_CHECKS)
            deployment.status = "health_checking"
            health_passed = await self._run_health_checks(deployment)

            if not health_passed:
                logger.error(
                    f"Health checks failed for deployment {deployment.deployment_id}"
                )
                await self._rollback_deployment(deployment)
                return

            # Phase 4: Gradual traffic switching
            deployment.phases_completed.append(DeploymentPhase.TRAFFIC_SWITCHING)
            deployment.status = "switching_traffic"
            await self._gradual_traffic_switching(deployment)

            # Phase 5: Full traffic validation
            deployment.phases_completed.append(DeploymentPhase.VALIDATION)
            deployment.status = "validating"
            validation_passed = await self._validate_full_traffic(deployment)

            if not validation_passed:
                logger.error(
                    f"Validation failed for deployment {deployment.deployment_id}"
                )
                await self._rollback_deployment(deployment)
                return

            # Phase 6: Switch to full traffic
            deployment.phases_completed.append(DeploymentPhase.FULL_TRAFFIC)
            deployment.status = "completing"
            await self._switch_to_full_traffic(deployment)

            # Phase 7: Cleanup old environment
            deployment.phases_completed.append(DeploymentPhase.CLEANUP)
            deployment.status = "completed"
            await self._cleanup_old_environment(deployment)

            deployment.end_time = datetime.now()
            deployment.rollback_available = True

            logger.info(
                f"Blue-green deployment {deployment.deployment_id} completed successfully"
            )

        except Exception as e:
            logger.error(
                f"Error during blue-green deployment {deployment.deployment_id}: {e}"
            )
            deployment.status = "failed"
            deployment.end_time = datetime.now()
            await self._rollback_deployment(deployment)

    async def _prepare_deployment(self, deployment: BlueGreenDeployment):
        """Prepare the deployment environment"""
        logger.info(f"Preparing deployment {deployment.deployment_id}")

        # Validate deployment prerequisites
        await self._validate_prerequisites(deployment)

        # Setup monitoring and alerting
        await self._setup_monitoring(deployment)

        # Prepare inactive environment
        await self._prepare_inactive_environment(deployment)

    async def _validate_prerequisites(self, deployment: BlueGreenDeployment):
        """Validate deployment prerequisites"""
        # Check Kubernetes cluster health
        if self.k8s_client:
            try:
                # Check if deployments exist
                blue_deployment = self.k8s_client.read_namespaced_deployment(
                    f"nexus-{deployment.environment}-blue", deployment.environment
                )
                green_deployment = self.k8s_client.read_namespaced_deployment(
                    f"nexus-{deployment.environment}-green", deployment.environment
                )
            except Exception as e:
                logger.error(f"Kubernetes validation failed: {e}")
                raise

        # Check service mesh/load balancer readiness
        await self._validate_service_mesh(deployment)

    async def _setup_monitoring(self, deployment: BlueGreenDeployment):
        """Setup monitoring and alerting for deployment"""
        # Setup deployment-specific metrics
        # Setup alerting rules
        pass

    async def _prepare_inactive_environment(self, deployment: BlueGreenDeployment):
        """Prepare the inactive environment for deployment"""
        inactive_color = deployment.inactive_color.value

        if self.k8s_client:
            # Scale up inactive deployment
            await self._scale_deployment(
                f"nexus-{deployment.environment}-{inactive_color}",
                deployment.environment,
                replicas=1,
            )

            # Update image version
            await self._update_deployment_image(
                f"nexus-{deployment.environment}-{inactive_color}",
                deployment.environment,
                f"nexus-platform:{deployment.version}",
            )

    async def _deploy_to_inactive_environment(self, deployment: BlueGreenDeployment):
        """Deploy new version to inactive environment"""
        logger.info(f"Deploying to inactive environment for {deployment.deployment_id}")

        inactive_color = deployment.inactive_color.value

        if self.k8s_client:
            # Trigger rolling update
            await self._trigger_rolling_update(
                f"nexus-{deployment.environment}-{inactive_color}",
                deployment.environment,
            )

            # Wait for rollout to complete
            await self._wait_for_rollout(
                f"nexus-{deployment.environment}-{inactive_color}",
                deployment.environment,
                timeout_minutes=10,
            )

    async def _run_health_checks(self, deployment: BlueGreenDeployment) -> bool:
        """Run comprehensive health checks on inactive environment"""
        logger.info(f"Running health checks for deployment {deployment.deployment_id}")

        inactive_color = deployment.inactive_color.value
        base_url = f"http://nexus-{deployment.environment}-{inactive_color}"

        health_results = []

        for endpoint in self.health_check_config["endpoints"]:
            result = await self._check_endpoint_health(
                f"{base_url}{endpoint}", deployment.deployment_id
            )
            health_results.append(result)

        # Calculate success rate
        successful_checks = sum(1 for r in health_results if r.status == "healthy")
        success_rate = successful_checks / len(health_results) if health_results else 0

        deployment.health_checks = {
            "total_checks": len(health_results),
            "successful_checks": successful_checks,
            "success_rate": success_rate,
            "results": [asdict(r) for r in health_results],
        }

        return success_rate >= self.health_check_config["success_threshold"]

    async def _check_endpoint_health(
        self, url: str, deployment_id: str
    ) -> HealthCheckResult:
        """Check health of a specific endpoint"""
        start_time = datetime.now()

        for attempt in range(self.health_check_config["retries"]):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        timeout=aiohttp.ClientTimeout(
                            total=self.health_check_config["timeout_seconds"]
                        ),
                    ) as response:
                        response_time = (
                            datetime.now() - start_time
                        ).total_seconds() * 1000

                        if response.status == 200:
                            result = HealthCheckResult(
                                service_name=url.split("/")[-1] or "health",
                                endpoint=url,
                                status="healthy",
                                response_time_ms=response_time,
                                error_message=None,
                                timestamp=datetime.now(),
                            )
                            self.health_check_results[deployment_id].append(result)
                            return result
                        else:
                            error_msg = f"HTTP {response.status}"

            except Exception as e:
                error_msg = str(e)

            # Wait before retry
            if attempt < self.health_check_config["retries"] - 1:
                await asyncio.sleep(1)

        # All retries failed
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        result = HealthCheckResult(
            service_name=url.split("/")[-1] or "health",
            endpoint=url,
            status="unhealthy",
            response_time_ms=response_time,
            error_message=error_msg,
            timestamp=datetime.now(),
        )
        self.health_check_results[deployment_id].append(result)
        return result

    async def _gradual_traffic_switching(self, deployment: BlueGreenDeployment):
        """Gradually switch traffic from blue to green"""
        logger.info(
            f"Starting gradual traffic switching for {deployment.deployment_id}"
        )

        current_dist = deployment.current_traffic

        # Find starting point in gradual steps
        steps = self.traffic_switch_config["gradual_steps"]
        start_index = steps.index(current_dist) if current_dist in steps else 0

        for i in range(start_index, len(steps)):
            target_distribution = steps[i]

            # Switch traffic
            switch_result = await self._switch_traffic(
                deployment, deployment.current_traffic, target_distribution
            )

            self.traffic_switch_history[deployment.deployment_id].append(switch_result)

            if not switch_result.success:
                logger.error(f"Traffic switch failed for {deployment.deployment_id}")
                raise Exception("Traffic switching failed")

            deployment.current_traffic = target_distribution

            # Validate traffic distribution
            await self._validate_traffic_distribution(deployment, target_distribution)

            # Wait before next step
            if i < len(steps) - 1:  # Not the last step
                await asyncio.sleep(
                    self.traffic_switch_config["step_duration_minutes"] * 60
                )

    async def _switch_traffic(
        self,
        deployment: BlueGreenDeployment,
        from_dist: TrafficDistribution,
        to_dist: TrafficDistribution,
    ) -> TrafficSwitchResult:
        """Switch traffic distribution"""
        start_time = datetime.now()

        try:
            # Calculate traffic percentages
            traffic_map = {
                TrafficDistribution.BLUE_ONLY: (100, 0),
                TrafficDistribution.GREEN_ONLY: (0, 100),
                TrafficDistribution.BLUE_90_GREEN_10: (90, 10),
                TrafficDistribution.BLUE_75_GREEN_25: (75, 25),
                TrafficDistribution.BLUE_50_GREEN_50: (50, 50),
                TrafficDistribution.BLUE_25_GREEN_75: (25, 75),
                TrafficDistribution.BLUE_10_GREEN_90: (10, 90),
            }

            blue_percent, green_percent = traffic_map[to_dist]

            # Update load balancer/ingress
            if self.k8s_client:
                await self._update_ingress_weights(
                    deployment.environment, blue_percent, green_percent
                )

            duration = (datetime.now() - start_time).total_seconds() * 1000

            return TrafficSwitchResult(
                from_distribution=from_dist,
                to_distribution=to_dist,
                success=True,
                traffic_shifted_percent=green_percent,
                duration_ms=duration,
                timestamp=datetime.now(),
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(f"Traffic switch failed: {e}")

            return TrafficSwitchResult(
                from_distribution=from_dist,
                to_distribution=to_dist,
                success=False,
                traffic_shifted_percent=0,
                duration_ms=duration,
                timestamp=datetime.now(),
            )

    async def _validate_traffic_distribution(
        self,
        deployment: BlueGreenDeployment,
        expected_distribution: TrafficDistribution,
    ):
        """Validate that traffic is distributed as expected"""
        # Monitor traffic distribution for validation period
        validation_duration = (
            self.traffic_switch_config["validation_duration_minutes"] * 60
        )

        # In a real implementation, this would monitor actual traffic metrics
        # For now, we'll simulate validation
        await asyncio.sleep(min(10, validation_duration))  # Brief validation

    async def _validate_full_traffic(self, deployment: BlueGreenDeployment) -> bool:
        """Validate full traffic switch"""
        logger.info(f"Validating full traffic switch for {deployment.deployment_id}")

        # Run comprehensive validation
        health_passed = await self._run_health_checks(deployment)

        # Check error rates
        error_rate_ok = await self._check_error_rates(deployment)

        # Check performance metrics
        performance_ok = await self._check_performance_metrics(deployment)

        return health_passed and error_rate_ok and performance_ok

    async def _check_error_rates(self, deployment: BlueGreenDeployment) -> bool:
        """Check error rates during deployment"""
        # Mock error rate checking
        return True

    async def _check_performance_metrics(self, deployment: BlueGreenDeployment) -> bool:
        """Check performance metrics during deployment"""
        # Mock performance checking
        return True

    async def _switch_to_full_traffic(self, deployment: BlueGreenDeployment):
        """Switch all traffic to new version"""
        logger.info(f"Switching to full traffic for {deployment.deployment_id}")

        final_switch = await self._switch_traffic(
            deployment, deployment.current_traffic, TrafficDistribution.GREEN_ONLY
        )

        if final_switch.success:
            # Swap colors - green becomes active
            deployment.active_color, deployment.inactive_color = (
                deployment.inactive_color,
                deployment.active_color,
            )
            deployment.current_traffic = TrafficDistribution.GREEN_ONLY

    async def _cleanup_old_environment(self, deployment: BlueGreenDeployment):
        """Clean up old environment"""
        logger.info(f"Cleaning up old environment for {deployment.deployment_id}")

        # Scale down old deployment
        old_color = deployment.inactive_color.value
        if self.k8s_client:
            await self._scale_deployment(
                f"nexus-{deployment.environment}-{old_color}",
                deployment.environment,
                replicas=0,
            )

    async def _rollback_deployment(self, deployment: BlueGreenDeployment):
        """Rollback deployment to previous version"""
        logger.info(f"Rolling back deployment {deployment.deployment_id}")

        deployment.phases_completed.append(DeploymentPhase.ROLLBACK)
        deployment.status = "rolled_back"

        try:
            # Switch all traffic back to blue
            rollback_switch = await self._switch_traffic(
                deployment, deployment.current_traffic, TrafficDistribution.BLUE_ONLY
            )

            if rollback_switch.success:
                deployment.current_traffic = TrafficDistribution.BLUE_ONLY
                deployment.active_color = DeploymentColor.BLUE
                deployment.inactive_color = DeploymentColor.GREEN

                # Scale down green environment
                if self.k8s_client:
                    await self._scale_deployment(
                        f"nexus-{deployment.environment}-green",
                        deployment.environment,
                        replicas=0,
                    )

                logger.info(
                    f"Rollback successful for deployment {deployment.deployment_id}"
                )
            else:
                logger.error(
                    f"Rollback traffic switch failed for deployment {deployment.deployment_id}"
                )

        except Exception as e:
            logger.error(
                f"Rollback failed for deployment {deployment.deployment_id}: {e}"
            )

    async def get_deployment_status(
        self, deployment_id: str
    ) -> Optional[BlueGreenDeployment]:
        """Get deployment status"""
        return self.deployments.get(deployment_id)

    async def list_deployments(
        self,
        environment: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
    ) -> List[BlueGreenDeployment]:
        """List deployments"""
        deployments = list(self.deployments.values())

        if environment:
            deployments = [d for d in deployments if d.environment == environment]

        if status:
            deployments = [d for d in deployments if d.status == status]

        return sorted(deployments, key=lambda d: d.start_time, reverse=True)[:limit]

    async def manual_traffic_switch(
        self, deployment_id: str, target_distribution: TrafficDistribution
    ) -> bool:
        """Manually switch traffic distribution"""
        deployment = self.deployments.get(deployment_id)
        if not deployment or deployment.status != "completed":
            return False

        switch_result = await self._switch_traffic(
            deployment, deployment.current_traffic, target_distribution
        )

        if switch_result.success:
            deployment.current_traffic = target_distribution
            self.traffic_switch_history[deployment_id].append(switch_result)
            return True

        return False

    async def trigger_rollback(self, deployment_id: str) -> bool:
        """Trigger manual rollback"""
        deployment = self.deployments.get(deployment_id)
        if not deployment or not deployment.rollback_available:
            return False

        await self._rollback_deployment(deployment)
        return True

    async def get_deployment_metrics(self, deployment_id: str) -> Dict[str, Any]:
        """Get detailed metrics for a deployment"""
        deployment = self.deployments.get(deployment_id)
        if not deployment:
            return {}

        health_results = self.health_check_results.get(deployment_id, [])
        traffic_history = self.traffic_switch_history.get(deployment_id, [])

        # Calculate metrics
        avg_response_time = (
            statistics.mean([r.response_time_ms for r in health_results])
            if health_results
            else 0
        )
        health_success_rate = (
            sum(1 for r in health_results if r.status == "healthy")
            / len(health_results)
            if health_results
            else 0
        )

        traffic_switch_times = [t.duration_ms for t in traffic_history if t.success]
        avg_switch_time = (
            statistics.mean(traffic_switch_times) if traffic_switch_times else 0
        )

        return {
            "deployment_id": deployment_id,
            "status": deployment.status,
            "duration_minutes": (
                deployment.end_time - deployment.start_time
            ).total_seconds()
            / 60
            if deployment.end_time
            else None,
            "health_checks_total": len(health_results),
            "health_success_rate": health_success_rate,
            "average_response_time_ms": avg_response_time,
            "traffic_switches_total": len(traffic_history),
            "traffic_switches_successful": sum(1 for t in traffic_history if t.success),
            "average_switch_time_ms": avg_switch_time,
            "current_traffic_distribution": deployment.current_traffic.value,
            "rollback_available": deployment.rollback_available,
        }

    # Kubernetes helper methods
    async def _scale_deployment(self, name: str, namespace: str, replicas: int):
        """Scale a Kubernetes deployment"""
        if not self.k8s_client:
            return

        # Mock scaling
        pass

    async def _update_deployment_image(self, name: str, namespace: str, image: str):
        """Update deployment image"""
        if not self.k8s_client:
            return

        # Mock image update
        pass

    async def _trigger_rolling_update(self, name: str, namespace: str):
        """Trigger rolling update"""
        if not self.k8s_client:
            return

        # Mock rolling update
        pass

    async def _wait_for_rollout(self, name: str, namespace: str, timeout_minutes: int):
        """Wait for rollout to complete"""
        if not self.k8s_client:
            return

        # Mock rollout wait
        await asyncio.sleep(5)

    async def _update_ingress_weights(
        self, namespace: str, blue_weight: int, green_weight: int
    ):
        """Update ingress traffic weights"""
        if not self.k8s_client:
            return

        # Mock ingress update
        pass

    async def _validate_service_mesh(self, deployment: BlueGreenDeployment):
        """Validate service mesh configuration"""
        # Mock service mesh validation
        pass


# Global instance
blue_green_deployment_service = BlueGreenDeploymentService()
