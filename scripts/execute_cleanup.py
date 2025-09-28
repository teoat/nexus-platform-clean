#!/usr/bin/env python3
"""
NEXUS Platform - Execute Duplicate Files Cleanup
Safely archives duplicate files based on analysis report
"""

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class CleanupExecutor:
    """Executes cleanup operations based on analysis report"""

    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        self.base_path = Path(base_path)
        self.archive_path = self.base_path / "archived_duplicates"
        self.archive_path.mkdir(exist_ok=True)

        # Load analysis report
        self.report_file = self.base_path / "cleanup_analysis_report.json"
        if not self.report_file.exists():
            print("❌ Analysis report not found. Run cleanup_duplicates.py first.")
            sys.exit(1)

        with open(self.report_file, "r") as f:
            self.report = json.load(f)

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
                json.dump(metadata, f, indent=2)

            print(f"📦 Archived: {file_path} -> {archive_file_path}")
            return True

        except Exception as e:
            print(f"❌ Failed to archive {file_path}: {e}")
            return False

    def cleanup_docker_compose_duplicates(self) -> Dict[str, int]:
        """Clean up duplicate docker-compose files"""
        print("🧹 Cleaning up Docker Compose duplicates...")

        duplicates = self.report["docker_compose"]["duplicates"]
        archived = 0
        errors = 0

        for hash_value, files in duplicates.items():
            if len(files) <= 1:
                continue

            # Keep the first file, archive the rest
            files_to_archive = files[1:]  # Skip the first one

            print(f"  Processing duplicate group (hash: {hash_value[:8]}...):")
            print(f"    Keeping: {files[0]}")

            for file_path_str in files_to_archive:
                file_path = Path(file_path_str)
                print(f"    Archiving: {file_path}")

                if self.archive_file(file_path, "docker_compose_duplicate"):
                    archived += 1
                else:
                    errors += 1

        return {"archived": archived, "errors": errors}

    def analyze_environment_files(self) -> Dict[str, List]:
        """Analyze environment files for consolidation opportunities"""
        print("🔍 Analyzing environment files for consolidation...")

        env_analysis = self.report["environment_files"]["analysis"]

        # Categorize environment files
        categories = {
            "production": [],
            "development": [],
            "staging": [],
            "examples": [],
            "backups": [],
            "other": [],
        }

        for file_path_str, info in env_analysis.items():
            file_path = Path(file_path_str)
            file_name = file_path.name.lower()

            if "production" in file_name:
                categories["production"].append(file_path_str)
            elif "development" in file_name or "dev" in file_name:
                categories["development"].append(file_path_str)
            elif "staging" in file_name:
                categories["staging"].append(file_path_str)
            elif "example" in file_name or "template" in file_name:
                categories["examples"].append(file_path_str)
            elif "backup" in file_name:
                categories["backups"].append(file_path_str)
            else:
                categories["other"].append(file_path_str)

        return categories

    def consolidate_environment_files(self) -> Dict[str, int]:
        """Consolidate environment files by archiving outdated ones"""
        print("🧹 Consolidating environment files...")

        categories = self.analyze_environment_files()

        archived = 0
        errors = 0

        # Archive backup files (safest to archive)
        print("  Archiving backup environment files...")
        for file_path_str in categories["backups"]:
            file_path = Path(file_path_str)
            print(f"    Archiving backup: {file_path}")
            if self.archive_file(file_path, "environment_backup"):
                archived += 1
            else:
                errors += 1

        # Archive example/template files that are not needed in production
        print("  Archiving example environment files...")
        for file_path_str in categories["examples"]:
            file_path = Path(file_path_str)
            # Keep main .env.example if it exists
            if file_path.name != ".env.example":
                print(f"    Archiving example: {file_path}")
                if self.archive_file(file_path, "environment_example"):
                    archived += 1
                else:
                    errors += 1

        # For other categories, be more conservative - just report
        print("  Environment files by category:")
        for category, files in categories.items():
            if files:
                print(f"    {category}: {len(files)} files")
                for file_path_str in files[:3]:  # Show first 3
                    print(f"      - {Path(file_path_str).name}")
                if len(files) > 3:
                    print(f"      ... and {len(files) - 3} more")

        return {"archived": archived, "errors": errors, "categories": categories}

    def create_cleanup_summary(self, results: Dict) -> Dict:
        """Create cleanup summary"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "operation": "duplicate_cleanup",
            "results": results,
            "archive_location": str(self.archive_path),
            "total_archived": sum(r.get("archived", 0) for r in results.values()),
            "total_errors": sum(r.get("errors", 0) for r in results.values()),
        }

        return summary

    def execute_cleanup(self) -> Dict:
        """Execute the full cleanup process"""
        print("🧹 Starting NEXUS Platform Cleanup Execution")
        print("=" * 50)

        results = {}

        # Step 1: Clean up Docker Compose duplicates
        print("\n1. Cleaning Docker Compose duplicates...")
        results["docker_compose"] = self.cleanup_docker_compose_duplicates()

        # Step 2: Consolidate environment files
        print("\n2. Consolidating environment files...")
        results["environment"] = self.consolidate_environment_files()

        # Create summary
        summary = self.create_cleanup_summary(results)

        # Save execution report
        execution_report = self.base_path / "cleanup_execution_report.json"
        with open(execution_report, "w") as f:
            json.dump(summary, f, indent=2)

        print(f"\n📋 Execution report saved to: {execution_report}")

        # Print final summary
        print("\n📊 CLEANUP SUMMARY:")
        print(
            f"  Docker Compose files archived: {results['docker_compose']['archived']}"
        )
        print(f"  Environment files archived: {results['environment']['archived']}")
        print(f"  Total files archived: {summary['total_archived']}")
        print(f"  Errors: {summary['total_errors']}")
        print(f"  Archive location: {summary['archive_location']}")

        if summary["total_errors"] == 0:
            print("\n✅ Cleanup completed successfully!")
        else:
            print(f"\n⚠️ Cleanup completed with {summary['total_errors']} errors.")

        return summary


def main():
    """Main execution function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--confirm":
        executor = CleanupExecutor()
        summary = executor.execute_cleanup()
    else:
        print("🧹 NEXUS Platform Cleanup Executor")
        print("=" * 40)
        print("This will archive duplicate files to prevent data loss.")
        print("Files will be moved to: archived_duplicates/")
        print("")
        print("Run with --confirm to execute cleanup.")
        print("")
        print("Analysis report: cleanup_analysis_report.json")


if __name__ == "__main__":
    main()
