#!/usr/bin/env python3
"""
NEXUS Platform - Docker & Kubernetes Analysis with SSOT Management
Comprehensive analysis of Docker and Kubernetes configurations, SSOT identification, and file archiving
"""

import os
import json
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DockerK8sSSOTAnalyzer:
    """Comprehensive analyzer for Docker, Kubernetes, and SSOT management"""
    
    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        self.base_path = Path(base_path)
        self.archived_bin = self.base_path / "archived_bin"
        self.archived_bin.mkdir(exist_ok=True)
        
        # Create subdirectories for organized archiving
        self.archive_dirs = {
            "docker": self.archived_bin / "docker",
            "kubernetes": self.archived_bin / "kubernetes", 
            "lock_files": self.archived_bin / "lock_files",
            "ssot_files": self.archived_bin / "ssot_files",
            "unused_configs": self.archived_bin / "unused_configs",
            "duplicate_files": self.archived_bin / "duplicate_files"
        }
        
        for dir_path in self.archive_dirs.values():
            dir_path.mkdir(exist_ok=True)
        
        # Analysis results
        self.analysis_results = {
            "docker_files": {"ssot": [], "unused": [], "duplicates": []},
            "kubernetes_files": {"ssot": [], "unused": [], "duplicates": []},
            "lock_files": {"active": [], "archived": []},
            "ssot_files": {"active": [], "archived": []},
            "recommendations": []
        }
    
    def run_comprehensive_analysis(self):
        """Run complete Docker, Kubernetes, and SSOT analysis"""
        logger.info("🔍 Starting comprehensive Docker & Kubernetes analysis...")
        print("\n" + "="*80)
        print("🔍 NEXUS PLATFORM - DOCKER & KUBERNETES ANALYSIS")
        print("="*80)
        
        try:
            # Analyze Docker configurations
            self._analyze_docker_configurations()
            
            # Analyze Kubernetes configurations
            self._analyze_kubernetes_configurations()
            
            # Analyze lock files
            self._analyze_lock_files()
            
            # Analyze SSOT files
            self._analyze_ssot_files()
            
            # Identify duplicates and unused files
            self._identify_duplicates_and_unused()
            
            # Archive unused files
            self._archive_unused_files()
            
            # Generate comprehensive report
            self._generate_analysis_report()
            
            # Print summary
            self._print_analysis_summary()
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            print(f"\n❌ ANALYSIS FAILED: {e}")
    
    def _analyze_docker_configurations(self):
        """Analyze all Docker configurations and identify SSOT files"""
        print("\n🐳 Analyzing Docker configurations...")
        
        # Find all Docker files (excluding problematic nested directories)
        docker_files = []
        compose_files = []
        
        for pattern in ["Dockerfile*", "docker-compose*.yml", "docker-compose*.yaml"]:
            for file_path in self.base_path.rglob(pattern):
                # Skip deeply nested backup directories and node_modules
                if any(part in str(file_path) for part in ["backup_", "node_modules", "archived_bin"]):
                    continue
                if len(str(file_path)) > 200:  # Skip very long paths
                    continue
                if pattern.startswith("Dockerfile"):
                    docker_files.append(file_path)
                else:
                    compose_files.append(file_path)
        
        # Identify SSOT Docker files (most recent/optimized versions)
        ssot_docker_files = [
            "docker-compose.optimized.yml",
            "docker-compose.yml", 
            "docker-compose.prod.yml",
            "docker-compose.override.yml",
            "docker/Dockerfile.backend.optimized",
            "docker/Dockerfile.frontend.optimized",
            "docker/Dockerfile.backend",
            "docker/Dockerfile.frontend"
        ]
        
        for file_path in docker_files + compose_files:
            relative_path = file_path.relative_to(self.base_path)
            
            if str(relative_path) in ssot_docker_files:
                self.analysis_results["docker_files"]["ssot"].append({
                    "path": str(relative_path),
                    "type": "Dockerfile" if "Dockerfile" in str(relative_path) else "Compose",
                    "status": "SSOT",
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
                print(f"  ✅ SSOT: {relative_path}")
            else:
                self.analysis_results["docker_files"]["unused"].append({
                    "path": str(relative_path),
                    "type": "Dockerfile" if "Dockerfile" in str(relative_path) else "Compose",
                    "status": "Unused",
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
                print(f"  📦 Unused: {relative_path}")
    
    def _analyze_kubernetes_configurations(self):
        """Analyze all Kubernetes configurations and identify SSOT files"""
        print("\n☸️ Analyzing Kubernetes configurations...")
        
        # Find all Kubernetes files (excluding problematic nested directories)
        k8s_files = []
        for pattern in ["*.yaml", "*.yml"]:
            for file_path in self.base_path.rglob(pattern):
                # Skip deeply nested backup directories and node_modules
                if any(part in str(file_path) for part in ["backup_", "node_modules", "archived_bin"]):
                    continue
                if len(str(file_path)) > 200:  # Skip very long paths
                    continue
                if any(keyword in str(file_path) for keyword in [
                    "deployment", "service", "ingress", "configmap", "secret", "namespace",
                    "pvc", "hpa", "networkpolicy", "clusterrole", "serviceaccount"
                ]):
                    k8s_files.append(file_path)
        
        # Identify SSOT Kubernetes files (most comprehensive/optimized versions)
        ssot_k8s_patterns = [
            "k8s-optimized/",
            "config/kubernetes/",
            "infrastructure/security/policies/",
            "monitoring/",
            "security/hardening/"
        ]
        
        for file_path in k8s_files:
            relative_path = file_path.relative_to(self.base_path)
            
            if any(pattern in str(relative_path) for pattern in ssot_k8s_patterns):
                self.analysis_results["kubernetes_files"]["ssot"].append({
                    "path": str(relative_path),
                    "type": "Kubernetes Manifest",
                    "status": "SSOT",
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
                print(f"  ✅ SSOT: {relative_path}")
            else:
                self.analysis_results["kubernetes_files"]["unused"].append({
                    "path": str(relative_path),
                    "type": "Kubernetes Manifest", 
                    "status": "Unused",
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
                print(f"  📦 Unused: {relative_path}")
    
    def _analyze_lock_files(self):
        """Analyze all lock files and identify active vs archived"""
        print("\n🔒 Analyzing lock files...")
        
        # Find all lock files (excluding problematic nested directories)
        lock_files = []
        for pattern in ["*lock*", "package-lock.json"]:
            for file_path in self.base_path.rglob(pattern):
                # Skip deeply nested backup directories and node_modules
                if any(part in str(file_path) for part in ["backup_", "node_modules", "archived_bin"]):
                    continue
                if len(str(file_path)) > 200:  # Skip very long paths
                    continue
                lock_files.append(file_path)
        
        # Active lock files (should be kept)
        active_lock_files = [
            "package-lock.json",
            "frontend/web/package-lock.json",
            "ssot_manifest.json",
            "lock_manifest.json",
            "ssot_lock_manager.py"
        ]
        
        for file_path in lock_files:
            relative_path = file_path.relative_to(self.base_path)
            
            if str(relative_path) in active_lock_files:
                self.analysis_results["lock_files"]["active"].append({
                    "path": str(relative_path),
                    "type": "Lock File",
                    "status": "Active",
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
                print(f"  ✅ Active: {relative_path}")
            else:
                self.analysis_results["lock_files"]["archived"].append({
                    "path": str(relative_path),
                    "type": "Lock File",
                    "status": "Archived",
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
                print(f"  📦 Archive: {relative_path}")
    
    def _analyze_ssot_files(self):
        """Analyze all SSOT files and identify active vs archived"""
        print("\n📋 Analyzing SSOT files...")
        
        # Find all SSOT files (excluding problematic nested directories)
        ssot_files = []
        for file_path in self.base_path.rglob("*ssot*"):
            # Skip deeply nested backup directories and node_modules
            if any(part in str(file_path) for part in ["backup_", "node_modules", "archived_bin"]):
                continue
            if len(str(file_path)) > 200:  # Skip very long paths
                continue
            ssot_files.append(file_path)
        
        # Active SSOT files (should be kept)
        active_ssot_files = [
            "ssot_manifest.json",
            "ssot_lock_manager.py",
            "ssot_manager.py",
            "ssot_master_todo.md",
            "ssot_phase_execution_summary.json"
        ]
        
        for file_path in ssot_files:
            relative_path = file_path.relative_to(self.base_path)
            
            if str(relative_path) in active_ssot_files:
                self.analysis_results["ssot_files"]["active"].append({
                    "path": str(relative_path),
                    "type": "SSOT File",
                    "status": "Active",
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
                print(f"  ✅ Active: {relative_path}")
            else:
                self.analysis_results["ssot_files"]["archived"].append({
                    "path": str(relative_path),
                    "type": "SSOT File",
                    "status": "Archived",
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
                print(f"  📦 Archive: {relative_path}")
    
    def _identify_duplicates_and_unused(self):
        """Identify duplicate and unused files"""
        print("\n🔍 Identifying duplicates and unused files...")
        
        # Find potential duplicates by filename (excluding problematic nested directories)
        all_files = {}
        for file_path in self.base_path.rglob("*"):
            if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                # Skip deeply nested backup directories and node_modules
                if any(part in str(file_path) for part in ["backup_", "node_modules", "archived_bin"]):
                    continue
                if len(str(file_path)) > 200:  # Skip very long paths
                    continue
                filename = file_path.name
                if filename not in all_files:
                    all_files[filename] = []
                all_files[filename].append(file_path)
        
        # Identify duplicates
        for filename, file_paths in all_files.items():
            if len(file_paths) > 1:
                # Keep the most recent one as SSOT
                file_paths.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                ssot_file = file_paths[0]
                duplicates = file_paths[1:]
                
                for dup_file in duplicates:
                    relative_path = dup_file.relative_to(self.base_path)
                    self.analysis_results["docker_files"]["duplicates"].append({
                        "path": str(relative_path),
                        "duplicate_of": str(ssot_file.relative_to(self.base_path)),
                        "status": "Duplicate"
                    })
                    print(f"  🔄 Duplicate: {relative_path} (of {ssot_file.relative_to(self.base_path)})")
    
    def _archive_unused_files(self):
        """Archive unused files to archived_bin"""
        print("\n📦 Archiving unused files...")
        
        # Archive unused Docker files
        for file_info in self.analysis_results["docker_files"]["unused"]:
            self._archive_file(file_info["path"], "docker")
        
        # Archive unused Kubernetes files
        for file_info in self.analysis_results["kubernetes_files"]["unused"]:
            self._archive_file(file_info["path"], "kubernetes")
        
        # Archive duplicate files
        for file_info in self.analysis_results["docker_files"]["duplicates"]:
            self._archive_file(file_info["path"], "duplicate_files")
        
        # Archive archived lock files
        for file_info in self.analysis_results["lock_files"]["archived"]:
            self._archive_file(file_info["path"], "lock_files")
        
        # Archive archived SSOT files
        for file_info in self.analysis_results["ssot_files"]["archived"]:
            self._archive_file(file_info["path"], "ssot_files")
    
    def _archive_file(self, relative_path: str, category: str):
        """Archive a single file to the appropriate category directory"""
        try:
            source_path = self.base_path / relative_path
            if source_path.exists():
                # Create destination directory structure
                dest_path = self.archive_dirs[category] / relative_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move file
                shutil.move(str(source_path), str(dest_path))
                print(f"  📦 Archived: {relative_path} -> {category}/")
                
        except Exception as e:
            print(f"  ❌ Failed to archive {relative_path}: {e}")
    
    def _generate_analysis_report(self):
        """Generate comprehensive analysis report"""
        print("\n📊 Generating analysis report...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "Docker & Kubernetes SSOT Analysis",
            "summary": {
                "docker_ssot_files": len(self.analysis_results["docker_files"]["ssot"]),
                "docker_unused_files": len(self.analysis_results["docker_files"]["unused"]),
                "kubernetes_ssot_files": len(self.analysis_results["kubernetes_files"]["ssot"]),
                "kubernetes_unused_files": len(self.analysis_results["kubernetes_files"]["unused"]),
                "active_lock_files": len(self.analysis_results["lock_files"]["active"]),
                "archived_lock_files": len(self.analysis_results["lock_files"]["archived"]),
                "active_ssot_files": len(self.analysis_results["ssot_files"]["active"]),
                "archived_ssot_files": len(self.analysis_results["ssot_files"]["archived"]),
                "duplicate_files": len(self.analysis_results["docker_files"]["duplicates"])
            },
            "docker_files": self.analysis_results["docker_files"],
            "kubernetes_files": self.analysis_results["kubernetes_files"],
            "lock_files": self.analysis_results["lock_files"],
            "ssot_files": self.analysis_results["ssot_files"],
            "recommendations": self._generate_recommendations()
        }
        
        # Save report
        report_path = self.base_path / "docker-k8s-ssot-analysis-report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"  📊 Report saved: {report_path}")
    
    def _generate_recommendations(self):
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Docker recommendations
        if len(self.analysis_results["docker_files"]["unused"]) > 0:
            recommendations.append({
                "category": "Docker",
                "priority": "High",
                "recommendation": f"Archive {len(self.analysis_results['docker_files']['unused'])} unused Docker files to reduce clutter",
                "action": "Files have been moved to archived_bin/docker/"
            })
        
        # Kubernetes recommendations
        if len(self.analysis_results["kubernetes_files"]["unused"]) > 0:
            recommendations.append({
                "category": "Kubernetes",
                "priority": "High", 
                "recommendation": f"Archive {len(self.analysis_results['kubernetes_files']['unused'])} unused Kubernetes manifests",
                "action": "Files have been moved to archived_bin/kubernetes/"
            })
        
        # Lock file recommendations
        if len(self.analysis_results["lock_files"]["archived"]) > 0:
            recommendations.append({
                "category": "Lock Files",
                "priority": "Medium",
                "recommendation": f"Review {len(self.analysis_results['lock_files']['archived'])} archived lock files for cleanup",
                "action": "Files have been moved to archived_bin/lock_files/"
            })
        
        # SSOT recommendations
        if len(self.analysis_results["ssot_files"]["archived"]) > 0:
            recommendations.append({
                "category": "SSOT",
                "priority": "Medium",
                "recommendation": f"Review {len(self.analysis_results['ssot_files']['archived'])} archived SSOT files",
                "action": "Files have been moved to archived_bin/ssot_files/"
            })
        
        # General recommendations
        recommendations.extend([
            {
                "category": "General",
                "priority": "High",
                "recommendation": "Use docker-compose.optimized.yml as the primary Docker Compose file",
                "action": "This file contains all optimizations and best practices"
            },
            {
                "category": "General", 
                "priority": "High",
                "recommendation": "Use k8s-optimized/ directory for Kubernetes manifests",
                "action": "This directory contains the most comprehensive and optimized configurations"
            },
            {
                "category": "General",
                "priority": "Medium",
                "recommendation": "Regularly review archived files and delete truly obsolete ones",
                "action": "Schedule quarterly cleanup of archived_bin/ directory"
            }
        ])
        
        return recommendations
    
    def _print_analysis_summary(self):
        """Print comprehensive analysis summary"""
        print("\n" + "="*80)
        print("🎯 DOCKER & KUBERNETES ANALYSIS COMPLETE")
        print("="*80)
        
        summary = self.analysis_results
        
        print(f"\n🐳 Docker Files:")
        print(f"  ✅ SSOT Files: {len(summary['docker_files']['ssot'])}")
        print(f"  📦 Unused Files: {len(summary['docker_files']['unused'])}")
        print(f"  🔄 Duplicate Files: {len(summary['docker_files']['duplicates'])}")
        
        print(f"\n☸️ Kubernetes Files:")
        print(f"  ✅ SSOT Files: {len(summary['kubernetes_files']['ssot'])}")
        print(f"  📦 Unused Files: {len(summary['kubernetes_files']['unused'])}")
        
        print(f"\n🔒 Lock Files:")
        print(f"  ✅ Active Files: {len(summary['lock_files']['active'])}")
        print(f"  📦 Archived Files: {len(summary['lock_files']['archived'])}")
        
        print(f"\n📋 SSOT Files:")
        print(f"  ✅ Active Files: {len(summary['ssot_files']['active'])}")
        print(f"  📦 Archived Files: {len(summary['ssot_files']['archived'])}")
        
        print(f"\n📦 Archive Locations:")
        for category, dir_path in self.archive_dirs.items():
            file_count = len(list(dir_path.rglob("*")))
            print(f"  📁 {category}: {file_count} files")
        
        print(f"\n🎯 Key Recommendations:")
        for rec in self._generate_recommendations()[:5]:  # Show top 5
            print(f"  {rec['priority']}: {rec['recommendation']}")
        
        print("\n🎉 ANALYSIS SUCCESSFUL!")
        print("Docker and Kubernetes configurations have been analyzed and organized!")
        print("Unused files have been archived to archived_bin/ directory!")
        print("="*80)


# Main execution
def main():
    """Main execution function"""
    analyzer = DockerK8sSSOTAnalyzer()
    analyzer.run_comprehensive_analysis()


if __name__ == "__main__":
    main()
