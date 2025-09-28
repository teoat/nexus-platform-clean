#!/usr/bin/env python3
"""
NEXUS Platform - Autonomous Optimizer
Supreme AI Agent - Autonomous Evolution System
"""

import os
import sys
import json
import shutil
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib
import re

class NexusAutonomousOptimizer:
    """Autonomous system optimizer for NEXUS Platform"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.archived_bin = self.workspace_path / "archived_bin"
        self.log_file = self.workspace_path / "logs" / "autonomous_optimizer.log"
        self.config_file = self.workspace_path / "optimization_config.json"
        
        # Setup logging
        self.setup_logging()
        
        # Load configuration
        self.config = self.load_config()
        
        # Analysis results
        self.analysis_results = {
            "duplicates": [],
            "unused_files": [],
            "conflicts": [],
            "optimizations": [],
            "backups_created": [],
            "files_archived": []
        }
    
    def setup_logging(self):
        """Setup logging configuration"""
        os.makedirs(self.log_file.parent, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_config(self) -> Dict[str, Any]:
        """Load optimization configuration"""
        default_config = {
            "backup_enabled": True,
            "archive_duplicates": True,
            "optimize_docker": True,
            "fix_api_versions": True,
            "performance_optimization": True,
            "exclude_patterns": [
                "node_modules",
                ".git",
                "__pycache__",
                "*.pyc",
                ".venv",
                "nexus_env",
                "nexus",
                "*.log"
            ],
            "critical_files": [
                "docker-compose.yml",
                "package.json",
                "requirements.txt",
                "main_unified.py"
            ]
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return {**default_config, **json.load(f)}
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")
        
        return default_config
    
    def save_config(self):
        """Save current configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def create_backup(self) -> str:
        """Create complete system backup"""
        if not self.config["backup_enabled"]:
            return ""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"nexus_backup_{timestamp}"
        backup_path = self.workspace_path.parent / backup_name
        
        self.logger.info(f"Creating backup: {backup_name}")
        
        try:
            # Create tar.gz backup
            cmd = [
                "tar", "-czf", str(backup_path) + ".tar.gz",
                "--exclude=node_modules",
                "--exclude=.git",
                "--exclude=*.pyc",
                "--exclude=__pycache__",
                "--exclude=.venv",
                "--exclude=nexus_env",
                "--exclude=nexus",
                "--exclude=*.log",
                "--exclude=*.tar.gz",
                "-C", str(self.workspace_path.parent),
                self.workspace_path.name
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            self.analysis_results["backups_created"].append(str(backup_path) + ".tar.gz")
            self.logger.info(f"Backup created successfully: {backup_name}.tar.gz")
            return str(backup_path) + ".tar.gz"
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Backup failed: {e}")
            return ""
    
    def analyze_duplicates(self) -> List[Dict[str, Any]]:
        """Analyze and detect duplicate files"""
        self.logger.info("Analyzing duplicate files...")
        
        duplicates = []
        file_hashes = {}
        
        for file_path in self.workspace_path.rglob("*"):
            if file_path.is_file() and not self.should_exclude(file_path):
                try:
                    file_hash = self.calculate_file_hash(file_path)
                    
                    if file_hash in file_hashes:
                        duplicates.append({
                            "original": str(file_hashes[file_hash]),
                            "duplicate": str(file_path),
                            "hash": file_hash,
                            "size": file_path.stat().st_size
                        })
                    else:
                        file_hashes[file_hash] = file_path
                        
                except Exception as e:
                    self.logger.warning(f"Error analyzing {file_path}: {e}")
        
        self.analysis_results["duplicates"] = duplicates
        self.logger.info(f"Found {len(duplicates)} duplicate files")
        return duplicates
    
    def analyze_docker_files(self) -> List[Dict[str, Any]]:
        """Analyze Docker Compose files for conflicts"""
        self.logger.info("Analyzing Docker Compose files...")
        
        docker_files = list(self.workspace_path.rglob("docker-compose*.yml"))
        conflicts = []
        
        for docker_file in docker_files:
            try:
                with open(docker_file, 'r') as f:
                    content = f.read()
                
                # Check for port conflicts
                port_matches = re.findall(r'(\d+):(\d+)', content)
                for host_port, container_port in port_matches:
                    conflicts.append({
                        "file": str(docker_file),
                        "type": "port_conflict",
                        "host_port": host_port,
                        "container_port": container_port
                    })
                
                # Check for service conflicts
                service_matches = re.findall(r'^\s*(\w+):', content, re.MULTILINE)
                for service in service_matches:
                    if service in ['services', 'networks', 'volumes']:
                        continue
                    conflicts.append({
                        "file": str(docker_file),
                        "type": "service_definition",
                        "service": service
                    })
                    
            except Exception as e:
                self.logger.warning(f"Error analyzing {docker_file}: {e}")
        
        self.analysis_results["conflicts"] = conflicts
        self.logger.info(f"Found {len(conflicts)} Docker conflicts")
        return conflicts
    
    def analyze_api_endpoints(self) -> List[Dict[str, Any]]:
        """Analyze API endpoint consistency"""
        self.logger.info("Analyzing API endpoints...")
        
        api_issues = []
        
        # Check frontend API calls
        frontend_files = list(self.workspace_path.glob("frontend/web/src/**/*.ts"))
        frontend_files.extend(list(self.workspace_path.glob("frontend/web/src/**/*.tsx")))
        
        for file_path in frontend_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Find API calls
                api_calls = re.findall(r'["\'](/api/[^"\']*)["\']', content)
                for api_call in api_calls:
                    if not api_call.startswith('/api/v1/'):
                        api_issues.append({
                            "file": str(file_path),
                            "type": "api_version_mismatch",
                            "endpoint": api_call,
                            "expected": api_call.replace('/api/', '/api/v1/')
                        })
                        
            except Exception as e:
                self.logger.warning(f"Error analyzing {file_path}: {e}")
        
        self.analysis_results["api_issues"] = api_issues
        self.logger.info(f"Found {len(api_issues)} API issues")
        return api_issues
    
    def should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded from analysis"""
        for pattern in self.config["exclude_patterns"]:
            if pattern in str(file_path) or file_path.match(pattern):
                return True
        return False
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def archive_duplicates(self):
        """Archive duplicate files"""
        if not self.config["archive_duplicates"]:
            return
        
        self.logger.info("Archiving duplicate files...")
        
        os.makedirs(self.archived_bin / "duplicates", exist_ok=True)
        
        for duplicate in self.analysis_results["duplicates"]:
            try:
                duplicate_path = Path(duplicate["duplicate"])
                archive_path = self.archived_bin / "duplicates" / duplicate_path.name
                
                # Handle name conflicts
                counter = 1
                while archive_path.exists():
                    archive_path = self.archived_bin / "duplicates" / f"{duplicate_path.stem}_{counter}{duplicate_path.suffix}"
                    counter += 1
                
                shutil.move(str(duplicate_path), str(archive_path))
                self.analysis_results["files_archived"].append({
                    "original": str(duplicate_path),
                    "archived": str(archive_path)
                })
                
                self.logger.info(f"Archived duplicate: {duplicate_path} -> {archive_path}")
                
            except Exception as e:
                self.logger.error(f"Failed to archive {duplicate['duplicate']}: {e}")
    
    def optimize_docker_compose(self):
        """Optimize Docker Compose configuration"""
        if not self.config["optimize_docker"]:
            return
        
        self.logger.info("Optimizing Docker Compose configuration...")
        
        # Archive old Docker Compose files
        docker_files = list(self.workspace_path.rglob("docker-compose*.yml"))
        docker_files = [f for f in docker_files if f.name != "docker-compose.optimized.yml"]
        
        os.makedirs(self.archived_bin / "docker_configs", exist_ok=True)
        
        for docker_file in docker_files:
            try:
                archive_path = self.archived_bin / "docker_configs" / docker_file.name
                shutil.move(str(docker_file), str(archive_path))
                self.analysis_results["files_archived"].append({
                    "original": str(docker_file),
                    "archived": str(archive_path)
                })
                self.logger.info(f"Archived Docker file: {docker_file} -> {archive_path}")
            except Exception as e:
                self.logger.error(f"Failed to archive {docker_file}: {e}")
        
        # Rename optimized file to main
        optimized_file = self.workspace_path / "docker-compose.optimized.yml"
        main_file = self.workspace_path / "docker-compose.yml"
        
        if optimized_file.exists():
            shutil.move(str(optimized_file), str(main_file))
            self.logger.info("Set optimized Docker Compose as main configuration")
    
    def fix_api_versions(self):
        """Fix API version mismatches"""
        if not self.config["fix_api_versions"]:
            return
        
        self.logger.info("Fixing API version mismatches...")
        
        # Update frontend files to use v1 API
        frontend_files = list(self.workspace_path.glob("frontend/web/src/**/*.ts"))
        frontend_files.extend(list(self.workspace_path.glob("frontend/web/src/**/*.tsx")))
        
        for file_path in frontend_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Replace /api/ with /api/v1/ (but not /api/v1/)
                updated_content = re.sub(r'["\'](/api/[^v][^"\']*)["\']', r'"\1"'.replace('/api/', '/api/v1/'), content)
                
                if content != updated_content:
                    with open(file_path, 'w') as f:
                        f.write(updated_content)
                    self.logger.info(f"Updated API versions in: {file_path}")
                    
            except Exception as e:
                self.logger.error(f"Failed to update {file_path}: {e}")
    
    def generate_optimization_report(self):
        """Generate comprehensive optimization report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "optimizer_version": "1.0.0",
            "workspace_path": str(self.workspace_path),
            "analysis_results": self.analysis_results,
            "config": self.config,
            "summary": {
                "duplicates_found": len(self.analysis_results["duplicates"]),
                "files_archived": len(self.analysis_results["files_archived"]),
                "backups_created": len(self.analysis_results["backups_created"]),
                "conflicts_resolved": len(self.analysis_results["conflicts"]),
                "api_issues_fixed": len(self.analysis_results.get("api_issues", []))
            }
        }
        
        report_file = self.workspace_path / "AUTONOMOUS_OPTIMIZATION_REPORT.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Optimization report generated: {report_file}")
        return report
    
    def run_autonomous_optimization(self):
        """Run complete autonomous optimization"""
        self.logger.info("🚀 Starting NEXUS Autonomous Optimization")
        
        try:
            # Step 1: Create backup
            self.create_backup()
            
            # Step 2: Analyze system
            self.analyze_duplicates()
            self.analyze_docker_files()
            self.analyze_api_endpoints()
            
            # Step 3: Apply optimizations
            self.archive_duplicates()
            self.optimize_docker_compose()
            self.fix_api_versions()
            
            # Step 4: Generate report
            report = self.generate_optimization_report()
            
            self.logger.info("✅ Autonomous optimization completed successfully")
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Optimization failed: {e}")
            raise

def main():
    """Main entry point"""
    workspace_path = sys.argv[1] if len(sys.argv) > 1 else "/Users/Arief/Desktop/Nexus"
    
    optimizer = NexusAutonomousOptimizer(workspace_path)
    optimizer.run_autonomous_optimization()

if __name__ == "__main__":
    main()
