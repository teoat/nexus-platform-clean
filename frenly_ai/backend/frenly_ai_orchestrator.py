#!/usr/bin/env python3
"""
NEXUS Platform - Frenly AI Automation Orchestrator
Main orchestrator that coordinates all Frenly AI automation components
"""

import asyncio
import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import aiohttp
import yaml
from cicd_pipeline import CICDPipeline
from security_compliance import SecurityComplianceAutomation
from ssot_integration import SSOTIntegrationLayer
# Import all the automation components
from ssot_operator import FrenlyAISSOTOperator

from monitoring import MonitoringSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AutomationConfig:
    """Configuration for Frenly AI automation"""

    name: str
    version: str
    environment: str
    ssot_registry_url: str
    ssot_api_key: str
    pipeline_config_path: str
    monitoring_config: Dict[str, Any]
    security_config: Dict[str, Any]
    notification_config: Dict[str, Any]
    auto_deploy: bool
    auto_scale: bool
    auto_heal: bool
    max_concurrent_operations: int
    operation_timeout: int
    retry_attempts: int
    retry_delay: int


@dataclass
class AutomationStatus:
    """Status of automation system"""

    running: bool
    components: Dict[str, bool]
    last_health_check: datetime
    total_operations: int
    successful_operations: int
    failed_operations: int
    active_operations: int
    performance_metrics: Dict[str, Any]
    alerts: List[Dict[str, Any]]


