#!/usr/bin/env python3
"""
NEXUS Platform - Predictive Analytics Routes
API endpoints for AI-powered financial insights and predictions
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
import re

from database.database import get_db
from services.predictive_analytics_service import (
    predictive_analytics_service,
    PredictiveAnalyticsError,
    InsufficientDataError,
    DataValidationError
)
from security.rbac import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/predictive", tags=["Predictive Analytics"])


class ValidatedAnalysisRequest(BaseModel):
    """Validated request model for analysis parameters"""
    days: int = Query(90, description="Number of days to analyze", ge=30, le=365)

    @validator('days')
    def validate_days(cls, v):
        if not isinstance(v, int) or v < 30 or v > 365:
            raise ValueError('Days must be an integer between 30 and 365')
        return v


class ValidatedPredictionRequest(BaseModel):
    """Validated request model for prediction parameters"""
    months: int = Query(1, description="Number of months to predict", ge=1, le=12)

    @validator('months')
    def validate_months(cls, v):
        if not isinstance(v, int) or v < 1 or v > 12:
            raise ValueError('Months must be an integer between 1 and 12')
        return v


class ValidatedBudgetRequest(BaseModel):
    """Validated request model for budget optimization parameters"""
    target_savings_rate: float = Query(0.15, description="Target savings rate (0.15 = 15%)", ge=0.05, le=0.5)

    @validator('target_savings_rate')
    def validate_savings_rate(cls, v):
        if not isinstance(v, (int, float)) or v < 0.05 or v > 0.5:
            raise ValueError('Target savings rate must be between 0.05 (5%) and 0.5 (50%)')
        return v


def sanitize_user_id(user_id: str) -> str:
    """Sanitize user ID input"""
    if not user_id or not isinstance(user_id, str):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    # Basic sanitization - allow alphanumeric, hyphens, underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
        raise HTTPException(status_code=400, detail="User ID contains invalid characters")

    # Length check
    if len(user_id) > 100:
        raise HTTPException(status_code=400, detail="User ID too long")

    return user_id


def validate_request_size(request: Request) -> None:
    """Validate request size to prevent abuse"""
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            size = int(content_length)
            max_size = 1024 * 1024  # 1MB limit
            if size > max_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"Request too large: {size} bytes (max {max_size} bytes)"
                )
        except ValueError:
            pass  # Invalid content-length header, continue


def rate_limit_check(user_id: str, endpoint: str) -> None:
    """Basic rate limiting check (placeholder for actual implementation)"""
    # This would integrate with the actual rate limiting service
    # For now, just log the request
    logger.debug(f"Rate limit check for user {user_id} on endpoint {endpoint}")


@router.get("/patterns", response_model=Dict[str, Any])
async def get_transaction_patterns(
    request: Request,
    params: ValidatedAnalysisRequest = Depends(),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get AI-powered transaction pattern analysis"""
    try:
        # Input validation and sanitization
        validate_request_size(request)
        sanitized_user_id = sanitize_user_id(user_id)
        rate_limit_check(sanitized_user_id, "patterns")

        logger.info(f"API request: transaction patterns for user {sanitized_user_id}, days={params.days}")
        result = await predictive_analytics_service.analyze_transaction_patterns(
            sanitized_user_id, db, params.days
        )
        logger.info(f"API response: transaction patterns completed for user {user_id}")
        return result
    except InsufficientDataError as e:
        logger.warning(f"Insufficient data for transaction patterns: user {user_id}, error: {e}")
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )
    except DataValidationError as e:
        logger.error(f"Data validation error for transaction patterns: user {user_id}, error: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input data: {e}"
        )
    except PredictiveAnalyticsError as e:
        logger.error(f"Predictive analytics error for transaction patterns: user {user_id}, error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {e}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in transaction patterns API for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during analysis"
        )


