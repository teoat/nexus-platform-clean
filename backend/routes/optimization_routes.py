#!/usr/bin/env python3
"""
NEXUS Platform - Intelligent Optimization API Routes
REST API endpoints for intelligent system optimization
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from services.intelligent_optimizer import (OptimizationPriority,
                                            OptimizationType,
                                            intelligent_optimizer)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/optimization", tags=["Intelligent Optimization"])


@router.get("/status")
async def get_optimization_status():
    """Get optimization service status"""
    try:
        status = await intelligent_optimizer.get_optimization_status()
        return {
            "success": True,
            "data": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting optimization status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_optimization_history(limit: int = 50):
    """Get optimization history"""
    try:
        history = await intelligent_optimizer.get_optimization_history(limit)
        return {
            "success": True,
            "data": {"optimizations": history, "total": len(history)},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting optimization history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rules")
async def add_optimization_rule(rule_data: Dict[str, Any]):
    """Add a new optimization rule"""
    try:
        # Validate required fields
        required_fields = [
            "rule_id",
            "name",
            "optimization_type",
            "condition",
            "action",
            "priority",
        ]
        for field in required_fields:
            if field not in rule_data:
                raise HTTPException(
                    status_code=400, detail=f"Missing required field: {field}"
                )

        await intelligent_optimizer.add_optimization_rule(rule_data)

        return {
            "success": True,
            "data": {"message": "Optimization rule added successfully"},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid enum value: {e}")
    except Exception as e:
        logger.error(f"Error adding optimization rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/rules/{rule_id}")
async def remove_optimization_rule(rule_id: str):
    """Remove an optimization rule"""
    try:
        await intelligent_optimizer.remove_optimization_rule(rule_id)
        return {
            "success": True,
            "data": {"message": f"Optimization rule {rule_id} removed"},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error removing optimization rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_optimization(background_tasks: BackgroundTasks):
    """Start the optimization service"""
    try:
        if intelligent_optimizer.is_running:
            return {
                "success": True,
                "data": {"message": "Optimization service is already running"},
                "timestamp": datetime.utcnow().isoformat(),
            }

        background_tasks.add_task(intelligent_optimizer.start)

        return {
            "success": True,
            "data": {"message": "Optimization service started successfully"},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error starting optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_optimization():
    """Stop the optimization service"""
    try:
        await intelligent_optimizer.stop()
        return {
            "success": True,
            "data": {"message": "Optimization service stopped successfully"},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error stopping optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def optimization_health_check():
    """Optimization service health check"""
    try:
        return {
            "status": "healthy" if intelligent_optimizer.is_running else "stopped",
            "optimization_running": intelligent_optimizer.is_running,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Optimization health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