class FrenlyAIAutomationOrchestrator:
    """
    Frenly AI Automation Orchestrator
    Coordinates all automation components:
    - SSOT Operator
    - SSOT Integration Layer
    - CI/CD Pipeline
    - Monitoring System
    - Security & Compliance
    - Auto-deployment
    - Auto-scaling
    - Auto-healing
    """

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        self.status = AutomationStatus(
            running=False,
            components={},
            last_health_check=datetime.now(timezone.utc),
            total_operations=0,
            successful_operations=0,
            failed_operations=0,
            active_operations=0,
            performance_metrics={},
            alerts=[],
        )

        # Initialize components
        self.ssot_operator = None
        self.ssot_integration = None
        self.cicd_pipeline = None
        self.monitoring_system = None
        self.security_system = None

        # Operation tracking
        self.active_operations = {}
        self.operation_history = []

        # Performance tracking
        self.performance_data = {
            "start_time": datetime.now(timezone.utc),
            "operations_per_minute": 0,
            "average_operation_duration": 0.0,
            "error_rate": 0.0,
        }

    def _load_config(self) -> AutomationConfig:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, "r") as f:
                config_data = yaml.safe_load(f)

            return AutomationConfig(
                name=config_data.get("name", "frenly-ai-automation"),
                version=config_data.get("version", "1.0.0"),
                environment=config_data.get("environment", "production"),
                ssot_registry_url=config_data.get(
                    "ssot_registry_url", "http://localhost:8000"
                ),
                ssot_api_key=config_data.get("ssot_api_key", ""),
                pipeline_config_path=config_data.get(
                    "pipeline_config_path", "pipeline-config.yaml"
                ),
                monitoring_config=config_data.get("monitoring", {}),
                security_config=config_data.get("security", {}),
                notification_config=config_data.get("notifications", {}),
                auto_deploy=config_data.get("auto_deploy", True),
                auto_scale=config_data.get("auto_scale", True),
                auto_heal=config_data.get("auto_heal", True),
                max_concurrent_operations=config_data.get(
                    "max_concurrent_operations", 10
                ),
                operation_timeout=config_data.get("operation_timeout", 300),
                retry_attempts=config_data.get("retry_attempts", 3),
                retry_delay=config_data.get("retry_delay", 5),
            )
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            # Return default config
            return AutomationConfig(
                name="frenly-ai-automation",
                version="1.0.0",
                environment="production",
                ssot_registry_url="http://localhost:8000",
                ssot_api_key="",
                pipeline_config_path="pipeline-config.yaml",
                monitoring_config={},
                security_config={},
                notification_config={},
                auto_deploy=True,
                auto_scale=True,
                auto_heal=True,
                max_concurrent_operations=10,
                operation_timeout=300,
                retry_attempts=3,
                retry_delay=5,
            )

    async def initialize(self) -> bool:
        """
        Initialize all automation components
        """
        logger.info("Initializing Frenly AI Automation Orchestrator")

        try:
            # Initialize SSOT Operator
            logger.info("Initializing SSOT Operator")
            self.ssot_operator = FrenlyAISSOTOperator(
                ssot_registry_url=self.config.ssot_registry_url,
                api_key=self.config.ssot_api_key,
            )
            await self.ssot_operator.initialize()
            self.status.components["ssot_operator"] = True

            # Initialize SSOT Integration Layer
            logger.info("Initializing SSOT Integration Layer")
            self.ssot_integration = SSOTIntegrationLayer(
                ssot_registry_url=self.config.ssot_registry_url,
                api_key=self.config.ssot_api_key,
            )
            self.status.components["ssot_integration"] = True

            # Initialize CI/CD Pipeline
            logger.info("Initializing CI/CD Pipeline")
            self.cicd_pipeline = CICDPipeline(
                config_path=self.config.pipeline_config_path,
                ssot_integration=self.ssot_integration,
            )
            self.status.components["cicd_pipeline"] = True

            # Initialize Monitoring System
            logger.info("Initializing Monitoring System")
            self.monitoring_system = MonitoringSystem(self.config.monitoring_config)
            await self.monitoring_system.start()
            self.status.components["monitoring"] = True

            # Initialize Security & Compliance System
            logger.info("Initializing Security & Compliance System")
            self.security_system = SecurityComplianceAutomation(
                self.config.security_config
            )
            self.status.components["security"] = True

            # Start background tasks
            asyncio.create_task(self._health_check_loop())
            asyncio.create_task(self._performance_monitoring_loop())
            asyncio.create_task(self._auto_healing_loop())

            self.status.running = True
            logger.info("Frenly AI Automation Orchestrator initialized successfully")

            return True

        except Exception as e:
            logger.error(f"Failed to initialize automation orchestrator: {e}")
            return False

    async def shutdown(self):
        """
        Shutdown all automation components
        """
        logger.info("Shutting down Frenly AI Automation Orchestrator")

        try:
            self.status.running = False

            # Stop monitoring system
            if self.monitoring_system:
                await self.monitoring_system.stop()

            # Cancel active operations
            for operation_id in list(self.active_operations.keys()):
                await self._cancel_operation(operation_id)

            logger.info("Frenly AI Automation Orchestrator shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    async def execute_operation(
        self, operation_type: str, parameters: Dict[str, Any], priority: int = 1
    ) -> str:
        """
        Execute an automation operation
        """
        operation_id = f"op_{int(time.time())}_{operation_type}"

        # Check if we can start new operations
        if len(self.active_operations) >= self.config.max_concurrent_operations:
            raise Exception("Maximum concurrent operations reached")

        logger.info(f"Starting operation {operation_id}: {operation_type}")

        try:
            # Create operation context
            operation_context = {
                "id": operation_id,
                "type": operation_type,
                "parameters": parameters,
                "priority": priority,
                "start_time": datetime.now(timezone.utc),
                "status": "running",
                "retry_count": 0,
            }

            # Add to active operations
            self.active_operations[operation_id] = operation_context

            # Update status
            self.status.active_operations = len(self.active_operations)
            self.status.total_operations += 1

            # Execute operation based on type
            result = await self._execute_operation_by_type(operation_type, parameters)

            # Mark as successful
            operation_context["status"] = "success"
            operation_context["end_time"] = datetime.now(timezone.utc)
            operation_context["result"] = result

            self.status.successful_operations += 1

            # Remove from active operations
            del self.active_operations[operation_id]
            self.status.active_operations = len(self.active_operations)

            # Add to history
            self.operation_history.append(operation_context)

            # Keep only last 1000 operations in history
            if len(self.operation_history) > 1000:
                self.operation_history = self.operation_history[-1000:]

            logger.info(f"Operation {operation_id} completed successfully")
            return operation_id

        except Exception as e:
            logger.error(f"Operation {operation_id} failed: {e}")

            # Mark as failed
            operation_context["status"] = "failed"
            operation_context["end_time"] = datetime.now(timezone.utc)
            operation_context["error"] = str(e)

            self.status.failed_operations += 1

            # Remove from active operations
            if operation_id in self.active_operations:
                del self.active_operations[operation_id]
            self.status.active_operations = len(self.active_operations)

            # Add to history
            self.operation_history.append(operation_context)

            raise

    async def _execute_operation_by_type(
        self, operation_type: str, parameters: Dict[str, Any]
    ) -> Any:
        """Execute operation based on type"""
        if operation_type == "ssot_query":
            return await self._execute_ssot_query(parameters)
        elif operation_type == "ssot_change_proposal":
            return await self._execute_ssot_change_proposal(parameters)
        elif operation_type == "cicd_pipeline":
            return await self._execute_cicd_pipeline(parameters)
        elif operation_type == "security_scan":
            return await self._execute_security_scan(parameters)
        elif operation_type == "compliance_check":
            return await self._execute_compliance_check(parameters)
        elif operation_type == "auto_deploy":
            return await self._execute_auto_deploy(parameters)
        elif operation_type == "auto_scale":
            return await self._execute_auto_scale(parameters)
        elif operation_type == "health_check":
            return await self._execute_health_check(parameters)
        else:
            raise ValueError(f"Unknown operation type: {operation_type}")

    async def _execute_ssot_query(self, parameters: Dict[str, Any]) -> Any:
        """Execute SSOT query operation"""
        if not self.ssot_operator:
            raise Exception("SSOT Operator not initialized")

        query = parameters.get("query")
        context = parameters.get("context", "default")

        return await self.ssot_operator.query(query, context)

    async def _execute_ssot_change_proposal(self, parameters: Dict[str, Any]) -> Any:
        """Execute SSOT change proposal operation"""
        if not self.ssot_operator:
            raise Exception("SSOT Operator not initialized")

        change_type = parameters.get("change_type")
        target = parameters.get("target")
        changes = parameters.get("changes", [])
        context = parameters.get("context", "default")

        return await self.ssot_operator.propose_changes(
            change_type, target, changes, context
        )

    async def _execute_cicd_pipeline(self, parameters: Dict[str, Any]) -> Any:
        """Execute CI/CD pipeline operation"""
        if not self.cicd_pipeline:
            raise Exception("CI/CD Pipeline not initialized")

        trigger = parameters.get("trigger", "manual")
        branch = parameters.get("branch", "main")
        commit_sha = parameters.get("commit_sha")

        return await self.cicd_pipeline.run_pipeline(trigger, branch, commit_sha)

    async def _execute_security_scan(self, parameters: Dict[str, Any]) -> Any:
        """Execute security scan operation"""
        if not self.security_system:
            raise Exception("Security System not initialized")

        scan_type = parameters.get("scan_type", "code")
        target = parameters.get("target")
        options = parameters.get("options", {})

        return await self.security_system.run_security_scan(scan_type, target, options)

    async def _execute_compliance_check(self, parameters: Dict[str, Any]) -> Any:
        """Execute compliance check operation"""
        if not self.security_system:
            raise Exception("Security System not initialized")

        target = parameters.get("target")

        return await self.security_system._run_compliance_checks(target)

    async def _execute_auto_deploy(self, parameters: Dict[str, Any]) -> Any:
        """Execute auto-deployment operation"""
        if not self.cicd_pipeline:
            raise Exception("CI/CD Pipeline not initialized")

        # Check if auto-deploy is enabled
        if not self.config.auto_deploy:
            return {"status": "disabled", "message": "Auto-deploy is disabled"}

        # Trigger deployment pipeline
        return await self.cicd_pipeline.run_pipeline("auto_deploy", "main")

    async def _execute_auto_scale(self, parameters: Dict[str, Any]) -> Any:
        """Execute auto-scaling operation"""
        if not self.config.auto_scale:
            return {"status": "disabled", "message": "Auto-scale is disabled"}

        # This would implement actual auto-scaling logic
        # For now, return placeholder
        return {
            "status": "not_implemented",
            "message": "Auto-scaling not yet implemented",
        }

    async def _execute_health_check(self, parameters: Dict[str, Any]) -> Any:
        """Execute health check operation"""
        if not self.monitoring_system:
            raise Exception("Monitoring System not initialized")

        return self.monitoring_system.get_health_status()

    async def _cancel_operation(self, operation_id: str):
        """Cancel an active operation"""
        if operation_id in self.active_operations:
            operation = self.active_operations[operation_id]
            operation["status"] = "cancelled"
            operation["end_time"] = datetime.now(timezone.utc)

            # Remove from active operations
            del self.active_operations[operation_id]
            self.status.active_operations = len(self.active_operations)

            # Add to history
            self.operation_history.append(operation)

            logger.info(f"Operation {operation_id} cancelled")

    async def _health_check_loop(self):
        """Background health check loop"""
        while self.status.running:
            try:
                await self._perform_health_check()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(30)

    async def _perform_health_check(self):
        """Perform comprehensive health check"""
        try:
            self.status.last_health_check = datetime.now(timezone.utc)

            # Check component health
            component_health = {}

            if self.ssot_operator:
                component_health[
                    "ssot_operator"
                ] = await self.ssot_operator.health_check()
            else:
                component_health["ssot_operator"] = False

            if self.ssot_integration:
                component_health["ssot_integration"] = True  # Simplified check
            else:
                component_health["ssot_integration"] = False

            if self.cicd_pipeline:
                component_health["cicd_pipeline"] = True  # Simplified check
            else:
                component_health["cicd_pipeline"] = False

            if self.monitoring_system:
                health_status = self.monitoring_system.get_health_status()
                component_health["monitoring"] = (
                    health_status.get("status") == "healthy"
                )
            else:
                component_health["monitoring"] = False

            if self.security_system:
                component_health["security"] = True  # Simplified check
            else:
                component_health["security"] = False

            # Update component status
            self.status.components = component_health

            # Check for alerts
            if self.monitoring_system:
                metrics = self.monitoring_system.get_metrics_summary()
                self.status.performance_metrics = metrics

                # Check for critical alerts
                if metrics.get("alerts", {}).get("active", 0) > 0:
                    self.status.alerts.append(
                        {
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "level": "warning",
                            "message": f"{metrics['alerts']['active']} active alerts",
                        }
                    )

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self.status.alerts.append(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "level": "error",
                    "message": f"Health check failed: {e}",
                }
            )

    async def _performance_monitoring_loop(self):
        """Background performance monitoring loop"""
        while self.status.running:
            try:
                await self._update_performance_metrics()
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"Performance monitoring loop error: {e}")
                await asyncio.sleep(60)

    async def _update_performance_metrics(self):
        """Update performance metrics"""
        try:
            current_time = datetime.now(timezone.utc)
            uptime = (
                current_time - self.performance_data["start_time"]
            ).total_seconds()

            # Calculate operations per minute
            if uptime > 0:
                self.performance_data[
                    "operations_per_minute"
                ] = self.status.total_operations / (uptime / 60)

            # Calculate error rate
            if self.status.total_operations > 0:
                self.performance_data["error_rate"] = (
                    self.status.failed_operations / self.status.total_operations
                )

            # Calculate average operation duration
            if self.operation_history:
                durations = []
                for op in self.operation_history:
                    if op.get("start_time") and op.get("end_time"):
                        duration = (op["end_time"] - op["start_time"]).total_seconds()
                        durations.append(duration)

                if durations:
                    self.performance_data["average_operation_duration"] = sum(
                        durations
                    ) / len(durations)

        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")

    async def _auto_healing_loop(self):
        """Background auto-healing loop"""
        while self.status.running:
            try:
                if self.config.auto_heal:
                    await self._perform_auto_healing()
                await asyncio.sleep(120)  # Check every 2 minutes
            except Exception as e:
                logger.error(f"Auto-healing loop error: {e}")
                await asyncio.sleep(120)

    async def _perform_auto_healing(self):
        """Perform auto-healing actions"""
        try:
            # Check for failed operations that can be retried
            for operation in self.operation_history[-100:]:  # Check last 100 operations
                if (
                    operation.get("status") == "failed"
                    and operation.get("retry_count", 0) < self.config.retry_attempts
                ):
                    # Retry the operation
                    await self._retry_operation(operation)

            # Check for component health issues
            unhealthy_components = [
                name for name, healthy in self.status.components.items() if not healthy
            ]

            if unhealthy_components:
                logger.warning(f"Unhealthy components detected: {unhealthy_components}")
                # This would implement actual healing logic
                # For now, just log the issue

        except Exception as e:
            logger.error(f"Auto-healing failed: {e}")

    async def _retry_operation(self, operation: Dict[str, Any]):
        """Retry a failed operation"""
        try:
            operation_id = operation["id"]
            operation_type = operation["type"]
            parameters = operation["parameters"]

            logger.info(f"Retrying operation {operation_id}")

            # Increment retry count
            operation["retry_count"] = operation.get("retry_count", 0) + 1

            # Execute the operation again
            result = await self._execute_operation_by_type(operation_type, parameters)

            # Update operation status
            operation["status"] = "success"
            operation["end_time"] = datetime.now(timezone.utc)
            operation["result"] = result

            logger.info(f"Operation {operation_id} retried successfully")

        except Exception as e:
            logger.error(f"Failed to retry operation {operation['id']}: {e}")
            operation["status"] = "failed"
            operation["end_time"] = datetime.now(timezone.utc)
            operation["error"] = str(e)

    def get_status(self) -> Dict[str, Any]:
        """Get current automation status"""
        return {
            "running": self.status.running,
            "components": self.status.components,
            "last_health_check": self.status.last_health_check.isoformat(),
            "total_operations": self.status.total_operations,
            "successful_operations": self.status.successful_operations,
            "failed_operations": self.status.failed_operations,
            "active_operations": self.status.active_operations,
            "performance_metrics": self.performance_data,
            "alerts": self.status.alerts,
            "config": asdict(self.config),
        }

    def get_operation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get operation history"""
        return self.operation_history[-limit:]

    def get_active_operations(self) -> List[Dict[str, Any]]:
        """Get active operations"""
        return list(self.active_operations.values())


# Example usage and testing
async def main():
    """
    Example usage of FrenlyAIAutomationOrchestrator
    """
    # Create sample configuration
    config_data = {
        "name": "frenly-ai-automation",
        "version": "1.0.0",
        "environment": "production",
        "ssot_registry_url": "http://localhost:8000",
        "ssot_api_key": "test-api-key",
        "pipeline_config_path": "pipeline-config.yaml",
        "monitoring": {"collection_interval": 10, "alert_rules": []},
        "security": {"security_policies": []},
        "notifications": {"enabled": True},
        "auto_deploy": True,
        "auto_scale": True,
        "auto_heal": True,
        "max_concurrent_operations": 10,
        "operation_timeout": 300,
        "retry_attempts": 3,
        "retry_delay": 5,
    }

    # Save config to file
    config_file = "automation-config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    # Initialize orchestrator
    orchestrator = FrenlyAIAutomationOrchestrator(config_file)

    try:
        # Initialize all components
        success = await orchestrator.initialize()
        if not success:
            print("Failed to initialize orchestrator")
            return

        print("Orchestrator initialized successfully")

        # Get status
        status = orchestrator.get_status()
        print(f"Status: {status}")

        # Execute some operations
        try:
            # SSOT query operation
            op1 = await orchestrator.execute_operation(
                "ssot_query", {"query": "user_management", "context": "frenly_ai"}
            )
            print(f"SSOT query operation: {op1}")

            # Health check operation
            op2 = await orchestrator.execute_operation("health_check", {})
            print(f"Health check operation: {op2}")

        except Exception as e:
            print(f"Operation failed: {e}")

        # Get operation history
        history = orchestrator.get_operation_history(10)
        print(f"Operation history: {len(history)} operations")

        # Wait a bit
        await asyncio.sleep(5)

    finally:
        # Shutdown orchestrator
        await orchestrator.shutdown()
        print("Orchestrator shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
