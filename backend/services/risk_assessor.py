"""
NEXUS Platform - Risk Assessor Service
Comprehensive risk assessment and scoring system
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class RiskType(str, Enum):
    CREDIT = "credit"
    OPERATIONAL = "operational"
    MARKET = "market"
    COMPLIANCE = "compliance"
    FRAUD = "fraud"
    LIQUIDITY = "liquidity"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RiskFactor:
    type: RiskType
    score: float
    weight: float
    description: str
    impact: str
    mitigation: List[str]
    metadata: Dict[str, Any]

@dataclass
class RiskAssessment:
    overall_score: float
    risk_level: RiskLevel
    risk_factors: List[RiskFactor]
    recommendations: List[str]
    confidence: float
    metadata: Dict[str, Any]

class RiskAssessor:
    """
    Comprehensive risk assessment engine
    """
    
    def __init__(self, user_id: str, sensitivity: float = 0.7):
        self.user_id = user_id
        self.sensitivity = sensitivity
        self.logger = logging.getLogger(f"{__name__}.{user_id}")
        
        # Risk weights (can be customized)
        self.risk_weights = {
            RiskType.CREDIT: 0.25,
            RiskType.OPERATIONAL: 0.20,
            RiskType.MARKET: 0.15,
            RiskType.COMPLIANCE: 0.20,
            RiskType.FRAUD: 0.15,
            RiskType.LIQUIDITY: 0.05
        }
    
    async def assess_credit_risk(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess credit risk factors"""
        try:
            risk_factors = []
            
            # Debt-to-income ratio analysis
            if 'income' in df.columns and 'debt' in df.columns:
                income = df['income'].sum()
                debt = df['debt'].sum()
                
                if income > 0:
                    dti_ratio = debt / income
                    dti_score = min(1.0, dti_ratio / 0.4)  # 40% is considered high
                    
                    risk_factors.append(RiskFactor(
                        type=RiskType.CREDIT,
                        score=dti_score,
                        weight=0.3,
                        description=f"Debt-to-Income Ratio: {dti_ratio:.2%}",
                        impact="High DTI indicates potential payment difficulties",
                        mitigation=["Reduce debt", "Increase income", "Refinance high-interest debt"],
                        metadata={'dti_ratio': dti_ratio, 'income': income, 'debt': debt}
                    ))
            
            # Payment history analysis
            if 'payment_status' in df.columns:
                late_payments = df[df['payment_status'] == 'late'].shape[0]
                total_payments = df.shape[0]
                
                if total_payments > 0:
                    late_payment_rate = late_payments / total_payments
                    payment_score = min(1.0, late_payment_rate * 2)  # Double weight for late payments
                    
                    risk_factors.append(RiskFactor(
                        type=RiskType.CREDIT,
                        score=payment_score,
                        weight=0.4,
                        description=f"Late Payment Rate: {late_payment_rate:.2%}",
                        impact="Late payments indicate credit risk",
                        mitigation=["Improve payment timeliness", "Set up automatic payments", "Negotiate payment terms"],
                        metadata={'late_payments': late_payments, 'total_payments': total_payments}
                    ))
            
            # Credit utilization analysis
            if 'credit_limit' in df.columns and 'credit_used' in df.columns:
                total_limit = df['credit_limit'].sum()
                total_used = df['credit_used'].sum()
                
                if total_limit > 0:
                    utilization_rate = total_used / total_limit
                    utilization_score = min(1.0, utilization_rate)
                    
                    risk_factors.append(RiskFactor(
                        type=RiskType.CREDIT,
                        score=utilization_score,
                        weight=0.3,
                        description=f"Credit Utilization: {utilization_rate:.2%}",
                        impact="High utilization indicates credit stress",
                        mitigation=["Pay down balances", "Request credit limit increases", "Use credit more responsibly"],
                        metadata={'utilization_rate': utilization_rate, 'total_limit': total_limit, 'total_used': total_used}
                    ))
            
            # Calculate overall credit risk score
            if risk_factors:
                weighted_score = sum(factor.score * factor.weight for factor in risk_factors)
                weighted_weight = sum(factor.weight for factor in risk_factors)
                overall_score = weighted_score / weighted_weight if weighted_weight > 0 else 0.0
            else:
                overall_score = 0.0
            
            return {
                'score': overall_score,
                'risk_factors': risk_factors,
                'confidence': 0.8,
                'metadata': {'analysis_type': 'credit_risk', 'factors_analyzed': len(risk_factors)}
            }
            
        except Exception as e:
            self.logger.error(f"Credit risk assessment failed: {str(e)}")
            return {'score': 0.0, 'risk_factors': [], 'confidence': 0.0, 'error': str(e)}
    
    async def assess_operational_risk(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess operational risk factors"""
        try:
            risk_factors = []
            
            # Transaction volume analysis
            if 'amount' in df.columns and 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['date'] = df['timestamp'].dt.date
                
                # Daily transaction volume
                daily_volume = df.groupby('date')['amount'].sum()
                volume_std = daily_volume.std()
                volume_mean = daily_volume.mean()
                
                if volume_mean > 0:
                    volume_cv = volume_std / volume_mean  # Coefficient of variation
                    volume_score = min(1.0, volume_cv)
                    
                    risk_factors.append(RiskFactor(
                        type=RiskType.OPERATIONAL,
                        score=volume_score,
                        weight=0.3,
                        description=f"Transaction Volume Volatility: {volume_cv:.2f}",
                        impact="High volatility indicates operational instability",
                        mitigation=["Implement volume controls", "Improve forecasting", "Diversify transaction sources"],
                        metadata={'volume_cv': volume_cv, 'mean_volume': volume_mean, 'std_volume': volume_std}
                    ))
            
            # Error rate analysis
            if 'status' in df.columns:
                error_transactions = df[df['status'].isin(['error', 'failed', 'rejected'])].shape[0]
                total_transactions = df.shape[0]
                
                if total_transactions > 0:
                    error_rate = error_transactions / total_transactions
                    error_score = min(1.0, error_rate * 5)  # 5x weight for errors
                    
                    risk_factors.append(RiskFactor(
                        type=RiskType.OPERATIONAL,
                        score=error_score,
                        weight=0.4,
                        description=f"Transaction Error Rate: {error_rate:.2%}",
                        impact="High error rate indicates operational issues",
                        mitigation=["Improve system reliability", "Enhance error handling", "Implement better validation"],
                        metadata={'error_rate': error_rate, 'error_count': error_transactions, 'total_count': total_transactions}
                    ))
            
            # Processing time analysis
            if 'processing_time' in df.columns:
                processing_times = df['processing_time'].dropna()
                
                if len(processing_times) > 0:
                    avg_processing_time = processing_times.mean()
                    processing_std = processing_times.std()
                    
                    # High processing time indicates operational inefficiency
                    if avg_processing_time > 300:  # More than 5 minutes
                        time_score = min(1.0, (avg_processing_time - 300) / 300)
                        
                        risk_factors.append(RiskFactor(
                            type=RiskType.OPERATIONAL,
                            score=time_score,
                            weight=0.3,
                            description=f"Average Processing Time: {avg_processing_time:.1f} seconds",
                            impact="Long processing times indicate operational inefficiency",
                            mitigation=["Optimize processes", "Upgrade infrastructure", "Implement caching"],
                            metadata={'avg_time': avg_processing_time, 'std_time': processing_std}
                        ))
            
            # Calculate overall operational risk score
            if risk_factors:
                weighted_score = sum(factor.score * factor.weight for factor in risk_factors)
                weighted_weight = sum(factor.weight for factor in risk_factors)
                overall_score = weighted_score / weighted_weight if weighted_weight > 0 else 0.0
            else:
                overall_score = 0.0
            
            return {
                'score': overall_score,
                'risk_factors': risk_factors,
                'confidence': 0.7,
                'metadata': {'analysis_type': 'operational_risk', 'factors_analyzed': len(risk_factors)}
            }
            
        except Exception as e:
            self.logger.error(f"Operational risk assessment failed: {str(e)}")
            return {'score': 0.0, 'risk_factors': [], 'confidence': 0.0, 'error': str(e)}
    
    async def assess_market_risk(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess market risk factors"""
        try:
            risk_factors = []
            
            # Currency exposure analysis
            if 'currency' in df.columns:
                currency_distribution = df['currency'].value_counts()
                total_transactions = len(df)
                
                # High concentration in single currency increases risk
                if len(currency_distribution) > 0:
                    max_currency_share = currency_distribution.iloc[0] / total_transactions
                    concentration_score = max_currency_share
                    
                    risk_factors.append(RiskFactor(
                        type=RiskType.MARKET,
                        score=concentration_score,
                        weight=0.4,
                        description=f"Currency Concentration: {max_currency_share:.2%} in {currency_distribution.index[0]}",
                        impact="High currency concentration increases exchange rate risk",
                        mitigation=["Diversify currency exposure", "Use hedging strategies", "Monitor exchange rates"],
                        metadata={'max_currency_share': max_currency_share, 'currencies': len(currency_distribution)}
                    ))
            
            # Geographic concentration analysis
            if 'country' in df.columns or 'region' in df.columns:
                geo_col = 'country' if 'country' in df.columns else 'region'
                geo_distribution = df[geo_col].value_counts()
                total_transactions = len(df)
                
                if len(geo_distribution) > 0:
                    max_geo_share = geo_distribution.iloc[0] / total_transactions
                    geo_score = max_geo_share
                    
                    risk_factors.append(RiskFactor(
                        type=RiskType.MARKET,
                        score=geo_score,
                        weight=0.3,
                        description=f"Geographic Concentration: {max_geo_share:.2%} in {geo_distribution.index[0]}",
                        impact="High geographic concentration increases regional risk",
                        mitigation=["Diversify geographic exposure", "Monitor regional conditions", "Implement regional risk controls"],
                        metadata={'max_geo_share': max_geo_share, 'regions': len(geo_distribution)}
                    ))
            
            # Interest rate sensitivity analysis
            if 'interest_rate' in df.columns:
                interest_rates = df['interest_rate'].dropna()
                
                if len(interest_rates) > 0:
                    rate_volatility = interest_rates.std()
                    avg_rate = interest_rates.mean()
                    
                    if avg_rate > 0:
                        rate_cv = rate_volatility / avg_rate
                        rate_score = min(1.0, rate_cv)
                        
                        risk_factors.append(RiskFactor(
                            type=RiskType.MARKET,
                            score=rate_score,
                            weight=0.3,
                            description=f"Interest Rate Volatility: {rate_cv:.2f}",
                            impact="High rate volatility increases market risk",
                            mitigation=["Use fixed-rate instruments", "Implement rate hedging", "Monitor rate trends"],
                            metadata={'rate_cv': rate_cv, 'avg_rate': avg_rate, 'rate_std': rate_volatility}
                        ))
            
            # Calculate overall market risk score
            if risk_factors:
                weighted_score = sum(factor.score * factor.weight for factor in risk_factors)
                weighted_weight = sum(factor.weight for factor in risk_factors)
                overall_score = weighted_score / weighted_weight if weighted_weight > 0 else 0.0
            else:
                overall_score = 0.0
            
            return {
                'score': overall_score,
                'risk_factors': risk_factors,
                'confidence': 0.6,
                'metadata': {'analysis_type': 'market_risk', 'factors_analyzed': len(risk_factors)}
            }
            
        except Exception as e:
            self.logger.error(f"Market risk assessment failed: {str(e)}")
            return {'score': 0.0, 'risk_factors': [], 'confidence': 0.0, 'error': str(e)}
    
    async def assess_compliance_risk(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess compliance risk factors"""
        try:
            risk_factors = []
            
            # Regulatory reporting analysis
            if 'regulatory_category' in df.columns:
                regulatory_categories = df['regulatory_category'].value_counts()
                total_transactions = len(df)
                
                # High-risk categories increase compliance risk
                high_risk_categories = ['suspicious', 'high_value', 'international', 'cash']
                high_risk_count = sum(regulatory_categories.get(cat, 0) for cat in high_risk_categories)
                high_risk_ratio = high_risk_count / total_transactions if total_transactions > 0 else 0
                
                if high_risk_ratio > 0:
                    compliance_score = min(1.0, high_risk_ratio * 2)
                    
                    risk_factors.append(RiskFactor(
                        type=RiskType.COMPLIANCE,
                        score=compliance_score,
                        weight=0.4,
                        description=f"High-Risk Transaction Ratio: {high_risk_ratio:.2%}",
                        impact="High-risk transactions require additional compliance monitoring",
                        mitigation=["Enhance due diligence", "Implement additional controls", "Improve documentation"],
                        metadata={'high_risk_ratio': high_risk_ratio, 'high_risk_count': high_risk_count}
                    ))
            
            # Documentation completeness analysis
            required_fields = ['amount', 'date', 'description', 'counterparty']
            missing_fields = []
            
            for field in required_fields:
                if field in df.columns:
                    missing_count = df[field].isna().sum()
                    missing_ratio = missing_count / len(df) if len(df) > 0 else 0
                    
                    if missing_ratio > 0.1:  # More than 10% missing
                        missing_fields.append(field)
            
            if missing_fields:
                doc_score = min(1.0, len(missing_fields) / len(required_fields))
                
                risk_factors.append(RiskFactor(
                    type=RiskType.COMPLIANCE,
                    score=doc_score,
                    weight=0.3,
                    description=f"Missing Documentation: {', '.join(missing_fields)}",
                    impact="Incomplete documentation increases compliance risk",
                    mitigation=["Improve data collection", "Implement validation rules", "Train staff on requirements"],
                    metadata={'missing_fields': missing_fields, 'missing_count': len(missing_fields)}
                ))
            
            # Audit trail completeness
            if 'audit_trail' in df.columns:
                incomplete_audit = df[df['audit_trail'].isna()].shape[0]
                total_transactions = len(df)
                
                if total_transactions > 0:
                    audit_incomplete_ratio = incomplete_audit / total_transactions
                    
                    if audit_incomplete_ratio > 0.05:  # More than 5% incomplete
                        audit_score = min(1.0, audit_incomplete_ratio * 10)
                        
                        risk_factors.append(RiskFactor(
                            type=RiskType.COMPLIANCE,
                            score=audit_score,
                            weight=0.3,
                            description=f"Incomplete Audit Trail: {audit_incomplete_ratio:.2%}",
                            impact="Incomplete audit trails increase compliance risk",
                            mitigation=["Implement audit logging", "Regular audit reviews", "Automated compliance checks"],
                            metadata={'incomplete_ratio': audit_incomplete_ratio, 'incomplete_count': incomplete_audit}
                        ))
            
            # Calculate overall compliance risk score
            if risk_factors:
                weighted_score = sum(factor.score * factor.weight for factor in risk_factors)
                weighted_weight = sum(factor.weight for factor in risk_factors)
                overall_score = weighted_score / weighted_weight if weighted_weight > 0 else 0.0
            else:
                overall_score = 0.0
            
            return {
                'score': overall_score,
                'risk_factors': risk_factors,
                'confidence': 0.9,
                'metadata': {'analysis_type': 'compliance_risk', 'factors_analyzed': len(risk_factors)}
            }
            
        except Exception as e:
            self.logger.error(f"Compliance risk assessment failed: {str(e)}")
            return {'score': 0.0, 'risk_factors': [], 'confidence': 0.0, 'error': str(e)}
    
    async def assess_fraud_risk(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess fraud risk factors"""
        try:
            risk_factors = []
            
            # Unusual transaction patterns
            if 'amount' in df.columns:
                amounts = df['amount'].abs()
                mean_amount = amounts.mean()
                std_amount = amounts.std()
                
                # Large transactions
                large_transactions = df[amounts > mean_amount + 2 * std_amount]
                large_ratio = len(large_transactions) / len(df) if len(df) > 0 else 0
                
                if large_ratio > 0.05:  # More than 5% large transactions
                    fraud_score = min(1.0, large_ratio * 5)
                    
                    risk_factors.append(RiskFactor(
                        type=RiskType.FRAUD,
                        score=fraud_score,
                        weight=0.4,
                        description=f"Large Transaction Ratio: {large_ratio:.2%}",
                        impact="High ratio of large transactions increases fraud risk",
                        mitigation=["Implement transaction limits", "Enhanced verification", "Real-time monitoring"],
                        metadata={'large_ratio': large_ratio, 'large_count': len(large_transactions)}
                    ))
            
            # Velocity analysis
            if 'timestamp' in df.columns and 'amount' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['hour'] = df['timestamp'].dt.hour
                
                # Transactions outside business hours
                off_hours = df[(df['hour'] < 9) | (df['hour'] > 17)]
                off_hours_ratio = len(off_hours) / len(df) if len(df) > 0 else 0
                
                if off_hours_ratio > 0.3:  # More than 30% off-hours
                    velocity_score = min(1.0, off_hours_ratio)
                    
                    risk_factors.append(RiskFactor(
                        type=RiskType.FRAUD,
                        score=velocity_score,
                        weight=0.3,
                        description=f"Off-Hours Transaction Ratio: {off_hours_ratio:.2%}",
                        impact="High off-hours activity may indicate fraud",
                        mitigation=["Implement time-based controls", "Enhanced monitoring", "User verification"],
                        metadata={'off_hours_ratio': off_hours_ratio, 'off_hours_count': len(off_hours)}
                    ))
            
            # Geographic anomalies
            if 'location' in df.columns:
                locations = df['location'].value_counts()
                total_transactions = len(df)
                
                # High number of unique locations
                unique_locations = len(locations)
                location_ratio = unique_locations / total_transactions if total_transactions > 0 else 0
                
                if location_ratio > 0.8:  # More than 80% unique locations
                    geo_score = min(1.0, location_ratio)
                    
                    risk_factors.append(RiskFactor(
                        type=RiskType.FRAUD,
                        score=geo_score,
                        weight=0.3,
                        description=f"High Location Diversity: {location_ratio:.2%}",
                        impact="High location diversity may indicate fraud",
                        mitigation=["Location-based controls", "Enhanced verification", "Pattern analysis"],
                        metadata={'location_ratio': location_ratio, 'unique_locations': unique_locations}
                    ))
            
            # Calculate overall fraud risk score
            if risk_factors:
                weighted_score = sum(factor.score * factor.weight for factor in risk_factors)
                weighted_weight = sum(factor.weight for factor in risk_factors)
                overall_score = weighted_score / weighted_weight if weighted_weight > 0 else 0.0
            else:
                overall_score = 0.0
            
            return {
                'score': overall_score,
                'risk_factors': risk_factors,
                'confidence': 0.8,
                'metadata': {'analysis_type': 'fraud_risk', 'factors_analyzed': len(risk_factors)}
            }
            
        except Exception as e:
            self.logger.error(f"Fraud risk assessment failed: {str(e)}")
            return {'score': 0.0, 'risk_factors': [], 'confidence': 0.0, 'error': str(e)}
    
    async def assess_liquidity_risk(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess liquidity risk factors"""
        try:
            risk_factors = []
            
            # Cash flow analysis
            if 'amount' in df.columns and 'type' in df.columns:
                inflows = df[df['type'] == 'inflow']['amount'].sum()
                outflows = df[df['type'] == 'outflow']['amount'].sum()
                
                if outflows > 0:
                    liquidity_ratio = inflows / outflows
                    liquidity_score = max(0, 1 - liquidity_ratio)  # Lower ratio = higher risk
                    
                    risk_factors.append(RiskFactor(
                        type=RiskType.LIQUIDITY,
                        score=liquidity_score,
                        weight=0.5,
                        description=f"Liquidity Ratio: {liquidity_ratio:.2f}",
                        impact="Low liquidity ratio indicates cash flow problems",
                        mitigation=["Improve cash flow", "Reduce expenses", "Increase revenue"],
                        metadata={'liquidity_ratio': liquidity_ratio, 'inflows': inflows, 'outflows': outflows}
                    ))
            
            # Payment timing analysis
            if 'due_date' in df.columns and 'payment_date' in df.columns:
                df['due_date'] = pd.to_datetime(df['due_date'])
                df['payment_date'] = pd.to_datetime(df['payment_date'])
                df['days_late'] = (df['payment_date'] - df['due_date']).dt.days
                
                late_payments = df[df['days_late'] > 0]
                late_ratio = len(late_payments) / len(df) if len(df) > 0 else 0
                
                if late_ratio > 0.1:  # More than 10% late payments
                    timing_score = min(1.0, late_ratio * 3)
                    
                    risk_factors.append(RiskFactor(
                        type=RiskType.LIQUIDITY,
                        score=timing_score,
                        weight=0.5,
                        description=f"Late Payment Ratio: {late_ratio:.2%}",
                        impact="High late payment ratio indicates liquidity issues",
                        mitigation=["Improve cash management", "Negotiate payment terms", "Optimize payment timing"],
                        metadata={'late_ratio': late_ratio, 'late_count': len(late_payments)}
                    ))
            
            # Calculate overall liquidity risk score
            if risk_factors:
                weighted_score = sum(factor.score * factor.weight for factor in risk_factors)
                weighted_weight = sum(factor.weight for factor in risk_factors)
                overall_score = weighted_score / weighted_weight if weighted_weight > 0 else 0.0
            else:
                overall_score = 0.0
            
            return {
                'score': overall_score,
                'risk_factors': risk_factors,
                'confidence': 0.7,
                'metadata': {'analysis_type': 'liquidity_risk', 'factors_analyzed': len(risk_factors)}
            }
            
        except Exception as e:
            self.logger.error(f"Liquidity risk assessment failed: {str(e)}")
            return {'score': 0.0, 'risk_factors': [], 'confidence': 0.0, 'error': str(e)}
    
    async def comprehensive_risk_assessment(self, df: pd.DataFrame) -> RiskAssessment:
        """Perform comprehensive risk assessment"""
        try:
            # Assess all risk types
            credit_risk = await self.assess_credit_risk(df)
            operational_risk = await self.assess_operational_risk(df)
            market_risk = await self.assess_market_risk(df)
            compliance_risk = await self.assess_compliance_risk(df)
            fraud_risk = await self.assess_fraud_risk(df)
            liquidity_risk = await self.assess_liquidity_risk(df)
            
            # Combine all risk factors
            all_risk_factors = []
            all_risk_factors.extend(credit_risk.get('risk_factors', []))
            all_risk_factors.extend(operational_risk.get('risk_factors', []))
            all_risk_factors.extend(market_risk.get('risk_factors', []))
            all_risk_factors.extend(compliance_risk.get('risk_factors', []))
            all_risk_factors.extend(fraud_risk.get('risk_factors', []))
            all_risk_factors.extend(liquidity_risk.get('risk_factors', []))
            
            # Calculate weighted overall score
            overall_score = 0.0
            total_weight = 0.0
            
            for risk_type, weight in self.risk_weights.items():
                if risk_type == RiskType.CREDIT:
                    score = credit_risk.get('score', 0.0)
                elif risk_type == RiskType.OPERATIONAL:
                    score = operational_risk.get('score', 0.0)
                elif risk_type == RiskType.MARKET:
                    score = market_risk.get('score', 0.0)
                elif risk_type == RiskType.COMPLIANCE:
                    score = compliance_risk.get('score', 0.0)
                elif risk_type == RiskType.FRAUD:
                    score = fraud_risk.get('score', 0.0)
                elif risk_type == RiskType.LIQUIDITY:
                    score = liquidity_risk.get('score', 0.0)
                else:
                    score = 0.0
                
                overall_score += score * weight
                total_weight += weight
            
            overall_score = overall_score / total_weight if total_weight > 0 else 0.0
            
            # Determine risk level
            if overall_score >= 0.8:
                risk_level = RiskLevel.CRITICAL
            elif overall_score >= 0.6:
                risk_level = RiskLevel.HIGH
            elif overall_score >= 0.4:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            # Generate recommendations
            recommendations = await self._generate_risk_recommendations(
                overall_score, risk_level, all_risk_factors
            )
            
            # Calculate confidence
            confidence_scores = [
                credit_risk.get('confidence', 0.0),
                operational_risk.get('confidence', 0.0),
                market_risk.get('confidence', 0.0),
                compliance_risk.get('confidence', 0.0),
                fraud_risk.get('confidence', 0.0),
                liquidity_risk.get('confidence', 0.0)
            ]
            confidence = np.mean(confidence_scores)
            
            return RiskAssessment(
                overall_score=overall_score,
                risk_level=risk_level,
                risk_factors=all_risk_factors,
                recommendations=recommendations,
                confidence=confidence,
                metadata={
                    'user_id': self.user_id,
                    'assessment_date': datetime.now().isoformat(),
                    'risk_types_assessed': len(self.risk_weights),
                    'total_factors': len(all_risk_factors),
                    'sensitivity': self.sensitivity
                }
            )
            
        except Exception as e:
            self.logger.error(f"Comprehensive risk assessment failed: {str(e)}")
            raise
    
    async def _generate_risk_recommendations(
        self, 
        overall_score: float, 
        risk_level: RiskLevel, 
        risk_factors: List[RiskFactor]
    ) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        # Overall risk level recommendations
        if risk_level == RiskLevel.CRITICAL:
            recommendations.append("CRITICAL RISK: Immediate action required to address high-risk factors")
            recommendations.append("Implement emergency risk controls and monitoring")
        elif risk_level == RiskLevel.HIGH:
            recommendations.append("HIGH RISK: Prioritize risk mitigation efforts")
            recommendations.append("Implement enhanced monitoring and controls")
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.append("MEDIUM RISK: Monitor and address risk factors proactively")
        else:
            recommendations.append("LOW RISK: Continue current risk management practices")
        
        # Factor-specific recommendations
        for factor in risk_factors:
            if factor.score > 0.7:  # High-risk factors
                recommendations.extend(factor.mitigation)
        
        # General recommendations based on risk types
        risk_types = set(factor.type for factor in risk_factors)
        
        if RiskType.CREDIT in risk_types:
            recommendations.append("Review credit policies and monitoring procedures")
        
        if RiskType.OPERATIONAL in risk_types:
            recommendations.append("Improve operational processes and system reliability")
        
        if RiskType.MARKET in risk_types:
            recommendations.append("Implement market risk hedging strategies")
        
        if RiskType.COMPLIANCE in risk_types:
            recommendations.append("Enhance compliance monitoring and reporting")
        
        if RiskType.FRAUD in risk_types:
            recommendations.append("Strengthen fraud detection and prevention measures")
        
        if RiskType.LIQUIDITY in risk_types:
            recommendations.append("Improve cash flow management and liquidity planning")
        
        return list(set(recommendations))  # Remove duplicates
