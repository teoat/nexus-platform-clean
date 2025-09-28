"""
NEXUS Platform - Reconciliation Engine
Automated bank statement reconciliation and matching
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

class MatchType(str, Enum):
    EXACT = "exact"
    FUZZY = "fuzzy"
    PARTIAL = "partial"
    MANUAL = "manual"

@dataclass
class MatchedTransaction:
    bank_transaction: Dict[str, Any]
    internal_transaction: Dict[str, Any]
    match_type: MatchType
    confidence: float
    match_reason: str
    metadata: Dict[str, Any]

@dataclass
class Discrepancy:
    transaction_id: str
    type: str
    description: str
    bank_amount: float
    internal_amount: float
    difference: float
    severity: str
    recommendations: List[str]

class ReconciliationEngine:
    """
    Automated bank statement reconciliation engine
    """
    
    def __init__(self, user_id: str, tolerance: float = 0.01, auto_match: bool = True, custom_rules: Dict = None):
        self.user_id = user_id
        self.tolerance = tolerance
        self.auto_match = auto_match
        self.custom_rules = custom_rules or {}
        self.logger = logging.getLogger(f"{__name__}.{user_id}")
        
        # Matching algorithms
        self.exact_matcher = ExactMatcher(tolerance)
        self.fuzzy_matcher = FuzzyMatcher(tolerance)
        self.partial_matcher = PartialMatcher(tolerance)
    
    async def reconcile(
        self, 
        bank_statement: Dict[str, Any], 
        internal_records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform reconciliation between bank statement and internal records
        """
        try:
            self.logger.info(f"Starting reconciliation for user {self.user_id}")
            
            # Extract transactions
            bank_transactions = bank_statement.get('transactions', [])
            if not bank_transactions or not internal_records:
                return self._create_empty_result("Missing bank statement or internal records")
            
            # Convert to DataFrames
            bank_df = pd.DataFrame(bank_transactions)
            internal_df = pd.DataFrame(internal_records)
            
            # Add unique IDs if not present
            bank_df = self._add_transaction_ids(bank_df, 'bank')
            internal_df = self._add_transaction_ids(internal_df, 'internal')
            
            # Perform matching
            matched_pairs = await self._perform_matching(bank_df, internal_df)
            
            # Identify unmatched transactions
            unmatched_bank = self._get_unmatched_transactions(bank_df, matched_pairs, 'bank')
            unmatched_internal = self._get_unmatched_transactions(internal_df, matched_pairs, 'internal')
            
            # Detect discrepancies
            discrepancies = await self._detect_discrepancies(matched_pairs)
            
            # Calculate metrics
            match_percentage = len(matched_pairs) / max(len(bank_transactions), len(internal_records)) * 100
            confidence_score = self._calculate_confidence_score(matched_pairs)
            
            # Generate recommendations
            recommendations = await self._generate_reconciliation_recommendations(
                matched_pairs, unmatched_bank, unmatched_internal, discrepancies
            )
            
            # Create audit trail
            audit_trail = await self._create_audit_trail(
                bank_statement, internal_records, matched_pairs, discrepancies
            )
            
            result = {
                'matched': [self._serialize_match(match) for match in matched_pairs],
                'unmatched': {
                    'bank': unmatched_bank.to_dict('records'),
                    'internal': unmatched_internal.to_dict('records')
                },
                'discrepancies': [self._serialize_discrepancy(disc) for disc in discrepancies],
                'match_percentage': match_percentage,
                'confidence_score': confidence_score,
                'recommendations': recommendations,
                'audit_trail': audit_trail,
                'metadata': {
                    'bank_transaction_count': len(bank_transactions),
                    'internal_transaction_count': len(internal_records),
                    'matched_count': len(matched_pairs),
                    'discrepancy_count': len(discrepancies),
                    'reconciliation_date': datetime.now().isoformat(),
                    'tolerance': self.tolerance
                }
            }
            
            self.logger.info(f"Reconciliation completed: {match_percentage:.1f}% matched")
            return result
            
        except Exception as e:
            self.logger.error(f"Reconciliation failed: {str(e)}")
            raise
    
    async def _perform_matching(self, bank_df: pd.DataFrame, internal_df: pd.DataFrame) -> List[MatchedTransaction]:
        """Perform multi-stage matching process"""
        matched_pairs = []
        remaining_bank = bank_df.copy()
        remaining_internal = internal_df.copy()
        
        # Stage 1: Exact matching
        exact_matches = await self.exact_matcher.match(remaining_bank, remaining_internal)
        matched_pairs.extend(exact_matches)
        remaining_bank, remaining_internal = self._remove_matched_transactions(
            remaining_bank, remaining_internal, exact_matches
        )
        
        # Stage 2: Fuzzy matching
        if not remaining_bank.empty and not remaining_internal.empty:
            fuzzy_matches = await self.fuzzy_matcher.match(remaining_bank, remaining_internal)
            matched_pairs.extend(fuzzy_matches)
            remaining_bank, remaining_internal = self._remove_matched_transactions(
                remaining_bank, remaining_internal, fuzzy_matches
            )
        
        # Stage 3: Partial matching
        if not remaining_bank.empty and not remaining_internal.empty:
            partial_matches = await self.partial_matcher.match(remaining_bank, remaining_internal)
            matched_pairs.extend(partial_matches)
        
        return matched_pairs
    
    def _add_transaction_ids(self, df: pd.DataFrame, prefix: str) -> pd.DataFrame:
        """Add unique transaction IDs if not present"""
        if 'id' not in df.columns:
            df['id'] = [f"{prefix}_{i}" for i in range(len(df))]
        return df
    
    def _remove_matched_transactions(
        self, 
        bank_df: pd.DataFrame, 
        internal_df: pd.DataFrame, 
        matches: List[MatchedTransaction]
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Remove matched transactions from remaining data"""
        matched_bank_ids = {match.bank_transaction['id'] for match in matches}
        matched_internal_ids = {match.internal_transaction['id'] for match in matches}
        
        remaining_bank = bank_df[~bank_df['id'].isin(matched_bank_ids)]
        remaining_internal = internal_df[~internal_df['id'].isin(matched_internal_ids)]
        
        return remaining_bank, remaining_internal
    
    def _get_unmatched_transactions(
        self, 
        df: pd.DataFrame, 
        matches: List[MatchedTransaction], 
        transaction_type: str
    ) -> pd.DataFrame:
        """Get transactions that couldn't be matched"""
        if transaction_type == 'bank':
            matched_ids = {match.bank_transaction['id'] for match in matches}
        else:
            matched_ids = {match.internal_transaction['id'] for match in matches}
        
        return df[~df['id'].isin(matched_ids)]
    
    async def _detect_discrepancies(self, matches: List[MatchedTransaction]) -> List[Discrepancy]:
        """Detect discrepancies in matched transactions"""
        discrepancies = []
        
        for match in matches:
            bank_amount = float(match.bank_transaction.get('amount', 0))
            internal_amount = float(match.internal_transaction.get('amount', 0))
            
            # Check amount discrepancies
            if abs(bank_amount - internal_amount) > self.tolerance:
                difference = bank_amount - internal_amount
                severity = self._determine_discrepancy_severity(abs(difference), bank_amount)
                
                discrepancies.append(Discrepancy(
                    transaction_id=match.bank_transaction['id'],
                    type="amount_mismatch",
                    description=f"Amount discrepancy: Bank ${bank_amount:.2f} vs Internal ${internal_amount:.2f}",
                    bank_amount=bank_amount,
                    internal_amount=internal_amount,
                    difference=difference,
                    severity=severity,
                    recommendations=self._get_amount_discrepancy_recommendations(difference, severity)
                ))
            
            # Check date discrepancies
            bank_date = match.bank_transaction.get('date', '')
            internal_date = match.internal_transaction.get('date', '')
            
            if bank_date and internal_date:
                try:
                    bank_dt = pd.to_datetime(bank_date)
                    internal_dt = pd.to_datetime(internal_date)
                    date_diff = abs((bank_dt - internal_dt).days)
                    
                    if date_diff > 1:  # More than 1 day difference
                        discrepancies.append(Discrepancy(
                            transaction_id=match.bank_transaction['id'],
                            type="date_mismatch",
                            description=f"Date discrepancy: Bank {bank_date} vs Internal {internal_date}",
                            bank_amount=bank_amount,
                            internal_amount=internal_amount,
                            difference=date_diff,
                            severity="medium" if date_diff <= 7 else "high",
                            recommendations=self._get_date_discrepancy_recommendations(date_diff)
                        ))
                except:
                    pass  # Skip if date parsing fails
        
        return discrepancies
    
    def _determine_discrepancy_severity(self, difference: float, amount: float) -> str:
        """Determine severity of discrepancy"""
        if amount == 0:
            return "critical"
        
        percentage = abs(difference) / abs(amount)
        
        if percentage >= 0.1:  # 10% or more
            return "critical"
        elif percentage >= 0.05:  # 5% or more
            return "high"
        elif percentage >= 0.01:  # 1% or more
            return "medium"
        else:
            return "low"
    
    def _get_amount_discrepancy_recommendations(self, difference: float, severity: str) -> List[str]:
        """Get recommendations for amount discrepancies"""
        recommendations = []
        
        if severity == "critical":
            recommendations.append("IMMEDIATE REVIEW: Critical amount discrepancy requires immediate investigation")
            recommendations.append("Verify bank statement accuracy and internal record integrity")
        elif severity == "high":
            recommendations.append("HIGH PRIORITY: Review amount discrepancy and verify transaction details")
            recommendations.append("Check for data entry errors or missing adjustments")
        elif severity == "medium":
            recommendations.append("Review amount discrepancy and verify transaction accuracy")
        else:
            recommendations.append("Minor discrepancy - verify if within acceptable tolerance")
        
        if abs(difference) > 1000:
            recommendations.append("Large amount discrepancy - consider fraud investigation")
        
        return recommendations
    
    def _get_date_discrepancy_recommendations(self, days_diff: int) -> List[str]:
        """Get recommendations for date discrepancies"""
        recommendations = []
        
        if days_diff > 30:
            recommendations.append("Significant date discrepancy - investigate timing issues")
            recommendations.append("Check for delayed posting or processing errors")
        elif days_diff > 7:
            recommendations.append("Moderate date discrepancy - verify transaction timing")
        else:
            recommendations.append("Minor date discrepancy - verify if within acceptable range")
        
        return recommendations
    
    def _calculate_confidence_score(self, matches: List[MatchedTransaction]) -> float:
        """Calculate overall confidence score for reconciliation"""
        if not matches:
            return 0.0
        
        # Weighted average of match confidences
        total_weight = sum(match.confidence for match in matches)
        if total_weight == 0:
            return 0.0
        
        weighted_confidence = sum(match.confidence for match in matches)
        return min(1.0, weighted_confidence / len(matches))
    
    async def _generate_reconciliation_recommendations(
        self,
        matches: List[MatchedTransaction],
        unmatched_bank: pd.DataFrame,
        unmatched_internal: pd.DataFrame,
        discrepancies: List[Discrepancy]
    ) -> List[str]:
        """Generate reconciliation recommendations"""
        recommendations = []
        
        # Match percentage recommendations
        total_transactions = len(matches) + len(unmatched_bank) + len(unmatched_internal)
        match_percentage = len(matches) / total_transactions * 100 if total_transactions > 0 else 0
        
        if match_percentage < 50:
            recommendations.append("LOW MATCH RATE: Review data quality and matching criteria")
        elif match_percentage < 80:
            recommendations.append("MODERATE MATCH RATE: Consider adjusting matching tolerance or rules")
        else:
            recommendations.append("GOOD MATCH RATE: Reconciliation is performing well")
        
        # Discrepancy recommendations
        if discrepancies:
            critical_discrepancies = [d for d in discrepancies if d.severity == "critical"]
            if critical_discrepancies:
                recommendations.append(f"CRITICAL: {len(critical_discrepancies)} critical discrepancies require immediate attention")
            
            high_discrepancies = [d for d in discrepancies if d.severity == "high"]
            if high_discrepancies:
                recommendations.append(f"HIGH PRIORITY: {len(high_discrepancies)} high-severity discrepancies need review")
        
        # Unmatched transaction recommendations
        if len(unmatched_bank) > 0:
            recommendations.append(f"Review {len(unmatched_bank)} unmatched bank transactions")
        
        if len(unmatched_internal) > 0:
            recommendations.append(f"Review {len(unmatched_internal)} unmatched internal transactions")
        
        # Data quality recommendations
        if len(matches) > 0:
            avg_confidence = np.mean([match.confidence for match in matches])
            if avg_confidence < 0.7:
                recommendations.append("LOW CONFIDENCE: Improve data quality for better matching")
        
        return recommendations
    
    async def _create_audit_trail(
        self,
        bank_statement: Dict[str, Any],
        internal_records: List[Dict[str, Any]],
        matches: List[MatchedTransaction],
        discrepancies: List[Discrepancy]
    ) -> List[Dict[str, Any]]:
        """Create comprehensive audit trail"""
        audit_trail = []
        
        # Reconciliation start
        audit_trail.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'reconciliation_started',
            'details': {
                'bank_transactions': len(bank_statement.get('transactions', [])),
                'internal_transactions': len(internal_records),
                'tolerance': self.tolerance
            }
        })
        
        # Matching results
        audit_trail.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'matching_completed',
            'details': {
                'matches_found': len(matches),
                'match_types': {
                    'exact': len([m for m in matches if m.match_type == MatchType.EXACT]),
                    'fuzzy': len([m for m in matches if m.match_type == MatchType.FUZZY]),
                    'partial': len([m for m in matches if m.match_type == MatchType.PARTIAL])
                }
            }
        })
        
        # Discrepancies found
        if discrepancies:
            audit_trail.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'discrepancies_detected',
                'details': {
                    'discrepancy_count': len(discrepancies),
                    'severity_breakdown': {
                        'critical': len([d for d in discrepancies if d.severity == "critical"]),
                        'high': len([d for d in discrepancies if d.severity == "high"]),
                        'medium': len([d for d in discrepancies if d.severity == "medium"]),
                        'low': len([d for d in discrepancies if d.severity == "low"])
                    }
                }
            })
        
        # Reconciliation completion
        audit_trail.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'reconciliation_completed',
            'details': {
                'total_processed': len(bank_statement.get('transactions', [])) + len(internal_records),
                'successful_matches': len(matches),
                'discrepancies_found': len(discrepancies)
            }
        })
        
        return audit_trail
    
    def _serialize_match(self, match: MatchedTransaction) -> Dict[str, Any]:
        """Serialize matched transaction for JSON response"""
        return {
            'bank_transaction': match.bank_transaction,
            'internal_transaction': match.internal_transaction,
            'match_type': match.match_type.value,
            'confidence': match.confidence,
            'match_reason': match.match_reason,
            'metadata': match.metadata
        }
    
    def _serialize_discrepancy(self, discrepancy: Discrepancy) -> Dict[str, Any]:
        """Serialize discrepancy for JSON response"""
        return {
            'transaction_id': discrepancy.transaction_id,
            'type': discrepancy.type,
            'description': discrepancy.description,
            'bank_amount': discrepancy.bank_amount,
            'internal_amount': discrepancy.internal_amount,
            'difference': discrepancy.difference,
            'severity': discrepancy.severity,
            'recommendations': discrepancy.recommendations
        }
    
    def _create_empty_result(self, message: str) -> Dict[str, Any]:
        """Create empty result with message"""
        return {
            'matched': [],
            'unmatched': {'bank': [], 'internal': []},
            'discrepancies': [],
            'match_percentage': 0.0,
            'confidence_score': 0.0,
            'recommendations': [message],
            'audit_trail': [],
            'metadata': {'error': message}
        }


