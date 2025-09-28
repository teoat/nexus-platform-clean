#!/usr/bin/env python3
"""
NEXUS Platform - Automated Anomaly Detection System
Real-time anomaly detection with multiple algorithms and alerting
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Anomaly detection libraries
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.metrics import classification_report
    from sklearn.neighbors import LocalOutlierFactor
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import OneClassSVM

    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    import tensorflow as tf
    from tensorflow.keras.layers import (LSTM, Dense, Input, RepeatVector,
                                         TimeDistributed)
    from tensorflow.keras.models import Model, Sequential

    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False

import asyncpg
import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from backend.config.settings import get_settings

logger = logging.getLogger(__name__)


class AnomalyAlgorithm(Enum):
    """Anomaly detection algorithm enumeration"""

    ISOLATION_FOREST = "isolation_forest"
    LOCAL_OUTLIER_FACTOR = "local_outlier_factor"
    ONE_CLASS_SVM = "one_class_svm"
    AUTOENCODER = "autoencoder"
    LSTM_AUTOENCODER = "lstm_autoencoder"
    STATISTICAL = "statistical"
    Z_SCORE = "z_score"
    IQR = "iqr"
    MAD = "mad"


class AnomalySeverity(Enum):
    """Anomaly severity enumeration"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status enumeration"""

    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


@dataclass
class AnomalyDetector:
    """Data class for anomaly detector"""

    detector_id: str
    name: str
    algorithm: AnomalyAlgorithm
    target_metric: str
    parameters: Dict[str, Any]
    training_data: Optional[pd.DataFrame] = None
    model: Any = None  # Trained model
    scaler: Any = None  # Data scaler
    baseline_stats: Dict[str, float] = field(default_factory=dict)
    is_active: bool = True
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_trained: Optional[datetime] = None


@dataclass
class Anomaly:
    """Data class for detected anomaly"""

    anomaly_id: str
    detector_id: str
    timestamp: datetime
    value: float
    expected_value: Optional[float] = None
    deviation: float = 0.0
    severity: AnomalySeverity = AnomalySeverity.LOW
    confidence: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    status: AlertStatus = AlertStatus.ACTIVE


