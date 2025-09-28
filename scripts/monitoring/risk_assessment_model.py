#!/usr/bin/env python3
"""
🤖 NEXUS Platform - Advanced Risk Assessment ML Model
Machine learning model for financial risk assessment and scoring
"""

import logging
from datetime import datetime, timedelta

import joblib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskAssessment:
    risk_score: float
    risk_level: RiskLevel
    confidence: float
    risk_factors: List[str]
    recommendations: List[str]
    feature_importance: Dict[str, float]
    prediction_timestamp: datetime


@dataclass
class RiskFeatures:
    transaction_volume: float
    transaction_frequency: float
    average_transaction_amount: float
    expense_ratio: float
    cash_flow_volatility: float
    payment_delays: int
    unusual_patterns: int
    geographic_spread: float
    vendor_concentration: float
    seasonal_variability: float


class RiskAssessmentModel:
    """Advanced ML model for financial risk assessment"""

    def __init__(self, model_path: str = "models/risk_assessment"):
        self.model_path = Path(model_path)
        self.model_path.mkdir(parents=True, exist_ok=True)
        self.model = None
        self.scaler = None
        self.feature_selector = None
        self.label_encoder = None
        self.feature_names = [
            "transaction_volume",
            "transaction_frequency",
            "average_transaction_amount",
            "expense_ratio",
            "cash_flow_volatility",
            "payment_delays",
            "unusual_patterns",
            "geographic_spread",
            "vendor_concentration",
            "seasonal_variability",
        ]
        self.is_trained = False

    def _analyze_risk_factors(
        self, features: RiskFeatures, risk_level: RiskLevel
    ) -> Tuple[List[str], List[str]]:
        """Analyze risk factors and generate recommendations"""
        risk_factors = []
        recommendations = []

        # Analyze each feature
        if features.expense_ratio > 0.8:
            risk_factors.append("High expense ratio (>80% of income)")
            recommendations.append("Review and optimize expense categories")

        if features.cash_flow_volatility > 1.5:
            risk_factors.append("High cash flow volatility")
            recommendations.append("Implement cash flow forecasting and budgeting")

        if features.payment_delays > 10:
            risk_factors.append("Frequent payment delays")
            recommendations.append("Improve accounts payable management")

        if features.unusual_patterns > 5:
            risk_factors.append("Unusual transaction patterns detected")
            recommendations.append("Review transactions for potential fraud or errors")

        if features.vendor_concentration > 0.7:
            risk_factors.append("High vendor concentration risk")
            recommendations.append("Diversify vendor relationships")

        if features.geographic_spread < 0.3:
            risk_factors.append("Limited geographic diversification")
            recommendations.append("Expand business operations geographically")

        # Default factors if none found
        if not risk_factors:
            risk_factors.append("Standard risk profile")
            recommendations.append("Continue monitoring financial metrics")

        return risk_factors, recommendations

    def _save_model(self):
        """Save trained model to disk"""
        try:
            joblib.dump(self.model, self.model_path / "risk_model.pkl")
            joblib.dump(self.scaler, self.model_path / "scaler.pkl")
            joblib.dump(self.feature_selector, self.model_path / "feature_selector.pkl")
            joblib.dump(self.label_encoder, self.model_path / "label_encoder.pkl")

            logger.info("Risk assessment model saved successfully")
        except Exception as e:
            logger.error(f"Error saving model: {e}")

    def _load_model(self) -> bool:
        """Load trained model from disk"""
        try:
            model_file = self.model_path / "risk_model.pkl"
            if model_file.exists():
                self.model = joblib.load(model_file)
                self.scaler = joblib.load(self.model_path / "scaler.pkl")
                self.feature_selector = joblib.load(
                    self.model_path / "feature_selector.pkl"
                )
                self.label_encoder = joblib.load(self.model_path / "label_encoder.pkl")
                self.is_trained = True
                logger.info("Risk assessment model loaded successfully")
                return True
            return False
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False


# Global instance
risk_assessment_model = RiskAssessmentModel()
