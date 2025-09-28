#!/usr/bin/env python3
"""
NEXUS Platform - Predictive Analytics API Routes
REST API endpoints for predictive analytics and business intelligence
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from services.predictive_analytics import (AnalysisType, RiskLevel,
                                           TimeSeriesData, analytics_engine)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/analytics", tags=["Predictive Analytics"])


@router.get("/status")
async def get_analytics_status():
    """Get predictive analytics engine status"""
    try:
        summary = await analytics_engine.get_analytics_summary()
        return {
            "success": True,
            "data": summary,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting analytics status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/anomalies")
async def get_anomalies(
    hours: int = Query(24, description="Number of hours to look back"),
    metric_name: Optional[str] = Query(None, description="Filter by metric name"),
):
    """Get anomaly detection results"""
    try:
        anomalies = await analytics_engine.get_anomalies(hours)

        # Filter by metric name if specified
        if metric_name:
            anomalies = [a for a in anomalies if a["metric_name"] == metric_name]

        # Count anomalies
        anomaly_count = len([a for a in anomalies if a["is_anomaly"]])

        return {
            "success": True,
            "data": {
                "anomalies": anomalies,
                "total_anomalies": anomaly_count,
                "total_checks": len(anomalies),
                "anomaly_rate": (anomaly_count / len(anomalies) * 100)
                if anomalies
                else 0,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk-assessments")
async def get_risk_assessments(
    limit: int = Query(10, description="Number of assessments to return")
):
    """Get risk assessment results"""
    try:
        assessments = await analytics_engine.get_risk_assessments(limit)

        # Calculate risk distribution
        risk_distribution = {}
        for assessment in assessments:
            risk_level = assessment["risk_level"]
            risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1

        return {
            "success": True,
            "data": {
                "assessments": assessments,
                "total_assessments": len(assessments),
                "risk_distribution": risk_distribution,
                "latest_risk": assessments[0] if assessments else None,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting risk assessments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/trends")
async def analyze_trends(
    analysis_request: Dict[str, Any], background_tasks: BackgroundTasks
):
    """Analyze trends for a specific metric"""
    try:
        # Validate required fields
        required_fields = ["metric_name", "data"]
        for field in required_fields:
            if field not in analysis_request:
                raise HTTPException(
                    status_code=400, detail=f"Missing required field: {field}"
                )

        metric_name = analysis_request["metric_name"]
        data_points = analysis_request["data"]

        # Convert data to TimeSeriesData objects
        time_series_data = []
        for point in data_points:
            time_series_data.append(
                TimeSeriesData(
                    timestamp=datetime.fromisoformat(
                        point["timestamp"].replace("Z", "+00:00")
                    ),
                    value=point["value"],
                    metric_name=metric_name,
                    tags=point.get("tags", {}),
                )
            )

        # Perform trend analysis
        trend_analysis = await analytics_engine.time_series_analyzer.analyze_trends(
            time_series_data, metric_name
        )

        return {
            "success": True,
            "data": {
                "metric_name": metric_name,
                "trend_analysis": trend_analysis,
                "data_points_analyzed": len(time_series_data),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error analyzing trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/forecast")
async def generate_forecast(
    forecast_request: Dict[str, Any], background_tasks: BackgroundTasks
):
    """Generate forecast for a specific metric"""
    try:
        # Validate required fields
        required_fields = ["metric_name", "data"]
        for field in required_fields:
            if field not in forecast_request:
                raise HTTPException(
                    status_code=400, detail=f"Missing required field: {field}"
                )

        metric_name = forecast_request["metric_name"]
        data_points = forecast_request["data"]
        hours_ahead = forecast_request.get("hours_ahead", 24)

        # Convert data to TimeSeriesData objects
        time_series_data = []
        for point in data_points:
            time_series_data.append(
                TimeSeriesData(
                    timestamp=datetime.fromisoformat(
                        point["timestamp"].replace("Z", "+00:00")
                    ),
                    value=point["value"],
                    metric_name=metric_name,
                    tags=point.get("tags", {}),
                )
            )

        # Generate forecast
        forecast = await analytics_engine.time_series_analyzer.forecast(
            time_series_data, metric_name, hours_ahead
        )

        return {
            "success": True,
            "data": {
                "metric_name": metric_name,
                "forecast": {
                    "predicted_value": forecast.predicted_value,
                    "confidence_interval": forecast.confidence_interval,
                    "trend": forecast.trend,
                    "forecast_horizon": forecast.forecast_horizon,
                    "model_accuracy": forecast.model_accuracy,
                },
                "data_points_used": len(time_series_data),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error generating forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/anomalies")
async def detect_anomalies(
    anomaly_request: Dict[str, Any], background_tasks: BackgroundTasks
):
    """Detect anomalies in time series data"""
    try:
        # Validate required fields
        required_fields = ["metric_name", "data"]
        for field in required_fields:
            if field not in anomaly_request:
                raise HTTPException(
                    status_code=400, detail=f"Missing required field: {field}"
                )

        metric_name = anomaly_request["metric_name"]
        data_points = anomaly_request["data"]

        # Convert data to TimeSeriesData objects
        time_series_data = []
        for point in data_points:
            time_series_data.append(
                TimeSeriesData(
                    timestamp=datetime.fromisoformat(
                        point["timestamp"].replace("Z", "+00:00")
                    ),
                    value=point["value"],
                    metric_name=metric_name,
                    tags=point.get("tags", {}),
                )
            )

        # Detect anomalies
        anomalies = await analytics_engine.anomaly_detector.detect_anomalies(
            time_series_data, metric_name
        )

        # Convert to dict format
        anomaly_results = []
        for anomaly in anomalies:
            anomaly_results.append(
                {
                    "timestamp": anomaly.timestamp.isoformat(),
                    "value": anomaly.value,
                    "predicted_value": anomaly.predicted_value,
                    "anomaly_score": anomaly.anomaly_score,
                    "is_anomaly": anomaly.is_anomaly,
                    "confidence": anomaly.confidence,
                }
            )

        anomaly_count = len([a for a in anomaly_results if a["is_anomaly"]])

        return {
            "success": True,
            "data": {
                "metric_name": metric_name,
                "anomalies": anomaly_results,
                "total_anomalies": anomaly_count,
                "total_checks": len(anomaly_results),
                "anomaly_rate": (anomaly_count / len(anomaly_results) * 100)
                if anomaly_results
                else 0,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/risk")
async def assess_risk(risk_request: Dict[str, Any], background_tasks: BackgroundTasks):
    """Perform risk assessment based on system metrics"""
    try:
        # Validate required fields
        required_fields = ["metrics"]
        for field in required_fields:
            if field not in risk_request:
                raise HTTPException(
                    status_code=400, detail=f"Missing required field: {field}"
                )

        metrics = risk_request["metrics"]

        # Perform risk assessment
        risk_assessment = await analytics_engine.risk_assessment_engine.assess_risk(
            metrics
        )

        return {
            "success": True,
            "data": {
                "assessment_id": risk_assessment.assessment_id,
                "risk_level": risk_assessment.risk_level.value,
                "risk_score": risk_assessment.risk_score,
                "factors": risk_assessment.factors,
                "recommendations": risk_assessment.recommendations,
                "confidence": risk_assessment.confidence,
                "timestamp": risk_assessment.timestamp.isoformat(),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error assessing risk: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_analytics_engine(background_tasks: BackgroundTasks):
    """Start the predictive analytics engine"""
    try:
        if analytics_engine.is_running:
            return {
                "success": True,
                "data": {"message": "Analytics engine is already running"},
                "timestamp": datetime.utcnow().isoformat(),
            }

        background_tasks.add_task(analytics_engine.start)

        return {
            "success": True,
            "data": {"message": "Analytics engine started successfully"},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error starting analytics engine: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_analytics_engine():
    """Stop the predictive analytics engine"""
    try:
        await analytics_engine.stop()
        return {
            "success": True,
            "data": {"message": "Analytics engine stopped successfully"},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error stopping analytics engine: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def analytics_health_check():
    """Analytics engine health check"""
    try:
        summary = await analytics_engine.get_analytics_summary()
        return {
            "status": "healthy" if analytics_engine.is_running else "stopped",
            "engine_running": analytics_engine.is_running,
            "recent_anomalies": summary.get("recent_anomalies", 0),
            "latest_risk_level": summary.get("latest_risk_level", "unknown"),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Analytics health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.get("/metrics/summary")
async def get_metrics_summary():
    """Get comprehensive metrics summary for analytics"""
    try:
        # Get data from monitoring service
        from services.advanced_monitoring import monitoring_service

        metrics_summary = await monitoring_service.get_metrics_summary()

        # Get analytics summary
        analytics_summary = await analytics_engine.get_analytics_summary()

        return {
            "success": True,
            "data": {
                "monitoring_metrics": metrics_summary,
                "analytics_summary": analytics_summary,
                "combined_insights": {
                    "system_health": "healthy"
                    if analytics_summary.get("latest_risk_level") in ["low", "medium"]
                    else "warning",
                    "anomaly_status": "normal"
                    if analytics_summary.get("recent_anomalies", 0) < 5
                    else "elevated",
                    "risk_level": analytics_summary.get("latest_risk_level", "unknown"),
                },
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting metrics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
