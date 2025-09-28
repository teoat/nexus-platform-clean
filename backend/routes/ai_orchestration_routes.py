#!/usr/bin/env python3
"""
NEXUS Platform - AI Orchestration API Routes
REST API endpoints for advanced AI orchestration
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..services.ai_orchestration import (
    ai_orchestrator, 
    ModelType, 
    OrchestrationStrategy, 
    TaskPriority
)

router = APIRouter(prefix="/api/v1/ai-orchestration", tags=["ai-orchestration"])

@router.post("/submit")
async def submit_ai_request(
    model_type: str,
    input_data: Any,
    parameters: Dict[str, Any] = None,
    priority: int = 2
):
    """Submit a single AI request"""
    try:
        request_id = await ai_orchestrator.submit_request(
            ModelType(model_type),
            input_data,
            parameters or {},
            TaskPriority(priority)
        )
        return {"request_id": request_id, "status": "submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orchestrate")
async def create_orchestration_plan(
    tasks: List[Dict[str, Any]],
    strategy: str = "sequential"
):
    """Create an orchestration plan with multiple tasks"""
    try:
        plan_id = await ai_orchestrator.create_orchestration_plan(
            tasks,
            OrchestrationStrategy(strategy)
        )
        return {"plan_id": plan_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/response/{request_id}")
async def get_ai_response(request_id: str):
    """Get AI processing response by request ID"""
    try:
        response = await ai_orchestrator.get_response(request_id)
        if not response:
            raise HTTPException(status_code=404, detail="Response not found")
        
        return {
            "request_id": response.request_id,
            "model_type": response.model_type.value,
            "result": response.result,
            "confidence": response.confidence,
            "processing_time": response.processing_time,
            "model_version": response.model_version,
            "created_at": response.created_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plan/{plan_id}/status")
async def get_plan_status(plan_id: str):
    """Get orchestration plan status"""
    try:
        status = await ai_orchestrator.get_plan_status(plan_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_orchestrator_status():
    """Get AI orchestrator status"""
    try:
        status = await ai_orchestrator.get_orchestrator_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def get_available_models():
    """Get available AI models"""
    try:
        status = await ai_orchestrator.get_orchestrator_status()
        return {
            "available_models": status["available_models"],
            "model_registry": {
                "nlp": ["sentiment", "classification", "ner", "summarization"],
                "vision": ["object_detection", "classification", "ocr"],
                "speech": ["transcription", "emotion"],
                "analytics": ["prediction", "anomaly"],
                "workflow": ["task_optimization", "resource_allocation"],
                "security": ["threat_detection", "risk_assessment"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_orchestration_metrics():
    """Get AI orchestration performance metrics"""
    try:
        status = await ai_orchestrator.get_orchestrator_status()
        return {
            "orchestrator_uptime": "active",
            "total_requests_processed": status["performance_metrics"]["total_requests"],
            "success_rate": (
                status["performance_metrics"]["successful_requests"] / 
                max(status["performance_metrics"]["total_requests"], 1)
            ),
            "average_processing_time": status["performance_metrics"]["average_processing_time"],
            "active_requests": status["active_requests"],
            "completed_responses": status["completed_responses"],
            "orchestration_plans": status["orchestration_plans"],
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch/nlp")
async def batch_nlp_processing(
    texts: List[str],
    operations: List[str],
    priority: int = 2
):
    """Process multiple texts with multiple NLP operations"""
    try:
        request_ids = []
        for text in texts:
            for operation in operations:
                request_id = await ai_orchestrator.submit_request(
                    ModelType.NLP,
                    text,
                    {"operation": operation},
                    TaskPriority(priority)
                )
                request_ids.append(request_id)
        
        return {
            "batch_id": f"batch_{int(datetime.now().timestamp())}",
            "request_ids": request_ids,
            "total_requests": len(request_ids)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch/vision")
async def batch_vision_processing(
    image_data: List[bytes],
    operations: List[str],
    priority: int = 2
):
    """Process multiple images with multiple vision operations"""
    try:
        request_ids = []
        for image in image_data:
            for operation in operations:
                request_id = await ai_orchestrator.submit_request(
                    ModelType.VISION,
                    image,
                    {"operation": operation},
                    TaskPriority(priority)
                )
                request_ids.append(request_id)
        
        return {
            "batch_id": f"batch_{int(datetime.now().timestamp())}",
            "request_ids": request_ids,
            "total_requests": len(request_ids)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/intelligent-routing")
async def intelligent_routing(
    input_data: Any,
    context: Dict[str, Any] = None
):
    """Intelligent routing based on input data and context"""
    try:
        # Determine best model type based on input
        model_type = ModelType.NLP  # Default
        
        if isinstance(input_data, bytes):
            # Check if it's image or audio
            if context and context.get("content_type", "").startswith("image/"):
                model_type = ModelType.VISION
            elif context and context.get("content_type", "").startswith("audio/"):
                model_type = ModelType.SPEECH
        
        # Determine operation based on context
        operation = "default"
        if context:
            if context.get("task") == "sentiment":
                operation = "sentiment"
            elif context.get("task") == "detect":
                operation = "detect"
            elif context.get("task") == "transcribe":
                operation = "transcribe"
        
        request_id = await ai_orchestrator.submit_request(
            model_type,
            input_data,
            {"operation": operation},
            TaskPriority.HIGH
        )
        
        return {
            "request_id": request_id,
            "routed_model_type": model_type.value,
            "routed_operation": operation,
            "status": "submitted"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_performance_analysis():
    """Get detailed performance analysis"""
    try:
        status = await ai_orchestrator.get_orchestrator_status()
        metrics = status["performance_metrics"]
        
        return {
            "overall_performance": {
                "total_requests": metrics["total_requests"],
                "success_rate": metrics["successful_requests"] / max(metrics["total_requests"], 1),
                "failure_rate": metrics["failed_requests"] / max(metrics["total_requests"], 1),
                "average_processing_time": metrics["average_processing_time"]
            },
            "model_performance": metrics.get("models_performance", {}),
            "recommendations": [
                "Consider using parallel processing for independent tasks",
                "Implement caching for frequently requested operations",
                "Monitor model accuracy and update when needed"
            ],
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
