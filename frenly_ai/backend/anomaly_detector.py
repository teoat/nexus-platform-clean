#!/usr/bin/env python3
"""
Frenly AI Anomaly Detector
Predictive anomaly detection and risk scoring
"""

import asyncio
import json
import logging
import statistics
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

import joblib  # Added for saving/loading ML model
import numpy as np  # Added for ML model training
from sklearn.ensemble import IsolationForest  # Added for ML model training


class MLModelTrainer:
    """Trains and manages ML models for anomaly detection"""

    def __init__(self, model_path: str = "anomaly_model.joblib"):
        self.model = None
        self.model_path = model_path
        self._load_model()

    def _load_model(self):
        """Loads a pre-trained model if it exists"""
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                logger.info(f"ML model loaded from {self.model_path}")
            except Exception as e:
                logger.error(f"Error loading ML model: {e}")
                self.model = None
        else:
            logger.info("No pre-trained ML model found.")

    def train_model(self, data: List[Dict[str, Any]]):
        """Trains an Isolation Forest model for anomaly detection"""
        if not data:
            logger.warning("No data provided for ML model training.")
            return

        # Convert data to a format suitable for scikit-learn
        # This is a placeholder for actual feature engineering
        features = []
        for entry in data:
            # Example: using 'value' from metrics history as a feature
            if "value" in entry:
                features.append([entry["value"]])
            elif "total_amount" in entry:  # For transaction data
                features.append([entry["total_amount"]])
            # Add more feature extraction logic here based on actual data structure

        if not features:
            logger.warning("No features extracted from data for ML model training.")
            return

        X = np.array(features)

        # Train Isolation Forest model
        self.model = IsolationForest(random_state=42)
        self.model.fit(X)
        joblib.dump(self.model, self.model_path)
        logger.info(f"ML model trained and saved to {self.model_path}")

    def predict_anomaly(self, data_point: Dict[str, Any]) -> float:
        """Predicts anomaly score for a single data point"""
        if self.model is None:
            logger.warning("ML model not trained or loaded. Cannot predict anomaly.")
            return 0.0  # Default to no anomaly

        # Preprocess data_point for prediction
        # This should match the feature engineering used during training
        features = []
        if "value" in data_point:
            features.append([data_point["value"]])
        elif "total_amount" in data_point:
            features.append([data_point["total_amount"]])

        if not features:
            logger.warning(
                "No features extracted from data point for ML anomaly prediction."
            )
            return 0.0

        X_pred = np.array(features)
        anomaly_score = self.model.decision_function(X_pred)[0]
        return anomaly_score


