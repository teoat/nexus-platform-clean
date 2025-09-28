#!/usr/bin/env python3
"""
NEXUS Platform - Workflow API Routes
REST API endpoints for workflow management and execution
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from services.workflow_engine import (
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowStatus,
    TaskType,
    workflow_engine,
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/workflows", tags=["Workflows"])


@router.get("/status")
async def get_workflow_status():
    """Get workflow engine status"""
    try:
        status = await workflow_engine.get_workflow_status()
        return {
            "success": True,
            "data": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting workflow status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create")
async def create_workflow(workflow_data: Dict[str, Any]):
    """Create a new workflow"""
    try:
        # Validate required fields
        required_fields = ["name", "tasks"]
        for field in required_fields:
            if field not in workflow_data:
                raise HTTPException(
                    status_code=400, detail=f"Missing required field: {field}"
                )

        # Validate tasks
        for task_data in workflow_data["tasks"]:
            if "task_id" not in task_data or "name" not in task_data or "task_type" not in task_data:
                raise HTTPException(
                    status_code=400, detail="Each task must have task_id, name, and task_type"
                )
            
            # Validate task type
            try:
                TaskType(task_data["task_type"])
            except ValueError:
                raise HTTPException(
                    status_code=400, detail=f"Invalid task type: {task_data['task_type']}"
                )

        workflow_id = await workflow_engine.create_workflow(workflow_data)
        
        return {
            "success": True,
            "data": {
                "workflow_id": workflow_id,
                "message": "Workflow created successfully",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute/{workflow_id}")
async def execute_workflow(
    workflow_id: str, 
    variables: Dict[str, Any] = None,
    background_tasks: BackgroundTasks = None
):
    """Execute a workflow"""
    try:
        execution_id = await workflow_engine.execute_workflow(workflow_id, variables)
        
        return {
            "success": True,
            "data": {
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "status": "started",
                "message": "Workflow execution started",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_workflows():
    """List all workflows"""
    try:
        workflows = []
        for workflow in workflow_engine.workflows.values():
            workflows.append({
                "workflow_id": workflow.workflow_id,
                "name": workflow.name,
                "description": workflow.description,
                "version": workflow.version,
                "status": workflow.status.value,
                "task_count": len(workflow.tasks),
                "created_at": workflow.created_at.isoformat(),
                "updated_at": workflow.updated_at.isoformat(),
                "created_by": workflow.created_by,
            })
        
        return {
            "success": True,
            "data": {
                "workflows": workflows,
                "total_workflows": len(workflows),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow details"""
    try:
        if workflow_id not in workflow_engine.workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        workflow = workflow_engine.workflows[workflow_id]
        
        workflow_data = {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "description": workflow.description,
            "version": workflow.version,
            "status": workflow.status.value,
            "tasks": [
                {
                    "task_id": task.task_id,
                    "name": task.name,
                    "task_type": task.task_type.value,
                    "config": task.config,
                    "inputs": task.inputs,
                    "outputs": task.outputs,
                    "conditions": task.conditions,
                    "retry_count": task.retry_count,
                    "timeout_seconds": task.timeout_seconds,
                    "dependencies": task.dependencies,
                }
                for task in workflow.tasks
            ],
            "variables": workflow.variables,
            "triggers": workflow.triggers,
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat(),
            "created_by": workflow.created_by,
        }
        
        return {
            "success": True,
            "data": workflow_data,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executions/list")
async def list_executions():
    """List all workflow executions"""
    try:
        executions = []
        for execution in workflow_engine.executions.values():
            executions.append({
                "execution_id": execution.execution_id,
                "workflow_id": execution.workflow_id,
                "status": execution.status.value,
                "started_at": execution.started_at.isoformat(),
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                "task_count": len(execution.task_executions),
                "triggered_by": execution.triggered_by,
                "error_message": execution.error_message,
            })
        
        return {
            "success": True,
            "data": {
                "executions": executions,
                "total_executions": len(executions),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error listing executions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executions/{execution_id}")
async def get_execution(execution_id: str):
    """Get workflow execution details"""
    try:
        if execution_id not in workflow_engine.executions:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        execution = workflow_engine.executions[execution_id]
        
        execution_data = {
            "execution_id": execution.execution_id,
            "workflow_id": execution.workflow_id,
            "status": execution.status.value,
            "started_at": execution.started_at.isoformat(),
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "variables": execution.variables,
            "result": execution.result,
            "error_message": execution.error_message,
            "triggered_by": execution.triggered_by,
            "task_executions": [
                {
                    "execution_id": task_exec.execution_id,
                    "task_id": task_exec.task_id,
                    "status": task_exec.status.value,
                    "started_at": task_exec.started_at.isoformat() if task_exec.started_at else None,
                    "completed_at": task_exec.completed_at.isoformat() if task_exec.completed_at else None,
                    "result": task_exec.result,
                    "error_message": task_exec.error_message,
                    "retry_count": task_exec.retry_count,
                }
                for task_exec in execution.task_executions
            ],
        }
        
        return {
            "success": True,
            "data": execution_data,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_workflow_engine(background_tasks: BackgroundTasks):
    """Start the workflow engine"""
    try:
        if workflow_engine.is_running:
            return {
                "success": True,
                "data": {"message": "Workflow engine is already running"},
                "timestamp": datetime.utcnow().isoformat(),
            }
        
        background_tasks.add_task(workflow_engine.start)
        
        return {
            "success": True,
            "data": {"message": "Workflow engine started successfully"},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error starting workflow engine: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_workflow_engine():
    """Stop the workflow engine"""
    try:
        await workflow_engine.stop()
        return {
            "success": True,
            "data": {"message": "Workflow engine stopped successfully"},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error stopping workflow engine: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task-types")
async def get_task_types():
    """Get available task types"""
    try:
        task_types = [
            {
                "type": task_type.value,
                "name": task_type.name,
                "description": f"Task type: {task_type.value}",
            }
            for task_type in TaskType
        ]
        
        return {
            "success": True,
            "data": {
                "task_types": task_types,
                "total_types": len(task_types),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting task types: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def workflow_health_check():
    """Workflow engine health check"""
    try:
        status = await workflow_engine.get_workflow_status()
        return {
            "status": "healthy" if workflow_engine.is_running else "stopped",
            "engine_running": workflow_engine.is_running,
            "total_workflows": status.get("total_workflows", 0),
            "active_executions": status.get("active_executions", 0),
            "completed_executions": status.get("completed_executions", 0),
            "registered_task_types": status.get("registered_task_types", 0),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Workflow health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
