#!/usr/bin/env python3
"""
NEXUS Platform - Cleanup and Archive System
Moves unneeded files to archived_bin and optimizes workspace
"""

import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WorkspaceCleanup:
    """Comprehensive workspace cleanup and archiving system"""
    
    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        self.base_path = Path(base_path)
        self.archived_bin = self.base_path / "archived_bin"
        self.cleanup_log = []
        
        # Files and directories to archive
        self.files_to_archive = {
            "backup_directories": [
                "backup_20250926_044357",
                "backup",
                "backups",
                "backup_phases"
            ],
            "duplicate_files": [
                "docker-compose.unified.yml",
                "docker-compose.staging.yml.backup",
                "Dockerfile.agents",
                "Dockerfile.auto-scaler",
                "Dockerfile.backup",
                "Dockerfile.frenly",
                "Dockerfile.frenly-brain",
                "Dockerfile.monitoring",
                "Dockerfile.orchestrated",
                "Dockerfile.self-healer",
                "Dockerfile.staging",
                "Dockerfile.secure"
            ],
            "old_implementation_files": [
                "execute_phases.py",
                "execute_ssot_phases.py",
                "live_execution_system.py",
                "direct_todo_executor.py",
                "directory_organizer.py",
                "doc_management_agent.py",
                "task_manager_agent.py",
                "quality_checker.py",
                "reference_updater.py",
                "unified_ssot_manager.py",
                "configuration_unifier.py",
                "parallel_file_merger.py",
                "apply_critical_components.py",
                "integrate_critical_components.py"
            ],
            "old_verification_files": [
                "comprehensive_verifier.py",
                "verification_batch_2.py",
                "verification_batch_3.py",
                "verification_batch_4.py",
                "verification_batch_5.py",
                "run_comprehensive_verification.py",
                "quick_fix_critical_issues.py",
                "run_verification_and_fixes.py",
                "simple_verification.py"
            ],
            "temporary_files": [
                "nexus_backend.log",
                "nexus_backup_20250925_205750.tar.gz",
                "dump.rdb",
                "nexus_redis_2024",
                "response_times.txt",
                "test123",
                "test.db"
            ],
            "old_reports": [
                "audit_report.json",
                "benchmark_results.json",
                "cleanup_analysis_report.json",
                "cleanup_execution_report.json",
                "frenly_validation_master_report.json",
                "load_test_results_20250926_020122.json",
                "phase_execution_summary.json",
                "phase3_integration_results.json",
                "phase3_validation_results.json",
                "production_readiness_report.json",
                "simple_integration_test_results.json",
                "simple_validation_results.json",
                "ssot_implementation_results.json",
                "validation_results.json",
                "NEXUS_SYSTEM_STARTUP_REPORT.json",
                "NEXUS_SYSTEM_VERIFICATION_REPORT.json",
                "autonomous_optimization_report.json",
                "critical_components_application_report.json",
                "critical_components_integration_report.json"
            ],
            "old_documentation": [
                "BEFORE_REFACTOR_STRUCTURE.txt",
                "COMPLETE_IMPLEMENTATION_SUMMARY.md",
                "COMPREHENSIVE_ANALYSIS_AND_REVIEW_V3.md",
                "COMPREHENSIVE_ANALYSIS_COMPLETE.md",
                "COMPREHENSIVE_APPLICATION_ANALYSIS.md",
                "COMPREHENSIVE_AUTOMATION_AND_SSOT_COMPLETE.md",
                "COMPREHENSIVE_AUTOMATION_REPORT.json",
                "COMPREHENSIVE_DIAGNOSTIC_REPORT.md",
                "COMPREHENSIVE_FRONTEND_BACKEND_MAPPING.md",
                "COMPREHENSIVE_IMPLEMENTATION_COMPLETE.md",
                "COMPREHENSIVE_IMPLEMENTATION_SUMMARY_V3.md",
                "COMPREHENSIVE_INTEGRATION_ANALYSIS.md",
                "COMPREHENSIVE_READINESS_AUDIT.md",
                "COMPREHENSIVE_SYSTEM_ARCHITECTURE_ANALYSIS.md",
                "COMPREHENSIVE_SYSTEM_OPTIMIZATION_REPORT.md",
                "COMPREHENSIVE_SYSTEM_REPORT.md",
                "COMPREHENSIVE_TODO_ANALYSIS_AND_AUTOMATION.md",
                "COMPREHENSIVE_WORKSPACE_ANALYSIS.md",
                "CONFIGURATION_INTELLIGENCE_REPORT.md",
                "CONSOLIDATION_COMPLETE_SUMMARY.md",
                "CONTAINERIZATION_COMPLETE.md",
                "CORE_FUNCTIONALITY_IMPLEMENTATION_SUMMARY.md",
                "CRITICAL_COMPONENTS_APPLICATION_COMPLETE.md",
                "CRITICAL_SECURITY_IMPLEMENTATION_COMPLETE.md",
                "DEPLOYMENT_GUIDE.md",
                "DEPLOYMENT_HALT_ANALYSIS_REPORT.md",
                "DEPLOYMENT_HALT_SUMMARY.md",
                "DEPLOYMENT_HALTED.md",
                "DEPLOYMENT_READY_REPORT.md",
                "DETAILED_TASK_BREAKDOWN.md",
                "DEVELOPMENT_GUIDE.md",
                "DOCUMENTATION_INTELLIGENCE_REPORT.md",
                "DUPLICATE_DETECTION_ANALYSIS.md",
                "E2E_TESTS_AND_MONITORING_COMPLETION_REPORT.md",
                "ENHANCED_INTEGRATION_GUIDE_V3.md",
                "ENTERPRISE_ENHANCEMENT_PLAN.md",
                "EXECUTE_CRITICAL_FIXES_NOW.md",
                "EXECUTION_STATUS_REPORT.md",
                "FINAL_COMPREHENSIVE_IMPLEMENTATION_COMPLETE_V3.md",
                "FINAL_CRITICAL_FIXES_COMPLETION_REPORT.md",
                "FINAL_DEPLOYMENT_READINESS_REPORT.md",
                "FINAL_IMPLEMENTATION_STATUS_V3.md",
                "FINAL_INTEGRATION_STATUS.md",
                "FINAL_PRODUCTION_SUMMARY.md",
                "FINAL_PROJECT_COMPLETION_REPORT.md",
                "FRENLY_AI_DOCUMENTATION.md",
                "FRENLY_AI_META_DOCUMENTATION.md",
                "FRONTEND_INTEGRATION.md",
                "FRONTEND_INTELLIGENCE_REPORT.md",
                "frontend_reorganization_plan.md",
                "HYBRID_SYSTEM_PROPOSAL.md",
                "IMMEDIATE_ACTION_PLAN.md",
                "IMMEDIATE_ACTIONS_IMPLEMENTED.md",
                "IMPLEMENT_NEXT_STEPS.md",
                "IMPLEMENTATION_STATUS_UPDATE.md",
                "IMPROVEMENTS_IMPLEMENTED.md",
                "INTELLIGENT_CONSOLIDATION_SYSTEM.md",
                "KUBERNETES_SYSTEMS_ANALYSIS.md",
                "LOCAL_DEPLOYMENT_GUIDE.md",
                "LOCAL_DEPLOYMENT_SUMMARY.md",
                "LOCAL_DEVELOPMENT_GUIDE.md",
                "MASTER_PLATFORM_OVERVIEW.md",
                "MASTER_TODO_FUTURE_PLANS.md",
                "MASTER_TODO_REFACTORED.md",
                "MASTER_TODO.md",
                "NEXUS_COMPREHENSIVE_ANALYSIS_AND_ENHANCEMENTS.md",
                "NEXUS_PLATFORM_BEST_PRACTICES_PLAN.md",
                "NEXUS_PLATFORM_ENHANCEMENT_ROADMAP.md",
                "NEXUS_SITE_PLAN.md",
                "NEXUS_SYSTEM_STATUS_COMPLETE.md",
                "NEXUS_V3_COMPLETE_IMPLEMENTATION_SUMMARY.md",
                "NUC_MAINTENANCE_IMPLEMENTATION_SUMMARY.md",
                "NUC_MAINTENANCE_SYSTEM_README.md",
                "OMNISCIENT_AI_OPTIMIZATION_COMPLETE.md",
                "OPTIMIZATION_NEXT_STEPS.md",
                "OPTIMIZATION_RESULTS.md",
                "OPTIMIZED_HYBRID_SYSTEM_ANALYSIS.md",
                "OPTIMIZED_SYSTEM_ARCHITECTURE.md",
                "ORCHESTRATION_INTEGRATION_GUIDE.md",
                "ORCHESTRATION_SYSTEM_README.md",
                "PHASE_1_COMPLETION_REPORT.md",
                "PHASE_1_PRODUCTION_OPTIMIZATION_COMPLETE.md",
                "PHASE_2_ADVANCED_FEATURES_IMPLEMENTATION.md",
                "PHASE_2_DETAILED_TASKS.md",
                "PHASE_3_DETAILED_TASKS.md",
                "PHASE_4_ADVANCED_FEATURES_PROPOSAL.md",
                "PHASE_4_WEEK1_COMPLETED.md",
                "PHASE_5_PRODUCTION_EXCELLENCE_PROPOSAL.md",
                "PHASE_5A_COMPLETE.md",
                "PHASE_5B_BATCH_1_COMPLETE.md",
                "PHASE_5B_BATCH_2_COMPLETE.md",
                "PHASE_5B_BATCH_3_COMPLETE.md",
                "PRODUCTION_BUILD_ANALYSIS_AND_FIXES.md",
                "PRODUCTION_BUILD_ANALYSIS_V3.md",
                "PRODUCTION_BUILD_COMPLETE_SUMMARY.md",
                "PRODUCTION_BUILD_SUMMARY_V3.md",
                "PRODUCTION_DEPLOYMENT_GUIDE_V3.md",
                "PRODUCTION_DEPLOYMENT_GUIDE.md",
                "PRODUCTION_IMPROVEMENTS_COMPLETION_REPORT.md",
                "PRODUCTION_READY_PROJECT.md",
                "PROJECT_STATUS_UPDATE.md",
                "QUICK_DEPLOYMENT_GUIDE_V3.md",
                "QUICK_FIX_GUIDE.md",
                "QUICK_START_GUIDE.md",
                "QUICK_START_LOCAL.md",
                "README_COMPLETE_SYSTEM.md",
                "README_DOCKER_K8S.md",
                "README_LAUNCHER_INTEGRATION.md",
                "README_NEXUS_PHASE_SYSTEM.md",
                "RECOMMENDATIONS_IMPLEMENTATION_COMPLETE.md",
                "REFACTORING_PLAN.md",
                "ROUTING_OPTIMIZATION_PLAN.md",
                "SIMPLE_DEPLOYMENT_REPORT_20250924_122401.md",
                "site_plan_validation_report.md",
                "SSOT_ANALYSIS_AND_PROPOSAL.md",
                "SSOT_CONSOLIDATION_REPORT.md",
                "SSOT_DOCUMENTATION_SYSTEM_README.md",
                "SSOT_IMPLEMENTATION_GUIDE.md",
                "SSOT_PHASE_2_3_IMPLEMENTATION_COMPLETE.md",
                "SUPREME_AI_ANALYSIS_REPORT.md",
                "SYSTEM_INTELLIGENCE_REPORT.md",
                "SYSTEM_LAUNCH_SUCCESS.md",
                "SYSTEM_OPTIMIZATION_COMPLETE.md",
                "SYSTEM_VS_FRENLY_AI_README.md",
                "SYSTEM_WORKFLOW_DIAGRAMS.md",
                "TASK_MANAGEMENT_SYSTEM.md",
                "TODO_EXECUTION_REPORT.md",
                "TODO_IMPLEMENTATION_SUMMARY.md",
                "TODO_INTELLIGENCE_ANALYSIS.md",
                "TODO_INTELLIGENCE_REPORT.md",
                "TYPESCRIPT_IMPLEMENTATION_COMPLETE.md",
                "ULTIMATE_COMPLETION_SUMMARY.md",
                "ULTIMATE_SYSTEM_README.md",
                "USER_TRAINING_GUIDE.md",
                "VALIDATION_REPORT_CONFIGURATION.md",
                "VALIDATION_REPORT_MARKDOWN_LINKS.md",
                "VALIDATION_REPORT_PYTHON_IMPORTS.md",
                "VALIDATION_REPORT_SYSTEM_INTEGRITY.md",
                "VALIDATION_REPORT_TYPESCRIPT_IMPORTS.md",
                "WORKSPACE_INVENTORY.md"
            ]
        }
        
        # Files to keep (production-ready)
        self.files_to_keep = [
            "README.md",
            "package.json",
            "requirements.txt",
            "docker-compose.yml",
            "docker-compose.prod.yml",
            "Dockerfile",
            "Dockerfile.backend",
            "Dockerfile.frontend",
            "Dockerfile.prod",
            "nginx.conf",
            "gunicorn.conf.py",
            ".env",
            "start_production.sh",
            "focused_verification.py",
            "deploy_production_complete.py",
            "demo_production_system.py",
            "IMPLEMENTATION_COMPLETE_FINAL.md",
            "FINAL_PRODUCTION_READY_SUMMARY.md",
            "backend/",
            "frontend/",
            "docker/",
            "k8s/",
            "monitoring/",
            "security/",
            "tests/",
            "docs/",
            "scripts/",
            "services/",
            "modules/",
            "integrations/",
            "infrastructure/",
            "e2e-tests/",
            "coordination-hub/",
            "frenly_ai/",
            "frenly_ai_meta/",
            "nexus/",
            "ai-analytics/",
            "discovery/",
            "learning_insights/",
            "learning_patterns/",
            "prediction_models/",
            "recommendation_rules/",
            "ssot/",
            "ssot_plan/",
            "audit/",
            "data/",
            "database/",
            "logs/",
            "locks/",
            "maintenance/",
            "reports/",
            "security-reports/",
            "tools/",
            "nexus_platform.db",
            "nexus.db",
            "redis.conf",
            "redis.acl",
            "frenly_ai_rules.json",
            "pyproject.toml",
            "pytest.ini",
            "jest.config.js",
            "babel.config.js",
            "tsconfig.json",
            "tsconfig.base.json"
        ]
    
    def run_cleanup(self):
        """Run complete workspace cleanup"""
        logger.info("🧹 Starting comprehensive workspace cleanup...")
        print("\n" + "="*80)
        print("🧹 NEXUS PLATFORM - WORKSPACE CLEANUP & ARCHIVING")
        print("="*80)
        
        try:
            # Create archived_bin directory
            self._create_archive_directory()
            
            # Archive files by category
            self._archive_backup_directories()
            self._archive_duplicate_files()
            self._archive_old_implementation_files()
            self._archive_old_verification_files()
            self._archive_temporary_files()
            self._archive_old_reports()
            self._archive_old_documentation()
            
            # Clean up empty directories
            self._cleanup_empty_directories()
            
            # Generate cleanup report
            self._generate_cleanup_report()
            
            # Print summary
            self._print_cleanup_summary()
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            print(f"\n❌ CLEANUP FAILED: {e}")
    
    def _create_archive_directory(self):
        """Create archived_bin directory structure"""
        print("\n📁 Creating archive directory structure...")
        
        # Create main archive directory
        self.archived_bin.mkdir(exist_ok=True)
        
        # Create subdirectories
        subdirs = [
            "backup_directories",
            "duplicate_files",
            "old_implementation",
            "old_verification",
            "temporary_files",
            "old_reports",
            "old_documentation",
            "logs"
        ]
        
        for subdir in subdirs:
            (self.archived_bin / subdir).mkdir(exist_ok=True)
        
        print("✅ Archive directory structure created")
        self._log_cleanup_step("create_archive", "Archive directory structure created", "success")
    
    def _archive_backup_directories(self):
        """Archive backup directories"""
        print("\n📦 Archiving backup directories...")
        
        for backup_dir in self.files_to_archive["backup_directories"]:
            source_path = self.base_path / backup_dir
            if source_path.exists():
                dest_path = self.archived_bin / "backup_directories" / backup_dir
                try:
                    shutil.move(str(source_path), str(dest_path))
                    print(f"  ✅ Archived: {backup_dir}")
                    self._log_cleanup_step("archive_backup", f"Archived {backup_dir}", "success")
                except Exception as e:
                    print(f"  ❌ Failed to archive {backup_dir}: {e}")
                    self._log_cleanup_step("archive_backup", f"Failed to archive {backup_dir}: {e}", "error")
            else:
                print(f"  ⚠️ Not found: {backup_dir}")
    
    def _archive_duplicate_files(self):
        """Archive duplicate files"""
        print("\n📄 Archiving duplicate files...")
        
        for duplicate_file in self.files_to_archive["duplicate_files"]:
            source_path = self.base_path / duplicate_file
            if source_path.exists():
                dest_path = self.archived_bin / "duplicate_files" / duplicate_file
                try:
                    shutil.move(str(source_path), str(dest_path))
                    print(f"  ✅ Archived: {duplicate_file}")
                    self._log_cleanup_step("archive_duplicate", f"Archived {duplicate_file}", "success")
                except Exception as e:
                    print(f"  ❌ Failed to archive {duplicate_file}: {e}")
                    self._log_cleanup_step("archive_duplicate", f"Failed to archive {duplicate_file}: {e}", "error")
            else:
                print(f"  ⚠️ Not found: {duplicate_file}")
    
    def _archive_old_implementation_files(self):
        """Archive old implementation files"""
        print("\n🔧 Archiving old implementation files...")
        
        for impl_file in self.files_to_archive["old_implementation_files"]:
            source_path = self.base_path / impl_file
            if source_path.exists():
                dest_path = self.archived_bin / "old_implementation" / impl_file
                try:
                    shutil.move(str(source_path), str(dest_path))
                    print(f"  ✅ Archived: {impl_file}")
                    self._log_cleanup_step("archive_implementation", f"Archived {impl_file}", "success")
                except Exception as e:
                    print(f"  ❌ Failed to archive {impl_file}: {e}")
                    self._log_cleanup_step("archive_implementation", f"Failed to archive {impl_file}: {e}", "error")
            else:
                print(f"  ⚠️ Not found: {impl_file}")
    
    def _archive_old_verification_files(self):
        """Archive old verification files"""
        print("\n🔍 Archiving old verification files...")
        
        for verif_file in self.files_to_archive["old_verification_files"]:
            source_path = self.base_path / verif_file
            if source_path.exists():
                dest_path = self.archived_bin / "old_verification" / verif_file
                try:
                    shutil.move(str(source_path), str(dest_path))
                    print(f"  ✅ Archived: {verif_file}")
                    self._log_cleanup_step("archive_verification", f"Archived {verif_file}", "success")
                except Exception as e:
                    print(f"  ❌ Failed to archive {verif_file}: {e}")
                    self._log_cleanup_step("archive_verification", f"Failed to archive {verif_file}: {e}", "error")
            else:
                print(f"  ⚠️ Not found: {verif_file}")
    
    def _archive_temporary_files(self):
        """Archive temporary files"""
        print("\n🗑️ Archiving temporary files...")
        
        for temp_file in self.files_to_archive["temporary_files"]:
            source_path = self.base_path / temp_file
            if source_path.exists():
                dest_path = self.archived_bin / "temporary_files" / temp_file
                try:
                    shutil.move(str(source_path), str(dest_path))
                    print(f"  ✅ Archived: {temp_file}")
                    self._log_cleanup_step("archive_temporary", f"Archived {temp_file}", "success")
                except Exception as e:
                    print(f"  ❌ Failed to archive {temp_file}: {e}")
                    self._log_cleanup_step("archive_temporary", f"Failed to archive {temp_file}: {e}", "error")
            else:
                print(f"  ⚠️ Not found: {temp_file}")
    
    def _archive_old_reports(self):
        """Archive old reports"""
        print("\n📊 Archiving old reports...")
        
        for report_file in self.files_to_archive["old_reports"]:
            source_path = self.base_path / report_file
            if source_path.exists():
                dest_path = self.archived_bin / "old_reports" / report_file
                try:
                    shutil.move(str(source_path), str(dest_path))
                    print(f"  ✅ Archived: {report_file}")
                    self._log_cleanup_step("archive_reports", f"Archived {report_file}", "success")
                except Exception as e:
                    print(f"  ❌ Failed to archive {report_file}: {e}")
                    self._log_cleanup_step("archive_reports", f"Failed to archive {report_file}: {e}", "error")
            else:
                print(f"  ⚠️ Not found: {report_file}")
    
    def _archive_old_documentation(self):
        """Archive old documentation"""
        print("\n📚 Archiving old documentation...")
        
        for doc_file in self.files_to_archive["old_documentation"]:
            source_path = self.base_path / doc_file
            if source_path.exists():
                dest_path = self.archived_bin / "old_documentation" / doc_file
                try:
                    shutil.move(str(source_path), str(dest_path))
                    print(f"  ✅ Archived: {doc_file}")
                    self._log_cleanup_step("archive_documentation", f"Archived {doc_file}", "success")
                except Exception as e:
                    print(f"  ❌ Failed to archive {doc_file}: {e}")
                    self._log_cleanup_step("archive_documentation", f"Failed to archive {doc_file}: {e}", "error")
            else:
                print(f"  ⚠️ Not found: {doc_file}")
    
    def _cleanup_empty_directories(self):
        """Clean up empty directories"""
        print("\n🧹 Cleaning up empty directories...")
        
        # Find and remove empty directories
        for root, dirs, files in os.walk(self.base_path, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    if not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        print(f"  ✅ Removed empty directory: {dir_path.relative_to(self.base_path)}")
                        self._log_cleanup_step("cleanup_empty", f"Removed empty directory: {dir_path.relative_to(self.base_path)}", "success")
                except Exception as e:
                    print(f"  ⚠️ Could not remove directory {dir_path}: {e}")
    
    def _log_cleanup_step(self, step: str, message: str, status: str):
        """Log cleanup step"""
        self.cleanup_log.append({
            "step": step,
            "message": message,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })
    
    def _generate_cleanup_report(self):
        """Generate cleanup report"""
        logger.info("📊 Generating cleanup report...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "cleanup_log": self.cleanup_log,
            "summary": {
                "total_steps": len(self.cleanup_log),
                "successful_steps": len([log for log in self.cleanup_log if log["status"] == "success"]),
                "warning_steps": len([log for log in self.cleanup_log if log["status"] == "warning"]),
                "error_steps": len([log for log in self.cleanup_log if log["status"] == "error"])
            },
            "archived_categories": {
                "backup_directories": len(self.files_to_archive["backup_directories"]),
                "duplicate_files": len(self.files_to_archive["duplicate_files"]),
                "old_implementation": len(self.files_to_archive["old_implementation_files"]),
                "old_verification": len(self.files_to_archive["old_verification_files"]),
                "temporary_files": len(self.files_to_archive["temporary_files"]),
                "old_reports": len(self.files_to_archive["old_reports"]),
                "old_documentation": len(self.files_to_archive["old_documentation"])
            }
        }
        
        # Save report
        report_path = self.base_path / "cleanup_report.json"
        with open(report_path, 'w') as f:
            import json
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Cleanup report saved to {report_path}")
    
    def _print_cleanup_summary(self):
        """Print cleanup summary"""
        print("\n" + "="*80)
        print("🎯 WORKSPACE CLEANUP COMPLETE")
        print("="*80)
        
        successful_steps = len([log for log in self.cleanup_log if log["status"] == "success"])
        warning_steps = len([log for log in self.cleanup_log if log["status"] == "warning"])
        error_steps = len([log for log in self.cleanup_log if log["status"] == "error"])
        
        print(f"✅ Successful Operations: {successful_steps}")
        print(f"⚠️ Warning Operations: {warning_steps}")
        print(f"❌ Error Operations: {error_steps}")
        
        print("\n📁 Archive Structure:")
        print("  📦 backup_directories/ - Old backup folders")
        print("  📄 duplicate_files/ - Duplicate configuration files")
        print("  🔧 old_implementation/ - Old implementation scripts")
        print("  🔍 old_verification/ - Old verification scripts")
        print("  🗑️ temporary_files/ - Temporary and log files")
        print("  📊 old_reports/ - Old JSON reports")
        print("  📚 old_documentation/ - Old documentation files")
        
        print("\n🎯 Production-Ready Files Kept:")
        print("  ✅ Core application files")
        print("  ✅ Production configuration")
        print("  ✅ Essential documentation")
        print("  ✅ Active verification system")
        print("  ✅ Deployment scripts")
        
        if error_steps == 0:
            print("\n🎉 CLEANUP SUCCESSFUL!")
            print("Workspace is now clean and optimized for production!")
        else:
            print(f"\n⚠️ CLEANUP COMPLETED WITH {error_steps} ERRORS")
            print("Please check the cleanup report for details.")
        
        print("="*80)


# Main execution
def main():
    """Main execution function"""
    cleanup = WorkspaceCleanup()
    cleanup.run_cleanup()


if __name__ == "__main__":
    main()
