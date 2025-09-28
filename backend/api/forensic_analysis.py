"""
NEXUS Platform - Forensic Analysis API
Comprehensive forensic financial analysis and fraud detection
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import asyncio
import logging
from enum import Enum

from ..services.forensic_analyzer import ForensicAnalyzer
from ..services.fraud_detector import FraudDetector
from ..services.reconciliation_engine import ReconciliationEngine
from ..services.risk_assessor import RiskAssessor
from ..middleware.auth import get_current_user
from ..models.user import User
from ..utils.audit_logger import audit_log

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/forensic", tags=["forensic"])

class AnalysisType(str, Enum):
    COMPREHENSIVE = "comprehensive"
    FRAUD_DETECTION = "fraud_detection"
    RECONCILIATION = "reconciliation"
    RISK_ASSESSMENT = "risk_assessment"
    PATTERN_ANALYSIS = "pattern_analysis"
    ANOMALY_DETECTION = "anomaly_detection"

class ForensicAnalysisRequest(BaseModel):
    data: Dict[str, Any] = Field(..., description="Financial data to analyze")
    analysis_type: AnalysisType = Field(..., description="Type of analysis to perform")
    options: Optional[Dict[str, Any]] = Field(None, description="Analysis configuration options")
    sensitivity: Optional[float] = Field(0.7, ge=0.0, le=1.0, description="Analysis sensitivity level")
    date_range: Optional[Dict[str, str]] = Field(None, description="Date range for analysis")
    include_explanations: bool = Field(True, description="Include explainable AI insights")

class ForensicAnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    results: Dict[str, Any]
    confidence_score: float
    risk_level: str
    recommendations: List[str]
    explanations: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any]
    created_at: datetime
    processing_time: float

class FraudDetectionRequest(BaseModel):
    transactions: List[Dict[str, Any]] = Field(..., description="Transaction data to analyze")
    rules: Optional[List[Dict[str, Any]]] = Field(None, description="Custom fraud detection rules")
    sensitivity: Optional[float] = Field(0.8, ge=0.0, le=1.0, description="Detection sensitivity level")
    historical_data: Optional[List[Dict[str, Any]]] = Field(None, description="Historical data for comparison")
    user_profile: Optional[Dict[str, Any]] = Field(None, description="User behavior profile")

class FraudDetectionResponse(BaseModel):
    fraud_score: float
    risk_level: str
    detected_patterns: List[Dict[str, Any]]
    suspicious_transactions: List[Dict[str, Any]]
    recommendations: List[str]
    confidence: float
    explanations: Dict[str, Any]
    metadata: Dict[str, Any]

class ReconciliationRequest(BaseModel):
    bank_statement: Dict[str, Any] = Field(..., description="Bank statement data")
    internal_records: List[Dict[str, Any]] = Field(..., description="Internal transaction records")
    matching_rules: Optional[Dict[str, Any]] = Field(None, description="Custom matching rules")
    tolerance: Optional[float] = Field(0.01, description="Matching tolerance")
    auto_match: bool = Field(True, description="Enable automatic matching")

class ReconciliationResponse(BaseModel):
    reconciliation_id: str
    status: str
    matched_transactions: List[Dict[str, Any]]
    unmatched_transactions: List[Dict[str, Any]]
    discrepancies: List[Dict[str, Any]]
    match_percentage: float
    confidence_score: float
    recommendations: List[str]
    audit_trail: List[Dict[str, Any]]

@router.post("/analyze", response_model=ForensicAnalysisResponse)
async def perform_forensic_analysis(
    request: ForensicAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Perform comprehensive forensic analysis on financial data
    """
    try:
        start_time = datetime.now()
        
        # Initialize forensic analyzer
        analyzer = ForensicAnalyzer(
            user_id=current_user.id,
            sensitivity=request.sensitivity,
            options=request.options or {}
        )
        
        # Perform analysis based on type
        if request.analysis_type == AnalysisType.COMPREHENSIVE:
            results = await analyzer.comprehensive_analysis(request.data)
        elif request.analysis_type == AnalysisType.FRAUD_DETECTION:
            results = await analyzer.fraud_analysis(request.data)
        elif request.analysis_type == AnalysisType.RECONCILIATION:
            results = await analyzer.reconciliation_analysis(request.data)
        elif request.analysis_type == AnalysisType.RISK_ASSESSMENT:
            results = await analyzer.risk_analysis(request.data)
        elif request.analysis_type == AnalysisType.PATTERN_ANALYSIS:
            results = await analyzer.pattern_analysis(request.data)
        elif request.analysis_type == AnalysisType.ANOMALY_DETECTION:
            results = await analyzer.anomaly_analysis(request.data)
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Generate explainable AI insights if requested
        explanations = None
        if request.include_explanations:
            explanations = await analyzer.generate_explanations(results)
        
        # Create response
        response = ForensicAnalysisResponse(
            analysis_id=f"forensic_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{current_user.id}",
            status="completed",
            results=results,
            confidence_score=results.get('confidence_score', 0.0),
            risk_level=results.get('risk_level', 'low'),
            recommendations=results.get('recommendations', []),
            explanations=explanations,
            metadata={
                'user_id': current_user.id,
                'analysis_type': request.analysis_type,
                'data_size': len(str(request.data)),
                'sensitivity': request.sensitivity
            },
            created_at=start_time,
            processing_time=processing_time
        )
        
        # Log audit trail
        background_tasks.add_task(
            audit_log,
            user_id=current_user.id,
            action="forensic_analysis",
            details={
                'analysis_type': request.analysis_type,
                'analysis_id': response.analysis_id,
                'confidence_score': response.confidence_score,
                'risk_level': response.risk_level
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Forensic analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/fraud-detection", response_model=FraudDetectionResponse)
async def detect_fraud(
    request: FraudDetectionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Detect potential fraud patterns in financial data
    """
    try:
        # Initialize fraud detector
        detector = FraudDetector(
            user_id=current_user.id,
            sensitivity=request.sensitivity,
            custom_rules=request.rules or []
        )
        
        # Perform fraud detection
        results = await detector.analyze_transactions(
            transactions=request.transactions,
            historical_data=request.historical_data,
            user_profile=request.user_profile
        )
        
        # Generate explainable insights
        explanations = await detector.generate_explanations(results)
        
        response = FraudDetectionResponse(
            fraud_score=results['fraud_score'],
            risk_level=results['risk_level'],
            detected_patterns=results['patterns'],
            suspicious_transactions=results['suspicious_transactions'],
            recommendations=results['recommendations'],
            confidence=results['confidence'],
            explanations=explanations,
            metadata={
                'user_id': current_user.id,
                'transaction_count': len(request.transactions),
                'sensitivity': request.sensitivity,
                'rules_applied': len(request.rules or [])
            }
        )
        
        # Log audit trail
        background_tasks.add_task(
            audit_log,
            user_id=current_user.id,
            action="fraud_detection",
            details={
                'fraud_score': response.fraud_score,
                'risk_level': response.risk_level,
                'suspicious_count': len(response.suspicious_transactions)
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Fraud detection failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fraud detection failed: {str(e)}")

@router.post("/reconciliation", response_model=ReconciliationResponse)
async def reconcile_transactions(
    request: ReconciliationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Reconcile bank statements with internal records
    """
    try:
        # Initialize reconciliation engine
        engine = ReconciliationEngine(
            user_id=current_user.id,
            tolerance=request.tolerance,
            auto_match=request.auto_match,
            custom_rules=request.matching_rules or {}
        )
        
        # Perform reconciliation
        results = await engine.reconcile(
            bank_statement=request.bank_statement,
            internal_records=request.internal_records
        )
        
        response = ReconciliationResponse(
            reconciliation_id=f"recon_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{current_user.id}",
            status="completed",
            matched_transactions=results['matched'],
            unmatched_transactions=results['unmatched'],
            discrepancies=results['discrepancies'],
            match_percentage=results['match_percentage'],
            confidence_score=results['confidence_score'],
            recommendations=results['recommendations'],
            audit_trail=results['audit_trail']
        )
        
        # Log audit trail
        background_tasks.add_task(
            audit_log,
            user_id=current_user.id,
            action="reconciliation",
            details={
                'reconciliation_id': response.reconciliation_id,
                'match_percentage': response.match_percentage,
                'discrepancy_count': len(response.discrepancies)
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Reconciliation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Reconciliation failed: {str(e)}")

@router.get("/analysis/{analysis_id}")
async def get_analysis_results(
    analysis_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve forensic analysis results by ID
    """
    try:
        # This would typically query a database
        # For now, return a placeholder response
        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "message": "Analysis results retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Failed to retrieve analysis results: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analysis results")

@router.get("/health")
async def health_check():
    """
    Health check endpoint for forensic analysis service
    """
    return {
        "status": "healthy",
        "service": "forensic_analysis",
        "timestamp": datetime.now().isoformat(),
        "version": "2.1.0"
    }
