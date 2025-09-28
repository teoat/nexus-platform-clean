#!/usr/bin/env python3
"""
NEXUS Platform - Integration Hub API Routes
REST API endpoints for enterprise integration management
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from services.integration_hub import (
    IntegrationConfig,
    IntegrationStatus,
    IntegrationType,
    SyncDirection,
    integration_hub,
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/integrations", tags=["Integrations"])


@router.get("/status")
async def get_integration_status():
    """Get integration hub status"""
    try:
        status = await integration_hub.get_integration_status()
        return {
            "success": True,
            "data": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting integration status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create")
async def create_integration(integration_data: Dict[str, Any]):
    """Create a new integration"""
    try:
        # Validate required fields
        required_fields = ["name", "integration_type"]
        for field in required_fields:
            if field not in integration_data:
                raise HTTPException(
                    status_code=400, detail=f"Missing required field: {field}"
                )

        # Validate integration type
        try:
            IntegrationType(integration_data["integration_type"])
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid integration type: {integration_data['integration_type']}"
            )

        # Validate sync direction if provided
        if "sync_direction" in integration_data:
            try:
                SyncDirection(integration_data["sync_direction"])
            except ValueError:
                raise HTTPException(
                    status_code=400, detail=f"Invalid sync direction: {integration_data['sync_direction']}"
                )

        integration_id = await integration_hub.create_integration(integration_data)
        
        return {
            "success": True,
            "data": {
                "integration_id": integration_id,
                "message": "Integration created successfully",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test/{integration_id}")
async def test_integration(integration_id: str):
    """Test an integration connection"""
    try:
        result = await integration_hub.test_integration(integration_id)
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error testing integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/{integration_id}")
async def sync_integration(
    integration_id: str, 
    direction: Optional[str] = None,
    background_tasks: BackgroundTasks = None
):
    """Start a data synchronization job"""
    try:
        sync_direction = None
        if direction:
            try:
                sync_direction = SyncDirection(direction)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail=f"Invalid sync direction: {direction}"
                )

        job_id = await integration_hub.sync_data(integration_id, sync_direction)
        
        return {
            "success": True,
            "data": {
                "job_id": job_id,
                "integration_id": integration_id,
                "status": "started",
                "message": "Sync job started successfully",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_integrations():
    """List all integrations"""
    try:
        integrations = []
        for integration in integration_hub.integrations.values():
            integrations.append({
                "integration_id": integration.integration_id,
                "name": integration.name,
                "integration_type": integration.integration_type.value,
                "status": integration.status.value,
                "sync_direction": integration.sync_direction.value,
                "sync_frequency": integration.sync_frequency,
                "webhook_url": integration.webhook_url,
                "api_endpoints": integration.api_endpoints,
                "created_at": integration.created_at.isoformat(),
                "updated_at": integration.updated_at.isoformat(),
                "created_by": integration.created_by,
            })
        
        return {
            "success": True,
            "data": {
                "integrations": integrations,
                "total_integrations": len(integrations),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error listing integrations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{integration_id}")
async def get_integration(integration_id: str):
    """Get integration details"""
    try:
        if integration_id not in integration_hub.integrations:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        integration = integration_hub.integrations[integration_id]
        
        integration_data = {
            "integration_id": integration.integration_id,
            "name": integration.name,
            "integration_type": integration.integration_type.value,
            "status": integration.status.value,
            "config": integration.config,
            "webhook_url": integration.webhook_url,
            "api_endpoints": integration.api_endpoints,
            "sync_direction": integration.sync_direction.value,
            "sync_frequency": integration.sync_frequency,
            "retry_count": integration.retry_count,
            "timeout_seconds": integration.timeout_seconds,
            "created_at": integration.created_at.isoformat(),
            "updated_at": integration.updated_at.isoformat(),
            "created_by": integration.created_by,
        }
        
        return {
            "success": True,
            "data": integration_data,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sync-jobs/list")
async def list_sync_jobs():
    """List all sync jobs"""
    try:
        sync_jobs = []
        for job in integration_hub.sync_jobs.values():
            sync_jobs.append({
                "job_id": job.job_id,
                "integration_id": job.integration_id,
                "status": job.status,
                "started_at": job.started_at.isoformat(),
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "records_processed": job.records_processed,
                "records_successful": job.records_successful,
                "records_failed": job.records_failed,
                "sync_direction": job.sync_direction.value,
                "error_message": job.error_message,
            })
        
        return {
            "success": True,
            "data": {
                "sync_jobs": sync_jobs,
                "total_jobs": len(sync_jobs),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error listing sync jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sync-jobs/{job_id}")
async def get_sync_job(job_id: str):
    """Get sync job details"""
    try:
        if job_id not in integration_hub.sync_jobs:
            raise HTTPException(status_code=404, detail="Sync job not found")
        
        job = integration_hub.sync_jobs[job_id]
        
        job_data = {
            "job_id": job.job_id,
            "integration_id": job.integration_id,
            "status": job.status,
            "started_at": job.started_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "records_processed": job.records_processed,
            "records_successful": job.records_successful,
            "records_failed": job.records_failed,
            "sync_direction": job.sync_direction.value,
            "error_message": job.error_message,
        }
        
        return {
            "success": True,
            "data": job_data,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sync job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/webhook-events/list")
async def list_webhook_events():
    """List all webhook events"""
    try:
        webhook_events = []
        for event in integration_hub.webhook_events.values():
            webhook_events.append({
                "event_id": event.event_id,
                "integration_id": event.integration_id,
                "event_type": event.event_type,
                "received_at": event.received_at.isoformat(),
                "processed": event.processed,
                "processed_at": event.processed_at.isoformat() if event.processed_at else None,
                "error_message": event.error_message,
            })
        
        return {
            "success": True,
            "data": {
                "webhook_events": webhook_events,
                "total_events": len(webhook_events),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error listing webhook events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/webhook-events/{event_id}")
async def get_webhook_event(event_id: str):
    """Get webhook event details"""
    try:
        if event_id not in integration_hub.webhook_events:
            raise HTTPException(status_code=404, detail="Webhook event not found")
        
        event = integration_hub.webhook_events[event_id]
        
        event_data = {
            "event_id": event.event_id,
            "integration_id": event.integration_id,
            "event_type": event.event_type,
            "payload": event.payload,
            "received_at": event.received_at.isoformat(),
            "processed": event.processed,
            "processed_at": event.processed_at.isoformat() if event.processed_at else None,
            "error_message": event.error_message,
        }
        
        return {
            "success": True,
            "data": event_data,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting webhook event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook/{integration_id}")
async def receive_webhook(
    integration_id: str,
    webhook_data: Dict[str, Any]
):
    """Receive a webhook event"""
    try:
        event_type = webhook_data.get("event_type", "webhook")
        payload = webhook_data.get("payload", {})
        
        event_id = await integration_hub.receive_webhook(integration_id, event_type, payload)
        
        return {
            "success": True,
            "data": {
                "event_id": event_id,
                "integration_id": integration_id,
                "event_type": event_type,
                "message": "Webhook received successfully",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error receiving webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_integration_hub(background_tasks: BackgroundTasks):
    """Start the integration hub"""
    try:
        if integration_hub.is_running:
            return {
                "success": True,
                "data": {"message": "Integration hub is already running"},
                "timestamp": datetime.utcnow().isoformat(),
            }
        
        background_tasks.add_task(integration_hub.start)
        
        return {
            "success": True,
            "data": {"message": "Integration hub started successfully"},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error starting integration hub: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_integration_hub():
    """Stop the integration hub"""
    try:
        await integration_hub.stop()
        return {
            "success": True,
            "data": {"message": "Integration hub stopped successfully"},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error stopping integration hub: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
async def get_integration_types():
    """Get available integration types"""
    try:
        integration_types = [
            {
                "type": integration_type.value,
                "name": integration_type.name,
                "description": f"Integration type: {integration_type.value}",
            }
            for integration_type in IntegrationType
        ]
        
        return {
            "success": True,
            "data": {
                "integration_types": integration_types,
                "total_types": len(integration_types),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting integration types: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def integration_health_check():
    """Integration hub health check"""
    try:
        status = await integration_hub.get_integration_status()
        return {
            "status": "healthy" if integration_hub.is_running else "stopped",
            "hub_running": integration_hub.is_running,
            "total_integrations": status.get("total_integrations", 0),
            "active_integrations": status.get("active_integrations", 0),
            "total_sync_jobs": status.get("total_sync_jobs", 0),
            "completed_sync_jobs": status.get("completed_sync_jobs", 0),
            "total_webhook_events": status.get("total_webhook_events", 0),
            "processed_webhook_events": status.get("processed_webhook_events", 0),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Integration health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }