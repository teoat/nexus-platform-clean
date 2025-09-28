#!/usr/bin/env python3
"""
NEXUS Platform - SSOT Analysis and Archive Management
Analyzes successful files and moves unused files to archived_bin
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

class SSOTAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.archived_bin = self.project_root / "archived_bin"
        self.archived_bin.mkdir(exist_ok=True)
        
        # Define SSOT categories
        self.ssot_categories = {
            "docker": {
                "patterns": ["docker-compose*.yml", "Dockerfile*", ".dockerignore"],
                "description": "Docker configuration files"
            },
            "kubernetes": {
                "patterns": ["k8s-*", "*.yaml", "*.yml"],
                "description": "Kubernetes manifests"
            },
            "environment": {
                "patterns": ["env*", ".env*", "*.env"],
                "description": "Environment configuration files"
            },
            "nginx": {
                "patterns": ["nginx/*.conf", "nginx/*.yml"],
                "description": "Nginx configuration files"
            },
            "monitoring": {
                "patterns": ["monitoring/*.yml", "monitoring/*.yaml"],
                "description": "Monitoring configuration files"
            },
            "scripts": {
                "patterns": ["*.sh", "scripts/*.py", "scripts/*.sh"],
                "description": "Deployment and utility scripts"
            },
            "documentation": {
                "patterns": ["*.md", "docs/*", "README*"],
                "description": "Documentation files"
            },
            "backend_core": {
                "patterns": ["backend/main_simple.py", "backend/requirements.txt"],
                "description": "Core backend files"
            },
            "frontend_core": {
                "patterns": ["frontend/web/package*.json", "frontend/web/src/*"],
                "description": "Core frontend files"
            }
        }
        
        # Define patterns for unused files
        self.unused_patterns = [
            "*.tmp", "*.temp", "*.log", "*.bak", "*.backup",
            "node_modules", ".git", "__pycache__", "*.pyc",
            "*.pyo", ".pytest_cache", ".coverage", "htmlcov",
            "*.egg-info", ".DS_Store", "Thumbs.db"
        ]
        
        # Define backup patterns to archive
        self.backup_patterns = [
            "backup_*", "archive_*", "old_*", "temp_*",
            "test_*", "debug_*", "*.orig", "*.rej"
        ]

    def find_files_by_patterns(self, patterns: List[str], base_path: Path = None) -> Set[Path]:
        """Find files matching patterns"""
        if base_path is None:
            base_path = self.project_root
            
        found_files = set()
        for pattern in patterns:
            for file_path in base_path.rglob(pattern):
                if file_path.is_file():
                    # Skip very long paths and problematic directories
                    if len(str(file_path)) > 200:
                        continue
                    if any(skip in str(file_path) for skip in ["archived_bin", "node_modules", ".git"]):
                        continue
                    found_files.add(file_path)
        return found_files

    def analyze_ssot_files(self) -> Dict[str, List[str]]:
        """Analyze and categorize SSOT files"""
        ssot_files = {}
        
        for category, config in self.ssot_categories.items():
            patterns = config["patterns"]
            files = self.find_files_by_patterns(patterns)
            
            # Convert to relative paths
            relative_files = []
            for file_path in files:
                try:
                    rel_path = file_path.relative_to(self.project_root)
                    relative_files.append(str(rel_path))
                except ValueError:
                    continue
            
            ssot_files[category] = {
                "files": sorted(relative_files),
                "description": config["description"],
                "count": len(relative_files)
            }
        
        return ssot_files

    def find_unused_files(self) -> List[str]:
        """Find unused files to archive"""
        unused_files = []
        
        # Find files matching unused patterns
        for pattern in self.unused_patterns + self.backup_patterns:
            files = self.find_files_by_patterns([pattern])
            for file_path in files:
                try:
                    rel_path = file_path.relative_to(self.project_root)
                    unused_files.append(str(rel_path))
                except ValueError:
                    continue
        
        return sorted(unused_files)

    def archive_unused_files(self, unused_files: List[str]) -> Dict[str, List[str]]:
        """Move unused files to archived_bin"""
        archived = {"success": [], "failed": []}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_dir = self.archived_bin / f"archive_{timestamp}"
        archive_dir.mkdir(exist_ok=True)
        
        for file_path in unused_files:
            try:
                source = self.project_root / file_path
                if source.exists():
                    # Create directory structure in archive
                    dest = archive_dir / file_path
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move file
                    shutil.move(str(source), str(dest))
                    archived["success"].append(file_path)
                    print(f"✅ Archived: {file_path}")
                else:
                    archived["failed"].append(f"{file_path} (not found)")
            except Exception as e:
                archived["failed"].append(f"{file_path} (error: {str(e)})")
                print(f"❌ Failed to archive {file_path}: {e}")
        
        return archived

    def create_ssot_manifest(self, ssot_files: Dict[str, List[str]]) -> None:
        """Create SSOT manifest file"""
        manifest = {
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "description": "NEXUS Platform Single Source of Truth (SSOT) Manifest",
            "categories": ssot_files,
            "total_files": sum(cat["count"] for cat in ssot_files.values())
        }
        
        manifest_path = self.project_root / "ssot_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ SSOT manifest created: {manifest_path}")

    def create_archive_manifest(self, archived: Dict[str, List[str]]) -> None:
        """Create archive manifest file"""
        manifest = {
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "description": "NEXUS Platform Archive Manifest",
            "archived_files": archived["success"],
            "failed_archives": archived["failed"],
            "total_archived": len(archived["success"]),
            "total_failed": len(archived["failed"])
        }
        
        manifest_path = self.project_root / "archive_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ Archive manifest created: {manifest_path}")

    def run_analysis(self) -> Dict:
        """Run complete SSOT analysis and archiving"""
        print("🔍 Starting SSOT Analysis and Archiving...")
        print("=" * 50)
        
        # Analyze SSOT files
        print("\n📋 Analyzing SSOT files...")
        ssot_files = self.analyze_ssot_files()
        
        for category, data in ssot_files.items():
            print(f"\n📁 {category.upper()} ({data['count']} files):")
            print(f"   Description: {data['description']}")
            for file_path in data['files'][:5]:  # Show first 5 files
                print(f"   - {file_path}")
            if len(data['files']) > 5:
                print(f"   ... and {len(data['files']) - 5} more files")
        
        # Find unused files
        print("\n🗑️  Finding unused files...")
        unused_files = self.find_unused_files()
        print(f"Found {len(unused_files)} unused files to archive")
        
        # Archive unused files
        print("\n📦 Archiving unused files...")
        archived = self.archive_unused_files(unused_files)
        
        # Create manifests
        print("\n📄 Creating manifest files...")
        self.create_ssot_manifest(ssot_files)
        self.create_archive_manifest(archived)
        
        # Summary
        print("\n" + "=" * 50)
        print("🎉 SSOT Analysis and Archiving Complete!")
        print(f"✅ SSOT files categorized: {sum(cat['count'] for cat in ssot_files.values())}")
        print(f"✅ Files archived: {len(archived['success'])}")
        print(f"❌ Failed archives: {len(archived['failed'])}")
        
        return {
            "ssot_files": ssot_files,
            "archived": archived,
            "total_ssot": sum(cat['count'] for cat in ssot_files.values()),
            "total_archived": len(archived['success'])
        }

if __name__ == "__main__":
    analyzer = SSOTAnalyzer("/Users/Arief/Desktop/Nexus")
    results = analyzer.run_analysis()
