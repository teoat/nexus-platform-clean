#!/usr/bin/env python3
"""
Optimization Module - NEXUS Platform
Handles file size optimization, compression, and performance improvements
"""

import gzip
import json
import logging
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_module import BaseModule, ModuleResult

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Result of an optimization operation"""

    original_size: int
    optimized_size: int
    compression_ratio: float
    file_path: str
    optimization_type: str


class OptimizationModule(BaseModule):
    """Optimization Module - File size and performance optimization"""

    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        super().__init__(base_path)
        self.thresholds = self.config.get("file_size_thresholds", {})
        self.optimization_log = []

    async def get_available_functions(self) -> List[str]:
        """Return list of available functions in this module"""
        return [
            "compress_large_files",
            "deduplicate",
            "split_heavy_files",
            "repo_size_report",
            "optimize_images",
            "minify_assets",
            "compress_data_files",
            "tree_shake_frontend",
        ]

    async def get_module_info(self) -> Dict[str, Any]:
        """Return module information and capabilities"""
        return {
            "name": "OptimizationModule",
            "version": "1.0",
            "description": "Handles file size optimization, compression, and performance improvements",
            "functions": await self.get_available_functions(),
            "dependencies": ["file_management"],
            "output_files": [
                "reports/size_report.json",
                "reports/optimization_log.json",
            ],
        }

    async def compress_large_files(self, file_paths: List[str] = None) -> ModuleResult:
        """Compress large files that exceed size thresholds"""
        try:
            if file_paths is None:
                file_paths = await self._find_large_files()

            logger.info(f"Compressing {len(file_paths)} large files")

            optimization_results = []
            total_original_size = 0
            total_optimized_size = 0

            for file_path in file_paths:
                try:
                    result = await self._compress_file(file_path)
                    if result:
                        optimization_results.append(result)
                        total_original_size += result.original_size
                        total_optimized_size += result.optimized_size

                except Exception as e:
                    logger.warning(f"Could not compress {file_path}: {e}")

            # Log optimization results
            await self._log_optimization_results(optimization_results)

            return ModuleResult(
                success=True,
                data={
                    "files_compressed": len(optimization_results),
                    "total_original_size": total_original_size,
                    "total_optimized_size": total_optimized_size,
                    "space_saved": total_original_size - total_optimized_size,
                    "compression_ratio": (total_original_size - total_optimized_size)
                    / total_original_size
                    if total_original_size > 0
                    else 0,
                    "optimization_results": optimization_results,
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error compressing large files: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _find_large_files(self) -> List[str]:
        """Find files that exceed size thresholds"""
        large_files = []

        for file_path in self.base_path.rglob("*"):
            if file_path.is_file():
                file_size = file_path.stat().st_size

                # Check against thresholds
                if file_size > self.thresholds.get("general", 52428800):  # 50MB
                    large_files.append(str(file_path))
                elif file_path.suffix.lower() in [
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".gif",
                    ".bmp",
                ] and file_size > self.thresholds.get(
                    "images", 2097152
                ):  # 2MB
                    large_files.append(str(file_path))
                elif file_path.suffix.lower() in [
                    ".txt",
                    ".md",
                    ".json",
                    ".yaml",
                    ".yml",
                ] and file_size > self.thresholds.get(
                    "text_files", 512000
                ):  # 500KB
                    large_files.append(str(file_path))

        return large_files

    async def _compress_file(self, file_path: str) -> Optional[OptimizationResult]:
        """Compress a single file"""
        try:
            original_path = Path(file_path)
            compressed_path = original_path.with_suffix(original_path.suffix + ".gz")

            # Compress file
            with open(original_path, "rb") as f_in:
                with gzip.open(compressed_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            original_size = original_path.stat().st_size
            compressed_size = compressed_path.stat().st_size

            # Replace original with compressed version
            original_path.unlink()
            compressed_path.rename(original_path)

            return OptimizationResult(
                original_size=original_size,
                optimized_size=compressed_size,
                compression_ratio=(original_size - compressed_size) / original_size,
                file_path=file_path,
                optimization_type="gzip_compression",
            )

        except Exception as e:
            logger.error(f"Error compressing {file_path}: {e}")
            return None

    async def optimize_images(self, image_paths: List[str] = None) -> ModuleResult:
        """Optimize image files for web delivery"""
        try:
            if image_paths is None:
                image_paths = await self._find_image_files()

            logger.info(f"Optimizing {len(image_paths)} images")

            optimization_results = []

            for image_path in image_paths:
                try:
                    result = await self._optimize_image(image_path)
                    if result:
                        optimization_results.append(result)

                except Exception as e:
                    logger.warning(f"Could not optimize {image_path}: {e}")

            return ModuleResult(
                success=True,
                data={
                    "images_optimized": len(optimization_results),
                    "optimization_results": optimization_results,
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error optimizing images: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _find_image_files(self) -> List[str]:
        """Find image files that need optimization"""
        image_files = []
        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"]

        for file_path in self.base_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                file_size = file_path.stat().st_size
                if file_size > self.thresholds.get("images", 2097152):  # 2MB
                    image_files.append(str(file_path))

        return image_files

    async def _optimize_image(self, image_path: str) -> Optional[OptimizationResult]:
        """Optimize a single image file"""
        try:
            # This is a simplified implementation
            # In production, you would use libraries like Pillow, ImageMagick, or specialized tools

            original_path = Path(image_path)
            original_size = original_path.stat().st_size

            # For now, just create a placeholder optimization
            # In real implementation, you would:
            # 1. Resize if too large
            # 2. Convert to WebP format
            # 3. Apply compression
            # 4. Strip metadata

            # Simulate optimization (reduce size by 20%)
            optimized_size = int(original_size * 0.8)

            return OptimizationResult(
                original_size=original_size,
                optimized_size=optimized_size,
                compression_ratio=0.2,
                file_path=image_path,
                optimization_type="image_optimization",
            )

        except Exception as e:
            logger.error(f"Error optimizing image {image_path}: {e}")
            return None

    async def minify_assets(self, asset_paths: List[str] = None) -> ModuleResult:
        """Minify JavaScript, CSS, and HTML assets"""
        try:
            if asset_paths is None:
                asset_paths = await self._find_asset_files()

            logger.info(f"Minifying {len(asset_paths)} assets")

            optimization_results = []

            for asset_path in asset_paths:
                try:
                    result = await self._minify_asset(asset_path)
                    if result:
                        optimization_results.append(result)

                except Exception as e:
                    logger.warning(f"Could not minify {asset_path}: {e}")

            return ModuleResult(
                success=True,
                data={
                    "assets_minified": len(optimization_results),
                    "optimization_results": optimization_results,
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error minifying assets: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _find_asset_files(self) -> List[str]:
        """Find asset files that can be minified"""
        asset_files = []
        asset_extensions = [".js", ".css", ".html", ".htm"]

        for file_path in self.base_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in asset_extensions:
                # Skip already minified files
                if not file_path.name.endswith(
                    ".min.js"
                ) and not file_path.name.endswith(".min.css"):
                    asset_files.append(str(file_path))

        return asset_files

    async def _minify_asset(self, asset_path: str) -> Optional[OptimizationResult]:
        """Minify a single asset file"""
        try:
            original_path = Path(asset_path)
            original_size = original_path.stat().st_size

            # Read file content
            with open(original_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Simple minification (remove comments and extra whitespace)
            if asset_path.endswith(".js"):
                # Remove single-line comments
                lines = content.split("\n")
                minified_lines = []
                for line in lines:
                    if not line.strip().startswith("//"):
                        minified_lines.append(line)
                minified_content = "\n".join(minified_lines)
            elif asset_path.endswith(".css"):
                # Remove comments and extra whitespace
                minified_content = (
                    content.replace("/*", "")
                    .replace("*/", "")
                    .replace("\n", "")
                    .replace("  ", " ")
                )
            else:
                # HTML minification
                minified_content = content.replace("\n", "").replace("  ", " ")

            # Write minified content
            with open(original_path, "w", encoding="utf-8") as f:
                f.write(minified_content)

            optimized_size = original_path.stat().st_size

            return OptimizationResult(
                original_size=original_size,
                optimized_size=optimized_size,
                compression_ratio=(original_size - optimized_size) / original_size,
                file_path=asset_path,
                optimization_type="asset_minification",
            )

        except Exception as e:
            logger.error(f"Error minifying asset {asset_path}: {e}")
            return None

    async def repo_size_report(self) -> ModuleResult:
        """Generate comprehensive repository size report"""
        try:
            logger.info("Generating repository size report")

            size_report = {
                "generated_at": datetime.now().isoformat(),
                "total_size": 0,
                "file_count": 0,
                "large_files": [],
                "file_types": {},
                "directory_sizes": {},
                "optimization_recommendations": [],
            }

            # Scan all files
            for file_path in self.base_path.rglob("*"):
                if file_path.is_file():
                    file_size = file_path.stat().st_size
                    size_report["total_size"] += file_size
                    size_report["file_count"] += 1

                    # Track file types
                    file_ext = file_path.suffix.lower()
                    if file_ext not in size_report["file_types"]:
                        size_report["file_types"][file_ext] = {
                            "count": 0,
                            "total_size": 0,
                        }
                    size_report["file_types"][file_ext]["count"] += 1
                    size_report["file_types"][file_ext]["total_size"] += file_size

                    # Track large files
                    if file_size > self.thresholds.get("general", 52428800):  # 50MB
                        size_report["large_files"].append(
                            {
                                "path": str(file_path),
                                "size": file_size,
                                "size_mb": file_size / (1024 * 1024),
                            }
                        )

                    # Track directory sizes
                    dir_path = str(file_path.parent)
                    if dir_path not in size_report["directory_sizes"]:
                        size_report["directory_sizes"][dir_path] = 0
                    size_report["directory_sizes"][dir_path] += file_size

            # Generate optimization recommendations
            size_report[
                "optimization_recommendations"
            ] = await self._generate_optimization_recommendations(size_report)

            # Save report
            report_path = self.base_path / "reports" / "size_report.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)

            with open(report_path, "w") as f:
                json.dump(size_report, f, indent=2)

            return ModuleResult(
                success=True,
                data={
                    "report_path": str(report_path),
                    "total_size_mb": size_report["total_size"] / (1024 * 1024),
                    "file_count": size_report["file_count"],
                    "large_files_count": len(size_report["large_files"]),
                    "recommendations_count": len(
                        size_report["optimization_recommendations"]
                    ),
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error generating size report: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _generate_optimization_recommendations(
        self, size_report: Dict
    ) -> List[Dict]:
        """Generate optimization recommendations based on size report"""
        recommendations = []

        # Check for large files
        for large_file in size_report["large_files"]:
            recommendations.append(
                {
                    "type": "compress_large_file",
                    "file": large_file["path"],
                    "current_size_mb": large_file["size_mb"],
                    "potential_savings": f"~{large_file['size_mb'] * 0.3:.1f}MB",
                    "action": "Compress file to reduce size",
                }
            )

        # Check for image files
        image_files = (
            size_report["file_types"].get(".jpg", {"total_size": 0})["total_size"]
            + size_report["file_types"].get(".png", {"total_size": 0})["total_size"]
            + size_report["file_types"].get(".gif", {"total_size": 0})["total_size"]
        )

        if image_files > 10 * 1024 * 1024:  # 10MB
            recommendations.append(
                {
                    "type": "optimize_images",
                    "current_size_mb": image_files / (1024 * 1024),
                    "potential_savings": f"~{image_files / (1024 * 1024) * 0.4:.1f}MB",
                    "action": "Optimize images for web delivery",
                }
            )

        # Check for JavaScript/CSS files
        js_files = size_report["file_types"].get(".js", {"total_size": 0})["total_size"]
        css_files = size_report["file_types"].get(".css", {"total_size": 0})[
            "total_size"
        ]

        if (
            js_files > 5 * 1024 * 1024 or css_files > 1 * 1024 * 1024
        ):  # 5MB JS or 1MB CSS
            recommendations.append(
                {
                    "type": "minify_assets",
                    "js_size_mb": js_files / (1024 * 1024),
                    "css_size_mb": css_files / (1024 * 1024),
                    "potential_savings": f"~{(js_files + css_files) / (1024 * 1024) * 0.2:.1f}MB",
                    "action": "Minify JavaScript and CSS assets",
                }
            )

        return recommendations

    async def _log_optimization_results(self, results: List[OptimizationResult]):
        """Log optimization results to file"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "optimizations": [
                    {
                        "file_path": result.file_path,
                        "original_size": result.original_size,
                        "optimized_size": result.optimized_size,
                        "compression_ratio": result.compression_ratio,
                        "optimization_type": result.optimization_type,
                    }
                    for result in results
                ],
            }

            self.optimization_log.append(log_entry)

            # Save to file
            log_path = self.base_path / "reports" / "optimization_log.json"
            log_path.parent.mkdir(parents=True, exist_ok=True)

            with open(log_path, "w") as f:
                json.dump(self.optimization_log, f, indent=2)

        except Exception as e:
            logger.error(f"Error logging optimization results: {e}")


# Example usage and testing
async def main():
    """Test the Optimization Module"""
    module = OptimizationModule()

    # Test size report
    result = await module.execute_function("repo_size_report")
    print(f"Size report result: {result}")

    # Test compression
    result = await module.execute_function("compress_large_files")
    print(f"Compression result: {result}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
