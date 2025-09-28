#!/usr/bin/env python3
"""
NEXUS Platform - ML Training API Routes
REST API endpoints for machine learning model training
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from services.ml_training_pipeline import (ModelConfig, ModelStatus, ModelType,
                                           ml_training_pipeline)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/ml", tags=["ML Training"])


@router.get("/status")
async def get_ml_status():
    """Get ML training pipeline status"""
    try:
        status = await ml_training_pipeline.get_training_status()
        return {
            "success": True,
            "data": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting ML status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train")
async def submit_training_job(
    training_request: Dict[str, Any], background_tasks: BackgroundTasks
):
    """Submit a new ML training job"""
    try:
        # Validate required fields
        required_fields = [
            "model_id",
            "name",
            "model_type",
            "target_metric",
            "features",
        ]
        for field in required_fields:
            if field not in training_request:
                raise HTTPException(
                    status_code=400, detail=f"Missing required field: {field}"
                )

        # Create model config
        config = ModelConfig(
            model_id=training_request["model_id"],
            name=training_request["name"],
            model_type=ModelType(training_request["model_type"]),
            target_metric=training_request["target_metric"],
            features=training_request["features"],
        )

        # Submit training job
        job_id = await ml_training_pipeline.submit_training_job(config)

        return {
            "success": True,
            "data": {
                "job_id": job_id,
                "model_id": config.model_id,
                "status": "submitted",
                "message": "Training job submitted successfully",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid enum value: {e}")
    except Exception as e:
        logger.error(f"Error submitting training job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs")
async def get_training_jobs():
    """Get all training jobs"""
    try:
        jobs = []
        for job in ml_training_pipeline.training_jobs.values():
            jobs.append(
                {
                    "job_id": job.job_id,
                    "model_id": job.model_config.model_id,
                    "name": job.model_config.name,
                    "model_type": job.model_config.model_type.value,
                    "status": job.status.value,
                    "created_at": job.created_at.isoformat(),
                    "started_at": job.started_at.isoformat()
                    if job.started_at
                    else None,
                    "completed_at": job.completed_at.isoformat()
                    if job.completed_at
                    else None,
                    "error_message": job.error_message,
                }
            )

        return {
            "success": True,
            "data": {"jobs": jobs, "total_jobs": len(jobs)},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting training jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}")
async def get_training_job(job_id: str):
    """Get specific training job details"""
    try:
        if job_id not in ml_training_pipeline.training_jobs:
            raise HTTPException(status_code=404, detail="Training job not found")

        job = ml_training_pipeline.training_jobs[job_id]

        job_data = {
            "job_id": job.job_id,
            "model_id": job.model_config.model_id,
            "name": job.model_config.name,
            "model_type": job.model_config.model_type.value,
            "target_metric": job.model_config.target_metric,
            "features": job.model_config.features,
            "status": job.status.value,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_message": job.error_message,
        }

        if job.metrics:
            job_data["metrics"] = {
                "accuracy": job.metrics.accuracy,
                "mse": job.metrics.mse,
                "rmse": job.metrics.rmse,
                "r2_score": job.metrics.r2_score,
                "training_time": job.metrics.training_time,
            }

        return {
            "success": True,
            "data": job_data,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting training job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_ml_pipeline(background_tasks: BackgroundTasks):
    """Start the ML training pipeline"""
    try:
        if ml_training_pipeline.is_running:
            return {
                "success": True,
                "data": {"message": "ML pipeline is already running"},
                "timestamp": datetime.utcnow().isoformat(),
            }

        background_tasks.add_task(ml_training_pipeline.start)

        return {
            "success": True,
            "data": {"message": "ML pipeline started successfully"},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error starting ML pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_ml_pipeline():
    """Stop the ML training pipeline"""
    try:
        await ml_training_pipeline.stop()
        return {
            "success": True,
            "data": {"message": "ML pipeline stopped successfully"},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error stopping ML pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def get_trained_models():
    """Get list of trained models"""
    try:
        models = []
        for model_id, model in ml_training_pipeline.trained_models.items():
            # Find the job that created this model
            job = None
            for j in ml_training_pipeline.training_jobs.values():
                if (
                    j.model_config.model_id == model_id
                    and j.status == ModelStatus.COMPLETED
                ):
                    job = j
                    break

            model_info = {
                "model_id": model_id,
                "name": job.model_config.name if job else "Unknown",
                "model_type": job.model_config.model_type.value if job else "Unknown",
                "status": "trained",
                "created_at": job.created_at.isoformat() if job else None,
            }

            if job and job.metrics:
                model_info["metrics"] = {
                    "accuracy": job.metrics.accuracy,
                    "mse": job.metrics.mse,
                    "rmse": job.metrics.rmse,
                    "r2_score": job.metrics.r2_score,
                    "training_time": job.metrics.training_time,
                }

            models.append(model_info)

        return {
            "success": True,
            "data": {"models": models, "total_models": len(models)},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting trained models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def ml_health_check():
    """ML pipeline health check"""
    try:
        status = await ml_training_pipeline.get_training_status()
        return {
            "status": "healthy" if ml_training_pipeline.is_running else "stopped",
            "pipeline_running": ml_training_pipeline.is_running,
            "total_jobs": status.get("total_jobs", 0),
            "completed_jobs": status.get("completed_jobs", 0),
            "trained_models": status.get("trained_models", 0),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"ML health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
