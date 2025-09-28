#!/usr/bin/env python3
"""
NEXUS Platform - Duplicate Files Cleanup Script
Analyzes and cleans up duplicate files identified in production readiness validation
"""

import hashlib
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple


class DuplicateCleanup:
    """Handles cleanup of duplicate files and consolidation of environment files"""

    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        self.base_path = Path(base_path)
        self.archive_path = self.base_path / "archived_duplicates"
        self.archive_path.mkdir(exist_ok=True)

        # Files to exclude from cleanup
        self.exclude_patterns = [
            ".git",
            "node_modules",
            "__pycache__",
            ".pytest_cache",
            "archived_bin",  # Already archived
            "archived_duplicates",  # Our archive
        ]

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        if not file_path.exists():
            return ""

        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return ""

    def find_duplicate_files(self, file_patterns: List[str]) -> Dict[str, List[Path]]:
        """Find duplicate files based on patterns"""
        duplicates = {}

        for pattern in file_patterns:
            files = []
            for file_path in self.base_path.rglob(pattern):
                if not any(excl in str(file_path) for excl in self.exclude_patterns):
                    files.append(file_path)

            # Group by content hash
            hash_groups = {}
            for file_path in files:
                file_hash = self.calculate_file_hash(file_path)
                if file_hash:
                    if file_hash not in hash_groups:
                        hash_groups[file_hash] = []
                    hash_groups[file_hash].append(file_path)

            # Only keep groups with duplicates
            for file_hash, file_list in hash_groups.items():
                if len(file_list) > 1:
                    duplicates[pattern] = file_list

        return duplicates

    def analyze_file_differences(self, files: List[Path]) -> Dict[str, Dict]:
        """Analyze differences between files"""
        analysis = {}

        for file_path in files:
            try:
                stat = file_path.stat()
                analysis[str(file_path)] = {
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "exists": True,
                }
            except Exception as e:
                analysis[str(file_path)] = {"error": str(e), "exists": False}

        return analysis

    def cleanup_docker_compose_files(self) -> Dict[str, any]:
        """Clean up docker-compose files"""
        print("🔍 Analyzing Docker Compose files...")

        docker_files = []
        for pattern in ["docker-compose*.yml", "docker-compose.yml"]:
            docker_files.extend(list(self.base_path.rglob(pattern)))

        # Filter out archived files
        docker_files = [f for f in docker_files if "archived_bin" not in str(f)]

        print(f"Found {len(docker_files)} Docker Compose files")

        # Analyze each file
        file_analysis = {}
        for file_path in docker_files:
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                    file_hash = hashlib.sha256(content.encode()).hexdigest()

                stat = file_path.stat()
                file_analysis[str(file_path)] = {
                    "hash": file_hash,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "services": content.count("services:")
                    if "services:" in content
                    else 0,
                }
            except Exception as e:
                file_analysis[str(file_path)] = {"error": str(e)}

        # Group by hash to find true duplicates
        hash_groups = {}
        for file_path, info in file_analysis.items():
            file_hash = info.get("hash", "")
            if file_hash:
                if file_hash not in hash_groups:
                    hash_groups[file_hash] = []
                hash_groups[file_hash].append(file_path)

        # Identify duplicates (same hash)
        duplicates = {k: v for k, v in hash_groups.items() if len(v) > 1}

        print(f"Found {len(duplicates)} duplicate groups")

        return {
            "total_files": len(docker_files),
            "duplicates": duplicates,
            "analysis": file_analysis,
        }

    def cleanup_environment_files(self) -> Dict[str, any]:
        """Clean up environment files"""
        print("🔍 Analyzing environment files...")

        env_files = []
        for pattern in ["*.env", ".env*"]:
            env_files.extend(list(self.base_path.rglob(pattern)))

        # Filter out archived and node_modules
        env_files = [
            f
            for f in env_files
            if "archived_bin" not in str(f) and "node_modules" not in str(f)
        ]

        print(f"Found {len(env_files)} environment files")

        # Analyze each file
        file_analysis = {}
        for file_path in env_files:
            try:
                with open(file_path, "r") as f:
                    content = f.read()

                stat = file_path.stat()
                lines = content.split("\n")
                variables = [
                    line.split("=")[0].strip()
                    for line in lines
                    if "=" in line and not line.strip().startswith("#")
                ]

                file_analysis[str(file_path)] = {
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "variables": len(variables),
                    "has_secrets": any(
                        secret in content.upper()
                        for secret in ["PASSWORD", "SECRET", "KEY", "TOKEN"]
                    ),
                }
            except Exception as e:
                file_analysis[str(file_path)] = {"error": str(e)}

        return {"total_files": len(env_files), "analysis": file_analysis}

    def archive_file(self, file_path: Path, reason: str = "duplicate") -> bool:
        """Archive a file safely"""
        try:
            # Create archive subdirectory structure
            relative_path = file_path.relative_to(self.base_path)
            archive_file_path = self.archive_path / relative_path

            # Ensure parent directory exists
            archive_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Move file
            shutil.move(str(file_path), str(archive_file_path))

            # Create metadata file
            metadata_file = archive_file_path.with_suffix(".metadata")
            metadata = {
                "original_path": str(file_path),
                "archived_at": datetime.now().isoformat(),
                "reason": reason,
                "size": archive_file_path.stat().st_size
                if archive_file_path.exists()
                else 0,
            }

            with open(metadata_file, "w") as f:
                import json

                json.dump(metadata, f, indent=2)

            print(f"📦 Archived: {file_path} -> {archive_file_path}")
            return True

        except Exception as e:
            print(f"❌ Failed to archive {file_path}: {e}")
            return False

    def generate_cleanup_report(self) -> Dict[str, any]:
        """Generate comprehensive cleanup report"""
        print("📊 Generating cleanup analysis report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "docker_compose": self.cleanup_docker_compose_files(),
            "environment_files": self.cleanup_environment_files(),
            "recommendations": [],
        }

        # Generate recommendations
        docker_dupes = report["docker_compose"]["duplicates"]
        if docker_dupes:
            report["recommendations"].append(
                {
                    "category": "docker_compose",
                    "action": "archive_duplicates",
                    "description": f"Archive {len(docker_dupes)} groups of duplicate docker-compose files",
                    "files_to_archive": sum(
                        len(files) - 1 for files in docker_dupes.values()
                    ),
                }
            )

        env_files = report["environment_files"]["analysis"]
        env_count = len(env_files)
        if env_count > 5:  # More than 5 env files is excessive
            report["recommendations"].append(
                {
                    "category": "environment",
                    "action": "consolidate",
                    "description": f"Consolidate {env_count} environment files into organized structure",
                    "files_to_review": env_count,
                }
            )

        return report


def main():
    """Main cleanup function"""
    print("🧹 NEXUS Platform Duplicate Files Cleanup")
    print("=" * 50)

    cleanup = DuplicateCleanup()

    # Generate report
    report = cleanup.generate_cleanup_report()

    # Save report
    report_file = cleanup.base_path / "cleanup_analysis_report.json"
    import json

    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"📋 Cleanup analysis report saved to: {report_file}")

    # Print summary
    print("\n📊 SUMMARY:")
    print(f"  Docker Compose files: {report['docker_compose']['total_files']}")
    print(f"  Environment files: {report['environment_files']['total_files']}")
    print(f"  Duplicate groups: {len(report['docker_compose']['duplicates'])}")
    print(f"  Recommendations: {len(report['recommendations'])}")

    if report["recommendations"]:
        print("\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"  {i}. {rec['description']}")

    print("\n✅ Analysis complete. Run with --cleanup to execute cleanup.")


if __name__ == "__main__":
    main()