# Matching algorithm classes
class ExactMatcher:
    """Exact matching algorithm"""
    
    def __init__(self, tolerance: float):
        self.tolerance = tolerance
    
    async def match(self, bank_df: pd.DataFrame, internal_df: pd.DataFrame) -> List[MatchedTransaction]:
        """Perform exact matching"""
        matches = []
        
        for _, bank_tx in bank_df.iterrows():
            for _, internal_tx in internal_df.iterrows():
                if self._is_exact_match(bank_tx, internal_tx):
                    matches.append(MatchedTransaction(
                        bank_transaction=bank_tx.to_dict(),
                        internal_transaction=internal_tx.to_dict(),
                        match_type=MatchType.EXACT,
                        confidence=1.0,
                        match_reason="Exact match on amount and date",
                        metadata={'tolerance': self.tolerance}
                    ))
        
        return matches
    
    def _is_exact_match(self, bank_tx: pd.Series, internal_tx: pd.Series) -> bool:
        """Check if transactions are exact matches"""
        # Amount match
        bank_amount = float(bank_tx.get('amount', 0))
        internal_amount = float(internal_tx.get('amount', 0))
        
        if abs(bank_amount - internal_amount) > self.tolerance:
            return False
        
        # Date match (if both have dates)
        bank_date = bank_tx.get('date', '')
        internal_date = internal_tx.get('date', '')
        
        if bank_date and internal_date:
            try:
                bank_dt = pd.to_datetime(bank_date).date()
                internal_dt = pd.to_datetime(internal_date).date()
                return bank_dt == internal_dt
            except:
                return bank_date == internal_date
        
        return True