class AnomalyDetector:
    """Predictive anomaly detection system"""

    def __init__(self):
        self.metrics_history = defaultdict(lambda: deque(maxlen=100))
        self.anomaly_thresholds = {
            "response_time": {"warning": 1000, "critical": 5000},  # milliseconds
            "error_rate": {"warning": 0.05, "critical": 0.15},  # 5% and 15%
            "memory_usage": {"warning": 0.8, "critical": 0.95},  # 80% and 95%
            "cpu_usage": {"warning": 0.8, "critical": 0.95},  # 80% and 95%
            "disk_usage": {"warning": 0.85, "critical": 0.95},  # 85% and 95%
            "active_connections": {"warning": 1000, "critical": 2000},
            "request_rate": {"warning": 1000, "critical": 2000},  # requests per minute
        }

        self.risk_factors = {
            "security": ["failed_logins", "suspicious_ips", "unusual_patterns"],
            "performance": ["slow_queries", "memory_leaks", "high_cpu"],
            "availability": ["service_down", "database_errors", "network_issues"],
            "compliance": ["audit_failures", "data_breaches", "policy_violations"],
        }

        self.anomaly_history = deque(maxlen=1000)
        self.risk_scores = defaultdict(float)
        self.ml_trainer = MLModelTrainer()  # Initialize ML model trainer

    def add_metric(
        self, metric_name: str, value: float, timestamp: Optional[datetime] = None
    ):
        """Add a metric value to history"""
        if timestamp is None:
            timestamp = datetime.now()

        self.metrics_history[metric_name].append(
            {"value": value, "timestamp": timestamp}
        )

    def detect_anomalies(self, current_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Detect anomalies in current metrics"""
        anomalies = []
        risk_score = 0.0

        for metric_name, value in current_metrics.items():
            if metric_name in self.anomaly_thresholds:
                thresholds = self.anomaly_thresholds[metric_name]

                # Check for critical anomalies
                if value >= thresholds["critical"]:
                    anomaly = {
                        "metric": metric_name,
                        "value": value,
                        "threshold": thresholds["critical"],
                        "severity": "critical",
                        "message": f"Critical {metric_name} anomaly detected",
                        "risk_impact": 0.9,
                    }
                    anomalies.append(anomaly)
                    risk_score += 0.9

                # Check for warning anomalies
                elif value >= thresholds["warning"]:
                    anomaly = {
                        "metric": metric_name,
                        "value": value,
                        "threshold": thresholds["warning"],
                        "severity": "warning",
                        "message": f"Warning {metric_name} anomaly detected",
                        "risk_impact": 0.5,
                    }
                    anomalies.append(anomaly)
                    risk_score += 0.5

        # Detect trend anomalies
        trend_anomalies = self._detect_trend_anomalies()
        anomalies.extend(trend_anomalies)

        # Calculate overall risk score
        risk_score = min(risk_score, 1.0)

        return {
            "anomalies": anomalies,
            "risk_score": risk_score,
            "risk_level": self._get_risk_level(risk_score),
            "timestamp": datetime.now().isoformat(),
            "total_anomalies": len(anomalies),
        }

    def _detect_trend_anomalies(self) -> List[Dict[str, Any]]:
        """Detect anomalies based on trends"""
        trend_anomalies = []

        for metric_name, history in self.metrics_history.items():
            if len(history) < 10:  # Need at least 10 data points
                continue

            values = [point["value"] for point in history]

            # Calculate trend
            if len(values) >= 5:
                recent_avg = statistics.mean(values[-5:])
                historical_avg = statistics.mean(values[:-5])

                # Detect significant deviation
                if recent_avg > historical_avg * 1.5:  # 50% increase
                    trend_anomalies.append(
                        {
                            "metric": metric_name,
                            "type": "trend",
                            "severity": "warning",
                            "message": f"Significant increase in {metric_name}",
                            "recent_avg": recent_avg,
                            "historical_avg": historical_avg,
                            "risk_impact": 0.3,
                        }
                    )
                elif recent_avg < historical_avg * 0.5:  # 50% decrease
                    trend_anomalies.append(
                        {
                            "metric": metric_name,
                            "type": "trend",
                            "severity": "info",
                            "message": f"Significant decrease in {metric_name}",
                            "recent_avg": recent_avg,
                            "historical_avg": historical_avg,
                            "risk_impact": 0.1,
                        }
                    )

        return trend_anomalies

    def _get_risk_level(self, risk_score: float) -> str:
        """Get risk level based on score"""
        if risk_score >= 0.8:
            return "critical"
        elif risk_score >= 0.6:
            return "high"
        elif risk_score >= 0.4:
            return "medium"
        elif risk_score >= 0.2:
            return "low"
        else:
            return "minimal"

    def predict_risk(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Predict potential risks based on context"""
        predictions = []
        risk_score = 0.0

        # Analyze context for risk factors
        page_type = context.get("type", "unknown")
        user_role = context.get("userRole", "user")
        timestamp = context.get("timestamp", datetime.now().isoformat())

        # Time-based risk analysis
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            hour = dt.hour

            # Higher risk during off-hours
            if hour < 6 or hour > 22:
                predictions.append(
                    {
                        "type": "time_based",
                        "risk": "unusual_access_time",
                        "severity": "medium",
                        "message": "Access during off-hours detected",
                        "confidence": 0.7,
                    }
                )
                risk_score += 0.3
        except:
            pass

        # Page-type risk analysis
        if page_type in ["admin", "settings", "security"]:
            predictions.append(
                {
                    "type": "page_based",
                    "risk": "sensitive_page_access",
                    "severity": "medium",
                    "message": "Access to sensitive page detected",
                    "confidence": 0.8,
                }
            )
            risk_score += 0.4

        # Role-based risk analysis
        if user_role == "admin" and page_type not in ["admin", "dashboard"]:
            predictions.append(
                {
                    "type": "role_based",
                    "risk": "admin_unusual_activity",
                    "severity": "low",
                    "message": "Admin user accessing non-admin pages",
                    "confidence": 0.6,
                }
            )
            risk_score += 0.2

        # Historical pattern analysis
        recent_anomalies = [
            a
            for a in self.anomaly_history
            if (datetime.now() - a.get("timestamp", datetime.now())).seconds < 3600
        ]

        if len(recent_anomalies) > 5:
            predictions.append(
                {
                    "type": "pattern_based",
                    "risk": "frequent_anomalies",
                    "severity": "high",
                    "message": "Frequent anomalies detected in recent history",
                    "confidence": 0.9,
                }
            )
            risk_score += 0.6

        return {
            "predictions": predictions,
            "risk_score": min(risk_score, 1.0),
            "risk_level": self._get_risk_level(risk_score),
            "timestamp": datetime.now().isoformat(),
            "total_predictions": len(predictions),
        }

    def suggest_actions(
        self, anomalies: List[Dict[str, Any]], predictions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Suggest actions based on anomalies and predictions"""
        actions = []

        # Analyze anomalies for action suggestions
        for anomaly in anomalies:
            if anomaly["severity"] == "critical":
                if anomaly["metric"] == "response_time":
                    actions.append(
                        {
                            "type": "performance",
                            "action": "scale_resources",
                            "priority": "high",
                            "description": "Scale up server resources to handle load",
                            "estimated_impact": "high",
                        }
                    )
                elif anomaly["metric"] == "error_rate":
                    actions.append(
                        {
                            "type": "reliability",
                            "action": "investigate_errors",
                            "priority": "critical",
                            "description": "Investigate and fix error sources",
                            "estimated_impact": "critical",
                        }
                    )
                elif anomaly["metric"] == "memory_usage":
                    actions.append(
                        {
                            "type": "performance",
                            "action": "restart_services",
                            "priority": "high",
                            "description": "Restart services to free memory",
                            "estimated_impact": "medium",
                        }
                    )

        # Analyze predictions for preventive actions
        for prediction in predictions:
            if prediction["severity"] == "high":
                if prediction["risk"] == "frequent_anomalies":
                    actions.append(
                        {
                            "type": "monitoring",
                            "action": "increase_monitoring",
                            "priority": "medium",
                            "description": "Increase monitoring frequency",
                            "estimated_impact": "medium",
                        }
                    )
                elif prediction["risk"] == "unusual_access_time":
                    actions.append(
                        {
                            "type": "security",
                            "action": "verify_identity",
                            "priority": "medium",
                            "description": "Verify user identity for off-hours access",
                            "estimated_impact": "medium",
                        }
                    )

        # Add general recommendations
        if not actions:
            actions.append(
                {
                    "type": "general",
                    "action": "continue_monitoring",
                    "priority": "low",
                    "description": "Continue monitoring system health",
                    "estimated_impact": "low",
                }
            )

        return actions


if __name__ == "__main__":
    # Test anomaly detector
    async def test_anomaly_detector():
        detector = AnomalyDetector()

        # Add some test metrics
        detector.add_metric("response_time", 500)
        detector.add_metric("error_rate", 0.02)
        detector.add_metric("memory_usage", 0.7)

        # Detect anomalies
        current_metrics = {
            "response_time": 6000,  # Critical anomaly
            "error_rate": 0.08,  # Warning anomaly
            "memory_usage": 0.9,  # Warning anomaly
        }

        anomalies = detector.detect_anomalies(current_metrics)
        print("Anomalies detected:")
        print(json.dumps(anomalies, indent=2))

        # Predict risks
        context = {
            "type": "admin",
            "userRole": "admin",
            "timestamp": datetime.now().isoformat(),
        }

        predictions = detector.predict_risk(context)
        print("\nRisk predictions:")
        print(json.dumps(predictions, indent=2))

        # Suggest actions
        actions = detector.suggest_actions(
            anomalies["anomalies"], predictions["predictions"]
        )
        print("\nSuggested actions:")
        print(json.dumps(actions, indent=2))

    asyncio.run(test_anomaly_detector())
