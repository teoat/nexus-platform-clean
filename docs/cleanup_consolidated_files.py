#!/usr/bin/env python3
"""
NEXUS Platform Documentation Cleanup Script

This script removes all files that have been consolidated into the new
consolidated documentation structure. It creates a backup before deletion
and provides a comprehensive report of all actions taken.

Author: NEXUS Development Team
Date: 2025-01-27
Version: 2.0
"""

import json
import shutil
from datetime import datetime


class DocumentationCleanup:
    """Comprehensive documentation cleanup and consolidation manager"""

    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.backup_dir = self.docs_dir / "archived_consolidated"
        self.cleanup_log = []
        self.consolidated_files = [
            "CONSOLIDATED_ARCHITECTURE.md",
            "CONSOLIDATED_IMPLEMENTATION_STATUS.md",
            "CONSOLIDATED_USER_DOCUMENTATION.md",
            "CONSOLIDATED_DEPLOYMENT_OPERATIONS.md",
            "CONSOLIDATED_DEVELOPMENT_GUIDE.md",
            "CONSOLIDATED_PLANNING_STRATEGY.md",
            "CONSOLIDATED_SECURITY_COMPLIANCE.md",
            "MASTER_DOCUMENTATION_INDEX.md",
        ]

    def run_cleanup(self) -> Dict[str, Any]:
        """Execute comprehensive documentation cleanup"""
        print("🧹 Starting NEXUS Platform Documentation Cleanup...")

        # Create backup directory
        self._create_backup_directory()

        # Define files to archive
        files_to_archive = self._get_files_to_archive()

        # Archive files
        archived_count = self._archive_files(files_to_archive)

        # Generate cleanup report
        report = self._generate_cleanup_report(archived_count)

        print(f"✅ Cleanup completed! Archived {archived_count} files.")
        print(f"📁 Backup created at: {self.backup_dir}")

        return report

    def _create_backup_directory(self):
        """Create backup directory with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.docs_dir / f"archived_consolidated_{timestamp}"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created backup directory: {self.backup_dir}")

    def _get_files_to_archive(self) -> List[Dict[str, str]]:
        """Get comprehensive list of files to archive"""
        files_to_archive = []

        # Architecture files (consolidated into CONSOLIDATED_ARCHITECTURE.md)
        architecture_files = [
            "architecture.md",
            "system-architecture.md",
            "pov-system-architecture.md",
            "file-structure.md",
            "file-organization.md",
            "structure.md",
            "ARCHITECTURE.md",
            "system_architecture.md",
            "pov_system_architecture.md",
            "file_structure.md",
            "file_organization.md",
        ]

        # Implementation status files (consolidated into CONSOLIDATED_IMPLEMENTATION_STATUS.md)
        implementation_files = [
            "COMPREHENSIVE_IMPLEMENTATION_COMPLETE.md",
            "STRATEGIC_IMPLEMENTATION_SUMMARY.md",
            "PHASE4_COMPLETION_REPORT.md",
            "NEXUS_COMPREHENSIVE_TASK_BREAKDOWN.md",
            "IMPLEMENTATION_COMPLETE.md",
            "SYSTEM_FIX_AND_LOCK_COMPLETE.md",
            "SYSTEM_LOCKDOWN_COMPLETE.md",
            "PHASE_1_ORCHESTRATION_COMPLETE.md",
            "COMPREHENSIVE_FIX_AND_LOCK_COMPLETE.md",
            "ADVANCED_PHASES_COMPLETE.md",
            "IMMEDIATE_NEXT_STEPS_COMPLETE.md",
            "AUTOMATION_SOLUTION_COMPLETE.md",
            "COMPREHENSIVE_SSOT_RECOMMENDATIONS_COMPLETE.md",
            "IMMEDIATE_RECOMMENDATIONS_APPLIED_COMPLETE.md",
            "PHASE_1_AND_PORT_ORCHESTRATION_COMPLETE.md",
            "phase-5-complete.md",
            "incremental-enhancements-complete-final.md",
            "complete-theme-implementation.md",
            "master-todo-completed.md",
            "complete-implementation.md",
            "frenly-ai-complete-analysis.md",
            "phase-2-complete.md",
            "autocomplete-valid.md",
            "reanalysis_complete.md",
        ]

        # User guide files (consolidated into CONSOLIDATED_USER_DOCUMENTATION.md)
        user_guide_files = [
            "USER_GUIDE.md",
            "USER_MANUAL.md",
            "TROUBLESHOOTING_GUIDE.md",
            "SECURITY_GUIDE.md",
            "PERFORMANCE_GUIDE.md",
            "INSTALLATION_GUIDE.md",
            "USER_GUIDE.md",
            "USER_MANUAL.md",
            "TROUBLESHOOTING_GUIDE.md",
            "SECURITY_GUIDE.md",
            "PERFORMANCE_GUIDE.md",
            "INSTALLATION_GUIDE.md",
        ]

        # Deployment files (consolidated into CONSOLIDATED_DEPLOYMENT_OPERATIONS.md)
        deployment_files = [
            "DEPLOYMENT_GUIDE.md",
            "DEPLOYMENT_GUIDES.md",
            "MIGRATION_GUIDE.md",
            "MIGRATION_GUIDES.md",
            "docker-daemon-readme.md",
            "deployment.md",
            "migration.md",
            "deployment_strategies.md",
        ]

        # Development files (consolidated into CONSOLIDATED_DEVELOPMENT_GUIDE.md)
        development_files = [
            "DEVELOPER_GUIDE.md",
            "DEVELOPER_GUIDES.md",
            "input_validation_guidelines.md",
            "manager_pattern_guide.md",
            "v3_migration_guide.md",
            "DEVELOPMENT_DOCUMENTATION.md",
            "DEVELOPMENT_PLANNING.md",
        ]

        # Planning files (consolidated into CONSOLIDATED_PLANNING_STRATEGY.md)
        planning_files = [
            "plan_b.md",
            "plan-b.md",
            "plana.md",
            "plana1.md",
            "plana2.md",
            "WORKSPACE_REORGANIZATION_PLAN.md",
            "workspace-reorganization-plan.md",
            "comprehensive-system-analysis-and-optimization-plan.md",
            "comprehensive-folder-orchestration-plan.md",
            "ZERO_REDUNDANCY_MANDATE_PLAN.md",
            "SSOT_ORCHESTRATION_MASTER_PLAN.md",
            "detailed-implementation-plan.md",
            "comprehensive-ui-ux-design-plan.md",
            "nexus-master-architectural-plan-v2.md",
            "immediate-action-plan.md",
            "next-phase-development-plan.md",
            "nags-integration-plan.md",
            "detailed-implementation-plan-system-architecture.md",
            "comprehensive-old-system-integration-plan.md",
            "parallel-batch-implementation-plan.md",
            "aggressive-implementation-plan.md",
            "IMMEDIATE_ACTION_PLAN.md",
            "NEXT_PHASE_DEVELOPMENT_PLAN.md",
            "COMPREHENSIVE_FOLDER_ORCHESTRATION_PLAN.md",
            "MASTER_PLANNING_DOCUMENTS.md",
            "optimization-implementation-plan.md",
            "critical-optimization-implementation-plan.md",
        ]

        # Security files (consolidated into CONSOLIDATED_SECURITY_COMPLIANCE.md)
        security_files = [
            "security_policies.md",
            "least_privilege_plan.md",
            "device_trust_plan.md",
            "identity_verification_plan.md",
            "zero_trust_design.md",
            "network_diagram.md",
            "threat_detection_architecture.md",
            "ai_threat_detection_engine_plan.md",
        ]

        # Index files (consolidated into MASTER_DOCUMENTATION_INDEX.md)
        index_files = [
            "MASTER_INDEX.md",
            "master-index.md",
            "DOCUMENTATION_INDEX.md",
            "documentation-index.md",
            "ARCHIVE_INDEX.md",
        ]

        # Summary files (consolidated into various consolidated files)
        summary_files = [
            "ssot-analysis-summary-20250917-185249.md",
            "ssot-analysis-summary-20250917-165812.md",
            "next-phase-implementation-summary-20250916-055009.md",
            "ssot-analysis-summary-20250917-184714.md",
            "ssot-analysis-summary-20250917-180452.md",
            "next-phase-implementation-summary-20250916-070225.md",
        ]

        # Combine all file categories
        all_files = (
            architecture_files
            + implementation_files
            + user_guide_files
            + deployment_files
            + development_files
            + planning_files
            + security_files
            + index_files
            + summary_files
        )

        # Create file list with categories
        for filename in all_files:
            file_path = self.docs_dir / filename
            if file_path.exists():
                category = self._get_file_category(
                    filename,
                    {
                        "architecture": architecture_files,
                        "implementation": implementation_files,
                        "user_guides": user_guide_files,
                        "deployment": deployment_files,
                        "development": development_files,
                        "planning": planning_files,
                        "security": security_files,
                        "index": index_files,
                        "summary": summary_files,
                    },
                )

                files_to_archive.append(
                    {
                        "filename": filename,
                        "path": str(file_path),
                        "category": category,
                        "size": file_path.stat().st_size,
                    }
                )

        return files_to_archive

    def _get_file_category(
        self, filename: str, categories: Dict[str, List[str]]
    ) -> str:
        """Determine file category based on filename"""
        for category, files in categories.items():
            if filename in files:
                return category
        return "other"

    def _archive_files(self, files_to_archive: List[Dict[str, str]]) -> int:
        """Archive files to backup directory"""
        archived_count = 0

        for file_info in files_to_archive:
            try:
                source_path = Path(file_info["path"])
                if source_path.exists():
                    # Create category subdirectory
                    category_dir = self.backup_dir / file_info["category"]
                    category_dir.mkdir(exist_ok=True)

                    # Move file to backup
                    dest_path = category_dir / file_info["filename"]
                    shutil.move(str(source_path), str(dest_path))

                    # Log the action
                    self.cleanup_log.append(
                        {
                            "action": "archived",
                            "file": file_info["filename"],
                            "category": file_info["category"],
                            "size": file_info["size"],
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

                    archived_count += 1
                    print(
                        f"📦 Archived: {file_info['filename']} ({file_info['category']})"
                    )

            except Exception as e:
                print(f"❌ Error archiving {file_info['filename']}: {e}")
                self.cleanup_log.append(
                    {
                        "action": "error",
                        "file": file_info["filename"],
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        return archived_count

    def _generate_cleanup_report(self, archived_count: int) -> Dict[str, Any]:
        """Generate comprehensive cleanup report"""
        report = {
            "cleanup_date": datetime.now().isoformat(),
            "archived_files": archived_count,
            "backup_location": str(self.backup_dir),
            "consolidated_files": self.consolidated_files,
            "cleanup_log": self.cleanup_log,
            "summary": {
                "total_files_archived": archived_count,
                "consolidated_documents": len(self.consolidated_files),
                "reduction_percentage": round(
                    (archived_count / (archived_count + len(self.consolidated_files)))
                    * 100,
                    2,
                ),
            },
        }

        # Save report to file
        report_path = self.docs_dir / "cleanup_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"📊 Cleanup report saved to: {report_path}")

        return report


def main():
    """Main execution function"""
    print("🚀 NEXUS Platform Documentation Cleanup Tool")
    print("=" * 50)

    # Initialize cleanup manager
    cleanup = DocumentationCleanup()

    # Auto-proceed with cleanup
    print("⚠️  Proceeding with automatic cleanup...")

    # Run cleanup
    try:
        report = cleanup.run_cleanup()

        print("\n" + "=" * 50)
        print("📊 CLEANUP SUMMARY")
        print("=" * 50)
        print(f"📦 Files Archived: {report['summary']['total_files_archived']}")
        print(
            f"📄 Consolidated Documents: {report['summary']['consolidated_documents']}"
        )
        print(f"📉 Reduction: {report['summary']['reduction_percentage']}%")
        print(f"📁 Backup Location: {report['backup_location']}")

        print("\n✅ Cleanup completed successfully!")
        print("🔗 All documentation is now consolidated into the new structure.")
        print("📚 See MASTER_DOCUMENTATION_INDEX.md for navigation.")

    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
