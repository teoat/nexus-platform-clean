"""
NEXUS Platform - Advanced Monitoring API Routes
REST API endpoints for advanced monitoring and predictive analytics
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import logging

try:
    from services.advanced_monitoring import (
        AdvancedMonitoring, MetricType, AlertLevel, MetricData, Alert, Prediction,
        monitoring as global_monitoring
    )
except ImportError:
    # Mock classes if advanced_monitoring module is not available
    class AdvancedMonitoring:
        def __init__(self): pass
        async def get_system_status(self): return {"status": "mock"}
        async def start(self): pass
        async def stop(self): pass
        @property
        def is_running(self): return True
        @property
        def metric_collector(self): return self
        @property
        def alert_manager(self): return self
        @property
        def predictive_analyzer(self): return self
        def get_metrics(self, **kwargs): return []
        def get_active_alerts(self): return []
        def get_predictions(self, **kwargs): return []
    
    class MetricType:
        CPU = "cpu"
        MEMORY = "memory"
        DISK = "disk"
    
    class AlertLevel:
        INFO = "info"
        WARNING = "warning"
        ERROR = "error"
        CRITICAL = "critical"
    
    class MetricData:
        def __init__(self, **kwargs): pass
    
    class Alert:
        def __init__(self, **kwargs): pass
    
    class Prediction:
        def __init__(self, **kwargs): pass
    
    global_monitoring = AdvancedMonitoring()

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/monitoring", tags=["Advanced Monitoring"])

# Dependency to get monitoring instance
def get_monitoring() -> AdvancedMonitoring:
    return global_monitoring

@router.get("/status")
async def get_monitoring_status(monitoring: AdvancedMonitoring = Depends(get_monitoring)):
    """Get comprehensive monitoring status"""
    try:
        status = await monitoring.get_system_status()
        return {
            "success": True,
            "data": status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting monitoring status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_metrics(
    metric_name: Optional[str] = None,
    metric_type: Optional[str] = None,
    limit: int = 100,
    monitoring: AdvancedMonitoring = Depends(get_monitoring)
):
    """Get system metrics"""
    try:
        # Convert string to enum if provided
        metric_type_enum = None
        if metric_type:
            try:
                metric_type_enum = MetricType(metric_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid metric type: {metric_type}")
        
        metrics = monitoring.metric_collector.get_metrics(
            metric_name=metric_name,
            metric_type=metric_type_enum,
            limit=limit
        )
        
        return {
            "success": True,
            "data": {
                "metrics": [{
                    "timestamp": m.timestamp,
                    "name": m.name,
                    "value": m.value,
                    "unit": m.unit,
                    "type": m.metric_type.value
                } for m in metrics],
                "total": len(metrics)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_alerts(
    active_only: bool = True,
    monitoring: AdvancedMonitoring = Depends(get_monitoring)
):
    """Get system alerts"""
    try:
        if active_only:
            alerts = monitoring.alert_manager.get_active_alerts()
        else:
            alerts = monitoring.alert_manager.alerts
        
        return {
            "success": True,
            "data": {
                "alerts": [{
                    "id": alert.id,
                    "level": alert.level.value,
                    "title": alert.title,
                    "description": alert.description,
                    "metric_name": alert.metric_name,
                    "threshold": alert.threshold,
                    "current_value": alert.current_value,
                    "timestamp": alert.timestamp,
                    "resolved": alert.resolved
                } for alert in alerts],
                "total": len(alerts),
                "active": len(monitoring.alert_manager.get_active_alerts())
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    monitoring: AdvancedMonitoring = Depends(get_monitoring)
):
    """Resolve an alert"""
    try:
        await monitoring.alert_manager.resolve_alert(alert_id)
        return {
            "success": True,
            "data": {"message": f"Alert {alert_id} resolved successfully"},
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error resolving alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predictions")
async def get_predictions(
    metric_name: Optional[str] = None,
    monitoring: AdvancedMonitoring = Depends(get_monitoring)
):
    """Get predictive analytics predictions"""
    try:
        predictions = monitoring.predictive_analyzer.get_predictions(metric_name=metric_name)
        
        return {
            "success": True,
            "data": {
                "predictions": [{
                    "metric_name": p.metric_name,
                    "predicted_value": p.predicted_value,
                    "confidence": p.confidence,
                    "time_horizon": p.time_horizon,
                    "trend": p.trend,
                    "timestamp": p.timestamp
                } for p in predictions],
                "total": len(predictions)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def monitoring_health_check(monitoring: AdvancedMonitoring = Depends(get_monitoring)):
    """Monitoring system health check"""
    try:
        status = await monitoring.get_system_status()
        
        return {
            "status": "healthy" if monitoring.is_running else "stopped",
            "monitoring_running": monitoring.is_running,
            "health_score": status.get("health_score", 0),
            "active_alerts": status.get("active_alerts", 0),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Monitoring health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.post("/start")
async def start_monitoring(
    background_tasks: BackgroundTasks,
    monitoring: AdvancedMonitoring = Depends(get_monitoring)
):
    """Start the monitoring system"""
    try:
        if monitoring.is_running:
            return {
                "success": True,
                "data": {"message": "Monitoring is already running"},
                "timestamp": datetime.utcnow().isoformat()
            }
        
        background_tasks.add_task(monitoring.start)
        
        return {
            "success": True,
            "data": {"message": "Monitoring started successfully"},
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_monitoring(monitoring: AdvancedMonitoring = Depends(get_monitoring)):
    """Stop the monitoring system"""
    try:
        await monitoring.stop()
        return {
            "success": True,
            "data": {"message": "Monitoring stopped successfully"},
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_dashboard_data(monitoring: AdvancedMonitoring = Depends(get_monitoring)):
    """Get comprehensive dashboard data"""
    try:
        status = await monitoring.get_system_status()
        recent_metrics = monitoring.metric_collector.get_metrics(limit=20)
        active_alerts = monitoring.alert_manager.get_active_alerts()
        predictions = monitoring.predictive_analyzer.get_predictions()
        
        dashboard_data = {
            "system_health": status.get("health_score", 0),
            "active_alerts": len(active_alerts),
            "alert_summary": monitoring.alert_manager.get_alert_summary(),
            "recent_metrics": [{
                "name": m.name,
                "value": m.value,
                "unit": m.unit,
                "timestamp": m.timestamp
            } for m in recent_metrics[-10:]],
            "predictions": [{
                "metric_name": p.metric_name,
                "predicted_value": p.predicted_value,
                "confidence": p.confidence,
                "trend": p.trend
            } for p in predictions[-5:]],
            "monitoring_status": "running" if monitoring.is_running else "stopped"
        }
        
        return {
            "success": True,
            "data": dashboard_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
