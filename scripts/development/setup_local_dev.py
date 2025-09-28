#!/usr/bin/env python3
"""
NEXUS Platform - Local Development Setup
Simplified setup for local development without external dependencies
"""

import json
import logging
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
class SetupStep:
    """Setup step data structure"""

    step_id: str
    name: str
    status: str
    message: str
    duration: float
    timestamp: datetime


class LocalDevSetup:
    """Local development setup manager"""

    def __init__(self):
        self.steps = []
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load setup configuration"""
        return {
            "base_url": "http://localhost:8000",
            "frontend_url": "http://localhost:3000",
            "timeout": 300,  # 5 minutes per step
            "setup_steps": [
                {
                    "id": "create-structure",
                    "name": "Create Project Structure",
                    "description": "Create necessary directories and files",
                    "commands": [
                        "mkdir -p logs/nexus",
                        "mkdir -p nexus_env",
                        "mkdir -p data/backups",
                        "mkdir -p config/local",
                    ],
                    "validation": "test -d logs/nexus && test -d nexus_env",
                },
                {
                    "id": "install-deps",
                    "name": "Install Dependencies",
                    "description": "Install Python dependencies",
                    "commands": [
                        "pip install --upgrade pip",
                        "pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose passlib pyotp httpx requests aiohttp psutil",
                    ],
                    "validation": "python3 -c 'import fastapi, uvicorn, sqlalchemy'",
                },
                {
                    "id": "create-config",
                    "name": "Create Configuration",
                    "description": "Create local development configuration",
                    "commands": [
                        "echo 'DATABASE_URL=sqlite:///./nexus.db' > .env.local",
                        "python3 -c \"import secrets; print(f'JWT_SECRET_KEY={secrets.token_urlsafe(32)}')\" >> .env.local",
                        "python3 -c \"import secrets; print(f'ENCRYPTION_KEY={secrets.token_urlsafe(32)}')\" >> .env.local",
                    ],
                    "validation": "test -f .env.local",
                },
                {
                    "id": "setup-database",
                    "name": "Setup Database",
                    "description": "Set up SQLite database for local development",
                    "commands": [
                        'python3 -c "from database.connection import create_local_engine; from database.models import Base; engine = create_local_engine(); Base.metadata.create_all(bind=engine)"'
                    ],
                    "validation": "test -f nexus.db",
                },
                {
                    "id": "run-security-audit",
                    "name": "Run Security Audit",
                    "description": "Run security audit for local setup",
                    "commands": ["python3 scripts/security_audit.py"],
                    "validation": "test -f logs/nexus/security_audit_report_*.json",
                },
                {
                    "id": "run-performance-tests",
                    "name": "Run Performance Tests",
                    "description": "Run performance optimization tests",
                    "commands": ["python3 scripts/performance_tuning.py"],
                    "validation": "test -f logs/nexus/performance_tuning_report_*.json",
                },
            ],
        }

    def setup_local_dev(self) -> bool:
        """Set up local development environment"""
        logger.info("Starting local development setup...")

        try:
            # Check prerequisites
            if not self._check_prerequisites():
                logger.error("Prerequisites check failed")
                return False

            # Execute setup steps
            if not self._execute_setup_steps():
                logger.error("Setup failed")
                return False

            # Generate setup report
            self._generate_setup_report()

            # Check overall status
            failed_steps = [s for s in self.steps if s.status == "FAILED"]
            if failed_steps:
                logger.error(f"Setup failed with {len(failed_steps)} failed steps")
                return False

            logger.info("Local development setup completed successfully")
            return True

        except Exception as e:
            logger.error(f"Setup failed with exception: {e}")
            return False

    def _check_prerequisites(self) -> bool:
        """Check prerequisites for setup"""
        logger.info("Checking prerequisites...")

        try:
            # Check required tools
            required_tools = ["python3", "pip"]
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

            logger.info("Prerequisites check passed")
            return True

        except Exception as e:
            logger.error(f"Prerequisites check failed: {e}")
            return False

    def _execute_setup_steps(self) -> bool:
        """Execute all setup steps"""
        logger.info("Executing setup steps...")

        try:
            for step_config in self.config["setup_steps"]:
                logger.info(f"Executing step: {step_config['name']}")

                start_time = time.time()

                # Execute step commands
                success = self._execute_step_commands(step_config)

                duration = time.time() - start_time

                self.steps.append(
                    SetupStep(
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
                time.sleep(2)

            return True

        except Exception as e:
            logger.error(f"Setup steps execution failed: {e}")
            return False

    def _execute_step_commands(self, step_config: Dict[str, Any]) -> bool:
        """Execute commands for a setup step"""
        try:
            for command in step_config["commands"]:
                logger.info(f"Executing command: {command}")

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

    def _generate_setup_report(self):
        """Generate setup report"""
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
        report_file = f"logs/nexus/local_dev_setup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Setup report saved to {report_file}")

        # Print summary
        print("\n" + "=" * 60)
        print("LOCAL DEVELOPMENT SETUP REPORT")
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
        print("LOCAL DEVELOPMENT SETUP COMPLETED")
        print("=" * 60)


def main():
    """Main entry point"""
    setup = LocalDevSetup()
    success = setup.setup_local_dev()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
