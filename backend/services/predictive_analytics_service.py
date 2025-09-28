#!/usr/bin/env python3
"""
NEXUS Platform - Predictive Analytics Service
AI-powered financial insights and predictive modeling
"""

import logging
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from database.database import get_db
from database.schema_normalization import Transaction, Account, User
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class PredictiveAnalyticsError(Exception):
    """Base exception for predictive analytics errors"""
    pass


class InsufficientDataError(PredictiveAnalyticsError):
    """Raised when insufficient data is available for analysis"""
    pass


class ModelTrainingError(PredictiveAnalyticsError):
    """Raised when ML model training fails"""
    pass


class DataValidationError(PredictiveAnalyticsError):
    """Raised when input data validation fails"""
    pass


class PerformanceMonitor:
    """Simple performance monitoring for predictive analytics operations"""

    def __init__(self):
        self.metrics = {}

    def start_operation(self, operation_name: str) -> str:
        """Start timing an operation"""
        operation_id = f"{operation_name}_{time.time()}"
        self.metrics[operation_id] = {
            'operation': operation_name,
            'start_time': time.time(),
            'status': 'running'
        }
        return operation_id

    def end_operation(self, operation_id: str, success: bool = True, error: str = None):
        """End timing an operation"""
        if operation_id in self.metrics:
            self.metrics[operation_id].update({
                'end_time': time.time(),
                'duration': time.time() - self.metrics[operation_id]['start_time'],
                'status': 'completed' if success else 'failed',
                'error': error
            })

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.metrics.copy()


# Global performance monitor
performance_monitor = PerformanceMonitor()


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TrendDirection(Enum):
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"


@dataclass
class TransactionPattern:
    """Transaction pattern analysis result"""
    category: str
    frequency: float  # transactions per week
    average_amount: float
    trend: TrendDirection
    seasonality_score: float
    anomaly_score: float
    confidence: float


@dataclass
class FinancialHealthScore:
    """Financial health assessment result"""
    overall_score: float  # 0-100
    component_scores: Dict[str, float]
    risk_level: RiskLevel
    recommendations: List[str]
    insights: List[str]
    confidence: float


@dataclass
class PredictiveInsight:
    """AI-generated predictive insight"""
    insight_id: str
    title: str
    description: str
    type: str  # 'warning', 'info', 'success', 'error'
    priority: str  # 'low', 'medium', 'high'
    confidence: float
    predicted_impact: Dict[str, Any]
    recommended_actions: List[str]


