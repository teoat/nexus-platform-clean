"""
Recommendation Engine for Frenly AI Meta Module

This module implements intelligent recommendation capabilities that provide
AI-driven suggestions for system optimization, configuration tuning, and
workflow improvements based on analysis and patterns.
"""

import asyncio
import json
import logging
import statistics
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

logger = logging.getLogger(__name__)


@dataclass
class Recommendation:
    """Represents a recommendation from the system"""

    recommendation_id: str
    recommendation_type: str
    title: str
    description: str
    confidence: float
    impact: str  # low, medium, high
    action_required: bool
    priority: int  # 1-10, higher is more urgent
    created_at: datetime
    metadata: Dict[str, Any]
    status: str = "pending"  # pending, applied, dismissed, expired


@dataclass
class RecommendationRule:
    """Represents a rule for generating recommendations"""

    rule_id: str
    rule_type: str
    condition: str
    recommendation_template: str
    priority: int
    enabled: bool
    parameters: Dict[str, Any]


class RecommendationEngine:
    """
    Recommendation Engine for Frenly AI Meta Module

    Generates intelligent recommendations for system optimization,
    configuration tuning, and workflow improvements based on analysis
    and learned patterns.
    """

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.recommendation_data_path = (
            self.base_path / "frenly_ai_meta" / "recommendations"
        )
        self.rules_path = self.base_path / "recommendation_rules"

        # Create directories
        self.recommendation_data_path.mkdir(parents=True, exist_ok=True)
        self.rules_path.mkdir(parents=True, exist_ok=True)

        # Recommendation state
        self.recommendations: List[Recommendation] = []
        self.rules: List[RecommendationRule] = []

        # Configuration
        self.config = self._load_recommendation_config()

        # Load existing data
        self._load_recommendation_data()
        self._load_recommendation_rules()

        # Initialize default rules
        self._initialize_default_rules()

    def _load_recommendation_config(self) -> Dict[str, Any]:
        """Load recommendation configuration"""
        config_path = self.base_path / "config" / "frenly_ai_meta.yaml"

        if config_path.exists():
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                return config.get("frenly_ai_meta", {}).get("recommendations", {})

        return {
            "enabled": True,
            "suggestion_frequency": "weekly",
            "min_confidence": 0.7,
            "max_recommendations": 10,
            "recommendation_types": [
                "optimization",
                "configuration",
                "workflow",
                "best_practices",
            ],
        }

    def _initialize_default_rules(self):
        """Initialize default recommendation rules"""
        if not self.rules:
            default_rules = [
                RecommendationRule(
                    rule_id="high_cpu_usage",
                    rule_type="performance",
                    condition="cpu_usage > 80",
                    recommendation_template="Consider optimizing CPU-intensive operations or scaling resources",
                    priority=8,
                    enabled=True,
                    parameters={"threshold": 80},
                ),
                RecommendationRule(
                    rule_id="low_success_rate",
                    rule_type="reliability",
                    condition="success_rate < 80",
                    recommendation_template="Investigate and fix failing operations to improve success rate",
                    priority=9,
                    enabled=True,
                    parameters={"threshold": 80},
                ),
                RecommendationRule(
                    rule_id="frequent_optimizations",
                    rule_type="efficiency",
                    condition="optimization_frequency > 2",
                    recommendation_template="Consider implementing continuous optimization to reduce manual intervention",
                    priority=6,
                    enabled=True,
                    parameters={"threshold": 2},
                ),
                RecommendationRule(
                    rule_id="large_repository",
                    rule_type="optimization",
                    condition="repository_size > 1000",
                    recommendation_template="Repository size is large, consider implementing aggressive optimization strategies",
                    priority=7,
                    enabled=True,
                    parameters={"threshold": 1000},
                ),
                RecommendationRule(
                    rule_id="slow_operations",
                    rule_type="performance",
                    condition="avg_execution_time > 10",
                    recommendation_template="Operations are running slowly, consider performance optimization",
                    priority=8,
                    enabled=True,
                    parameters={"threshold": 10},
                ),
            ]

            self.rules.extend(default_rules)
            asyncio.create_task(self._save_rules())

    async def generate_optimization_recommendations(
        self, system_analysis: Dict[str, Any]
    ) -> List[Recommendation]:
        """Generate optimization-related recommendations"""
        logger.info("Generating optimization recommendations...")

        recommendations = []

        # Repository size optimization
        if system_analysis.get("repository_size", 0) > 500:  # MB
            rec = Recommendation(
                recommendation_id="repo_size_optimization",
                recommendation_type="optimization",
                title="Repository Size Optimization",
                description=f"Repository size is {system_analysis.get('repository_size', 0):.1f}MB. Consider implementing file compression and cleanup strategies.",
                confidence=0.8,
                impact="medium",
                action_required=True,
                priority=7,
                created_at=datetime.now(),
                metadata={
                    "current_size": system_analysis.get("repository_size", 0),
                    "threshold": 500,
                    "suggested_actions": [
                        "file_compression",
                        "duplicate_removal",
                        "archive_old_files",
                    ],
                },
            )
            recommendations.append(rec)

        # File optimization
        large_files = system_analysis.get("large_files", [])
        if large_files:
            rec = Recommendation(
                recommendation_id="large_file_optimization",
                recommendation_type="optimization",
                title="Large File Optimization",
                description=f"Found {len(large_files)} large files that could benefit from compression or optimization.",
                confidence=0.9,
                impact="high",
                action_required=True,
                priority=8,
                created_at=datetime.now(),
                metadata={
                    "large_files_count": len(large_files),
                    "largest_file": max(large_files, key=lambda x: x.get("size", 0))
                    if large_files
                    else None,
                    "suggested_actions": [
                        "compress_large_files",
                        "convert_formats",
                        "split_files",
                    ],
                },
            )
            recommendations.append(rec)

        # Dependency optimization
        if system_analysis.get("unused_dependencies", 0) > 5:
            rec = Recommendation(
                recommendation_id="dependency_cleanup",
                recommendation_type="optimization",
                title="Dependency Cleanup",
                description=f"Found {system_analysis.get('unused_dependencies', 0)} unused dependencies that can be removed to reduce bundle size.",
                confidence=0.7,
                impact="medium",
                action_required=False,
                priority=5,
                created_at=datetime.now(),
                metadata={
                    "unused_dependencies": system_analysis.get(
                        "unused_dependencies", 0
                    ),
                    "suggested_actions": [
                        "remove_unused_deps",
                        "update_dependencies",
                        "audit_imports",
                    ],
                },
            )
            recommendations.append(rec)

        return recommendations

    async def generate_configuration_recommendations(
        self, system_analysis: Dict[str, Any]
    ) -> List[Recommendation]:
        """Generate configuration-related recommendations"""
        logger.info("Generating configuration recommendations...")

        recommendations = []

        # Performance thresholds
        if system_analysis.get("avg_execution_time", 0) > 5:
            rec = Recommendation(
                recommendation_id="timeout_adjustment",
                recommendation_type="configuration",
                title="Adjust Timeout Settings",
                description=f"Average execution time is {system_analysis.get('avg_execution_time', 0):.1f}s. Consider increasing timeout thresholds.",
                confidence=0.8,
                impact="medium",
                action_required=False,
                priority=6,
                created_at=datetime.now(),
                metadata={
                    "current_avg_time": system_analysis.get("avg_execution_time", 0),
                    "suggested_timeout": system_analysis.get("avg_execution_time", 0)
                    * 2,
                    "suggested_actions": [
                        "increase_timeouts",
                        "optimize_operations",
                        "add_caching",
                    ],
                },
            )
            recommendations.append(rec)

        # Batch processing
        if system_analysis.get("frequent_operations", 0) > 10:
            rec = Recommendation(
                recommendation_id="batch_processing",
                recommendation_type="configuration",
                title="Enable Batch Processing",
                description=f"High frequency of operations ({system_analysis.get('frequent_operations', 0)} per day). Consider enabling batch processing.",
                confidence=0.7,
                impact="medium",
                action_required=False,
                priority=5,
                created_at=datetime.now(),
                metadata={
                    "operation_frequency": system_analysis.get(
                        "frequent_operations", 0
                    ),
                    "suggested_batch_size": 10,
                    "suggested_actions": [
                        "enable_batching",
                        "optimize_scheduling",
                        "reduce_frequency",
                    ],
                },
            )
            recommendations.append(rec)

        # Resource allocation
        if system_analysis.get("cpu_usage", 0) > 70:
            rec = Recommendation(
                recommendation_id="resource_scaling",
                recommendation_type="configuration",
                title="Scale Resources",
                description=f"CPU usage is {system_analysis.get('cpu_usage', 0):.1f}%. Consider scaling up resources or optimizing operations.",
                confidence=0.9,
                impact="high",
                action_required=True,
                priority=9,
                created_at=datetime.now(),
                metadata={
                    "current_cpu": system_analysis.get("cpu_usage", 0),
                    "suggested_actions": [
                        "scale_up",
                        "optimize_code",
                        "add_caching",
                        "load_balancing",
                    ],
                },
            )
            recommendations.append(rec)

        return recommendations

    async def generate_workflow_recommendations(
        self, system_analysis: Dict[str, Any]
    ) -> List[Recommendation]:
        """Generate workflow-related recommendations"""
        logger.info("Generating workflow recommendations...")

        recommendations = []

        # Error handling
        if system_analysis.get("error_rate", 0) > 0.1:  # 10%
            rec = Recommendation(
                recommendation_id="improve_error_handling",
                recommendation_type="workflow",
                title="Improve Error Handling",
                description=f"Error rate is {system_analysis.get('error_rate', 0):.1%}. Consider improving error handling and retry mechanisms.",
                confidence=0.8,
                impact="high",
                action_required=True,
                priority=8,
                created_at=datetime.now(),
                metadata={
                    "current_error_rate": system_analysis.get("error_rate", 0),
                    "suggested_actions": [
                        "add_retry_logic",
                        "improve_logging",
                        "add_circuit_breakers",
                    ],
                },
            )
            recommendations.append(rec)

        # Scheduling optimization
        if system_analysis.get("peak_hours"):
            peak_hours = system_analysis.get("peak_hours", [])
            rec = Recommendation(
                recommendation_id="schedule_optimization",
                recommendation_type="workflow",
                title="Optimize Scheduling",
                description=f"Peak usage detected during hours {peak_hours}. Consider scheduling heavy operations during off-peak hours.",
                confidence=0.7,
                impact="medium",
                action_required=False,
                priority=6,
                created_at=datetime.now(),
                metadata={
                    "peak_hours": peak_hours,
                    "suggested_actions": [
                        "schedule_off_peak",
                        "load_balancing",
                        "resource_scaling",
                    ],
                },
            )
            recommendations.append(rec)

        # Automation opportunities
        if system_analysis.get("manual_operations", 0) > 5:
            rec = Recommendation(
                recommendation_id="increase_automation",
                recommendation_type="workflow",
                title="Increase Automation",
                description=f"High number of manual operations ({system_analysis.get('manual_operations', 0)}). Consider automating repetitive tasks.",
                confidence=0.6,
                impact="medium",
                action_required=False,
                priority=4,
                created_at=datetime.now(),
                metadata={
                    "manual_operations": system_analysis.get("manual_operations", 0),
                    "suggested_actions": [
                        "automate_repetitive_tasks",
                        "create_scripts",
                        "implement_triggers",
                    ],
                },
            )
            recommendations.append(rec)

        return recommendations

    async def generate_best_practice_recommendations(
        self, system_analysis: Dict[str, Any]
    ) -> List[Recommendation]:
        """Generate best practice recommendations"""
        logger.info("Generating best practice recommendations...")

        recommendations = []

        # Monitoring
        if not system_analysis.get("monitoring_enabled", False):
            rec = Recommendation(
                recommendation_id="enable_monitoring",
                recommendation_type="best_practices",
                title="Enable Comprehensive Monitoring",
                description="Consider implementing comprehensive monitoring to track system performance and identify issues early.",
                confidence=0.9,
                impact="high",
                action_required=True,
                priority=8,
                created_at=datetime.now(),
                metadata={
                    "suggested_actions": [
                        "setup_monitoring",
                        "configure_alerts",
                        "create_dashboards",
                    ]
                },
            )
            recommendations.append(rec)

        # Backup strategy
        if not system_analysis.get("backup_enabled", False):
            rec = Recommendation(
                recommendation_id="implement_backup",
                recommendation_type="best_practices",
                title="Implement Backup Strategy",
                description="Implement a comprehensive backup strategy to protect against data loss.",
                confidence=0.8,
                impact="high",
                action_required=True,
                priority=9,
                created_at=datetime.now(),
                metadata={
                    "suggested_actions": [
                        "setup_automated_backups",
                        "test_restore_procedures",
                        "configure_retention",
                    ]
                },
            )
            recommendations.append(rec)

        # Security
        if not system_analysis.get("security_scan_enabled", False):
            rec = Recommendation(
                recommendation_id="security_scanning",
                recommendation_type="best_practices",
                title="Enable Security Scanning",
                description="Implement regular security scanning to identify vulnerabilities and security issues.",
                confidence=0.7,
                impact="high",
                action_required=True,
                priority=7,
                created_at=datetime.now(),
                metadata={
                    "suggested_actions": [
                        "setup_security_scanning",
                        "configure_vulnerability_checks",
                        "implement_security_policies",
                    ]
                },
            )
            recommendations.append(rec)

        return recommendations

    async def apply_recommendation(self, recommendation_id: str) -> bool:
        """Apply a recommendation"""
        recommendation = next(
            (
                r
                for r in self.recommendations
                if r.recommendation_id == recommendation_id
            ),
            None,
        )

        if not recommendation:
            return False

        # Mark as applied
        recommendation.status = "applied"
        recommendation.metadata["applied_at"] = datetime.now().isoformat()

        # Save updated recommendations
        await self._save_recommendations()

        logger.info(f"Applied recommendation: {recommendation.title}")
        return True

    async def dismiss_recommendation(self, recommendation_id: str) -> bool:
        """Dismiss a recommendation"""
        recommendation = next(
            (
                r
                for r in self.recommendations
                if r.recommendation_id == recommendation_id
            ),
            None,
        )

        if not recommendation:
            return False

        # Mark as dismissed
        recommendation.status = "dismissed"
        recommendation.metadata["dismissed_at"] = datetime.now().isoformat()

        # Save updated recommendations
        await self._save_recommendations()

        logger.info(f"Dismissed recommendation: {recommendation.title}")
        return True

    def get_recommendation_summary(self) -> Dict[str, Any]:
        """Get summary of recommendations"""
        active_recommendations = [
            r for r in self.recommendations if r.status == "pending"
        ]

        return {
            "total_recommendations": len(self.recommendations),
            "active_recommendations": len(active_recommendations),
            "applied_recommendations": len(
                [r for r in self.recommendations if r.status == "applied"]
            ),
            "dismissed_recommendations": len(
                [r for r in self.recommendations if r.status == "dismissed"]
            ),
            "high_priority_count": len(
                [r for r in active_recommendations if r.priority >= 8]
            ),
            "recommendations_by_type": {
                rtype: len(
                    [
                        r
                        for r in active_recommendations
                        if r.recommendation_type == rtype
                    ]
                )
                for rtype in set(r.recommendation_type for r in active_recommendations)
            },
            "recommendations_by_impact": {
                impact: len([r for r in active_recommendations if r.impact == impact])
                for impact in set(r.impact for r in active_recommendations)
            },
        }

    async def _save_recommendations(self):
        """Save recommendations to disk"""
        recommendations_data = []
        for recommendation in self.recommendations:
            recommendations_data.append(
                {
                    "recommendation_id": recommendation.recommendation_id,
                    "recommendation_type": recommendation.recommendation_type,
                    "title": recommendation.title,
                    "description": recommendation.description,
                    "confidence": recommendation.confidence,
                    "impact": recommendation.impact,
                    "action_required": recommendation.action_required,
                    "priority": recommendation.priority,
                    "created_at": recommendation.created_at.isoformat(),
                    "metadata": recommendation.metadata,
                    "status": recommendation.status,
                }
            )

        with open(self.recommendation_data_path / "recommendations.json", "w") as f:
            json.dump(recommendations_data, f, indent=2)

    async def _save_rules(self):
        """Save recommendation rules to disk"""
        rules_data = []
        for rule in self.rules:
            rules_data.append(
                {
                    "rule_id": rule.rule_id,
                    "rule_type": rule.rule_type,
                    "condition": rule.condition,
                    "recommendation_template": rule.recommendation_template,
                    "priority": rule.priority,
                    "enabled": rule.enabled,
                    "parameters": rule.parameters,
                }
            )

        with open(self.rules_path / "rules.json", "w") as f:
            json.dump(rules_data, f, indent=2)

    def _load_recommendation_data(self):
        """Load existing recommendation data"""
        recommendations_file = self.recommendation_data_path / "recommendations.json"
        if recommendations_file.exists():
            try:
                with open(recommendations_file, "r") as f:
                    recommendations_data = json.load(f)
                    for r_data in recommendations_data:
                        recommendation = Recommendation(
                            recommendation_id=r_data.get(
                                "recommendation_id", "unknown"
                            ),
                            recommendation_type=r_data.get(
                                "recommendation_type", "unknown"
                            ),
                            title=r_data.get("title", "Unknown"),
                            description=r_data.get("description", "N/A"),
                            confidence=r_data.get("confidence", 0.0),
                            impact=r_data.get("impact", "low"),
                            action_required=r_data.get("action_required", False),
                            priority=r_data.get("priority", 1),
                            created_at=datetime.fromisoformat(
                                r_data.get("created_at", datetime.now().isoformat())
                            ),
                            metadata=r_data.get("metadata", {}),
                            status=r_data.get("status", "pending"),
                        )
                        self.recommendations.append(recommendation)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning(f"Failed to load recommendations data: {e}")
                self.recommendations = []

    def _load_recommendation_rules(self):
        """Load existing recommendation rules"""
        rules_file = self.rules_path / "rules.json"
        if rules_file.exists():
            with open(rules_file, "r") as f:
                rules_data = json.load(f)
                for rule_data in rules_data:
                    rule = RecommendationRule(
                        rule_id=rule_data["rule_id"],
                        rule_type=rule_data["rule_type"],
                        condition=rule_data["condition"],
                        recommendation_template=rule_data["recommendation_template"],
                        priority=rule_data["priority"],
                        enabled=rule_data["enabled"],
                        parameters=rule_data["parameters"],
                    )
                    self.rules.append(rule)
