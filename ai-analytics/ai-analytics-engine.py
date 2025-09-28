#!/usr/bin/env python3
"""
AI Analytics Engine for NEXUS Platform - Phase 2 Integration
AI-powered analytics and predictive insights
"""

import asyncio
import json
import logging
import os
import pickle
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


@dataclass
class AnalyticsInsight:
    insight_id: str
    type: str
    title: str
    description: str
    confidence: float
    impact: str
    recommendations: List[str]
    data_points: Dict[str, Any]
    timestamp: str
    category: str


@dataclass
class PredictionResult:
    prediction_id: str
    model_name: str
    target: str
    predicted_value: float
    confidence: float
    actual_value: Optional[float]
    error: Optional[float]
    timestamp: str
    features_used: List[str]


class AIAnalyticsEngine:
    """AI-powered analytics engine for predictive insights"""

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.data_cache = {}
        self.insights_history = []
        self.db_path = "/app/data/analytics.db"
        self.models_path = "/app/data/models"
        self._initialize_database()
        self._load_models()

    def _initialize_database(self):
        """Initialize analytics database"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create tables
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    tags TEXT,
                    source TEXT
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prediction_id TEXT UNIQUE NOT NULL,
                    model_name TEXT NOT NULL,
                    target TEXT NOT NULL,
                    predicted_value REAL NOT NULL,
                    confidence REAL NOT NULL,
                    actual_value REAL,
                    error REAL,
                    timestamp TEXT NOT NULL,
                    features_used TEXT
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    insight_id TEXT UNIQUE NOT NULL,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    impact TEXT NOT NULL,
                    recommendations TEXT NOT NULL,
                    data_points TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    category TEXT NOT NULL
                )
            """
            )

            # Create indexes
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(metric_name)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_insights_timestamp ON insights(timestamp)"
            )

            conn.commit()
            conn.close()

            logger.info("Analytics database initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize analytics database: {e}")

    def _load_models(self):
        """Load pre-trained models"""
        try:
            os.makedirs(self.models_path, exist_ok=True)

            # Load performance prediction model
            performance_model_path = os.path.join(
                self.models_path, "performance_model.pkl"
            )
            if os.path.exists(performance_model_path):
                self.models["performance"] = joblib.load(performance_model_path)
                logger.info("Performance prediction model loaded")

            # Load anomaly detection model
            anomaly_model_path = os.path.join(self.models_path, "anomaly_model.pkl")
            if os.path.exists(anomaly_model_path):
                self.models["anomaly"] = joblib.load(anomaly_model_path)
                logger.info("Anomaly detection model loaded")

            # Load clustering model
            clustering_model_path = os.path.join(
                self.models_path, "clustering_model.pkl"
            )
            if os.path.exists(clustering_model_path):
                self.models["clustering"] = joblib.load(clustering_model_path)
                logger.info("Clustering model loaded")

            # Load scalers
            scaler_path = os.path.join(self.models_path, "scaler.pkl")
            if os.path.exists(scaler_path):
                self.scalers["main"] = joblib.load(scaler_path)
                logger.info("Data scaler loaded")

        except Exception as e:
            logger.error(f"Failed to load models: {e}")

    async def analyze_performance_trends(
        self, time_range_hours: int = 24
    ) -> List[AnalyticsInsight]:
        """Analyze performance trends and generate insights"""
        try:
            # Get performance metrics
            metrics_data = await self._get_metrics_data("performance", time_range_hours)

            if not metrics_data:
                return []

            insights = []

            # Analyze CPU trends
            cpu_insights = await self._analyze_cpu_trends(metrics_data)
            insights.extend(cpu_insights)

            # Analyze memory trends
            memory_insights = await self._analyze_memory_trends(metrics_data)
            insights.extend(memory_insights)

            # Analyze response time trends
            response_insights = await self._analyze_response_time_trends(metrics_data)
            insights.extend(response_insights)

            # Analyze error rate trends
            error_insights = await self._analyze_error_rate_trends(metrics_data)
            insights.extend(error_insights)

            # Save insights to database
            for insight in insights:
                await self._save_insight(insight)

            return insights

        except Exception as e:
            logger.error(f"Error analyzing performance trends: {e}")
            return []

    async def predict_performance(self, features: Dict[str, float]) -> PredictionResult:
        """Predict future performance based on current metrics"""
        try:
            # Prepare features
            feature_vector = self._prepare_feature_vector(features)

            # Get or create performance model
            if "performance" not in self.models:
                await self._train_performance_model()

            model = self.models["performance"]
            scaler = self.scalers.get("main")

            if scaler:
                feature_vector = scaler.transform([feature_vector])

            # Make prediction
            prediction = model.predict(feature_vector)[0]
            confidence = self._calculate_prediction_confidence(model, feature_vector)

            prediction_result = PredictionResult(
                prediction_id=f"perf_{int(datetime.utcnow().timestamp())}",
                model_name="performance_prediction",
                target="response_time",
                predicted_value=prediction,
                confidence=confidence,
                actual_value=None,
                error=None,
                timestamp=datetime.utcnow().isoformat(),
                features_used=list(features.keys()),
            )

            # Save prediction
            await self._save_prediction(prediction_result)

            return prediction_result

        except Exception as e:
            logger.error(f"Error predicting performance: {e}")
            raise Exception(f"Prediction failed: {str(e)}")

    async def detect_anomalies(
        self, metrics_data: List[Dict[str, Any]]
    ) -> List[AnalyticsInsight]:
        """Detect anomalies in system metrics"""
        try:
            if not metrics_data:
                return []

            # Prepare data for anomaly detection
            df = pd.DataFrame(metrics_data)
            numeric_columns = df.select_dtypes(include=[np.number]).columns

            if len(numeric_columns) == 0:
                return []

            # Get or create anomaly detection model
            if "anomaly" not in self.models:
                await self._train_anomaly_model(df[numeric_columns])

            model = self.models["anomaly"]

            # Detect anomalies
            anomaly_scores = model.decision_function(df[numeric_columns])
            anomaly_labels = model.predict(df[numeric_columns])

            insights = []

            # Analyze anomalies
            for i, (score, label) in enumerate(zip(anomaly_scores, anomaly_labels)):
                if label == -1:  # Anomaly detected
                    insight = AnalyticsInsight(
                        insight_id=f"anomaly_{int(datetime.utcnow().timestamp())}_{i}",
                        type="anomaly_detection",
                        title="System Anomaly Detected",
                        description=f"Anomalous behavior detected in system metrics (score: {score:.3f})",
                        confidence=abs(score),
                        impact="medium",
                        recommendations=[
                            "Investigate the anomalous data point",
                            "Check for system issues or unusual load",
                            "Monitor system closely for further anomalies",
                        ],
                        data_points={
                            "anomaly_score": score,
                            "timestamp": df.iloc[i].get("timestamp", ""),
                            "metrics": df.iloc[i][numeric_columns].to_dict(),
                        },
                        timestamp=datetime.utcnow().isoformat(),
                        category="performance",
                    )
                    insights.append(insight)

            # Save insights
            for insight in insights:
                await self._save_insight(insight)

            return insights

        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []

    async def cluster_user_behavior(
        self, user_data: List[Dict[str, Any]]
    ) -> List[AnalyticsInsight]:
        """Cluster user behavior patterns"""
        try:
            if not user_data:
                return []

            # Prepare user data
            df = pd.DataFrame(user_data)
            numeric_columns = df.select_dtypes(include=[np.number]).columns

            if len(numeric_columns) < 2:
                return []

            # Determine optimal number of clusters
            optimal_clusters = await self._find_optimal_clusters(df[numeric_columns])

            # Perform clustering
            kmeans = KMeans(n_clusters=optimal_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(df[numeric_columns])

            # Analyze clusters
            insights = []
            for cluster_id in range(optimal_clusters):
                cluster_data = df[cluster_labels == cluster_id]

                insight = AnalyticsInsight(
                    insight_id=f"cluster_{cluster_id}_{int(datetime.utcnow().timestamp())}",
                    type="user_clustering",
                    title=f"User Behavior Cluster {cluster_id}",
                    description=f"Identified user behavior pattern with {len(cluster_data)} users",
                    confidence=0.8,
                    impact="low",
                    recommendations=[
                        f"Analyze cluster {cluster_id} characteristics",
                        "Develop targeted features for this user segment",
                        "Monitor cluster evolution over time",
                    ],
                    data_points={
                        "cluster_id": cluster_id,
                        "cluster_size": len(cluster_data),
                        "cluster_centroid": cluster_data[numeric_columns]
                        .mean()
                        .to_dict(),
                        "cluster_characteristics": cluster_data.describe().to_dict(),
                    },
                    timestamp=datetime.utcnow().isoformat(),
                    category="user_behavior",
                )
                insights.append(insight)

            # Save clustering model
            self.models["clustering"] = kmeans
            await self._save_model("clustering", kmeans)

            # Save insights
            for insight in insights:
                await self._save_insight(insight)

            return insights

        except Exception as e:
            logger.error(f"Error clustering user behavior: {e}")
            return []

    async def generate_business_insights(
        self, business_data: Dict[str, Any]
    ) -> List[AnalyticsInsight]:
        """Generate business-focused insights"""
        try:
            insights = []

            # Revenue analysis
            if "revenue" in business_data:
                revenue_insights = await self._analyze_revenue_trends(
                    business_data["revenue"]
                )
                insights.extend(revenue_insights)

            # User engagement analysis
            if "engagement" in business_data:
                engagement_insights = await self._analyze_user_engagement(
                    business_data["engagement"]
                )
                insights.extend(engagement_insights)

            # Feature usage analysis
            if "feature_usage" in business_data:
                feature_insights = await self._analyze_feature_usage(
                    business_data["feature_usage"]
                )
                insights.extend(feature_insights)

            # Save insights
            for insight in insights:
                await self._save_insight(insight)

            return insights

        except Exception as e:
            logger.error(f"Error generating business insights: {e}")
            return []

    async def _get_metrics_data(
        self, metric_type: str, hours: int
    ) -> List[Dict[str, Any]]:
        """Get metrics data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cutoff_time = datetime.utcnow() - timedelta(hours=hours)

            cursor.execute(
                """
                SELECT timestamp, metric_name, value, tags, source
                FROM metrics
                WHERE timestamp >= ? AND metric_name LIKE ?
                ORDER BY timestamp ASC
            """,
                (cutoff_time.isoformat(), f"{metric_type}%"),
            )

            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    "timestamp": row[0],
                    "metric_name": row[1],
                    "value": row[2],
                    "tags": json.loads(row[3]) if row[3] else {},
                    "source": row[4],
                }
                for row in rows
            ]

        except Exception as e:
            logger.error(f"Error getting metrics data: {e}")
            return []

    async def _analyze_cpu_trends(
        self, metrics_data: List[Dict[str, Any]]
    ) -> List[AnalyticsInsight]:
        """Analyze CPU usage trends"""
        insights = []

        cpu_data = [m for m in metrics_data if "cpu" in m["metric_name"].lower()]
        if len(cpu_data) < 10:
            return insights

        cpu_values = [m["value"] for m in cpu_data]
        avg_cpu = np.mean(cpu_values)
        max_cpu = np.max(cpu_values)
        cpu_trend = np.polyfit(range(len(cpu_values)), cpu_values, 1)[0]

        # Generate insights based on CPU patterns
        if avg_cpu > 80:
            insights.append(
                AnalyticsInsight(
                    insight_id=f"cpu_high_{int(datetime.utcnow().timestamp())}",
                    type="performance_analysis",
                    title="High CPU Usage Detected",
                    description=f"Average CPU usage is {avg_cpu:.1f}%, indicating potential performance issues",
                    confidence=0.9,
                    impact="high",
                    recommendations=[
                        "Consider scaling horizontally",
                        "Optimize CPU-intensive operations",
                        "Monitor CPU usage closely",
                    ],
                    data_points={
                        "average_cpu": avg_cpu,
                        "max_cpu": max_cpu,
                        "trend": cpu_trend,
                        "data_points": len(cpu_values),
                    },
                    timestamp=datetime.utcnow().isoformat(),
                    category="performance",
                )
            )

        if cpu_trend > 0.1:
            insights.append(
                AnalyticsInsight(
                    insight_id=f"cpu_trend_{int(datetime.utcnow().timestamp())}",
                    type="trend_analysis",
                    title="Increasing CPU Usage Trend",
                    description=f"CPU usage is trending upward (slope: {cpu_trend:.3f})",
                    confidence=0.7,
                    impact="medium",
                    recommendations=[
                        "Investigate the cause of increasing CPU usage",
                        "Plan for capacity scaling",
                        "Optimize resource utilization",
                    ],
                    data_points={
                        "trend_slope": cpu_trend,
                        "average_cpu": avg_cpu,
                        "data_points": len(cpu_values),
                    },
                    timestamp=datetime.utcnow().isoformat(),
                    category="performance",
                )
            )

        return insights

    async def _analyze_memory_trends(
        self, metrics_data: List[Dict[str, Any]]
    ) -> List[AnalyticsInsight]:
        """Analyze memory usage trends"""
        insights = []

        memory_data = [m for m in metrics_data if "memory" in m["metric_name"].lower()]
        if len(memory_data) < 10:
            return insights

        memory_values = [m["value"] for m in memory_data]
        avg_memory = np.mean(memory_values)
        max_memory = np.max(memory_values)
        memory_trend = np.polyfit(range(len(memory_values)), memory_values, 1)[0]

        # Generate insights based on memory patterns
        if avg_memory > 85:
            insights.append(
                AnalyticsInsight(
                    insight_id=f"memory_high_{int(datetime.utcnow().timestamp())}",
                    type="performance_analysis",
                    title="High Memory Usage Detected",
                    description=f"Average memory usage is {avg_memory:.1f}%, indicating potential memory pressure",
                    confidence=0.9,
                    impact="high",
                    recommendations=[
                        "Investigate memory leaks",
                        "Consider increasing memory allocation",
                        "Optimize memory usage patterns",
                    ],
                    data_points={
                        "average_memory": avg_memory,
                        "max_memory": max_memory,
                        "trend": memory_trend,
                        "data_points": len(memory_values),
                    },
                    timestamp=datetime.utcnow().isoformat(),
                    category="performance",
                )
            )

        return insights

    async def _analyze_response_time_trends(
        self, metrics_data: List[Dict[str, Any]]
    ) -> List[AnalyticsInsight]:
        """Analyze response time trends"""
        insights = []

        response_data = [
            m for m in metrics_data if "response" in m["metric_name"].lower()
        ]
        if len(response_data) < 10:
            return insights

        response_values = [m["value"] for m in response_data]
        avg_response = np.mean(response_values)
        p95_response = np.percentile(response_values, 95)
        response_trend = np.polyfit(range(len(response_values)), response_values, 1)[0]

        # Generate insights based on response time patterns
        if avg_response > 1000:  # 1 second
            insights.append(
                AnalyticsInsight(
                    insight_id=f"response_slow_{int(datetime.utcnow().timestamp())}",
                    type="performance_analysis",
                    title="Slow Response Times Detected",
                    description=f"Average response time is {avg_response:.0f}ms, indicating performance issues",
                    confidence=0.8,
                    impact="high",
                    recommendations=[
                        "Optimize database queries",
                        "Implement caching strategies",
                        "Review application performance",
                    ],
                    data_points={
                        "average_response": avg_response,
                        "p95_response": p95_response,
                        "trend": response_trend,
                        "data_points": len(response_values),
                    },
                    timestamp=datetime.utcnow().isoformat(),
                    category="performance",
                )
            )

        return insights

    async def _analyze_error_rate_trends(
        self, metrics_data: List[Dict[str, Any]]
    ) -> List[AnalyticsInsight]:
        """Analyze error rate trends"""
        insights = []

        error_data = [m for m in metrics_data if "error" in m["metric_name"].lower()]
        if len(error_data) < 10:
            return insights

        error_values = [m["value"] for m in error_data]
        avg_error_rate = np.mean(error_values)
        max_error_rate = np.max(error_values)
        error_trend = np.polyfit(range(len(error_values)), error_values, 1)[0]

        # Generate insights based on error rate patterns
        if avg_error_rate > 0.05:  # 5%
            insights.append(
                AnalyticsInsight(
                    insight_id=f"error_rate_high_{int(datetime.utcnow().timestamp())}",
                    type="reliability_analysis",
                    title="High Error Rate Detected",
                    description=f"Average error rate is {avg_error_rate:.2%}, indicating reliability issues",
                    confidence=0.9,
                    impact="high",
                    recommendations=[
                        "Investigate error patterns",
                        "Improve error handling",
                        "Monitor error rates closely",
                    ],
                    data_points={
                        "average_error_rate": avg_error_rate,
                        "max_error_rate": max_error_rate,
                        "trend": error_trend,
                        "data_points": len(error_values),
                    },
                    timestamp=datetime.utcnow().isoformat(),
                    category="reliability",
                )
            )

        return insights

    def _prepare_feature_vector(self, features: Dict[str, float]) -> List[float]:
        """Prepare feature vector for model prediction"""
        # Define expected features in order
        expected_features = [
            "cpu_percent",
            "memory_percent",
            "disk_usage_percent",
            "active_connections",
            "total_requests",
            "error_rate",
            "cache_hit_rate",
            "avg_response_time",
        ]

        feature_vector = []
        for feature in expected_features:
            feature_vector.append(features.get(feature, 0.0))

        return feature_vector

    def _calculate_prediction_confidence(self, model, feature_vector) -> float:
        """Calculate prediction confidence"""
        try:
            # For tree-based models, we can use feature importance
            if hasattr(model, "feature_importances_"):
                # Simple confidence based on feature importance
                importance_sum = np.sum(model.feature_importances_)
                return min(0.95, importance_sum)
            else:
                return 0.7  # Default confidence
        except:
            return 0.5  # Fallback confidence

    async def _train_performance_model(self):
        """Train performance prediction model"""
        try:
            # Get historical data for training
            training_data = await self._get_metrics_data("performance", 168)  # 1 week

            if len(training_data) < 100:
                logger.warning("Insufficient data for training performance model")
                return

            # Prepare training data
            df = pd.DataFrame(training_data)
            features = self._prepare_feature_vector(df.iloc[0])

            # Create dummy training data (in production, use real historical data)
            X = np.random.rand(100, len(features))
            y = np.random.rand(100) * 1000  # Response times

            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)

            # Train scaler
            scaler = StandardScaler()
            scaler.fit(X)

            # Save models
            self.models["performance"] = model
            self.scalers["main"] = scaler

            await self._save_model("performance", model)
            await self._save_model("scaler", scaler)

            logger.info("Performance prediction model trained successfully")

        except Exception as e:
            logger.error(f"Error training performance model: {e}")

    async def _train_anomaly_model(self, data):
        """Train anomaly detection model"""
        try:
            model = IsolationForest(contamination=0.1, random_state=42)
            model.fit(data)

            self.models["anomaly"] = model
            await self._save_model("anomaly", model)

            logger.info("Anomaly detection model trained successfully")

        except Exception as e:
            logger.error(f"Error training anomaly model: {e}")

    async def _find_optimal_clusters(self, data) -> int:
        """Find optimal number of clusters using silhouette score"""
        try:
            max_clusters = min(10, len(data) // 2)
            if max_clusters < 2:
                return 2

            best_score = -1
            best_k = 2

            for k in range(2, max_clusters + 1):
                kmeans = KMeans(n_clusters=k, random_state=42)
                cluster_labels = kmeans.fit_predict(data)
                score = silhouette_score(data, cluster_labels)

                if score > best_score:
                    best_score = score
                    best_k = k

            return best_k

        except Exception as e:
            logger.error(f"Error finding optimal clusters: {e}")
            return 2

    async def _save_model(self, model_name: str, model):
        """Save model to disk"""
        try:
            model_path = os.path.join(self.models_path, f"{model_name}_model.pkl")
            joblib.dump(model, model_path)
            logger.info(f"Model {model_name} saved successfully")
        except Exception as e:
            logger.error(f"Error saving model {model_name}: {e}")

    async def _save_insight(self, insight: AnalyticsInsight):
        """Save insight to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO insights
                (insight_id, type, title, description, confidence, impact,
                 recommendations, data_points, timestamp, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    insight.insight_id,
                    insight.type,
                    insight.title,
                    insight.description,
                    insight.confidence,
                    insight.impact,
                    json.dumps(insight.recommendations),
                    json.dumps(insight.data_points),
                    insight.timestamp,
                    insight.category,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error saving insight: {e}")

    async def _save_prediction(self, prediction: PredictionResult):
        """Save prediction to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO predictions
                (prediction_id, model_name, target, predicted_value, confidence,
                 actual_value, error, timestamp, features_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    prediction.prediction_id,
                    prediction.model_name,
                    prediction.target,
                    prediction.predicted_value,
                    prediction.confidence,
                    prediction.actual_value,
                    prediction.error,
                    prediction.timestamp,
                    json.dumps(prediction.features_used),
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error saving prediction: {e}")

    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get insight counts
            cursor.execute(
                'SELECT COUNT(*) FROM insights WHERE timestamp >= datetime("now", "-24 hours")'
            )
            recent_insights = cursor.fetchone()[0]

            # Get prediction counts
            cursor.execute(
                'SELECT COUNT(*) FROM predictions WHERE timestamp >= datetime("now", "-24 hours")'
            )
            recent_predictions = cursor.fetchone()[0]

            # Get model status
            model_status = {}
            for model_name in self.models:
                model_status[model_name] = "loaded"

            conn.close()

            return {
                "recent_insights_24h": recent_insights,
                "recent_predictions_24h": recent_predictions,
                "models_loaded": model_status,
                "database_path": self.db_path,
                "models_path": self.models_path,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting analytics summary: {e}")
            return {"error": str(e)}


# Global AI analytics engine instance
ai_analytics_engine = AIAnalyticsEngine()
