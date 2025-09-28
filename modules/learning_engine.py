"""
Learning Engine for Frenly AI Meta Module

This module implements the learning capabilities that analyze system behavior,
identify patterns, and adapt the system based on learned insights.
"""

import asyncio
import json
import logging
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import yaml

logger = logging.getLogger(__name__)


@dataclass
class LearningPattern:
    """Represents a learned pattern from system behavior"""

    pattern_id: str
    pattern_type: str
    confidence: float
    frequency: int
    first_observed: datetime
    last_observed: datetime
    metadata: Dict[str, Any]
    impact_score: float = 0.0


@dataclass
class LearningInsight:
    """Represents an insight derived from learning"""

    insight_id: str
    insight_type: str
    description: str
    confidence: float
    evidence: List[str]
    recommendations: List[str]
    created_at: datetime


class LearningEngine:
    """
    Learning Engine for Frenly AI Meta Module

    Analyzes system behavior, identifies patterns, and generates insights
    for adaptive system optimization.
    """

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.learning_data_path = self.base_path / "frenly_ai_meta" / "learning_data"
        self.patterns_path = self.base_path / "learning_patterns"
        self.insights_path = self.base_path / "learning_insights"

        # Create directories
        self.learning_data_path.mkdir(parents=True, exist_ok=True)
        self.patterns_path.mkdir(parents=True, exist_ok=True)
        self.insights_path.mkdir(parents=True, exist_ok=True)

        # Learning state
        self.learned_patterns: List[LearningPattern] = []
        self.insights: List[LearningInsight] = []
        self.behavior_history: List[Dict[str, Any]] = []

        # Learning configuration
        self.config = self._load_learning_config()

        # Load existing data
        self._load_learning_data()

    def _load_learning_config(self) -> Dict[str, Any]:
        """Load learning configuration"""
        config_path = self.base_path / "config" / "frenly_ai_meta.yaml"

        if config_path.exists():
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                return config.get("frenly_ai_meta", {}).get("learning", {})

        return {
            "enabled": True,
            "analysis_interval": "daily",
            "learning_rate": 0.1,
            "memory_retention_days": 90,
            "min_data_points": 100,
            "confidence_threshold": 0.8,
        }

    async def analyze_behavior_patterns(
        self, audit_logs: List[Dict[str, Any]]
    ) -> List[LearningPattern]:
        """Analyze audit logs to identify behavior patterns"""
        logger.info("Analyzing behavior patterns...")

        patterns = []

        # Analyze action frequency patterns
        action_patterns = self._analyze_action_frequency(audit_logs)
        patterns.extend(action_patterns)

        # Analyze temporal patterns
        temporal_patterns = self._analyze_temporal_patterns(audit_logs)
        patterns.extend(temporal_patterns)

        # Analyze success/failure patterns
        success_patterns = self._analyze_success_patterns(audit_logs)
        patterns.extend(success_patterns)

        # Analyze resource usage patterns
        resource_patterns = self._analyze_resource_patterns(audit_logs)
        patterns.extend(resource_patterns)

        # Update learned patterns
        for pattern in patterns:
            self._update_or_add_pattern(pattern)

        # Save patterns
        await self._save_patterns()

        return patterns

    def _analyze_action_frequency(
        self, audit_logs: List[Dict[str, Any]]
    ) -> List[LearningPattern]:
        """Analyze action frequency patterns"""
        patterns = []

        # Count action frequencies
        action_counts = Counter(log.get("action", "unknown") for log in audit_logs)
        total_actions = len(audit_logs)

        for action, count in action_counts.items():
            frequency = count / total_actions if total_actions > 0 else 0

            if frequency > 0.1:  # More than 10% of actions
                pattern = LearningPattern(
                    pattern_id=f"action_frequency_{action}",
                    pattern_type="action_frequency",
                    confidence=min(frequency * 2, 1.0),  # Scale to 0-1
                    frequency=count,
                    first_observed=datetime.now(),
                    last_observed=datetime.now(),
                    metadata={
                        "action": action,
                        "frequency_percentage": frequency * 100,
                        "total_actions": total_actions,
                    },
                    impact_score=frequency * 0.5,
                )
                patterns.append(pattern)

        return patterns

    def _analyze_temporal_patterns(
        self, audit_logs: List[Dict[str, Any]]
    ) -> List[LearningPattern]:
        """Analyze temporal patterns in system behavior"""
        patterns = []

        # Group logs by hour
        hourly_counts = defaultdict(int)
        for log in audit_logs:
            try:
                timestamp = datetime.fromisoformat(
                    log.get("timestamp", "").replace("Z", "+00:00")
                )
                hour = timestamp.hour
                hourly_counts[hour] += 1
            except:
                continue

        if hourly_counts:
            # Find peak hours
            max_count = max(hourly_counts.values())
            peak_hours = [
                hour
                for hour, count in hourly_counts.items()
                if count >= max_count * 0.8
            ]

            if peak_hours:
                pattern = LearningPattern(
                    pattern_id="peak_usage_hours",
                    pattern_type="temporal",
                    confidence=0.8,
                    frequency=len(peak_hours),
                    first_observed=datetime.now(),
                    last_observed=datetime.now(),
                    metadata={
                        "peak_hours": peak_hours,
                        "hourly_distribution": dict(hourly_counts),
                    },
                    impact_score=0.7,
                )
                patterns.append(pattern)

        return patterns

    def _analyze_success_patterns(
        self, audit_logs: List[Dict[str, Any]]
    ) -> List[LearningPattern]:
        """Analyze success/failure patterns"""
        patterns = []

        # Count success/failure by action
        action_success = defaultdict(lambda: {"success": 0, "failure": 0})

        for log in audit_logs:
            action = log.get("action", "unknown")
            status = log.get("status", "unknown")

            if status == "success":
                action_success[action]["success"] += 1
            elif status == "failure":
                action_success[action]["failure"] += 1

        # Identify problematic actions
        for action, counts in action_success.items():
            total = counts["success"] + counts["failure"]
            if total > 0:
                success_rate = counts["success"] / total

                if success_rate < 0.8:  # Less than 80% success rate
                    pattern = LearningPattern(
                        pattern_id=f"low_success_{action}",
                        pattern_type="success_rate",
                        confidence=1.0
                        - success_rate,  # Higher confidence for lower success rate
                        frequency=total,
                        first_observed=datetime.now(),
                        last_observed=datetime.now(),
                        metadata={
                            "action": action,
                            "success_rate": success_rate,
                            "success_count": counts["success"],
                            "failure_count": counts["failure"],
                        },
                        impact_score=1.0 - success_rate,
                    )
                    patterns.append(pattern)

        return patterns

    def _analyze_resource_patterns(
        self, audit_logs: List[Dict[str, Any]]
    ) -> List[LearningPattern]:
        """Analyze resource usage patterns"""
        patterns = []

        # Analyze execution times
        execution_times = []
        for log in audit_logs:
            if "execution_time" in log:
                try:
                    execution_times.append(float(log["execution_time"]))
                except:
                    continue

        if execution_times:
            avg_time = np.mean(execution_times)
            std_time = np.std(execution_times)

            # Identify slow operations
            if avg_time > 5.0:  # More than 5 seconds average
                pattern = LearningPattern(
                    pattern_id="slow_operations",
                    pattern_type="performance",
                    confidence=min(avg_time / 10.0, 1.0),  # Scale to 0-1
                    frequency=len(execution_times),
                    first_observed=datetime.now(),
                    last_observed=datetime.now(),
                    metadata={
                        "average_execution_time": avg_time,
                        "std_execution_time": std_time,
                        "sample_count": len(execution_times),
                    },
                    impact_score=min(avg_time / 10.0, 1.0),
                )
                patterns.append(pattern)

        return patterns

    def _update_or_add_pattern(self, new_pattern: LearningPattern):
        """Update existing pattern or add new one"""
        for i, existing_pattern in enumerate(self.learned_patterns):
            if existing_pattern.pattern_id == new_pattern.pattern_id:
                # Update existing pattern
                existing_pattern.confidence = max(
                    existing_pattern.confidence, new_pattern.confidence
                )
                existing_pattern.frequency += new_pattern.frequency
                existing_pattern.last_observed = new_pattern.last_observed
                existing_pattern.impact_score = max(
                    existing_pattern.impact_score, new_pattern.impact_score
                )
                return

        # Add new pattern
        self.learned_patterns.append(new_pattern)

    async def generate_insights(self) -> List[LearningInsight]:
        """Generate insights from learned patterns"""
        logger.info("Generating learning insights...")

        insights = []

        # Generate performance insights
        performance_insights = self._generate_performance_insights()
        insights.extend(performance_insights)

        # Generate optimization insights
        optimization_insights = self._generate_optimization_insights()
        insights.extend(optimization_insights)

        # Generate workflow insights
        workflow_insights = self._generate_workflow_insights()
        insights.extend(workflow_insights)

        # Update insights
        self.insights.extend(insights)

        # Save insights
        await self._save_insights()

        return insights

    def _generate_performance_insights(self) -> List[LearningInsight]:
        """Generate performance-related insights"""
        insights = []

        # Find slow operation patterns
        slow_patterns = [
            p for p in self.learned_patterns if p.pattern_type == "performance"
        ]

        if slow_patterns:
            insight = LearningInsight(
                insight_id="performance_optimization",
                insight_type="performance",
                description="System performance can be improved by optimizing slow operations",
                confidence=0.8,
                evidence=[f"Pattern: {p.pattern_id}" for p in slow_patterns],
                recommendations=[
                    "Consider optimizing slow operations",
                    "Review execution time thresholds",
                    "Implement caching for frequently used operations",
                ],
                created_at=datetime.now(),
            )
            insights.append(insight)

        return insights

    def _generate_optimization_insights(self) -> List[LearningInsight]:
        """Generate optimization-related insights"""
        insights = []

        # Find high-frequency action patterns
        freq_patterns = [
            p
            for p in self.learned_patterns
            if p.pattern_type == "action_frequency" and p.frequency > 50
        ]

        if freq_patterns:
            insight = LearningInsight(
                insight_id="frequent_actions",
                insight_type="optimization",
                description="Some actions are performed very frequently and could benefit from optimization",
                confidence=0.7,
                evidence=[
                    f"Action: {p.metadata.get('action', 'unknown')} - {p.frequency} times"
                    for p in freq_patterns
                ],
                recommendations=[
                    "Consider batching frequent actions",
                    "Implement caching for repeated operations",
                    "Optimize the most common workflows",
                ],
                created_at=datetime.now(),
            )
            insights.append(insight)

        return insights

    def _generate_workflow_insights(self) -> List[LearningInsight]:
        """Generate workflow-related insights"""
        insights = []

        # Find low success rate patterns
        failure_patterns = [
            p
            for p in self.learned_patterns
            if p.pattern_type == "success_rate" and p.confidence > 0.3
        ]

        if failure_patterns:
            insight = LearningInsight(
                insight_id="workflow_reliability",
                insight_type="workflow",
                description="Some workflows have low success rates and need attention",
                confidence=0.9,
                evidence=[
                    f"Action: {p.metadata.get('action', 'unknown')} - {p.metadata.get('success_rate', 0):.1%} success rate"
                    for p in failure_patterns
                ],
                recommendations=[
                    "Investigate and fix failing workflows",
                    "Add better error handling",
                    "Implement retry mechanisms for critical operations",
                ],
                created_at=datetime.now(),
            )
            insights.append(insight)

        return insights

    async def adapt_parameters(self, current_config: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt system parameters based on learned patterns"""
        logger.info("Adapting parameters based on learned patterns...")

        adapted_config = current_config.copy()

        # Adapt based on performance patterns
        performance_patterns = [
            p for p in self.learned_patterns if p.pattern_type == "performance"
        ]
        if performance_patterns:
            # Increase timeouts for slow operations
            if "timeouts" in adapted_config:
                adapted_config["timeouts"]["default"] = max(
                    adapted_config["timeouts"].get("default", 30),
                    60,  # Increase to 60 seconds
                )

        # Adapt based on frequency patterns
        freq_patterns = [
            p for p in self.learned_patterns if p.pattern_type == "action_frequency"
        ]
        if freq_patterns:
            # Adjust batch sizes for frequent operations
            if "batch_processing" in adapted_config:
                adapted_config["batch_processing"]["batch_size"] = min(
                    adapted_config["batch_processing"].get("batch_size", 10),
                    50,  # Increase batch size
                )

        # Adapt based on temporal patterns
        temporal_patterns = [
            p for p in self.learned_patterns if p.pattern_type == "temporal"
        ]
        if temporal_patterns:
            # Adjust scheduling based on peak hours
            peak_hours = temporal_patterns[0].metadata.get("peak_hours", [])
            if peak_hours:
                adapted_config["scheduling"] = {
                    "peak_hours": peak_hours,
                    "off_peak_optimization": True,
                }

        return adapted_config

    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of learning state"""
        return {
            "patterns_learned": len(self.learned_patterns),
            "insights_generated": len(self.insights),
            "learning_enabled": self.config.get("enabled", True),
            "confidence_threshold": self.config.get("confidence_threshold", 0.8),
            "recent_patterns": [
                {
                    "id": p.pattern_id,
                    "type": p.pattern_type,
                    "confidence": p.confidence,
                    "impact": p.impact_score,
                }
                for p in self.learned_patterns[-5:]  # Last 5 patterns
            ],
            "recent_insights": [
                {
                    "id": i.insight_id,
                    "type": i.insight_type,
                    "confidence": i.confidence,
                    "description": i.description,
                }
                for i in self.insights[-3:]  # Last 3 insights
            ],
        }

    async def _save_patterns(self):
        """Save learned patterns to disk"""
        patterns_data = []
        for pattern in self.learned_patterns:
            patterns_data.append(
                {
                    "pattern_id": pattern.pattern_id,
                    "pattern_type": pattern.pattern_type,
                    "confidence": pattern.confidence,
                    "frequency": pattern.frequency,
                    "first_observed": pattern.first_observed.isoformat(),
                    "last_observed": pattern.last_observed.isoformat(),
                    "metadata": pattern.metadata,
                    "impact_score": pattern.impact_score,
                }
            )

        with open(self.patterns_path / "patterns.json", "w") as f:
            json.dump(patterns_data, f, indent=2)

    async def _save_insights(self):
        """Save insights to disk"""
        insights_data = []
        for insight in self.insights:
            insights_data.append(
                {
                    "insight_id": insight.insight_id,
                    "insight_type": insight.insight_type,
                    "description": insight.description,
                    "confidence": insight.confidence,
                    "evidence": insight.evidence,
                    "recommendations": insight.recommendations,
                    "created_at": insight.created_at.isoformat(),
                }
            )

        with open(self.insights_path / "insights.json", "w") as f:
            json.dump(insights_data, f, indent=2)

    def _load_learning_data(self):
        """Load existing learning data"""
        # Load patterns
        patterns_file = self.patterns_path / "patterns.json"
        if patterns_file.exists():
            try:
                with open(patterns_file, "r") as f:
                    patterns_data = json.load(f)
                    for p_data in patterns_data:
                        pattern = LearningPattern(
                            pattern_id=p_data.get("pattern_id", "unknown"),
                            pattern_type=p_data.get("pattern_type", "unknown"),
                            confidence=p_data.get("confidence", 0.0),
                            frequency=p_data.get("frequency", 0),
                            first_observed=datetime.fromisoformat(
                                p_data.get("first_observed", datetime.now().isoformat())
                            ),
                            last_observed=datetime.fromisoformat(
                                p_data.get("last_observed", datetime.now().isoformat())
                            ),
                            metadata=p_data.get("metadata", {}),
                            impact_score=p_data.get("impact_score", 0.0),
                        )
                        self.learned_patterns.append(pattern)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning(f"Failed to load patterns data: {e}")
                self.learned_patterns = []

        # Load insights
        insights_file = self.insights_path / "insights.json"
        if insights_file.exists():
            try:
                with open(insights_file, "r") as f:
                    insights_data = json.load(f)
                    for i_data in insights_data:
                        insight = LearningInsight(
                            insight_id=i_data.get("insight_id", "unknown"),
                            insight_type=i_data.get("insight_type", "unknown"),
                            description=i_data.get("description", "N/A"),
                            confidence=i_data.get("confidence", 0.0),
                            evidence=i_data.get("evidence", []),
                            recommendations=i_data.get("recommendations", []),
                            created_at=datetime.fromisoformat(
                                i_data.get("created_at", datetime.now().isoformat())
                            ),
                        )
                        self.insights.append(insight)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning(f"Failed to load insights data: {e}")
                self.insights = []