@router.get("/health-score", response_model=Dict[str, Any])
async def get_financial_health_score(
    request: Request,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get comprehensive financial health score with AI analysis"""
    try:
        # Input validation and sanitization
        validate_request_size(request)
        sanitized_user_id = sanitize_user_id(user_id)
        rate_limit_check(sanitized_user_id, "health-score")

        logger.info(f"API request: financial health score for user {sanitized_user_id}")
        result = await predictive_analytics_service.calculate_financial_health_score(
            sanitized_user_id, db
        )
        response_data = {
            "overall_score": result.overall_score,
            "component_scores": result.component_scores,
            "risk_level": result.risk_level.value,
            "recommendations": result.recommendations,
            "insights": result.insights,
            "confidence": result.confidence,
            "timestamp": datetime.utcnow().isoformat()
        }
        logger.info(f"API response: health score {result.overall_score}/100 for user {user_id}")
        return response_data
    except InsufficientDataError as e:
        logger.warning(f"Insufficient data for health score: user {user_id}, error: {e}")
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )
    except DataValidationError as e:
        logger.error(f"Data validation error for health score: user {user_id}, error: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input data: {e}"
        )
    except PredictiveAnalyticsError as e:
        logger.error(f"Predictive analytics error for health score: user {user_id}, error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Health score calculation failed: {e}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in health score API for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during health score calculation"
        )


@router.get("/insights", response_model=List[Dict[str, Any]])
async def get_predictive_insights(
    limit: int = Query(10, description="Maximum number of insights to return", ge=1, le=50),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get AI-generated predictive insights and recommendations"""
    try:
        insights = await predictive_analytics_service.generate_predictive_insights(
            user_id, db
        )

        # Limit results and format for API response
        limited_insights = insights[:limit]

        return [{
            "insight_id": insight.insight_id,
            "title": insight.title,
            "description": insight.description,
            "type": insight.type,
            "priority": insight.priority,
            "confidence": insight.confidence,
            "predicted_impact": insight.predicted_impact,
            "recommended_actions": insight.recommended_actions,
            "timestamp": datetime.utcnow().isoformat()
        } for insight in limited_insights]

    except Exception as e:
        logger.error(f"Error generating predictive insights for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate predictive insights"
        )


@router.get("/spending-prediction", response_model=Dict[str, Any])
async def get_spending_prediction(
    request: Request,
    params: ValidatedPredictionRequest = Depends(),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get AI-powered spending predictions for future months"""
    try:
        # Input validation and sanitization
        validate_request_size(request)
        sanitized_user_id = sanitize_user_id(user_id)
        rate_limit_check(sanitized_user_id, "spending-prediction")

        # Get historical spending data
        spending_data = await predictive_analytics_service._get_spending_data(sanitized_user_id, db)

        if not spending_data:
            return {
                "predictions": [],
                "message": "Insufficient spending data for predictions",
                "confidence": 0.0
            }

        predictions = []
        current_data = spending_data.copy()

        for i in range(months):
            # Predict next month
            next_month = predictive_analytics_service._predict_monthly_spending(current_data)
            predictions.append({
                "month": i + 1,
                "predicted_amount": round(next_month, 2),
                "confidence": max(0.5, 1.0 - (i * 0.1))  # Confidence decreases over time
            })
            # Add prediction to data for next iteration
            current_data.append(next_month)

        return {
            "predictions": predictions,
            "historical_average": round(sum(spending_data) / len(spending_data), 2),
            "trend": "increasing" if spending_data[-1] > spending_data[0] else "decreasing",
            "analysis_period_months": len(spending_data),
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error generating spending prediction for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate spending prediction"
        )


@router.get("/income-prediction", response_model=Dict[str, Any])
async def get_income_prediction(
    request: Request,
    params: ValidatedPredictionRequest = Depends(),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get AI-powered income predictions for future months"""
    try:
        # Input validation and sanitization
        validate_request_size(request)
        sanitized_user_id = sanitize_user_id(user_id)
        rate_limit_check(sanitized_user_id, "income-prediction")

        # Get historical income data
        income_data = await predictive_analytics_service._get_income_data(sanitized_user_id, db)

        if not income_data:
            return {
                "predictions": [],
                "message": "Insufficient income data for predictions",
                "confidence": 0.0
            }

        predictions = []
        current_data = income_data.copy()

        for i in range(months):
            # Predict next month
            next_month = predictive_analytics_service._predict_monthly_income(current_data)
            predictions.append({
                "month": i + 1,
                "predicted_amount": round(next_month, 2),
                "confidence": max(0.6, 1.0 - (i * 0.05))  # Income is more predictable
            })
            # Add prediction to data for next iteration
            current_data.append(next_month)

        return {
            "predictions": predictions,
            "historical_average": round(sum(income_data) / len(income_data), 2),
            "stability_score": predictive_analytics_service._score_income_stability({
                "monthly_income": sum(income_data) / len(income_data),
                "income_transaction_count": len(income_data)
            }),
            "analysis_period_months": len(income_data),
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error generating income prediction for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate income prediction"
        )


@router.get("/risk-assessment", response_model=Dict[str, Any])
async def get_risk_assessment(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get comprehensive financial risk assessment"""
    try:
        # Get expense volatility
        volatility = await predictive_analytics_service._calculate_expense_volatility(user_id, db)

        # Calculate risk factors
        risk_factors = {
            "expense_volatility": volatility,
            "income_stability": 0.8,  # Placeholder - would calculate from actual data
            "debt_ratio": 0.3,  # Placeholder
            "emergency_fund_ratio": 0.6,  # Placeholder
            "savings_rate": 0.15  # Placeholder
        }

        # Calculate overall risk score (0-100, higher = more risky)
        overall_risk = (
            risk_factors["expense_volatility"] * 0.3 +
            (1 - risk_factors["income_stability"]) * 0.25 +
            risk_factors["debt_ratio"] * 0.25 +
            (1 - risk_factors["emergency_fund_ratio"]) * 0.15 +
            (1 - risk_factors["savings_rate"]) * 0.05
        ) * 100

        # Determine risk level
        if overall_risk < 20:
            risk_level = "low"
            risk_description = "Low financial risk - you're in a strong position"
        elif overall_risk < 40:
            risk_level = "medium"
            risk_description = "Moderate financial risk - some areas need attention"
        elif overall_risk < 60:
            risk_level = "high"
            risk_description = "High financial risk - action needed to improve stability"
        else:
            risk_level = "critical"
            risk_description = "Critical financial risk - immediate action required"

        # Generate risk mitigation recommendations
        recommendations = []
        if risk_factors["expense_volatility"] > 0.3:
            recommendations.append("Reduce spending variability by creating a consistent budget")
        if risk_factors["income_stability"] < 0.7:
            recommendations.append("Diversify income sources to improve stability")
        if risk_factors["emergency_fund_ratio"] < 0.5:
            recommendations.append("Build emergency fund to cover 3-6 months of expenses")
        if risk_factors["savings_rate"] < 0.1:
            recommendations.append("Increase savings rate to at least 10% of income")

        return {
            "overall_risk_score": round(overall_risk, 1),
            "risk_level": risk_level,
            "risk_description": risk_description,
            "risk_factors": {k: round(v, 2) for k, v in risk_factors.items()},
            "recommendations": recommendations,
            "confidence": 0.85,  # Based on available data quality
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error generating risk assessment for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate risk assessment"
        )


@router.get("/budget-optimization", response_model=Dict[str, Any])
async def get_budget_optimization(
    request: Request,
    params: ValidatedBudgetRequest = Depends(),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get AI-optimized budget recommendations"""
    try:
        # Input validation and sanitization
        validate_request_size(request)
        sanitized_user_id = sanitize_user_id(user_id)
        rate_limit_check(sanitized_user_id, "budget-optimization")

        # Get current financial data
        metrics = await predictive_analytics_service._calculate_financial_metrics(sanitized_user_id, db)

        if metrics["monthly_income"] == 0:
            return {
                "message": "Income data required for budget optimization",
                "recommendations": [],
                "confidence": 0.0
            }

        # Calculate optimal budget allocations
        current_expenses = metrics["monthly_expenses"]
        target_savings = metrics["monthly_income"] * params.target_savings_rate
        disposable_income = metrics["monthly_income"] - target_savings

        # AI-based category recommendations
        category_recommendations = {}

        for category, amount in metrics["expense_categories"].items():
            monthly_amount = amount / 3  # Assuming 3 months of data
            percentage = monthly_amount / current_expenses

            # AI logic for recommendations
            if category.lower() in ['dining', 'entertainment', 'shopping']:
                if percentage > 0.15:  # More than 15% of expenses
                    recommended_percentage = 0.10
                    category_recommendations[category] = {
                        "current_percentage": round(percentage, 3),
                        "recommended_percentage": recommended_percentage,
                        "recommended_amount": round(disposable_income * recommended_percentage, 2),
                        "savings_potential": round(monthly_amount - (disposable_income * recommended_percentage), 2),
                        "priority": "high"
                    }
            elif category.lower() in ['utilities', 'insurance', 'healthcare']:
                # Essential categories - maintain or slight reduction
                recommended_percentage = min(percentage, 0.25)
                category_recommendations[category] = {
                    "current_percentage": round(percentage, 3),
                    "recommended_percentage": recommended_percentage,
                    "recommended_amount": round(disposable_income * recommended_percentage, 2),
                    "savings_potential": round(monthly_amount - (disposable_income * recommended_percentage), 2),
                    "priority": "medium"
                }

        # Calculate total potential savings
        total_savings_potential = sum(
            rec["savings_potential"] for rec in category_recommendations.values()
            if rec["savings_potential"] > 0
        )

        return {
            "current_income": round(metrics["monthly_income"], 2),
            "current_expenses": round(current_expenses, 2),
            "target_savings_rate": params.target_savings_rate,
            "target_savings_amount": round(target_savings, 2),
            "disposable_income": round(disposable_income, 2),
            "category_recommendations": category_recommendations,
            "total_savings_potential": round(total_savings_potential, 2),
            "projected_expenses": round(current_expenses - total_savings_potential, 2),
            "projected_savings_rate": round((metrics["monthly_income"] - (current_expenses - total_savings_potential)) / metrics["monthly_income"], 3),
            "confidence": 0.75,  # Based on AI analysis quality
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error generating budget optimization for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate budget optimization"
        )


@router.get("/performance", response_model=Dict[str, Any])
async def get_performance_metrics(
    user_id: str = Depends(get_current_user_id)
):
    """Get performance metrics for predictive analytics operations"""
    try:
        logger.info(f"API request: performance metrics for user {user_id}")
        metrics = predictive_analytics_service.get_performance_metrics()
        logger.info(f"API response: performance metrics retrieved for user {user_id}")
        return {
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat(),
            "service": "predictive_analytics"
        }
    except Exception as e:
        logger.error(f"Error retrieving performance metrics for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve performance metrics"
        )


@router.post("/cache/clear")
async def clear_user_cache(
    user_id: str = Depends(get_current_user_id)
):
    """Clear cached results for the current user"""
    try:
        logger.info(f"API request: clear cache for user {user_id}")
        predictive_analytics_service.clear_cache(user_id)
        logger.info(f"API response: cache cleared for user {user_id}")
        return {
            "message": "Cache cleared successfully",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error clearing cache for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to clear cache"
        )