#!/usr/bin/env python3
"""
Repo Pruner Module - NEXUS Platform
Handles repository pruning, cleanup, and maintenance operations
"""

import logging
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_module import BaseModule, ModuleResult

logger = logging.getLogger(__name__)


@dataclass
class CleanupResult:
    """Result of cleanup operation"""

    operation_type: str
    files_removed: int
    space_freed: int
    removed_paths: List[str]


class RepoPruner(BaseModule):
    """Repo Pruner - Handles repository cleanup and maintenance"""

    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        super().__init__(base_path)
        self.cleanup_log = []

    async def get_available_functions(self) -> List[str]:
        """Return list of available functions in this module"""
        return [
            "clear_temp_files",
            "archive_old_releases",
            "git_history_cleanup",
            "cleanup_build_artifacts",
            "remove_duplicate_files",
            "cleanup_logs",
            "generate_cleanup_report",
        ]

    async def get_module_info(self) -> Dict[str, Any]:
        """Return module information and capabilities"""
        return {
            "name": "RepoPruner",
            "version": "1.0",
            "description": "Handles repository pruning, cleanup, and maintenance operations",
            "functions": await self.get_available_functions(),
            "dependencies": ["file_management", "optimization"],
            "output_files": ["reports/cleanup_report.json", "reports/cleanup_log.json"],
        }

    async def clear_temp_files(self, path: str = None) -> ModuleResult:
        """Remove .tmp, .cache, build artifacts, logs"""
        try:
            if path is None:
                path = str(self.base_path)

            logger.info(f"Clearing temp files in {path}")

            temp_patterns = [
                "**/.tmp",
                "**/.cache",
                "**/tmp",
                "**/temp",
                "**/*.tmp",
                "**/*.cache",
                "**/*.log",
                "**/node_modules/.cache",
                "**/.pytest_cache",
                "**/__pycache__",
                "**/*.pyc",
                "**/*.pyo",
                "**/.coverage",
                "**/coverage",
                "**/.nyc_output",
                "**/dist",
                "**/build",
                "**/.next",
                "**/.nuxt",
                "**/.output",
            ]

            cleanup_results = []
            total_files_removed = 0
            total_space_freed = 0

            for pattern in temp_patterns:
                result = await self._cleanup_pattern(path, pattern)
                if result:
                    cleanup_results.append(result)
                    total_files_removed += result.files_removed
                    total_space_freed += result.space_freed

            # Log cleanup results
            await self._log_cleanup_results(cleanup_results)

            return ModuleResult(
                success=True,
                data={
                    "files_removed": total_files_removed,
                    "space_freed": total_space_freed,
                    "cleanup_operations": len(cleanup_results),
                    "cleanup_results": cleanup_results,
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error clearing temp files: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _cleanup_pattern(
        self, base_path: str, pattern: str
    ) -> Optional[CleanupResult]:
        """Clean up files matching a specific pattern"""
        try:
            base_path_obj = Path(base_path)
            files_removed = 0
            space_freed = 0
            removed_paths = []

            for file_path in base_path_obj.glob(pattern):
                if file_path.is_file():
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    files_removed += 1
                    space_freed += file_size
                    removed_paths.append(str(file_path))
                elif file_path.is_dir():
                    dir_size = await self._get_directory_size(file_path)
                    shutil.rmtree(file_path)
                    files_removed += 1
                    space_freed += dir_size
                    removed_paths.append(str(file_path))

            if files_removed > 0:
                return CleanupResult(
                    operation_type=f"cleanup_{pattern.replace('**/', '').replace('*', '')}",
                    files_removed=files_removed,
                    space_freed=space_freed,
                    removed_paths=removed_paths,
                )

            return None

        except Exception as e:
            logger.warning(f"Error cleaning up pattern {pattern}: {e}")
            return None

    async def _get_directory_size(self, directory: Path) -> int:
        """Get total size of directory"""
        total_size = 0
        try:
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception as e:
            logger.warning(f"Error calculating directory size for {directory}: {e}")
        return total_size

    async def archive_old_releases(
        self, path: str = None, keep_last: int = 3
    ) -> ModuleResult:
        """Archive older release folders/binaries, keep last N stable releases"""
        try:
            if path is None:
                path = str(self.base_path / "releases")

            releases_path = Path(path)
            if not releases_path.exists():
                return ModuleResult(
                    success=False,
                    data=None,
                    error="No releases directory found",
                    timestamp=datetime.now(),
                )

            logger.info(f"Archiving old releases, keeping last {keep_last}")

            # Find all release directories
            release_dirs = []
            for item in releases_path.iterdir():
                if item.is_dir():
                    # Try to extract version from directory name
                    version = await self._extract_version_from_name(item.name)
                    if version:
                        release_dirs.append((item, version))

            # Sort by version (newest first)
            release_dirs.sort(key=lambda x: x[1], reverse=True)

            # Archive old releases
            archived_releases = []
            space_freed = 0

            for i, (release_dir, version) in enumerate(release_dirs):
                if i >= keep_last:
                    # Archive this release
                    archive_path = releases_path / f"{release_dir.name}.tar.gz"

                    # Create compressed archive
                    await self._create_archive(release_dir, archive_path)

                    # Calculate space before removal
                    dir_size = await self._get_directory_size(release_dir)

                    # Remove original directory
                    shutil.rmtree(release_dir)

                    archived_releases.append(
                        {
                            "name": release_dir.name,
                            "version": str(version),
                            "archive_path": str(archive_path),
                            "space_freed": dir_size,
                        }
                    )
                    space_freed += dir_size

            return ModuleResult(
                success=True,
                data={
                    "archived_releases": len(archived_releases),
                    "space_freed": space_freed,
                    "kept_releases": min(keep_last, len(release_dirs)),
                    "archived_details": archived_releases,
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error archiving old releases: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _extract_version_from_name(self, name: str) -> Optional[tuple]:
        """Extract version tuple from directory name"""
        import re

        # Try to match semantic versioning (e.g., v1.2.3, 1.2.3, v2.0.0-beta)
        version_pattern = r"v?(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?"
        match = re.search(version_pattern, name)

        if match:
            major, minor, patch = map(int, match.groups()[:3])
            prerelease = match.group(4) if match.group(4) else None
            return (major, minor, patch, prerelease)

        return None

    async def _create_archive(self, source_dir: Path, archive_path: Path):
        """Create compressed archive of directory"""
        import tarfile

        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(source_dir, arcname=source_dir.name)

    async def git_history_cleanup(self, repo_path: str = None) -> ModuleResult:
        """Run git gc and BFG cleanup to reduce repo history size"""
        try:
            if repo_path is None:
                repo_path = str(self.base_path)

            git_path = Path(repo_path) / ".git"
            if not git_path.exists():
                return ModuleResult(
                    success=False,
                    data=None,
                    error="No git repository found",
                    timestamp=datetime.now(),
                )

            logger.info(f"Cleaning up git history in {repo_path}")

            # Get original repo size
            original_size = await self._get_directory_size(git_path)

            # Run git garbage collection
            await self._run_git_gc(repo_path)

            # Get new repo size
            new_size = await self._get_directory_size(git_path)

            return ModuleResult(
                success=True,
                data={
                    "original_size": original_size,
                    "new_size": new_size,
                    "space_freed": original_size - new_size,
                    "optimization_type": "git_history_cleanup",
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error cleaning up git history: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _run_git_gc(self, repo_path: str):
        """Run git garbage collection"""
        try:
            # Run git gc --aggressive
            result = subprocess.run(
                ["git", "gc", "--aggressive", "--prune=now"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode != 0:
                logger.warning(f"Git gc returned non-zero exit code: {result.stderr}")

        except subprocess.TimeoutExpired:
            logger.warning("Git gc timed out")
        except Exception as e:
            logger.warning(f"Error running git gc: {e}")

    async def cleanup_build_artifacts(self, path: str = None) -> ModuleResult:
        """Clean up build artifacts and compiled files"""
        try:
            if path is None:
                path = str(self.base_path)

            logger.info(f"Cleaning up build artifacts in {path}")

            build_patterns = [
                "**/dist",
                "**/build",
                "**/target",
                "**/out",
                "**/.gradle",
                "**/.mvn",
                "**/node_modules/.cache",
                "**/.next",
                "**/.nuxt",
                "**/.output",
                "**/coverage",
                "**/.nyc_output",
                "**/__pycache__",
                "**/*.pyc",
                "**/*.pyo",
                "**/*.class",
                "**/*.jar",
                "**/*.war",
                "**/*.ear",
            ]

            cleanup_results = []
            total_files_removed = 0
            total_space_freed = 0

            for pattern in build_patterns:
                result = await self._cleanup_pattern(path, pattern)
                if result:
                    cleanup_results.append(result)
                    total_files_removed += result.files_removed
                    total_space_freed += result.space_freed

            return ModuleResult(
                success=True,
                data={
                    "files_removed": total_files_removed,
                    "space_freed": total_space_freed,
                    "cleanup_operations": len(cleanup_results),
                    "cleanup_results": cleanup_results,
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error cleaning up build artifacts: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def remove_duplicate_files(self, path: str = None) -> ModuleResult:
        """Remove duplicate files based on content hash"""
        try:
            if path is None:
                path = str(self.base_path)

            logger.info(f"Removing duplicate files in {path}")

            # Find duplicate files
            duplicates = await self._find_duplicate_files(path)

            # Remove duplicates (keep first occurrence)
            removed_files = []
            space_freed = 0

            for hash_key, files in duplicates.items():
                if len(files) > 1:
                    # Keep the first file, remove the rest
                    for file_path in files[1:]:
                        try:
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            removed_files.append(str(file_path))
                            space_freed += file_size
                        except Exception as e:
                            logger.warning(f"Error removing duplicate {file_path}: {e}")

            return ModuleResult(
                success=True,
                data={
                    "duplicates_found": len(duplicates),
                    "files_removed": len(removed_files),
                    "space_freed": space_freed,
                    "removed_files": removed_files,
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error removing duplicate files: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _find_duplicate_files(self, path: str) -> Dict[str, List[Path]]:
        """Find duplicate files based on content hash"""
        import hashlib

        hash_groups = {}
        base_path = Path(path)

        for file_path in base_path.rglob("*"):
            if file_path.is_file():
                try:
                    # Calculate file hash
                    file_hash = await self._calculate_file_hash(file_path)

                    if file_hash not in hash_groups:
                        hash_groups[file_hash] = []
                    hash_groups[file_hash].append(file_path)

                except Exception as e:
                    logger.warning(f"Error calculating hash for {file_path}: {e}")

        # Return only groups with duplicates
        return {
            hash_key: files for hash_key, files in hash_groups.items() if len(files) > 1
        }

    async def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content"""
        import hashlib

        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.warning(f"Error calculating hash for {file_path}: {e}")
            return ""

    async def cleanup_logs(
        self, path: str = None, max_age_days: int = 30
    ) -> ModuleResult:
        """Clean up old log files"""
        try:
            if path is None:
                path = str(self.base_path)

            logger.info(f"Cleaning up logs older than {max_age_days} days")

            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            log_patterns = ["**/*.log", "**/logs/**", "**/log/**"]

            cleanup_results = []
            total_files_removed = 0
            total_space_freed = 0

            for pattern in log_patterns:
                result = await self._cleanup_old_files(path, pattern, cutoff_date)
                if result:
                    cleanup_results.append(result)
                    total_files_removed += result.files_removed
                    total_space_freed += result.space_freed

            return ModuleResult(
                success=True,
                data={
                    "files_removed": total_files_removed,
                    "space_freed": total_space_freed,
                    "cleanup_operations": len(cleanup_results),
                    "max_age_days": max_age_days,
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error cleaning up logs: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _cleanup_old_files(
        self, base_path: str, pattern: str, cutoff_date: datetime
    ) -> Optional[CleanupResult]:
        """Clean up files older than cutoff date"""
        try:
            base_path_obj = Path(base_path)
            files_removed = 0
            space_freed = 0
            removed_paths = []

            for file_path in base_path_obj.glob(pattern):
                if file_path.is_file():
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime < cutoff_date:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        files_removed += 1
                        space_freed += file_size
                        removed_paths.append(str(file_path))

            if files_removed > 0:
                return CleanupResult(
                    operation_type=f"cleanup_old_{pattern.replace('**/', '').replace('*', '')}",
                    files_removed=files_removed,
                    space_freed=space_freed,
                    removed_paths=removed_paths,
                )

            return None

        except Exception as e:
            logger.warning(f"Error cleaning up old files with pattern {pattern}: {e}")
            return None

    async def generate_cleanup_report(self) -> ModuleResult:
        """Generate comprehensive cleanup report"""
        try:
            logger.info("Generating cleanup report")

            report = {
                "generated_at": datetime.now().isoformat(),
                "cleanup_operations": len(self.cleanup_log),
                "total_space_freed": sum(
                    op.get("space_freed", 0) for op in self.cleanup_log
                ),
                "cleanup_history": self.cleanup_log,
                "recommendations": await self._generate_cleanup_recommendations(),
            }

            # Save report
            report_path = self.base_path / "reports" / "cleanup_report.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)

            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)

            return ModuleResult(
                success=True,
                data={
                    "report_path": str(report_path),
                    "cleanup_operations": len(self.cleanup_log),
                    "total_space_freed": report["total_space_freed"],
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error generating cleanup report: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _generate_cleanup_recommendations(self) -> List[Dict]:
        """Generate cleanup recommendations"""
        recommendations = []

        # Check for large directories that could be cleaned
        large_dirs = await self._find_large_directories()
        for dir_info in large_dirs:
            recommendations.append(
                {
                    "type": "cleanup_large_directory",
                    "path": dir_info["path"],
                    "size_mb": dir_info["size_mb"],
                    "action": f"Consider cleaning up {dir_info['path']} ({dir_info['size_mb']:.1f}MB)",
                }
            )

        return recommendations

    async def _find_large_directories(self) -> List[Dict]:
        """Find large directories that could be cleaned"""
        large_dirs = []

        for item in self.base_path.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                dir_size = await self._get_directory_size(item)
                if dir_size > 100 * 1024 * 1024:  # 100MB
                    large_dirs.append(
                        {"path": str(item), "size_mb": dir_size / (1024 * 1024)}
                    )

        return large_dirs

    async def _log_cleanup_results(self, results: List[CleanupResult]):
        """Log cleanup results to file"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "operations": [
                    {
                        "type": result.operation_type,
                        "files_removed": result.files_removed,
                        "space_freed": result.space_freed,
                        "removed_paths": result.removed_paths,
                    }
                    for result in results
                ],
            }

            self.cleanup_log.append(log_entry)

            # Save to file
            log_path = self.base_path / "reports" / "cleanup_log.json"
            log_path.parent.mkdir(parents=True, exist_ok=True)

            with open(log_path, "w") as f:
                json.dump(self.cleanup_log, f, indent=2)

        except Exception as e:
            logger.error(f"Error logging cleanup results: {e}")


# Example usage and testing
async def main():
    """Test the Repo Pruner Module"""
    pruner = RepoPruner()

    # Test temp file cleanup
    result = await pruner.execute_function("clear_temp_files")
    print(f"Temp file cleanup result: {result}")

    # Test build artifact cleanup
    result = await pruner.execute_function("cleanup_build_artifacts")
    print(f"Build artifact cleanup result: {result}")

    # Test duplicate file removal
    result = await pruner.execute_function("remove_duplicate_files")
    print(f"Duplicate file removal result: {result}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
