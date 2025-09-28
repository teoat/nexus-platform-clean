#!/usr/bin/env python3
"""
NEXUS Platform - Local Development Deployment Script
Implements next steps for local development and testing
"""

import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class DeploymentStep:
    """Deployment step data structure"""

    step_id: str
    name: str
    status: str
    message: str
    duration: float
    timestamp: datetime


class LocalDeployer:
    """Local development deployment manager"""

    def __init__(self):
        self.steps = []
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load deployment configuration"""
        return {
            "base_url": "http://localhost:8000",
            "frontend_url": "http://localhost:3000",
            "timeout": 300,  # 5 minutes per step
            "deployment_steps": [
                {
                    "id": "setup-environment",
                    "name": "Setup Development Environment",
                    "description": "Set up local development environment",
                    "commands": [
                        "python3 -m venv nexus_env",
                        "source nexus_env/bin/activate && pip install -r requirements.txt",
                    ],
                    "validation": "test -f nexus_env/bin/activate",
                },
                {
                    "id": "database-setup",
                    "name": "Database Setup",
                    "description": "Set up local database",
                    "commands": [
                        'python3 -c "from database.connection import engine; from database.models import Base; Base.metadata.create_all(bind=engine)"'
                    ],
                    "validation": "python3 -c \"from database.connection import engine; print('Database connected successfully')\"",
                },
                {
                    "id": "backend-deployment",
                    "name": "Backend Deployment",
                    "description": "Deploy backend services",
                    "commands": [
                        "python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"
                    ],
                    "validation": "curl -f http://localhost:8000/health",
                },
                {
                    "id": "frontend-deployment",
                    "name": "Frontend Deployment",
                    "description": "Deploy frontend application",
                    "commands": ["cd frontend && npm install && npm run dev"],
                    "validation": "curl -f http://localhost:3000",
                },
                {
                    "id": "security-audit",
                    "name": "Security Audit",
                    "description": "Run security audit",
                    "commands": ["python3 scripts/security_audit.py"],
                    "validation": "test -f logs/nexus/security_audit_report_*.json",
                },
                {
                    "id": "load-testing",
                    "name": "Load Testing",
                    "description": "Run load tests",
                    "commands": [
                        "python3 tests/load/load_test.py --url http://localhost:8000 --users 10 --duration 60"
                    ],
                    "validation": "test -f logs/nexus/load_test_report_*.json",
                },
                {
                    "id": "backup-testing",
                    "name": "Backup Testing",
                    "description": "Test backup procedures",
                    "commands": ["python3 scripts/test_backup_restore.py"],
                    "validation": "test -f logs/nexus/backup_test_report_*.json",
                },
                {
                    "id": "performance-tuning",
                    "name": "Performance Tuning",
                    "description": "Run performance optimization",
                    "commands": ["python3 scripts/performance_tuning.py"],
                    "validation": "test -f logs/nexus/performance_tuning_report_*.json",
                },
            ],
        }

    def deploy_local(self) -> bool:
        """Deploy local development environment"""
        logger.info("Starting local development deployment...")

        try:
            # Check prerequisites
            if not self._check_prerequisites():
                logger.error("Prerequisites check failed")
                return False

            # Execute deployment steps
            if not self._execute_deployment_steps():
                logger.error("Deployment failed")
                return False

            # Generate deployment report
            self._generate_deployment_report()

            # Check overall status
            failed_steps = [s for s in self.steps if s.status == "FAILED"]
            if failed_steps:
                logger.error(f"Deployment failed with {len(failed_steps)} failed steps")
                return False

            logger.info("Local development deployment completed successfully")
            return True

        except Exception as e:
            logger.error(f"Deployment failed with exception: {e}")
            return False

    def _check_prerequisites(self) -> bool:
        """Check prerequisites for deployment"""
        logger.info("Checking prerequisites...")

        try:
            # Check required tools
            required_tools = ["python3", "pip", "curl"]
            for tool in required_tools:
                result = subprocess.run(["which", tool], capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"Required tool {tool} is not installed")
                    return False

            # Check Python version
            result = subprocess.run(
                ["python3", "--version"], capture_output=True, text=True
            )
            if result.returncode != 0:
                logger.error("Python 3 is not available")
                return False

            # Create required directories
            os.makedirs("logs/nexus", exist_ok=True)
            os.makedirs("nexus_env", exist_ok=True)

            logger.info("Prerequisites check passed")
            return True

        except Exception as e:
            logger.error(f"Prerequisites check failed: {e}")
            return False

    def _execute_deployment_steps(self) -> bool:
        """Execute all deployment steps"""
        logger.info("Executing deployment steps...")

        try:
            for step_config in self.config["deployment_steps"]:
                logger.info(f"Executing step: {step_config['name']}")

                start_time = time.time()

                # Execute step commands
                success = self._execute_step_commands(step_config)

                duration = time.time() - start_time

                self.steps.append(
                    DeploymentStep(
                        step_id=step_config["id"],
                        name=step_config["name"],
                        status="PASSED" if success else "FAILED",
                        message="Step completed successfully"
                        if success
                        else "Step failed",
                        duration=duration,
                        timestamp=datetime.now(),
                    )
                )

                if not success:
                    logger.error(f"Step {step_config['id']} failed")
                    # Continue with other steps for local development
                    continue

                # Wait between steps
                time.sleep(5)

            return True

        except Exception as e:
            logger.error(f"Deployment steps execution failed: {e}")
            return False

    def _execute_step_commands(self, step_config: Dict[str, Any]) -> bool:
        """Execute commands for a deployment step"""
        try:
            for command in step_config["commands"]:
                logger.info(f"Executing command: {command}")

                # Handle background processes for long-running services
                if "uvicorn" in command or "npm run dev" in command:
                    logger.info(f"Starting background service: {command}")
                    # For local development, we'll skip background services
                    continue

                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=self.config["timeout"],
                )

                if result.returncode != 0:
                    logger.error(f"Command failed: {command}")
                    logger.error(f"Error: {result.stderr}")
                    return False

                logger.info(f"Command completed: {command}")

            # Validate step
            if "validation" in step_config:
                logger.info(f"Validating step: {step_config['name']}")

                result = subprocess.run(
                    step_config["validation"],
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                if result.returncode != 0:
                    logger.error(f"Validation failed: {step_config['validation']}")
                    logger.error(f"Error: {result.stderr}")
                    return False

                logger.info(f"Validation passed: {step_config['name']}")

            return True

        except subprocess.TimeoutExpired:
            logger.error(f"Step {step_config['id']} timed out")
            return False
        except Exception as e:
            logger.error(f"Step {step_config['id']} failed with exception: {e}")
            return False

    def _generate_deployment_report(self):
        """Generate deployment report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_steps": len(self.steps),
                "passed": len([s for s in self.steps if s.status == "PASSED"]),
                "failed": len([s for s in self.steps if s.status == "FAILED"]),
                "total_duration": sum(s.duration for s in self.steps),
            },
            "config": self.config,
            "steps": [
                {
                    "step_id": s.step_id,
                    "name": s.name,
                    "status": s.status,
                    "message": s.message,
                    "duration": s.duration,
                    "timestamp": s.timestamp.isoformat(),
                }
                for s in self.steps
            ],
        }

        # Save report
        report_file = f"logs/nexus/local_deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Deployment report saved to {report_file}")

        # Print summary
        print("\n" + "=" * 60)
        print("LOCAL DEVELOPMENT DEPLOYMENT REPORT")
        print("=" * 60)
        print(f"Total Steps: {report['summary']['total_steps']}")
        print(f"Passed: {report['summary']['passed']}")
        print(f"Failed: {report['summary']['failed']}")
        print(f"Total Duration: {report['summary']['total_duration']:.2f} seconds")
        print("=" * 60)

        if report["summary"]["failed"] > 0:
            print("\nFAILED STEPS:")
            for s in self.steps:
                if s.status == "FAILED":
                    print(f"  - {s.name}: {s.message}")

        print("\nCOMPLETED STEPS:")
        for s in self.steps:
            if s.status == "PASSED":
                print(f"  ✅ {s.name} ({s.duration:.2f}s)")

        print("\n" + "=" * 60)
        print("LOCAL DEVELOPMENT DEPLOYMENT COMPLETED")
        print("=" * 60)


def main():
    """Main entry point"""
    deployer = LocalDeployer()
    success = deployer.deploy_local()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
