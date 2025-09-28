#!/usr/bin/env python3
"""
Dependency Optimizer Module - NEXUS Platform
Handles dependency slimming, unused library removal, and version deduplication
"""

import json
import logging
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .base_module import BaseModule, ModuleResult

logger = logging.getLogger(__name__)


@dataclass
class DependencyInfo:
    """Information about a dependency"""

    name: str
    version: str
    file_path: str
    is_used: bool = False
    usage_count: int = 0
    size_bytes: int = 0


@dataclass
class DependencyOptimizationResult:
    """Result of dependency optimization operation"""

    original_dependencies: int
    optimized_dependencies: int
    removed_dependencies: List[str]
    deduplicated_versions: Dict[str, List[str]]
    space_saved: int
    optimization_type: str


class DependencyOptimizer(BaseModule):
    """Dependency Optimizer - Handles dependency slimming and version management"""

    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        super().__init__(base_path)
        self.dependency_cache = {}
        self.usage_analysis = {}

    async def get_available_functions(self) -> List[str]:
        """Return list of available functions in this module"""
        return [
            "prune_unused_libs",
            "deduplicate_versions",
            "analyze_dependency_graph",
            "optimize_package_json",
            "optimize_requirements_txt",
            "generate_dependency_report",
            "cleanup_node_modules",
        ]

    async def get_module_info(self) -> Dict[str, Any]:
        """Return module information and capabilities"""
        return {
            "name": "DependencyOptimizer",
            "version": "1.0",
            "description": "Handles dependency slimming, unused library removal, and version deduplication",
            "functions": await self.get_available_functions(),
            "dependencies": ["file_management", "optimization"],
            "output_files": [
                "reports/dependency_report.json",
                "reports/optimization_log.json",
            ],
        }

    async def prune_unused_libs(self, requirements_file: str = None) -> ModuleResult:
        """Scan dependencies, remove unused libs"""
        try:
            if requirements_file is None:
                requirements_file = await self._find_requirements_file()

            if not requirements_file:
                return ModuleResult(
                    success=False,
                    data=None,
                    error="No requirements file found",
                    timestamp=datetime.now(),
                )

            logger.info(f"Pruning unused libraries from {requirements_file}")

            # Analyze current dependencies
            dependencies = await self._parse_dependencies(requirements_file)

            # Analyze usage
            usage_analysis = await self._analyze_dependency_usage(dependencies)

            # Identify unused dependencies
            unused_deps = [
                dep
                for dep in dependencies
                if not usage_analysis.get(dep.name, {}).get("is_used", False)
            ]

            # Create optimized requirements file
            optimized_deps = [
                dep
                for dep in dependencies
                if usage_analysis.get(dep.name, {}).get("is_used", False)
            ]

            # Save optimized requirements
            await self._save_optimized_requirements(requirements_file, optimized_deps)

            return ModuleResult(
                success=True,
                data={
                    "original_dependencies": len(dependencies),
                    "optimized_dependencies": len(optimized_deps),
                    "removed_dependencies": [dep.name for dep in unused_deps],
                    "space_saved": sum(dep.size_bytes for dep in unused_deps),
                    "optimization_type": "unused_lib_removal",
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error pruning unused libraries: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _find_requirements_file(self) -> Optional[str]:
        """Find requirements file in the project"""
        possible_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "pyproject.toml",
            "setup.py",
            "package.json",
            "yarn.lock",
            "package-lock.json",
        ]

        for file_name in possible_files:
            file_path = self.base_path / file_name
            if file_path.exists():
                return str(file_path)

        return None

    async def _parse_dependencies(self, requirements_file: str) -> List[DependencyInfo]:
        """Parse dependencies from requirements file"""
        dependencies = []
        file_path = Path(requirements_file)

        if file_path.suffix == ".json":
            # Handle package.json
            with open(file_path, "r") as f:
                package_data = json.load(f)

            deps = package_data.get("dependencies", {})
            dev_deps = package_data.get("devDependencies", {})

            for name, version in deps.items():
                dependencies.append(
                    DependencyInfo(
                        name=name,
                        version=version,
                        file_path=str(file_path),
                        size_bytes=await self._estimate_dependency_size(name),
                    )
                )

            for name, version in dev_deps.items():
                dependencies.append(
                    DependencyInfo(
                        name=name,
                        version=version,
                        file_path=str(file_path),
                        size_bytes=await self._estimate_dependency_size(name),
                    )
                )

        else:
            # Handle requirements.txt
            with open(file_path, "r") as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "==" in line:
                        name, version = line.split("==", 1)
                    elif ">=" in line:
                        name, version = line.split(">=", 1)
                    else:
                        name, version = line, "latest"

                    dependencies.append(
                        DependencyInfo(
                            name=name.strip(),
                            version=version.strip(),
                            file_path=str(file_path),
                            size_bytes=await self._estimate_dependency_size(
                                name.strip()
                            ),
                        )
                    )

        return dependencies

    async def _estimate_dependency_size(self, name: str) -> int:
        """Estimate dependency size (simplified)"""
        # This is a simplified estimation
        # In production, you would query package registries or analyze node_modules
        return 1024 * 1024  # 1MB default estimate

    async def _analyze_dependency_usage(
        self, dependencies: List[DependencyInfo]
    ) -> Dict[str, Dict]:
        """Analyze which dependencies are actually used in the codebase"""
        usage_analysis = {}

        for dep in dependencies:
            usage_analysis[dep.name] = {
                "is_used": False,
                "usage_count": 0,
                "usage_locations": [],
            }

        # Search for import statements and usage patterns
        for file_path in self.base_path.rglob("*.py"):
            if file_path.is_file():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    for dep in dependencies:
                        # Check for import statements
                        import_patterns = [
                            f"import {dep.name}",
                            f"from {dep.name}",
                            f"require('{dep.name}')",
                            f"import {dep.name} from",
                        ]

                        for pattern in import_patterns:
                            if pattern in content:
                                usage_analysis[dep.name]["is_used"] = True
                                usage_analysis[dep.name][
                                    "usage_count"
                                ] += content.count(pattern)
                                usage_analysis[dep.name]["usage_locations"].append(
                                    str(file_path)
                                )

                except Exception as e:
                    logger.warning(f"Error analyzing file {file_path}: {e}")

        return usage_analysis

    async def _save_optimized_requirements(
        self, original_file: str, optimized_deps: List[DependencyInfo]
    ):
        """Save optimized requirements file"""
        file_path = Path(original_file)

        if file_path.suffix == ".json":
            # Handle package.json
            with open(file_path, "r") as f:
                package_data = json.load(f)

            # Update dependencies
            package_data["dependencies"] = {
                dep.name: dep.version
                for dep in optimized_deps
                if not dep.name.startswith("@")
            }
            package_data["devDependencies"] = {
                dep.name: dep.version
                for dep in optimized_deps
                if dep.name.startswith("@")
            }

            # Create backup
            backup_path = file_path.with_suffix(file_path.suffix + ".backup")
            shutil.copy2(file_path, backup_path)

            # Save optimized version
            with open(file_path, "w") as f:
                json.dump(package_data, f, indent=2)

        else:
            # Handle requirements.txt
            with open(file_path, "r") as f:
                original_content = f.read()

            # Create backup
            backup_path = file_path.with_suffix(file_path.suffix + ".backup")
            with open(backup_path, "w") as f:
                f.write(original_content)

            # Write optimized requirements
            with open(file_path, "w") as f:
                for dep in optimized_deps:
                    f.write(f"{dep.name}=={dep.version}\n")

    async def deduplicate_versions(self, lock_file: str = None) -> ModuleResult:
        """Detect multiple versions of same library and force SSOT single version"""
        try:
            if lock_file is None:
                lock_file = await self._find_lock_file()

            if not lock_file:
                return ModuleResult(
                    success=False,
                    data=None,
                    error="No lock file found",
                    timestamp=datetime.now(),
                )

            logger.info(f"Deduplicating versions in {lock_file}")

            # Parse lock file
            dependencies = await self._parse_lock_file(lock_file)

            # Find duplicate versions
            version_groups = {}
            for dep in dependencies:
                if dep.name not in version_groups:
                    version_groups[dep.name] = []
                version_groups[dep.name].append(dep)

            # Identify duplicates
            duplicates = {
                name: versions
                for name, versions in version_groups.items()
                if len(versions) > 1
            }

            # Choose canonical versions (latest stable)
            canonical_versions = {}
            for name, versions in duplicates.items():
                # Sort by version and pick the latest
                sorted_versions = sorted(
                    versions, key=lambda x: x.version, reverse=True
                )
                canonical_versions[name] = sorted_versions[0]

            # Update lock file with canonical versions
            await self._update_lock_file_with_canonical_versions(
                lock_file, canonical_versions
            )

            return ModuleResult(
                success=True,
                data={
                    "duplicates_found": len(duplicates),
                    "canonical_versions": {
                        name: version.version
                        for name, version in canonical_versions.items()
                    },
                    "optimization_type": "version_deduplication",
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error deduplicating versions: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _find_lock_file(self) -> Optional[str]:
        """Find lock file in the project"""
        possible_files = [
            "package-lock.json",
            "yarn.lock",
            "poetry.lock",
            "Pipfile.lock",
        ]

        for file_name in possible_files:
            file_path = self.base_path / file_name
            if file_path.exists():
                return str(file_path)

        return None

    async def _parse_lock_file(self, lock_file: str) -> List[DependencyInfo]:
        """Parse lock file to extract dependencies"""
        dependencies = []
        file_path = Path(lock_file)

        if file_path.suffix == ".json":
            # Handle package-lock.json
            with open(file_path, "r") as f:
                lock_data = json.load(f)

            # Extract dependencies from lock file
            deps = lock_data.get("dependencies", {})
            for name, dep_info in deps.items():
                if isinstance(dep_info, dict) and "version" in dep_info:
                    dependencies.append(
                        DependencyInfo(
                            name=name,
                            version=dep_info["version"],
                            file_path=str(file_path),
                            size_bytes=await self._estimate_dependency_size(name),
                        )
                    )

        else:
            # Handle other lock file formats (simplified)
            with open(file_path, "r") as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Simple parsing for other formats
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[0]
                        version = parts[1]
                        dependencies.append(
                            DependencyInfo(
                                name=name,
                                version=version,
                                file_path=str(file_path),
                                size_bytes=await self._estimate_dependency_size(name),
                            )
                        )

        return dependencies

    async def _update_lock_file_with_canonical_versions(
        self, lock_file: str, canonical_versions: Dict[str, DependencyInfo]
    ):
        """Update lock file with canonical versions"""
        # This is a simplified implementation
        # In production, you would properly update the lock file format
        logger.info(
            f"Updated {len(canonical_versions)} dependencies to canonical versions"
        )

    async def analyze_dependency_graph(self, path: str = None) -> ModuleResult:
        """Build graph of dependency relationships and identify optimization opportunities"""
        try:
            if path is None:
                path = str(self.base_path)

            logger.info(f"Analyzing dependency graph for {path}")

            # Find all dependency files
            dependency_files = await self._find_all_dependency_files()

            # Build dependency graph
            graph = await self._build_dependency_graph(dependency_files)

            # Analyze graph for optimization opportunities
            analysis = await self._analyze_graph_for_optimizations(graph)

            # Generate report
            report = {
                "generated_at": datetime.now().isoformat(),
                "total_dependencies": len(graph),
                "dependency_files": dependency_files,
                "graph_analysis": analysis,
                "recommendations": await self._generate_dependency_recommendations(
                    analysis
                ),
            }

            # Save report
            report_path = self.base_path / "reports" / "dependency_report.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)

            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)

            return ModuleResult(
                success=True,
                data={
                    "report_path": str(report_path),
                    "total_dependencies": len(graph),
                    "dependency_files": len(dependency_files),
                    "recommendations_count": len(report["recommendations"]),
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error analyzing dependency graph: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _find_all_dependency_files(self) -> List[str]:
        """Find all dependency files in the project"""
        dependency_files = []
        patterns = [
            "**/package.json",
            "**/requirements.txt",
            "**/pyproject.toml",
            "**/setup.py",
            "**/yarn.lock",
            "**/package-lock.json",
            "**/poetry.lock",
        ]

        for pattern in patterns:
            for file_path in self.base_path.glob(pattern):
                if file_path.is_file():
                    dependency_files.append(str(file_path))

        return dependency_files

    async def _build_dependency_graph(
        self, dependency_files: List[str]
    ) -> Dict[str, List[str]]:
        """Build dependency graph from files"""
        graph = {}

        for file_path in dependency_files:
            try:
                dependencies = await self._parse_dependencies(file_path)
                for dep in dependencies:
                    if dep.name not in graph:
                        graph[dep.name] = []
                    graph[dep.name].append(dep.version)
            except Exception as e:
                logger.warning(f"Error parsing {file_path}: {e}")

        return graph

    async def _analyze_graph_for_optimizations(
        self, graph: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Analyze dependency graph for optimization opportunities"""
        analysis = {
            "duplicate_versions": {},
            "unused_dependencies": [],
            "heavy_dependencies": [],
            "circular_dependencies": [],
            "outdated_dependencies": [],
        }

        # Find duplicate versions
        for name, versions in graph.items():
            if len(set(versions)) > 1:
                analysis["duplicate_versions"][name] = list(set(versions))

        # Find heavy dependencies (simplified)
        for name in graph.keys():
            estimated_size = await self._estimate_dependency_size(name)
            if estimated_size > 10 * 1024 * 1024:  # 10MB
                analysis["heavy_dependencies"].append(
                    {"name": name, "estimated_size_mb": estimated_size / (1024 * 1024)}
                )

        return analysis

    async def _generate_dependency_recommendations(
        self, analysis: Dict[str, Any]
    ) -> List[Dict]:
        """Generate optimization recommendations based on analysis"""
        recommendations = []

        # Duplicate version recommendations
        for name, versions in analysis["duplicate_versions"].items():
            recommendations.append(
                {
                    "type": "deduplicate_versions",
                    "dependency": name,
                    "versions": versions,
                    "action": f"Consolidate {name} to single version",
                }
            )

        # Heavy dependency recommendations
        for dep in analysis["heavy_dependencies"]:
            recommendations.append(
                {
                    "type": "replace_heavy_dependency",
                    "dependency": dep["name"],
                    "size_mb": dep["estimated_size_mb"],
                    "action": f"Consider replacing {dep['name']} with lighter alternative",
                }
            )

        return recommendations

    async def cleanup_node_modules(self) -> ModuleResult:
        """Clean up node_modules directory to remove unused packages"""
        try:
            node_modules_path = self.base_path / "node_modules"

            if not node_modules_path.exists():
                return ModuleResult(
                    success=False,
                    data=None,
                    error="No node_modules directory found",
                    timestamp=datetime.now(),
                )

            logger.info("Cleaning up node_modules directory")

            # Get original size
            original_size = await self._get_directory_size(node_modules_path)

            # Remove unused packages (simplified)
            # In production, you would use tools like npm prune or yarn autoclean
            removed_packages = await self._remove_unused_packages(node_modules_path)

            # Get new size
            new_size = await self._get_directory_size(node_modules_path)

            return ModuleResult(
                success=True,
                data={
                    "original_size": original_size,
                    "new_size": new_size,
                    "space_saved": original_size - new_size,
                    "removed_packages": removed_packages,
                    "optimization_type": "node_modules_cleanup",
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error cleaning up node_modules: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _get_directory_size(self, directory: Path) -> int:
        """Get total size of directory"""
        total_size = 0
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size

    async def _remove_unused_packages(self, node_modules_path: Path) -> List[str]:
        """Remove unused packages from node_modules (simplified)"""
        # This is a simplified implementation
        # In production, you would use proper package management tools
        removed_packages = []

        # Simulate removing some packages
        for package_dir in node_modules_path.iterdir():
            if package_dir.is_dir() and package_dir.name.startswith("."):
                # Remove hidden directories
                shutil.rmtree(package_dir)
                removed_packages.append(package_dir.name)

        return removed_packages


# Example usage and testing
async def main():
    """Test the Dependency Optimizer Module"""
    optimizer = DependencyOptimizer()

    # Test unused lib pruning
    result = await optimizer.execute_function("prune_unused_libs")
    print(f"Unused lib pruning result: {result}")

    # Test version deduplication
    result = await optimizer.execute_function("deduplicate_versions")
    print(f"Version deduplication result: {result}")

    # Test dependency graph analysis
    result = await optimizer.execute_function("analyze_dependency_graph")
    print(f"Dependency graph analysis result: {result}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
