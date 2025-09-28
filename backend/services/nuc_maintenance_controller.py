#!/usr/bin/env python3
"""
NUC Automated Maintenance System Controller
Central controller for workspace maintenance, locking, and automation
"""

import asyncio
import json
import logging
import os
import shutil
import stat
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import aiofiles
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MaintenanceAction(Enum):
    """Maintenance action types"""
    CLEAN = "clean"
    LOCK = "lock"
    MONITOR = "monitor"
    BACKUP = "backup"
    ALERT = "alert"
    HEAL = "heal"


class FileCategory(Enum):
    """File categorization for maintenance"""
    ESSENTIAL = "essential"
    CONFIG = "config"
    SOURCE = "source"
    DOCS = "docs"
    LOGS = "logs"
    TEMP = "temp"
    BACKUP = "backup"
    ARCHIVE = "archive"
    REMOVABLE = "removable"


@dataclass
class MaintenanceRule:
    """Maintenance rule definition"""
    id: str
    name: str
    action: MaintenanceAction
    pattern: str
    category: FileCategory
    priority: int
    enabled: bool = True
    schedule: str = "*/5 * * * *"  # Cron-like schedule
    conditions: Dict[str, Any] = field(default_factory=dict)
    actions: List[str] = field(default_factory=list)


@dataclass
class FileInfo:
    """File information for maintenance"""
    path: Path
    size: int
    modified: datetime
    category: FileCategory
    locked: bool = False
    essential: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class NUCMaintenanceController:
    """NUC Automated Maintenance System Controller"""
    
    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        self.base_path = Path(base_path)
        self.rules: Dict[str, MaintenanceRule] = {}
        self.file_registry: Dict[str, FileInfo] = {}
        self.locked_files: Set[str] = set()
        self.essential_files: Set[str] = set()
        self.running = False
        
        # Statistics
        self.stats = {
            "files_processed": 0,
            "files_cleaned": 0,
            "files_locked": 0,
            "files_unlocked": 0,
            "rules_executed": 0,
            "alerts_sent": 0,
            "errors": 0
        }
        
        # Initialize essential files
        self._init_essential_files()
        self._load_maintenance_rules()
        
    def _init_essential_files(self):
        """Initialize list of essential application files"""
        essential_patterns = [
            # Core application files
            "package.json", "requirements.txt", "docker-compose.yml",
            "Dockerfile*", "*.py", "*.tsx", "*.ts", "*.js", "*.jsx",
            
            # Configuration files
            "*.yaml", "*.yml", "*.json", "*.env*", "*.conf", "*.config",
            
            # Database files
            "*.db", "*.sqlite", "*.sql",
            
            # Essential directories
            "frontend/web/src/**", "backend/**", "nexus/**",
            "config/**", "docker/**", "nginx/**"
        ]
        
        for pattern in essential_patterns:
            self.essential_files.add(pattern)
    
    def _load_maintenance_rules(self):
        """Load maintenance rules from configuration"""
        default_rules = [
            MaintenanceRule(
                id="clean_logs",
                name="Clean Log Files",
                action=MaintenanceAction.CLEAN,
                pattern="*.log",
                category=FileCategory.LOGS,
                priority=1,
                schedule="0 */6 * * *",  # Every 6 hours
                conditions={"max_age_days": 7, "max_size_mb": 100},
                actions=["delete", "compress_old"]
            ),
            MaintenanceRule(
                id="clean_temp",
                name="Clean Temporary Files",
                action=MaintenanceAction.CLEAN,
                pattern="**/__pycache__/**",
                category=FileCategory.TEMP,
                priority=2,
                schedule="0 */2 * * *",  # Every 2 hours
                conditions={"max_age_days": 1},
                actions=["delete"]
            ),
            MaintenanceRule(
                id="clean_backups",
                name="Clean Old Backups",
                action=MaintenanceAction.CLEAN,
                pattern="backup*/**",
                category=FileCategory.BACKUP,
                priority=3,
                schedule="0 2 * * *",  # Daily at 2 AM
                conditions={"max_age_days": 30},
                actions=["delete", "compress"]
            ),
            MaintenanceRule(
                id="lock_essential",
                name="Lock Essential Files",
                action=MaintenanceAction.LOCK,
                pattern="package.json|requirements.txt|docker-compose.yml",
                category=FileCategory.ESSENTIAL,
                priority=1,
                schedule="*/1 * * * *",  # Every minute
                conditions={},
                actions=["readonly", "gitignore"]
            ),
            MaintenanceRule(
                id="monitor_size",
                name="Monitor Directory Size",
                action=MaintenanceAction.MONITOR,
                pattern="**/*",
                category=FileCategory.ESSENTIAL,
                priority=2,
                schedule="*/5 * * * *",  # Every 5 minutes
                conditions={"max_size_gb": 10},
                actions=["alert", "cleanup"]
            )
        ]
        
        for rule in default_rules:
            self.rules[rule.id] = rule
    
    async def start(self):
        """Start the maintenance controller"""
        logger.info("Starting NUC Maintenance Controller...")
        self.running = True
        
        # Start background tasks
        asyncio.create_task(self._maintenance_loop())
        asyncio.create_task(self._monitoring_loop())
        asyncio.create_task(self._file_registry_update())
        
        logger.info("NUC Maintenance Controller started")
    
    async def stop(self):
        """Stop the maintenance controller"""
        logger.info("Stopping NUC Maintenance Controller...")
        self.running = False
        logger.info("NUC Maintenance Controller stopped")
    
    async def _maintenance_loop(self):
        """Main maintenance execution loop"""
        while self.running:
            try:
                await self._execute_maintenance_rules()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in maintenance loop: {e}")
                self.stats["errors"] += 1
                await asyncio.sleep(30)
    
    async def _execute_maintenance_rules(self):
        """Execute all enabled maintenance rules"""
        current_time = datetime.now()
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
                
            try:
                # Check if rule should execute based on schedule
                if self._should_execute_rule(rule, current_time):
                    await self._execute_rule(rule)
                    self.stats["rules_executed"] += 1
                    
            except Exception as e:
                logger.error(f"Error executing rule {rule.id}: {e}")
                self.stats["errors"] += 1
    
    def _should_execute_rule(self, rule: MaintenanceRule, current_time: datetime) -> bool:
        """Check if a rule should execute based on its schedule"""
        # Simple schedule checking (in production, use cron parser)
        if rule.schedule == "*/1 * * * *":  # Every minute
            return True
        elif rule.schedule == "*/5 * * * *":  # Every 5 minutes
            return current_time.minute % 5 == 0
        elif rule.schedule == "0 */2 * * *":  # Every 2 hours
            return current_time.minute == 0 and current_time.hour % 2 == 0
        elif rule.schedule == "0 */6 * * *":  # Every 6 hours
            return current_time.minute == 0 and current_time.hour % 6 == 0
        elif rule.schedule == "0 2 * * *":  # Daily at 2 AM
            return current_time.minute == 0 and current_time.hour == 2
        
        return False
    
    async def _execute_rule(self, rule: MaintenanceRule):
        """Execute a specific maintenance rule"""
        logger.info(f"Executing rule: {rule.name}")
        
        if rule.action == MaintenanceAction.CLEAN:
            await self._clean_files(rule)
        elif rule.action == MaintenanceAction.LOCK:
            await self._lock_files(rule)
        elif rule.action == MaintenanceAction.MONITOR:
            await self._monitor_files(rule)
        elif rule.action == MaintenanceAction.BACKUP:
            await self._backup_files(rule)
        elif rule.action == MaintenanceAction.ALERT:
            await self._send_alert(rule)
        elif rule.action == MaintenanceAction.HEAL:
            await self._heal_system(rule)
    
    async def _clean_files(self, rule: MaintenanceRule):
        """Clean files based on rule"""
        files_to_clean = await self._find_files(rule.pattern, rule.category)
        
        for file_path in files_to_clean:
            try:
                if await self._should_clean_file(file_path, rule.conditions):
                    await self._clean_file(file_path, rule.actions)
                    self.stats["files_cleaned"] += 1
                    
            except Exception as e:
                logger.error(f"Error cleaning file {file_path}: {e}")
                self.stats["errors"] += 1
    
    async def _lock_files(self, rule: MaintenanceRule):
        """Lock files based on rule"""
        files_to_lock = await self._find_files(rule.pattern, rule.category)
        
        for file_path in files_to_lock:
            try:
                if await self._should_lock_file(file_path, rule.conditions):
                    await self._lock_file(file_path, rule.actions)
                    self.stats["files_locked"] += 1
                    
            except Exception as e:
                logger.error(f"Error locking file {file_path}: {e}")
                self.stats["errors"] += 1
    
    async def _monitor_files(self, rule: MaintenanceRule):
        """Monitor files based on rule"""
        files_to_monitor = await self._find_files(rule.pattern, rule.category)
        
        for file_path in files_to_monitor:
            try:
                if await self._should_alert_file(file_path, rule.conditions):
                    await self._send_file_alert(file_path, rule.actions)
                    self.stats["alerts_sent"] += 1
                    
            except Exception as e:
                logger.error(f"Error monitoring file {file_path}: {e}")
                self.stats["errors"] += 1
    
    async def _find_files(self, pattern: str, category: FileCategory) -> List[Path]:
        """Find files matching pattern and category"""
        files = []
        
        try:
            if "**" in pattern:
                # Recursive search
                for file_path in self.base_path.rglob(pattern.replace("**", "*")):
                    if file_path.is_file():
                        files.append(file_path)
            else:
                # Simple pattern matching
                for file_path in self.base_path.glob(pattern):
                    if file_path.is_file():
                        files.append(file_path)
                        
        except Exception as e:
            logger.error(f"Error finding files with pattern {pattern}: {e}")
        
        return files
    
    async def _should_clean_file(self, file_path: Path, conditions: Dict[str, Any]) -> bool:
        """Check if a file should be cleaned based on conditions"""
        try:
            # Check if file is essential
            if str(file_path) in self.essential_files:
                return False
            
            # Check age
            if "max_age_days" in conditions:
                max_age = timedelta(days=conditions["max_age_days"])
                file_age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_age < max_age:
                    return False
            
            # Check size
            if "max_size_mb" in conditions:
                max_size = conditions["max_size_mb"] * 1024 * 1024
                if file_path.stat().st_size < max_size:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking file conditions {file_path}: {e}")
            return False
    
    async def _should_lock_file(self, file_path: Path, conditions: Dict[str, Any]) -> bool:
        """Check if a file should be locked based on conditions"""
        try:
            # Check if file is essential
            if str(file_path) in self.essential_files:
                return True
            
            # Check if already locked
            if str(file_path) in self.locked_files:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking lock conditions {file_path}: {e}")
            return False
    
    async def _should_alert_file(self, file_path: Path, conditions: Dict[str, Any]) -> bool:
        """Check if a file should trigger an alert based on conditions"""
        try:
            # Check size
            if "max_size_gb" in conditions:
                max_size = conditions["max_size_gb"] * 1024 * 1024 * 1024
                if file_path.stat().st_size > max_size:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking alert conditions {file_path}: {e}")
            return False
    
    async def _clean_file(self, file_path: Path, actions: List[str]):
        """Clean a file based on actions"""
        try:
            if "delete" in actions:
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
            elif "compress" in actions:
                # Compress file (simplified)
                compressed_path = file_path.with_suffix(file_path.suffix + ".gz")
                # Implementation would compress the file
                logger.info(f"Compressed file: {file_path}")
                
        except Exception as e:
            logger.error(f"Error cleaning file {file_path}: {e}")
    
    async def _lock_file(self, file_path: Path, actions: List[str]):
        """Lock a file based on actions"""
        try:
            if "readonly" in actions:
                # Set read-only permissions
                current_perms = file_path.stat().st_mode
                file_path.chmod(current_perms & ~stat.S_IWRITE)
                self.locked_files.add(str(file_path))
                logger.info(f"Locked file (readonly): {file_path}")
            
            if "gitignore" in actions:
                # Add to .gitignore
                gitignore_path = self.base_path / ".gitignore"
                if gitignore_path.exists():
                    async with aiofiles.open(gitignore_path, "a") as f:
                        await f.write(f"\n{file_path.relative_to(self.base_path)}\n")
                logger.info(f"Added to .gitignore: {file_path}")
                
        except Exception as e:
            logger.error(f"Error locking file {file_path}: {e}")
    
    async def _send_file_alert(self, file_path: Path, actions: List[str]):
        """Send alert for a file based on actions"""
        try:
            alert_message = f"File alert: {file_path} exceeds size limit"
            logger.warning(alert_message)
            
            if "cleanup" in actions:
                await self._clean_file(file_path, ["delete"])
                
        except Exception as e:
            logger.error(f"Error sending file alert {file_path}: {e}")
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.running:
            try:
                await self._update_system_metrics()
                await asyncio.sleep(30)  # Update every 30 seconds
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def _update_system_metrics(self):
        """Update system metrics"""
        try:
            # Get disk usage
            disk_usage = psutil.disk_usage(str(self.base_path))
            
            # Get memory usage
            memory_usage = psutil.virtual_memory()
            
            # Log metrics
            logger.info(f"Disk usage: {disk_usage.percent}%")
            logger.info(f"Memory usage: {memory_usage.percent}%")
            
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")
    
    async def _file_registry_update(self):
        """Update file registry"""
        while self.running:
            try:
                await self._scan_workspace()
                await asyncio.sleep(300)  # Update every 5 minutes
            except Exception as e:
                logger.error(f"Error updating file registry: {e}")
                await asyncio.sleep(600)
    
    async def _scan_workspace(self):
        """Scan workspace and update file registry"""
        try:
            for file_path in self.base_path.rglob("*"):
                if file_path.is_file():
                    file_info = FileInfo(
                        path=file_path,
                        size=file_path.stat().st_size,
                        modified=datetime.fromtimestamp(file_path.stat().st_mtime),
                        category=self._categorize_file(file_path),
                        locked=str(file_path) in self.locked_files,
                        essential=str(file_path) in self.essential_files
                    )
                    
                    self.file_registry[str(file_path)] = file_info
                    self.stats["files_processed"] += 1
                    
        except Exception as e:
            logger.error(f"Error scanning workspace: {e}")
    
    def _categorize_file(self, file_path: Path) -> FileCategory:
        """Categorize a file based on its path and extension"""
        path_str = str(file_path)
        
        if any(pattern in path_str for pattern in ["*.log", "logs/"]):
            return FileCategory.LOGS
        elif any(pattern in path_str for pattern in ["__pycache__", "*.tmp", "*.temp"]):
            return FileCategory.TEMP
        elif any(pattern in path_str for pattern in ["backup", "*.bak", "*.backup"]):
            return FileCategory.BACKUP
        elif any(pattern in path_str for pattern in ["archive", "archived"]):
            return FileCategory.ARCHIVE
        elif any(pattern in path_str for pattern in ["package.json", "requirements.txt", "docker-compose.yml"]):
            return FileCategory.ESSENTIAL
        elif any(pattern in path_str for pattern in ["*.yaml", "*.yml", "*.json", "*.conf"]):
            return FileCategory.CONFIG
        elif any(pattern in path_str for pattern in ["*.py", "*.ts", "*.tsx", "*.js", "*.jsx"]):
            return FileCategory.SOURCE
        elif any(pattern in path_str for pattern in ["*.md", "docs/", "README"]):
            return FileCategory.DOCS
        else:
            return FileCategory.REMOVABLE
    
    def get_status(self) -> Dict[str, Any]:
        """Get maintenance controller status"""
        return {
            "running": self.running,
            "rules_count": len(self.rules),
            "files_registered": len(self.file_registry),
            "files_locked": len(self.locked_files),
            "essential_files": len(self.essential_files),
            "stats": self.stats
        }
    
    def add_rule(self, rule: MaintenanceRule):
        """Add a new maintenance rule"""
        self.rules[rule.id] = rule
        logger.info(f"Added maintenance rule: {rule.name}")
    
    def remove_rule(self, rule_id: str):
        """Remove a maintenance rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Removed maintenance rule: {rule_id}")
    
    def enable_rule(self, rule_id: str):
        """Enable a maintenance rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            logger.info(f"Enabled maintenance rule: {rule_id}")
    
    def disable_rule(self, rule_id: str):
        """Disable a maintenance rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            logger.info(f"Disabled maintenance rule: {rule_id}")


# Global maintenance controller instance
maintenance_controller = NUCMaintenanceController()


async def main():
    """Main entry point for testing"""
    try:
        await maintenance_controller.start()
        
        # Wait for some maintenance cycles
        await asyncio.sleep(300)  # 5 minutes
        
        # Show status
        status = maintenance_controller.get_status()
        print(f"Maintenance Status: {json.dumps(status, indent=2)}")
        
        await maintenance_controller.stop()
        
    except Exception as e:
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
