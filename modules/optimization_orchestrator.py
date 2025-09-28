#!/usr/bin/env python3
"""
Optimization Orchestrator Module - NEXUS Platform
Handles optimization triggers, thresholds, and flow logic
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .background_optimizer import BackgroundOptimizer
from .base_module import BaseModule, ModuleResult
from .dependency_optimizer import DependencyOptimizer
from .file_optimizer import FileOptimizer
from .repo_pruner import RepoPruner

logger = logging.getLogger(__name__)


@dataclass
class OptimizationThreshold:
    """Optimization threshold configuration"""

    trigger: str
    threshold_value: float
    unit: str  # "MB", "GB", "count", "percentage"
    action: str
    priority: int = 1
    enabled: bool = True


@dataclass
class OptimizationEvent:
    """Optimization event"""

    event_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    severity: str = "info"  # "info", "warning", "critical"


class OptimizationOrchestrator(BaseModule):
    """Optimization Orchestrator - Handles optimization triggers and flow logic"""

    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        super().__init__(base_path)
        self.thresholds = {}
        self.event_history = []
        self.optimization_stats = {}

        # Initialize sub-modules
        self.file_optimizer = FileOptimizer(base_path)
        self.dependency_optimizer = DependencyOptimizer(base_path)
        self.repo_pruner = RepoPruner(base_path)
        self.background_optimizer = BackgroundOptimizer(base_path)

        # Load configuration
        self._load_optimization_config()

        # Convert dict configs to proper objects
        self._convert_config_objects()

    def _load_optimization_config(self):
        """Load optimization configuration from config file"""
        config_path = self.base_path / "config" / "optimization_thresholds.yaml"
        if config_path.exists():
            import yaml

            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                self.thresholds = config.get("thresholds", {})
        else:
            # Default configuration
            self._create_default_thresholds()

    def _create_default_thresholds(self):
        """Create default optimization thresholds"""
        self.thresholds = {
            "repo_size_growth": [
                OptimizationThreshold("repo_size", 500, "MB", "compress_assets", 1),
                OptimizationThreshold("repo_size", 1000, "MB", "prune_dependencies", 2),
                OptimizationThreshold(
                    "repo_size", 2000, "MB", "archive_old_releases", 3
                ),
            ],
            "file_upload": [
                OptimizationThreshold(
                    "file_size", 100, "MB", "lock_file_require_approval", 1
                ),
                OptimizationThreshold("file_size", 50, "MB", "auto_compress", 2),
            ],
            "dependency_tree": [
                OptimizationThreshold(
                    "dependency_count", 200, "count", "suggest_slimming", 1
                ),
                OptimizationThreshold(
                    "dependency_duplication", 3, "count", "force_ssot_version", 2
                ),
            ],
            "build_frequency": [
                OptimizationThreshold("old_builds", 10, "count", "auto_archive", 1)
            ],
        }

    async def get_available_functions(self) -> List[str]:
        """Return list of available functions in this module"""
        return [
            "handle_event",
            "check_thresholds",
            "run_optimization_flow",
            "get_optimization_status",
            "generate_optimization_report",
            "configure_thresholds",
            "get_event_history",
        ]

    async def get_module_info(self) -> Dict[str, Any]:
        """Return module information and capabilities"""
        return {
            "name": "OptimizationOrchestrator",
            "version": "1.0",
            "description": "Handles optimization triggers, thresholds, and flow logic",
            "functions": await self.get_available_functions(),
            "dependencies": [
                "file_optimizer",
                "dependency_optimizer",
                "repo_pruner",
                "background_optimizer",
            ],
            "output_files": [
                "reports/optimization_orchestration_report.json",
                "reports/event_history.json",
            ],
        }

    async def handle_event(
        self, event_type: str, payload: Dict[str, Any]
    ) -> ModuleResult:
        """Handle optimization events and trigger appropriate actions"""
        try:
            logger.info(f"Handling event: {event_type}")

            # Create event
            event = OptimizationEvent(
                event_type=event_type, payload=payload, timestamp=datetime.now()
            )

            # Log event
            self.event_history.append(event)

            # Check thresholds and determine actions
            actions = await self._check_thresholds_for_event(event)

            # Execute actions
            results = []
            for action in actions:
                try:
                    result = await self._execute_optimization_action(action, event)
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.error(f"Error executing action {action}: {e}")
                    results.append(
                        {"action": action, "status": "failed", "error": str(e)}
                    )

            return ModuleResult(
                success=True,
                data={
                    "event_type": event_type,
                    "payload": payload,
                    "actions_triggered": len(actions),
                    "results": results,
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error handling event {event_type}: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _check_thresholds_for_event(self, event: OptimizationEvent) -> List[str]:
        """Check thresholds for event and return actions to take"""
        actions = []

        if event.event_type == "repo_growth":
            size_mb = event.payload.get("size", 0) / (1024 * 1024)

            for threshold in self.thresholds.get("repo_size_growth", []):
                if threshold.enabled and self._evaluate_threshold(size_mb, threshold):
                    actions.append(threshold.action)

        elif event.event_type == "file_upload":
            file_size_mb = event.payload.get("file_size", 0) / (1024 * 1024)

            for threshold in self.thresholds.get("file_upload", []):
                if threshold.enabled and self._evaluate_threshold(
                    file_size_mb, threshold
                ):
                    actions.append(threshold.action)

        elif event.event_type == "dependency_change":
            dep_count = event.payload.get("total_libs", 0)

            for threshold in self.thresholds.get("dependency_tree", []):
                if threshold.enabled and self._evaluate_threshold(dep_count, threshold):
                    actions.append(threshold.action)

        elif event.event_type == "build_complete":
            old_builds = event.payload.get("old_builds", 0)

            for threshold in self.thresholds.get("build_frequency", []):
                if threshold.enabled and self._evaluate_threshold(
                    old_builds, threshold
                ):
                    actions.append(threshold.action)

        return actions

    def _evaluate_threshold(
        self, value: float, threshold: OptimizationThreshold
    ) -> bool:
        """Evaluate if threshold is exceeded"""
        if threshold.unit == "MB":
            return value > threshold.threshold_value
        elif threshold.unit == "GB":
            return value > threshold.threshold_value * 1024
        elif threshold.unit == "count":
            return value > threshold.threshold_value
        elif threshold.unit == "percentage":
            return value > threshold.threshold_value
        else:
            return False

    async def _execute_optimization_action(
        self, action: str, event: OptimizationEvent
    ) -> Optional[Dict[str, Any]]:
        """Execute optimization action"""
        try:
            if action == "compress_assets":
                result = await self.file_optimizer.compress_assets(threshold_mb=5)
                return {
                    "action": action,
                    "status": "success" if result.success else "failed",
                    "data": result.data,
                    "error": result.error,
                }

            elif action == "prune_dependencies":
                result = await self.dependency_optimizer.prune_unused_libs()
                return {
                    "action": action,
                    "status": "success" if result.success else "failed",
                    "data": result.data,
                    "error": result.error,
                }

            elif action == "archive_old_releases":
                result = await self.repo_pruner.archive_old_releases(keep_last=3)
                return {
                    "action": action,
                    "status": "success" if result.success else "failed",
                    "data": result.data,
                    "error": result.error,
                }

            elif action == "lock_file_require_approval":
                # This would typically lock the file and notify human
                return {
                    "action": action,
                    "status": "pending_approval",
                    "message": "Large file uploaded, manual approval needed",
                    "file_path": event.payload.get("file_path", "unknown"),
                }

            elif action == "auto_compress":
                result = await self.file_optimizer.compress_assets(
                    files=[event.payload.get("file_path")]
                )
                return {
                    "action": action,
                    "status": "success" if result.success else "failed",
                    "data": result.data,
                    "error": result.error,
                }

            elif action == "suggest_slimming":
                result = await self.dependency_optimizer.analyze_dependency_graph()
                return {
                    "action": action,
                    "status": "success" if result.success else "failed",
                    "data": result.data,
                    "error": result.error,
                }

            elif action == "force_ssot_version":
                result = await self.dependency_optimizer.deduplicate_versions()
                return {
                    "action": action,
                    "status": "success" if result.success else "failed",
                    "data": result.data,
                    "error": result.error,
                }

            elif action == "auto_archive":
                result = await self.repo_pruner.archive_old_releases(keep_last=5)
                return {
                    "action": action,
                    "status": "success" if result.success else "failed",
                    "data": result.data,
                    "error": result.error,
                }

            else:
                logger.warning(f"Unknown action: {action}")
                return None

        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
            return {"action": action, "status": "failed", "error": str(e)}

    async def check_thresholds(self, event_type: str = None) -> ModuleResult:
        """Check all thresholds and return current status"""
        try:
            logger.info(f"Checking thresholds for event type: {event_type}")

            threshold_status = {}

            if event_type is None:
                # Check all thresholds
                for category, thresholds in self.thresholds.items():
                    threshold_status[category] = []
                    for threshold in thresholds:
                        threshold_status[category].append(
                            {
                                "trigger": threshold.trigger,
                                "threshold_value": threshold.threshold_value,
                                "unit": threshold.unit,
                                "action": threshold.action,
                                "priority": threshold.priority,
                                "enabled": threshold.enabled,
                            }
                        )
            else:
                # Check specific event type
                if event_type in self.thresholds:
                    threshold_status[event_type] = []
                    for threshold in self.thresholds[event_type]:
                        threshold_status[event_type].append(
                            {
                                "trigger": threshold.trigger,
                                "threshold_value": threshold.threshold_value,
                                "unit": threshold.unit,
                                "action": threshold.action,
                                "priority": threshold.priority,
                                "enabled": threshold.enabled,
                            }
                        )

            return ModuleResult(
                success=True,
                data={"event_type": event_type, "thresholds": threshold_status},
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error checking thresholds: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def run_optimization_flow(self, flow_type: str = "full") -> ModuleResult:
        """Run complete optimization flow"""
        try:
            logger.info(f"Running optimization flow: {flow_type}")

            flow_results = []

            if flow_type == "full":
                # Run all optimization modules
                modules = [
                    ("file_optimizer", "compress_assets"),
                    ("file_optimizer", "minify_code"),
                    ("dependency_optimizer", "prune_unused_libs"),
                    ("dependency_optimizer", "deduplicate_versions"),
                    ("repo_pruner", "clear_temp_files"),
                    ("repo_pruner", "cleanup_build_artifacts"),
                ]

                for module_name, function_name in modules:
                    try:
                        if module_name == "file_optimizer":
                            result = await self.file_optimizer.execute_function(
                                function_name
                            )
                        elif module_name == "dependency_optimizer":
                            result = await self.dependency_optimizer.execute_function(
                                function_name
                            )
                        elif module_name == "repo_pruner":
                            result = await self.repo_pruner.execute_function(
                                function_name
                            )

                        flow_results.append(
                            {
                                "module": module_name,
                                "function": function_name,
                                "status": "success" if result.success else "failed",
                                "data": result.data,
                                "error": result.error,
                            }
                        )

                    except Exception as e:
                        logger.error(
                            f"Error running {module_name}.{function_name}: {e}"
                        )
                        flow_results.append(
                            {
                                "module": module_name,
                                "function": function_name,
                                "status": "failed",
                                "error": str(e),
                            }
                        )

            elif flow_type == "quick":
                # Run quick optimization (only critical tasks)
                quick_modules = [
                    ("file_optimizer", "compress_assets"),
                    ("repo_pruner", "clear_temp_files"),
                ]

                for module_name, function_name in quick_modules:
                    try:
                        if module_name == "file_optimizer":
                            result = await self.file_optimizer.execute_function(
                                function_name
                            )
                        elif module_name == "repo_pruner":
                            result = await self.repo_pruner.execute_function(
                                function_name
                            )

                        flow_results.append(
                            {
                                "module": module_name,
                                "function": function_name,
                                "status": "success" if result.success else "failed",
                                "data": result.data,
                                "error": result.error,
                            }
                        )

                    except Exception as e:
                        logger.error(
                            f"Error running {module_name}.{function_name}: {e}"
                        )
                        flow_results.append(
                            {
                                "module": module_name,
                                "function": function_name,
                                "status": "failed",
                                "error": str(e),
                            }
                        )

            return ModuleResult(
                success=True,
                data={
                    "flow_type": flow_type,
                    "modules_executed": len(flow_results),
                    "successful_modules": len(
                        [r for r in flow_results if r["status"] == "success"]
                    ),
                    "results": flow_results,
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error running optimization flow: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def get_optimization_status(self) -> ModuleResult:
        """Get current optimization status"""
        try:
            status = {
                "orchestrator_running": True,
                "thresholds_configured": len(self.thresholds),
                "events_processed": len(self.event_history),
                "recent_events": self.event_history[-10:] if self.event_history else [],
                "optimization_stats": self.optimization_stats,
            }

            return ModuleResult(success=True, data=status, timestamp=datetime.now())

        except Exception as e:
            logger.error(f"Error getting optimization status: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def generate_optimization_report(self) -> ModuleResult:
        """Generate comprehensive optimization report"""
        try:
            logger.info("Generating optimization report")

            report = {
                "generated_at": datetime.now().isoformat(),
                "thresholds": {
                    category: [
                        {
                            "trigger": threshold.trigger,
                            "threshold_value": threshold.threshold_value,
                            "unit": threshold.unit,
                            "action": threshold.action,
                            "priority": threshold.priority,
                            "enabled": threshold.enabled,
                        }
                        for threshold in thresholds
                    ]
                    for category, thresholds in self.thresholds.items()
                },
                "event_history": [
                    {
                        "event_type": event.event_type,
                        "payload": event.payload,
                        "timestamp": event.timestamp.isoformat(),
                        "severity": event.severity,
                    }
                    for event in self.event_history
                ],
                "optimization_stats": self.optimization_stats,
                "recommendations": await self._generate_optimization_recommendations(),
            }

            # Save report
            report_path = (
                self.base_path / "reports" / "optimization_orchestration_report.json"
            )
            report_path.parent.mkdir(parents=True, exist_ok=True)

            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)

            return ModuleResult(
                success=True,
                data={
                    "report_path": str(report_path),
                    "thresholds_configured": len(self.thresholds),
                    "events_processed": len(self.event_history),
                    "recommendations_count": len(report["recommendations"]),
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error generating optimization report: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _generate_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        recommendations = []

        # Analyze event history for patterns
        if self.event_history:
            # Check for frequent events
            event_counts = {}
            for event in self.event_history:
                event_counts[event.event_type] = (
                    event_counts.get(event.event_type, 0) + 1
                )

            for event_type, count in event_counts.items():
                if count > 5:  # More than 5 occurrences
                    recommendations.append(
                        {
                            "type": "frequent_event",
                            "event_type": event_type,
                            "count": count,
                            "action": f"Consider adjusting thresholds for {event_type} events",
                        }
                    )

        # Check threshold effectiveness
        for category, thresholds in self.thresholds.items():
            for threshold in thresholds:
                if not threshold.enabled:
                    recommendations.append(
                        {
                            "type": "disabled_threshold",
                            "category": category,
                            "threshold": threshold.trigger,
                            "action": f"Consider enabling {threshold.trigger} threshold",
                        }
                    )

        return recommendations

    def _convert_config_objects(self):
        """Convert dict configs to proper objects"""
        # Convert thresholds if they're dicts
        if isinstance(self.thresholds, dict):
            converted_thresholds = {}
            for category, threshold_list in self.thresholds.items():
                if isinstance(threshold_list, list):
                    converted_list = []
                    for threshold_data in threshold_list:
                        if isinstance(threshold_data, dict):
                            converted_list.append(
                                OptimizationThreshold(
                                    trigger=threshold_data.get("trigger", ""),
                                    threshold_value=threshold_data.get(
                                        "threshold_value", 0
                                    ),
                                    unit=threshold_data.get("unit", "MB"),
                                    action=threshold_data.get("action", ""),
                                    priority=threshold_data.get("priority", 1),
                                    enabled=threshold_data.get("enabled", True),
                                )
                            )
                        else:
                            converted_list.append(threshold_data)
                    converted_thresholds[category] = converted_list
                else:
                    converted_thresholds[category] = threshold_list
            self.thresholds = converted_thresholds

    async def configure_thresholds(
        self, category: str, thresholds: List[Dict[str, Any]]
    ) -> ModuleResult:
        """Configure optimization thresholds"""
        try:
            logger.info(f"Configuring thresholds for category: {category}")

            # Convert threshold dictionaries to OptimizationThreshold objects
            threshold_objects = []
            for threshold_data in thresholds:
                threshold = OptimizationThreshold(
                    trigger=threshold_data.get("trigger", ""),
                    threshold_value=threshold_data.get("threshold_value", 0),
                    unit=threshold_data.get("unit", "MB"),
                    action=threshold_data.get("action", ""),
                    priority=threshold_data.get("priority", 1),
                    enabled=threshold_data.get("enabled", True),
                )
                threshold_objects.append(threshold)

            # Update thresholds
            self.thresholds[category] = threshold_objects

            # Save configuration
            await self._save_optimization_config()

            return ModuleResult(
                success=True,
                data={
                    "category": category,
                    "thresholds_configured": len(threshold_objects),
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error configuring thresholds: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _save_optimization_config(self):
        """Save optimization configuration to file"""
        try:
            config_path = self.base_path / "config" / "optimization_thresholds.yaml"
            config_path.parent.mkdir(parents=True, exist_ok=True)

            import yaml

            config = {
                "thresholds": {
                    category: [
                        {
                            "trigger": threshold.trigger,
                            "threshold_value": threshold.threshold_value,
                            "unit": threshold.unit,
                            "action": threshold.action,
                            "priority": threshold.priority,
                            "enabled": threshold.enabled,
                        }
                        for threshold in thresholds
                    ]
                    for category, thresholds in self.thresholds.items()
                }
            }

            with open(config_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False)

        except Exception as e:
            logger.error(f"Error saving optimization config: {e}")


# Example usage and testing
async def main():
    """Test the Optimization Orchestrator Module"""
    orchestrator = OptimizationOrchestrator()

    # Test event handling
    result = await orchestrator.execute_function(
        "handle_event", event_type="repo_growth", payload={"size": 1500 * 1024 * 1024}
    )  # 1.5GB
    print(f"Event handling result: {result}")

    # Test threshold checking
    result = await orchestrator.execute_function("check_thresholds")
    print(f"Threshold checking result: {result}")

    # Test optimization flow
    result = await orchestrator.execute_function(
        "run_optimization_flow", flow_type="quick"
    )
    print(f"Optimization flow result: {result}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
