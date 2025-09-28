#!/usr/bin/env python3
"""
NUC Intelligent Workspace Cleaner
AI-powered file classification and intelligent cleanup system
"""

import asyncio
import hashlib
import json
import logging
import shutil
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import aiofiles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CleanupAction(Enum):
    """Cleanup action types"""
    DELETE = "delete"
    ARCHIVE = "archive"
    COMPRESS = "compress"
    MOVE = "move"
    KEEP = "keep"
    QUARANTINE = "quarantine"


class FileImportance(Enum):
    """File importance levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    REMOVABLE = 5


@dataclass
class FileAnalysis:
    """File analysis result"""
    path: Path
    size: int
    modified: datetime
    accessed: datetime
    importance: FileImportance
    category: str
    confidence: float
    dependencies: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CleanupPlan:
    """Cleanup plan for files"""
    file_path: Path
    action: CleanupAction
    reason: str
    priority: int
    estimated_space_saved: int
    risk_level: str
    backup_required: bool = False


class IntelligentWorkspaceCleaner:
    """AI-powered intelligent workspace cleaner"""
    
    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        self.base_path = Path(base_path)
        self.file_analyses: Dict[str, FileAnalysis] = {}
        self.cleanup_plans: List[CleanupPlan] = []
        self.essential_patterns: Set[str] = set()
        self.removable_patterns: Set[str] = set()
        
        # Statistics
        self.stats = {
            "files_analyzed": 0,
            "files_cleaned": 0,
            "space_saved": 0,
            "errors": 0,
            "false_positives": 0
        }
        
        # Initialize patterns
        self._init_patterns()
    
    def _init_patterns(self):
        """Initialize file patterns for classification"""
        # Essential patterns (never remove)
        self.essential_patterns = {
            # Core application files
            "package.json", "package-lock.json", "requirements.txt",
            "docker-compose.yml", "Dockerfile*", "*.py", "*.ts", "*.tsx",
            "*.js", "*.jsx", "*.json", "*.yaml", "*.yml",
            
            # Source code directories
            "frontend/web/src/**", "backend/**", "nexus/**",
            "config/**", "docker/**", "nginx/**",
            
            # Database files
            "*.db", "*.sqlite", "*.sql",
            
            # Environment files
            "*.env*", "*.config", "*.conf"
        }
        
        # Removable patterns (safe to remove)
        self.removable_patterns = {
            # Log files
            "*.log", "logs/**", "*.out", "*.err",
            
            # Temporary files
            "__pycache__/**", "*.pyc", "*.pyo", "*.pyd",
            "*.tmp", "*.temp", "*.swp", "*.swo",
            ".DS_Store", "Thumbs.db",
            
            # Build artifacts
            "build/**", "dist/**", "node_modules/**",
            "*.egg-info/**", ".pytest_cache/**",
            
            # Backup files
            "backup*/**", "*.bak", "*.backup", "*.old",
            "*.orig", "*.rej",
            
            # Cache files
            ".cache/**", "*.cache", ".npm/**", ".yarn/**",
            
            # IDE files
            ".vscode/**", ".idea/**", "*.sublime-*",
            
            # OS files
            ".DS_Store", "Thumbs.db", "desktop.ini"
        }
    
    async def analyze_workspace(self) -> Dict[str, Any]:
        """Analyze entire workspace and create cleanup plan"""
        logger.info("Starting intelligent workspace analysis...")
        
        try:
            # Scan all files
            await self._scan_files()
            
            # Analyze file importance
            await self._analyze_file_importance()
            
            # Detect dependencies
            await self._detect_dependencies()
            
            # Create cleanup plan
            await self._create_cleanup_plan()
            
            # Generate report
            report = self._generate_analysis_report()
            
            logger.info(f"Workspace analysis complete: {len(self.file_analyses)} files analyzed")
            return report
            
        except Exception as e:
            logger.error(f"Error analyzing workspace: {e}")
            self.stats["errors"] += 1
            return {"error": str(e)}
    
    async def _scan_files(self):
        """Scan all files in workspace"""
        for file_path in self.base_path.rglob("*"):
            if file_path.is_file():
                try:
                    stat_info = file_path.stat()
                    
                    analysis = FileAnalysis(
                        path=file_path,
                        size=stat_info.st_size,
                        modified=datetime.fromtimestamp(stat_info.st_mtime),
                        accessed=datetime.fromtimestamp(stat_info.st_atime),
                        importance=FileImportance.MEDIUM,  # Default
                        category="unknown",
                        confidence=0.0
                    )
                    
                    self.file_analyses[str(file_path)] = analysis
                    self.stats["files_analyzed"] += 1
                    
                except Exception as e:
                    logger.error(f"Error scanning file {file_path}: {e}")
                    self.stats["errors"] += 1
    
    async def _analyze_file_importance(self):
        """Analyze file importance using multiple heuristics"""
        for file_path, analysis in self.file_analyses.items():
            try:
                # Check against essential patterns
                if self._matches_patterns(analysis.path, self.essential_patterns):
                    analysis.importance = FileImportance.CRITICAL
                    analysis.category = "essential"
                    analysis.confidence = 0.9
                    continue
                
                # Check against removable patterns
                if self._matches_patterns(analysis.path, self.removable_patterns):
                    analysis.importance = FileImportance.REMOVABLE
                    analysis.category = "removable"
                    analysis.confidence = 0.8
                    continue
                
                # Analyze file content for importance
                await self._analyze_file_content(analysis)
                
                # Analyze file usage patterns
                await self._analyze_usage_patterns(analysis)
                
                # Analyze file relationships
                await self._analyze_file_relationships(analysis)
                
            except Exception as e:
                logger.error(f"Error analyzing file importance {file_path}: {e}")
                self.stats["errors"] += 1
    
    def _matches_patterns(self, file_path: Path, patterns: Set[str]) -> bool:
        """Check if file matches any of the given patterns"""
        path_str = str(file_path.relative_to(self.base_path))
        
        for pattern in patterns:
            if "**" in pattern:
                # Recursive pattern matching
                pattern_parts = pattern.split("**")
                if len(pattern_parts) == 2:
                    prefix, suffix = pattern_parts
                    if path_str.startswith(prefix.replace("**", "")) and path_str.endswith(suffix.replace("**", "")):
                        return True
            elif "*" in pattern:
                # Wildcard pattern matching
                import fnmatch
                if fnmatch.fnmatch(path_str, pattern):
                    return True
            else:
                # Exact match
                if pattern in path_str:
                    return True
        
        return False
    
    async def _analyze_file_content(self, analysis: FileAnalysis):
        """Analyze file content for importance indicators"""
        try:
            # Check file extension
            ext = analysis.path.suffix.lower()
            
            if ext in ['.py', '.ts', '.tsx', '.js', '.jsx']:
                analysis.importance = FileImportance.HIGH
                analysis.category = "source_code"
                analysis.confidence = 0.8
            elif ext in ['.json', '.yaml', '.yml', '.conf', '.config']:
                analysis.importance = FileImportance.HIGH
                analysis.category = "configuration"
                analysis.confidence = 0.7
            elif ext in ['.md', '.txt', '.rst']:
                analysis.importance = FileImportance.MEDIUM
                analysis.category = "documentation"
                analysis.confidence = 0.6
            elif ext in ['.log', '.out', '.err']:
                analysis.importance = FileImportance.REMOVABLE
                analysis.category = "log_file"
                analysis.confidence = 0.9
            
            # Check file size for importance
            if analysis.size > 100 * 1024 * 1024:  # > 100MB
                analysis.importance = FileImportance.LOW
                analysis.confidence = min(analysis.confidence + 0.1, 1.0)
            
            # Check if file is recently modified
            days_since_modified = (datetime.now() - analysis.modified).days
            if days_since_modified < 7:
                analysis.importance = FileImportance.HIGH
                analysis.confidence = min(analysis.confidence + 0.2, 1.0)
            elif days_since_modified > 90:
                analysis.importance = FileImportance.LOW
                analysis.confidence = min(analysis.confidence + 0.1, 1.0)
                
        except Exception as e:
            logger.error(f"Error analyzing file content {analysis.path}: {e}")
    
    async def _analyze_usage_patterns(self, analysis: FileAnalysis):
        """Analyze file usage patterns"""
        try:
            # Check if file is in active development directories
            path_str = str(analysis.path)
            
            if any(dir_name in path_str for dir_name in ['src', 'app', 'lib', 'components']):
                analysis.importance = FileImportance.HIGH
                analysis.confidence = min(analysis.confidence + 0.2, 1.0)
            
            # Check if file is in test directories
            if any(dir_name in path_str for dir_name in ['test', 'tests', '__tests__', 'spec']):
                analysis.importance = FileImportance.MEDIUM
                analysis.confidence = min(analysis.confidence + 0.1, 1.0)
            
            # Check if file is in documentation directories
            if any(dir_name in path_str for dir_name in ['docs', 'documentation', 'readme']):
                analysis.importance = FileImportance.MEDIUM
                analysis.confidence = min(analysis.confidence + 0.1, 1.0)
                
        except Exception as e:
            logger.error(f"Error analyzing usage patterns {analysis.path}: {e}")
    
    async def _analyze_file_relationships(self, analysis: FileAnalysis):
        """Analyze file relationships and dependencies"""
        try:
            # Look for import statements in source files
            if analysis.path.suffix in ['.py', '.ts', '.tsx', '.js', '.jsx']:
                await self._find_imports(analysis)
            
            # Look for references in configuration files
            if analysis.path.suffix in ['.json', '.yaml', '.yml']:
                await self._find_config_references(analysis)
                
        except Exception as e:
            logger.error(f"Error analyzing file relationships {analysis.path}: {e}")
    
    async def _find_imports(self, analysis: FileAnalysis):
        """Find import statements in source files"""
        try:
            async with aiofiles.open(analysis.path, 'r', encoding='utf-8') as f:
                content = await f.read()
                
                # Simple import detection (can be enhanced)
                import_lines = [line.strip() for line in content.split('\n') 
                              if line.strip().startswith(('import ', 'from '))]
                
                if import_lines:
                    analysis.metadata['imports'] = import_lines
                    analysis.importance = FileImportance.HIGH
                    analysis.confidence = min(analysis.confidence + 0.1, 1.0)
                    
        except Exception as e:
            logger.error(f"Error finding imports {analysis.path}: {e}")
    
    async def _find_config_references(self, analysis: FileAnalysis):
        """Find references in configuration files"""
        try:
            async with aiofiles.open(analysis.path, 'r', encoding='utf-8') as f:
                content = await f.read()
                
                # Look for file references
                import re
                file_refs = re.findall(r'["\']([^"\']*\.(py|ts|tsx|js|jsx|json|yaml|yml))["\']', content)
                
                if file_refs:
                    analysis.metadata['references'] = [ref[0] for ref in file_refs]
                    analysis.importance = FileImportance.HIGH
                    analysis.confidence = min(analysis.confidence + 0.1, 1.0)
                    
        except Exception as e:
            logger.error(f"Error finding config references {analysis.path}: {e}")
    
    async def _detect_dependencies(self):
        """Detect file dependencies"""
        for file_path, analysis in self.file_analyses.items():
            try:
                # Find files that depend on this file
                dependencies = []
                
                for other_path, other_analysis in self.file_analyses.items():
                    if other_path == file_path:
                        continue
                    
                    # Check if this file is referenced by other files
                    if 'references' in other_analysis.metadata:
                        if str(analysis.path.relative_to(self.base_path)) in other_analysis.metadata['references']:
                            dependencies.append(other_path)
                
                analysis.dependencies = dependencies
                
            except Exception as e:
                logger.error(f"Error detecting dependencies {file_path}: {e}")
    
    async def _create_cleanup_plan(self):
        """Create intelligent cleanup plan"""
        self.cleanup_plans = []
        
        for file_path, analysis in self.file_analyses.items():
            try:
                plan = await self._create_file_cleanup_plan(analysis)
                if plan:
                    self.cleanup_plans.append(plan)
                    
            except Exception as e:
                logger.error(f"Error creating cleanup plan {file_path}: {e}")
    
    async def _create_file_cleanup_plan(self, analysis: FileAnalysis) -> Optional[CleanupPlan]:
        """Create cleanup plan for a specific file"""
        try:
            # Skip essential files
            if analysis.importance == FileImportance.CRITICAL:
                return None
            
            # Determine action based on importance and confidence
            if analysis.importance == FileImportance.REMOVABLE and analysis.confidence > 0.8:
                action = CleanupAction.DELETE
                reason = "Safe to remove based on pattern matching"
                priority = 1
                risk_level = "low"
            elif analysis.importance == FileImportance.LOW and analysis.confidence > 0.7:
                action = CleanupAction.ARCHIVE
                reason = "Low importance, archive for safety"
                priority = 2
                risk_level = "medium"
            elif analysis.importance == FileImportance.MEDIUM and analysis.confidence > 0.6:
                action = CleanupAction.COMPRESS
                reason = "Medium importance, compress to save space"
                priority = 3
                risk_level = "low"
            else:
                action = CleanupAction.KEEP
                reason = "Uncertain importance, keep for safety"
                priority = 5
                risk_level = "high"
            
            # Calculate estimated space saved
            if action in [CleanupAction.DELETE, CleanupAction.ARCHIVE, CleanupAction.COMPRESS]:
                estimated_space_saved = analysis.size
            else:
                estimated_space_saved = 0
            
            return CleanupPlan(
                file_path=analysis.path,
                action=action,
                reason=reason,
                priority=priority,
                estimated_space_saved=estimated_space_saved,
                risk_level=risk_level,
                backup_required=action in [CleanupAction.DELETE, CleanupAction.ARCHIVE]
            )
            
        except Exception as e:
            logger.error(f"Error creating file cleanup plan {analysis.path}: {e}")
            return None
    
    def _generate_analysis_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        total_files = len(self.file_analyses)
        total_size = sum(analysis.size for analysis in self.file_analyses.values())
        
        # Categorize files by importance
        importance_counts = {}
        for importance in FileImportance:
            count = len([a for a in self.file_analyses.values() if a.importance == importance])
            importance_counts[importance.name] = count
        
        # Categorize files by category
        category_counts = {}
        for analysis in self.file_analyses.values():
            category = analysis.category
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Calculate cleanup potential
        cleanup_plans = [p for p in self.cleanup_plans if p.action != CleanupAction.KEEP]
        total_space_savings = sum(p.estimated_space_saved for p in cleanup_plans)
        
        return {
            "summary": {
                "total_files": total_files,
                "total_size_mb": total_size / (1024 * 1024),
                "files_by_importance": importance_counts,
                "files_by_category": category_counts
            },
            "cleanup_potential": {
                "files_to_clean": len(cleanup_plans),
                "estimated_space_saved_mb": total_space_savings / (1024 * 1024),
                "cleanup_plans": [
                    {
                        "file": str(p.file_path.relative_to(self.base_path)),
                        "action": p.action.value,
                        "reason": p.reason,
                        "priority": p.priority,
                        "space_saved_mb": p.estimated_space_saved / (1024 * 1024),
                        "risk_level": p.risk_level
                    }
                    for p in cleanup_plans
                ]
            },
            "recommendations": self._generate_recommendations(),
            "stats": self.stats
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate cleanup recommendations"""
        recommendations = []
        
        # Check for large files
        large_files = [a for a in self.file_analyses.values() if a.size > 100 * 1024 * 1024]
        if large_files:
            recommendations.append(f"Found {len(large_files)} large files (>100MB) that could be compressed or archived")
        
        # Check for old log files
        old_logs = [a for a in self.file_analyses.values() 
                   if a.category == "log_file" and (datetime.now() - a.modified).days > 30]
        if old_logs:
            recommendations.append(f"Found {len(old_logs)} old log files that can be safely removed")
        
        # Check for temporary files
        temp_files = [a for a in self.file_analyses.values() if a.category == "temp_file"]
        if temp_files:
            recommendations.append(f"Found {len(temp_files)} temporary files that can be cleaned up")
        
        # Check for duplicate files
        file_hashes = {}
        duplicates = []
        for analysis in self.file_analyses.values():
            try:
                file_hash = hashlib.md5(analysis.path.read_bytes()).hexdigest()
                if file_hash in file_hashes:
                    duplicates.append((file_hashes[file_hash], analysis.path))
                else:
                    file_hashes[file_hash] = analysis.path
            except:
                pass
        
        if duplicates:
            recommendations.append(f"Found {len(duplicates)} potential duplicate files")
        
        return recommendations
    
    async def execute_cleanup(self, dry_run: bool = True) -> Dict[str, Any]:
        """Execute the cleanup plan"""
        logger.info(f"Executing cleanup plan (dry_run={dry_run})...")
        
        results = {
            "files_processed": 0,
            "files_cleaned": 0,
            "space_saved": 0,
            "errors": 0,
            "actions": []
        }
        
        try:
            # Sort cleanup plans by priority
            sorted_plans = sorted(self.cleanup_plans, key=lambda p: p.priority)
            
            for plan in sorted_plans:
                try:
                    action_result = await self._execute_cleanup_action(plan, dry_run)
                    results["actions"].append(action_result)
                    results["files_processed"] += 1
                    
                    if action_result["success"]:
                        results["files_cleaned"] += 1
                        results["space_saved"] += plan.estimated_space_saved
                    else:
                        results["errors"] += 1
                        
                except Exception as e:
                    logger.error(f"Error executing cleanup action {plan.file_path}: {e}")
                    results["errors"] += 1
            
            self.stats["files_cleaned"] += results["files_cleaned"]
            self.stats["space_saved"] += results["space_saved"]
            
            logger.info(f"Cleanup execution complete: {results['files_cleaned']} files cleaned, {results['space_saved'] / (1024 * 1024):.2f} MB saved")
            
        except Exception as e:
            logger.error(f"Error executing cleanup: {e}")
            results["error"] = str(e)
        
        return results
    
    async def _execute_cleanup_action(self, plan: CleanupPlan, dry_run: bool) -> Dict[str, Any]:
        """Execute a single cleanup action"""
        try:
            if dry_run:
                return {
                    "file": str(plan.file_path),
                    "action": plan.action.value,
                    "success": True,
                    "dry_run": True,
                    "message": f"Would {plan.action.value} {plan.file_path}"
                }
            
            if plan.action == CleanupAction.DELETE:
                plan.file_path.unlink()
                message = f"Deleted {plan.file_path}"
            elif plan.action == CleanupAction.ARCHIVE:
                archive_dir = self.base_path / "archived_cleanup"
                archive_dir.mkdir(exist_ok=True)
                shutil.move(str(plan.file_path), str(archive_dir / plan.file_path.name))
                message = f"Archived {plan.file_path}"
            elif plan.action == CleanupAction.COMPRESS:
                # Simple compression (in production, use proper compression)
                compressed_path = plan.file_path.with_suffix(plan.file_path.suffix + ".gz")
                # Implementation would compress the file
                message = f"Compressed {plan.file_path}"
            else:
                message = f"Kept {plan.file_path}"
            
            return {
                "file": str(plan.file_path),
                "action": plan.action.value,
                "success": True,
                "dry_run": False,
                "message": message
            }
            
        except Exception as e:
            return {
                "file": str(plan.file_path),
                "action": plan.action.value,
                "success": False,
                "error": str(e)
            }


# Global cleaner instance
workspace_cleaner = IntelligentWorkspaceCleaner()


async def main():
    """Main entry point for testing"""
    try:
        # Analyze workspace
        report = await workspace_cleaner.analyze_workspace()
        print(f"Analysis Report: {json.dumps(report, indent=2)}")
        
        # Execute cleanup (dry run)
        results = await workspace_cleaner.execute_cleanup(dry_run=True)
        print(f"Cleanup Results: {json.dumps(results, indent=2)}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
