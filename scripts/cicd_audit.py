#!/usr/bin/env python3
"""
NEXUS Platform - CI/CD Pipeline Audit
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import yaml

logger = logging.getLogger(__name__)


class CICDAuditor:
    def __init__(self, workflows_dir: str = ".github/workflows/"):
        self.workflows_dir = Path(workflows_dir)
        self.audit_results = {}

    def audit_pipelines(self) -> Dict[str, Any]:
        """Audit all CI/CD pipelines"""
        results = {
            "total_workflows": 0,
            "workflows": [],
            "recommendations": [],
            "security_issues": [],
            "performance_issues": [],
        }

        for workflow_file in self.workflows_dir.glob("*.yml"):
            if workflow_file.name.endswith(".yml"):
                workflow_audit = self.audit_workflow(workflow_file)
                results["workflows"].append(workflow_audit)
                results["total_workflows"] += 1

        # Generate overall recommendations
        results["recommendations"] = self.generate_recommendations(results["workflows"])

        return results

    def audit_workflow(self, workflow_path: Path) -> Dict[str, Any]:
        """Audit a single workflow file"""
        try:
            with open(workflow_path, "r") as f:
                workflow = yaml.safe_load(f)

            audit = {
                "file": str(workflow_path),
                "name": workflow.get("name", "Unknown"),
                "jobs": len(workflow.get("jobs", {})),
                "issues": [],
                "security_score": 0,
                "performance_score": 0,
            }

            # Check for security issues
            security_issues = self.check_security(workflow)
            audit["issues"].extend(security_issues)
            audit["security_score"] = max(0, 100 - len(security_issues) * 10)

            # Check for performance issues
            performance_issues = self.check_performance(workflow)
            audit["issues"].extend(performance_issues)
            audit["performance_score"] = max(0, 100 - len(performance_issues) * 10)

            return audit

        except Exception as e:
            return {"file": str(workflow_path), "error": str(e)}

    def check_security(self, workflow: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for security issues"""
        issues = []

        jobs = workflow.get("jobs", {})

        for job_name, job_config in jobs.items():
            steps = job_config.get("steps", [])

            for step in steps:
                # Check for hardcoded secrets
                if "run" in step:
                    run_content = step["run"]
                    if any(
                        secret in run_content.lower()
                        for secret in ["password", "secret", "token", "key"]
                    ):
                        issues.append(
                            {
                                "type": "hardcoded_secret",
                                "job": job_name,
                                "step": step.get("name", "Unknown"),
                                "severity": "high",
                                "description": "Potential hardcoded secret in step",
                            }
                        )

                # Check for insecure actions
                if "uses" in step:
                    action = step["uses"]
                    if not action.startswith(
                        ("actions/", "docker/", "azure/", "aws-actions/")
                    ):
                        issues.append(
                            {
                                "type": "insecure_action",
                                "job": job_name,
                                "step": step.get("name", "Unknown"),
                                "severity": "medium",
                                "description": f"Using potentially insecure action: {action}",
                            }
                        )

        return issues

    def check_performance(self, workflow: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for performance issues"""
        issues = []

        jobs = workflow.get("jobs", {})

        for job_name, job_config in jobs.items():
            # Check for missing caching
            steps = job_config.get("steps", [])
            has_cache = any("cache" in step.get("uses", "") for step in steps)

            if not has_cache and any("npm" in step.get("run", "") for step in steps):
                issues.append(
                    {
                        "type": "missing_cache",
                        "job": job_name,
                        "severity": "medium",
                        "description": "Consider adding npm cache for better performance",
                    }
                )

            # Check for parallel jobs
            if len(jobs) > 1:
                dependencies = job_config.get("needs", [])
                if not dependencies:
                    issues.append(
                        {
                            "type": "sequential_jobs",
                            "job": job_name,
                            "severity": "low",
                            "description": "Consider running independent jobs in parallel",
                        }
                    )

        return issues

    def generate_recommendations(
        self, workflows: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate overall recommendations"""
        recommendations = []

        # Check for common patterns
        total_workflows = len(workflows)
        workflows_with_secrets = len(
            [
                w
                for w in workflows
                if any(
                    issue["type"] == "hardcoded_secret" for issue in w.get("issues", [])
                )
            ]
        )

        if workflows_with_secrets > 0:
            recommendations.append(
                {
                    "type": "security",
                    "priority": "high",
                    "description": f"{workflows_with_secrets}/{total_workflows} workflows have potential security issues",
                }
            )

        # Check for caching
        workflows_with_cache = len([w for w in workflows if any("cache" in str(w))])
        if workflows_with_cache < total_workflows * 0.5:
            recommendations.append(
                {
                    "type": "performance",
                    "priority": "medium",
                    "description": "Consider adding caching to more workflows for better performance",
                }
            )

        return recommendations


if __name__ == "__main__":
    auditor = CICDAuditor()
    results = auditor.audit_pipelines()
    print(json.dumps(results, indent=2))