@dataclass
class AnomalyAlert:
    """Data class for anomaly alert"""

    alert_id: str
    anomaly_id: str
    detector_id: str
    title: str
    description: str
    severity: AnomalySeverity
    status: AlertStatus
    notified_channels: List[str] = field(default_factory=list)
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AutomatedAnomalyDetectionSystem:
    """Automated anomaly detection system with real-time monitoring"""

    def __init__(self):
        self.settings = get_settings()
        self.db_engine = None
        self.redis_client = None

        # Detectors registry
        self.detectors: Dict[str, AnomalyDetector] = {}

        # Active monitoring tasks
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}

        # Alert thresholds
        self.alert_thresholds = {
            AnomalySeverity.LOW: 0.6,
            AnomalySeverity.MEDIUM: 0.75,
            AnomalySeverity.HIGH: 0.85,
            AnomalySeverity.CRITICAL: 0.95,
        }

    async def initialize(self):
        """Initialize the anomaly detection system"""
        try:
            # Database connection
            self.db_engine = create_async_engine(
                self.settings.database_url, echo=False, pool_size=10, max_overflow=20
            )

            # Redis connection
            self.redis_client = redis.Redis(
                host=self.settings.redis_host,
                port=self.settings.redis_port,
                db=self.settings.redis_db,
                decode_responses=True,
            )

            # Create tables
            await self._create_tables()

            # Load detectors
            await self._load_detectors()

            logger.info("Automated anomaly detection system initialized")

        except Exception as e:
            logger.error(f"Failed to initialize anomaly detection system: {e}")
            raise

    async def _create_tables(self):
        """Create necessary database tables"""
        try:
            async with self.db_engine.begin() as conn:
                # Anomaly detectors table
                await conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS anomaly_detectors (
                        detector_id VARCHAR(255) PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        algorithm VARCHAR(50) NOT NULL,
                        target_metric VARCHAR(255) NOT NULL,
                        parameters JSONB,
                        baseline_stats JSONB,
                        is_active BOOLEAN DEFAULT TRUE,
                        performance_metrics JSONB,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        last_trained TIMESTAMP WITH TIME ZONE
                    )
                """
                    )
                )

                # Anomalies table
                await conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS anomalies (
                        anomaly_id VARCHAR(255) PRIMARY KEY,
                        detector_id VARCHAR(255) NOT NULL,
                        timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                        value FLOAT NOT NULL,
                        expected_value FLOAT,
                        deviation FLOAT DEFAULT 0,
                        severity VARCHAR(20) DEFAULT 'low',
                        confidence FLOAT DEFAULT 0,
                        context JSONB,
                        description TEXT,
                        status VARCHAR(20) DEFAULT 'active'
                    )
                """
                    )
                )

                # Anomaly alerts table
                await conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS anomaly_alerts (
                        alert_id VARCHAR(255) PRIMARY KEY,
                        anomaly_id VARCHAR(255) NOT NULL,
                        detector_id VARCHAR(255) NOT NULL,
                        title VARCHAR(255) NOT NULL,
                        description TEXT,
                        severity VARCHAR(20) NOT NULL,
                        status VARCHAR(20) DEFAULT 'active',
                        notified_channels JSONB,
                        acknowledged_by VARCHAR(255),
                        acknowledged_at TIMESTAMP WITH TIME ZONE,
                        resolved_at TIMESTAMP WITH TIME ZONE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """
                    )
                )

        except Exception as e:
            logger.error(f"Failed to create anomaly detection tables: {e}")
            raise

    async def _load_detectors(self):
        """Load detectors from database"""
        try:
            async with self.db_engine.begin() as conn:
                result = await conn.execute(
                    text(
                        """
                    SELECT detector_id, name, algorithm, target_metric, parameters,
                           baseline_stats, is_active, performance_metrics, created_at, last_trained
                    FROM anomaly_detectors
                """
                    )
                )

                rows = result.fetchall()
                for row in rows:
                    detector = AnomalyDetector(
                        detector_id=row[0],
                        name=row[1],
                        algorithm=AnomalyAlgorithm(row[2]),
                        target_metric=row[3],
                        parameters=row[4] or {},
                        baseline_stats=row[5] or {},
                        is_active=row[6],
                        performance_metrics=row[7] or {},
                        created_at=row[8],
                        last_trained=row[9],
                    )
                    self.detectors[detector.detector_id] = detector

        except Exception as e:
            logger.error(f"Failed to load detectors: {e}")

    async def create_detector(
        self,
        name: str,
        algorithm: AnomalyAlgorithm,
        target_metric: str,
        parameters: Dict[str, Any] = None,
    ) -> Optional[str]:
        """Create a new anomaly detector"""
        try:
            detector_id = f"detector_{uuid.uuid4().hex}"

            detector = AnomalyDetector(
                detector_id=detector_id,
                name=name,
                algorithm=algorithm,
                target_metric=target_metric,
                parameters=parameters or {},
            )

            # Store detector
            await self._store_detector(detector)

            # Add to registry
            self.detectors[detector_id] = detector

            logger.info(f"Anomaly detector {detector_id} created")
            return detector_id

        except Exception as e:
            logger.error(f"Failed to create detector: {e}")
            return None

    async def train_detector(
        self, detector_id: str, training_data: pd.DataFrame
    ) -> bool:
        """Train an anomaly detector"""
        try:
            if detector_id not in self.detectors:
                logger.error(f"Detector {detector_id} not found")
                return False

            detector = self.detectors[detector_id]

            # Prepare training data
            if detector.target_metric not in training_data.columns:
                raise ValueError(
                    f"Target metric {detector.target_metric} not found in training data"
                )

            data = training_data[detector.target_metric].dropna().values.reshape(-1, 1)

            # Scale data
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(data)

            # Train model based on algorithm
            model = await self._train_model_by_algorithm(
                detector.algorithm, scaled_data, detector.parameters
            )

            if model:
                # Calculate baseline statistics
                baseline_stats = self._calculate_baseline_stats(data)

                # Update detector
                detector.model = model
                detector.scaler = scaler
                detector.baseline_stats = baseline_stats
                detector.last_trained = datetime.now(timezone.utc)

                # Evaluate performance (if labeled data available)
                if "is_anomaly" in training_data.columns:
                    performance = await self._evaluate_detector_performance(
                        model, scaled_data, training_data["is_anomaly"].values
                    )
                    detector.performance_metrics = performance

                await self._store_detector(detector)

                logger.info(f"Detector {detector_id} trained successfully")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to train detector {detector_id}: {e}")
            return False

    async def _train_model_by_algorithm(
        self, algorithm: AnomalyAlgorithm, data: np.ndarray, parameters: Dict[str, Any]
    ) -> Optional[Any]:
        """Train model based on algorithm"""
        try:
            if not HAS_SKLEARN:
                logger.warning("Scikit-learn not available, using statistical methods")
                return None

            if algorithm == AnomalyAlgorithm.ISOLATION_FOREST:
                model = IsolationForest(
                    contamination=parameters.get("contamination", 0.1),
                    random_state=42,
                    n_estimators=parameters.get("n_estimators", 100),
                )
                model.fit(data)

            elif algorithm == AnomalyAlgorithm.LOCAL_OUTLIER_FACTOR:
                model = LocalOutlierFactor(
                    contamination=parameters.get("contamination", 0.1),
                    n_neighbors=parameters.get("n_neighbors", 20),
                )
                model.fit(data)

            elif algorithm == AnomalyAlgorithm.ONE_CLASS_SVM:
                model = OneClassSVM(
                    nu=parameters.get("nu", 0.1),
                    kernel=parameters.get("kernel", "rbf"),
                    gamma=parameters.get("gamma", "scale"),
                )
                model.fit(data)

            elif algorithm == AnomalyAlgorithm.AUTOENCODER and HAS_TENSORFLOW:
                model = await self._train_autoencoder(data, parameters)

            elif algorithm == AnomalyAlgorithm.LSTM_AUTOENCODER and HAS_TENSORFLOW:
                model = await self._train_lstm_autoencoder(data, parameters)

            else:
                # Fallback to statistical methods
                model = None

            return model

        except Exception as e:
            logger.error(f"Failed to train {algorithm.value} model: {e}")
            return None

    async def _train_autoencoder(
        self, data: np.ndarray, parameters: Dict[str, Any]
    ) -> Optional[Any]:
        """Train autoencoder model"""
        try:
            input_dim = data.shape[1]
            encoding_dim = parameters.get("encoding_dim", 32)

            # Build autoencoder
            input_layer = Input(shape=(input_dim,))
            encoded = Dense(encoding_dim, activation="relu")(input_layer)
            encoded = Dense(int(encoding_dim / 2), activation="relu")(encoded)
            decoded = Dense(encoding_dim, activation="relu")(encoded)
            decoded = Dense(input_dim, activation="sigmoid")(decoded)

            autoencoder = Model(input_layer, decoded)
            autoencoder.compile(optimizer="adam", loss="mse")

            # Train
            autoencoder.fit(
                data,
                data,
                epochs=parameters.get("epochs", 50),
                batch_size=parameters.get("batch_size", 32),
                verbose=0,
            )

            return autoencoder

        except Exception as e:
            logger.error(f"Failed to train autoencoder: {e}")
            return None

    async def _train_lstm_autoencoder(
        self, data: np.ndarray, parameters: Dict[str, Any]
    ) -> Optional[Any]:
        """Train LSTM autoencoder model"""
        try:
            # Reshape for LSTM (assuming time series data)
            sequence_length = parameters.get("sequence_length", 10)
            if len(data) < sequence_length:
                return None

            # Create sequences
            sequences = []
            for i in range(len(data) - sequence_length + 1):
                sequences.append(data[i : i + sequence_length])
            sequences = np.array(sequences)

            # Build LSTM autoencoder
            model = Sequential(
                [
                    LSTM(
                        64,
                        activation="relu",
                        input_shape=(sequence_length, data.shape[1]),
                        return_sequences=True,
                    ),
                    LSTM(32, activation="relu", return_sequences=False),
                    RepeatVector(sequence_length),
                    LSTM(32, activation="relu", return_sequences=True),
                    LSTM(64, activation="relu", return_sequences=True),
                    TimeDistributed(Dense(data.shape[1])),
                ]
            )

            model.compile(optimizer="adam", loss="mse")

            # Train
            model.fit(
                sequences,
                sequences,
                epochs=parameters.get("epochs", 50),
                batch_size=parameters.get("batch_size", 32),
                verbose=0,
            )

            return model

        except Exception as e:
            logger.error(f"Failed to train LSTM autoencoder: {e}")
            return None

    def _calculate_baseline_stats(self, data: np.ndarray) -> Dict[str, float]:
        """Calculate baseline statistics for anomaly detection"""
        try:
            return {
                "mean": float(np.mean(data)),
                "std": float(np.std(data)),
                "median": float(np.median(data)),
                "q25": float(np.percentile(data, 25)),
                "q75": float(np.percentile(data, 75)),
                "iqr": float(np.subtract(*np.percentile(data, [75, 25]))),
                "min": float(np.min(data)),
                "max": float(np.max(data)),
            }
        except Exception as e:
            logger.error(f"Failed to calculate baseline stats: {e}")
            return {}

    async def _evaluate_detector_performance(
        self, model: Any, data: np.ndarray, labels: np.ndarray
    ) -> Dict[str, float]:
        """Evaluate detector performance"""
        try:
            # Get predictions
            if hasattr(model, "predict"):
                predictions = model.predict(data)
                # Convert to binary labels (-1 for anomaly, 1 for normal)
                if hasattr(model, "negative_outlier_label_"):
                    # For algorithms that use -1 for anomalies
                    predictions = (predictions == model.negative_outlier_label_).astype(
                        int
                    )
                else:
                    predictions = (predictions == -1).astype(int)
            else:
                predictions = np.zeros(len(data))  # Default to normal

            # Calculate metrics
            report = classification_report(
                labels, predictions, output_dict=True, zero_division=0
            )

            return {
                "accuracy": report.get("accuracy", 0),
                "precision": report.get("weighted avg", {}).get("precision", 0),
                "recall": report.get("weighted avg", {}).get("recall", 0),
                "f1_score": report.get("weighted avg", {}).get("f1-score", 0),
            }

        except Exception as e:
            logger.error(f"Failed to evaluate detector performance: {e}")
            return {}

    async def detect_anomalies(
        self, detector_id: str, data_point: float, context: Dict[str, Any] = None
    ) -> Optional[Anomaly]:
        """Detect anomalies in real-time data"""
        try:
            if detector_id not in self.detectors:
                logger.error(f"Detector {detector_id} not found")
                return None

            detector = self.detectors[detector_id]

            if not detector.model and not detector.baseline_stats:
                logger.warning(f"Detector {detector_id} not trained")
                return None

            # Prepare data
            data = np.array([[data_point]])

            # Scale data
            if detector.scaler:
                scaled_data = detector.scaler.transform(data)
            else:
                scaled_data = data

            # Detect anomaly
            is_anomaly, score, expected_value = await self._detect_anomaly_by_algorithm(
                detector, scaled_data, data_point
            )

            if is_anomaly:
                # Calculate severity
                severity = self._calculate_anomaly_severity(
                    score, detector.baseline_stats
                )

                # Create anomaly
                anomaly_id = f"anomaly_{uuid.uuid4().hex}"
                anomaly = Anomaly(
                    anomaly_id=anomaly_id,
                    detector_id=detector_id,
                    timestamp=datetime.now(timezone.utc),
                    value=data_point,
                    expected_value=expected_value,
                    deviation=abs(
                        data_point
                        - (
                            expected_value
                            or detector.baseline_stats.get("mean", data_point)
                        )
                    ),
                    severity=severity,
                    confidence=score,
                    context=context or {},
                    description=self._generate_anomaly_description(
                        detector, data_point, expected_value, severity
                    ),
                )

                # Store anomaly
                await self._store_anomaly(anomaly)

                # Create alert
                await self._create_anomaly_alert(anomaly)

                logger.info(
                    f"Anomaly detected by {detector_id}: value={data_point}, severity={severity.value}"
                )
                return anomaly

            return None

        except Exception as e:
            logger.error(f"Failed to detect anomalies for {detector_id}: {e}")
            return None

    async def _detect_anomaly_by_algorithm(
        self, detector: AnomalyDetector, scaled_data: np.ndarray, original_value: float
    ) -> Tuple[bool, float, Optional[float]]:
        """Detect anomaly based on algorithm"""
        try:
            expected_value = detector.baseline_stats.get("mean")

            if detector.algorithm in [
                AnomalyAlgorithm.ISOLATION_FOREST,
                AnomalyAlgorithm.ONE_CLASS_SVM,
            ]:
                if detector.model:
                    score = detector.model.decision_function(scaled_data)[0]
                    prediction = detector.model.predict(scaled_data)[0]

                    # Convert score to confidence (higher score = more anomalous)
                    confidence = (
                        (score - detector.model.offset_) / (1 - detector.model.offset_)
                        if hasattr(detector.model, "offset_")
                        else abs(score)
                    )
                    is_anomaly = prediction == -1

                    return is_anomaly, min(confidence, 1.0), expected_value

            elif detector.algorithm == AnomalyAlgorithm.LOCAL_OUTLIER_FACTOR:
                if detector.model:
                    # LOF doesn't have decision_function, use negative_outlier_factor_
                    scores = detector.model.negative_outlier_factor_
                    if len(scores) > 0:
                        score = scores[0]
                        is_anomaly = detector.model.predict(scaled_data)[0] == -1
                        confidence = min(abs(score), 1.0)
                        return is_anomaly, confidence, expected_value

            elif detector.algorithm == AnomalyAlgorithm.AUTOENCODER and HAS_TENSORFLOW:
                if detector.model:
                    reconstructed = detector.model.predict(scaled_data)
                    mse = np.mean(np.square(scaled_data - reconstructed))
                    threshold = detector.parameters.get("threshold", 0.1)
                    is_anomaly = mse > threshold
                    confidence = min(mse / (threshold * 2), 1.0)
                    return is_anomaly, confidence, expected_value

            elif detector.algorithm == AnomalyAlgorithm.STATISTICAL:
                return self._statistical_anomaly_detection(
                    original_value, detector.baseline_stats, detector.parameters
                )

            elif detector.algorithm == AnomalyAlgorithm.Z_SCORE:
                return self._z_score_anomaly_detection(
                    original_value, detector.baseline_stats, detector.parameters
                )

            elif detector.algorithm == AnomalyAlgorithm.IQR:
                return self._iqr_anomaly_detection(
                    original_value, detector.baseline_stats, detector.parameters
                )

            elif detector.algorithm == AnomalyAlgorithm.MAD:
                return self._mad_anomaly_detection(
                    original_value, detector.baseline_stats, detector.parameters
                )

            # Default: no anomaly
            return False, 0.0, expected_value

        except Exception as e:
            logger.error(f"Failed to detect anomaly: {e}")
            return False, 0.0, None

    def _statistical_anomaly_detection(
        self, value: float, baseline: Dict[str, float], parameters: Dict[str, Any]
    ) -> Tuple[bool, float, Optional[float]]:
        """Statistical anomaly detection using baseline statistics"""
        try:
            mean = baseline.get("mean", value)
            std = baseline.get("std", 1.0)
            threshold = parameters.get("threshold", 3.0)  # 3-sigma rule

            z_score = abs(value - mean) / std
            is_anomaly = z_score > threshold
            confidence = min(z_score / (threshold * 2), 1.0)

            return is_anomaly, confidence, mean

        except Exception:
            return False, 0.0, None

    def _z_score_anomaly_detection(
        self, value: float, baseline: Dict[str, float], parameters: Dict[str, Any]
    ) -> Tuple[bool, float, Optional[float]]:
        """Z-score based anomaly detection"""
        return self._statistical_anomaly_detection(value, baseline, parameters)

    def _iqr_anomaly_detection(
        self, value: float, baseline: Dict[str, float], parameters: Dict[str, Any]
    ) -> Tuple[bool, float, Optional[float]]:
        """IQR-based anomaly detection"""
        try:
            q25 = baseline.get("q25", value)
            q75 = baseline.get("q75", value)
            iqr = baseline.get("iqr", 1.0)
            multiplier = parameters.get("multiplier", 1.5)

            lower_bound = q25 - multiplier * iqr
            upper_bound = q75 + multiplier * iqr

            is_anomaly = value < lower_bound or value > upper_bound
            expected_value = (q25 + q75) / 2

            if is_anomaly:
                if value < lower_bound:
                    deviation = lower_bound - value
                else:
                    deviation = value - upper_bound
                confidence = min(deviation / (multiplier * iqr * 2), 1.0)
            else:
                confidence = 0.0

            return is_anomaly, confidence, expected_value

        except Exception:
            return False, 0.0, None

    def _mad_anomaly_detection(
        self, value: float, baseline: Dict[str, float], parameters: Dict[str, Any]
    ) -> Tuple[bool, float, Optional[float]]:
        """Median Absolute Deviation based anomaly detection"""
        try:
            median = baseline.get("median", value)
            mad = parameters.get(
                "mad", 1.0
            )  # Would need to be calculated from training data
            threshold = parameters.get("threshold", 3.0)

            mad_score = abs(value - median) / mad
            is_anomaly = mad_score > threshold
            confidence = min(mad_score / (threshold * 2), 1.0)

            return is_anomaly, confidence, median

        except Exception:
            return False, 0.0, None

    def _calculate_anomaly_severity(
        self, confidence: float, baseline: Dict[str, float]
    ) -> AnomalySeverity:
        """Calculate anomaly severity based on confidence"""
        try:
            for severity, threshold in self.alert_thresholds.items():
                if confidence >= threshold:
                    return severity
            return AnomalySeverity.LOW

        except Exception:
            return AnomalySeverity.LOW

    def _generate_anomaly_description(
        self,
        detector: AnomalyDetector,
        value: float,
        expected: Optional[float],
        severity: AnomalySeverity,
    ) -> str:
        """Generate human-readable anomaly description"""
        try:
            expected_str = f" (expected: {expected:.2f})" if expected else ""
            return f"Anomaly detected in {detector.target_metric}: value {value:.2f}{expected_str}, severity: {severity.value}"

        except Exception:
            return f"Anomaly detected in {detector.target_metric}"

    async def _create_anomaly_alert(self, anomaly: Anomaly):
        """Create an alert for detected anomaly"""
        try:
            alert_id = f"alert_{uuid.uuid4().hex}"

            alert = AnomalyAlert(
                alert_id=alert_id,
                anomaly_id=anomaly.anomaly_id,
                detector_id=anomaly.detector_id,
                title=f"Anomaly Alert: {anomaly.description}",
                description=anomaly.description,
                severity=anomaly.severity,
                status=AlertStatus.ACTIVE,
            )

            # Store alert
            await self._store_anomaly_alert(alert)

            # Send notifications
            await self._send_anomaly_notifications(alert)

            logger.info(f"Anomaly alert created: {alert_id}")

        except Exception as e:
            logger.error(f"Failed to create anomaly alert: {e}")

    async def _send_anomaly_notifications(self, alert: AnomalyAlert):
        """Send notifications for anomaly alert"""
        try:
            # This would integrate with notification systems
            # For now, just log the alert
            logger.warning(f"ANOMALY ALERT: {alert.title} - {alert.description}")

            # Mark channels as notified
            alert.notified_channels = ["log"]

            # Update alert
            await self._store_anomaly_alert(alert)

        except Exception as e:
            logger.error(f"Failed to send anomaly notifications: {e}")

    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge an anomaly alert"""
        try:
            async with self.db_engine.begin() as conn:
                await conn.execute(
                    text(
                        """
                    UPDATE anomaly_alerts
                    SET status = 'acknowledged', acknowledged_by = $1, acknowledged_at = NOW()
                    WHERE alert_id = $2
                """
                    ),
                    (user_id, alert_id),
                )

            logger.info(f"Alert {alert_id} acknowledged by {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to acknowledge alert {alert_id}: {e}")
            return False

    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an anomaly alert"""
        try:
            async with self.db_engine.begin() as conn:
                await conn.execute(
                    text(
                        """
                    UPDATE anomaly_alerts
                    SET status = 'resolved', resolved_at = NOW()
                    WHERE alert_id = $2
                """
                    ),
                    (alert_id,),
                )

            logger.info(f"Alert {alert_id} resolved")
            return True

        except Exception as e:
            logger.error(f"Failed to resolve alert {alert_id}: {e}")
            return False

    async def start_monitoring(
        self, detector_id: str, data_source: Callable, interval_seconds: int = 60
    ) -> bool:
        """Start real-time monitoring for a detector"""
        try:
            if detector_id not in self.detectors:
                logger.error(f"Detector {detector_id} not found")
                return False

            if detector_id in self.monitoring_tasks:
                logger.warning(f"Monitoring already active for {detector_id}")
                return True

            # Create monitoring task
            task = asyncio.create_task(
                self._monitor_data_source(detector_id, data_source, interval_seconds)
            )

            self.monitoring_tasks[detector_id] = task

            logger.info(f"Started monitoring for detector {detector_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to start monitoring for {detector_id}: {e}")
            return False

    async def stop_monitoring(self, detector_id: str) -> bool:
        """Stop monitoring for a detector"""
        try:
            if detector_id in self.monitoring_tasks:
                task = self.monitoring_tasks[detector_id]
                task.cancel()

                try:
                    await task
                except asyncio.CancelledError:
                    pass

                del self.monitoring_tasks[detector_id]

                logger.info(f"Stopped monitoring for detector {detector_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to stop monitoring for {detector_id}: {e}")
            return False

    async def _monitor_data_source(
        self, detector_id: str, data_source: Callable, interval: int
    ):
        """Monitor data source for anomalies"""
        try:
            while True:
                try:
                    # Get current data point
                    data_point = await data_source()

                    if data_point is not None:
                        # Detect anomalies
                        anomaly = await self.detect_anomalies(detector_id, data_point)

                        if anomaly:
                            logger.info(
                                f"Anomaly detected in monitoring: {anomaly.description}"
                            )

                    # Wait for next interval
                    await asyncio.sleep(interval)

                except Exception as e:
                    logger.error(f"Error in monitoring loop for {detector_id}: {e}")
                    await asyncio.sleep(interval)

        except asyncio.CancelledError:
            logger.info(f"Monitoring cancelled for {detector_id}")
            raise

    async def get_anomaly_stats(
        self, detector_id: Optional[str] = None, hours: int = 24
    ) -> Dict[str, Any]:
        """Get anomaly detection statistics"""
        try:
            async with self.db_engine.begin() as conn:
                query = (
                    """
                    SELECT
                        detector_id,
                        COUNT(*) as total_anomalies,
                        COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical_anomalies,
                        COUNT(CASE WHEN severity = 'high' THEN 1 END) as high_anomalies,
                        COUNT(CASE WHEN severity = 'medium' THEN 1 END) as medium_anomalies,
                        COUNT(CASE WHEN severity = 'low' THEN 1 END) as low_anomalies,
                        AVG(confidence) as avg_confidence,
                        MAX(timestamp) as last_anomaly
                    FROM anomalies
                    WHERE timestamp >= NOW() - INTERVAL '%s hours'
                """
                    % hours
                )

                if detector_id:
                    query += f" AND detector_id = '{detector_id}'"

                query += " GROUP BY detector_id"

                result = await conn.execute(text(query))
                rows = result.fetchall()

                stats = {}
                for row in rows:
                    stats[row[0]] = {
                        "total_anomalies": row[1],
                        "critical_anomalies": row[2],
                        "high_anomalies": row[3],
                        "medium_anomalies": row[4],
                        "low_anomalies": row[5],
                        "avg_confidence": float(row[6]) if row[6] else 0,
                        "last_anomaly": row[7].isoformat() if row[7] else None,
                    }

                return stats

        except Exception as e:
            logger.error(f"Failed to get anomaly stats: {e}")
            return {}

    async def _store_detector(self, detector: AnomalyDetector):
        """Store detector in database"""
        try:
            async with self.db_engine.begin() as conn:
                await conn.execute(
                    text(
                        """
                    INSERT INTO anomaly_detectors
                    (detector_id, name, algorithm, target_metric, parameters,
                     baseline_stats, is_active, performance_metrics, last_trained)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT (detector_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        algorithm = EXCLUDED.algorithm,
                        target_metric = EXCLUDED.target_metric,
                        parameters = EXCLUDED.parameters,
                        baseline_stats = EXCLUDED.baseline_stats,
                        is_active = EXCLUDED.is_active,
                        performance_metrics = EXCLUDED.performance_metrics,
                        last_trained = EXCLUDED.last_trained
                """
                    ),
                    (
                        detector.detector_id,
                        detector.name,
                        detector.algorithm.value,
                        detector.target_metric,
                        json.dumps(detector.parameters),
                        json.dumps(detector.baseline_stats),
                        detector.is_active,
                        json.dumps(detector.performance_metrics),
                        detector.last_trained,
                    ),
                )

        except Exception as e:
            logger.error(f"Failed to store detector: {e}")

    async def _store_anomaly(self, anomaly: Anomaly):
        """Store anomaly in database"""
        try:
            async with self.db_engine.begin() as conn:
                await conn.execute(
                    text(
                        """
                    INSERT INTO anomalies
                    (anomaly_id, detector_id, timestamp, value, expected_value,
                     deviation, severity, confidence, context, description, status)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """
                    ),
                    (
                        anomaly.anomaly_id,
                        anomaly.detector_id,
                        anomaly.timestamp,
                        anomaly.value,
                        anomaly.expected_value,
                        anomaly.deviation,
                        anomaly.severity.value,
                        anomaly.confidence,
                        json.dumps(anomaly.context),
                        anomaly.description,
                        anomaly.status.value,
                    ),
                )

        except Exception as e:
            logger.error(f"Failed to store anomaly: {e}")

    async def _store_anomaly_alert(self, alert: AnomalyAlert):
        """Store anomaly alert in database"""
        try:
            async with self.db_engine.begin() as conn:
                await conn.execute(
                    text(
                        """
                    INSERT INTO anomaly_alerts
                    (alert_id, anomaly_id, detector_id, title, description, severity,
                     status, notified_channels, acknowledged_by, acknowledged_at, resolved_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    ON CONFLICT (alert_id) DO UPDATE SET
                        status = EXCLUDED.status,
                        notified_channels = EXCLUDED.notified_channels,
                        acknowledged_by = EXCLUDED.acknowledged_by,
                        acknowledged_at = EXCLUDED.acknowledged_at,
                        resolved_at = EXCLUDED.resolved_at
                """
                    ),
                    (
                        alert.alert_id,
                        alert.anomaly_id,
                        alert.detector_id,
                        alert.title,
                        alert.description,
                        alert.severity.value,
                        alert.status.value,
                        json.dumps(alert.notified_channels),
                        alert.acknowledged_by,
                        alert.acknowledged_at,
                        alert.resolved_at,
                    ),
                )

        except Exception as e:
            logger.error(f"Failed to store anomaly alert: {e}")


# Global automated anomaly detection system instance
anomaly_detection_system = AutomatedAnomalyDetectionSystem()
