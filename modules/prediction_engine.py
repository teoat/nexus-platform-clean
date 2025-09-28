"""
Prediction Engine for Frenly AI Meta Module

This module implements predictive capabilities that forecast future system needs,
repository growth, and optimization requirements based on historical data.
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

import numpy as np
import yaml

logger = logging.getLogger(__name__)


@dataclass
class Prediction:
    """Represents a prediction made by the system"""

    prediction_id: str
    prediction_type: str
    value: Any
    confidence: float
    horizon_days: int
    created_at: datetime
    metadata: Dict[str, Any]
    accuracy_score: float = 0.0


@dataclass
class PredictionModel:
    """Represents a prediction model"""

    model_id: str
    model_type: str
    accuracy: float
    last_trained: datetime
    parameters: Dict[str, Any]
    training_data_size: int


class PredictionEngine:
    """
    Prediction Engine for Frenly AI Meta Module

    Generates predictions about future system behavior, repository growth,
    and optimization needs based on historical data and patterns.
    """

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.prediction_data_path = self.base_path / "frenly_ai_meta" / "predictions"
        self.models_path = self.base_path / "prediction_models"

        # Create directories
        self.prediction_data_path.mkdir(parents=True, exist_ok=True)
        self.models_path.mkdir(parents=True, exist_ok=True)

        # Prediction state
        self.predictions: List[Prediction] = []
        self.models: List[PredictionModel] = []
        self.historical_data: Dict[str, List[float]] = defaultdict(list)

        # Configuration
        self.config = self._load_prediction_config()

        # Load existing data
        self._load_prediction_data()

    def _load_prediction_config(self) -> Dict[str, Any]:
        """Load prediction configuration"""
        config_path = self.base_path / "config" / "frenly_ai_meta.yaml"

        if config_path.exists():
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                return config.get("frenly_ai_meta", {}).get("prediction", {})

        return {
            "enabled": True,
            "forecast_horizon_days": 30,
            "confidence_threshold": 0.8,
            "prediction_types": [
                "repository_growth",
                "optimization_needs",
                "performance_trends",
                "resource_requirements",
            ],
        }

    async def generate_repository_growth_prediction(
        self, historical_data: List[Dict[str, Any]]
    ) -> Prediction:
        """Predict repository growth based on historical data"""
        logger.info("Generating repository growth prediction...")

        # Extract repository size data
        size_data = []
        for data_point in historical_data:
            if "repository_size" in data_point:
                size_data.append(data_point["repository_size"])

        if len(size_data) < 2:
            # Not enough data for prediction
            return Prediction(
                prediction_id="repo_growth_insufficient_data",
                prediction_type="repository_growth",
                value="Insufficient data for prediction",
                confidence=0.0,
                horizon_days=30,
                created_at=datetime.now(),
                metadata={"data_points": len(size_data)},
                accuracy_score=0.0,
            )

        # Simple linear regression for growth prediction
        growth_rate = self._calculate_growth_rate(size_data)
        current_size = size_data[-1]
        predicted_growth = current_size * (1 + growth_rate)

        # Calculate confidence based on data consistency
        confidence = self._calculate_confidence(size_data)

        prediction = Prediction(
            prediction_id="repo_growth_prediction",
            prediction_type="repository_growth",
            value=f"{predicted_growth:.2f} MB",
            confidence=confidence,
            horizon_days=30,
            created_at=datetime.now(),
            metadata={
                "current_size": current_size,
                "growth_rate": growth_rate,
                "data_points": len(size_data),
                "trend": "increasing" if growth_rate > 0 else "decreasing",
            },
            accuracy_score=confidence,
        )

        self.predictions.append(prediction)
        await self._save_predictions()

        return prediction

    async def generate_optimization_needs_prediction(
        self, historical_data: List[Dict[str, Any]]
    ) -> Prediction:
        """Predict future optimization needs"""
        logger.info("Generating optimization needs prediction...")

        # Analyze optimization frequency and effectiveness
        optimization_events = [
            d for d in historical_data if d.get("action", "").startswith("optimize")
        ]

        if len(optimization_events) < 3:
            return Prediction(
                prediction_id="optimization_needs_insufficient_data",
                prediction_type="optimization_needs",
                value="Insufficient data for prediction",
                confidence=0.0,
                horizon_days=14,
                created_at=datetime.now(),
                metadata={"optimization_events": len(optimization_events)},
                accuracy_score=0.0,
            )

        # Calculate optimization frequency
        optimization_frequency = len(optimization_events) / 30  # per day

        # Predict next optimization need
        days_until_next = (
            max(1, int(7 / optimization_frequency))
            if optimization_frequency > 0
            else 14
        )

        # Determine optimization type based on patterns
        optimization_types = [
            d.get("optimization_type", "general") for d in optimization_events
        ]
        most_common_type = max(set(optimization_types), key=optimization_types.count)

        confidence = min(0.9, len(optimization_events) / 10.0)

        prediction = Prediction(
            prediction_id="optimization_needs_prediction",
            prediction_type="optimization_needs",
            value=f"{most_common_type}_optimization_needed",
            confidence=confidence,
            horizon_days=days_until_next,
            created_at=datetime.now(),
            metadata={
                "optimization_frequency": optimization_frequency,
                "days_until_next": days_until_next,
                "recommended_type": most_common_type,
                "historical_events": len(optimization_events),
            },
            accuracy_score=confidence,
        )

        self.predictions.append(prediction)
        await self._save_predictions()

        return prediction

    async def generate_performance_trend_prediction(
        self, historical_data: List[Dict[str, Any]]
    ) -> Prediction:
        """Predict performance trends"""
        logger.info("Generating performance trend prediction...")

        # Extract performance metrics
        execution_times = []
        success_rates = []

        for data_point in historical_data:
            if "execution_time" in data_point:
                execution_times.append(data_point["execution_time"])
            if "success_rate" in data_point:
                success_rates.append(data_point["success_rate"])

        if len(execution_times) < 5:
            return Prediction(
                prediction_id="performance_trend_insufficient_data",
                prediction_type="performance_trends",
                value="Insufficient data for prediction",
                confidence=0.0,
                horizon_days=7,
                created_at=datetime.now(),
                metadata={"data_points": len(execution_times)},
                accuracy_score=0.0,
            )

        # Analyze trends
        time_trend = self._analyze_trend(execution_times)
        success_trend = (
            self._analyze_trend(success_rates) if success_rates else "stable"
        )

        # Predict performance direction
        if time_trend == "improving" and success_trend in ["improving", "stable"]:
            performance_direction = "improving"
            confidence = 0.8
        elif time_trend == "degrading" or success_trend == "degrading":
            performance_direction = "degrading"
            confidence = 0.9
        else:
            performance_direction = "stable"
            confidence = 0.7

        prediction = Prediction(
            prediction_id="performance_trend_prediction",
            prediction_type="performance_trends",
            value=performance_direction,
            confidence=confidence,
            horizon_days=7,
            created_at=datetime.now(),
            metadata={
                "execution_time_trend": time_trend,
                "success_rate_trend": success_trend,
                "data_points": len(execution_times),
                "average_execution_time": statistics.mean(execution_times),
                "average_success_rate": statistics.mean(success_rates)
                if success_rates
                else 0,
            },
            accuracy_score=confidence,
        )

        self.predictions.append(prediction)
        await self._save_predictions()

        return prediction

    async def generate_resource_requirements_prediction(
        self, historical_data: List[Dict[str, Any]]
    ) -> Prediction:
        """Predict future resource requirements"""
        logger.info("Generating resource requirements prediction...")

        # Extract resource usage data
        cpu_usage = []
        memory_usage = []
        disk_usage = []

        for data_point in historical_data:
            if "cpu_usage" in data_point:
                cpu_usage.append(data_point["cpu_usage"])
            if "memory_usage" in data_point:
                memory_usage.append(data_point["memory_usage"])
            if "disk_usage" in data_point:
                disk_usage.append(data_point["disk_usage"])

        if len(cpu_usage) < 5:
            return Prediction(
                prediction_id="resource_requirements_insufficient_data",
                prediction_type="resource_requirements",
                value="Insufficient data for prediction",
                confidence=0.0,
                horizon_days=14,
                created_at=datetime.now(),
                metadata={"data_points": len(cpu_usage)},
                accuracy_score=0.0,
            )

        # Predict resource requirements
        cpu_trend = self._analyze_trend(cpu_usage)
        memory_trend = self._analyze_trend(memory_usage) if memory_usage else "stable"
        disk_trend = self._analyze_trend(disk_usage) if disk_usage else "stable"

        # Determine if scaling is needed
        scaling_needed = any(
            trend == "increasing" for trend in [cpu_trend, memory_trend, disk_trend]
        )

        prediction = Prediction(
            prediction_id="resource_requirements_prediction",
            prediction_type="resource_requirements",
            value="scaling_recommended"
            if scaling_needed
            else "current_resources_sufficient",
            confidence=0.7,
            horizon_days=14,
            created_at=datetime.now(),
            metadata={
                "cpu_trend": cpu_trend,
                "memory_trend": memory_trend,
                "disk_trend": disk_trend,
                "scaling_needed": scaling_needed,
                "current_cpu": cpu_usage[-1] if cpu_usage else 0,
                "current_memory": memory_usage[-1] if memory_usage else 0,
                "current_disk": disk_usage[-1] if disk_usage else 0,
            },
            accuracy_score=0.7,
        )

        self.predictions.append(prediction)
        await self._save_predictions()

        return prediction

    def _calculate_growth_rate(self, data: List[float]) -> float:
        """Calculate growth rate using linear regression"""
        if len(data) < 2:
            return 0.0

        n = len(data)
        x = np.arange(n)
        y = np.array(data)

        # Simple linear regression
        slope = np.corrcoef(x, y)[0, 1] * (np.std(y) / np.std(x))

        # Convert to percentage growth rate
        if data[0] > 0:
            growth_rate = slope / data[0]
        else:
            growth_rate = 0.0

        return max(0.0, min(growth_rate, 1.0))  # Clamp between 0 and 100%

    def _calculate_confidence(self, data: List[float]) -> float:
        """Calculate prediction confidence based on data consistency"""
        if len(data) < 3:
            return 0.5

        # Calculate coefficient of variation
        mean_val = statistics.mean(data)
        std_val = statistics.stdev(data)

        if mean_val == 0:
            return 0.5

        cv = std_val / mean_val
        confidence = max(0.1, 1.0 - cv)  # Higher consistency = higher confidence

        return min(0.95, confidence)

    def _analyze_trend(self, data: List[float]) -> str:
        """Analyze trend in data series"""
        if len(data) < 3:
            return "stable"

        # Calculate slope using simple linear regression
        n = len(data)
        x = np.arange(n)
        y = np.array(data)

        slope = np.corrcoef(x, y)[0, 1] * (np.std(y) / np.std(x))

        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"

    async def evaluate_prediction_accuracy(
        self, prediction_id: str, actual_value: Any
    ) -> float:
        """Evaluate the accuracy of a prediction"""
        prediction = next(
            (p for p in self.predictions if p.prediction_id == prediction_id), None
        )

        if not prediction:
            return 0.0

        # Simple accuracy calculation based on prediction type
        if prediction.prediction_type == "repository_growth":
            try:
                predicted_size = float(prediction.value.split()[0])
                actual_size = float(actual_value)
                accuracy = 1.0 - abs(predicted_size - actual_size) / actual_size
            except:
                accuracy = 0.0
        elif prediction.prediction_type == "performance_trends":
            accuracy = 1.0 if prediction.value == actual_value else 0.0
        else:
            accuracy = 0.5  # Default accuracy for other types

        # Update prediction accuracy
        prediction.accuracy_score = max(0.0, min(1.0, accuracy))

        await self._save_predictions()

        return accuracy

    def get_prediction_summary(self) -> Dict[str, Any]:
        """Get summary of predictions"""
        recent_predictions = [
            p for p in self.predictions if (datetime.now() - p.created_at).days <= 7
        ]

        return {
            "total_predictions": len(self.predictions),
            "recent_predictions": len(recent_predictions),
            "average_confidence": statistics.mean(
                [p.confidence for p in recent_predictions]
            )
            if recent_predictions
            else 0.0,
            "average_accuracy": statistics.mean(
                [p.accuracy_score for p in recent_predictions]
            )
            if recent_predictions
            else 0.0,
            "prediction_types": list(set(p.prediction_type for p in self.predictions)),
            "recent_predictions_by_type": {
                ptype: len(
                    [p for p in recent_predictions if p.prediction_type == ptype]
                )
                for ptype in set(p.prediction_type for p in recent_predictions)
            },
        }

    async def _save_predictions(self):
        """Save predictions to disk"""
        predictions_data = []
        for prediction in self.predictions:
            predictions_data.append(
                {
                    "prediction_id": prediction.prediction_id,
                    "prediction_type": prediction.prediction_type,
                    "value": prediction.value,
                    "confidence": prediction.confidence,
                    "horizon_days": prediction.horizon_days,
                    "created_at": prediction.created_at.isoformat(),
                    "metadata": prediction.metadata,
                    "accuracy_score": prediction.accuracy_score,
                }
            )

        with open(self.prediction_data_path / "predictions.json", "w") as f:
            json.dump(predictions_data, f, indent=2)

    def _load_prediction_data(self):
        """Load existing prediction data"""
        predictions_file = self.prediction_data_path / "predictions.json"
        if predictions_file.exists():
            try:
                with open(predictions_file, "r") as f:
                    predictions_data = json.load(f)
                    for p_data in predictions_data:
                        prediction = Prediction(
                            prediction_id=p_data.get("prediction_id", "unknown"),
                            prediction_type=p_data.get("prediction_type", "unknown"),
                            value=p_data.get("value", "N/A"),
                            confidence=p_data.get("confidence", 0.0),
                            horizon_days=p_data.get("horizon_days", 0),
                            created_at=datetime.fromisoformat(
                                p_data.get("created_at", datetime.now().isoformat())
                            ),
                            metadata=p_data.get("metadata", {}),
                            accuracy_score=p_data.get("accuracy_score", 0.0),
                        )
                        self.predictions.append(prediction)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning(f"Failed to load prediction data: {e}")
                # Initialize with empty predictions
                self.predictions = []