class FuzzyMatcher:
    """Fuzzy matching algorithm"""
    
    def __init__(self, tolerance: float):
        self.tolerance = tolerance
    
    async def match(self, bank_df: pd.DataFrame, internal_df: pd.DataFrame) -> List[MatchedTransaction]:
        """Perform fuzzy matching"""
        matches = []
        
        for _, bank_tx in bank_df.iterrows():
            best_match = None
            best_confidence = 0.0
            
            for _, internal_tx in internal_df.iterrows():
                confidence = self._calculate_fuzzy_confidence(bank_tx, internal_tx)
                
                if confidence > best_confidence and confidence > 0.7:  # Minimum confidence threshold
                    best_match = internal_tx
                    best_confidence = confidence
            
            if best_match is not None:
                matches.append(MatchedTransaction(
                    bank_transaction=bank_tx.to_dict(),
                    internal_transaction=best_match.to_dict(),
                    match_type=MatchType.FUZZY,
                    confidence=best_confidence,
                    match_reason=f"Fuzzy match with {best_confidence:.2f} confidence",
                    metadata={'tolerance': self.tolerance}
                ))
        
        return matches
    
    def _calculate_fuzzy_confidence(self, bank_tx: pd.Series, internal_tx: pd.Series) -> float:
        """Calculate fuzzy matching confidence"""
        confidence = 0.0
        
        # Amount similarity (40% weight)
        bank_amount = float(bank_tx.get('amount', 0))
        internal_amount = float(internal_tx.get('amount', 0))
        
        if bank_amount != 0 and internal_amount != 0:
            amount_similarity = 1 - abs(bank_amount - internal_amount) / max(abs(bank_amount), abs(internal_amount))
            confidence += amount_similarity * 0.4
        
        # Date similarity (30% weight)
        bank_date = bank_tx.get('date', '')
        internal_date = internal_tx.get('date', '')
        
        if bank_date and internal_date:
            try:
                bank_dt = pd.to_datetime(bank_date)
                internal_dt = pd.to_datetime(internal_date)
                days_diff = abs((bank_dt - internal_dt).days)
                date_similarity = max(0, 1 - days_diff / 30)  # 30-day window
                confidence += date_similarity * 0.3
            except:
                pass
        
        # Description similarity (30% weight)
        bank_desc = str(bank_tx.get('description', '')).lower()
        internal_desc = str(internal_tx.get('description', '')).lower()
        
        if bank_desc and internal_desc:
            # Simple string similarity (could be improved with more sophisticated algorithms)
            common_words = set(bank_desc.split()) & set(internal_desc.split())
            total_words = set(bank_desc.split()) | set(internal_desc.split())
            
            if total_words:
                desc_similarity = len(common_words) / len(total_words)
                confidence += desc_similarity * 0.3
        
        return min(1.0, confidence)


