#!/usr/bin/env python3
"""
NEXUS Platform - System Dashboard API Routes
Comprehensive system status and metrics dashboard
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import psutil
from fastapi import APIRouter, Depends, HTTPException
from services.advanced_monitoring import monitoring_service
from services.ai_orchestrator import orchestrator
from services.intelligent_optimizer import intelligent_optimizer
from services.ssot_registry import SSOTRegistry

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/dashboard", tags=["System Dashboard"])


@router.get("/overview")
async def get_system_overview():
    """Get comprehensive system overview"""
    try:
        # Collect data from all services
        tasks = [
            orchestrator.get_status(),
            monitoring_service.get_metrics_summary(),
            monitoring_service.get_alerts_summary(),
            intelligent_optimizer.get_optimization_status(),
            _get_system_info(),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        orchestrator_status = (
            results[0] if not isinstance(results[0], Exception) else {}
        )
        metrics = results[1] if not isinstance(results[1], Exception) else {}
        alerts = results[2] if not isinstance(results[2], Exception) else {}
        optimization_status = (
            results[3] if not isinstance(results[3], Exception) else {}
        )
        system_info = results[4] if not isinstance(results[4], Exception) else {}

        # Calculate overall system health
        health_score = _calculate_health_score(
            orchestrator_status, metrics, alerts, optimization_status, system_info
        )

        overview = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_health": {
                "overall_score": health_score,
                "status": _get_health_status(health_score),
                "last_updated": datetime.now(timezone.utc).isoformat(),
            },
            "services": {
                "ai_orchestrator": {
                    "running": orchestrator.is_running,
                    "agents_count": len(orchestrator.agents),
                    "task_queue_size": orchestrator_status.get("task_queue_size", 0),
                    "completed_tasks": orchestrator_status.get("completed_tasks", 0),
                },
                "monitoring": {
                    "running": monitoring_service.is_running,
                    "metrics_collected": metrics.get("total_metrics_collected", 0),
                    "active_alerts": alerts.get("total_active_alerts", 0),
                },
                "optimization": {
                    "running": intelligent_optimizer.is_running,
                    "total_optimizations": optimization_status.get(
                        "total_optimizations", 0
                    ),
                    "success_rate": optimization_status.get("success_rate", 0),
                },
            },
            "system_metrics": {
                "cpu_usage": system_info.get("cpu_usage", 0),
                "memory_usage": system_info.get("memory_usage", 0),
                "disk_usage": system_info.get("disk_usage", 0),
                "uptime_seconds": system_info.get("uptime_seconds", 0),
            },
            "alerts_summary": {
                "active_alerts": alerts.get("total_active_alerts", 0),
                "alerts_today": alerts.get("total_alerts_today", 0),
                "critical_alerts": len(
                    [
                        alert
                        for alert in alerts.get("active_alerts", [])
                        if alert.get("severity") == "critical"
                    ]
                ),
            },
        }

        return {
            "success": True,
            "data": overview,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting system overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_detailed_metrics():
    """Get detailed system metrics"""
    try:
        # Get metrics from monitoring service
        metrics_summary = await monitoring_service.get_metrics_summary()
        system_info = await _get_system_info()

        detailed_metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_metrics": {
                "cpu": {
                    "usage_percent": system_info.get("cpu_usage", 0),
                    "load_1m": system_info.get("cpu_load_1m", 0),
                    "cores": system_info.get("cpu_cores", 0),
                },
                "memory": {
                    "usage_percent": system_info.get("memory_usage", 0),
                    "available_gb": system_info.get("memory_available_gb", 0),
                    "total_gb": system_info.get("memory_total_gb", 0),
                },
                "disk": {
                    "usage_percent": system_info.get("disk_usage", 0),
                    "free_gb": system_info.get("disk_free_gb", 0),
                    "total_gb": system_info.get("disk_total_gb", 0),
                },
                "network": {
                    "bytes_sent": system_info.get("network_bytes_sent", 0),
                    "bytes_received": system_info.get("network_bytes_received", 0),
                },
            },
            "application_metrics": metrics_summary.get("latest_metrics", {}),
            "monitoring_status": {
                "total_metrics_collected": metrics_summary.get(
                    "total_metrics_collected", 0
                ),
                "monitoring_running": monitoring_service.is_running,
            },
        }

        return {
            "success": True,
            "data": detailed_metrics,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting detailed metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_alerts_dashboard():
    """Get alerts dashboard data"""
    try:
        alerts_summary = await monitoring_service.get_alerts_summary()

        # Categorize alerts by severity
        active_alerts = alerts_summary.get("active_alerts", [])
        alerts_by_severity = {
            "critical": [
                alert for alert in active_alerts if alert.get("severity") == "critical"
            ],
            "warning": [
                alert for alert in active_alerts if alert.get("severity") == "warning"
            ],
            "info": [
                alert for alert in active_alerts if alert.get("severity") == "info"
            ],
        }

        alerts_dashboard = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_active": len(active_alerts),
                "critical": len(alerts_by_severity["critical"]),
                "warning": len(alerts_by_severity["warning"]),
                "info": len(alerts_by_severity["info"]),
                "alerts_today": alerts_summary.get("total_alerts_today", 0),
            },
            "alerts_by_severity": alerts_by_severity,
            "recent_alerts": alerts_summary.get("recent_alerts", [])[
                :10
            ],  # Last 10 alerts
        }

        return {
            "success": True,
            "data": alerts_dashboard,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting alerts dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance")
async def get_performance_dashboard():
    """Get performance dashboard data"""
    try:
        # Get optimization status
        optimization_status = await intelligent_optimizer.get_optimization_status()
        optimization_history = await intelligent_optimizer.get_optimization_history(20)

        # Get system metrics
        system_info = await _get_system_info()

        performance_dashboard = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "optimization": {
                "is_running": intelligent_optimizer.is_running,
                "total_optimizations": optimization_status.get(
                    "total_optimizations", 0
                ),
                "successful_optimizations": optimization_status.get(
                    "successful_optimizations", 0
                ),
                "success_rate": optimization_status.get("success_rate", 0),
                "average_improvement": optimization_status.get(
                    "average_improvement", 0
                ),
                "active_rules": optimization_status.get("active_rules", 0),
            },
            "recent_optimizations": optimization_history[:10],  # Last 10 optimizations
            "system_performance": {
                "cpu_usage": system_info.get("cpu_usage", 0),
                "memory_usage": system_info.get("memory_usage", 0),
                "disk_usage": system_info.get("disk_usage", 0),
                "uptime_seconds": system_info.get("uptime_seconds", 0),
            },
        }

        return {
            "success": True,
            "data": performance_dashboard,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting performance dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services")
async def get_services_status():
    """Get detailed services status"""
    try:
        # Get status from all services
        orchestrator_status = await orchestrator.get_status()
        metrics_summary = await monitoring_service.get_metrics_summary()
        alerts_summary = await monitoring_service.get_alerts_summary()
        optimization_status = await intelligent_optimizer.get_optimization_status()

        services_status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {
                "ai_orchestrator": {
                    "name": "AI Orchestrator",
                    "status": "running" if orchestrator.is_running else "stopped",
                    "health": "healthy" if orchestrator.is_running else "unhealthy",
                    "details": {
                        "agents_count": len(orchestrator.agents),
                        "task_queue_size": orchestrator_status.get(
                            "task_queue_size", 0
                        ),
                        "completed_tasks": orchestrator_status.get(
                            "completed_tasks", 0
                        ),
                        "failed_tasks": orchestrator_status.get("failed_tasks", 0),
                    },
                },
                "monitoring": {
                    "name": "Advanced Monitoring",
                    "status": "running" if monitoring_service.is_running else "stopped",
                    "health": "healthy"
                    if monitoring_service.is_running
                    else "unhealthy",
                    "details": {
                        "metrics_collected": metrics_summary.get(
                            "total_metrics_collected", 0
                        ),
                        "active_alerts": alerts_summary.get("total_active_alerts", 0),
                        "alerts_today": alerts_summary.get("total_alerts_today", 0),
                    },
                },
                "optimization": {
                    "name": "Intelligent Optimizer",
                    "status": "running"
                    if intelligent_optimizer.is_running
                    else "stopped",
                    "health": "healthy"
                    if intelligent_optimizer.is_running
                    else "unhealthy",
                    "details": {
                        "total_optimizations": optimization_status.get(
                            "total_optimizations", 0
                        ),
                        "success_rate": optimization_status.get("success_rate", 0),
                        "active_rules": optimization_status.get("active_rules", 0),
                    },
                },
            },
        }

        return {
            "success": True,
            "data": services_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting services status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _get_system_info() -> Dict[str, Any]:
    """Get basic system information"""
    try:
        # CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_load = psutil.getloadavg()[0]
        cpu_cores = psutil.cpu_count()

        # Memory usage
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        memory_available_gb = memory.available / (1024**3)
        memory_total_gb = memory.total / (1024**3)

        # Disk usage
        disk = psutil.disk_usage("/")
        disk_usage = (disk.used / disk.total) * 100
        disk_free_gb = disk.free / (1024**3)
        disk_total_gb = disk.total / (1024**3)

        # Network
        net_io = psutil.net_io_counters()

        # Uptime
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time

        return {
            "cpu_usage": cpu_usage,
            "cpu_load_1m": cpu_load,
            "cpu_cores": cpu_cores,
            "memory_usage": memory_usage,
            "memory_available_gb": memory_available_gb,
            "memory_total_gb": memory_total_gb,
            "disk_usage": disk_usage,
            "disk_free_gb": disk_free_gb,
            "disk_total_gb": disk_total_gb,
            "network_bytes_sent": net_io.bytes_sent,
            "network_bytes_received": net_io.bytes_recv,
            "uptime_seconds": uptime_seconds,
        }
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return {}


def _calculate_health_score(
    orchestrator_status: Dict,
    metrics: Dict,
    alerts: Dict,
    optimization_status: Dict,
    system_info: Dict,
) -> float:
    """Calculate overall system health score (0-100)"""
    try:
        score = 100.0

        # Deduct points for issues
        if not orchestrator_status.get("orchestrator_running", False):
            score -= 20

        if not monitoring_service.is_running:
            score -= 15

        if not intelligent_optimizer.is_running:
            score -= 10

        # System resource usage
        cpu_usage = system_info.get("cpu_usage", 0)
        if cpu_usage > 90:
            score -= 20
        elif cpu_usage > 80:
            score -= 10

        memory_usage = system_info.get("memory_usage", 0)
        if memory_usage > 90:
            score -= 15
        elif memory_usage > 80:
            score -= 8

        disk_usage = system_info.get("disk_usage", 0)
        if disk_usage > 95:
            score -= 25
        elif disk_usage > 90:
            score -= 15

        # Active alerts
        active_alerts = alerts.get("total_active_alerts", 0)
        if active_alerts > 5:
            score -= 15
        elif active_alerts > 2:
            score -= 8

        # Critical alerts
        critical_alerts = len(
            [
                alert
                for alert in alerts.get("active_alerts", [])
                if alert.get("severity") == "critical"
            ]
        )
        if critical_alerts > 0:
            score -= 20

        return max(0.0, min(100.0, score))

    except Exception as e:
        logger.error(f"Error calculating health score: {e}")
        return 50.0  # Default score if calculation fails


def _get_health_status(score: float) -> str:
    """Get health status based on score"""
    if score >= 90:
        return "excellent"
    elif score >= 80:
        return "good"
    elif score >= 70:
        return "fair"
    elif score >= 50:
        return "poor"
    else:
        return "critical"
