#!/usr/bin/env python3
"""
NEXUS Platform - Enhanced API Architecture
Phase 2: Advanced Features Implementation
"""

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import uuid
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our parallel task processor
from backend.services.parallel_task_processor import ParallelTaskProcessor, Task, TaskPriority, TaskStatus


class APIResponse(BaseModel):
    """Standardized API response format"""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class TaskCreateRequest(BaseModel):
    """Request model for creating tasks"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: TaskPriority = TaskPriority.MEDIUM
    function_name: str = Field(..., min_length=1)
    args: List[Any] = Field(default_factory=list)
    kwargs: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    timeout: Optional[float] = Field(None, gt=0)
    max_retries: int = Field(3, ge=0, le=10)
    retry_delay: float = Field(1.0, ge=0.1, le=60.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Initialize FastAPI app
app = FastAPI(
    title="NEXUS Platform API v2.0",
    description="Advanced task processing and management system",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Global task processor instance
task_processor = ParallelTaskProcessor(max_workers=10)

# Available task functions registry
TASK_FUNCTIONS = {
    "example_task": lambda name, duration=1.0: f"Task {name} completed",
    "data_processing": lambda data: {"processed": True, "items": len(data) if isinstance(data, list) else 1},
    "file_operation": lambda filename: f"File {filename} processed",
    "api_call": lambda url: f"API call to {url} completed",
    "database_query": lambda query: f"Query '{query}' executed",
    "email_send": lambda to, subject: f"Email sent to {to} with subject '{subject}'",
    "report_generation": lambda report_type: f"Report '{report_type}' generated",
    "backup_operation": lambda source: f"Backup of {source} completed",
    "cleanup_task": lambda target: f"Cleanup of {target} completed",
    "validation_task": lambda data: f"Validation of {len(data) if isinstance(data, list) else 'data'} completed"
}


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current user (simplified for demo)"""
    return {"user_id": "demo_user", "username": "demo"}


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    logger.info("🚀 Starting NEXUS Platform API v2.0")
    logger.info("📊 Initializing task processor...")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("🛑 Shutting down NEXUS Platform API")
    await task_processor.shutdown()


@app.get("/", response_model=APIResponse)
async def root():
    """Root endpoint with API information"""
    return APIResponse(
        success=True,
        data={
            "name": "NEXUS Platform API",
            "version": "2.0.0",
            "status": "operational",
            "features": [
                "Parallel Task Processing",
                "Priority-based Scheduling",
                "Dependency Resolution",
                "Real-time Monitoring",
                "Batch Operations"
            ]
        },
        message="Welcome to NEXUS Platform API v2.0"
    )


@app.get("/health", response_model=APIResponse)
async def health_check():
    """Health check endpoint"""
    stats = task_processor.get_statistics()
    return APIResponse(
        success=True,
        data={
            "status": "healthy",
            "timestamp": datetime.now(),
            "task_processor": {
                "active_tasks": stats["active_tasks"],
                "pending_tasks": stats["pending_tasks"],
                "success_rate": stats["success_rate"]
            }
        },
        message="System is healthy"
    )


@app.post("/tasks", response_model=APIResponse)
async def create_task(
    task_request: TaskCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Create a new task"""
    try:
        # Get the function from registry
        if task_request.function_name not in TASK_FUNCTIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown function: {task_request.function_name}"
            )
        
        function = TASK_FUNCTIONS[task_request.function_name]
        
        # Create task
        task = Task(
            name=task_request.name,
            description=task_request.description,
            priority=task_request.priority,
            function=function,
            args=tuple(task_request.args),
            kwargs=task_request.kwargs,
            dependencies=task_request.dependencies,
            timeout=task_request.timeout,
            max_retries=task_request.max_retries,
            retry_delay=task_request.retry_delay,
            metadata={
                **task_request.metadata,
                "created_by": current_user["username"],
                "api_version": "2.0.0"
            }
        )
        
        # Add task to processor
        task_id = await task_processor.add_task(task)
        
        # Execute immediately
        background_tasks.add_task(execute_single_task, task_id)
        
        return APIResponse(
            success=True,
            data={"task_id": task_id},
            message=f"Task '{task_request.name}' created successfully"
        )
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/tasks/{task_id}", response_model=APIResponse)
async def get_task(task_id: str, current_user: dict = Depends(get_current_user)):
    """Get task information"""
    try:
        if task_id not in task_processor.tasks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        task = task_processor.tasks[task_id]
        return APIResponse(
            success=True,
            data={
                "id": task.id,
                "name": task.name,
                "description": task.description,
                "priority": task.priority.value,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "dependencies": task.dependencies,
                "timeout": task.timeout,
                "max_retries": task.max_retries,
                "retry_delay": task.retry_delay,
                "metadata": task.metadata
            },
            message="Task information retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/stats", response_model=APIResponse)
async def get_system_stats(current_user: dict = Depends(get_current_user)):
    """Get system statistics"""
    try:
        stats = task_processor.get_statistics()
        
        return APIResponse(
            success=True,
            data=stats,
            message="System statistics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/functions", response_model=APIResponse)
async def list_available_functions(current_user: dict = Depends(get_current_user)):
    """List available task functions"""
    try:
        functions_info = []
        for name, func in TASK_FUNCTIONS.items():
            functions_info.append({
                "name": name,
                "description": func.__doc__ or f"Execute {name} function"
            })
        
        return APIResponse(
            success=True,
            data=functions_info,
            message=f"Retrieved {len(functions_info)} available functions"
        )
        
    except Exception as e:
        logger.error(f"Error listing functions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Background task functions
async def execute_single_task(task_id: str):
    """Execute a single task in the background"""
    try:
        if task_id in task_processor.tasks:
            task = task_processor.tasks[task_id]
            await task_processor.process_task_enhanced(task)
    except Exception as e:
        logger.error(f"Error executing single task {task_id}: {e}")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat(),
            "request_id": str(uuid.uuid4())
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
