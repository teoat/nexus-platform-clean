#!/usr/bin/env python3
"""
NEXUS Platform - AI Model Training
Train AI models with production data for optimization and analytics
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from services.ai_optimizer import AISSOTOptimizer
from services.analytics_engine import AIAnalyticsEngine, AnalyticsType
from services.performance_monitor import PerformanceMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AIModelTrainer:
    """AI model training service for NEXUS Phase 3"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.models = {}
        self.training_data = {}
        self.model_metrics = {}

        # Model configuration
        self.optimization_model_path = self.config.get(
            "optimization_model_path", "models/optimization_model.pkl"
        )
        self.analytics_model_path = self.config.get(
            "analytics_model_path", "models/analytics_model.pkl"
        )
        self.anomaly_model_path = self.config.get(
            "anomaly_model_path", "models/anomaly_model.pkl"
        )

        # Training configuration
        self.training_window_days = self.config.get("training_window_days", 30)
        self.test_size = self.config.get("test_size", 0.2)
        self.random_state = self.config.get("random_state", 42)

    async def collect_training_data(self) -> Dict[str, Any]:
        """Collect production data for model training"""
        logger.info("Collecting training data from production")

        training_data = {
            "performance_data": [],
            "usage_patterns": [],
            "optimization_opportunities": [],
            "analytics_insights": [],
            "security_events": [],
            "deployment_events": [],
        }

        try:
            # Collect performance data
            performance_monitor = PerformanceMonitor()
            performance_metrics = await performance_monitor.collect_metrics()

            if performance_metrics:
                training_data["performance_data"].append(
                    {
                        "timestamp": performance_metrics.timestamp.isoformat(),
                        "cpu_percent": performance_metrics.cpu_percent,
                        "memory_percent": performance_metrics.memory_percent,
                        "response_time": performance_metrics.average_response_time,
                        "error_rate": performance_metrics.error_rate,
                        "cache_hit_rate": performance_metrics.cache_hit_rate,
                        "throughput": performance_metrics.throughput,
                    }
                )

            # Collect optimization data
            ai_optimizer = AISSOTOptimizer(ssot_registry=None)
            optimization_opportunities = (
                await ai_optimizer.get_optimization_opportunities()
            )

            for opp in optimization_opportunities:
                training_data["optimization_opportunities"].append(
                    {
                        "type": opp.type.value,
                        "performance_gain": opp.performance_gain,
                        "confidence_score": opp.confidence_score,
                        "description": opp.description,
                    }
                )

            # Collect analytics data
            analytics_engine = AIAnalyticsEngine()
            time_range = (
                datetime.now(timezone.utc) - timedelta(days=self.training_window_days),
                datetime.now(timezone.utc),
            )

            usage_insights = await analytics_engine.analyze_usage_patterns(time_range)
            predictive_insights = await analytics_engine.generate_predictive_insights()

            for insight in usage_insights:
                training_data["analytics_insights"].append(
                    {
                        "type": insight.type.value,
                        "category": insight.category,
                        "confidence_score": insight.confidence_score,
                        "impact_score": insight.impact_score,
                        "actionable": insight.actionable,
                    }
                )

            for insight in predictive_insights:
                training_data["analytics_insights"].append(
                    {
                        "type": insight.type.value,
                        "category": insight.category,
                        "confidence_score": insight.confidence_score,
                        "impact_score": insight.impact_score,
                        "actionable": insight.actionable,
                    }
                )

            logger.info(
                f"Collected training data: {len(training_data['performance_data'])} performance records, "
                f"{len(training_data['optimization_opportunities'])} optimization opportunities, "
                f"{len(training_data['analytics_insights'])} analytics insights"
            )

        except Exception as e:
            logger.error(f"Error collecting training data: {e}")

        self.training_data = training_data
        return training_data

    async def train_optimization_model(self) -> Dict[str, Any]:
        """Train AI optimization model"""
        logger.info("Training AI optimization model")

        try:
            # Prepare training data
            X, y = self._prepare_optimization_training_data()

            if len(X) == 0:
                logger.warning("No optimization training data available")
                return {"success": False, "error": "No training data"}

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=self.test_size, random_state=self.random_state
            )

            # Train model
            model = RandomForestRegressor(
                n_estimators=100, max_depth=10, random_state=self.random_state
            )

            model.fit(X_train, y_train)

            # Evaluate model
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            accuracy = model.score(X_test, y_test)

            # Save model
            Path(self.optimization_model_path).parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(model, self.optimization_model_path)

            # Store metrics
            self.model_metrics["optimization"] = {
                "mse": mse,
                "accuracy": accuracy,
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "feature_importance": dict(
                    zip(
                        [
                            "cpu_percent",
                            "memory_percent",
                            "response_time",
                            "error_rate",
                            "cache_hit_rate",
                        ],
                        model.feature_importances_,
                    )
                ),
            }

            self.models["optimization"] = model

            logger.info(
                f"Optimization model trained successfully. MSE: {mse:.4f}, Accuracy: {accuracy:.4f}"
            )

            return {
                "success": True,
                "mse": mse,
                "accuracy": accuracy,
                "training_samples": len(X_train),
                "test_samples": len(X_test),
            }

        except Exception as e:
            logger.error(f"Error training optimization model: {e}")
            return {"success": False, "error": str(e)}

    async def train_analytics_model(self) -> Dict[str, Any]:
        """Train analytics insights model"""
        logger.info("Training analytics insights model")

        try:
            # Prepare training data
            X, y = self._prepare_analytics_training_data()

            if len(X) == 0:
                logger.warning("No analytics training data available")
                return {"success": False, "error": "No training data"}

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=self.test_size, random_state=self.random_state
            )

            # Train model
            model = RandomForestRegressor(
                n_estimators=150, max_depth=12, random_state=self.random_state
            )

            model.fit(X_train, y_train)

            # Evaluate model
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            accuracy = model.score(X_test, y_test)

            # Save model
            Path(self.analytics_model_path).parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(model, self.analytics_model_path)

            # Store metrics
            self.model_metrics["analytics"] = {
                "mse": mse,
                "accuracy": accuracy,
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "feature_importance": dict(
                    zip(
                        ["confidence_score", "impact_score", "actionable"],
                        model.feature_importances_,
                    )
                ),
            }

            self.models["analytics"] = model

            logger.info(
                f"Analytics model trained successfully. MSE: {mse:.4f}, Accuracy: {accuracy:.4f}"
            )

            return {
                "success": True,
                "mse": mse,
                "accuracy": accuracy,
                "training_samples": len(X_train),
                "test_samples": len(X_test),
            }

        except Exception as e:
            logger.error(f"Error training analytics model: {e}")
            return {"success": False, "error": str(e)}

    async def train_anomaly_detection_model(self) -> Dict[str, Any]:
        """Train anomaly detection model"""
        logger.info("Training anomaly detection model")

        try:
            # Prepare training data
            X = self._prepare_anomaly_training_data()

            if len(X) == 0:
                logger.warning("No anomaly training data available")
                return {"success": False, "error": "No training data"}

            # Train model
            model = IsolationForest(contamination=0.1, random_state=self.random_state)

            model.fit(X)

            # Evaluate model
            anomaly_scores = model.decision_function(X)
            predictions = model.predict(X)

            # Save model
            Path(self.anomaly_model_path).parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(model, self.anomaly_model_path)

            # Store metrics
            self.model_metrics["anomaly"] = {
                "training_samples": len(X),
                "anomaly_rate": np.mean(predictions == -1),
                "mean_anomaly_score": np.mean(anomaly_scores),
            }

            self.models["anomaly"] = model

            logger.info(
                f"Anomaly detection model trained successfully. Anomaly rate: {np.mean(predictions == -1):.4f}"
            )

            return {
                "success": True,
                "training_samples": len(X),
                "anomaly_rate": np.mean(predictions == -1),
                "mean_anomaly_score": np.mean(anomaly_scores),
            }

        except Exception as e:
            logger.error(f"Error training anomaly detection model: {e}")
            return {"success": False, "error": str(e)}

    def _prepare_optimization_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare optimization model training data"""
        X = []
        y = []

        for perf_data in self.training_data["performance_data"]:
            # Features: CPU, memory, response time, error rate, cache hit rate
            features = [
                perf_data["cpu_percent"],
                perf_data["memory_percent"],
                perf_data["response_time"],
                perf_data["error_rate"],
                perf_data["cache_hit_rate"],
            ]
            X.append(features)

            # Target: throughput (performance indicator)
            y.append(perf_data["throughput"])

        return np.array(X), np.array(y)

    def _prepare_analytics_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare analytics model training data"""
        X = []
        y = []

        for insight in self.training_data["analytics_insights"]:
            # Features: confidence score, impact score, actionable
            features = [
                insight["confidence_score"],
                insight["impact_score"],
                1.0 if insight["actionable"] else 0.0,
            ]
            X.append(features)

            # Target: combined score (confidence * impact)
            target = insight["confidence_score"] * insight["impact_score"]
            y.append(target)

        return np.array(X), np.array(y)

    def _prepare_anomaly_training_data(self) -> np.ndarray:
        """Prepare anomaly detection training data"""
        X = []

        for perf_data in self.training_data["performance_data"]:
            # Features: all performance metrics
            features = [
                perf_data["cpu_percent"],
                perf_data["memory_percent"],
                perf_data["response_time"],
                perf_data["error_rate"],
                perf_data["cache_hit_rate"],
                perf_data["throughput"],
            ]
            X.append(features)

        return np.array(X)

    async def train_all_models(self) -> Dict[str, Any]:
        """Train all AI models"""
        logger.info("Starting comprehensive AI model training")

        results = {
            "start_time": datetime.now(timezone.utc).isoformat(),
            "end_time": None,
            "success": True,
            "models_trained": [],
            "errors": [],
        }

        try:
            # Collect training data
            await self.collect_training_data()

            # Train optimization model
            opt_result = await self.train_optimization_model()
            if opt_result["success"]:
                results["models_trained"].append("optimization")
            else:
                results["errors"].append(f"Optimization model: {opt_result['error']}")
                results["success"] = False

            # Train analytics model
            analytics_result = await self.train_analytics_model()
            if analytics_result["success"]:
                results["models_trained"].append("analytics")
            else:
                results["errors"].append(
                    f"Analytics model: {analytics_result['error']}"
                )
                results["success"] = False

            # Train anomaly detection model
            anomaly_result = await self.train_anomaly_detection_model()
            if anomaly_result["success"]:
                results["models_trained"].append("anomaly_detection")
            else:
                results["errors"].append(
                    f"Anomaly detection model: {anomaly_result['error']}"
                )
                results["success"] = False

            results["end_time"] = datetime.now(timezone.utc).isoformat()
            results["model_metrics"] = self.model_metrics

            logger.info(
                f"AI model training completed. Trained {len(results['models_trained'])} models"
            )

        except Exception as e:
            logger.error(f"Error in AI model training: {e}")
            results["success"] = False
            results["errors"].append(str(e))

        return results

    def get_model_metrics(self) -> Dict[str, Any]:
        """Get model training metrics"""
        return self.model_metrics

    def load_trained_models(self) -> Dict[str, Any]:
        """Load trained models from disk"""
        loaded_models = {}

        try:
            if Path(self.optimization_model_path).exists():
                loaded_models["optimization"] = joblib.load(
                    self.optimization_model_path
                )
                logger.info("Loaded optimization model")

            if Path(self.analytics_model_path).exists():
                loaded_models["analytics"] = joblib.load(self.analytics_model_path)
                logger.info("Loaded analytics model")

            if Path(self.anomaly_model_path).exists():
                loaded_models["anomaly"] = joblib.load(self.anomaly_model_path)
                logger.info("Loaded anomaly detection model")

        except Exception as e:
            logger.error(f"Error loading models: {e}")

        return loaded_models


async def main():
    """Main function to run AI model training"""
    logger.info("Starting AI model training")

    # Configuration
    config = {
        "optimization_model_path": "models/optimization_model.pkl",
        "analytics_model_path": "models/analytics_model.pkl",
        "anomaly_model_path": "models/anomaly_model.pkl",
        "training_window_days": 30,
        "test_size": 0.2,
        "random_state": 42,
    }

    trainer = AIModelTrainer(config)

    try:
        # Train all models
        results = await trainer.train_all_models()

        # Save results
        results_file = Path("ai_model_training_results.json")
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        # Print results
        print("\n" + "=" * 60)
        print("AI MODEL TRAINING RESULTS")
        print("=" * 60)
        print(f"Success: {results['success']}")
        print(f"Models Trained: {len(results['models_trained'])}")
        print(f"Models: {', '.join(results['models_trained'])}")

        if results["errors"]:
            print(f"Errors: {len(results['errors'])}")
            for error in results["errors"]:
                print(f"  - {error}")

        print("=" * 60)
        print(f"Results saved to: {results_file}")

        # Exit with appropriate code
        sys.exit(0 if results["success"] else 1)

    except Exception as e:
        logger.critical(f"AI model training failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
