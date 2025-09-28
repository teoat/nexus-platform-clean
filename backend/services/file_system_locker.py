#!/usr/bin/env python3
"""
NUC File System Locker
Advanced file system protection and locking mechanisms
"""

import asyncio
import json
import logging
import os
import stat
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import aiofiles
except ImportError:
    # Fallback for systems without aiofiles
    aiofiles = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LockType(Enum):
    """File lock types"""
    READONLY = "readonly"
    WRITE_PROTECT = "write_protect"
    EXECUTE_PROTECT = "execute_protect"
    DELETE_PROTECT = "delete_protect"
    GIT_IGNORE = "git_ignore"
    PERMISSION_LOCK = "permission_lock"
    DOCKER_LOCK = "docker_lock"
    ENVIRONMENT_LOCK = "environment_lock"


class LockLevel(Enum):
    """Lock protection levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class FileLock:
    """File lock information"""
    path: Path
    lock_type: LockType
    level: LockLevel
    created_at: datetime
    expires_at: Optional[datetime] = None
    owner: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LockRule:
    """Lock rule definition"""
    id: str
    name: str
    pattern: str
    lock_type: LockType
    level: LockLevel
    enabled: bool = True
    conditions: Dict[str, Any] = field(default_factory=dict)
    auto_apply: bool = True


class FileSystemLocker:
    """Advanced file system locker with multiple protection mechanisms"""
    
    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        self.base_path = Path(base_path)
        self.active_locks: Dict[str, FileLock] = {}
        self.lock_rules: Dict[str, LockRule] = {}
        self.protected_files: Set[str] = set()
        self.gitignore_entries: Set[str] = set()
        
        # Statistics
        self.stats = {
            "files_locked": 0,
            "files_unlocked": 0,
            "rules_applied": 0,
            "protection_violations": 0,
            "errors": 0
        }
        
        # Initialize lock rules
        self._init_lock_rules()
        self._load_gitignore()
    
    def _init_lock_rules(self):
        """Initialize default lock rules"""
        default_rules = [
            LockRule(
                id="essential_config",
                name="Lock Essential Configuration Files",
                pattern="package.json|requirements.txt|docker-compose.yml|Dockerfile*",
                lock_type=LockType.READONLY,
                level=LockLevel.CRITICAL,
                conditions={"auto_apply": True},
                auto_apply=True
            ),
            LockRule(
                id="source_code",
                name="Protect Source Code Files",
                pattern="**/*.{py,ts,tsx,js,jsx}",
                lock_type=LockType.WRITE_PROTECT,
                level=LockLevel.HIGH,
                conditions={"exclude_test": True},
                auto_apply=True
            ),
            LockRule(
                id="database_files",
                name="Protect Database Files",
                pattern="**/*.{db,sqlite,sql}",
                lock_type=LockType.DELETE_PROTECT,
                level=LockLevel.CRITICAL,
                conditions={},
                auto_apply=True
            ),
            LockRule(
                id="log_files",
                name="Git Ignore Log Files",
                pattern="**/*.log",
                lock_type=LockType.GIT_IGNORE,
                level=LockLevel.LOW,
                conditions={},
                auto_apply=True
            ),
            LockRule(
                id="temp_files",
                name="Git Ignore Temporary Files",
                pattern="**/__pycache__/**|**/*.tmp|**/*.temp",
                lock_type=LockType.GIT_IGNORE,
                level=LockLevel.LOW,
                conditions={},
                auto_apply=True
            ),
            LockRule(
                id="backup_files",
                name="Git Ignore Backup Files",
                pattern="backup*/**|**/*.bak|**/*.backup",
                lock_type=LockType.GIT_IGNORE,
                level=LockLevel.LOW,
                conditions={},
                auto_apply=True
            )
        ]
        
        for rule in default_rules:
            self.lock_rules[rule.id] = rule
    
    def _load_gitignore(self):
        """Load existing .gitignore entries"""
        gitignore_path = self.base_path / ".gitignore"
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r') as f:
                    self.gitignore_entries = set(line.strip() for line in f if line.strip() and not line.startswith('#'))
            except Exception as e:
                logger.error(f"Error loading .gitignore: {e}")
    
    async def start(self):
        """Start the file system locker"""
        logger.info("Starting File System Locker...")
        
        # Apply all enabled rules
        await self._apply_all_rules()
        
        # Start monitoring
        asyncio.create_task(self._monitor_protection())
        
        logger.info("File System Locker started")
    
    async def stop(self):
        """Stop the file system locker"""
        logger.info("Stopping File System Locker...")
        logger.info("File System Locker stopped")
    
    async def _apply_all_rules(self):
        """Apply all enabled lock rules"""
        for rule in self.lock_rules.values():
            if rule.enabled and rule.auto_apply:
                try:
                    await self._apply_rule(rule)
                    self.stats["rules_applied"] += 1
                except Exception as e:
                    logger.error(f"Error applying rule {rule.id}: {e}")
                    self.stats["errors"] += 1
    
    async def _apply_rule(self, rule: LockRule):
        """Apply a specific lock rule"""
        logger.info(f"Applying lock rule: {rule.name}")
        
        # Find files matching the pattern
        matching_files = await self._find_matching_files(rule.pattern)
        
        for file_path in matching_files:
            try:
                if await self._should_apply_lock(file_path, rule):
                    await self._lock_file(file_path, rule)
            except Exception as e:
                logger.error(f"Error applying lock to {file_path}: {e}")
                self.stats["errors"] += 1
    
    async def _find_matching_files(self, pattern: str) -> List[Path]:
        """Find files matching the pattern"""
        files = []
        
        try:
            if "|" in pattern:
                # Multiple patterns separated by |
                patterns = pattern.split("|")
                for p in patterns:
                    files.extend(await self._find_files_by_pattern(p.strip()))
            else:
                files = await self._find_files_by_pattern(pattern)
                
        except Exception as e:
            logger.error(f"Error finding files with pattern {pattern}: {e}")
        
        return files
    
    async def _find_files_by_pattern(self, pattern: str) -> List[Path]:
        """Find files by pattern"""
        files = []
        
        try:
            if "**" in pattern:
                # Recursive search
                for file_path in self.base_path.rglob(pattern.replace("**", "*")):
                    if file_path.is_file():
                        files.append(file_path)
            elif "*" in pattern:
                # Wildcard search
                for file_path in self.base_path.glob(pattern):
                    if file_path.is_file():
                        files.append(file_path)
            else:
                # Exact match
                file_path = self.base_path / pattern
                if file_path.exists() and file_path.is_file():
                    files.append(file_path)
                    
        except Exception as e:
            logger.error(f"Error finding files with pattern {pattern}: {e}")
        
        return files
    
    async def _should_apply_lock(self, file_path: Path, rule: LockRule) -> bool:
        """Check if lock should be applied to file"""
        try:
            # Check conditions
            if "exclude_test" in rule.conditions and rule.conditions["exclude_test"]:
                if "test" in str(file_path).lower() or "spec" in str(file_path).lower():
                    return False
            
            # Check if file is already locked
            if str(file_path) in self.active_locks:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking lock conditions {file_path}: {e}")
            return False
    
    async def _lock_file(self, file_path: Path, rule: LockRule):
        """Lock a file based on rule"""
        try:
            lock = FileLock(
                path=file_path,
                lock_type=rule.lock_type,
                level=rule.level,
                created_at=datetime.now(),
                owner="system",
                metadata={"rule_id": rule.id}
            )
            
            # Apply the lock based on type
            if rule.lock_type == LockType.READONLY:
                await self._apply_readonly_lock(file_path)
            elif rule.lock_type == LockType.WRITE_PROTECT:
                await self._apply_write_protect_lock(file_path)
            elif rule.lock_type == LockType.DELETE_PROTECT:
                await self._apply_delete_protect_lock(file_path)
            elif rule.lock_type == LockType.GIT_IGNORE:
                await self._apply_gitignore_lock(file_path)
            elif rule.lock_type == LockType.PERMISSION_LOCK:
                await self._apply_permission_lock(file_path)
            elif rule.lock_type == LockType.DOCKER_LOCK:
                await self._apply_docker_lock(file_path)
            elif rule.lock_type == LockType.ENVIRONMENT_LOCK:
                await self._apply_environment_lock(file_path)
            
            # Store lock information
            self.active_locks[str(file_path)] = lock
            self.protected_files.add(str(file_path))
            self.stats["files_locked"] += 1
            
            logger.info(f"Locked file: {file_path} ({rule.lock_type.value})")
            
        except Exception as e:
            logger.error(f"Error locking file {file_path}: {e}")
            self.stats["errors"] += 1
    
    async def _apply_readonly_lock(self, file_path: Path):
        """Apply read-only lock to file"""
        try:
            current_perms = file_path.stat().st_mode
            file_path.chmod(current_perms & ~stat.S_IWRITE)
        except Exception as e:
            logger.error(f"Error applying readonly lock {file_path}: {e}")
    
    async def _apply_write_protect_lock(self, file_path: Path):
        """Apply write protection lock to file"""
        try:
            # Set file to read-only for owner, group, and others
            file_path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        except Exception as e:
            logger.error(f"Error applying write protect lock {file_path}: {e}")
    
    async def _apply_delete_protect_lock(self, file_path: Path):
        """Apply delete protection lock to file"""
        try:
            # Set file to read-only and add to protected list
            file_path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
            self.protected_files.add(str(file_path))
        except Exception as e:
            logger.error(f"Error applying delete protect lock {file_path}: {e}")
    
    async def _apply_gitignore_lock(self, file_path: Path):
        """Apply gitignore lock to file"""
        try:
            relative_path = file_path.relative_to(self.base_path)
            gitignore_entry = str(relative_path)
            
            if gitignore_entry not in self.gitignore_entries:
                self.gitignore_entries.add(gitignore_entry)
                await self._update_gitignore()
                
        except Exception as e:
            logger.error(f"Error applying gitignore lock {file_path}: {e}")
    
    async def _apply_permission_lock(self, file_path: Path):
        """Apply permission-based lock to file"""
        try:
            # Set restrictive permissions
            file_path.chmod(stat.S_IRUSR)  # Only owner can read
        except Exception as e:
            logger.error(f"Error applying permission lock {file_path}: {e}")
    
    async def _apply_docker_lock(self, file_path: Path):
        """Apply Docker-based lock to file"""
        try:
            # Add file to Docker ignore or create Docker lock file
            docker_lock_file = self.base_path / ".dockerignore"
            if not docker_lock_file.exists():
                docker_lock_file.touch()
            
            async with aiofiles.open(docker_lock_file, 'a') as f:
                relative_path = file_path.relative_to(self.base_path)
                await f.write(f"{relative_path}\n")
                
        except Exception as e:
            logger.error(f"Error applying docker lock {file_path}: {e}")
    
    async def _apply_environment_lock(self, file_path: Path):
        """Apply environment-based lock to file"""
        try:
            # Create environment lock file
            env_lock_file = file_path.with_suffix(file_path.suffix + ".lock")
            env_lock_file.write_text(f"Locked by NUC at {datetime.now().isoformat()}")
            
        except Exception as e:
            logger.error(f"Error applying environment lock {file_path}: {e}")
    
    async def _update_gitignore(self):
        """Update .gitignore file with new entries"""
        try:
            gitignore_path = self.base_path / ".gitignore"
            
            if aiofiles:
                async with aiofiles.open(gitignore_path, 'w') as f:
                    await f.write("# NUC File System Locker - Auto-generated\n")
                    for entry in sorted(self.gitignore_entries):
                        await f.write(f"{entry}\n")
            else:
                with open(gitignore_path, 'w') as f:
                    f.write("# NUC File System Locker - Auto-generated\n")
                    for entry in sorted(self.gitignore_entries):
                        f.write(f"{entry}\n")
                    
        except Exception as e:
            logger.error(f"Error updating .gitignore: {e}")
    
    async def _monitor_protection(self):
        """Monitor file protection and detect violations"""
        while True:
            try:
                await self._check_protection_violations()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in protection monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _check_protection_violations(self):
        """Check for protection violations"""
        try:
            for file_path_str in self.protected_files:
                file_path = Path(file_path_str)
                
                if not file_path.exists():
                    logger.warning(f"Protected file deleted: {file_path}")
                    self.stats["protection_violations"] += 1
                    # Recreate protection if needed
                    await self._recreate_protection(file_path)
                else:
                    # Check if permissions were changed
                    current_perms = file_path.stat().st_mode
                    if current_perms & stat.S_IWRITE:
                        logger.warning(f"Protected file permissions changed: {file_path}")
                        self.stats["protection_violations"] += 1
                        # Reapply protection
                        await self._reapply_protection(file_path)
                        
        except Exception as e:
            logger.error(f"Error checking protection violations: {e}")
    
    async def _recreate_protection(self, file_path: Path):
        """Recreate protection for a deleted file"""
        try:
            # Find the original lock rule
            for lock in self.active_locks.values():
                if lock.path == file_path:
                    # Reapply the lock rule
                    for rule in self.lock_rules.values():
                        if rule.id == lock.metadata.get("rule_id"):
                            await self._apply_rule(rule)
                            break
                    break
                    
        except Exception as e:
            logger.error(f"Error recreating protection {file_path}: {e}")
    
    async def _reapply_protection(self, file_path: Path):
        """Reapply protection to a file"""
        try:
            # Find the original lock rule
            for lock in self.active_locks.values():
                if lock.path == file_path:
                    # Reapply the lock
                    await self._lock_file(file_path, self.lock_rules[lock.metadata["rule_id"]])
                    break
                    
        except Exception as e:
            logger.error(f"Error reapplying protection {file_path}: {e}")
    
    async def unlock_file(self, file_path: Path, owner: str = "system") -> bool:
        """Unlock a file"""
        try:
            file_path_str = str(file_path)
            
            if file_path_str not in self.active_locks:
                logger.warning(f"File not locked: {file_path}")
                return False
            
            lock = self.active_locks[file_path_str]
            
            # Check ownership
            if lock.owner != owner:
                logger.warning(f"File locked by different owner: {file_path}")
                return False
            
            # Remove lock
            del self.active_locks[file_path_str]
            self.protected_files.discard(file_path_str)
            self.stats["files_unlocked"] += 1
            
            # Restore original permissions
            await self._restore_permissions(file_path)
            
            logger.info(f"Unlocked file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error unlocking file {file_path}: {e}")
            self.stats["errors"] += 1
            return False
    
    async def _restore_permissions(self, file_path: Path):
        """Restore original file permissions"""
        try:
            # Restore write permissions
            current_perms = file_path.stat().st_mode
            file_path.chmod(current_perms | stat.S_IWRITE)
            
        except Exception as e:
            logger.error(f"Error restoring permissions {file_path}: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get file system locker status"""
        return {
            "active_locks": len(self.active_locks),
            "protected_files": len(self.protected_files),
            "lock_rules": len(self.lock_rules),
            "gitignore_entries": len(self.gitignore_entries),
            "stats": self.stats
        }
    
    def get_locked_files(self) -> List[Dict[str, Any]]:
        """Get list of locked files"""
        return [
            {
                "path": str(lock.path),
                "type": lock.lock_type.value,
                "level": lock.level.value,
                "created_at": lock.created_at.isoformat(),
                "owner": lock.owner
            }
            for lock in self.active_locks.values()
        ]
    
    def add_lock_rule(self, rule: LockRule):
        """Add a new lock rule"""
        self.lock_rules[rule.id] = rule
        logger.info(f"Added lock rule: {rule.name}")
    
    def remove_lock_rule(self, rule_id: str):
        """Remove a lock rule"""
        if rule_id in self.lock_rules:
            del self.lock_rules[rule_id]
            logger.info(f"Removed lock rule: {rule_id}")
    
    async def force_unlock_all(self, owner: str = "system"):
        """Force unlock all files (use with caution)"""
        logger.warning("Force unlocking all files...")
        
        unlocked_count = 0
        for file_path_str in list(self.active_locks.keys()):
            file_path = Path(file_path_str)
            if await self.unlock_file(file_path, owner):
                unlocked_count += 1
        
        logger.info(f"Force unlocked {unlocked_count} files")
        return unlocked_count


# Global file system locker instance
file_system_locker = FileSystemLocker()


async def main():
    """Main entry point for testing"""
    try:
        await file_system_locker.start()
        
        # Wait for some monitoring
        await asyncio.sleep(60)
        
        # Show status
        status = file_system_locker.get_status()
        print(f"File System Locker Status: {json.dumps(status, indent=2)}")
        
        # Show locked files
        locked_files = file_system_locker.get_locked_files()
        print(f"Locked Files: {json.dumps(locked_files, indent=2)}")
        
        await file_system_locker.stop()
        
    except Exception as e:
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
