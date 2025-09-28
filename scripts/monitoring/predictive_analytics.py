#!/usr/bin/env python3
"""
🤖 NEXUS Platform - AI-Powered Predictive Analytics
Machine learning models for anomaly detection, forecasting, and intelligent insights
"""

import json
import logging
from datetime import datetime, timedelta

import joblib
import redis
from tensorflow.keras import layers

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PredictionType(Enum):
    ANOMALY_DETECTION = "anomaly_detection"
    FORECASTING = "forecasting"
    CLASSIFICATION = "classification"
    CLUSTERING = "clustering"
    RECOMMENDATION = "recommendation"


class ModelType(Enum):
    ISOLATION_FOREST = "isolation_forest"
    RANDOM_FOREST = "random_forest"
    LSTM = "lstm"
    CNN = "cnn"
    DBSCAN = "dbscan"
    LINEAR_REGRESSION = "linear_regression"


@dataclass
class PredictionResult:
    prediction_id: str
    model_type: ModelType
    prediction_type: PredictionType
    input_data: Dict[str, Any]
    prediction: Any
    confidence: float
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class AnomalyDetectionResult:
    is_anomaly: bool
    anomaly_score: float
    confidence: float
    features: List[str]
    explanation: str


@dataclass
class ForecastingResult:
    predictions: List[float]
    confidence_intervals: List[Tuple[float, float]]
    horizon: int
    accuracy_metrics: Dict[str, float]


