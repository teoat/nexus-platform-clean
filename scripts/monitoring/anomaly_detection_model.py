#!/usr/bin/env python3
"""
🤖 NEXUS Platform - Advanced Anomaly Detection ML Model
Machine learning model for fraud detection and unusual pattern identification
"""

import json
import logging
from datetime import datetime, timedelta

import joblib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnomalySeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AnomalyDetection:
    is_anomaly: bool
    anomaly_score: float
    severity: AnomalySeverity
    explanation: str
    confidence: float
    detected_at: datetime
    features: Dict[str, Any]


@dataclass
class TransactionFeatures:
    amount: float
    amount_log: float
    is_income: bool
    is_expense: bool
    hour_of_day: int
    day_of_week: int
    day_of_month: int
    category: str
    account: str
    description_length: int
    is_weekend: bool
    is_business_hours: bool
    amount_zscore: float
    category_frequency: float
    time_since_last_transaction: float


class AnomalyDetectionModel:
    """Advanced ML model for transaction anomaly detection"""

    def __init__(self, model_path: str = "models/anomaly_detection"):
        self.model_path = Path(model_path)
        self.model_path.mkdir(parents=True, exist_ok=True)
        self.isolation_forest = None
        self.classifier = None
        self.scaler = None
        self.encoder = None
        self.feature_stats = {}
        self.is_trained = False

    def _analyze_anomaly(
        self, features: TransactionFeatures, anomaly_score: float, is_anomaly: bool
    ) -> Tuple[AnomalySeverity, str]:
        """Analyze anomaly and determine severity and explanation"""
        if not is_anomaly:
            return AnomalySeverity.LOW, "Transaction appears normal"

        reasons = []
        severity_score = 0

        # Amount-based anomalies
        if abs(features.amount_zscore) > 3:
            reasons.append("unusually large amount")
            severity_score += 3
        elif abs(features.amount_zscore) > 2:
            reasons.append("moderately large amount")
            severity_score += 2

        # Time-based anomalies
        if not features.is_business_hours and features.amount > self.feature_stats.get(
            "amount_percentiles", {}
        ).get(0.95, 1000):
            reasons.append("large transaction outside business hours")
            severity_score += 2

        if features.is_weekend and features.amount > self.feature_stats.get(
            "amount_percentiles", {}
        ).get(0.90, 500):
            reasons.append("large transaction on weekend")
            severity_score += 1

        # Category-based anomalies
        category_count = self.feature_stats.get("category_counts", {}).get(
            features.category, 0
        )
        if category_count == 0:
            reasons.append("unusual category")
            severity_score += 2
        elif features.category_frequency < 0.05:  # Less than 5% of transactions
            reasons.append("infrequent category")
            severity_score += 1

        # Pattern-based anomalies
        if features.time_since_last_transaction > 720:  # More than 30 days
            reasons.append("long time since last transaction")
            severity_score += 1

        # Determine severity
        if severity_score >= 5:
            severity = AnomalySeverity.CRITICAL
        elif severity_score >= 3:
            severity = AnomalySeverity.HIGH
        elif severity_score >= 2:
            severity = AnomalySeverity.MEDIUM
        else:
            severity = AnomalySeverity.LOW

        explanation = (
            f"Anomalous transaction due to: {', '.join(reasons)}"
            if reasons
            else "Anomalous pattern detected"
        )

        return severity, explanation

    def _save_model(self):
        """Save trained model to disk"""
        try:
            joblib.dump(self.isolation_forest, self.model_path / "anomaly_model.pkl")
            with open(self.model_path / "feature_stats.json", "w") as f:
                json.dump(self.feature_stats, f, default=str)

            logger.info("Anomaly detection model saved successfully")
        except Exception as e:
            logger.error(f"Error saving anomaly model: {e}")

    def _load_model(self) -> bool:
        """Load trained model from disk"""
        try:
            model_file = self.model_path / "anomaly_model.pkl"
            stats_file = self.model_path / "feature_stats.json"

            if model_file.exists() and stats_file.exists():
                self.isolation_forest = joblib.load(model_file)
                with open(stats_file, "r") as f:
                    self.feature_stats = json.load(f)
                self.is_trained = True
                logger.info("Anomaly detection model loaded successfully")
                return True
            return False
        except Exception as e:
            logger.error(f"Error loading anomaly model: {e}")
            return False


# Global instance
anomaly_detection_model = AnomalyDetectionModel()