class PartialMatcher:
    """Partial matching algorithm"""
    
    def __init__(self, tolerance: float):
        self.tolerance = tolerance
    
    async def match(self, bank_df: pd.DataFrame, internal_df: pd.DataFrame) -> List[MatchedTransaction]:
        """Perform partial matching"""
        matches = []
        
        for _, bank_tx in bank_df.iterrows():
            for _, internal_tx in internal_df.iterrows():
                if self._is_partial_match(bank_tx, internal_tx):
                    confidence = self._calculate_partial_confidence(bank_tx, internal_tx)
                    
                    matches.append(MatchedTransaction(
                        bank_transaction=bank_tx.to_dict(),
                        internal_transaction=internal_tx.to_dict(),
                        match_type=MatchType.PARTIAL,
                        confidence=confidence,
                        match_reason="Partial match on key fields",
                        metadata={'tolerance': self.tolerance}
                    ))
        
        return matches
    
    def _is_partial_match(self, bank_tx: pd.Series, internal_tx: pd.Series) -> bool:
        """Check if transactions are partial matches"""
        # Amount within tolerance
        bank_amount = float(bank_tx.get('amount', 0))
        internal_amount = float(internal_tx.get('amount', 0))
        
        return abs(bank_amount - internal_amount) <= self.tolerance * 2  # More lenient for partial matches
    
    def _calculate_partial_confidence(self, bank_tx: pd.Series, internal_tx: pd.Series) -> float:
        """Calculate partial matching confidence"""
        confidence = 0.5  # Base confidence for partial matches
        
        # Amount similarity
        bank_amount = float(bank_tx.get('amount', 0))
        internal_amount = float(internal_tx.get('amount', 0))
        
        if bank_amount != 0 and internal_amount != 0:
            amount_similarity = 1 - abs(bank_amount - internal_amount) / max(abs(bank_amount), abs(internal_amount))
            confidence += amount_similarity * 0.3
        
        return min(1.0, confidence)
