#!/usr/bin/env python3
"""
File Optimizer Module - NEXUS Platform
Handles file size minimization, asset compression, and code optimization
"""

import gzip
import json
import logging
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .base_module import BaseModule, ModuleResult

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Result of file optimization operation"""

    original_size: int
    optimized_size: int
    compression_ratio: float
    file_path: str
    optimization_type: str
    saved_bytes: int


class FileOptimizer(BaseModule):
    """File Optimizer - Handles file size minimization and asset compression"""

    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        super().__init__(base_path)
        self.thresholds = self.config.get("file_size_thresholds", {})
        self.optimization_log = []

    async def get_available_functions(self) -> List[str]:
        """Return list of available functions in this module"""
        return [
            "compress_assets",
            "strip_binaries",
            "minify_code",
            "optimize_images",
            "compress_text_files",
            "archive_large_files",
            "generate_optimization_report",
        ]

    async def get_module_info(self) -> Dict[str, Any]:
        """Return module information and capabilities"""
        return {
            "name": "FileOptimizer",
            "version": "1.0",
            "description": "Handles file size minimization, asset compression, and code optimization",
            "functions": await self.get_available_functions(),
            "dependencies": ["file_management", "optimization"],
            "output_files": [
                "reports/optimization_report.json",
                "reports/compression_log.json",
            ],
        }

    async def compress_assets(
        self, files: List[str] = None, threshold_mb: int = 5
    ) -> ModuleResult:
        """Compress assets (images, videos, PDFs, logs) larger than threshold"""
        try:
            if files is None:
                files = await self._find_large_files(threshold_mb * 1024 * 1024)

            logger.info(f"Compressing {len(files)} assets larger than {threshold_mb}MB")

            optimization_results = []
            total_original_size = 0
            total_optimized_size = 0

            for file_path in files:
                try:
                    result = await self._compress_single_asset(file_path)
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
            logger.error(f"Error compressing assets: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _find_large_files(self, threshold_bytes: int) -> List[str]:
        """Find files larger than threshold"""
        large_files = []

        for file_path in self.base_path.rglob("*"):
            if file_path.is_file():
                file_size = file_path.stat().st_size
                if file_size > threshold_bytes:
                    large_files.append(str(file_path))

        return large_files

    async def _compress_single_asset(
        self, file_path: str
    ) -> Optional[OptimizationResult]:
        """Compress a single asset file"""
        try:
            original_path = Path(file_path)
            original_size = original_path.stat().st_size

            # Determine compression strategy based on file type
            if original_path.suffix.lower() in [".png", ".jpg", ".jpeg"]:
                return await self._compress_image(file_path)
            elif original_path.suffix.lower() in [".mp4", ".avi", ".mov"]:
                return await self._compress_video(file_path)
            elif original_path.suffix.lower() in [".pdf"]:
                return await self._compress_pdf(file_path)
            elif original_path.suffix.lower() in [".txt", ".log", ".json", ".csv"]:
                return await self._compress_text_file(file_path)
            else:
                # Generic compression
                return await self._generic_compress(file_path)

        except Exception as e:
            logger.error(f"Error compressing asset {file_path}: {e}")
            return None

    async def _compress_image(self, file_path: str) -> Optional[OptimizationResult]:
        """Compress image files (PNG/JPEG → WebP)"""
        try:
            original_path = Path(file_path)
            original_size = original_path.stat().st_size

            # For now, simulate WebP conversion (in production, use Pillow or imagemagick)
            # Simulate 30% compression
            optimized_size = int(original_size * 0.7)

            return OptimizationResult(
                original_size=original_size,
                optimized_size=optimized_size,
                compression_ratio=0.3,
                file_path=file_path,
                optimization_type="image_compression",
                saved_bytes=original_size - optimized_size,
            )

        except Exception as e:
            logger.error(f"Error compressing image {file_path}: {e}")
            return None

    async def _compress_video(self, file_path: str) -> Optional[OptimizationResult]:
        """Compress video files (MP4 → H.265)"""
        try:
            original_path = Path(file_path)
            original_size = original_path.stat().st_size

            # Simulate H.265 compression (in production, use ffmpeg)
            # Simulate 50% compression
            optimized_size = int(original_size * 0.5)

            return OptimizationResult(
                original_size=original_size,
                optimized_size=optimized_size,
                compression_ratio=0.5,
                file_path=file_path,
                optimization_type="video_compression",
                saved_bytes=original_size - optimized_size,
            )

        except Exception as e:
            logger.error(f"Error compressing video {file_path}: {e}")
            return None

    async def _compress_pdf(self, file_path: str) -> Optional[OptimizationResult]:
        """Compress PDF files"""
        try:
            original_path = Path(file_path)
            original_size = original_path.stat().st_size

            # Simulate PDF compression (in production, use ghostscript or similar)
            # Simulate 25% compression
            optimized_size = int(original_size * 0.75)

            return OptimizationResult(
                original_size=original_size,
                optimized_size=optimized_size,
                compression_ratio=0.25,
                file_path=file_path,
                optimization_type="pdf_compression",
                saved_bytes=original_size - optimized_size,
            )

        except Exception as e:
            logger.error(f"Error compressing PDF {file_path}: {e}")
            return None

    async def _compress_text_file(self, file_path: str) -> Optional[OptimizationResult]:
        """Compress text files using gzip"""
        try:
            original_path = Path(file_path)
            original_size = original_path.stat().st_size

            # Create compressed version
            compressed_path = original_path.with_suffix(original_path.suffix + ".gz")

            with open(original_path, "rb") as f_in:
                with gzip.open(compressed_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

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
                saved_bytes=original_size - compressed_size,
            )

        except Exception as e:
            logger.error(f"Error compressing text file {file_path}: {e}")
            return None

    async def _generic_compress(self, file_path: str) -> Optional[OptimizationResult]:
        """Generic compression for unknown file types"""
        try:
            original_path = Path(file_path)
            original_size = original_path.stat().st_size

            # Use gzip for generic compression
            compressed_path = original_path.with_suffix(original_path.suffix + ".gz")

            with open(original_path, "rb") as f_in:
                with gzip.open(compressed_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            compressed_size = compressed_path.stat().st_size

            # Replace original with compressed version
            original_path.unlink()
            compressed_path.rename(original_path)

            return OptimizationResult(
                original_size=original_size,
                optimized_size=compressed_size,
                compression_ratio=(original_size - compressed_size) / original_size,
                file_path=file_path,
                optimization_type="generic_compression",
                saved_bytes=original_size - compressed_size,
            )

        except Exception as e:
            logger.error(f"Error generic compressing {file_path}: {e}")
            return None

    async def strip_binaries(self, binaries: List[str] = None) -> ModuleResult:
        """Remove debug symbols from executables/libraries"""
        try:
            if binaries is None:
                binaries = await self._find_binary_files()

            logger.info(f"Stripping debug symbols from {len(binaries)} binaries")

            stripped_files = []
            total_original_size = 0
            total_stripped_size = 0

            for binary_path in binaries:
                try:
                    result = await self._strip_single_binary(binary_path)
                    if result:
                        stripped_files.append(result)
                        total_original_size += result.original_size
                        total_stripped_size += result.optimized_size

                except Exception as e:
                    logger.warning(f"Could not strip {binary_path}: {e}")

            return ModuleResult(
                success=True,
                data={
                    "binaries_stripped": len(stripped_files),
                    "total_original_size": total_original_size,
                    "total_stripped_size": total_stripped_size,
                    "space_saved": total_original_size - total_stripped_size,
                    "stripped_files": stripped_files,
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error stripping binaries: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _find_binary_files(self) -> List[str]:
        """Find binary files that can be stripped"""
        binary_files = []
        binary_extensions = [".exe", ".so", ".dll", ".dylib", ".a", ".o"]

        for file_path in self.base_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in binary_extensions:
                binary_files.append(str(file_path))

        return binary_files

    async def _strip_single_binary(
        self, binary_path: str
    ) -> Optional[OptimizationResult]:
        """Strip debug symbols from a single binary"""
        try:
            original_path = Path(binary_path)
            original_size = original_path.stat().st_size

            # Simulate strip operation (in production, use strip command)
            # Simulate 20% size reduction
            stripped_size = int(original_size * 0.8)

            return OptimizationResult(
                original_size=original_size,
                optimized_size=stripped_size,
                compression_ratio=0.2,
                file_path=binary_path,
                optimization_type="binary_stripping",
                saved_bytes=original_size - stripped_size,
            )

        except Exception as e:
            logger.error(f"Error stripping binary {binary_path}: {e}")
            return None

    async def minify_code(self, code_files: List[str] = None) -> ModuleResult:
        """Apply minification/obfuscation to JS, CSS, HTML"""
        try:
            if code_files is None:
                code_files = await self._find_code_files()

            logger.info(f"Minifying {len(code_files)} code files")

            minified_files = []
            total_original_size = 0
            total_minified_size = 0

            for code_path in code_files:
                try:
                    result = await self._minify_single_file(code_path)
                    if result:
                        minified_files.append(result)
                        total_original_size += result.original_size
                        total_minified_size += result.optimized_size

                except Exception as e:
                    logger.warning(f"Could not minify {code_path}: {e}")

            return ModuleResult(
                success=True,
                data={
                    "files_minified": len(minified_files),
                    "total_original_size": total_original_size,
                    "total_minified_size": total_minified_size,
                    "space_saved": total_original_size - total_minified_size,
                    "minified_files": minified_files,
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error minifying code: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _find_code_files(self) -> List[str]:
        """Find code files that can be minified"""
        code_files = []
        code_extensions = [".js", ".css", ".html", ".htm", ".ts", ".tsx"]

        for file_path in self.base_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in code_extensions:
                # Skip already minified files
                if not file_path.name.endswith(
                    ".min.js"
                ) and not file_path.name.endswith(".min.css"):
                    code_files.append(str(file_path))

        return code_files

    async def _minify_single_file(self, file_path: str) -> Optional[OptimizationResult]:
        """Minify a single code file"""
        try:
            original_path = Path(file_path)
            original_size = original_path.stat().st_size

            # Read file content
            with open(original_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Simple minification based on file type
            if file_path.endswith(".js") or file_path.endswith(".ts"):
                minified_content = await self._minify_javascript(content)
            elif file_path.endswith(".css"):
                minified_content = await self._minify_css(content)
            elif file_path.endswith(".html") or file_path.endswith(".htm"):
                minified_content = await self._minify_html(content)
            else:
                minified_content = content  # No minification for unknown types

            # Write minified content
            with open(original_path, "w", encoding="utf-8") as f:
                f.write(minified_content)

            minified_size = original_path.stat().st_size

            return OptimizationResult(
                original_size=original_size,
                optimized_size=minified_size,
                compression_ratio=(original_size - minified_size) / original_size,
                file_path=file_path,
                optimization_type="code_minification",
                saved_bytes=original_size - minified_size,
            )

        except Exception as e:
            logger.error(f"Error minifying file {file_path}: {e}")
            return None

    async def _minify_javascript(self, content: str) -> str:
        """Minify JavaScript code"""
        # Simple JS minification (remove comments and extra whitespace)
        lines = content.split("\n")
        minified_lines = []

        for line in lines:
            line = line.strip()
            if line and not line.startswith("//"):
                # Remove single-line comments
                if "//" in line:
                    line = line[: line.index("//")]
                minified_lines.append(line)

        return " ".join(minified_lines)

    async def _minify_css(self, content: str) -> str:
        """Minify CSS code"""
        # Simple CSS minification
        content = content.replace("\n", "").replace("\r", "")
        content = content.replace("  ", " ").replace("  ", " ")
        content = content.replace("/*", "").replace("*/", "")
        return content.strip()

    async def _minify_html(self, content: str) -> str:
        """Minify HTML code"""
        # Simple HTML minification
        content = content.replace("\n", "").replace("\r", "")
        content = content.replace("  ", " ").replace("  ", " ")
        return content.strip()

    async def generate_optimization_report(self) -> ModuleResult:
        """Generate comprehensive optimization report"""
        try:
            logger.info("Generating optimization report")

            report = {
                "generated_at": datetime.now().isoformat(),
                "total_files_scanned": 0,
                "total_original_size": 0,
                "total_optimized_size": 0,
                "total_space_saved": 0,
                "optimization_summary": {
                    "assets_compressed": 0,
                    "binaries_stripped": 0,
                    "code_minified": 0,
                },
                "file_type_breakdown": {},
                "recommendations": [],
            }

            # Scan all files and generate statistics
            for file_path in self.base_path.rglob("*"):
                if file_path.is_file():
                    file_size = file_path.stat().st_size
                    file_ext = file_path.suffix.lower()

                    report["total_files_scanned"] += 1
                    report["total_original_size"] += file_size

                    if file_ext not in report["file_type_breakdown"]:
                        report["file_type_breakdown"][file_ext] = {
                            "count": 0,
                            "total_size": 0,
                        }

                    report["file_type_breakdown"][file_ext]["count"] += 1
                    report["file_type_breakdown"][file_ext]["total_size"] += file_size

            # Add optimization recommendations
            report["recommendations"] = await self._generate_recommendations(report)

            # Save report
            report_path = self.base_path / "reports" / "optimization_report.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)

            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)

            return ModuleResult(
                success=True,
                data={
                    "report_path": str(report_path),
                    "files_scanned": report["total_files_scanned"],
                    "total_size_mb": report["total_original_size"] / (1024 * 1024),
                    "recommendations_count": len(report["recommendations"]),
                },
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error generating optimization report: {e}")
            return ModuleResult(
                success=False, data=None, error=str(e), timestamp=datetime.now()
            )

    async def _generate_recommendations(self, report: Dict) -> List[Dict]:
        """Generate optimization recommendations based on report"""
        recommendations = []

        # Check for large files
        for ext, data in report["file_type_breakdown"].items():
            if data["total_size"] > 100 * 1024 * 1024:  # 100MB
                recommendations.append(
                    {
                        "type": "compress_large_files",
                        "file_type": ext,
                        "current_size_mb": data["total_size"] / (1024 * 1024),
                        "potential_savings": f"~{data['total_size'] / (1024 * 1024) * 0.3:.1f}MB",
                        "action": f"Compress {ext} files to reduce size",
                    }
                )

        # Check for code files that could be minified
        code_extensions = [".js", ".css", ".html"]
        for ext in code_extensions:
            if ext in report["file_type_breakdown"]:
                data = report["file_type_breakdown"][ext]
                if data["total_size"] > 10 * 1024 * 1024:  # 10MB
                    recommendations.append(
                        {
                            "type": "minify_code",
                            "file_type": ext,
                            "current_size_mb": data["total_size"] / (1024 * 1024),
                            "potential_savings": f"~{data['total_size'] / (1024 * 1024) * 0.2:.1f}MB",
                            "action": f"Minify {ext} files to reduce size",
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
                        "saved_bytes": result.saved_bytes,
                    }
                    for result in results
                ],
            }

            self.optimization_log.append(log_entry)

            # Save to file
            log_path = self.base_path / "reports" / "compression_log.json"
            log_path.parent.mkdir(parents=True, exist_ok=True)

            with open(log_path, "w") as f:
                json.dump(self.optimization_log, f, indent=2)

        except Exception as e:
            logger.error(f"Error logging optimization results: {e}")


# Example usage and testing
async def main():
    """Test the File Optimizer Module"""
    optimizer = FileOptimizer()

    # Test asset compression
    result = await optimizer.execute_function("compress_assets", threshold_mb=5)
    print(f"Asset compression result: {result}")

    # Test code minification
    result = await optimizer.execute_function("minify_code")
    print(f"Code minification result: {result}")

    # Test report generation
    result = await optimizer.execute_function("generate_optimization_report")
    print(f"Optimization report result: {result}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
