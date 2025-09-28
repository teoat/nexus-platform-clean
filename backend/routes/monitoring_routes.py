#!/usr/bin/env python3
"""
NEXUS Platform - Advanced Monitoring API Routes
REST API endpoints for advanced monitoring and alerting
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from services.advanced_monitoring import (AlertSeverity, MetricType,
                                          monitoring_service)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/monitoring", tags=["Advanced Monitoring"])


@router.get("/status")
async def get_monitoring_status():
    """Get monitoring service status"""
    try:
        status = {
            "monitoring_running": monitoring_service.is_running,
            "timestamp": datetime.utcnow().isoformat(),
        }
        return {"success": True, "data": status}
    except Exception as e:
        logger.error(f"Error getting monitoring status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_metrics_summary():
    """Get metrics summary"""
    try:
        metrics = await monitoring_service.get_metrics_summary()
        return {
            "success": True,
            "data": metrics,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_alerts_summary():
    """Get alerts summary"""
    try:
        alerts = await monitoring_service.get_alerts_summary()
        return {
            "success": True,
            "data": alerts,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Resolve an alert"""
    try:
        await monitoring_service.resolve_alert(alert_id)
        return {
            "success": True,
            "data": {"message": f"Alert {alert_id} resolved"},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error resolving alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/rules")
async def add_alert_rule(rule_data: Dict[str, Any]):
    """Add a new alerting rule"""
    try:
        # Validate required fields
        required_fields = [
            "rule_id",
            "name",
            "metric_name",
            "condition",
            "threshold",
            "severity",
        ]
        for field in required_fields:
            if field not in rule_data:
                raise HTTPException(
                    status_code=400, detail=f"Missing required field: {field}"
                )

        await monitoring_service.add_alert_rule(rule_data)

        return {
            "success": True,
            "data": {"message": "Alert rule added successfully"},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid enum value: {e}")
    except Exception as e:
        logger.error(f"Error adding alert rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_monitoring(background_tasks: BackgroundTasks):
    """Start the monitoring service"""
    try:
        if monitoring_service.is_running:
            return {
                "success": True,
                "data": {"message": "Monitoring service is already running"},
                "timestamp": datetime.utcnow().isoformat(),
            }

        background_tasks.add_task(monitoring_service.start)

        return {
            "success": True,
            "data": {"message": "Monitoring service started successfully"},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_monitoring():
    """Stop the monitoring service"""
    try:
        await monitoring_service.stop()
        return {
            "success": True,
            "data": {"message": "Monitoring service stopped successfully"},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def monitoring_health_check():
    """Monitoring service health check"""
    try:
        return {
            "status": "healthy" if monitoring_service.is_running else "stopped",
            "monitoring_running": monitoring_service.is_running,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Monitoring health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
