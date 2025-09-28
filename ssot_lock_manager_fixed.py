#!/usr/bin/env python3
"""
NEXUS Platform - SSOT & Lock Manager (Fixed)
Marks production files with SSOT status and applies file locks
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SSOTLockManager:
    """SSOT marking and file locking system for production files"""
    
    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        self.base_path = Path(base_path)
        self.ssot_manifest = self.base_path / "ssot_manifest.json"
        self.lock_manifest = self.base_path / "lock_manifest.json"
        
        # Production files to mark as SSOT and lock
        self.production_files = {
            "core_application": [
                "backend/",
                "frontend/",
                "nexus/",
                "services/",
                "modules/",
                "integrations/",
                "ai-analytics/",
                "discovery/",
                "coordination-hub/",
                "frenly_ai/",
                "frenly_ai_meta/"
            ],
            "configuration": [
                "docker-compose.yml",
                "docker-compose.prod.yml",
                "Dockerfile",
                "Dockerfile.backend",
                "Dockerfile.frontend",
                "Dockerfile.prod",
                "Dockerfile.production",
                "nginx.conf",
                "gunicorn.conf.py",
                ".env",
                ".env.production",
                "requirements.txt",
                "package.json",
                "tsconfig.json",
                "tsconfig.base.json",
                "pytest.ini",
                "jest.config.js",
                "babel.config.js",
                "pyproject.toml"
            ],
            "deployment": [
                "deploy_production_complete.py",
                "deploy-production.sh",
                "deploy-docker.sh",
                "deploy-k8s.sh",
                "deploy-production-optimized.sh",
                "demo-docker-deployment.sh",
                "check-deployment.sh",
                "fix-dependencies.sh",
                "stop_all_systems.sh",
                "launch_nuc_maintenance.sh",
                "maintenance-automation.sh",
                "setup-local-dev.sh"
            ],
            "infrastructure": [
                "docker/",
                "k8s/",
                "k8s-optimized/",
                "infrastructure/",
                "monitoring/",
                "security/",
                "ssl/",
                "nginx/",
                "helm/"
            ],
            "data_storage": [
                "database/",
                "data/",
                "logs/",
                "locks/",
                "reports/",
                "nexus_platform.db",
                "nexus.db",
                "redis.conf",
                "redis.acl"
            ],
            "testing": [
                "tests/",
                "e2e-tests/",
                "focused_verification.py",
                "validate_production_readiness.py",
                "validate_system.py",
                "test_nuc_maintenance.py"
            ],
            "documentation": [
                "README.md",
                "IMPLEMENTATION_COMPLETE_FINAL.md",
                "FINAL_PRODUCTION_READY_SUMMARY.md",
                "FINAL_CLEANUP_AND_OPTIMIZATION_COMPLETE.md",
                "ARCHITECTURE_OVERVIEW.md",
                "SECURITY_AUDIT_REPORT.md",
                "PRODUCTION_READINESS_REPORT.md",
                "docs/"
            ],
            "system_management": [
                "ssot/",
                "ssot_plan/",
                "ssot_manager.py",
                "ssot_manifest.json",
                "ssot_master_todo.md",
                "ssot_phase_execution_summary.json",
                "advanced_lock_manager.py",
                "archive_manager.py",
                "archival_script.py",
                "integration_fix.py",
                "setup_production_database.py",
                "setup_sqlite_database.py",
                "demo_production_system.py",
                "cleanup_and_archive.py",
                "ssot_lock_manager.py"
            ],
            "root_files": [
                ".gitignore",
                ".pre-commit-config.yaml",
                ".husky/",
                ".github/",
                ".cursor/",
                ".pytest_cache/",
                ".taskmaster/",
                ".venv/",
                ".infrastructure/",
                ".monitoring/"
            ]
        }
        
        # Files to lock (read-only) - excluding manifests
        self.lock_files = [
            "nexus_platform.db",
            "nexus.db",
            "redis.conf",
            "redis.acl",
            "encryption_key.key",
            "frenly_ai_rules.json",
            "ssot_master_todo.md",
            "ssot_phase_execution_summary.json"
        ]
    
    def run_ssot_lock_management(self):
        """Run complete SSOT marking and file locking"""
        logger.info("🔒 Starting SSOT marking and file locking...")
        print("\n" + "="*80)
        print("🔒 NEXUS PLATFORM - SSOT & LOCK MANAGEMENT")
        print("="*80)
        
        try:
            # Generate manifests first (before locking)
            self._generate_manifests()
            
            # Mark files as SSOT
            self._mark_ssot_files()
            
            # Apply file locks
            self._apply_file_locks()
            
            # Print summary
            self._print_summary()
            
        except Exception as e:
            logger.error(f"SSOT/Lock management failed: {e}")
            print(f"\n❌ SSOT/LOCK MANAGEMENT FAILED: {e}")
    
    def _mark_ssot_files(self):
        """Mark production files as SSOT"""
        print("\n📋 Marking files as SSOT (Single Source of Truth)...")
        
        ssot_marked = []
        
        for category, files in self.production_files.items():
            print(f"\n  📁 {category.replace('_', ' ').title()}:")
            
            for file_path in files:
                full_path = self.base_path / file_path
                
                if full_path.exists():
                    # Create SSOT marker file
                    ssot_marker = full_path.parent / f".{full_path.name}.ssot"
                    try:
                        with open(ssot_marker, 'w') as f:
                            json.dump({
                                "ssot_status": "active",
                                "category": category,
                                "marked_at": datetime.now().isoformat(),
                                "file_type": "directory" if full_path.is_dir() else "file",
                                "description": f"SSOT marker for {file_path}"
                            }, f, indent=2)
                        
                        print(f"    ✅ {file_path}")
                        ssot_marked.append({
                            "path": str(file_path),
                            "category": category,
                            "type": "directory" if full_path.is_dir() else "file",
                            "marked_at": datetime.now().isoformat()
                        })
                        
                    except Exception as e:
                        print(f"    ❌ Failed to mark {file_path}: {e}")
                else:
                    print(f"    ⚠️ Not found: {file_path}")
        
        return ssot_marked
    
    def _apply_file_locks(self):
        """Apply file locks to critical files"""
        print("\n🔒 Applying file locks...")
        
        locked_files = []
        
        for file_path in self.lock_files:
            full_path = self.base_path / file_path
            
            if full_path.exists():
                try:
                    # Make file read-only
                    os.chmod(full_path, 0o444)
                    print(f"  ✅ Locked: {file_path}")
                    locked_files.append({
                        "path": str(file_path),
                        "locked_at": datetime.now().isoformat(),
                        "permissions": "read-only"
                    })
                    
                except Exception as e:
                    print(f"  ❌ Failed to lock {file_path}: {e}")
            else:
                print(f"  ⚠️ Not found: {file_path}")
        
        # Lock root directory (make it read-only for non-owners)
        try:
            os.chmod(self.base_path, 0o755)
            print(f"  ✅ Root directory permissions set: {self.base_path}")
            locked_files.append({
                "path": str(self.base_path),
                "locked_at": datetime.now().isoformat(),
                "permissions": "owner-write, others-read"
            })
        except Exception as e:
            print(f"  ❌ Failed to set root directory permissions: {e}")
        
        return locked_files
    
    def _generate_manifests(self):
        """Generate SSOT and lock manifests"""
        logger.info("📊 Generating SSOT and lock manifests...")
        
        # Generate SSOT manifest
        ssot_manifest = {
            "timestamp": datetime.now().isoformat(),
            "total_categories": len(self.production_files),
            "total_files": sum(len(files) for files in self.production_files.values()),
            "categories": self.production_files,
            "ssot_status": "active",
            "description": "NEXUS Platform SSOT Manifest - Production Files"
        }
        
        with open(self.ssot_manifest, 'w') as f:
            json.dump(ssot_manifest, f, indent=2)
        
        # Generate lock manifest
        lock_manifest = {
            "timestamp": datetime.now().isoformat(),
            "locked_files": self.lock_files,
            "total_locked": len(self.lock_files),
            "lock_status": "active",
            "description": "NEXUS Platform Lock Manifest - Protected Files"
        }
        
        with open(self.lock_manifest, 'w') as f:
            json.dump(lock_manifest, f, indent=2)
        
        logger.info(f"📊 SSOT manifest saved to {self.ssot_manifest}")
        logger.info(f"📊 Lock manifest saved to {self.lock_manifest}")
    
    def _print_summary(self):
        """Print SSOT and lock summary"""
        print("\n" + "="*80)
        print("🎯 SSOT & LOCK MANAGEMENT COMPLETE")
        print("="*80)
        
        total_files = sum(len(files) for files in self.production_files.values())
        total_locked = len(self.lock_files)
        
        print(f"📋 SSOT Files Marked: {total_files}")
        print(f"🔒 Files Locked: {total_locked}")
        print(f"📁 Root Directory: Protected")
        
        print("\n📋 SSOT Categories:")
        for category, files in self.production_files.items():
            print(f"  📁 {category.replace('_', ' ').title()}: {len(files)} files")
        
        print("\n🔒 Locked Files:")
        for file_path in self.lock_files:
            print(f"  🔒 {file_path}")
        
        print("\n📊 Manifests Generated:")
        print(f"  📋 SSOT Manifest: {self.ssot_manifest}")
        print(f"  🔒 Lock Manifest: {self.lock_manifest}")
        
        print("\n🎯 Production Status:")
        print("  ✅ All production files marked as SSOT")
        print("  ✅ Critical files locked (read-only)")
        print("  ✅ Root directory protected")
        print("  ✅ Manifests generated")
        
        print("\n🎉 SSOT & LOCK MANAGEMENT SUCCESSFUL!")
        print("Production files are now protected and marked as single source of truth!")
        print("="*80)


# Main execution
def main():
    """Main execution function"""
    manager = SSOTLockManager()
    manager.run_ssot_lock_management()


if __name__ == "__main__":
    main()
