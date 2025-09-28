#!/usr/bin/env python3
"""
NEXUS Platform - Master File Consolidation & SSOT Management
Comprehensive file consolidation, SSOT marking, and file locking system
"""

import os
import shutil
import json
import stat
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Set
import hashlib
import logging
import subprocess

class NexusConsolidationSSOTManager:
    def __init__(self, root_path: str = "/Users/Arief/Desktop/Nexus"):
        self.root_path = Path(root_path)
        self.archived_bin = self.root_path / "archived_bin"
        self.consolidation_report = {}
        self.ssot_files = set()
        self.locked_files = set()
        self.logger = self._setup_logging()
        
        # Directories to exclude from processing
        self.exclude_dirs = {
            'backup',
            'backup_live_execution',
            'archived_bin',
            'node_modules',
            '__pycache__',
            '.git',
            'venv',
            'env',
            '.pytest_cache',
            'backup_*',
            'archived_*'
        }
        
        # Define SSOT (Single Source of Truth) files
        self.ssot_patterns = {
            'docker_compose': [
                'docker-compose.yml',
                'docker-compose.dev.yml', 
                'docker-compose.staging.yml'
            ],
            'dockerfiles': [
                'docker/Dockerfile.backend',
                'docker/Dockerfile.frontend',
                'docker/Dockerfile.backend.multi-stage',
                'docker/Dockerfile.frontend.multi-stage'
            ],
            'requirements': [
                'backend/requirements.txt',
                'frontend/web/package.json',
                'package.json'
            ],
            'config': [
                'config/environment/production.yml',
                'config/environment/development.yml',
                'config/environment/staging.yml'
            ],
            'scripts': [
                'scripts/deploy-production.sh',
                'scripts/start-local-dev.sh',
                'scripts/health_check.py'
            ],
            'documentation': [
                'README.md',
                'NEXUS_PLATFORM_DOCUMENTATION.md',
                'ARCHITECTURE_OVERVIEW.md'
            ]
        }
        
        # Define critical files to lock
        self.critical_files = [
            'docker-compose.yml',
            'docker/Dockerfile.backend',
            'docker/Dockerfile.frontend',
            'backend/requirements.txt',
            'frontend/web/package.json',
            'package.json',
            'README.md',
            'backend/main_unified.py',
            'frontend/web/src/App.tsx'
        ]
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('consolidation_ssot.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _should_exclude_path(self, path: Path) -> bool:
        """Check if a path should be excluded from processing"""
        try:
            # Convert to relative path from root
            rel_path = path.relative_to(self.root_path)
            path_parts = rel_path.parts
            
            # Check each part of the path
            for part in path_parts:
                # Check exact matches
                if part in self.exclude_dirs:
                    return True
                
                # Check pattern matches
                for pattern in self.exclude_dirs:
                    if '*' in pattern:
                        import fnmatch
                        if fnmatch.fnmatch(part, pattern):
                            return True
            
            return False
        except ValueError:
            # Path is not relative to root, exclude it
            return True
    
    def consolidate_duplicate_files(self):
        """Consolidate duplicate files and archive them"""
        self.logger.info("Starting file consolidation process...")
        
        # Create archived_bin structure
        self._create_archive_structure()
        
        # Consolidate by category
        self._consolidate_docker_files()
        self._consolidate_requirements()
        self._consolidate_scripts()
        self._consolidate_documentation()
        self._consolidate_config_files()
        
        self.logger.info("File consolidation completed")
    
    def _create_archive_structure(self):
        """Create organized archive directory structure"""
        archive_dirs = [
            'docker-compose/variants',
            'docker-compose/environments', 
            'dockerfiles/backend',
            'dockerfiles/frontend',
            'dockerfiles/services',
            'requirements/duplicates',
            'scripts/deployment',
            'scripts/utilities',
            'scripts/testing',
            'docs/archived',
            'docs/duplicates',
            'config/environment',
            'config/docker',
            'config/security'
        ]
        
        for dir_path in archive_dirs:
            (self.archived_bin / dir_path).mkdir(parents=True, exist_ok=True)
    
    def _consolidate_docker_files(self):
        """Consolidate Docker Compose and Dockerfile duplicates"""
        self.logger.info("Consolidating Docker files...")
        
        # Docker Compose files
        docker_compose_files = [f for f in self.root_path.glob("docker-compose*.yml") 
                               if not self._should_exclude_path(f)]
        keep_files = self.ssot_patterns['docker_compose']
        
        for file in docker_compose_files:
            if file.name not in keep_files:
                self._archive_file(file, "docker-compose/variants/")
        
        # Dockerfiles
        dockerfiles = [f for f in self.root_path.glob("**/Dockerfile*") 
                      if not self._should_exclude_path(f)]
        keep_dockerfiles = self.ssot_patterns['dockerfiles']
        
        for dockerfile in dockerfiles:
            rel_path = str(dockerfile.relative_to(self.root_path))
            if rel_path not in keep_dockerfiles:
                if "backend" in str(dockerfile):
                    self._archive_file(dockerfile, "dockerfiles/backend/")
                elif "frontend" in str(dockerfile):
                    self._archive_file(dockerfile, "dockerfiles/frontend/")
                else:
                    self._archive_file(dockerfile, "dockerfiles/services/")
    
    def _consolidate_requirements(self):
        """Consolidate requirements and package files"""
        self.logger.info("Consolidating requirements files...")
        
        # Requirements files
        req_files = [f for f in self.root_path.glob("**/requirements*.txt") 
                    if not self._should_exclude_path(f)]
        keep_req = [f for f in self.ssot_patterns['requirements'] if f.endswith('.txt')]
        
        for req_file in req_files:
            rel_path = str(req_file.relative_to(self.root_path))
            if rel_path not in keep_req:
                self._archive_file(req_file, "requirements/duplicates/")
        
        # Package files
        package_files = [f for f in self.root_path.glob("**/package*.json") 
                        if not self._should_exclude_path(f)]
        keep_package = [f for f in self.ssot_patterns['requirements'] if f.endswith('.json')]
        
        for package_file in package_files:
            rel_path = str(package_file.relative_to(self.root_path))
            if rel_path not in keep_package:
                self._archive_file(package_file, "requirements/duplicates/")
    
    def _consolidate_scripts(self):
        """Consolidate duplicate scripts"""
        self.logger.info("Consolidating scripts...")
        
        # Deployment scripts
        deploy_scripts = [f for f in self.root_path.glob("**/deploy*.sh") 
                         if not self._should_exclude_path(f)]
        keep_deploy = [f for f in self.ssot_patterns['scripts'] if f.endswith('.sh')]
        
        for script in deploy_scripts:
            rel_path = str(script.relative_to(self.root_path))
            if rel_path not in keep_deploy:
                self._archive_file(script, "scripts/deployment/")
        
        # Utility scripts
        util_scripts = [f for f in self.root_path.glob("**/utilities/*.py") 
                       if not self._should_exclude_path(f)]
        for script in util_scripts:
            self._archive_file(script, "scripts/utilities/")
        
        # Testing scripts
        test_scripts = [f for f in self.root_path.glob("**/testing/*.sh") 
                       if not self._should_exclude_path(f)]
        for script in test_scripts:
            self._archive_file(script, "scripts/testing/")
    
    def _consolidate_documentation(self):
        """Consolidate duplicate documentation"""
        self.logger.info("Consolidating documentation...")
        
        # Move archived docs
        archived_docs = [f for f in self.root_path.glob("docs/archived_*") 
                        if not self._should_exclude_path(f)]
        for doc in archived_docs:
            self._archive_file(doc, "docs/archived/")
        
        # Move duplicate guides
        duplicate_guides = [
            "docs/developer/DEVELOPER_GUIDE.md",
            "docs/deployment/DEPLOYMENT_GUIDE.md"
        ]
        
        for guide in duplicate_guides:
            guide_path = self.root_path / guide
            if guide_path.exists() and not self._should_exclude_path(guide_path):
                self._archive_file(guide_path, "docs/duplicates/")
    
    def _consolidate_config_files(self):
        """Consolidate configuration files"""
        self.logger.info("Consolidating configuration files...")
        
        # Environment configs
        env_configs = [f for f in self.root_path.glob("config/environment/*.yml") 
                      if not self._should_exclude_path(f)]
        keep_env = [f for f in self.ssot_patterns['config'] if f.endswith('.yml')]
        
        for config in env_configs:
            rel_path = str(config.relative_to(self.root_path))
            if rel_path not in keep_env:
                self._archive_file(config, "config/environment/")
        
        # Docker configs
        docker_configs = [f for f in self.root_path.glob("config/docker/*.yml") 
                         if not self._should_exclude_path(f)]
        for config in docker_configs:
            self._archive_file(config, "config/docker/")
        
        # Security configs
        security_configs = [f for f in self.root_path.glob("config/security/*.yml") 
                           if not self._should_exclude_path(f)]
        for config in security_configs:
            self._archive_file(config, "config/security/")
    
    def _archive_file(self, file_path: Path, archive_subdir: str):
        """Archive a file to the archived_bin directory"""
        try:
            archive_dir = self.archived_bin / archive_subdir
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            # Create archive path
            archive_path = archive_dir / file_path.name
            
            # Handle name conflicts
            counter = 1
            while archive_path.exists():
                name_parts = file_path.stem, counter, file_path.suffix
                archive_path = archive_dir / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                counter += 1
            
            # Move file
            shutil.move(str(file_path), str(archive_path))
            
            # Log the action
            self.logger.info(f"Archived: {file_path} -> {archive_path}")
            
            # Update report
            if archive_subdir not in self.consolidation_report:
                self.consolidation_report[archive_subdir] = []
            self.consolidation_report[archive_subdir].append({
                "original": str(file_path),
                "archived": str(archive_path),
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Failed to archive {file_path}: {e}")
    
    def mark_ssot_files(self):
        """Mark SSOT files with .ssot markers"""
        self.logger.info("Marking SSOT files...")
        
        for category, files in self.ssot_patterns.items():
            for file_path in files:
                full_path = self.root_path / file_path
                if full_path.exists() and not self._should_exclude_path(full_path):
                    self._create_ssot_marker(full_path, category)
                    self.ssot_files.add(str(full_path))
        
        self.logger.info(f"Marked {len(self.ssot_files)} files as SSOT")
    
    def _create_ssot_marker(self, file_path: Path, category: str):
        """Create .ssot marker file"""
        try:
            ssot_marker = file_path.parent / f".{file_path.name}.ssot"
            
            ssot_data = {
                "file_path": str(file_path.relative_to(self.root_path)),
                "category": category,
                "marked_at": datetime.now().isoformat(),
                "ssot_version": "2.1.0",
                "description": f"Single Source of Truth for {category}",
                "checksum": self._calculate_checksum(file_path)
            }
            
            with open(ssot_marker, 'w') as f:
                json.dump(ssot_data, f, indent=2)
            
            self.logger.info(f"Created SSOT marker: {ssot_marker}")
            
        except Exception as e:
            self.logger.error(f"Failed to create SSOT marker for {file_path}: {e}")
    
    def lock_critical_files(self):
        """Apply read-only locks to critical files"""
        self.logger.info("Locking critical files...")
        
        for file_path in self.critical_files:
            full_path = self.root_path / file_path
            if full_path.exists():
                self._apply_file_lock(full_path)
                self.locked_files.add(str(full_path))
        
        self.logger.info(f"Locked {len(self.locked_files)} critical files")
    
    def _apply_file_lock(self, file_path: Path):
        """Apply read-only lock to file"""
        try:
            # Make file read-only
            current_permissions = file_path.stat().st_mode
            new_permissions = current_permissions & ~stat.S_IWRITE
            file_path.chmod(new_permissions)
            
            # Create lock marker
            lock_marker = file_path.parent / f".{file_path.name}.lock"
            lock_data = {
                "file_path": str(file_path.relative_to(self.root_path)),
                "locked_at": datetime.now().isoformat(),
                "lock_version": "2.1.0",
                "reason": "Critical production file - read-only protection",
                "unlock_command": f"chmod +w {file_path}"
            }
            
            with open(lock_marker, 'w') as f:
                json.dump(lock_data, f, indent=2)
            
            self.logger.info(f"Locked file: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to lock {file_path}: {e}")
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"Failed to calculate checksum for {file_path}: {e}")
            return "error"
    
    def generate_ssot_manifest(self):
        """Generate comprehensive SSOT manifest"""
        manifest = {
            "ssot_manifest": {
                "version": "2.1.0",
                "generated_at": datetime.now().isoformat(),
                "total_ssot_files": len(self.ssot_files),
                "total_locked_files": len(self.locked_files),
                "categories": {}
            },
            "ssot_files": {},
            "locked_files": {},
            "consolidation_report": self.consolidation_report
        }
        
        # Add SSOT files to manifest
        for file_path in self.ssot_files:
            rel_path = str(Path(file_path).relative_to(self.root_path))
            manifest["ssot_files"][rel_path] = {
                "full_path": file_path,
                "checksum": self._calculate_checksum(Path(file_path)),
                "size": Path(file_path).stat().st_size,
                "modified": datetime.fromtimestamp(Path(file_path).stat().st_mtime).isoformat()
            }
        
        # Add locked files to manifest
        for file_path in self.locked_files:
            rel_path = str(Path(file_path).relative_to(self.root_path))
            manifest["locked_files"][rel_path] = {
                "full_path": file_path,
                "locked_at": datetime.now().isoformat(),
                "permissions": oct(Path(file_path).stat().st_mode)[-3:]
            }
        
        # Save manifest
        manifest_path = self.root_path / "ssot_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        self.logger.info(f"SSOT manifest saved to {manifest_path}")
        return manifest
    
    def run_full_consolidation_and_ssot(self):
        """Run complete consolidation, SSOT marking, and locking process"""
        self.logger.info("Starting full consolidation and SSOT process...")
        
        try:
            # Phase 1: Consolidate duplicate files
            self.consolidate_duplicate_files()
            
            # Phase 2: Mark SSOT files
            self.mark_ssot_files()
            
            # Phase 3: Lock critical files
            self.lock_critical_files()
            
            # Phase 4: Generate manifest
            manifest = self.generate_ssot_manifest()
            
            # Phase 5: Generate summary report
            self._generate_summary_report(manifest)
            
            self.logger.info("Full consolidation and SSOT process completed successfully!")
            return manifest
            
        except Exception as e:
            self.logger.error(f"Process failed: {e}")
            raise
    
    def _generate_summary_report(self, manifest):
        """Generate summary report"""
        report = f"""
# NEXUS Platform - File Consolidation & SSOT Report
Generated: {datetime.now().isoformat()}

## Summary
- **Files Consolidated**: {sum(len(files) for files in self.consolidation_report.values())}
- **SSOT Files Marked**: {len(self.ssot_files)}
- **Critical Files Locked**: {len(self.locked_files)}

## SSOT Files
"""
        
        for category, files in self.ssot_patterns.items():
            report += f"\n### {category.title()}\n"
            for file_path in files:
                if self.root_path / file_path in [Path(f) for f in self.ssot_files]:
                    report += f"- ✅ {file_path}\n"
                else:
                    report += f"- ❌ {file_path} (not found)\n"
        
        report += f"\n## Locked Files\n"
        for file_path in self.locked_files:
            report += f"- 🔒 {file_path}\n"
        
        report += f"\n## Archived Files\n"
        for category, files in self.consolidation_report.items():
            report += f"\n### {category}\n"
            for file_info in files:
                report += f"- {file_info['original']} -> {file_info['archived']}\n"
        
        # Save report
        report_path = self.root_path / "CONSOLIDATION_SSOT_REPORT.md"
        with open(report_path, 'w') as f:
            f.write(report)
        
        self.logger.info(f"Summary report saved to {report_path}")

if __name__ == "__main__":
    manager = NexusConsolidationSSOTManager()
    manager.run_full_consolidation_and_ssot()
