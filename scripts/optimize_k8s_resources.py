#!/usr/bin/env python3
"""
NEXUS Platform - Kubernetes Resource Optimization
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import yaml

logger = logging.getLogger(__name__)


class K8sResourceOptimizer:
    def __init__(self, manifests_dir: str = "k8s/"):
        self.manifests_dir = Path(manifests_dir)
        self.optimizations = []

    def optimize_manifests(self) -> Dict[str, Any]:
        """Optimize all Kubernetes manifests"""
        results = {
            "optimized_manifests": [],
            "recommendations": [],
            "resource_usage": {},
        }

        for manifest_file in self.manifests_dir.glob("*.yaml"):
            if manifest_file.name.endswith(".yaml"):
                optimized = self.optimize_manifest(manifest_file)
                results["optimized_manifests"].append(optimized)

        return results

    def optimize_manifest(self, manifest_path: Path) -> Dict[str, Any]:
        """Optimize a single manifest file"""
        try:
            with open(manifest_path, "r") as f:
                manifest = yaml.safe_load(f)

            optimizations = []

            if manifest.get("kind") == "Deployment":
                optimizations.extend(self.optimize_deployment(manifest))
            elif manifest.get("kind") == "Service":
                optimizations.extend(self.optimize_service(manifest))
            elif manifest.get("kind") == "ConfigMap":
                optimizations.extend(self.optimize_configmap(manifest))

            return {
                "file": str(manifest_path),
                "kind": manifest.get("kind"),
                "optimizations": optimizations,
            }

        except Exception as e:
            return {"file": str(manifest_path), "error": str(e)}

    def optimize_deployment(self, deployment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Optimize deployment resource settings"""
        optimizations = []

        containers = (
            deployment.get("spec", {})
            .get("template", {})
            .get("spec", {})
            .get("containers", [])
        )

        for container in containers:
            resources = container.get("resources", {})

            # Add resource requests if missing
            if "requests" not in resources:
                optimizations.append(
                    {
                        "type": "add_resource_requests",
                        "container": container.get("name"),
                        "recommendation": "Add resource requests for better scheduling",
                    }
                )

            # Add resource limits if missing
            if "limits" not in resources:
                optimizations.append(
                    {
                        "type": "add_resource_limits",
                        "container": container.get("name"),
                        "recommendation": "Add resource limits to prevent resource exhaustion",
                    }
                )

            # Add health checks if missing
            if "livenessProbe" not in container:
                optimizations.append(
                    {
                        "type": "add_liveness_probe",
                        "container": container.get("name"),
                        "recommendation": "Add liveness probe for better health monitoring",
                    }
                )

            if "readinessProbe" not in container:
                optimizations.append(
                    {
                        "type": "add_readiness_probe",
                        "container": container.get("name"),
                        "recommendation": "Add readiness probe for better traffic management",
                    }
                )

        return optimizations

    def optimize_service(self, service: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Optimize service settings"""
        optimizations = []

        # Check for session affinity
        if "sessionAffinity" not in service.get("spec", {}):
            optimizations.append(
                {
                    "type": "add_session_affinity",
                    "recommendation": "Consider adding session affinity for stateful applications",
                }
            )

        return optimizations

    def optimize_configmap(self, configmap: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Optimize ConfigMap settings"""
        optimizations = []

        # Check for immutable ConfigMaps
        if not configmap.get("spec", {}).get("immutable", False):
            optimizations.append(
                {
                    "type": "make_immutable",
                    "recommendation": "Consider making ConfigMap immutable for better performance",
                }
            )

        return optimizations


if __name__ == "__main__":
    optimizer = K8sResourceOptimizer()
    results = optimizer.optimize_manifests()
    print(json.dumps(results, indent=2))