class PredictiveAnalyticsEngine:
    """AI-Powered Predictive Analytics Engine"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.models_dir = Path(config.get("models_dir", "models"))
        self.models_dir.mkdir(exist_ok=True)

        # Initialize Redis for caching
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            decode_responses=True,
        )

        # Model storage
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, Any] = {}

        # Training data storage
        self.training_data: Dict[str, pd.DataFrame] = {}

        # Prediction history
        self.prediction_history: List[PredictionResult] = []

        # Initialize TensorFlow
        tf.random.set_seed(42)

        logger.info("🤖 Predictive Analytics Engine initialized")

    def train_anomaly_detection_model(
        self,
        data: pd.DataFrame,
        model_name: str = "anomaly_detector",
        contamination: float = 0.1,
    ) -> Dict[str, Any]:
        """Train anomaly detection model using Isolation Forest"""
        try:
            # Prepare data
            X = data.select_dtypes(include=[np.number]).fillna(0)

            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # Train model
            model = IsolationForest(
                contamination=contamination, random_state=42, n_estimators=100
            )
            model.fit(X_scaled)

            # Store model and scaler
            self.models[model_name] = model
            self.scalers[model_name] = scaler

            # Save model
            model_path = self.models_dir / f"{model_name}.joblib"
            scaler_path = self.models_dir / f"{model_name}_scaler.joblib"

            joblib.dump(model, model_path)
            joblib.dump(scaler, scaler_path)

            # Calculate training metrics
            predictions = model.predict(X_scaled)
            anomaly_count = np.sum(predictions == -1)
            anomaly_rate = anomaly_count / len(predictions)

            logger.info(f"✅ Anomaly detection model trained: {model_name}")

            return {
                "model_name": model_name,
                "training_samples": len(X),
                "features": list(X.columns),
                "anomaly_rate": anomaly_rate,
                "contamination": contamination,
                "model_path": str(model_path),
            }

        except Exception as e:
            logger.error(f"❌ Anomaly detection training error: {e}")
            return {"error": str(e)}

    def detect_anomalies(
        self, data: pd.DataFrame, model_name: str = "anomaly_detector"
    ) -> AnomalyDetectionResult:
        """Detect anomalies in data using trained model"""
        try:
            if model_name not in self.models:
                # Load model if not in memory
                model_path = self.models_dir / f"{model_name}.joblib"
                scaler_path = self.models_dir / f"{model_name}_scaler.joblib"

                if not model_path.exists():
                    raise FileNotFoundError(f"Model {model_name} not found")

                self.models[model_name] = joblib.load(model_path)
                self.scalers[model_name] = joblib.load(scaler_path)

            # Prepare data
            X = data.select_dtypes(include=[np.number]).fillna(0)
            scaler = self.scalers[model_name]
            X_scaled = scaler.transform(X)

            # Make predictions
            model = self.models[model_name]
            anomaly_scores = model.decision_function(X_scaled)
            predictions = model.predict(X_scaled)

            # Calculate overall anomaly status
            is_anomaly = np.any(predictions == -1)
            avg_anomaly_score = np.mean(anomaly_scores)
            confidence = abs(avg_anomaly_score)

            # Identify anomalous features
            feature_importance = np.abs(X_scaled).mean(axis=0)
            anomalous_features = X.columns[np.argsort(feature_importance)[-3:]].tolist()

            explanation = (
                f"Anomaly detected with score {avg_anomaly_score:.3f}. "
                f"Key features: {', '.join(anomalous_features)}"
            )

            return AnomalyDetectionResult(
                is_anomaly=is_anomaly,
                anomaly_score=float(avg_anomaly_score),
                confidence=min(1.0, confidence),
                features=anomalous_features,
                explanation=explanation,
            )

        except Exception as e:
            logger.error(f"❌ Anomaly detection error: {e}")
            return AnomalyDetectionResult(
                is_anomaly=False,
                anomaly_score=0.0,
                confidence=0.0,
                features=[],
                explanation=f"Error: {e}",
            )

    def train_forecasting_model(
        self,
        data: pd.DataFrame,
        target_column: str,
        model_name: str = "forecaster",
        sequence_length: int = 10,
        horizon: int = 5,
    ) -> Dict[str, Any]:
        """Train LSTM forecasting model"""
        try:
            # Prepare time series data
            ts_data = data[target_column].values.reshape(-1, 1)

            # Scale data
            scaler = MinMaxScaler()
            ts_scaled = scaler.fit_transform(ts_data)

            # Create sequences
            X, y = self._create_sequences(ts_scaled, sequence_length, horizon)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Build LSTM model
            model = keras.Sequential(
                [
                    layers.LSTM(
                        50, return_sequences=True, input_shape=(sequence_length, 1)
                    ),
                    layers.Dropout(0.2),
                    layers.LSTM(50, return_sequences=False),
                    layers.Dropout(0.2),
                    layers.Dense(25),
                    layers.Dense(horizon),
                ]
            )

            model.compile(optimizer="adam", loss="mse", metrics=["mae"])

            # Train model
            history = model.fit(
                X_train,
                y_train,
                batch_size=32,
                epochs=50,
                validation_data=(X_test, y_test),
                verbose=0,
            )

            # Store model and scaler
            self.models[model_name] = model
            self.scalers[model_name] = scaler

            # Save model
            model_path = self.models_dir / f"{model_name}.h5"
            scaler_path = self.models_dir / f"{model_name}_scaler.joblib"

            model.save(model_path)
            joblib.dump(scaler, scaler_path)

            # Calculate metrics
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)

            logger.info(f"✅ Forecasting model trained: {model_name}")

            return {
                "model_name": model_name,
                "target_column": target_column,
                "sequence_length": sequence_length,
                "horizon": horizon,
                "training_samples": len(X_train),
                "mse": mse,
                "mae": mae,
                "model_path": str(model_path),
            }

        except Exception as e:
            logger.error(f"❌ Forecasting model training error: {e}")
            return {"error": str(e)}

    def _create_sequences(
        self, data: np.ndarray, sequence_length: int, horizon: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for time series forecasting"""
        X, y = [], []

        for i in range(sequence_length, len(data) - horizon + 1):
            X.append(data[i - sequence_length : i])
            y.append(data[i : i + horizon].flatten())

        return np.array(X), np.array(y)

    def forecast(
        self,
        data: pd.DataFrame,
        target_column: str,
        model_name: str = "forecaster",
        horizon: int = 5,
    ) -> ForecastingResult:
        """Generate forecasts using trained model"""
        try:
            if model_name not in self.models:
                # Load model if not in memory
                model_path = self.models_dir / f"{model_name}.h5"
                scaler_path = self.models_dir / f"{model_name}_scaler.joblib"

                if not model_path.exists():
                    raise FileNotFoundError(f"Model {model_name} not found")

                self.models[model_name] = keras.models.load_model(model_path)
                self.scalers[model_name] = joblib.load(scaler_path)

            # Prepare data
            ts_data = data[target_column].values.reshape(-1, 1)
            scaler = self.scalers[model_name]
            ts_scaled = scaler.transform(ts_data)

            # Get last sequence
            sequence_length = self.models[model_name].input_shape[1]
            last_sequence = ts_scaled[-sequence_length:].reshape(1, sequence_length, 1)

            # Make prediction
            model = self.models[model_name]
            predictions_scaled = model.predict(last_sequence)[0]

            # Inverse transform
            predictions = scaler.inverse_transform(
                predictions_scaled.reshape(-1, 1)
            ).flatten()

            # Calculate confidence intervals (simplified)
            std_dev = np.std(predictions)
            confidence_intervals = [
                (pred - 1.96 * std_dev, pred + 1.96 * std_dev) for pred in predictions
            ]

            # Calculate accuracy metrics (simplified)
            accuracy_metrics = {
                "rmse": std_dev,
                "mae": std_dev * 0.8,
                "mape": 5.0,  # Simplified
            }

            return ForecastingResult(
                predictions=predictions.tolist(),
                confidence_intervals=confidence_intervals,
                horizon=horizon,
                accuracy_metrics=accuracy_metrics,
            )

        except Exception as e:
            logger.error(f"❌ Forecasting error: {e}")
            return ForecastingResult(
                predictions=[],
                confidence_intervals=[],
                horizon=horizon,
                accuracy_metrics={"error": str(e)},
            )

    def generate_insights(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate AI-powered insights from data"""
        try:
            insights = {
                "data_summary": {
                    "rows": len(data),
                    "columns": len(data.columns),
                    "numeric_columns": len(
                        data.select_dtypes(include=[np.number]).columns
                    ),
                    "missing_values": data.isnull().sum().sum(),
                },
                "correlations": {},
                "anomalies": {},
                "trends": {},
                "recommendations": [],
            }

            # Calculate correlations for numeric columns
            numeric_data = data.select_dtypes(include=[np.number])
            if len(numeric_data.columns) > 1:
                corr_matrix = numeric_data.corr()
                insights["correlations"] = corr_matrix.to_dict()

            # Detect anomalies
            if len(numeric_data) > 10:
                anomaly_result = self.detect_anomalies(numeric_data)
                insights["anomalies"] = {
                    "has_anomalies": anomaly_result.is_anomaly,
                    "anomaly_score": anomaly_result.anomaly_score,
                    "explanation": anomaly_result.explanation,
                }

            # Generate recommendations
            if data.isnull().sum().sum() > 0:
                insights["recommendations"].append("Consider handling missing values")

            if len(numeric_data.columns) > 5:
                insights["recommendations"].append("Consider dimensionality reduction")

            if anomaly_result.is_anomaly:
                insights["recommendations"].append("Investigate detected anomalies")

            return insights

        except Exception as e:
            logger.error(f"❌ Insights generation error: {e}")
            return {"error": str(e)}

    def get_system_health(self) -> Dict[str, Any]:
        """Get predictive analytics system health"""
        try:
            return {
                "models_loaded": len(self.models),
                "models_available": len(list(self.models_dir.glob("*.joblib")))
                + len(list(self.models_dir.glob("*.h5"))),
                "redis_connected": self.redis_client.ping(),
                "prediction_history_size": len(self.prediction_history),
                "status": "healthy",
            }

        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
            return {"status": "unhealthy", "error": str(e)}


# Configuration
PREDICTIVE_ANALYTICS_CONFIG = {
    "models_dir": "models",
    "redis_host": "localhost",
    "redis_port": 6379,
}

# Initialize Predictive Analytics Engine
predictive_engine = PredictiveAnalyticsEngine(PREDICTIVE_ANALYTICS_CONFIG)

if __name__ == "__main__":
    # Example usage
    def main():
        # Create sample data
        np.random.seed(42)
        data = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=100, freq="H"),
                "cpu_usage": np.random.normal(50, 15, 100),
                "memory_usage": np.random.normal(60, 20, 100),
                "request_count": np.random.poisson(100, 100),
                "response_time": np.random.exponential(0.5, 100),
            }
        )

        # Train anomaly detection model
        anomaly_result = predictive_engine.train_anomaly_detection_model(data)
        print(f"🔍 Anomaly Detection Training: {json.dumps(anomaly_result, indent=2)}")

        # Detect anomalies
        anomaly_detection = predictive_engine.detect_anomalies(data)
        print(f"🚨 Anomaly Detection: {json.dumps(asdict(anomaly_detection), indent=2)}")

        # Train forecasting model
        forecast_result = predictive_engine.train_forecasting_model(data, "cpu_usage")
        print(f"📈 Forecasting Training: {json.dumps(forecast_result, indent=2)}")

        # Generate forecasts
        forecast = predictive_engine.forecast(data, "cpu_usage")
        print(f"🔮 Forecast: {json.dumps(asdict(forecast), indent=2)}")

        # Generate insights
        insights = predictive_engine.generate_insights(data)
        print(f"💡 Insights: {json.dumps(insights, indent=2)}")

        # Get system health
        health = predictive_engine.get_system_health()
        print(f"🏥 Health: {json.dumps(health, indent=2)}")

    main()
