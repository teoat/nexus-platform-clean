#!/usr/bin/env python3
"""
Background Optimizer Module - NEXUS Platform
Handles continuous background optimization and scheduled maintenance
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import schedule

from .base_module import BaseModule, ModuleResult
from .dependency_optimizer import DependencyOptimizer
from .file_optimizer import FileOptimizer
from .repo_pruner import RepoPruner

logger = logging.getLogger(__name__)


@dataclass
class OptimizationSchedule:
    """Optimization schedule configuration"""

    interval: str  # "daily", "weekly", "monthly"
    time: str  # "02:00" for daily
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


@dataclass
class OptimizationTask:
    """Individual optimization task"""

    name: str
    module: str
    function: str
    parameters: Dict[str, Any]
    priority: int = 1
    enabled: bool = True


class BackgroundOptimizer(BaseModule):
    """Background Optimizer - Handles continuous optimization and scheduling"""

    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        super().__init__(base_path)
        self.schedules = {}
        self.tasks = []
        self.running = False
        self.optimization_history = []

        # Initialize sub-modules
        self.file_optimizer = FileOptimizer(base_path)
        self.dependency_optimizer = DependencyOptimizer(base_path)
        self.repo_pruner = RepoPruner(base_path)

        # Load configuration
        self._load_optimization_config()

        # Convert dict configs to proper objects
        self._convert_config_objects()

    def _load_optimization_config(self):
        """Load optimization configuration from config file"""
        config_path = self.base_path / "config" / "optimization_schedule.yaml"
        if config_path.exists():
            import yaml

            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                self.schedules = config.get("schedules", {})
                self.tasks = config.get("tasks", [])
        else:
            # Default configuration
            self._create_default_config()

    def _create_default_config(self):
        """Create default optimization configuration"""
        self.schedules = {
            "daily_cleanup": OptimizationSchedule(
                interval="daily", time="02:00", enabled=True
            ),
            "weekly_optimization": OptimizationSchedule(
                interval="weekly", time="03:00", enabled=True
            ),
            "monthly_deep_clean": OptimizationSchedule(
                interval="monthly", time="04:00", enabled=True
            ),
        }

    def _convert_config_objects(self):
        """Convert dict configs to proper objects"""
        # Convert schedules if they're dicts
        if isinstance(self.schedules, dict):
            converted_schedules = {}
            for name, schedule_data in self.schedules.items():
                if isinstance(schedule_data, dict):
                    converted_schedules[name] = OptimizationSchedule(
                        interval=schedule_data.get("interval", "daily"),
                        time=schedule_data.get("time", "02:00"),
                        enabled=schedule_data.get("enabled", True),
                        last_run=schedule_data.get("last_run"),
                        next_run=schedule_data.get("next_run"),
                    )
                else:
                    converted_schedules[name] = schedule_data
            self.schedules = converted_schedules

        # Convert tasks if they're dicts
        if isinstance(self.tasks, list):
            converted_tasks = []
            for task_data in self.tasks:
                if isinstance(task_data, dict):
                    converted_tasks.append(
                        OptimizationTask(
                            name=task_data.get("name", ""),
                            module=task_data.get("module", ""),
                            function=task_data.get("function", ""),
                            parameters=task_data.get("parameters", {}),
                            priority=task_data.get("priority", 1),
                            enabled=task_data.get("enabled", True),
                        )
                    )
                else:
                    converted_tasks.append(task_data)
            self.tasks = converted_tasks

        self.tasks = [
            OptimizationTask(
                name="temp_file_cleanup",
                module="repo_pruner",
                function="clear_temp_files",
                parameters={},
                priority=1,
            ),
            OptimizationTask(
                name="build_artifact_cleanup",
                module="repo_pruner",
                function="cleanup_build_artifacts",
                parameters={},
                priority=2,
            ),
            OptimizationTask(
                name="asset_compression",
                module="file_optimizer",
                function="compress_assets",
                parameters={"threshold_mb": 5},
                priority=3,
            ),
            OptimizationTask(
                name="dependency_optimization",
                module="dependency_optimizer",
                function="prune_unused_libs",
                parameters={},
                priority=4,
            ),
            OptimizationTask(
                name="code_minification",
                module="file_optimizer",
                function="minify_code",
                parameters={},
                priority=5,
            ),
        ]

    async def get_available_functions(self) -> List[str]:
        """Return list of available functions in this module"""
        return [
            "run_continuous_scan",
            "schedule_optimization",
            "run_scheduled_tasks",
            "start_background_optimizer",
            "stop_background_optimizer",
            "get_optimization_status",
            "generate_optimization_summary",
        ]

    async def get_module_info(self) -> Dict[str, Any]:
        """Return module information and capabilities"""
        return {
            "name": "BackgroundOptimizer",
            "version": "1.0",
            "description": "Handles continuous background optimization and scheduled maintenance",
            "functions": await self.get_available_functions(),
            "dependencies": ["file_optimizer", "dependency_optimizer", "repo_pruner"],
            "output_files": [
                "reports/optimization_summary.json",
                "reports/background_optimization_log.json",
            ],
        }

    async def run_continuous_scan(self, interval: str = "daily") -> ModuleResult:
        """Scheduled optimization run"""
        try:
            logger.info(f"Running continuous scan with interval: {interval}")

            # Determine which tasks to run based on interval
            tasks_to_run = self._get_tasks_for_interval(interval)

            results = []
            total_space_saved = 0
            total_files_processed = 0

            for task in tasks_to_run:
                try:
                    result = await self._execute_optimization_task(task)
                    if result:
                        results.append(result)
                        total_space_saved += result.get("space_saved", 0)
                        total_files_processed += result.get("files_processed", 0)

                except Exception as e:
                    logger.error(f"Error executing task {task.name}: {e}")
                    results.append(
                        {"task": task.name, "status": "failed", "error": str(e)}
                    )

            # Log optimization results
            await self._log_optimization_run(interval, results)

            return ModuleResult(
                success=True,
                data={
                    "interval": interval,
                    "tasks_executed": len(tasks_to_run),
                    "successful_tasks": len(
                        [r for r in results if r.get("status") == "success"]
                    ),
                    "total_space_saved": total_space_saved,
                    "total_files_processed": total_files_processed,
                    "results": results,
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error running continuous scan: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    def _get_tasks_for_interval(self, interval: str) -> List[OptimizationTask]:
        """Get tasks to run for specific interval"""
        if interval == "daily":
            return [task for task in self.tasks if task.priority <= 3 and task.enabled]
        elif interval == "weekly":
            return [task for task in self.tasks if task.priority <= 4 and task.enabled]
        elif interval == "monthly":
            return [task for task in self.tasks if task.enabled]
        else:
            return [task for task in self.tasks if task.enabled]

    async def _execute_optimization_task(
        self, task: OptimizationTask
    ) -> Optional[Dict[str, Any]]:
        """Execute a single optimization task"""
        try:
            # Get the appropriate module
            if task.module == "file_optimizer":
                module = self.file_optimizer
            elif task.module == "dependency_optimizer":
                module = self.dependency_optimizer
            elif task.module == "repo_pruner":
                module = self.repo_pruner
            else:
                logger.error(f"Unknown module: {task.module}")
                return None

            # Execute the function
            result = await module.execute_function(task.function, **task.parameters)

            return {
                "task": task.name,
                "module": task.module,
                "function": task.function,
                "status": "success" if result.success else "failed",
                "data": result.data,
                "error": result.error,
                "execution_time": result.execution_time,
            }

        except Exception as e:
            logger.error(f"Error executing task {task.name}: {e}")
            return {"task": task.name, "status": "failed", "error": str(e)}

    async def schedule_optimization(
        self, schedule_name: str, interval: str, time: str
    ) -> ModuleResult:
        """Schedule optimization tasks"""
        try:
            logger.info(
                f"Scheduling optimization: {schedule_name} - {interval} at {time}"
            )

            # Create schedule
            self.schedules[schedule_name] = OptimizationSchedule(
                interval=interval,
                time=time,
                enabled=True,
                next_run=self._calculate_next_run(interval, time),
            )

            # Save configuration
            await self._save_optimization_config()

            return ModuleResult(
                success=True,
                data={
                    "schedule_name": schedule_name,
                    "interval": interval,
                    "time": time,
                    "next_run": self.schedules[schedule_name].next_run.isoformat()
                    if self.schedules[schedule_name].next_run
                    else None,
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error scheduling optimization: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    def _calculate_next_run(self, interval: str, time: str) -> datetime:
        """Calculate next run time for schedule"""
        now = datetime.now()
        hour, minute = map(int, time.split(":"))

        if interval == "daily":
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
        elif interval == "weekly":
            # Run on Monday
            days_ahead = 0 - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )
        elif interval == "monthly":
            # Run on first day of next month
            if now.month == 12:
                next_run = now.replace(
                    year=now.year + 1,
                    month=1,
                    day=1,
                    hour=hour,
                    minute=minute,
                    second=0,
                    microsecond=0,
                )
            else:
                next_run = now.replace(
                    month=now.month + 1,
                    day=1,
                    hour=hour,
                    minute=minute,
                    second=0,
                    microsecond=0,
                )
        else:
            next_run = now + timedelta(hours=1)

        return next_run

    async def run_scheduled_tasks(self) -> ModuleResult:
        """Run all scheduled tasks that are due"""
        try:
            logger.info("Running scheduled tasks")

            now = datetime.now()
            tasks_run = []

            for schedule_name, schedule in self.schedules.items():
                if not schedule.enabled:
                    continue

                if schedule.next_run and now >= schedule.next_run:
                    # Run tasks for this schedule
                    interval = schedule.interval
                    tasks_to_run = self._get_tasks_for_interval(interval)

                    for task in tasks_to_run:
                        try:
                            result = await self._execute_optimization_task(task)
                            if result:
                                tasks_run.append(result)
                        except Exception as e:
                            logger.error(
                                f"Error running scheduled task {task.name}: {e}"
                            )

                    # Update next run time
                    schedule.last_run = now
                    schedule.next_run = self._calculate_next_run(
                        schedule.interval, schedule.time
                    )

            return ModuleResult(
                success=True,
                data={
                    "tasks_run": len(tasks_run),
                    "schedules_checked": len(self.schedules),
                    "results": tasks_run,
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error running scheduled tasks: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def start_background_optimizer(self) -> ModuleResult:
        """Start background optimizer daemon"""
        try:
            if self.running:
                return ModuleResult(
                    success=False,
                    data=None,
                    error="Background optimizer is already running",
                    timestamp=datetime.now(),
                )

            logger.info("Starting background optimizer")
            self.running = True

            # Start background task
            asyncio.create_task(self._background_loop())

            return ModuleResult(
                success=True,
                data={"status": "started", "running": self.running},
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error starting background optimizer: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def stop_background_optimizer(self) -> ModuleResult:
        """Stop background optimizer daemon"""
        try:
            logger.info("Stopping background optimizer")
            self.running = False

            return ModuleResult(
                success=True,
                data={"status": "stopped", "running": self.running},
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error stopping background optimizer: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _background_loop(self):
        """Background optimization loop"""
        while self.running:
            try:
                # Check for scheduled tasks
                await self.run_scheduled_tasks()

                # Wait for next check (every hour)
                await asyncio.sleep(3600)

            except Exception as e:
                logger.error(f"Error in background loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying

    async def get_optimization_status(self) -> ModuleResult:
        """Get current optimization status"""
        try:
            status = {
                "running": self.running,
                "schedules": len(self.schedules),
                "enabled_schedules": len(
                    [s for s in self.schedules.values() if s.enabled]
                ),
                "tasks": len(self.tasks),
                "enabled_tasks": len([t for t in self.tasks if t.enabled]),
                "last_optimization": self.optimization_history[-1]
                if self.optimization_history
                else None,
                "next_scheduled_run": min(
                    [s.next_run for s in self.schedules.values() if s.next_run],
                    default=None,
                ),
            }

            return ModuleResult(success=True, data=status, timestamp=datetime.now())

        except Exception as e:
            logger.error(f"Error getting optimization status: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def generate_optimization_summary(self) -> ModuleResult:
        """Generate comprehensive optimization summary"""
        try:
            logger.info("Generating optimization summary")

            summary = {
                "generated_at": datetime.now().isoformat(),
                "optimization_history": self.optimization_history,
                "schedules": {
                    name: {
                        "interval": schedule.interval,
                        "time": schedule.time,
                        "enabled": schedule.enabled,
                        "last_run": schedule.last_run.isoformat()
                        if schedule.last_run
                        else None,
                        "next_run": schedule.next_run.isoformat()
                        if schedule.next_run
                        else None,
                    }
                    for name, schedule in self.schedules.items()
                },
                "tasks": [
                    {
                        "name": task.name,
                        "module": task.module,
                        "function": task.function,
                        "priority": task.priority,
                        "enabled": task.enabled,
                    }
                    for task in self.tasks
                ],
                "statistics": await self._calculate_optimization_statistics(),
            }

            # Save summary
            summary_path = self.base_path / "reports" / "optimization_summary.json"
            summary_path.parent.mkdir(parents=True, exist_ok=True)

            with open(summary_path, "w") as f:
                json.dump(summary, f, indent=2)

            return ModuleResult(
                success=True,
                data={
                    "summary_path": str(summary_path),
                    "history_entries": len(self.optimization_history),
                    "schedules": len(self.schedules),
                    "tasks": len(self.tasks),
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error generating optimization summary: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _calculate_optimization_statistics(self) -> Dict[str, Any]:
        """Calculate optimization statistics"""
        stats = {
            "total_optimizations": len(self.optimization_history),
            "total_space_saved": 0,
            "total_files_processed": 0,
            "success_rate": 0,
        }

        if self.optimization_history:
            successful_runs = [
                run
                for run in self.optimization_history
                if run.get("status") == "success"
            ]
            stats["success_rate"] = len(successful_runs) / len(
                self.optimization_history
            )

            for run in self.optimization_history:
                stats["total_space_saved"] += run.get("total_space_saved", 0)
                stats["total_files_processed"] += run.get("total_files_processed", 0)

        return stats

    async def _log_optimization_run(self, interval: str, results: List[Dict[str, Any]]):
        """Log optimization run results"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "interval": interval,
                "status": "success"
                if all(r.get("status") == "success" for r in results)
                else "partial",
                "tasks_executed": len(results),
                "successful_tasks": len(
                    [r for r in results if r.get("status") == "success"]
                ),
                "total_space_saved": sum(r.get("space_saved", 0) for r in results),
                "total_files_processed": sum(
                    r.get("files_processed", 0) for r in results
                ),
                "results": results,
            }

            self.optimization_history.append(log_entry)

            # Save to file
            log_path = self.base_path / "reports" / "background_optimization_log.json"
            log_path.parent.mkdir(parents=True, exist_ok=True)

            with open(log_path, "w") as f:
                json.dump(self.optimization_history, f, indent=2)

        except Exception as e:
            logger.error(f"Error logging optimization run: {e}")

    async def _save_optimization_config(self):
        """Save optimization configuration to file"""
        try:
            config_path = self.base_path / "config" / "optimization_schedule.yaml"
            config_path.parent.mkdir(parents=True, exist_ok=True)

            import yaml

            config = {
                "schedules": {
                    name: {
                        "interval": schedule.interval,
                        "time": schedule.time,
                        "enabled": schedule.enabled,
                        "last_run": schedule.last_run.isoformat()
                        if schedule.last_run
                        else None,
                        "next_run": schedule.next_run.isoformat()
                        if schedule.next_run
                        else None,
                    }
                    for name, schedule in self.schedules.items()
                },
                "tasks": [
                    {
                        "name": task.name,
                        "module": task.module,
                        "function": task.function,
                        "parameters": task.parameters,
                        "priority": task.priority,
                        "enabled": task.enabled,
                    }
                    for task in self.tasks
                ],
            }

            with open(config_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False)

        except Exception as e:
            logger.error(f"Error saving optimization config: {e}")


# Example usage and testing
async def main():
    """Test the Background Optimizer Module"""
    optimizer = BackgroundOptimizer()

    # Test continuous scan
    result = await optimizer.execute_function("run_continuous_scan", interval="daily")
    print(f"Continuous scan result: {result}")

    # Test scheduling
    result = await optimizer.execute_function(
        "schedule_optimization",
        schedule_name="test_schedule",
        interval="daily",
        time="02:00",
    )
    print(f"Schedule optimization result: {result}")

    # Test status
    result = await optimizer.execute_function("get_optimization_status")
    print(f"Optimization status result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
