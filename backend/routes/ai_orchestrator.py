"""
NEXUS Platform - AI Orchestrator API Routes
REST API endpoints for AI agent management and orchestration
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import logging

try:
    from services.ai_orchestrator import (
        AIOrchestrator, AgentType, TaskPriority, AgentTask, 
        orchestrator as global_orchestrator
    )
except ImportError:
    # Mock classes if ai_orchestrator module is not available
    class AIOrchestrator:
        def __init__(self): pass
        async def get_status(self): return {"status": "mock"}
        async def submit_task(self, **kwargs): return "mock_task_id"
        async def get_task_history(self, **kwargs): return []
        async def start(self): pass
        async def stop(self): pass
        @property
        def is_running(self): return True
    
    class AgentType:
        PERFORMANCE_OPTIMIZER = "performance_optimizer"
        SECURITY_GUARDIAN = "security_guardian"
    
    class TaskPriority:
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"
    
    class AgentTask:
        def __init__(self, **kwargs): pass
    
    global_orchestrator = AIOrchestrator()

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/ai", tags=["AI Orchestrator"])

# Dependency to get orchestrator instance
def get_orchestrator() -> AIOrchestrator:
    return global_orchestrator

@router.get("/status")
async def get_orchestrator_status(orchestrator: AIOrchestrator = Depends(get_orchestrator)):
    """Get AI orchestrator status"""
    try:
        status = await orchestrator.get_status()
        return {
            "success": True,
            "data": status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting orchestrator status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks")
async def submit_task(
    task_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    orchestrator: AIOrchestrator = Depends(get_orchestrator)
):
    """Submit a new task to the AI orchestrator"""
    try:
        # Validate required fields
        required_fields = ["agent_type", "task_type", "description", "priority"]
        for field in required_fields:
            if field not in task_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Convert string enums to enum objects
        agent_type = AgentType(task_data["agent_type"])
        priority = TaskPriority(task_data["priority"])
        
        # Submit task
        task_id = await orchestrator.submit_task(
            agent_type=agent_type,
            task_type=task_data["task_type"],
            description=task_data["description"],
            priority=priority,
            data=task_data.get("data", {})
        )
        
        return {
            "success": True,
            "data": {
                "task_id": task_id,
                "status": "submitted",
                "message": "Task submitted successfully"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid enum value: {e}")
    except Exception as e:
        logger.error(f"Error submitting task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/history")
async def get_task_history(
    limit: int = 50,
    orchestrator: AIOrchestrator = Depends(get_orchestrator)
):
    """Get task execution history"""
    try:
        history = await orchestrator.get_task_history(limit=limit)
        return {
            "success": True,
            "data": {
                "tasks": history,
                "total": len(history)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting task history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents")
async def get_agents_status(orchestrator: AIOrchestrator = Depends(get_orchestrator)):
    """Get status of all AI agents"""
    try:
        status = await orchestrator.get_status()
        agents = status.get("agents", {})
        
        return {
            "success": True,
            "data": {
                "agents": agents,
                "total_agents": len(agents)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting agents status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start")
async def start_orchestrator(
    background_tasks: BackgroundTasks,
    orchestrator: AIOrchestrator = Depends(get_orchestrator)
):
    """Start the AI orchestrator"""
    try:
        if orchestrator.is_running:
            return {
                "success": True,
                "data": {"message": "Orchestrator is already running"},
                "timestamp": datetime.utcnow().isoformat()
            }
        
        background_tasks.add_task(orchestrator.start)
        
        return {
            "success": True,
            "data": {"message": "Orchestrator started successfully"},
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error starting orchestrator: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_orchestrator(orchestrator: AIOrchestrator = Depends(get_orchestrator)):
    """Stop the AI orchestrator"""
    try:
        await orchestrator.stop()
        return {
            "success": True,
            "data": {"message": "Orchestrator stopped successfully"},
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error stopping orchestrator: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_orchestrator_metrics(orchestrator: AIOrchestrator = Depends(get_orchestrator)):
    """Get orchestrator performance metrics"""
    try:
        status = await orchestrator.get_status()
        
        # Calculate metrics
        total_agents = len(status.get("agents", {}))
        active_agents = sum(1 for agent in status.get("agents", {}).values() 
                           if agent.get("status") == "active")
        pending_tasks = status.get("task_queue_size", 0)
        completed_tasks = status.get("completed_tasks", 0)
        
        metrics = {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "pending_tasks": pending_tasks,
            "completed_tasks": completed_tasks,
            "orchestrator_running": orchestrator.is_running,
            "system_metrics": status.get("system_metrics")
        }
        
        return {
            "success": True,
            "data": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting orchestrator metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@router.get("/health")
async def ai_health_check(orchestrator: AIOrchestrator = Depends(get_orchestrator)):
    """AI orchestrator health check"""
    try:
        status = await orchestrator.get_status()
        
        return {
            "status": "healthy" if orchestrator.is_running else "stopped",
            "orchestrator_running": orchestrator.is_running,
            "agents_count": len(status.get("agents", {})),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
