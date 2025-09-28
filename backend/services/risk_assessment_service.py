#!/usr/bin/env python3
"""
NEXUS Platform - Automated Risk Scoring and Assessment Service
Comprehensive risk assessment across security, financial, and operational domains
"""

import asyncio
import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import asyncpg
import numpy as np
import redis.asyncio as redis
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from backend.config.settings import get_settings

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level enumeration"""

    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCategory(Enum):
    """Risk category enumeration"""

    SECURITY = "security"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"


@dataclass
class RiskFactor:
    """Data class for individual risk factors"""

    factor_id: str
    category: RiskCategory
    name: str
    description: str
    severity: RiskLevel
    probability: float  # 0.0 to 1.0
    impact: float  # 0.0 to 1.0
    score: float  # calculated risk score
    source: str
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class RiskAssessment:
    """Data class for comprehensive risk assessment"""

    assessment_id: str
    target: str
    overall_score: float
    risk_level: RiskLevel
    risk_factors: List[RiskFactor]
    recommendations: List[str]
    ml_confidence: float
    timestamp: datetime
    valid_until: datetime


class RiskAssessmentService:
    """Automated risk scoring and assessment service with ML capabilities"""

    def __init__(self):
        self.settings = get_settings()
        self.db_engine = None
        self.redis_client = None

        # ML components for risk prediction
        self.risk_predictor = None
        self.anomaly_detector = None
        self.scaler = None
        self._initialize_ml_components()

        # Risk thresholds
        self.risk_thresholds = {
            RiskLevel.MINIMAL: 0,
            RiskLevel.LOW: 15,
            RiskLevel.MEDIUM: 30,
            RiskLevel.HIGH: 60,
            RiskLevel.CRITICAL: 80,
        }

    def _initialize_ml_components(self):
        """Initialize machine learning components for risk assessment"""
        try:
            self.risk_predictor = RandomForestRegressor(
                n_estimators=100, random_state=42, n_jobs=-1
            )
            self.anomaly_detector = IsolationForest(
                contamination=0.1, random_state=42, n_jobs=-1
            )
            self.scaler = StandardScaler()

            # Load or train models if available
            self._load_or_train_models()

            logger.info("ML components initialized for risk assessment")

        except Exception as e:
            logger.warning(f"Failed to initialize ML components: {e}")
            self.risk_predictor = None
            self.anomaly_detector = None
            self.scaler = None

    def _load_or_train_models(self):
        """Load existing models or train with baseline data"""
        try:
            # In production, load pre-trained models
            # For now, train with synthetic data
            self._train_baseline_models()
        except Exception as e:
            logger.warning(f"Failed to load/train models: {e}")

    def _train_baseline_models(self):
        """Train ML models with synthetic risk data"""
        try:
            np.random.seed(42)

            # Generate synthetic risk data
            n_samples = 1000
            features = np.random.randn(n_samples, 10)

            # Generate risk scores (0-100)
            risk_scores = np.random.beta(2, 5, n_samples) * 100

            # Train risk predictor
            if self.risk_predictor and self.scaler:
                features_scaled = self.scaler.fit_transform(features)
                self.risk_predictor.fit(features_scaled, risk_scores)

            # Train anomaly detector
            if self.anomaly_detector:
                self.anomaly_detector.fit(features)

            logger.info("Baseline ML models trained for risk assessment")

        except Exception as e:
            logger.warning(f"Failed to train baseline models: {e}")

    async def initialize(self):
        """Initialize database and Redis connections"""
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

            # Create risk assessment tables if they don't exist
            await self._create_tables()

            logger.info("Risk assessment service initialized")

        except Exception as e:
            logger.error(f"Failed to initialize risk assessment service: {e}")
            raise

    async def _create_tables(self):
        """Create necessary database tables for risk assessment"""
        try:
            async with self.db_engine.begin() as conn:
                # Risk assessments table
                await conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS risk_assessments (
                        assessment_id VARCHAR(255) PRIMARY KEY,
                        target VARCHAR(255) NOT NULL,
                        overall_score FLOAT NOT NULL,
                        risk_level VARCHAR(50) NOT NULL,
                        risk_factors JSONB,
                        recommendations JSONB,
                        ml_confidence FLOAT,
                        timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                        valid_until TIMESTAMP WITH TIME ZONE NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """
                    )
                )

                # Risk factors table
                await conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS risk_factors (
                        factor_id VARCHAR(255) PRIMARY KEY,
                        category VARCHAR(50) NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        severity VARCHAR(50) NOT NULL,
                        probability FLOAT,
                        impact FLOAT,
                        score FLOAT,
                        source VARCHAR(255),
                        timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                        metadata JSONB,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """
                    )
                )

                # Risk trends table for historical analysis
                await conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS risk_trends (
                        trend_id SERIAL PRIMARY KEY,
                        target VARCHAR(255) NOT NULL,
                        period_start TIMESTAMP WITH TIME ZONE NOT NULL,
                        period_end TIMESTAMP WITH TIME ZONE NOT NULL,
                        avg_score FLOAT,
                        max_score FLOAT,
                        risk_level_changes JSONB,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """
                    )
                )

        except Exception as e:
            logger.error(f"Failed to create risk assessment tables: {e}")
            raise

    async def assess_target_risk(
        self, target: str, categories: List[RiskCategory] = None
    ) -> RiskAssessment:
        """Perform comprehensive risk assessment for a target"""
        try:
            if categories is None:
                categories = list(RiskCategory)

            # Collect risk factors from all categories
            risk_factors = []
            for category in categories:
                factors = await self._collect_risk_factors(target, category)
                risk_factors.extend(factors)

            # Calculate overall risk score
            overall_score, ml_confidence = self._calculate_overall_risk(risk_factors)

            # Determine risk level
            risk_level = self._get_risk_level(overall_score)

            # Generate recommendations
            recommendations = self._generate_recommendations(risk_factors, risk_level)

            # Create assessment
            assessment_id = (
                f"risk_{target}_{int(datetime.now(timezone.utc).timestamp())}"
            )
            timestamp = datetime.now(timezone.utc)
            valid_until = timestamp + timedelta(hours=24)  # Valid for 24 hours

            assessment = RiskAssessment(
                assessment_id=assessment_id,
                target=target,
                overall_score=overall_score,
                risk_level=risk_level,
                risk_factors=risk_factors,
                recommendations=recommendations,
                ml_confidence=ml_confidence,
                timestamp=timestamp,
                valid_until=valid_until,
            )

            # Store assessment
            await self._store_assessment(assessment)

            # Cache assessment
            await self._cache_assessment(assessment)

            logger.info(
                f"Risk assessment completed for {target}: score={overall_score:.1f}, level={risk_level.value}"
            )

            return assessment

        except Exception as e:
            logger.error(f"Failed to assess risk for {target}: {e}")
            raise

    async def _collect_risk_factors(
        self, target: str, category: RiskCategory
    ) -> List[RiskFactor]:
        """Collect risk factors for a specific category"""
        try:
            factors = []

            if category == RiskCategory.SECURITY:
                factors.extend(await self._collect_security_risks(target))
            elif category == RiskCategory.FINANCIAL:
                factors.extend(await self._collect_financial_risks(target))
            elif category == RiskCategory.OPERATIONAL:
                factors.extend(await self._collect_operational_risks(target))
            elif category == RiskCategory.COMPLIANCE:
                factors.extend(await self._collect_compliance_risks(target))
            elif category == RiskCategory.PERFORMANCE:
                factors.extend(await self._collect_performance_risks(target))

            return factors

        except Exception as e:
            logger.warning(
                f"Failed to collect {category.value} risks for {target}: {e}"
            )
            return []

    async def _collect_security_risks(self, target: str) -> List[RiskFactor]:
        """Collect security-related risk factors"""
        factors = []

        try:
            # Get security scan results from security scanner
            from .security_hardening import security_hardening_service

            # Check for recent security scans
            scan_results = await security_hardening_service.get_recent_scans(
                target, hours=24
            )

            for scan in scan_results:
                if scan.get("vulnerabilities"):
                    for vuln in scan["vulnerabilities"]:
                        severity_map = {
                            "critical": RiskLevel.CRITICAL,
                            "high": RiskLevel.HIGH,
                            "medium": RiskLevel.MEDIUM,
                            "low": RiskLevel.LOW,
                            "unknown": RiskLevel.LOW,
                        }

                        severity = severity_map.get(
                            vuln.get("severity", "unknown"), RiskLevel.LOW
                        )
                        cvss_score = vuln.get("cvss_score", 0) or 0

                        factor = RiskFactor(
                            factor_id=f"sec_{vuln.get('vulnerability_id', 'unknown')}_{target}",
                            category=RiskCategory.SECURITY,
                            name=vuln.get("title", "Security Vulnerability"),
                            description=vuln.get("description", ""),
                            severity=severity,
                            probability=0.8,  # High probability for known vulnerabilities
                            impact=cvss_score / 10.0 if cvss_score else 0.5,
                            score=self._calculate_risk_score(
                                severity, 0.8, cvss_score / 10.0 if cvss_score else 0.5
                            ),
                            source="security_scanner",
                            timestamp=datetime.now(timezone.utc),
                            metadata={
                                "cve_id": vuln.get("cve_id"),
                                "cvss_score": cvss_score,
                                "scan_type": scan.get("scan_type"),
                            },
                        )
                        factors.append(factor)

            # Check for authentication risks
            auth_risks = await self._check_authentication_risks(target)
            factors.extend(auth_risks)

            # Check for access control risks
            access_risks = await self._check_access_control_risks(target)
            factors.extend(access_risks)

        except Exception as e:
            logger.warning(f"Failed to collect security risks: {e}")

        return factors

    async def _collect_financial_risks(self, target: str) -> List[RiskFactor]:
        """Collect financial-related risk factors"""
        factors = []

        try:
            # Get financial data from budget service
            from .budget_service import budget_service

            budget_data = await budget_service.get_budget_status(target)

            if budget_data:
                # Budget overrun risk
                if budget_data.get("utilization", 0) > 0.9:
                    factor = RiskFactor(
                        factor_id=f"fin_budget_{target}",
                        category=RiskCategory.FINANCIAL,
                        name="Budget Overrun Risk",
                        description=f"Budget utilization at {budget_data['utilization']*100:.1f}%",
                        severity=RiskLevel.HIGH,
                        probability=0.7,
                        impact=0.8,
                        score=self._calculate_risk_score(RiskLevel.HIGH, 0.7, 0.8),
                        source="budget_service",
                        timestamp=datetime.now(timezone.utc),
                        metadata=budget_data,
                    )
                    factors.append(factor)

                # Cost variance risk
                variance = budget_data.get("variance", 0)
                if abs(variance) > 0.2:
                    severity = (
                        RiskLevel.CRITICAL if abs(variance) > 0.5 else RiskLevel.HIGH
                    )
                    factor = RiskFactor(
                        factor_id=f"fin_variance_{target}",
                        category=RiskCategory.FINANCIAL,
                        name="Cost Variance Risk",
                        description=f"Cost variance of {variance*100:.1f}% from budget",
                        severity=severity,
                        probability=0.8,
                        impact=abs(variance),
                        score=self._calculate_risk_score(severity, 0.8, abs(variance)),
                        source="budget_service",
                        timestamp=datetime.now(timezone.utc),
                        metadata={"variance": variance},
                    )
                    factors.append(factor)

        except Exception as e:
            logger.warning(f"Failed to collect financial risks: {e}")

        return factors

    async def _collect_operational_risks(self, target: str) -> List[RiskFactor]:
        """Collect operational risk factors"""
        factors = []

        try:
            # Check system health
            health_data = await self._get_system_health(target)

            if health_data:
                # Service availability risk
                uptime = health_data.get("uptime_percentage", 100)
                if uptime < 99.5:
                    severity = RiskLevel.CRITICAL if uptime < 95 else RiskLevel.HIGH
                    factor = RiskFactor(
                        factor_id=f"ops_uptime_{target}",
                        category=RiskCategory.OPERATIONAL,
                        name="Service Availability Risk",
                        description=f"Service uptime at {uptime:.1f}%",
                        severity=severity,
                        probability=0.9,
                        impact=(100 - uptime) / 100,
                        score=self._calculate_risk_score(
                            severity, 0.9, (100 - uptime) / 100
                        ),
                        source="monitoring",
                        timestamp=datetime.now(timezone.utc),
                        metadata=health_data,
                    )
                    factors.append(factor)

                # Resource utilization risk
                cpu_usage = health_data.get("cpu_usage", 0)
                if cpu_usage > 90:
                    factor = RiskFactor(
                        factor_id=f"ops_cpu_{target}",
                        category=RiskCategory.OPERATIONAL,
                        name="High CPU Utilization",
                        description=f"CPU usage at {cpu_usage:.1f}%",
                        severity=RiskLevel.MEDIUM,
                        probability=0.6,
                        impact=0.4,
                        score=self._calculate_risk_score(RiskLevel.MEDIUM, 0.6, 0.4),
                        source="monitoring",
                        timestamp=datetime.now(timezone.utc),
                        metadata={"cpu_usage": cpu_usage},
                    )
                    factors.append(factor)

        except Exception as e:
            logger.warning(f"Failed to collect operational risks: {e}")

        return factors

    async def _collect_compliance_risks(self, target: str) -> List[RiskFactor]:
        """Collect compliance-related risk factors"""
        factors = []

        try:
            # Check compliance status
            compliance_data = await self._get_compliance_status(target)

            if compliance_data:
                non_compliant = compliance_data.get("non_compliant_items", 0)
                if non_compliant > 0:
                    severity = (
                        RiskLevel.CRITICAL if non_compliant > 5 else RiskLevel.HIGH
                    )
                    factor = RiskFactor(
                        factor_id=f"comp_noncomp_{target}",
                        category=RiskCategory.COMPLIANCE,
                        name="Compliance Violations",
                        description=f"{non_compliant} compliance violations detected",
                        severity=severity,
                        probability=0.9,
                        impact=min(non_compliant / 10, 1.0),
                        score=self._calculate_risk_score(
                            severity, 0.9, min(non_compliant / 10, 1.0)
                        ),
                        source="compliance_checker",
                        timestamp=datetime.now(timezone.utc),
                        metadata=compliance_data,
                    )
                    factors.append(factor)

        except Exception as e:
            logger.warning(f"Failed to collect compliance risks: {e}")

        return factors

    async def _collect_performance_risks(self, target: str) -> List[RiskFactor]:
        """Collect performance-related risk factors"""
        factors = []

        try:
            # Get performance metrics
            perf_data = await self._get_performance_metrics(target)

            if perf_data:
                # Response time risk
                avg_response_time = perf_data.get("avg_response_time", 0)
                if avg_response_time > 2000:  # 2 seconds
                    severity = (
                        RiskLevel.CRITICAL
                        if avg_response_time > 5000
                        else RiskLevel.HIGH
                    )
                    factor = RiskFactor(
                        factor_id=f"perf_response_{target}",
                        category=RiskCategory.PERFORMANCE,
                        name="Slow Response Times",
                        description=f"Average response time: {avg_response_time:.0f}ms",
                        severity=severity,
                        probability=0.7,
                        impact=min(avg_response_time / 10000, 1.0),
                        score=self._calculate_risk_score(
                            severity, 0.7, min(avg_response_time / 10000, 1.0)
                        ),
                        source="performance_monitor",
                        timestamp=datetime.now(timezone.utc),
                        metadata=perf_data,
                    )
                    factors.append(factor)

                # Error rate risk
                error_rate = perf_data.get("error_rate", 0)
                if error_rate > 0.05:  # 5%
                    severity = (
                        RiskLevel.CRITICAL if error_rate > 0.1 else RiskLevel.HIGH
                    )
                    factor = RiskFactor(
                        factor_id=f"perf_errors_{target}",
                        category=RiskCategory.PERFORMANCE,
                        name="High Error Rate",
                        description=f"Error rate: {error_rate*100:.1f}%",
                        severity=severity,
                        probability=0.8,
                        impact=error_rate * 2,
                        score=self._calculate_risk_score(
                            severity, 0.8, min(error_rate * 2, 1.0)
                        ),
                        source="performance_monitor",
                        timestamp=datetime.now(timezone.utc),
                        metadata={"error_rate": error_rate},
                    )
                    factors.append(factor)

        except Exception as e:
            logger.warning(f"Failed to collect performance risks: {e}")

        return factors

    def _calculate_risk_score(
        self, severity: RiskLevel, probability: float, impact: float
    ) -> float:
        """Calculate risk score using severity, probability, and impact"""
        severity_score = {
            RiskLevel.MINIMAL: 5,
            RiskLevel.LOW: 15,
            RiskLevel.MEDIUM: 30,
            RiskLevel.HIGH: 60,
            RiskLevel.CRITICAL: 80,
        }[severity]

        # Risk = Severity * Probability * Impact
        risk_score = severity_score * probability * impact

        return min(risk_score, 100)

    def _calculate_overall_risk(
        self, risk_factors: List[RiskFactor]
    ) -> Tuple[float, float]:
        """Calculate overall risk score using traditional and ML methods"""
        if not risk_factors:
            return 0.0, 0.0

        # Traditional weighted average
        total_weight = sum(factor.score for factor in risk_factors)
        traditional_score = total_weight / len(risk_factors) if risk_factors else 0

        # ML-enhanced score
        ml_score = self._calculate_ml_risk_score(risk_factors)
        ml_confidence = 0.8 if ml_score is not None else 0.0

        # Combine scores (70% traditional, 30% ML if available)
        if ml_score is not None:
            overall_score = 0.7 * traditional_score + 0.3 * ml_score
        else:
            overall_score = traditional_score

        return overall_score, ml_confidence

    def _calculate_ml_risk_score(
        self, risk_factors: List[RiskFactor]
    ) -> Optional[float]:
        """Calculate ML-enhanced risk score"""
        if not self.risk_predictor or not self.scaler or not risk_factors:
            return None

        try:
            # Extract features from risk factors
            features = self._extract_risk_features(risk_factors)

            if not features:
                return None

            # Scale features and predict
            features_scaled = self.scaler.transform([features])
            predicted_score = self.risk_predictor.predict(features_scaled)[0]

            return max(0, min(100, predicted_score))

        except Exception as e:
            logger.warning(f"ML risk score calculation failed: {e}")
            return None

    def _extract_risk_features(self, risk_factors: List[RiskFactor]) -> List[float]:
        """Extract numerical features from risk factors for ML"""
        features = []

        # Count factors by category
        category_counts = {cat: 0 for cat in RiskCategory}
        for factor in risk_factors:
            category_counts[factor.category] += 1

        features.extend(category_counts.values())

        # Count factors by severity
        severity_counts = {level: 0 for level in RiskLevel}
        for factor in risk_factors:
            severity_counts[factor.severity] += 1

        features.extend(severity_counts.values())

        # Average probability and impact
        if risk_factors:
            avg_probability = sum(f.probability for f in risk_factors) / len(
                risk_factors
            )
            avg_impact = sum(f.impact for f in risk_factors) / len(risk_factors)
            max_score = max(f.score for f in risk_factors)
        else:
            avg_probability = avg_impact = max_score = 0

        features.extend([avg_probability, avg_impact, max_score])

        # Total number of factors
        features.append(len(risk_factors))

        return features

    def _get_risk_level(self, score: float) -> RiskLevel:
        """Determine risk level based on score"""
        for level in reversed(list(RiskLevel)):
            if score >= self.risk_thresholds[level]:
                return level
        return RiskLevel.MINIMAL

    def _generate_recommendations(
        self, risk_factors: List[RiskFactor], risk_level: RiskLevel
    ) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []

        # Group factors by category
        category_factors = {}
        for factor in risk_factors:
            if factor.category not in category_factors:
                category_factors[factor.category] = []
            category_factors[factor.category].append(factor)

        # Generate category-specific recommendations
        for category, factors in category_factors.items():
            if category == RiskCategory.SECURITY:
                recommendations.extend(self._generate_security_recommendations(factors))
            elif category == RiskCategory.FINANCIAL:
                recommendations.extend(
                    self._generate_financial_recommendations(factors)
                )
            elif category == RiskCategory.OPERATIONAL:
                recommendations.extend(
                    self._generate_operational_recommendations(factors)
                )
            elif category == RiskCategory.COMPLIANCE:
                recommendations.extend(
                    self._generate_compliance_recommendations(factors)
                )
            elif category == RiskCategory.PERFORMANCE:
                recommendations.extend(
                    self._generate_performance_recommendations(factors)
                )

        # Add general recommendations based on overall risk level
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.insert(
                0, "URGENT: Immediate attention required for critical risk factors"
            )
            recommendations.append(
                "Consider implementing emergency response procedures"
            )
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.append(
                "Monitor risk factors closely and implement mitigation plans"
            )
        else:
            recommendations.append("Continue regular risk monitoring and maintenance")

        return recommendations[:10]  # Limit to top 10 recommendations

    def _generate_security_recommendations(
        self, factors: List[RiskFactor]
    ) -> List[str]:
        """Generate security-specific recommendations"""
        recommendations = []

        critical_count = sum(1 for f in factors if f.severity == RiskLevel.CRITICAL)
        high_count = sum(1 for f in factors if f.severity == RiskLevel.HIGH)

        if critical_count > 0:
            recommendations.append(
                f"Address {critical_count} critical security vulnerabilities immediately"
            )
        if high_count > 0:
            recommendations.append(
                f"Remediate {high_count} high-severity security issues within 30 days"
            )

        recommendations.extend(
            [
                "Implement automated security scanning in CI/CD pipeline",
                "Regular security training for development team",
                "Keep all dependencies and containers updated",
                "Implement least privilege access controls",
            ]
        )

        return recommendations

    def _generate_financial_recommendations(
        self, factors: List[RiskFactor]
    ) -> List[str]:
        """Generate financial-specific recommendations"""
        recommendations = []

        budget_overruns = [f for f in factors if "budget" in f.factor_id.lower()]
        if budget_overruns:
            recommendations.append("Review and optimize budget allocation")
            recommendations.append("Implement cost monitoring and alerting")

        recommendations.extend(
            [
                "Regular financial risk assessments",
                "Diversify resource allocation",
                "Implement cost optimization strategies",
            ]
        )

        return recommendations

    def _generate_operational_recommendations(
        self, factors: List[RiskFactor]
    ) -> List[str]:
        """Generate operational-specific recommendations"""
        recommendations = []

        uptime_issues = [f for f in factors if "uptime" in f.factor_id.lower()]
        if uptime_issues:
            recommendations.append("Implement redundancy and failover mechanisms")
            recommendations.append("Improve monitoring and alerting systems")

        recommendations.extend(
            [
                "Regular backup and disaster recovery testing",
                "Implement automated scaling based on load",
                "Regular maintenance windows for system updates",
            ]
        )

        return recommendations

    def _generate_compliance_recommendations(
        self, factors: List[RiskFactor]
    ) -> List[str]:
        """Generate compliance-specific recommendations"""
        recommendations = []

        non_compliant = [f for f in factors if "noncomp" in f.factor_id.lower()]
        if non_compliant:
            recommendations.append("Address compliance violations immediately")
            recommendations.append("Schedule compliance audit and remediation")

        recommendations.extend(
            [
                "Regular compliance monitoring and reporting",
                "Implement automated compliance checks",
                "Staff training on regulatory requirements",
            ]
        )

        return recommendations

    def _generate_performance_recommendations(
        self, factors: List[RiskFactor]
    ) -> List[str]:
        """Generate performance-specific recommendations"""
        recommendations = []

        response_time_issues = [f for f in factors if "response" in f.factor_id.lower()]
        if response_time_issues:
            recommendations.append("Optimize application performance and caching")
            recommendations.append("Implement load balancing and scaling")

        error_issues = [f for f in factors if "errors" in f.factor_id.lower()]
        if error_issues:
            recommendations.append("Improve error handling and monitoring")
            recommendations.append("Conduct root cause analysis for errors")

        recommendations.extend(
            [
                "Regular performance testing and profiling",
                "Optimize database queries and indexing",
                "Implement content delivery network (CDN)",
            ]
        )

        return recommendations

    async def _store_assessment(self, assessment: RiskAssessment):
        """Store risk assessment in database"""
        try:
            async with self.db_engine.begin() as conn:
                # Store assessment
                await conn.execute(
                    text(
                        """
                    INSERT INTO risk_assessments
                    (assessment_id, target, overall_score, risk_level, risk_factors,
                     recommendations, ml_confidence, timestamp, valid_until)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT (assessment_id) DO UPDATE SET
                        overall_score = EXCLUDED.overall_score,
                        risk_level = EXCLUDED.risk_level,
                        risk_factors = EXCLUDED.risk_factors,
                        recommendations = EXCLUDED.recommendations,
                        ml_confidence = EXCLUDED.ml_confidence,
                        timestamp = EXCLUDED.timestamp,
                        valid_until = EXCLUDED.valid_until
                """
                    ),
                    (
                        assessment.assessment_id,
                        assessment.target,
                        assessment.overall_score,
                        assessment.risk_level.value,
                        json.dumps(
                            [
                                {
                                    "factor_id": f.factor_id,
                                    "category": f.category.value,
                                    "name": f.name,
                                    "severity": f.severity.value,
                                    "score": f.score,
                                    "source": f.source,
                                }
                                for f in assessment.risk_factors
                            ]
                        ),
                        json.dumps(assessment.recommendations),
                        assessment.ml_confidence,
                        assessment.timestamp,
                        assessment.valid_until,
                    ),
                )

                # Store individual risk factors
                for factor in assessment.risk_factors:
                    await conn.execute(
                        text(
                            """
                        INSERT INTO risk_factors
                        (factor_id, category, name, description, severity, probability,
                         impact, score, source, timestamp, metadata)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                        ON CONFLICT (factor_id) DO UPDATE SET
                            severity = EXCLUDED.severity,
                            probability = EXCLUDED.probability,
                            impact = EXCLUDED.impact,
                            score = EXCLUDED.score,
                            timestamp = EXCLUDED.timestamp,
                            metadata = EXCLUDED.metadata
                    """
                        ),
                        (
                            factor.factor_id,
                            factor.category.value,
                            factor.name,
                            factor.description,
                            factor.severity.value,
                            factor.probability,
                            factor.impact,
                            factor.score,
                            factor.source,
                            factor.timestamp,
                            json.dumps(factor.metadata),
                        ),
                    )

        except Exception as e:
            logger.error(f"Failed to store risk assessment: {e}")

    async def _cache_assessment(self, assessment: RiskAssessment):
        """Cache risk assessment in Redis"""
        try:
            cache_key = f"risk_assessment:{assessment.target}"
            cache_data = {
                "assessment_id": assessment.assessment_id,
                "overall_score": assessment.overall_score,
                "risk_level": assessment.risk_level.value,
                "recommendations": assessment.recommendations,
                "ml_confidence": assessment.ml_confidence,
                "timestamp": assessment.timestamp.isoformat(),
                "valid_until": assessment.valid_until.isoformat(),
            }

            await self.redis_client.setex(
                cache_key, 3600, json.dumps(cache_data)  # 1 hour TTL
            )

        except Exception as e:
            logger.warning(f"Failed to cache risk assessment: {e}")

    async def get_cached_assessment(self, target: str) -> Optional[RiskAssessment]:
        """Get cached risk assessment"""
        try:
            cache_key = f"risk_assessment:{target}"
            cached_data = await self.redis_client.get(cache_key)

            if cached_data:
                data = json.loads(cached_data)
                valid_until = datetime.fromisoformat(data["valid_until"])

                if datetime.now(timezone.utc) < valid_until:
                    # Reconstruct assessment from cache
                    return RiskAssessment(
                        assessment_id=data["assessment_id"],
                        target=target,
                        overall_score=data["overall_score"],
                        risk_level=RiskLevel(data["risk_level"]),
                        risk_factors=[],  # Not cached for space
                        recommendations=data["recommendations"],
                        ml_confidence=data["ml_confidence"],
                        timestamp=datetime.fromisoformat(data["timestamp"]),
                        valid_until=valid_until,
                    )

            return None

        except Exception as e:
            logger.warning(f"Failed to get cached assessment: {e}")
            return None

    async def get_risk_trends(self, target: str, days: int = 30) -> Dict[str, Any]:
        """Get risk trends for a target over time"""
        try:
            async with self.db_engine.begin() as conn:
                result = await conn.execute(
                    text(
                        """
                    SELECT
                        DATE_TRUNC('day', timestamp) as date,
                        AVG(overall_score) as avg_score,
                        MAX(overall_score) as max_score,
                        COUNT(*) as assessment_count
                    FROM risk_assessments
                    WHERE target = $1
                        AND timestamp >= NOW() - INTERVAL '%s days'
                    GROUP BY DATE_TRUNC('day', timestamp)
                    ORDER BY date
                """
                    ),
                    (target, days),
                )

                rows = result.fetchall()

                trends = {
                    "target": target,
                    "period_days": days,
                    "daily_scores": [
                        {
                            "date": row[0].isoformat(),
                            "avg_score": float(row[1]),
                            "max_score": float(row[2]),
                            "assessment_count": row[3],
                        }
                        for row in rows
                    ],
                }

                return trends

        except Exception as e:
            logger.error(f"Failed to get risk trends: {e}")
            return {"error": str(e)}

    # Placeholder methods for data collection (to be implemented based on existing services)
    async def _check_authentication_risks(self, target: str) -> List[RiskFactor]:
        """Check for authentication-related risks"""
        # Implementation would integrate with auth service
        return []

    async def _check_access_control_risks(self, target: str) -> List[RiskFactor]:
        """Check for access control risks"""
        # Implementation would integrate with auth service
        return []

    async def _get_system_health(self, target: str) -> Optional[Dict[str, Any]]:
        """Get system health data"""
        # Implementation would integrate with monitoring service
        return {"uptime_percentage": 99.9, "cpu_usage": 45.0}

    async def _get_compliance_status(self, target: str) -> Optional[Dict[str, Any]]:
        """Get compliance status"""
        # Implementation would integrate with compliance service
        return {"non_compliant_items": 0}

    async def _get_performance_metrics(self, target: str) -> Optional[Dict[str, Any]]:
        """Get performance metrics"""
        # Implementation would integrate with monitoring service
        return {"avg_response_time": 150.0, "error_rate": 0.01}


# Global risk assessment service instance
risk_assessment_service = RiskAssessmentService()
