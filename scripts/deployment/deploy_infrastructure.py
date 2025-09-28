#!/usr/bin/env python3
"""
NEXUS Platform - Infrastructure Deployment Script
Automated deployment of production infrastructure
"""

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class InfrastructureDeployer:
    """Infrastructure deployment manager"""

    def __init__(self, config_file: str = "config/production.yaml"):
        self.config_file = config_file
        self.config = self._load_config()
        self.deployment_log = []

    def _load_config(self) -> Dict[str, Any]:
        """Load deployment configuration"""
        try:
            import yaml

            with open(self.config_file, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)

    def deploy_all(self) -> bool:
        """Deploy all infrastructure components"""
        try:
            logger.info("Starting infrastructure deployment...")

            # Step 1: Deploy Terraform infrastructure
            if not self._deploy_terraform():
                logger.error("Terraform deployment failed")
                return False

            # Step 2: Configure Kubernetes
            if not self._configure_kubernetes():
                logger.error("Kubernetes configuration failed")
                return False

            # Step 3: Deploy applications
            if not self._deploy_applications():
                logger.error("Application deployment failed")
                return False

            # Step 4: Configure monitoring
            if not self._configure_monitoring():
                logger.error("Monitoring configuration failed")
                return False

            # Step 5: Run validation
            if not self._run_validation():
                logger.error("Validation failed")
                return False

            logger.info("Infrastructure deployment completed successfully")
            self._generate_deployment_report()
            return True

        except Exception as e:
            logger.error(f"Infrastructure deployment failed: {e}")
            return False

    def _deploy_terraform(self) -> bool:
        """Deploy Terraform infrastructure"""
        logger.info("Deploying Terraform infrastructure...")

        try:
            # Change to terraform directory
            terraform_dir = Path("infrastructure/terraform")
            if not terraform_dir.exists():
                logger.error("Terraform directory not found")
                return False

            # Initialize Terraform
            result = subprocess.run(
                ["terraform", "init"],
                cwd=terraform_dir,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                logger.error(f"Terraform init failed: {result.stderr}")
                return False

            # Plan Terraform deployment
            result = subprocess.run(
                ["terraform", "plan", "-out=tfplan"],
                cwd=terraform_dir,
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode != 0:
                logger.error(f"Terraform plan failed: {result.stderr}")
                return False

            # Apply Terraform deployment
            result = subprocess.run(
                ["terraform", "apply", "-auto-approve", "tfplan"],
                cwd=terraform_dir,
                capture_output=True,
                text=True,
                timeout=1800,
            )

            if result.returncode != 0:
                logger.error(f"Terraform apply failed: {result.stderr}")
                return False

            logger.info("Terraform infrastructure deployed successfully")
            self.deployment_log.append("Terraform infrastructure deployed")
            return True

        except Exception as e:
            logger.error(f"Terraform deployment failed: {e}")
            return False

    def _configure_kubernetes(self) -> bool:
        """Configure Kubernetes cluster"""
        logger.info("Configuring Kubernetes cluster...")

        try:
            # Update kubeconfig
            result = subprocess.run(
                [
                    "aws",
                    "eks",
                    "update-kubeconfig",
                    "--region",
                    "us-east-1",
                    "--name",
                    "nexus-platform-cluster",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                logger.error(f"Failed to update kubeconfig: {result.stderr}")
                return False

            # Create namespace
            result = subprocess.run(
                ["kubectl", "apply", "-f", "k8s/manifests/namespace.yaml"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                logger.error(f"Failed to create namespace: {result.stderr}")
                return False

            # Ensure nexus-secrets Kubernetes Secret exists (assumed to be pre-created by user)
            result = subprocess.run(
                ["kubectl", "get", "secret", "nexus-secrets", "-n", "nexus-platform"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                logger.error(
                    f"Kubernetes secret 'nexus-secrets' not found. Please create it using 'k8s/manifests/nexus-secrets.yaml' before running this script. Error: {result.stderr}"
                )
                return False
            logger.info("Kubernetes secret 'nexus-secrets' found.")

            logger.info("Kubernetes cluster configured successfully")
            self.deployment_log.append("Kubernetes cluster configured")
            return True

        except Exception as e:
            logger.error(f"Kubernetes configuration failed: {e}")
            return False

    def _deploy_applications(self) -> bool:
        """Deploy applications to Kubernetes"""
        logger.info("Deploying applications...")

        try:
            # Deploy backend
            result = subprocess.run(
                ["kubectl", "apply", "-f", "k8s/manifests/backend-deployment.yaml"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                logger.error(f"Failed to deploy backend: {result.stderr}")
                return False

            # Deploy frontend
            result = subprocess.run(
                ["kubectl", "apply", "-f", "k8s/manifests/frontend-deployment.yaml"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                logger.error(f"Failed to deploy frontend: {result.stderr}")
                return False

            # Deploy nginx
            result = subprocess.run(
                ["kubectl", "apply", "-f", "k8s/manifests/nginx-deployment.yaml"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                logger.error(f"Failed to deploy nginx: {result.stderr}")
                return False

            # Wait for deployments to be ready
            if not self._wait_for_deployments():
                logger.error("Deployments failed to become ready")
                return False

            logger.info("Applications deployed successfully")
            self.deployment_log.append("Applications deployed")
            return True

        except Exception as e:
            logger.error(f"Application deployment failed: {e}")
            return False

    def _wait_for_deployments(self) -> bool:
        """Wait for deployments to be ready"""
        logger.info("Waiting for deployments to be ready...")

        deployments = ["nexus-backend", "nexus-frontend", "nexus-nginx"]

        for deployment in deployments:
            result = subprocess.run(
                [
                    "kubectl",
                    "rollout",
                    "status",
                    f"deployment/{deployment}",
                    "-n",
                    "nexus-platform",
                ],
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode != 0:
                logger.error(
                    f"Deployment {deployment} failed to become ready: {result.stderr}"
                )
                return False

            logger.info(f"Deployment {deployment} is ready")

        return True

    def _configure_monitoring(self) -> bool:
        """Configure monitoring stack"""
        logger.info("Configuring monitoring...")

        try:
            # Install Prometheus
            result = subprocess.run(
                [
                    "helm",
                    "repo",
                    "add",
                    "prometheus-community",
                    "https://prometheus-community.github.io/helm-charts",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                logger.error(f"Failed to add Prometheus Helm repo: {result.stderr}")
                return False

            result = subprocess.run(
                ["helm", "repo", "update"], capture_output=True, text=True, timeout=60
            )

            if result.returncode != 0:
                logger.error(f"Failed to update Helm repos: {result.stderr}")
                return False

            # Install Prometheus
            result = subprocess.run(
                [
                    "helm",
                    "install",
                    "prometheus",
                    "prometheus-community/kube-prometheus-stack",
                    "--namespace",
                    "nexus-platform",
                    "--create-namespace",
                    "--set",
                    "grafana.adminPassword=admin123",
                ],
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode != 0:
                logger.error(f"Failed to install Prometheus: {result.stderr}")
                return False

            logger.info("Monitoring configured successfully")
            self.deployment_log.append("Monitoring configured")
            return True

        except Exception as e:
            logger.error(f"Monitoring configuration failed: {e}")
            return False

    def _run_validation(self) -> bool:
        """Run production validation"""
        logger.info("Running production validation...")

        try:
            result = subprocess.run(
                ["python3", "scripts/validate_production.py"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                logger.error(f"Validation failed: {result.stderr}")
                return False

            logger.info("Production validation completed successfully")
            self.deployment_log.append("Production validation completed")
            return True

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False

    def _generate_deployment_report(self):
        """Generate deployment report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "deployment_log": self.deployment_log,
            "configuration": {
                "config_file": self.config_file,
                "environment": "production",
            },
        }

        report_file = f"/var/log/nexus/deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Deployment report generated: {report_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="NEXUS Platform Infrastructure Deployment"
    )
    parser.add_argument(
        "--config", default="config/production.yaml", help="Configuration file"
    )
    parser.add_argument("--dry-run", action="store_true", help="Dry run deployment")

    args = parser.parse_args()

    if args.dry_run:
        logger.info("Dry run mode - no actual deployment will be performed")
        return

    # Create deployer instance
    deployer = InfrastructureDeployer(args.config)

    # Deploy infrastructure
    success = deployer.deploy_all()

    if success:
        logger.info("Infrastructure deployment completed successfully")
        sys.exit(0)
    else:
        logger.error("Infrastructure deployment failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
