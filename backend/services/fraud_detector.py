"""
NEXUS Platform - Fraud Detector Service
AI-powered fraud detection and pattern recognition
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class FraudPattern(str, Enum):
    VELOCITY = "velocity"
    AMOUNT = "amount"
    LOCATION = "location"
    TIME = "time"
    VENDOR = "vendor"
    SEQUENCE = "sequence"
    BEHAVIORAL = "behavioral"

@dataclass
class FraudAlert:
    transaction_id: str
    pattern_type: FraudPattern
    risk_score: float
    description: str
    confidence: float
    metadata: Dict[str, Any]

class FraudDetector:
    """
    AI-powered fraud detection engine
    """
    
    def __init__(self, user_id: str, sensitivity: float = 0.8, custom_rules: List[Dict] = None):
        self.user_id = user_id
        self.sensitivity = sensitivity
        self.custom_rules = custom_rules or []
        self.logger = logging.getLogger(f"{__name__}.{user_id}")
        
        # Initialize detection models
        self.velocity_model = None
        self.amount_model = None
        self.location_model = None
        self.behavioral_model = None
        
    async def analyze_transactions(
        self, 
        transactions: List[Dict[str, Any]], 
        historical_data: Optional[List[Dict[str, Any]]] = None,
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze transactions for fraud patterns
        """
        try:
            self.logger.info(f"Starting fraud analysis for {len(transactions)} transactions")
            
            if not transactions:
                return self._create_empty_result("No transactions to analyze")
            
            # Convert to DataFrame
            df = pd.DataFrame(transactions)
            historical_df = pd.DataFrame(historical_data) if historical_data else pd.DataFrame()
            
            # Perform various fraud detection methods
            velocity_alerts = await self._detect_velocity_fraud(df, historical_df)
            amount_alerts = await self._detect_amount_fraud(df, historical_df)
            location_alerts = await self._detect_location_fraud(df, historical_df)
            time_alerts = await self._detect_time_fraud(df, historical_df)
            vendor_alerts = await self._detect_vendor_fraud(df, historical_df)
            sequence_alerts = await self._detect_sequence_fraud(df, historical_df)
            behavioral_alerts = await self._detect_behavioral_fraud(df, historical_df, user_profile)
            
            # Combine all alerts
            all_alerts = (velocity_alerts + amount_alerts + location_alerts + 
                         time_alerts + vendor_alerts + sequence_alerts + behavioral_alerts)
            
            # Calculate overall fraud score
            fraud_score = self._calculate_fraud_score(all_alerts)
            risk_level = self._determine_risk_level(fraud_score)
            
            # Get suspicious transactions
            suspicious_transactions = self._get_suspicious_transactions(df, all_alerts)
            
            # Generate patterns summary
            patterns = self._summarize_patterns(all_alerts)
            
            # Generate recommendations
            recommendations = await self._generate_fraud_recommendations(all_alerts, fraud_score)
            
            # Generate explanations
            explanations = await self._generate_fraud_explanations(all_alerts, fraud_score)
            
            result = {
                'fraud_score': fraud_score,
                'risk_level': risk_level.value,
                'patterns': patterns,
                'suspicious_transactions': suspicious_transactions,
                'alerts': all_alerts,
                'recommendations': recommendations,
                'confidence': self._calculate_confidence(all_alerts),
                'explanations': explanations,
                'metadata': {
                    'transaction_count': len(transactions),
                    'alerts_count': len(all_alerts),
                    'suspicious_count': len(suspicious_transactions),
                    'analysis_date': datetime.now().isoformat(),
                    'sensitivity': self.sensitivity
                }
            }
            
            self.logger.info(f"Fraud analysis completed with score {fraud_score}")
            return result
            
        except Exception as e:
            self.logger.error(f"Fraud analysis failed: {str(e)}")
            raise
    
    async def _detect_velocity_fraud(self, df: pd.DataFrame, historical_df: pd.DataFrame) -> List[FraudAlert]:
        """Detect velocity-based fraud patterns"""
        alerts = []
        
        try:
            if 'amount' in df.columns and 'timestamp' in df.columns:
                # Calculate transaction velocity (transactions per hour)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['hour'] = df['timestamp'].dt.floor('H')
                
                velocity_by_hour = df.groupby('hour').size()
                
                # Detect unusual velocity spikes
                mean_velocity = velocity_by_hour.mean()
                std_velocity = velocity_by_hour.std()
                threshold = mean_velocity + (2 * std_velocity)
                
                high_velocity_hours = velocity_by_hour[velocity_by_hour > threshold]
                
                for hour, count in high_velocity_hours.items():
                    risk_score = min(1.0, (count - mean_velocity) / (std_velocity + 1))
                    
                    if risk_score > self.sensitivity:
                        alerts.append(FraudAlert(
                            transaction_id=f"velocity_{hour}",
                            pattern_type=FraudPattern.VELOCITY,
                            risk_score=risk_score,
                            description=f"Unusual transaction velocity: {count} transactions in {hour}",
                            confidence=0.8,
                            metadata={'hour': hour.isoformat(), 'count': count, 'threshold': threshold}
                        ))
            
        except Exception as e:
            self.logger.error(f"Velocity fraud detection failed: {str(e)}")
        
        return alerts
    
    async def _detect_amount_fraud(self, df: pd.DataFrame, historical_df: pd.DataFrame) -> List[FraudAlert]:
        """Detect amount-based fraud patterns"""
        alerts = []
        
        try:
            if 'amount' in df.columns:
                amounts = df['amount'].abs()
                
                # Statistical analysis
                mean_amount = amounts.mean()
                std_amount = amounts.std()
                threshold = mean_amount + (3 * std_amount)
                
                # Detect unusually large transactions
                large_transactions = df[amounts > threshold]
                
                for idx, transaction in large_transactions.iterrows():
                    risk_score = min(1.0, (transaction['amount'] - mean_amount) / (std_amount + 1))
                    
                    if risk_score > self.sensitivity:
                        alerts.append(FraudAlert(
                            transaction_id=transaction.get('id', f"amount_{idx}"),
                            pattern_type=FraudPattern.AMOUNT,
                            risk_score=risk_score,
                            description=f"Unusually large transaction: ${transaction['amount']:.2f}",
                            confidence=0.9,
                            metadata={
                                'amount': transaction['amount'],
                                'mean_amount': mean_amount,
                                'threshold': threshold
                            }
                        ))
                
                # Detect round number patterns (potential test transactions)
                round_amounts = df[amounts % 100 == 0]
                if len(round_amounts) > len(df) * 0.3:  # More than 30% round amounts
                    alerts.append(FraudAlert(
                        transaction_id="round_amounts",
                        pattern_type=FraudPattern.AMOUNT,
                        risk_score=0.6,
                        description=f"High percentage of round number amounts: {len(round_amounts)}/{len(df)}",
                        confidence=0.7,
                        metadata={'round_count': len(round_amounts), 'total_count': len(df)}
                    ))
            
        except Exception as e:
            self.logger.error(f"Amount fraud detection failed: {str(e)}")
        
        return alerts
    
    async def _detect_location_fraud(self, df: pd.DataFrame, historical_df: pd.DataFrame) -> List[FraudAlert]:
        """Detect location-based fraud patterns"""
        alerts = []
        
        try:
            if 'location' in df.columns or 'merchant_location' in df.columns:
                location_col = 'location' if 'location' in df.columns else 'merchant_location'
                locations = df[location_col].dropna()
                
                if len(locations) > 0:
                    # Detect unusual locations
                    location_counts = locations.value_counts()
                    total_locations = len(location_counts)
                    
                    # If too many unique locations relative to transaction count
                    if total_locations > len(df) * 0.8:
                        alerts.append(FraudAlert(
                            transaction_id="location_diversity",
                            pattern_type=FraudPattern.LOCATION,
                            risk_score=0.7,
                            description=f"Unusual location diversity: {total_locations} unique locations for {len(df)} transactions",
                            confidence=0.6,
                            metadata={'unique_locations': total_locations, 'transaction_count': len(df)}
                        ))
                    
                    # Detect transactions from high-risk locations
                    high_risk_locations = ['Unknown', 'Online', 'International']
                    high_risk_transactions = df[df[location_col].isin(high_risk_locations)]
                    
                    if len(high_risk_transactions) > 0:
                        alerts.append(FraudAlert(
                            transaction_id="high_risk_locations",
                            pattern_type=FraudPattern.LOCATION,
                            risk_score=0.8,
                            description=f"Transactions from high-risk locations: {len(high_risk_transactions)}",
                            confidence=0.8,
                            metadata={'high_risk_count': len(high_risk_transactions)}
                        ))
            
        except Exception as e:
            self.logger.error(f"Location fraud detection failed: {str(e)}")
        
        return alerts
    
    async def _detect_time_fraud(self, df: pd.DataFrame, historical_df: pd.DataFrame) -> List[FraudAlert]:
        """Detect time-based fraud patterns"""
        alerts = []
        
        try:
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['hour'] = df['timestamp'].dt.hour
                df['day_of_week'] = df['timestamp'].dt.dayofweek
                
                # Detect unusual transaction times (e.g., very late night)
                late_night_transactions = df[(df['hour'] >= 2) & (df['hour'] <= 5)]
                if len(late_night_transactions) > len(df) * 0.2:  # More than 20% late night
                    alerts.append(FraudAlert(
                        transaction_id="late_night_transactions",
                        pattern_type=FraudPattern.TIME,
                        risk_score=0.6,
                        description=f"High percentage of late night transactions: {len(late_night_transactions)}/{len(df)}",
                        confidence=0.7,
                        metadata={'late_night_count': len(late_night_transactions), 'total_count': len(df)}
                    ))
                
                # Detect weekend transactions (if unusual for user)
                weekend_transactions = df[df['day_of_week'].isin([5, 6])]  # Saturday, Sunday
                if len(weekend_transactions) > len(df) * 0.4:  # More than 40% weekend
                    alerts.append(FraudAlert(
                        transaction_id="weekend_transactions",
                        pattern_type=FraudPattern.TIME,
                        risk_score=0.5,
                        description=f"High percentage of weekend transactions: {len(weekend_transactions)}/{len(df)}",
                        confidence=0.6,
                        metadata={'weekend_count': len(weekend_transactions), 'total_count': len(df)}
                    ))
            
        except Exception as e:
            self.logger.error(f"Time fraud detection failed: {str(e)}")
        
        return alerts
    
    async def _detect_vendor_fraud(self, df: pd.DataFrame, historical_df: pd.DataFrame) -> List[FraudAlert]:
        """Detect vendor-based fraud patterns"""
        alerts = []
        
        try:
            if 'vendor' in df.columns or 'merchant' in df.columns:
                vendor_col = 'vendor' if 'vendor' in df.columns else 'merchant'
                vendors = df[vendor_col].dropna()
                
                if len(vendors) > 0:
                    vendor_counts = vendors.value_counts()
                    
                    # Detect new vendors (not in historical data)
                    if not historical_df.empty and 'vendor' in historical_df.columns:
                        historical_vendors = set(historical_df['vendor'].dropna().unique())
                        current_vendors = set(vendors.unique())
                        new_vendors = current_vendors - historical_vendors
                        
                        if len(new_vendors) > len(current_vendors) * 0.5:  # More than 50% new vendors
                            alerts.append(FraudAlert(
                                transaction_id="new_vendors",
                                pattern_type=FraudPattern.VENDOR,
                                risk_score=0.7,
                                description=f"High percentage of new vendors: {len(new_vendors)}/{len(current_vendors)}",
                                confidence=0.8,
                                metadata={'new_vendor_count': len(new_vendors), 'total_vendors': len(current_vendors)}
                            ))
                    
                    # Detect unusual vendor patterns
                    if len(vendor_counts) > len(df) * 0.9:  # Too many unique vendors
                        alerts.append(FraudAlert(
                            transaction_id="vendor_diversity",
                            pattern_type=FraudPattern.VENDOR,
                            risk_score=0.6,
                            description=f"Unusual vendor diversity: {len(vendor_counts)} unique vendors for {len(df)} transactions",
                            confidence=0.6,
                            metadata={'unique_vendors': len(vendor_counts), 'transaction_count': len(df)}
                        ))
            
        except Exception as e:
            self.logger.error(f"Vendor fraud detection failed: {str(e)}")
        
        return alerts
    
    async def _detect_sequence_fraud(self, df: pd.DataFrame, historical_df: pd.DataFrame) -> List[FraudAlert]:
        """Detect sequence-based fraud patterns"""
        alerts = []
        
        try:
            if 'amount' in df.columns and 'timestamp' in df.columns:
                df_sorted = df.sort_values('timestamp')
                amounts = df_sorted['amount'].values
                
                # Detect sequential amounts (potential test pattern)
                sequential_count = 0
                for i in range(1, len(amounts)):
                    if abs(amounts[i] - amounts[i-1]) <= 1.0:  # Within $1
                        sequential_count += 1
                
                if sequential_count > len(amounts) * 0.3:  # More than 30% sequential
                    alerts.append(FraudAlert(
                        transaction_id="sequential_amounts",
                        pattern_type=FraudPattern.SEQUENCE,
                        risk_score=0.8,
                        description=f"Sequential amount pattern detected: {sequential_count}/{len(amounts)} transactions",
                        confidence=0.9,
                        metadata={'sequential_count': sequential_count, 'total_count': len(amounts)}
                    ))
            
        except Exception as e:
            self.logger.error(f"Sequence fraud detection failed: {str(e)}")
        
        return alerts
    
    async def _detect_behavioral_fraud(
        self, 
        df: pd.DataFrame, 
        historical_df: pd.DataFrame, 
        user_profile: Optional[Dict[str, Any]]
    ) -> List[FraudAlert]:
        """Detect behavioral fraud patterns"""
        alerts = []
        
        try:
            # Compare with user's historical behavior
            if not historical_df.empty and user_profile:
                # Analyze spending patterns
                current_avg_amount = df['amount'].mean() if 'amount' in df.columns else 0
                historical_avg_amount = historical_df['amount'].mean() if 'amount' in historical_df.columns else 0
                
                if historical_avg_amount > 0:
                    amount_deviation = abs(current_avg_amount - historical_avg_amount) / historical_avg_amount
                    
                    if amount_deviation > 0.5:  # 50% deviation from historical average
                        alerts.append(FraudAlert(
                            transaction_id="behavioral_amount_deviation",
                            pattern_type=FraudPattern.BEHAVIORAL,
                            risk_score=min(1.0, amount_deviation),
                            description=f"Significant deviation from historical spending: {amount_deviation:.1%}",
                            confidence=0.8,
                            metadata={
                                'current_avg': current_avg_amount,
                                'historical_avg': historical_avg_amount,
                                'deviation': amount_deviation
                            }
                        ))
            
        except Exception as e:
            self.logger.error(f"Behavioral fraud detection failed: {str(e)}")
        
        return alerts
    
    def _calculate_fraud_score(self, alerts: List[FraudAlert]) -> float:
        """Calculate overall fraud score from alerts"""
        if not alerts:
            return 0.0
        
        # Weighted average of alert risk scores
        total_weight = sum(alert.confidence for alert in alerts)
        if total_weight == 0:
            return 0.0
        
        weighted_score = sum(alert.risk_score * alert.confidence for alert in alerts)
        return min(1.0, weighted_score / total_weight)
    
    def _determine_risk_level(self, fraud_score: float) -> str:
        """Determine risk level based on fraud score"""
        if fraud_score >= 0.8:
            return "critical"
        elif fraud_score >= 0.6:
            return "high"
        elif fraud_score >= 0.4:
            return "medium"
        else:
            return "low"
    
    def _get_suspicious_transactions(self, df: pd.DataFrame, alerts: List[FraudAlert]) -> List[Dict[str, Any]]:
        """Get transactions flagged as suspicious"""
        suspicious = []
        
        for alert in alerts:
            if alert.transaction_id.startswith(('velocity_', 'amount_', 'location_', 'time_', 'vendor_', 'sequence_', 'behavioral_')):
                # Find corresponding transaction
                if alert.transaction_id in df.index:
                    transaction = df.loc[alert.transaction_id].to_dict()
                    transaction['fraud_alert'] = {
                        'pattern_type': alert.pattern_type.value,
                        'risk_score': alert.risk_score,
                        'description': alert.description,
                        'confidence': alert.confidence
                    }
                    suspicious.append(transaction)
        
        return suspicious
    
    def _summarize_patterns(self, alerts: List[FraudAlert]) -> List[Dict[str, Any]]:
        """Summarize detected fraud patterns"""
        pattern_summary = {}
        
        for alert in alerts:
            pattern_type = alert.pattern_type.value
            if pattern_type not in pattern_summary:
                pattern_summary[pattern_type] = {
                    'count': 0,
                    'max_risk_score': 0,
                    'descriptions': []
                }
            
            pattern_summary[pattern_type]['count'] += 1
            pattern_summary[pattern_type]['max_risk_score'] = max(
                pattern_summary[pattern_type]['max_risk_score'], 
                alert.risk_score
            )
            pattern_summary[pattern_type]['descriptions'].append(alert.description)
        
        return [
            {
                'pattern_type': pattern_type,
                'count': data['count'],
                'max_risk_score': data['max_risk_score'],
                'descriptions': data['descriptions']
            }
            for pattern_type, data in pattern_summary.items()
        ]
    
    async def _generate_fraud_recommendations(self, alerts: List[FraudAlert], fraud_score: float) -> List[str]:
        """Generate fraud prevention recommendations"""
        recommendations = []
        
        if fraud_score >= 0.8:
            recommendations.append("IMMEDIATE ACTION REQUIRED: High fraud risk detected. Review all flagged transactions immediately.")
        elif fraud_score >= 0.6:
            recommendations.append("HIGH PRIORITY: Review flagged transactions and consider additional verification.")
        elif fraud_score >= 0.4:
            recommendations.append("MEDIUM PRIORITY: Monitor flagged transactions and review patterns.")
        
        # Pattern-specific recommendations
        pattern_types = [alert.pattern_type.value for alert in alerts]
        
        if 'velocity' in pattern_types:
            recommendations.append("Consider implementing velocity limits for transactions.")
        
        if 'amount' in pattern_types:
            recommendations.append("Review large transaction approval processes.")
        
        if 'location' in pattern_types:
            recommendations.append("Implement location-based fraud detection rules.")
        
        if 'time' in pattern_types:
            recommendations.append("Consider time-based transaction restrictions.")
        
        if 'vendor' in pattern_types:
            recommendations.append("Implement vendor verification processes.")
        
        if 'sequence' in pattern_types:
            recommendations.append("Review for potential test transaction patterns.")
        
        if 'behavioral' in pattern_types:
            recommendations.append("Update user behavior profiles and monitoring rules.")
        
        return recommendations
    
    async def _generate_fraud_explanations(self, alerts: List[FraudAlert], fraud_score: float) -> Dict[str, Any]:
        """Generate explainable AI insights for fraud detection"""
        return {
            'fraud_score_explanation': f"The fraud score of {fraud_score:.2f} is calculated based on {len(alerts)} detected patterns.",
            'pattern_explanations': [
                {
                    'pattern_type': alert.pattern_type.value,
                    'description': alert.description,
                    'risk_score': alert.risk_score,
                    'confidence': alert.confidence
                }
                for alert in alerts
            ],
            'methodology': "Fraud detection uses multiple pattern recognition algorithms including statistical analysis, machine learning models, and rule-based systems.",
            'confidence_factors': [
                "Transaction velocity analysis",
                "Amount pattern detection",
                "Location-based risk assessment",
                "Temporal pattern analysis",
                "Vendor behavior analysis",
                "Sequence pattern recognition",
                "Behavioral deviation detection"
            ]
        }
    
    def _calculate_confidence(self, alerts: List[FraudAlert]) -> float:
        """Calculate overall confidence in fraud detection"""
        if not alerts:
            return 0.0
        
        return np.mean([alert.confidence for alert in alerts])
    
    def _create_empty_result(self, message: str) -> Dict[str, Any]:
        """Create empty result with message"""
        return {
            'fraud_score': 0.0,
            'risk_level': 'low',
            'patterns': [],
            'suspicious_transactions': [],
            'recommendations': [message],
            'confidence': 0.0,
            'explanations': {'error': message},
            'metadata': {'error': message}
        }
