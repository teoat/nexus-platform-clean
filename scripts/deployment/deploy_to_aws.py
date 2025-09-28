#!/usr/bin/env python3
"""
NEXUS Platform - AWS Deployment Script
Comprehensive deployment script for AWS infrastructure and application
"""

import argparse
import json
import logging
import subprocess
import sys

import boto3

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("aws_deployment.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class AWSDeployer:
    """AWS deployment manager"""

    def __init__(self, environment: str = "production", region: str = "us-east-1"):
        self.environment = environment
        self.region = region
        self.project_name = "nexus-platform"
        self.aws_account_id = None
        self.ecr_repository = f"{self.project_name}-{environment}"

        # Initialize AWS clients
        self.ecs_client = None
        self.ecr_client = None
        self.elb_client = None
        self.rds_client = None
        self.elasticache_client = None

        self._initialize_aws_clients()

    def _initialize_aws_clients(self):
        """Initialize AWS clients"""
        try:
            # Get AWS account ID
            sts_client = boto3.client("sts", region_name=self.region)
            self.aws_account_id = sts_client.get_caller_identity()["Account"]

            # Initialize clients
            self.ecs_client = boto3.client("ecs", region_name=self.region)
            self.ecr_client = boto3.client("ecr", region_name=self.region)
            self.elb_client = boto3.client("elbv2", region_name=self.region)
            self.rds_client = boto3.client("rds", region_name=self.region)
            self.elasticache_client = boto3.client(
                "elasticache", region_name=self.region
            )

            logger.info("AWS clients initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AWS clients: {e}")
            raise

    def check_prerequisites(self) -> bool:
        """Check deployment prerequisites"""
        try:
            logger.info("Checking deployment prerequisites...")

            # Check AWS CLI
            result = subprocess.run(
                ["aws", "--version"], capture_output=True, text=True
            )
            if result.returncode != 0:
                logger.error("AWS CLI not found or not configured")
                return False

            # Check Docker
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True
            )
            if result.returncode != 0:
                logger.error("Docker not found")
                return False

            # Check if ECR repository exists
            try:
                self.ecr_client.describe_repositories(
                    repositoryNames=[self.ecr_repository]
                )
                logger.info(f"ECR repository {self.ecr_repository} exists")
            except ClientError:
                logger.warning(
                    f"ECR repository {self.ecr_repository} does not exist, will create it"
                )

            logger.info("Prerequisites check completed successfully")
            return True

        except Exception as e:
            logger.error(f"Prerequisites check failed: {e}")
            return False

    def create_ecr_repository(self) -> bool:
        """Create ECR repository if it doesn't exist"""
        try:
            try:
                # Check if repository exists
                self.ecr_client.describe_repositories(
                    repositoryNames=[self.ecr_repository]
                )
                logger.info(f"ECR repository {self.ecr_repository} already exists")
                return True
            except ClientError:
                # Create repository
                response = self.ecr_client.create_repository(
                    repositoryName=self.ecr_repository,
                    imageScanningConfiguration={"scanOnPush": True},
                    imageTagMutability="MUTABLE",
                )
                logger.info(
                    f"Created ECR repository: {response['repository']['repositoryUri']}"
                )
                return True

        except Exception as e:
            logger.error(f"Failed to create ECR repository: {e}")
            return False

    def build_and_push_backend_image(self) -> bool:
        """Build and push backend Docker image to ECR"""
        try:
            logger.info("Building backend Docker image...")

            # Build Docker image
            image_tag = f"{self.aws_account_id}.dkr.ecr.{self.region}.amazonaws.com/{self.ecr_repository}:backend-latest"

            build_cmd = [
                "docker",
                "build",
                "-f",
                str(project_root / "docker/nexus_backend/Dockerfile"),
                "-t",
                image_tag,
                str(project_root),
            ]

            result = subprocess.run(build_cmd, cwd=project_root, check=True)
            if result.returncode != 0:
                raise Exception("Docker build failed")

            # Login to ECR
            login_cmd = f"aws ecr get-login-password --region {self.region} | docker login --username AWS --password-stdin {self.aws_account_id}.dkr.ecr.{self.region}.amazonaws.com"
            subprocess.run(login_cmd, shell=True, check=True)

            # Push image
            push_cmd = ["docker", "push", image_tag]
            result = subprocess.run(push_cmd, check=True)
            if result.returncode != 0:
                raise Exception("Docker push failed")

            logger.info(f"Successfully built and pushed backend image: {image_tag}")
            return True

        except Exception as e:
            logger.error(f"Failed to build and push backend image: {e}")
            return False

    def build_and_push_frontend_image(self) -> bool:
        """Build and push frontend Docker image to ECR"""
        try:
            logger.info("Building frontend Docker image...")

            # Build Docker image
            image_tag = f"{self.aws_account_id}.dkr.ecr.{self.region}.amazonaws.com/{self.ecr_repository}:frontend-latest"

            build_cmd = [
                "docker",
                "build",
                "-f",
                str(project_root / "docker/nexus_frontend/Dockerfile"),
                "-t",
                image_tag,
                str(project_root / "unified-frontend"),
            ]

            result = subprocess.run(build_cmd, cwd=project_root, check=True)
            if result.returncode != 0:
                raise Exception("Docker build failed")

            # Push image
            push_cmd = ["docker", "push", image_tag]
            result = subprocess.run(push_cmd, check=True)
            if result.returncode != 0:
                raise Exception("Docker push failed")

            logger.info(f"Successfully built and pushed frontend image: {image_tag}")
            return True

        except Exception as e:
            logger.error(f"Failed to build and push frontend image: {e}")
            return False

    def deploy_infrastructure(self) -> bool:
        """Deploy infrastructure using Terraform"""
        try:
            logger.info("Deploying infrastructure with Terraform...")

            terraform_dir = project_root / "infrastructure/terraform"

            # Initialize Terraform
            init_cmd = ["terraform", "init"]
            result = subprocess.run(init_cmd, cwd=terraform_dir, check=True)
            if result.returncode != 0:
                raise Exception("Terraform init failed")

            # Plan deployment
            plan_cmd = ["terraform", "plan", "-var", f"environment={self.environment}"]
            result = subprocess.run(plan_cmd, cwd=terraform_dir, check=True)
            if result.returncode != 0:
                raise Exception("Terraform plan failed")

            # Apply deployment
            apply_cmd = [
                "terraform",
                "apply",
                "-auto-approve",
                "-var",
                f"environment={self.environment}",
            ]
            result = subprocess.run(apply_cmd, cwd=terraform_dir, check=True)
            if result.returncode != 0:
                raise Exception("Terraform apply failed")

            logger.info("Infrastructure deployment completed successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to deploy infrastructure: {e}")
            return False

    def update_ecs_service(self) -> bool:
        """Update ECS service with new task definition"""
        try:
            logger.info("Updating ECS service...")

            # Get current task definition
            task_def_response = self.ecs_client.describe_task_definition(
                taskDefinition=f"{self.project_name}-{self.environment}-task"
            )

            # Create new task definition revision
            new_task_def = task_def_response["taskDefinition"].copy()
            new_task_def["containerDefinitions"][0][
                "image"
            ] = f"{self.aws_account_id}.dkr.ecr.{self.region}.amazonaws.com/{self.ecr_repository}:backend-latest"

            # Register new task definition
            register_response = self.ecs_client.register_task_definition(**new_task_def)
            new_revision = register_response["taskDefinition"]["revision"]

            # Update service
            update_response = self.ecs_client.update_service(
                cluster=f"{self.project_name}-{self.environment}-cluster",
                service=f"{self.project_name}-{self.environment}-service",
                taskDefinition=f"{self.project_name}-{self.environment}-task:{new_revision}",
                forceNewDeployment=True,
            )

            logger.info(
                f"ECS service updated with task definition revision {new_revision}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to update ECS service: {e}")
            return False

    def wait_for_deployment(self) -> bool:
        """Wait for deployment to complete"""
        try:
            logger.info("Waiting for deployment to complete...")

            # Wait for ECS service to be stable
            waiter = self.ecs_client.get_waiter("services_stable")
            waiter.wait(
                cluster=f"{self.project_name}-{self.environment}-cluster",
                services=[f"{self.project_name}-{self.environment}-service"],
                WaiterConfig={"Delay": 30, "MaxAttempts": 60},
            )

            logger.info("Deployment completed successfully")
            return True

        except Exception as e:
            logger.error(f"Deployment failed or timed out: {e}")
            return False

    def run_health_checks(self) -> bool:
        """Run health checks on deployed services"""
        try:
            logger.info("Running health checks...")

            # Check ECS service health
            service_response = self.ecs_client.describe_services(
                cluster=f"{self.project_name}-{self.environment}-cluster",
                services=[f"{self.project_name}-{self.environment}-service"],
            )

            service = service_response["services"][0]
            if service["status"] != "ACTIVE":
                logger.error(f"ECS service is not active: {service['status']}")
                return False

            # Check load balancer health
            lb_response = self.elb_client.describe_load_balancers(
                Names=[f"{self.project_name}-{self.environment}-alb"]
            )

            if lb_response["LoadBalancers"]:
                lb = lb_response["LoadBalancers"][0]
                logger.info(f"Load balancer DNS: {lb['DNSName']}")

                # Check target group health
                tg_response = self.elb_client.describe_target_groups(
                    Names=[f"{self.project_name}-{self.environment}-tg"]
                )

                if tg_response["TargetGroups"]:
                    tg = tg_response["TargetGroups"][0]
                    health_response = self.elb_client.describe_target_health(
                        TargetGroupArn=tg["TargetGroupArn"]
                    )

                    healthy_count = sum(
                        1
                        for target in health_response["TargetHealthDescriptions"]
                        if target["TargetHealth"]["State"] == "healthy"
                    )

                    logger.info(
                        f"Healthy targets: {healthy_count}/{len(health_response['TargetHealthDescriptions'])}"
                    )

                    if healthy_count == 0:
                        logger.error("No healthy targets found")
                        return False

            logger.info("Health checks passed")
            return True

        except Exception as e:
            logger.error(f"Health checks failed: {e}")
            return False

    def create_deployment_report(self, results: Dict[str, bool]) -> str:
        """Create deployment report"""
        report = {
            "deployment_date": subprocess.run(
                ["date", "+%Y-%m-%d %H:%M:%S"], capture_output=True, text=True
            ).stdout.strip(),
            "environment": self.environment,
            "region": self.region,
            "aws_account_id": self.aws_account_id,
            "results": results,
            "successful_steps": sum(1 for r in results.values() if r),
            "total_steps": len(results),
        }

        report_file = (
            project_root
            / f"deployment_report_{self.environment}_{report['deployment_date'].replace(' ', '_').replace(':', '-')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Deployment report saved to {report_file}")
        return str(report_file)

    def run_deployment(self) -> bool:
        """Run complete deployment process"""
        try:
            logger.info(f"Starting deployment to {self.environment} environment...")

            # Track deployment steps
            steps = {
                "prerequisites": False,
                "ecr_repository": False,
                "backend_image": False,
                "frontend_image": False,
                "infrastructure": False,
                "ecs_service": False,
                "deployment_wait": False,
                "health_checks": False,
            }

            # 1. Check prerequisites
            steps["prerequisites"] = self.check_prerequisites()
            if not steps["prerequisites"]:
                return False

            # 2. Create ECR repository
            steps["ecr_repository"] = self.create_ecr_repository()
            if not steps["ecr_repository"]:
                return False

            # 3. Build and push backend image
            steps["backend_image"] = self.build_and_push_backend_image()
            if not steps["backend_image"]:
                return False

            # 4. Build and push frontend image
            steps["frontend_image"] = self.build_and_push_frontend_image()
            if not steps["frontend_image"]:
                return False

            # 5. Deploy infrastructure
            steps["infrastructure"] = self.deploy_infrastructure()
            if not steps["infrastructure"]:
                return False

            # 6. Update ECS service
            steps["ecs_service"] = self.update_ecs_service()
            if not steps["ecs_service"]:
                return False

            # 7. Wait for deployment
            steps["deployment_wait"] = self.wait_for_deployment()
            if not steps["deployment_wait"]:
                return False

            # 8. Run health checks
            steps["health_checks"] = self.run_health_checks()
            if not steps["health_checks"]:
                return False

            # Create deployment report
            report_file = self.create_deployment_report(steps)

            # Summary
            successful_steps = sum(1 for r in steps.values() if r)

            logger.info("=" * 60)
            logger.info("DEPLOYMENT SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Environment: {self.environment}")
            logger.info(f"Region: {self.region}")
            logger.info(f"Successful steps: {successful_steps}/{len(steps)}")
            logger.info(f"Report: {report_file}")

            if successful_steps == len(steps):
                logger.info("✅ Deployment completed successfully!")
                return True
            else:
                logger.error("❌ Deployment completed with errors")
                return False

        except Exception as e:
            logger.error(f"Deployment failed with error: {e}")
            return False


def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description="NEXUS AWS Deployment Tool")
    parser.add_argument(
        "--environment",
        default="production",
        choices=["staging", "production"],
        help="Deployment environment",
    )
    parser.add_argument("--region", default="us-east-1", help="AWS region")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deployed without actually doing it",
    )
    parser.add_argument(
        "--skip-infrastructure",
        action="store_true",
        help="Skip infrastructure deployment",
    )
    parser.add_argument(
        "--skip-images", action="store_true", help="Skip Docker image building"
    )

    args = parser.parse_args()

    deployer = AWSDeployer(environment=args.environment, region=args.region)

    if args.dry_run:
        logger.info("DRY RUN MODE")
        logger.info("Would perform the following deployment steps:")
        logger.info("  1. Check prerequisites")
        logger.info("  2. Create ECR repository")
        logger.info("  3. Build and push backend image")
        logger.info("  4. Build and push frontend image")
        logger.info("  5. Deploy infrastructure")
        logger.info("  6. Update ECS service")
        logger.info("  7. Wait for deployment")
        logger.info("  8. Run health checks")
        return

    success = deployer.run_deployment()

    if success:
        logger.info("Deployment completed successfully!")
        sys.exit(0)
    else:
        logger.error("Deployment failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