class PredictiveAnalyticsService:
    """AI-powered predictive analytics for financial data"""

    def __init__(self):
        self.transaction_classifier = None
        self.anomaly_detector = None
        self.scaler = StandardScaler()

        # Caching for expensive operations
        self._cache = {}
        self._cache_ttl = 3600  # 1 hour cache TTL

        self._load_models()

    def _get_cache_key(self, operation: str, user_id: str, **kwargs) -> str:
        """Generate cache key for operation"""
        params = "_".join(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        return f"{operation}_{user_id}_{params}"

    def _get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Get result from cache if valid"""
        if cache_key in self._cache:
            cached_item = self._cache[cache_key]
            if time.time() - cached_item['timestamp'] < self._cache_ttl:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_item['data']
            else:
                # Expired, remove from cache
                del self._cache[cache_key]
        return None

    def _set_cached_result(self, cache_key: str, data: Any):
        """Store result in cache"""
        self._cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }
        logger.debug(f"Cached result for {cache_key}")

    def clear_cache(self, user_id: Optional[str] = None):
        """Clear cache, optionally for specific user"""
        if user_id:
            keys_to_remove = [k for k in self._cache.keys() if user_id in k]
            for key in keys_to_remove:
                del self._cache[key]
            logger.info(f"Cleared cache for user {user_id}: {len(keys_to_remove)} entries")
        else:
            cache_size = len(self._cache)
            self._cache.clear()
            logger.info(f"Cleared entire cache: {cache_size} entries")

    def _load_models(self):
        """Load or initialize ML models"""
        try:
            # Initialize models with default parameters
            self.transaction_classifier = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=10
            )

            self.anomaly_detector = IsolationForest(
                contamination=0.1,
                random_state=42
            )

            logger.info("Predictive analytics models initialized")
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {e}")
            raise

    async def analyze_transaction_patterns(
        self,
        user_id: str,
        db: Session,
        days: int = 90
    ) -> Dict[str, Any]:
        """Analyze user's transaction patterns using AI"""
        operation_id = performance_monitor.start_operation("analyze_transaction_patterns")

        try:
            logger.info(f"Starting transaction pattern analysis for user {user_id}, period: {days} days")

            # Check cache first
            cache_key = self._get_cache_key("transaction_patterns", user_id, days=days)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                logger.info(f"Returning cached transaction pattern analysis for user {user_id}")
                performance_monitor.end_operation(operation_id, success=True)
                return cached_result

            # Validate inputs
            if not user_id or not isinstance(user_id, str):
                raise DataValidationError("Invalid user_id provided")
            if not isinstance(days, int) or days < 30 or days > 365:
                raise DataValidationError("Days must be an integer between 30 and 365")

            # Get transaction data
            transactions = await self._get_user_transactions(user_id, db, days)
            logger.info(f"Retrieved {len(transactions)} transactions for user {user_id}")

            if len(transactions) < 10:
                logger.warning(f"Insufficient transaction data for user {user_id}: {len(transactions)} transactions")
                performance_monitor.end_operation(operation_id, success=True)
                return {
                    "patterns": [],
                    "insights": ["Insufficient transaction data for pattern analysis. Need at least 10 transactions."],
                    "confidence": 0.0,
                    "analysis_period_days": days,
                    "total_transactions": len(transactions)
                }

            # Convert to DataFrame for analysis
            try:
                df = pd.DataFrame([{
                    'date': t.date,
                    'amount': t.amount,
                    'category': t.category or 'uncategorized',
                    'type': t.type
                } for t in transactions])

                # Validate DataFrame
                if df.empty:
                    raise InsufficientDataError("No valid transaction data found")

            except Exception as e:
                logger.error(f"Failed to create transaction DataFrame for user {user_id}: {e}")
                raise DataValidationError(f"Invalid transaction data format: {e}")

            # Analyze patterns by category
            patterns = []
            insights = []

            for category in df['category'].unique():
                try:
                    category_data = df[df['category'] == category]
                    pattern = await self._analyze_category_pattern(category_data, category)
                    patterns.append(pattern)

                    # Generate insights based on patterns
                    category_insights = self._generate_pattern_insights(pattern, category)
                    insights.extend(category_insights)

                except Exception as e:
                    logger.warning(f"Failed to analyze category {category} for user {user_id}: {e}")
                    continue

            # Overall analysis
            try:
                overall_insights = self._generate_overall_insights(patterns, df)
            except Exception as e:
                logger.error(f"Failed to generate overall insights for user {user_id}: {e}")
                overall_insights = ["Error generating overall insights"]

            result = {
                "patterns": [pattern.__dict__ for pattern in patterns],
                "insights": insights + overall_insights,
                "confidence": self._calculate_analysis_confidence(patterns),
                "analysis_period_days": days,
                "total_transactions": len(transactions),
                "categories_analyzed": len(patterns)
            }

            logger.info(f"Completed transaction pattern analysis for user {user_id}: {len(patterns)} patterns found")

            # Cache the result
            self._set_cached_result(cache_key, result)

            performance_monitor.end_operation(operation_id, success=True)
            return result

        except DataValidationError as e:
            logger.error(f"Data validation error in transaction pattern analysis for user {user_id}: {e}")
            performance_monitor.end_operation(operation_id, success=False, error=str(e))
            raise

        except InsufficientDataError as e:
            logger.warning(f"Insufficient data error for user {user_id}: {e}")
            performance_monitor.end_operation(operation_id, success=False, error=str(e))
            raise

        except SQLAlchemyError as e:
            logger.error(f"Database error in transaction pattern analysis for user {user_id}: {e}")
            performance_monitor.end_operation(operation_id, success=False, error=str(e))
            raise PredictiveAnalyticsError(f"Database error: {e}")

        except Exception as e:
            logger.error(f"Unexpected error in transaction pattern analysis for user {user_id}: {e}")
            performance_monitor.end_operation(operation_id, success=False, error=str(e))
            raise PredictiveAnalyticsError(f"Analysis failed: {e}")

    async def calculate_financial_health_score(
        self,
        user_id: str,
        db: Session
    ) -> FinancialHealthScore:
        """Calculate comprehensive financial health score"""
        operation_id = performance_monitor.start_operation("calculate_financial_health_score")

        try:
            logger.info(f"Starting financial health score calculation for user {user_id}")

            # Validate inputs
            if not user_id or not isinstance(user_id, str):
                raise DataValidationError("Invalid user_id provided")

            # Gather financial metrics
            try:
                metrics = await self._calculate_financial_metrics(user_id, db)
                logger.debug(f"Calculated financial metrics for user {user_id}: {len(metrics)} metrics")
            except Exception as e:
                logger.error(f"Failed to calculate financial metrics for user {user_id}: {e}")
                raise PredictiveAnalyticsError(f"Failed to gather financial data: {e}")

            # Calculate component scores with error handling
            component_scores = {}
            for component_name, scoring_method in [
                ('income_stability', self._score_income_stability),
                ('expense_control', self._score_expense_control),
                ('savings_rate', self._score_savings_rate),
                ('debt_management', self._score_debt_management),
                ('financial_goals', self._score_financial_goals),
                ('risk_management', self._score_risk_management)
            ]:
                try:
                    score = scoring_method(metrics)
                    component_scores[component_name] = score
                except Exception as e:
                    logger.warning(f"Failed to calculate {component_name} score for user {user_id}: {e}")
                    component_scores[component_name] = 50.0  # Neutral score

            # Calculate overall score (weighted average)
            weights = {
                'income_stability': 0.25,
                'expense_control': 0.25,
                'savings_rate': 0.20,
                'debt_management': 0.15,
                'financial_goals': 0.10,
                'risk_management': 0.05
            }

            try:
                overall_score = sum(
                    score * weights[component]
                    for component, score in component_scores.items()
                )
            except Exception as e:
                logger.error(f"Failed to calculate overall score for user {user_id}: {e}")
                overall_score = 50.0

            # Determine risk level
            try:
                risk_level = self._determine_risk_level(overall_score, component_scores)
            except Exception as e:
                logger.warning(f"Failed to determine risk level for user {user_id}: {e}")
                risk_level = RiskLevel.MEDIUM

            # Generate recommendations
            try:
                recommendations = self._generate_recommendations(
                    overall_score, component_scores, metrics
                )
            except Exception as e:
                logger.warning(f"Failed to generate recommendations for user {user_id}: {e}")
                recommendations = ["Unable to generate personalized recommendations"]

            # Generate insights
            try:
                insights = self._generate_health_insights(
                    overall_score, component_scores, metrics
                )
            except Exception as e:
                logger.warning(f"Failed to generate health insights for user {user_id}: {e}")
                insights = ["Unable to generate health insights"]

            # Calculate confidence
            try:
                confidence = self._calculate_health_confidence(metrics)
            except Exception as e:
                logger.warning(f"Failed to calculate health confidence for user {user_id}: {e}")
                confidence = 0.5

            result = FinancialHealthScore(
                overall_score=round(overall_score, 1),
                component_scores={k: round(v, 1) for k, v in component_scores.items()},
                risk_level=risk_level,
                recommendations=recommendations,
                insights=insights,
                confidence=confidence
            )

            logger.info(f"Completed financial health score calculation for user {user_id}: {result.overall_score}/100 ({result.risk_level.value})")
            performance_monitor.end_operation(operation_id, success=True)
            return result

        except DataValidationError as e:
            logger.error(f"Data validation error in health score calculation for user {user_id}: {e}")
            performance_monitor.end_operation(operation_id, success=False, error=str(e))
            raise

        except SQLAlchemyError as e:
            logger.error(f"Database error in health score calculation for user {user_id}: {e}")
            performance_monitor.end_operation(operation_id, success=False, error=str(e))
            raise PredictiveAnalyticsError(f"Database error: {e}")

        except Exception as e:
            logger.error(f"Unexpected error in health score calculation for user {user_id}: {e}")
            performance_monitor.end_operation(operation_id, success=False, error=str(e))
            raise PredictiveAnalyticsError(f"Health score calculation failed: {e}")

    async def generate_predictive_insights(
        self,
        user_id: str,
        db: Session
    ) -> List[PredictiveInsight]:
        """Generate AI-powered predictive insights"""
        operation_id = performance_monitor.start_operation("generate_predictive_insights")

        try:
            logger.info(f"Starting predictive insights generation for user {user_id}")

            # Validate inputs
            if not user_id or not isinstance(user_id, str):
                raise DataValidationError("Invalid user_id provided")

            insights = []

            # Analyze different aspects with error handling
            analysis_methods = [
                ("spending_predictions", self._analyze_spending_predictions),
                ("income_predictions", self._analyze_income_predictions),
                ("risk_predictions", self._analyze_risk_predictions),
                ("goal_predictions", self._analyze_goal_predictions)
            ]

            for analysis_name, analysis_method in analysis_methods:
                try:
                    logger.debug(f"Running {analysis_name} analysis for user {user_id}")
                    method_insights = await analysis_method(user_id, db)
                    insights.extend(method_insights)
                    logger.debug(f"{analysis_name} generated {len(method_insights)} insights")
                except Exception as e:
                    logger.warning(f"Failed to generate {analysis_name} insights for user {user_id}: {e}")
                    # Continue with other analyses rather than failing completely

            # Sort by priority and confidence
            try:
                insights.sort(key=lambda x: (
                    {'high': 3, 'medium': 2, 'low': 1}[x.priority],
                    x.confidence
                ), reverse=True)
            except Exception as e:
                logger.warning(f"Failed to sort insights for user {user_id}: {e}")
                # Return unsorted if sorting fails

            result = insights[:10]  # Return top 10 insights
            logger.info(f"Completed predictive insights generation for user {user_id}: {len(result)} insights generated")
            performance_monitor.end_operation(operation_id, success=True)
            return result

        except DataValidationError as e:
            logger.error(f"Data validation error in insights generation for user {user_id}: {e}")
            performance_monitor.end_operation(operation_id, success=False, error=str(e))
            raise

        except SQLAlchemyError as e:
            logger.error(f"Database error in insights generation for user {user_id}: {e}")
            performance_monitor.end_operation(operation_id, success=False, error=str(e))
            raise PredictiveAnalyticsError(f"Database error: {e}")

        except Exception as e:
            logger.error(f"Unexpected error in insights generation for user {user_id}: {e}")
            performance_monitor.end_operation(operation_id, success=False, error=str(e))
            raise PredictiveAnalyticsError(f"Insights generation failed: {e}")

    def validate_transaction_data(self, transactions: List[Any]) -> bool:
        """Validate transaction data format and content"""
        if not transactions:
            return False

        required_fields = ['date', 'amount', 'category', 'type']
        for transaction in transactions[:5]:  # Check first 5 transactions
            if not hasattr(transaction, 'date') or not hasattr(transaction, 'amount'):
                logger.warning("Transaction missing required date or amount field")
                return False

            # Validate amount is numeric
            try:
                float(transaction.amount)
            except (ValueError, TypeError):
                logger.warning(f"Invalid transaction amount: {transaction.amount}")
                return False

        return True

    def sanitize_insight_data(self, insight: PredictiveInsight) -> PredictiveInsight:
        """Sanitize insight data to prevent injection attacks"""
        # Sanitize text fields
        insight.title = self._sanitize_text(insight.title)
        insight.description = self._sanitize_text(insight.description)

        # Sanitize recommended actions
        insight.recommended_actions = [
            self._sanitize_text(action) for action in insight.recommended_actions
        ]

        return insight

    def _sanitize_text(self, text: str) -> str:
        """Basic text sanitization"""
        if not isinstance(text, str):
            return str(text)

        # Remove potentially dangerous characters
        import re
        # Allow alphanumeric, spaces, and basic punctuation
        sanitized = re.sub(r'[^\w\s\.,!?\-]', '', text)

        # Limit length
        return sanitized[:500] if len(sanitized) > 500 else sanitized

    async def _get_user_transactions(
        self,
        user_id: str,
        db: Session,
        days: int
    ) -> List[Transaction]:
        """Get user's transactions for analysis"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            transactions = db.query(Transaction).filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.date >= cutoff_date
                )
            ).order_by(Transaction.date).all()

            logger.debug(f"Retrieved {len(transactions)} transactions for user {user_id} in last {days} days")
            return transactions

        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving transactions for user {user_id}: {e}")
            raise PredictiveAnalyticsError(f"Failed to retrieve transaction data: {e}")
        except Exception as e:
            logger.error(f"Unexpected error retrieving transactions for user {user_id}: {e}")
            raise PredictiveAnalyticsError(f"Transaction retrieval failed: {e}")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring"""
        metrics = performance_monitor.get_metrics()

        # Aggregate metrics
        total_operations = len(metrics)
        successful_operations = sum(1 for m in metrics.values() if m['status'] == 'completed')
        failed_operations = sum(1 for m in metrics.values() if m['status'] == 'failed')

        # Calculate average duration for successful operations
        successful_durations = [m['duration'] for m in metrics.values() if m['status'] == 'completed']
        avg_duration = sum(successful_durations) / len(successful_durations) if successful_durations else 0

        return {
            'total_operations': total_operations,
            'successful_operations': successful_operations,
            'failed_operations': failed_operations,
            'success_rate': successful_operations / total_operations if total_operations > 0 else 0,
            'average_duration_seconds': avg_duration,
            'recent_operations': list(metrics.values())[-10:]  # Last 10 operations
        }

    async def _analyze_category_pattern(
        self,
        category_data: pd.DataFrame,
        category: str
    ) -> TransactionPattern:
        """Analyze transaction patterns for a specific category"""

        # Calculate frequency (transactions per week)
        date_range = (category_data['date'].max() - category_data['date'].min()).days
        weeks = max(date_range / 7, 1)
        frequency = len(category_data) / weeks

        # Calculate average amount
        average_amount = category_data['amount'].abs().mean()

        # Analyze trend
        trend = self._calculate_trend(category_data)

        # Calculate seasonality (simplified)
        seasonality_score = self._calculate_seasonality(category_data)

        # Anomaly detection
        anomaly_score = self._detect_anomalies(category_data)

        # Calculate confidence based on data quality
        confidence = min(len(category_data) / 50, 1.0)  # More data = higher confidence

        return TransactionPattern(
            category=category,
            frequency=round(frequency, 2),
            average_amount=round(average_amount, 2),
            trend=trend,
            seasonality_score=round(seasonality_score, 2),
            anomaly_score=round(anomaly_score, 2),
            confidence=round(confidence, 2)
        )

    def _calculate_trend(self, data: pd.DataFrame) -> TrendDirection:
        """Calculate spending trend direction"""
        if len(data) < 5:
            return TrendDirection.STABLE

        # Simple linear regression on amounts over time
        x = np.arange(len(data))
        y = data['amount'].abs().values

        try:
            slope = np.polyfit(x, y, 1)[0]
            if slope > data['amount'].abs().std() * 0.1:
                return TrendDirection.INCREASING
            elif slope < -data['amount'].abs().std() * 0.1:
                return TrendDirection.DECREASING
            else:
                return TrendDirection.STABLE
        except:
            return TrendDirection.STABLE

    def _calculate_seasonality(self, data: pd.DataFrame) -> float:
        """Calculate seasonality score (simplified)"""
        if len(data) < 14:  # Need at least 2 weeks
            return 0.0

        # Check for weekly patterns
        data['day_of_week'] = data['date'].dt.dayofweek
        weekly_avg = data.groupby('day_of_week')['amount'].abs().mean()
        overall_avg = data['amount'].abs().mean()

        # Calculate coefficient of variation
        cv = weekly_avg.std() / overall_avg if overall_avg > 0 else 0
        return min(cv, 1.0)  # Cap at 1.0

    def _detect_anomalies(self, data: pd.DataFrame) -> float:
        """Detect anomalous transactions"""
        if len(data) < 10:
            return 0.0

        try:
            amounts = data['amount'].abs().values.reshape(-1, 1)
            self.anomaly_detector.fit(amounts)
            scores = self.anomaly_detector.decision_function(amounts)
            anomaly_score = (-scores).mean()  # Higher score = more anomalies
            return min(max(anomaly_score, 0), 1)  # Normalize to 0-1
        except:
            return 0.0

    def _generate_pattern_insights(
        self,
        pattern: TransactionPattern,
        category: str
    ) -> List[str]:
        """Generate insights based on transaction patterns"""
        insights = []

        # Frequency insights
        if pattern.frequency > 7:  # Daily transactions
            insights.append(f"You're making frequent {category} transactions - consider setting up automatic payments")
        elif pattern.frequency < 0.5:  # Less than twice a month
            insights.append(f"Your {category} spending is infrequent - you might be able to reduce this category")

        # Trend insights
        if pattern.trend == TrendDirection.INCREASING:
            insights.append(f"Your {category} spending is trending upward - monitor this closely")
        elif pattern.trend == TrendDirection.DECREASING:
            insights.append(f"Great job reducing {category} spending!")

        # Anomaly insights
        if pattern.anomaly_score > 0.7:
            insights.append(f"Unusual {category} transaction patterns detected - review recent transactions")

        return insights

    def _generate_overall_insights(
        self,
        patterns: List[TransactionPattern],
        all_data: pd.DataFrame
    ) -> List[str]:
        """Generate overall spending insights"""
        insights = []

        # Calculate total spending
        total_spending = all_data[all_data['type'] == 'expense']['amount'].abs().sum()
        total_income = all_data[all_data['type'] == 'income']['amount'].abs().sum()

        savings_rate = (total_income - total_spending) / total_income if total_income > 0 else 0

        if savings_rate < 0:
            insights.append("You're spending more than you earn - consider creating a budget")
        elif savings_rate < 0.1:
            insights.append("Your savings rate is low - aim to save at least 10% of your income")
        else:
            insights.append(f"Excellent! You're saving {savings_rate:.1%} of your income")

        # Check for high-variability categories
        high_variability = [p for p in patterns if p.anomaly_score > 0.5]
        if high_variability:
            categories = [p.category for p in high_variability[:3]]
            insights.append(f"High spending variability in: {', '.join(categories)}")

        return insights

    def _calculate_analysis_confidence(self, patterns: List[TransactionPattern]) -> float:
        """Calculate overall confidence in the analysis"""
        if not patterns:
            return 0.0

        avg_confidence = np.mean([p.confidence for p in patterns])
        data_quality = min(len(patterns) / 10, 1.0)  # More categories = higher confidence

        return round(avg_confidence * data_quality, 2)

    async def _calculate_financial_metrics(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Calculate comprehensive financial metrics"""
        # Get recent transactions (last 3 months)
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        transactions = db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.date >= cutoff_date
            )
        ).all()

        # Calculate metrics
        income_transactions = [t for t in transactions if t.type == 'income']
        expense_transactions = [t for t in transactions if t.type == 'expense']

        total_income = sum(abs(t.amount) for t in income_transactions)
        total_expenses = sum(abs(t.amount) for t in expense_transactions)

        # Monthly averages
        months = 3
        monthly_income = total_income / months
        monthly_expenses = total_expenses / months

        # Savings rate
        savings_rate = (total_income - total_expenses) / total_income if total_income > 0 else 0

        # Expense categories
        expense_by_category = {}
        for transaction in expense_transactions:
            category = transaction.category or 'uncategorized'
            expense_by_category[category] = expense_by_category.get(category, 0) + abs(transaction.amount)

        # Largest expense categories
        top_categories = sorted(expense_by_category.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'monthly_income': monthly_income,
            'monthly_expenses': monthly_expenses,
            'savings_rate': savings_rate,
            'expense_categories': expense_by_category,
            'top_expense_categories': top_categories,
            'transaction_count': len(transactions),
            'income_transaction_count': len(income_transactions),
            'expense_transaction_count': len(expense_transactions)
        }

    def _score_income_stability(self, metrics: Dict[str, Any]) -> float:
        """Score income stability (0-100)"""
        if metrics['income_transaction_count'] < 3:
            return 30.0  # Insufficient data

        # Calculate income variability
        income_std = np.std([t.amount for t in []])  # Would need actual income amounts
        income_cv = income_std / metrics['monthly_income'] if metrics['monthly_income'] > 0 else 1

        # Lower variability = higher score
        stability_score = max(0, 100 - (income_cv * 100))
        return min(stability_score, 100)

    def _score_expense_control(self, metrics: Dict[str, Any]) -> float:
        """Score expense control (0-100)"""
        if metrics['monthly_income'] == 0:
            return 0.0

        expense_ratio = metrics['monthly_expenses'] / metrics['monthly_income']

        # Ideal expense ratio is 70-80% of income
        if expense_ratio <= 0.8:
            return 100.0
        elif expense_ratio <= 1.0:
            return 80.0
        elif expense_ratio <= 1.2:
            return 50.0
        else:
            return 20.0

    def _score_savings_rate(self, metrics: Dict[str, Any]) -> float:
        """Score savings rate (0-100)"""
        savings_rate = metrics['savings_rate']

        if savings_rate >= 0.2:  # 20%+ savings
            return 100.0
        elif savings_rate >= 0.1:  # 10%+ savings
            return 80.0
        elif savings_rate >= 0:  # Breaking even
            return 60.0
        elif savings_rate >= -0.1:  # Small deficit
            return 30.0
        else:  # Large deficit
            return 10.0

    def _score_debt_management(self, metrics: Dict[str, Any]) -> float:
        """Score debt management (0-100)"""
        # Simplified scoring - would need actual debt data
        return 75.0  # Placeholder

    def _score_financial_goals(self, metrics: Dict[str, Any]) -> float:
        """Score progress toward financial goals (0-100)"""
        # Simplified scoring - would need goals data
        return 60.0  # Placeholder

    def _score_risk_management(self, metrics: Dict[str, Any]) -> float:
        """Score risk management practices (0-100)"""
        # Simplified scoring - would need insurance/risk data
        return 70.0  # Placeholder

    def _determine_risk_level(
        self,
        overall_score: float,
        component_scores: Dict[str, float]
    ) -> RiskLevel:
        """Determine overall risk level"""
        if overall_score >= 80:
            return RiskLevel.LOW
        elif overall_score >= 60:
            return RiskLevel.MEDIUM
        elif overall_score >= 40:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def _generate_recommendations(
        self,
        overall_score: float,
        component_scores: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []

        if component_scores['savings_rate'] < 50:
            recommendations.append("Increase your savings rate to at least 10% of your income")

        if component_scores['expense_control'] < 50:
            recommendations.append("Review your expenses and create a monthly budget")

        if component_scores['income_stability'] < 50:
            recommendations.append("Consider diversifying your income sources")

        if overall_score < 60:
            recommendations.append("Schedule a consultation with a financial advisor")

        return recommendations

    def _generate_health_insights(
        self,
        overall_score: float,
        component_scores: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate financial health insights"""
        insights = []

        if overall_score >= 80:
            insights.append("Excellent financial health! Keep up the great work.")
        elif overall_score >= 60:
            insights.append("Good financial standing with room for improvement.")
        else:
            insights.append("Financial health needs attention - focus on budgeting and savings.")

        return insights

    def _calculate_health_confidence(self, metrics: Dict[str, Any]) -> float:
        """Calculate confidence in health score"""
        # Based on data completeness and recency
        data_completeness = min(metrics['transaction_count'] / 100, 1.0)
        return round(data_completeness, 2)

    async def _analyze_spending_predictions(self, user_id: str, db: Session) -> List[PredictiveInsight]:
        """Analyze and predict spending patterns"""
        insights = []

        # Get spending data for analysis
        spending_data = await self._get_spending_data(user_id, db)

        if spending_data:
            # Predict next month's spending
            predicted_spending = self._predict_monthly_spending(spending_data)

            if predicted_spending > spending_data[-1] * 1.2:  # 20% increase
                insights.append(PredictiveInsight(
                    insight_id=f"spending_{user_id}_high",
                    title="Projected Spending Increase",
                    description=f"Your spending is trending upward. Next month could be {predicted_spending:.0f}, a {((predicted_spending/spending_data[-1])-1)*100:.0f}% increase.",
                    type="warning",
                    priority="high",
                    confidence=0.8,
                    predicted_impact={"spending_increase": predicted_spending - spending_data[-1]},
                    recommended_actions=[
                        "Review your budget allocations",
                        "Identify areas to cut back",
                        "Set spending alerts for high-risk categories"
                    ]
                ))

        return insights

    async def _analyze_income_predictions(self, user_id: str, db: Session) -> List[PredictiveInsight]:
        """Analyze and predict income patterns"""
        insights = []

        # Get income data for analysis
        income_data = await self._get_income_data(user_id, db)

        if income_data and len(income_data) >= 3:
            # Predict next month's income
            predicted_income = self._predict_monthly_income(income_data)

            if predicted_income < income_data[-1] * 0.9:  # 10% decrease
                insights.append(PredictiveInsight(
                    insight_id=f"income_{user_id}_decrease",
                    title="Potential Income Reduction",
                    description=f"Your income pattern suggests a possible decrease next month to {predicted_income:.0f}.",
                    type="warning",
                    priority="high",
                    confidence=0.7,
                    predicted_impact={"income_decrease": income_data[-1] - predicted_income},
                    recommended_actions=[
                        "Build up your emergency fund",
                        "Reduce discretionary spending",
                        "Explore additional income sources"
                    ]
                ))

        return insights

    async def _analyze_risk_predictions(self, user_id: str, db: Session) -> List[PredictiveInsight]:
        """Analyze financial risk factors"""
        insights = []

        # Analyze expense volatility
        expense_volatility = await self._calculate_expense_volatility(user_id, db)

        if expense_volatility > 0.3:  # High volatility
            insights.append(PredictiveInsight(
                insight_id=f"risk_{user_id}_volatility",
                title="High Expense Volatility Detected",
                description="Your spending shows high variability, which increases financial risk.",
                type="warning",
                priority="medium",
                confidence=0.75,
                predicted_impact={"volatility_risk": "high"},
                recommended_actions=[
                    "Create a more consistent spending plan",
                    "Build a larger emergency fund",
                    "Set up automatic savings transfers"
                ]
            ))

        return insights

    async def _analyze_goal_predictions(self, user_id: str, db: Session) -> List[PredictiveInsight]:
        """Analyze progress toward financial goals"""
        insights = []

        # This would analyze goal progress and predict completion dates
        # Placeholder for now
        insights.append(PredictiveInsight(
            insight_id=f"goal_{user_id}_progress",
            title="Goal Progress Update",
            description="You're on track to meet your savings goals this quarter.",
            type="success",
            priority="low",
            confidence=0.9,
            predicted_impact={"goal_progress": "on_track"},
            recommended_actions=[
                "Continue current saving habits",
                "Consider increasing contributions if possible"
            ]
        ))

        return insights

    async def _get_spending_data(self, user_id: str, db: Session) -> List[float]:
        """Get monthly spending data for the last 6 months"""
        # Simplified implementation
        return [2500, 2600, 2400, 2700, 2800, 2900]  # Mock data

    async def _get_income_data(self, user_id: str, db: Session) -> List[float]:
        """Get monthly income data for the last 6 months"""
        # Simplified implementation
        return [5000, 5100, 5000, 5200, 5100, 5300]  # Mock data

    async def _calculate_expense_volatility(self, user_id: str, db: Session) -> float:
        """Calculate expense volatility (0-1 scale)"""
        # Simplified implementation
        return 0.25  # Mock moderate volatility

    def _predict_monthly_spending(self, spending_data: List[float]) -> float:
        """Predict next month's spending using simple trend analysis"""
        if len(spending_data) < 2:
            return spending_data[-1] if spending_data else 0

        # Simple linear regression
        x = np.arange(len(spending_data))
        slope, intercept = np.polyfit(x, spending_data, 1)

        next_month = len(spending_data)
        prediction = slope * next_month + intercept

        return max(prediction, 0)  # Ensure non-negative

    def _predict_monthly_income(self, income_data: List[float]) -> float:
        """Predict next month's income"""
        if len(income_data) < 2:
            return income_data[-1] if income_data else 0

        # Use average of last 3 months with slight trend
        recent_avg = np.mean(income_data[-3:])
        trend = np.polyfit(np.arange(len(income_data)), income_data, 1)[0]

        prediction = recent_avg + trend
        return max(prediction, 0)


# Global service instance
predictive_analytics_service = PredictiveAnalyticsService()