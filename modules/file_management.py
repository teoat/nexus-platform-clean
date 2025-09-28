#!/usr/bin/env python3
"""
File Management Module - NEXUS Platform
Handles file scanning, SSOT enforcement, locking, and archiving
"""

import csv
import hashlib
import json
import logging
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .base_module import BaseModule, ModuleResult

logger = logging.getLogger(__name__)


@dataclass
class FileInfo:
    """File information for management operations"""

    path: str
    size: int
    hash: str
    modified_time: float
    content_type: str
    is_duplicate: bool = False
    duplicate_group: str = ""
    ssot_candidate: bool = False


class FileManagementModule(BaseModule):
    """File Management Module - Core file operations and SSOT enforcement"""

    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        super().__init__(base_path)
        self.file_registry: Dict[str, FileInfo] = {}
        self.duplicate_groups: Dict[str, List[FileInfo]] = {}
        self.ssot_manifest_path = (
            self.base_path / self.config["global"]["ssot_manifest_path"]
        )
        self.lock_manifest_path = (
            self.base_path / self.config["global"]["lock_manifest_path"]
        )
        self.snapshots_path = self.base_path / self.config["global"]["snapshots_path"]

        # Create necessary directories
        self.ssot_manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock_manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.snapshots_path.mkdir(parents=True, exist_ok=True)

    async def get_available_functions(self) -> List[str]:
        """Return list of available functions in this module"""
        return [
            "scan_files",
            "enforce_ssot",
            "lock_files",
            "archive_unused",
            "detect_duplicates",
            "create_ssot_manifest",
            "create_lock_manifest",
        ]

    async def get_module_info(self) -> Dict[str, Any]:
        """Return module information and capabilities"""
        return {
            "name": "FileManagementModule",
            "version": "1.0",
            "description": "Handles file scanning, SSOT enforcement, locking, and archiving",
            "functions": await self.get_available_functions(),
            "dependencies": ["audit_system"],
            "output_files": [
                "ssot/candidates.csv",
                "ssot/manifest.yaml",
                "locks/lock_manifest.json",
                "dependency_graph.json",
            ],
        }

    async def scan_files(
        self, workspace_path: str = None, extensions: List[str] = None
    ) -> ModuleResult:
        """Scan files and build registry with dependency analysis"""
        try:
            if workspace_path is None:
                workspace_path = str(self.base_path)

            if extensions is None:
                extensions = [
                    ".py",
                    ".js",
                    ".ts",
                    ".tsx",
                    ".json",
                    ".md",
                    ".txt",
                    ".yml",
                    ".yaml",
                    ".sql",
                ]

            logger.info(f"Scanning files in {workspace_path}")

            # Reset registry
            self.file_registry = {}

            # Scan files
            workspace = Path(workspace_path)
            for ext in extensions:
                for file_path in workspace.rglob(f"*{ext}"):
                    if file_path.is_file() and not any(
                        part.startswith(".") for part in file_path.parts
                    ):
                        file_info = await self._process_file(file_path)
                        if file_info:
                            self.file_registry[str(file_path)] = file_info

            # Generate candidates CSV
            await self._generate_candidates_csv()

            # Generate dependency graph
            await self._generate_dependency_graph()

            return ModuleResult(
                success=True,
                data={
                    "files_scanned": len(self.file_registry),
                    "candidates_csv": str(self.base_path / "ssot" / "candidates.csv"),
                    "dependency_graph": str(self.base_path / "dependency_graph.json"),
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error scanning files: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _process_file(self, file_path: Path) -> Optional[FileInfo]:
        """Process individual file and extract metadata"""
        try:
            if not file_path.exists() or not file_path.is_file():
                return None

            stat = file_path.stat()

            # Calculate file hash
            file_hash = await self._calculate_file_hash(file_path)

            # Determine content type
            content_type = self._determine_content_type(file_path)

            return FileInfo(
                path=str(file_path),
                size=stat.st_size,
                hash=file_hash,
                modified_time=stat.st_mtime,
                content_type=content_type,
            )

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return None

    async def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""

    def _determine_content_type(self, file_path: Path) -> str:
        """Determine content type based on file extension and content"""
        ext = file_path.suffix.lower()

        if ext in [".py"]:
            return "python"
        elif ext in [".js", ".ts", ".tsx"]:
            return "javascript"
        elif ext in [".json"]:
            return "json"
        elif ext in [".md"]:
            return "markdown"
        elif ext in [".yml", ".yaml"]:
            return "yaml"
        elif ext in [".sql"]:
            return "sql"
        else:
            return "other"

    async def _generate_candidates_csv(self):
        """Generate SSOT candidates CSV file"""
        try:
            candidates_path = self.base_path / "ssot" / "candidates.csv"
            candidates_path.parent.mkdir(parents=True, exist_ok=True)

            with open(candidates_path, "w", newline="") as csvfile:
                fieldnames = [
                    "path",
                    "size",
                    "hash",
                    "modified_time",
                    "content_type",
                    "is_duplicate",
                    "ssot_candidate",
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for file_info in self.file_registry.values():
                    writer.writerow(
                        {
                            "path": file_info.path,
                            "size": file_info.size,
                            "hash": file_info.hash,
                            "modified_time": file_info.modified_time,
                            "content_type": file_info.content_type,
                            "is_duplicate": file_info.is_duplicate,
                            "ssot_candidate": file_info.ssot_candidate,
                        }
                    )

            logger.info(f"Generated candidates CSV: {candidates_path}")

        except Exception as e:
            logger.error(f"Error generating candidates CSV: {e}")

    async def _generate_dependency_graph(self):
        """Generate dependency graph JSON file"""
        try:
            dependency_graph = {
                "version": "1.0",
                "generated_at": datetime.now().isoformat(),
                "files": {},
                "dependencies": {},
                "duplicate_groups": {},
            }

            # Add file information
            for file_path, file_info in self.file_registry.items():
                dependency_graph["files"][file_path] = {
                    "size": file_info.size,
                    "hash": file_info.hash,
                    "content_type": file_info.content_type,
                    "modified_time": file_info.modified_time,
                }

            # Add duplicate groups
            for hash_key, files in self.duplicate_groups.items():
                dependency_graph["duplicate_groups"][hash_key] = [f.path for f in files]

            # Save dependency graph
            graph_path = self.base_path / "dependency_graph.json"
            with open(graph_path, "w") as f:
                json.dump(dependency_graph, f, indent=2)

            logger.info(f"Generated dependency graph: {graph_path}")

        except Exception as e:
            logger.error(f"Error generating dependency graph: {e}")

    async def detect_duplicates(self) -> ModuleResult:
        """Detect duplicate files based on content hash"""
        try:
            logger.info("Detecting duplicate files...")

            # Group files by hash
            hash_groups = {}
            for file_info in self.file_registry.values():
                if file_info.hash:
                    if file_info.hash not in hash_groups:
                        hash_groups[file_info.hash] = []
                    hash_groups[file_info.hash].append(file_info)

            # Identify duplicates
            duplicates_found = 0
            for hash_key, files in hash_groups.items():
                if len(files) > 1:
                    duplicates_found += len(files) - 1
                    self.duplicate_groups[hash_key] = files

                    # Mark files as duplicates
                    for file_info in files:
                        file_info.is_duplicate = True
                        file_info.duplicate_group = hash_key

            return ModuleResult(
                success=True,
                data={
                    "duplicates_found": duplicates_found,
                    "duplicate_groups": len(self.duplicate_groups),
                    "duplicate_groups_detail": self.duplicate_groups,
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error detecting duplicates: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def enforce_ssot(self, strategy: str = "pick_smallest") -> ModuleResult:
        """Enforce Single Source of Truth by merging duplicates"""
        try:
            logger.info(f"Enforcing SSOT with strategy: {strategy}")

            ssot_files = []
            duplicates_removed = 0

            for hash_key, files in self.duplicate_groups.items():
                if len(files) > 1:
                    # Choose canonical file based on strategy
                    if strategy == "pick_smallest":
                        canonical_file = min(files, key=lambda x: x.size)
                    elif strategy == "pick_newest":
                        canonical_file = max(files, key=lambda x: x.modified_time)
                    else:
                        canonical_file = files[0]  # Default to first

                    ssot_files.append(canonical_file)

                    # Remove duplicates
                    for file_info in files:
                        if file_info != canonical_file:
                            try:
                                # Create backup before deletion
                                await self._create_snapshot(file_info.path)

                                # Remove duplicate
                                os.remove(file_info.path)
                                duplicates_removed += 1
                                logger.info(f"Removed duplicate: {file_info.path}")

                            except Exception as e:
                                logger.warning(
                                    f"Could not remove {file_info.path}: {e}"
                                )

            # Create SSOT manifest
            await self.create_ssot_manifest(ssot_files)

            return ModuleResult(
                success=True,
                data={
                    "ssot_files": [f.path for f in ssot_files],
                    "duplicates_removed": duplicates_removed,
                    "ssot_manifest": str(self.ssot_manifest_path),
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error enforcing SSOT: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def create_ssot_manifest(
        self, ssot_files: List[FileInfo] = None
    ) -> ModuleResult:
        """Create SSOT manifest YAML file"""
        try:
            if ssot_files is None:
                ssot_files = [
                    f for f in self.file_registry.values() if not f.is_duplicate
                ]

            manifest = {
                "version": 1,
                "generated_at": datetime.now().isoformat(),
                "modules": [],
            }

            for file_info in ssot_files:
                module_info = {
                    "id": self._generate_module_id(file_info.path),
                    "path": str(Path(file_info.path).parent),
                    "entrypoint": file_info.path,
                    "owner": "system",
                    "hash": file_info.hash,
                    "last_modified": datetime.fromtimestamp(
                        file_info.modified_time
                    ).isoformat(),
                    "content_type": file_info.content_type,
                    "notes": "Canonical file - SSOT enforced",
                }
                manifest["modules"].append(module_info)

            # Save manifest
            with open(self.ssot_manifest_path, "w") as f:
                yaml.dump(manifest, f, default_flow_style=False)

            logger.info(f"Created SSOT manifest: {self.ssot_manifest_path}")

            return ModuleResult(
                success=True,
                data={
                    "manifest_path": str(self.ssot_manifest_path),
                    "modules_count": len(ssot_files),
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error creating SSOT manifest: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    def _generate_module_id(self, file_path: str) -> str:
        """Generate module ID from file path"""
        path_obj = Path(file_path)
        relative_path = path_obj.relative_to(self.base_path)
        return str(relative_path).replace("/", ".").replace("\\", ".")

    async def lock_files(
        self, file_paths: List[str], lock_type: str = "immutable"
    ) -> ModuleResult:
        """Apply locks to specified files"""
        try:
            logger.info(f"Locking {len(file_paths)} files with type: {lock_type}")

            locked_files = []

            for file_path in file_paths:
                try:
                    # Create snapshot before locking
                    await self._create_snapshot(file_path)

                    # Create lock file
                    lock_file_path = f"{file_path}.lock"
                    with open(lock_file_path, "w") as f:
                        f.write(
                            f"Locked by FileManagementModule at {datetime.now().isoformat()}\n"
                        )
                        f.write(f"Lock type: {lock_type}\n")
                        f.write(f"Original file: {file_path}\n")

                    locked_files.append(
                        {
                            "file": file_path,
                            "lock_file": lock_file_path,
                            "lock_type": lock_type,
                            "locked_at": datetime.now().isoformat(),
                        }
                    )

                except Exception as e:
                    logger.warning(f"Could not lock {file_path}: {e}")

            # Create lock manifest
            await self.create_lock_manifest(locked_files)

            return ModuleResult(
                success=True,
                data={
                    "locked_files": locked_files,
                    "lock_manifest": str(self.lock_manifest_path),
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error locking files: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def create_lock_manifest(self, locked_files: List[Dict]) -> ModuleResult:
        """Create lock manifest JSON file"""
        try:
            manifest = {
                "version": 1,
                "generated_at": datetime.now().isoformat(),
                "locks": [],
            }

            for lock_info in locked_files:
                # Calculate file hash
                file_path = Path(lock_info["file"])
                if file_path.exists():
                    file_hash = await self._calculate_file_hash(file_path)
                else:
                    file_hash = "unknown"

                lock_entry = {
                    "file": lock_info["file"],
                    "lock_type": lock_info["lock_type"],
                    "owner": "FileManagementModule",
                    "hash": file_hash,
                    "snapshot": f"s3://ssot-snapshots/{datetime.now().strftime('%Y-%m-%d')}/{file_hash}.tar.gz",
                    "reason": "SSOT enforcement",
                    "locked_at": lock_info["locked_at"],
                }
                manifest["locks"].append(lock_entry)

            # Save manifest
            with open(self.lock_manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)

            logger.info(f"Created lock manifest: {self.lock_manifest_path}")

            return ModuleResult(
                success=True,
                data={
                    "manifest_path": str(self.lock_manifest_path),
                    "locks_count": len(locked_files),
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error creating lock manifest: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _create_snapshot(self, file_path: str):
        """Create snapshot of file before modification"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_name = f"{Path(file_path).name}_{timestamp}.tar.gz"
            snapshot_path = self.snapshots_path / snapshot_name

            # Create compressed snapshot
            import tarfile

            with tarfile.open(snapshot_path, "w:gz") as tar:
                tar.add(file_path, arcname=Path(file_path).name)

            logger.info(f"Created snapshot: {snapshot_path}")

        except Exception as e:
            logger.error(f"Error creating snapshot for {file_path}: {e}")

    async def archive_unused(self, archive_path: str = None) -> ModuleResult:
        """Archive unused or obsolete files"""
        try:
            if archive_path is None:
                archive_path = str(self.base_path / "archive")

            archive_dir = Path(archive_path)
            archive_dir.mkdir(parents=True, exist_ok=True)

            archived_files = []

            # Find unused files (simplified logic)
            for file_path, file_info in self.file_registry.items():
                if (
                    file_info.content_type == "other" and file_info.size < 1000
                ):  # Small unknown files
                    try:
                        # Move to archive
                        archive_file = archive_dir / Path(file_path).name
                        shutil.move(file_path, str(archive_file))
                        archived_files.append(
                            {"original": file_path, "archived": str(archive_file)}
                        )
                    except Exception as e:
                        logger.warning(f"Could not archive {file_path}: {e}")

            return ModuleResult(
                success=True,
                data={"archived_files": archived_files, "archive_path": archive_path},
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error archiving unused files: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )


# Example usage and testing
async def main():
    """Test the File Management Module"""
    module = FileManagementModule()

    # Test file scanning
    result = await module.execute_function("scan_files")
    print(f"Scan result: {result}")

    # Test duplicate detection
    result = await module.execute_function("detect_duplicates")
    print(f"Duplicate detection result: {result}")

    # Test SSOT enforcement
    result = await module.execute_function("enforce_ssot")
    print(f"SSOT enforcement result: {result}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
