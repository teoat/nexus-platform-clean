#!/usr/bin/env python3
"""
NEXUS Platform - Production Deployment Script
Comprehensive production deployment with health checks, rollback, and monitoring
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime

import requests
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("deployment.log"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


@dataclass
class DeploymentConfig:
    """Deployment configuration"""

    environment: str
    version: str
    docker_registry: str
    namespace: str
    replicas: int
    resources: Dict[str, Any]
    health_check_url: str
    rollback_enabled: bool
    monitoring_enabled: bool


class HealthChecker:
    """Health check utility"""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()

    def check_health(self) -> bool:
        """Check application health"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def check_readiness(self) -> bool:
        """Check application readiness"""
        try:
            response = self.session.get(f"{self.base_url}/ready", timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            return False

    def check_liveness(self) -> bool:
        """Check application liveness"""
        try:
            response = self.session.get(f"{self.base_url}/live", timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Liveness check failed: {e}")
            return False

    def wait_for_healthy(self, max_wait: int = 300) -> bool:
        """Wait for application to become healthy"""
        logger.info("Waiting for application to become healthy...")

        start_time = time.time()
        while time.time() - start_time < max_wait:
            if self.check_health() and self.check_readiness() and self.check_liveness():
                logger.info("Application is healthy")
                return True

            time.sleep(10)

        logger.error("Application failed to become healthy within timeout")
        return False


class DatabaseMigrator:
    """Database migration utility"""

    def __init__(self, database_url: str):
        self.database_url = database_url

    def run_migrations(self) -> bool:
        """Run database migrations"""
        try:
            logger.info("Running database migrations...")

            # Set environment variable
            env = os.environ.copy()
            env["DATABASE_URL"] = self.database_url

            # Run migration command
            result = subprocess.run(
                ["python", "-m", "database.migration_manager", "migrate"],
                env=env,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                logger.error(f"Migration failed: {result.stderr}")
                return False

            logger.info("Database migrations completed successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to run migrations: {e}")
            return False

    def verify_migration(self) -> bool:
        """Verify migration was successful"""
        try:
            logger.info("Verifying database migration...")

            # Test database connection
            env = os.environ.copy()
            env["DATABASE_URL"] = self.database_url

            result = subprocess.run(
                [
                    "python",
                    "-c",
                    "from database.connection import check_connection; assert check_connection()",
                ],
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                logger.error(f"Migration verification failed: {result.stderr}")
                return False

            logger.info("Database migration verified successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to verify migration: {e}")
            return False


class DockerManager:
    """Docker management utility"""

    def __init__(self, registry: str, namespace: str):
        self.registry = registry
        self.namespace = namespace

    def build_image(self, service: str, version: str, dockerfile: str) -> bool:
        """Build Docker image"""
        try:
            logger.info(f"Building Docker image for {service}...")

            image_name = f"{self.registry}/{self.namespace}/{service}:{version}"

            # Build image
            result = subprocess.run(
                ["docker", "build", "-t", image_name, "-f", dockerfile, "."],
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode != 0:
                logger.error(f"Docker build failed: {result.stderr}")
                return False

            logger.info(f"Docker image built successfully: {image_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to build Docker image: {e}")
            return False

    def push_image(self, service: str, version: str) -> bool:
        """Push Docker image to registry"""
        try:
            logger.info(f"Pushing Docker image for {service}...")

            image_name = f"{self.registry}/{self.namespace}/{service}:{version}"

            # Push image
            result = subprocess.run(
                ["docker", "push", image_name],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                logger.error(f"Docker push failed: {result.stderr}")
                return False

            logger.info(f"Docker image pushed successfully: {image_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to push Docker image: {e}")
            return False

    def tag_image(self, service: str, version: str, tag: str) -> bool:
        """Tag Docker image"""
        try:
            logger.info(f"Tagging Docker image for {service}...")

            source_image = f"{self.registry}/{self.namespace}/{service}:{version}"
            target_image = f"{self.registry}/{self.namespace}/{service}:{tag}"

            # Tag image
            result = subprocess.run(
                ["docker", "tag", source_image, target_image],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                logger.error(f"Docker tag failed: {result.stderr}")
                return False

            logger.info(f"Docker image tagged successfully: {target_image}")
            return True

        except Exception as e:
            logger.error(f"Failed to tag Docker image: {e}")
            return False


class KubernetesManager:
    """Kubernetes management utility"""

    def __init__(self, namespace: str):
        self.namespace = namespace

    def apply_manifests(self, manifest_dir: str) -> bool:
        """Apply Kubernetes manifests"""
        try:
            logger.info("Applying Kubernetes manifests...")

            # Apply all YAML files in manifest directory
            manifest_files = list(Path(manifest_dir).glob("*.yaml"))

            for manifest_file in manifest_files:
                logger.info(f"Applying manifest: {manifest_file}")

                result = subprocess.run(
                    [
                        "kubectl",
                        "apply",
                        "-f",
                        str(manifest_file),
                        "-n",
                        self.namespace,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

                if result.returncode != 0:
                    logger.error(
                        f"Failed to apply manifest {manifest_file}: {result.stderr}"
                    )
                    return False

            logger.info("Kubernetes manifests applied successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to apply Kubernetes manifests: {e}")
            return False

    def rollout_status(self, deployment: str) -> bool:
        """Check rollout status"""
        try:
            logger.info(f"Checking rollout status for {deployment}...")

            result = subprocess.run(
                [
                    "kubectl",
                    "rollout",
                    "status",
                    f"deployment/{deployment}",
                    "-n",
                    self.namespace,
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                logger.error(f"Rollout status check failed: {result.stderr}")
                return False

            logger.info(f"Rollout status for {deployment}: {result.stdout}")
            return True

        except Exception as e:
            logger.error(f"Failed to check rollout status: {e}")
            return False

    def rollback_deployment(self, deployment: str) -> bool:
        """Rollback deployment"""
        try:
            logger.info(f"Rolling back deployment {deployment}...")

            result = subprocess.run(
                [
                    "kubectl",
                    "rollout",
                    "undo",
                    f"deployment/{deployment}",
                    "-n",
                    self.namespace,
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                logger.error(f"Rollback failed: {result.stderr}")
                return False

            logger.info(f"Deployment {deployment} rolled back successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to rollback deployment: {e}")
            return False


class DeploymentManager:
    """Main deployment manager"""

    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.health_checker = HealthChecker(config.health_check_url)
        self.database_migrator = DatabaseMigrator(os.getenv("DATABASE_URL"))
        self.docker_manager = DockerManager(config.docker_registry, config.namespace)
        self.k8s_manager = KubernetesManager(config.namespace)

        self.deployment_start_time = None
        self.deployment_status = "pending"

    def deploy(self) -> bool:
        """Execute full deployment"""
        try:
            self.deployment_start_time = datetime.now()
            self.deployment_status = "in_progress"

            logger.info(f"Starting deployment of version {self.config.version}")
            logger.info(f"Environment: {self.config.environment}")
            logger.info(f"Namespace: {self.config.namespace}")

            # Step 1: Run database migrations
            if not self.database_migrator.run_migrations():
                logger.error("Database migration failed")
                self.deployment_status = "failed"
                return False

            if not self.database_migrator.verify_migration():
                logger.error("Database migration verification failed")
                self.deployment_status = "failed"
                return False

            # Step 2: Build and push Docker images
            services = ["backend", "frontend", "nginx"]
            for service in services:
                dockerfile = f"docker/{service}/Dockerfile"
                if not self.docker_manager.build_image(
                    service, self.config.version, dockerfile
                ):
                    logger.error(f"Failed to build image for {service}")
                    self.deployment_status = "failed"
                    return False

                if not self.docker_manager.push_image(service, self.config.version):
                    logger.error(f"Failed to push image for {service}")
                    self.deployment_status = "failed"
                    return False

                # Tag as latest
                if not self.docker_manager.tag_image(
                    service, self.config.version, "latest"
                ):
                    logger.error(f"Failed to tag image for {service}")
                    self.deployment_status = "failed"
                    return False

            # Step 3: Apply Kubernetes manifests
            if not self.k8s_manager.apply_manifests("k8s/manifests"):
                logger.error("Failed to apply Kubernetes manifests")
                self.deployment_status = "failed"
                return False

            # Step 4: Wait for rollout
            for service in services:
                if not self.k8s_manager.rollout_status(service):
                    logger.error(f"Rollout failed for {service}")
                    self.deployment_status = "failed"
                    return False

            # Step 5: Health checks
            if not self.health_checker.wait_for_healthy():
                logger.error("Health checks failed")
                self.deployment_status = "failed"
                return False

            # Step 6: Post-deployment verification
            if not self._verify_deployment():
                logger.error("Post-deployment verification failed")
                self.deployment_status = "failed"
                return False

            self.deployment_status = "success"
            logger.info("Deployment completed successfully")
            return True

        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            self.deployment_status = "failed"
            return False

    def rollback(self) -> bool:
        """Rollback deployment"""
        try:
            logger.info("Starting rollback...")

            if not self.config.rollback_enabled:
                logger.error("Rollback is disabled")
                return False

            # Rollback each service
            services = ["backend", "frontend", "nginx"]
            for service in services:
                if not self.k8s_manager.rollback_deployment(service):
                    logger.error(f"Failed to rollback {service}")
                    return False

            # Wait for rollback to complete
            for service in services:
                if not self.k8s_manager.rollout_status(service):
                    logger.error(f"Rollback failed for {service}")
                    return False

            # Verify rollback
            if not self.health_checker.wait_for_healthy():
                logger.error("Health checks failed after rollback")
                return False

            logger.info("Rollback completed successfully")
            return True

        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

    def _verify_deployment(self) -> bool:
        """Verify deployment is working correctly"""
        try:
            logger.info("Verifying deployment...")

            # Check health endpoints
            if not self.health_checker.check_health():
                return False

            if not self.health_checker.check_readiness():
                return False

            if not self.health_checker.check_liveness():
                return False

            # Check API endpoints
            api_endpoints = ["/api/health", "/api/ready", "/api/live"]

            for endpoint in api_endpoints:
                try:
                    response = requests.get(
                        f"{self.config.health_check_url}{endpoint}", timeout=10
                    )
                    if response.status_code != 200:
                        logger.error(
                            f"API endpoint {endpoint} returned {response.status_code}"
                        )
                        return False
                except Exception as e:
                    logger.error(f"Failed to check API endpoint {endpoint}: {e}")
                    return False

            logger.info("Deployment verification successful")
            return True

        except Exception as e:
            logger.error(f"Deployment verification failed: {e}")
            return False

    def get_deployment_status(self) -> Dict[str, Any]:
        """Get deployment status"""
        return {
            "status": self.deployment_status,
            "version": self.config.version,
            "environment": self.config.environment,
            "namespace": self.config.namespace,
            "start_time": self.deployment_start_time.isoformat()
            if self.deployment_start_time
            else None,
            "duration": (datetime.now() - self.deployment_start_time).total_seconds()
            if self.deployment_start_time
            else None,
        }


def load_config(config_file: str) -> DeploymentConfig:
    """Load deployment configuration from file"""
    try:
        with open(config_file, "r") as f:
            config_data = yaml.safe_load(f)

        return DeploymentConfig(
            environment=config_data["environment"],
            version=config_data["version"],
            docker_registry=config_data["docker_registry"],
            namespace=config_data["namespace"],
            replicas=config_data["replicas"],
            resources=config_data["resources"],
            health_check_url=config_data["health_check_url"],
            rollback_enabled=config_data["rollback_enabled"],
            monitoring_enabled=config_data["monitoring_enabled"],
        )

    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="NEXUS Platform Production Deployment")
    parser.add_argument("--config", required=True, help="Deployment configuration file")
    parser.add_argument("--rollback", action="store_true", help="Rollback deployment")
    parser.add_argument("--status", action="store_true", help="Check deployment status")
    parser.add_argument("--dry-run", action="store_true", help="Dry run deployment")

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Create deployment manager
    deployment_manager = DeploymentManager(config)

    if args.rollback:
        # Rollback deployment
        success = deployment_manager.rollback()
        sys.exit(0 if success else 1)

    elif args.status:
        # Check deployment status
        status = deployment_manager.get_deployment_status()
        print(json.dumps(status, indent=2))
        sys.exit(0)

    elif args.dry_run:
        # Dry run deployment
        logger.info("Dry run mode - no actual deployment will be performed")
        logger.info(f"Would deploy version {config.version} to {config.environment}")
        sys.exit(0)

    else:
        # Execute deployment
        success = deployment_manager.deploy()

        if success:
            logger.info("Deployment completed successfully")
            sys.exit(0)
        else:
            logger.error("Deployment failed")
            sys.exit(1)


if __name__ == "__main__":
    main()
