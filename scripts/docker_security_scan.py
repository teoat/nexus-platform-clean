#!/usr/bin/env python3
"""
NEXUS Platform - Docker Security Scanning
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class DockerSecurityScanner:
    def __init__(self):
        self.scan_results = {}

    def scan_image(self, image_name: str) -> Dict[str, Any]:
        """Scan Docker image for vulnerabilities"""
        try:
            # Run Trivy scan
            cmd = [
                "trivy",
                "image",
                "--format",
                "json",
                "--severity",
                "HIGH,CRITICAL",
                image_name,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                vulnerabilities = json.loads(result.stdout)
                return {
                    "image": image_name,
                    "status": "success",
                    "vulnerabilities": vulnerabilities,
                    "critical_count": len(
                        [
                            v
                            for v in vulnerabilities.get("Results", [])
                            if v.get("Severity") == "CRITICAL"
                        ]
                    ),
                    "high_count": len(
                        [
                            v
                            for v in vulnerabilities.get("Results", [])
                            if v.get("Severity") == "HIGH"
                        ]
                    ),
                }
            else:
                return {"image": image_name, "status": "error", "error": result.stderr}
        except Exception as e:
            return {"image": image_name, "status": "error", "error": str(e)}

    def scan_all_images(self) -> Dict[str, Any]:
        """Scan all project images"""
        images = [
            "nexus/backend:latest",
            "nexus/frontend:latest",
            "nexus/frenly-ai:latest",
        ]

        results = {}
        for image in images:
            results[image] = self.scan_image(image)

        return results


if __name__ == "__main__":
    scanner = DockerSecurityScanner()
    results = scanner.scan_all_images()
    print(json.dumps(results, indent=2))
