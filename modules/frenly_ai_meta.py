"""
Frenly AI Meta Module

This module implements Frenly AI as a Meta AI that operates above the Ultimate Frenly AI Orchestration System.
It provides intelligent analysis, learning, prediction, and recommendation capabilities.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .base_module import BaseModule, ModuleResult
from .learning_engine import LearningEngine
from .prediction_engine import PredictionEngine
from .recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)


@dataclass
class LearningPattern:
    """Represents a learned pattern from system behavior"""

    pattern_type: str
    confidence: float
    frequency: int
    last_observed: datetime
    metadata: Dict[str, Any]


@dataclass
class Prediction:
    """Represents a prediction made by the Meta AI"""

    prediction_type: str
    value: Any
    confidence: float
    horizon_days: int
    created_at: datetime


@dataclass
class Recommendation:
    """Represents a recommendation from the Meta AI"""

    recommendation_type: str
    title: str
    description: str
    confidence: float
    impact: str  # low, medium, high
    action_required: bool
    metadata: Dict[str, Any]


class FrenlyAIMetaModule(BaseModule):
    """
    Frenly AI Meta Module - Operates above the automation system

    This module provides:
    - System analysis and learning
    - Pattern recognition and prediction
    - Intelligent recommendations
    - Adaptive parameter tuning
    """

    def __init__(self, base_path: str):
        super().__init__(base_path)
        self.learning_data_path = self.base_path / "frenly_ai_meta" / "learning_data"
        self.patterns_path = self.base_path / "frenly_ai_meta" / "patterns"
        self.predictions_path = self.base_path / "frenly_ai_meta" / "predictions"
        self.recommendations_path = (
            self.base_path / "frenly_ai_meta" / "recommendations"
        )

        # Create directories
        self.learning_data_path.mkdir(parents=True, exist_ok=True)
        self.patterns_path.mkdir(parents=True, exist_ok=True)
        self.predictions_path.mkdir(parents=True, exist_ok=True)
        self.recommendations_path.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.config = self._load_meta_config()

        # Initialize engines
        self.learning_engine = LearningEngine(base_path)
        self.prediction_engine = PredictionEngine(base_path)
        self.recommendation_engine = RecommendationEngine(base_path)

        # Initialize learning data
        self.learned_patterns: List[LearningPattern] = []
        self.predictions: List[Prediction] = []
        self.recommendations: List[Recommendation] = []

        # Load existing data
        self._load_learning_data()

    def _load_meta_config(self) -> Dict[str, Any]:
        """Load Meta AI configuration"""
        config_path = self.base_path / "config" / "frenly_ai_meta.yaml"

        if config_path.exists():
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        else:
            # Create default configuration
            default_config = {
                "learning": {
                    "enabled": True,
                    "analysis_interval": "daily",
                    "learning_rate": 0.1,
                    "memory_retention_days": 90,
                },
                "prediction": {
                    "enabled": True,
                    "forecast_horizon_days": 30,
                    "confidence_threshold": 0.8,
                },
                "recommendations": {
                    "enabled": True,
                    "suggestion_frequency": "weekly",
                    "min_confidence": 0.7,
                },
            }

            # Save default configuration
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, "w") as f:
                yaml.dump(default_config, f)

            return default_config

    async def get_available_functions(self) -> List[str]:
        """Return list of available Meta AI functions"""
        return [
            "analyze_system_performance",
            "learn_from_patterns",
            "generate_predictions",
            "generate_recommendations",
            "adapt_system_parameters",
            "get_learning_status",
            "get_pattern_insights",
            "get_prediction_summary",
            "get_recommendation_summary",
            "apply_recommendation",
            "dismiss_recommendation",
            "evaluate_prediction_accuracy",
            "reset_learning_data",
        ]

    async def get_module_info(self) -> ModuleResult:
        """Return Meta AI module information"""
        info = {
            "name": "Frenly AI Meta Module",
            "version": "1.0.0",
            "description": "Meta AI that operates above the automation system",
            "capabilities": [
                "System Analysis & Learning",
                "Pattern Recognition & Prediction",
                "Intelligent Recommendations",
                "Adaptive Parameter Tuning",
            ],
            "status": "operational",
            "patterns_learned": len(self.learned_patterns),
            "predictions_generated": len(self.predictions),
            "recommendations_active": len(self.recommendations),
        }

        return ModuleResult(success=True, data=info, error=None)

    async def analyze_system_performance(self, **kwargs) -> ModuleResult:
        """Analyze underlying system performance and patterns"""
        try:
            logger.info("Analyzing system performance...")

            # Analyze audit logs
            audit_analysis = await self._analyze_audit_logs()

            # Analyze optimization results
            optimization_analysis = await self._analyze_optimization_results()

            # Analyze system metrics
            metrics_analysis = await self._analyze_system_metrics()

            analysis_result = {
                "audit_analysis": audit_analysis,
                "optimization_analysis": optimization_analysis,
                "metrics_analysis": metrics_analysis,
                "analysis_timestamp": datetime.now().isoformat(),
                "patterns_identified": len(audit_analysis.get("patterns", [])),
                "performance_score": self._calculate_performance_score(
                    metrics_analysis
                ),
            }

            # Save analysis results
            await self._save_analysis_results(analysis_result)

            return ModuleResult(success=True, data=analysis_result, error=None)

        except Exception as e:
            logger.error(f"Error analyzing system performance: {e}")
            return ModuleResult(
                success=False,
                data={},
                error=f"Failed to analyze system performance: {str(e)}",
            )

    async def learn_from_patterns(self, **kwargs) -> ModuleResult:
        """Learn from observed patterns and behaviors"""
        try:
            logger.info("Learning from system patterns...")

            # Load recent audit logs
            recent_logs = await self._load_recent_audit_logs(days=30)

            # Use learning engine to analyze patterns
            patterns = await self.learning_engine.analyze_behavior_patterns(recent_logs)

            # Generate insights
            insights = await self.learning_engine.generate_insights()

            learning_result = {
                "patterns_learned": len(patterns),
                "insights_generated": len(insights),
                "total_patterns": len(self.learning_engine.learned_patterns),
                "learning_timestamp": datetime.now().isoformat(),
                "patterns": [self._pattern_to_dict(p) for p in patterns],
                "insights": [self._insight_to_dict(i) for i in insights],
            }

            return ModuleResult(success=True, data=learning_result, error=None)

        except Exception as e:
            logger.error(f"Error learning from patterns: {e}")
            return ModuleResult(
                success=False, data={}, error=f"Failed to learn from patterns: {str(e)}"
            )

    async def generate_predictions(self, **kwargs) -> ModuleResult:
        """Generate AI-driven predictions"""
        try:
            logger.info("Generating predictions...")

            # Load historical data
            recent_logs = await self._load_recent_audit_logs(days=30)

            # Use prediction engine to generate predictions
            growth_pred = (
                await self.prediction_engine.generate_repository_growth_prediction(
                    recent_logs
                )
            )
            optimization_pred = (
                await self.prediction_engine.generate_optimization_needs_prediction(
                    recent_logs
                )
            )
            performance_pred = (
                await self.prediction_engine.generate_performance_trend_prediction(
                    recent_logs
                )
            )
            resource_pred = (
                await self.prediction_engine.generate_resource_requirements_prediction(
                    recent_logs
                )
            )

            predictions = [
                growth_pred,
                optimization_pred,
                performance_pred,
                resource_pred,
            ]

            prediction_result = {
                "predictions_generated": len(predictions),
                "total_predictions": len(self.prediction_engine.predictions),
                "prediction_timestamp": datetime.now().isoformat(),
                "predictions": [self._prediction_to_dict(p) for p in predictions],
            }

            return ModuleResult(success=True, data=prediction_result, error=None)

        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            return ModuleResult(
                success=False,
                data={},
                error=f"Failed to generate predictions: {str(e)}",
            )

    async def generate_recommendations(self, **kwargs) -> ModuleResult:
        """Generate AI-driven recommendations"""
        try:
            logger.info("Generating recommendations...")

            # Get system analysis data
            analysis_data = await self._get_system_analysis_data()

            # Use recommendation engine to generate recommendations
            optimization_recs = (
                await self.recommendation_engine.generate_optimization_recommendations(
                    analysis_data
                )
            )
            config_recs = (
                await self.recommendation_engine.generate_configuration_recommendations(
                    analysis_data
                )
            )
            workflow_recs = (
                await self.recommendation_engine.generate_workflow_recommendations(
                    analysis_data
                )
            )
            best_practice_recs = (
                await self.recommendation_engine.generate_best_practice_recommendations(
                    analysis_data
                )
            )

            recommendations = (
                optimization_recs + config_recs + workflow_recs + best_practice_recs
            )

            recommendation_result = {
                "recommendations_generated": len(recommendations),
                "total_recommendations": len(
                    self.recommendation_engine.recommendations
                ),
                "recommendation_timestamp": datetime.now().isoformat(),
                "recommendations": [
                    self._recommendation_to_dict(r) for r in recommendations
                ],
            }

            return ModuleResult(success=True, data=recommendation_result, error=None)

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ModuleResult(
                success=False,
                data={},
                error=f"Failed to generate recommendations: {str(e)}",
            )

    async def adapt_system_parameters(self, **kwargs) -> ModuleResult:
        """Adapt system parameters based on learned patterns"""
        try:
            logger.info("Adapting system parameters...")

            # Analyze current parameters
            current_params = await self._analyze_current_parameters()

            # Generate parameter adjustments
            adjustments = await self._generate_parameter_adjustments()

            # Apply adjustments (if confidence is high enough)
            applied_adjustments = []
            for adjustment in adjustments:
                if adjustment.get("confidence", 0) >= 0.8:
                    await self._apply_parameter_adjustment(adjustment)
                    applied_adjustments.append(adjustment)

            adaptation_result = {
                "adjustments_generated": len(adjustments),
                "adjustments_applied": len(applied_adjustments),
                "adaptation_timestamp": datetime.now().isoformat(),
                "applied_adjustments": applied_adjustments,
            }

            return ModuleResult(success=True, data=adaptation_result, error=None)

        except Exception as e:
            logger.error(f"Error adapting system parameters: {e}")
            return ModuleResult(
                success=False,
                data={},
                error=f"Failed to adapt system parameters: {str(e)}",
            )

    async def get_learning_status(self, **kwargs) -> ModuleResult:
        """Get current learning status and insights"""
        try:
            # Get status from engines
            learning_summary = self.learning_engine.get_learning_summary()
            prediction_summary = self.prediction_engine.get_prediction_summary()
            recommendation_summary = (
                self.recommendation_engine.get_recommendation_summary()
            )

            status = {
                "patterns_learned": learning_summary.get("patterns_learned", 0),
                "insights_generated": learning_summary.get("insights_generated", 0),
                "predictions_generated": prediction_summary.get("total_predictions", 0),
                "recommendations_active": recommendation_summary.get(
                    "active_recommendations", 0
                ),
                "learning_enabled": self.config.get("learning", {}).get(
                    "enabled", True
                ),
                "prediction_enabled": self.config.get("prediction", {}).get(
                    "enabled", True
                ),
                "recommendation_enabled": self.config.get("recommendations", {}).get(
                    "enabled", True
                ),
                "learning_confidence": learning_summary.get("learning_confidence", 0.0),
                "prediction_accuracy": prediction_summary.get("average_accuracy", 0.0),
                "recommendation_impact": recommendation_summary.get(
                    "high_priority_count", 0
                ),
            }

            return ModuleResult(success=True, data=status, error=None)

        except Exception as e:
            logger.error(f"Error getting learning status: {e}")
            return ModuleResult(
                success=False, data={}, error=f"Failed to get learning status: {str(e)}"
            )

    # Helper methods for analysis and learning

    async def _analyze_audit_logs(self) -> Dict[str, Any]:
        """Analyze audit logs for patterns"""
        audit_logs = await self._load_recent_audit_logs(days=7)

        patterns = []
        total_actions = len(audit_logs)
        successful_actions = sum(
            1 for log in audit_logs if log.get("status") == "success"
        )

        # Analyze action frequency
        action_counts = {}
        for log in audit_logs:
            action = log.get("action", "unknown")
            action_counts[action] = action_counts.get(action, 0) + 1

        # Identify common patterns
        for action, count in action_counts.items():
            if count > total_actions * 0.1:  # More than 10% of actions
                patterns.append(
                    {
                        "type": "frequent_action",
                        "action": action,
                        "frequency": count,
                        "percentage": (count / total_actions) * 100,
                    }
                )

        return {
            "total_actions": total_actions,
            "successful_actions": successful_actions,
            "success_rate": (successful_actions / total_actions) * 100
            if total_actions > 0
            else 0,
            "patterns": patterns,
        }

    async def _analyze_optimization_results(self) -> Dict[str, Any]:
        """Analyze optimization results"""
        # This would analyze optimization reports and results
        return {
            "optimization_runs": 0,
            "space_saved": 0,
            "files_processed": 0,
            "efficiency_score": 0.0,
        }

    async def _analyze_system_metrics(self) -> Dict[str, Any]:
        """Analyze system performance metrics"""
        # This would analyze system performance metrics
        return {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0,
            "response_time": 0.0,
        }

    def _calculate_performance_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall performance score"""
        # Simple performance score calculation
        return 0.85  # Placeholder

    async def _load_recent_audit_logs(self, days: int = 30) -> List[Dict[str, Any]]:
        """Load recent audit logs"""
        logs = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            log_file = self.audit_log_path / f"{date.strftime('%Y%m%d')}.jsonl"

            if log_file.exists():
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        for line in f:
                            try:
                                logs.append(json.loads(line.strip()))
                            except json.JSONDecodeError:
                                continue
                except UnicodeDecodeError:
                    # Skip files that can't be decoded (might be compressed)
                    continue

        return logs

    async def _identify_patterns(
        self, logs: List[Dict[str, Any]]
    ) -> List[LearningPattern]:
        """Identify patterns in audit logs"""
        patterns = []

        # Simple pattern identification
        action_times = {}
        for log in logs:
            action = log.get("action", "unknown")
            timestamp = log.get("timestamp", "")

            if action not in action_times:
                action_times[action] = []

            try:
                action_times[action].append(
                    datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                )
            except:
                continue

        # Identify time-based patterns
        for action, times in action_times.items():
            if len(times) > 5:  # Minimum data points
                patterns.append(
                    LearningPattern(
                        pattern_type="time_based",
                        confidence=0.7,
                        frequency=len(times),
                        last_observed=max(times),
                        metadata={
                            "action": action,
                            "times": [t.isoformat() for t in times],
                        },
                    )
                )

        return patterns

    async def _predict_repository_growth(self) -> List[Prediction]:
        """Predict repository growth"""
        predictions = []

        # Simple growth prediction based on patterns
        predictions.append(
            Prediction(
                prediction_type="repository_growth",
                value="15%",
                confidence=0.8,
                horizon_days=30,
                created_at=datetime.now(),
            )
        )

        return predictions

    async def _predict_optimization_needs(self) -> List[Prediction]:
        """Predict optimization needs"""
        predictions = []

        predictions.append(
            Prediction(
                prediction_type="optimization_needs",
                value="file_compression_needed",
                confidence=0.75,
                horizon_days=14,
                created_at=datetime.now(),
            )
        )

        return predictions

    async def _predict_performance_trends(self) -> List[Prediction]:
        """Predict performance trends"""
        predictions = []

        predictions.append(
            Prediction(
                prediction_type="performance_trend",
                value="stable",
                confidence=0.9,
                horizon_days=7,
                created_at=datetime.now(),
            )
        )

        return predictions

    async def _generate_optimization_recommendations(self) -> List[Recommendation]:
        """Generate optimization recommendations"""
        recommendations = []

        recommendations.append(
            Recommendation(
                recommendation_type="optimization",
                title="Enable Asset Compression",
                description="Consider enabling automatic asset compression for files larger than 2MB",
                confidence=0.8,
                impact="medium",
                action_required=True,
                metadata={"threshold": "2MB", "action": "enable_compression"},
            )
        )

        return recommendations

    async def _generate_configuration_recommendations(self) -> List[Recommendation]:
        """Generate configuration recommendations"""
        recommendations = []

        recommendations.append(
            Recommendation(
                recommendation_type="configuration",
                title="Adjust Optimization Thresholds",
                description="Consider lowering file size thresholds based on usage patterns",
                confidence=0.7,
                impact="low",
                action_required=False,
                metadata={"current_threshold": "50MB", "suggested_threshold": "25MB"},
            )
        )

        return recommendations

    async def _generate_workflow_recommendations(self) -> List[Recommendation]:
        """Generate workflow recommendations"""
        recommendations = []

        recommendations.append(
            Recommendation(
                recommendation_type="workflow",
                title="Schedule Daily Cleanup",
                description="Consider scheduling daily cleanup tasks during off-peak hours",
                confidence=0.6,
                impact="low",
                action_required=False,
                metadata={"suggested_time": "02:00", "frequency": "daily"},
            )
        )

        return recommendations

    # Data persistence methods

    async def _save_analysis_results(self, results: Dict[str, Any]):
        """Save analysis results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self.learning_data_path / f"analysis_{timestamp}.json"

        with open(file_path, "w") as f:
            json.dump(results, f, indent=2, default=str)

    async def _save_patterns(self):
        """Save learned patterns"""
        patterns_data = [self._pattern_to_dict(p) for p in self.learned_patterns]

        with open(self.patterns_path / "patterns.json", "w") as f:
            json.dump(patterns_data, f, indent=2, default=str)

    async def _save_predictions(self):
        """Save predictions"""
        predictions_data = [self._prediction_to_dict(p) for p in self.predictions]

        with open(self.predictions_path / "predictions.json", "w") as f:
            json.dump(predictions_data, f, indent=2, default=str)

    async def _save_recommendations(self):
        """Save recommendations"""
        recommendations_data = [
            self._recommendation_to_dict(r) for r in self.recommendations
        ]

        with open(self.recommendations_path / "recommendations.json", "w") as f:
            json.dump(recommendations_data, f, indent=2, default=str)

    def _load_learning_data(self):
        """Load existing learning data"""
        # Load patterns
        patterns_file = self.patterns_path / "patterns.json"
        if patterns_file.exists():
            with open(patterns_file, "r") as f:
                patterns_data = json.load(f)
                self.learned_patterns = [
                    self._dict_to_pattern(p) for p in patterns_data
                ]

        # Load predictions
        predictions_file = self.predictions_path / "predictions.json"
        if predictions_file.exists():
            with open(predictions_file, "r") as f:
                predictions_data = json.load(f)
                self.predictions = [
                    self._dict_to_prediction(p) for p in predictions_data
                ]

        # Load recommendations
        recommendations_file = self.recommendations_path / "recommendations.json"
        if recommendations_file.exists():
            with open(recommendations_file, "r") as f:
                recommendations_data = json.load(f)
                self.recommendations = [
                    self._dict_to_recommendation(r) for r in recommendations_data
                ]

    # Conversion methods

    def _pattern_to_dict(self, pattern: LearningPattern) -> Dict[str, Any]:
        """Convert LearningPattern to dictionary"""
        return {
            "pattern_type": pattern.pattern_type,
            "confidence": pattern.confidence,
            "frequency": pattern.frequency,
            "last_observed": pattern.last_observed.isoformat(),
            "metadata": pattern.metadata,
        }

    def _dict_to_pattern(self, data: Dict[str, Any]) -> LearningPattern:
        """Convert dictionary to LearningPattern"""
        return LearningPattern(
            pattern_type=data["pattern_type"],
            confidence=data["confidence"],
            frequency=data["frequency"],
            last_observed=datetime.fromisoformat(data["last_observed"]),
            metadata=data["metadata"],
        )

    def _prediction_to_dict(self, prediction: Prediction) -> Dict[str, Any]:
        """Convert Prediction to dictionary"""
        return {
            "prediction_type": prediction.prediction_type,
            "value": prediction.value,
            "confidence": prediction.confidence,
            "horizon_days": prediction.horizon_days,
            "created_at": prediction.created_at.isoformat(),
        }

    def _dict_to_prediction(self, data: Dict[str, Any]) -> Prediction:
        """Convert dictionary to Prediction"""
        return Prediction(
            prediction_type=data["prediction_type"],
            value=data["value"],
            confidence=data["confidence"],
            horizon_days=data["horizon_days"],
            created_at=datetime.fromisoformat(data["created_at"]),
        )

    def _recommendation_to_dict(self, recommendation: Recommendation) -> Dict[str, Any]:
        """Convert Recommendation to dictionary"""
        return {
            "recommendation_type": recommendation.recommendation_type,
            "title": recommendation.title,
            "description": recommendation.description,
            "confidence": recommendation.confidence,
            "impact": recommendation.impact,
            "action_required": recommendation.action_required,
            "metadata": recommendation.metadata,
        }

    def _dict_to_recommendation(self, data: Dict[str, Any]) -> Recommendation:
        """Convert dictionary to Recommendation"""
        return Recommendation(
            recommendation_type=data["recommendation_type"],
            title=data["title"],
            description=data["description"],
            confidence=data["confidence"],
            impact=data["impact"],
            action_required=data["action_required"],
            metadata=data["metadata"],
        )

    # Helper methods for system analysis

    async def _get_system_analysis_data(self) -> Dict[str, Any]:
        """Get system analysis data for recommendations"""
        recent_logs = await self._load_recent_audit_logs(days=7)

        # Calculate basic metrics
        total_actions = len(recent_logs)
        successful_actions = sum(
            1 for log in recent_logs if log.get("status") == "success"
        )
        success_rate = successful_actions / total_actions if total_actions > 0 else 0

        # Calculate execution times
        execution_times = [
            float(log.get("execution_time", 0))
            for log in recent_logs
            if "execution_time" in log
        ]
        avg_execution_time = (
            sum(execution_times) / len(execution_times) if execution_times else 0
        )

        # Calculate repository size (placeholder)
        repository_size = 500  # MB - placeholder

        # Calculate large files (placeholder)
        large_files = (
            [{"size": 100, "path": "example.txt"}] if repository_size > 400 else []
        )

        return {
            "repository_size": repository_size,
            "large_files": large_files,
            "unused_dependencies": 3,  # placeholder
            "avg_execution_time": avg_execution_time,
            "success_rate": success_rate,
            "error_rate": 1.0 - success_rate,
            "frequent_operations": total_actions,
            "cpu_usage": 65.0,  # placeholder
            "memory_usage": 70.0,  # placeholder
            "disk_usage": 80.0,  # placeholder
            "peak_hours": [9, 10, 11, 14, 15, 16],  # placeholder
            "manual_operations": 2,  # placeholder
            "monitoring_enabled": True,  # placeholder
            "backup_enabled": False,  # placeholder
            "security_scan_enabled": True,  # placeholder
        }

    def _insight_to_dict(self, insight) -> Dict[str, Any]:
        """Convert LearningInsight to dictionary"""
        return {
            "insight_id": insight.insight_id,
            "insight_type": insight.insight_type,
            "description": insight.description,
            "confidence": insight.confidence,
            "evidence": insight.evidence,
            "recommendations": insight.recommendations,
            "created_at": insight.created_at.isoformat(),
        }

    # Placeholder methods for complex operations

    async def _analyze_current_parameters(self) -> Dict[str, Any]:
        """Analyze current system parameters"""
        try:
            # Load current configuration
            config_path = self.base_path / "config" / "policies.yaml"
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f)
            else:
                config = {}

            # Analyze file size thresholds
            thresholds = config.get("file_size_thresholds", {})

            # Analyze optimization schedules
            schedules = config.get("optimization_schedules", {})

            return {
                "current_thresholds": thresholds,
                "current_schedules": schedules,
                "optimization_enabled": config.get("optimization", {}).get(
                    "enabled", True
                ),
                "compression_enabled": config.get("compression", {}).get(
                    "enabled", True
                ),
                "cleanup_enabled": config.get("cleanup", {}).get("enabled", True),
            }
        except Exception as e:
            logger.error(f"Error analyzing current parameters: {e}")
            return {"current_thresholds": {}, "current_schedules": {}}

    async def _generate_parameter_adjustments(self) -> List[Dict[str, Any]]:
        """Generate parameter adjustments based on learning"""
        try:
            adjustments = []

            # Analyze patterns to suggest threshold adjustments
            if self.learned_patterns:
                # Find patterns related to file sizes
                size_patterns = [
                    p for p in self.learned_patterns if "size" in p.metadata
                ]

                if size_patterns:
                    # Suggest lowering thresholds if many large files are being processed
                    avg_confidence = sum(p.confidence for p in size_patterns) / len(
                        size_patterns
                    )
                    if avg_confidence > 0.7:
                        adjustments.append(
                            {
                                "parameter": "file_size_thresholds.general",
                                "current_value": 52428800,  # 50MB
                                "suggested_value": 26214400,  # 25MB
                                "confidence": avg_confidence,
                                "reason": "High confidence in size patterns suggests lowering thresholds",
                            }
                        )

            # Analyze performance patterns
            performance_patterns = [
                p for p in self.learned_patterns if "performance" in p.pattern_type
            ]
            if performance_patterns:
                avg_perf_confidence = sum(
                    p.confidence for p in performance_patterns
                ) / len(performance_patterns)
                if avg_perf_confidence > 0.8:
                    adjustments.append(
                        {
                            "parameter": "optimization_schedules.frequency",
                            "current_value": "daily",
                            "suggested_value": "hourly",
                            "confidence": avg_perf_confidence,
                            "reason": "Performance patterns suggest more frequent optimization",
                        }
                    )

            return adjustments
        except Exception as e:
            logger.error(f"Error generating parameter adjustments: {e}")
            return []

    async def _apply_parameter_adjustment(self, adjustment: Dict[str, Any]):
        """Apply parameter adjustment"""
        try:
            # Load current configuration
            config_path = self.base_path / "config" / "policies.yaml"
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f)
            else:
                config = {}

            # Apply adjustment
            param_path = adjustment["parameter"].split(".")
            current_config = config
            for key in param_path[:-1]:
                if key not in current_config:
                    current_config[key] = {}
                current_config = current_config[key]

            current_config[param_path[-1]] = adjustment["suggested_value"]

            # Save updated configuration
            with open(config_path, "w") as f:
                yaml.dump(config, f)

            logger.info(
                f"Applied parameter adjustment: {adjustment['parameter']} = {adjustment['suggested_value']}"
            )

        except Exception as e:
            logger.error(f"Error applying parameter adjustment: {e}")

    async def _get_last_analysis_time(self) -> Optional[str]:
        """Get last analysis time"""
        try:
            analysis_files = list(self.learning_data_path.glob("analysis_*.json"))
            if analysis_files:
                # Get the most recent analysis file
                latest_file = max(analysis_files, key=lambda x: x.stat().st_mtime)
                with open(latest_file, "r") as f:
                    analysis_data = json.load(f)
                return analysis_data.get("analysis_timestamp")
            return None
        except Exception as e:
            logger.error(f"Error getting last analysis time: {e}")
            return None

    def _calculate_learning_confidence(self) -> float:
        """Calculate learning confidence score"""
        try:
            if not self.learned_patterns:
                return 0.0

            # Calculate average confidence of learned patterns
            avg_confidence = sum(p.confidence for p in self.learned_patterns) / len(
                self.learned_patterns
            )

            # Factor in number of patterns (more patterns = higher confidence)
            pattern_bonus = min(len(self.learned_patterns) / 10, 0.2)  # Max 0.2 bonus

            # Factor in recency of patterns
            recent_patterns = [
                p
                for p in self.learned_patterns
                if (datetime.now() - p.last_observed).days < 7
            ]
            recency_bonus = min(
                len(recent_patterns) / len(self.learned_patterns), 0.1
            )  # Max 0.1 bonus

            total_confidence = min(avg_confidence + pattern_bonus + recency_bonus, 1.0)

            return total_confidence
        except Exception as e:
            logger.error(f"Error calculating learning confidence: {e}")
            return 0.0
