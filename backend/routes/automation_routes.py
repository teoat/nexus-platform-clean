#!/usr/bin/env python3
"""
NEXUS Platform - Automation API Routes
REST API endpoints for intelligent automation engine
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..services.automation.intelligent_automation import (
    intelligent_automation_engine,
    AutomationType,
    TriggerType,
    AutomationStatus
)

router = APIRouter(prefix="/api/v1/automation", tags=["automation"])

@router.post("/rules")
async def create_automation_rule(rule_data: Dict[str, Any]):
    """Create a new automation rule"""
    try:
        rule_id = await intelligent_automation_engine.create_rule(rule_data)
        return {"rule_id": rule_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rules")
async def get_all_rules():
    """Get all automation rules"""
    try:
        rules = await intelligent_automation_engine.get_all_rules()
        return {
            "rules": [
                {
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "description": rule.description,
                    "automation_type": rule.automation_type.value,
                    "trigger_type": rule.trigger_type.value,
                    "enabled": rule.enabled,
                    "priority": rule.priority,
                    "execution_count": rule.execution_count,
                    "success_count": rule.success_count,
                    "failure_count": rule.failure_count,
                    "created_at": rule.created_at.isoformat(),
                    "last_executed": rule.last_executed.isoformat() if rule.last_executed else None
                }
                for rule in rules
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rules/{rule_id}")
async def get_rule(rule_id: str):
    """Get a specific automation rule"""
    try:
        rule = await intelligent_automation_engine.get_rule(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        return {
            "rule_id": rule.rule_id,
            "name": rule.name,
            "description": rule.description,
            "automation_type": rule.automation_type.value,
            "trigger_type": rule.trigger_type.value,
            "trigger_config": rule.trigger_config,
            "actions": rule.actions,
            "conditions": rule.conditions,
            "enabled": rule.enabled,
            "priority": rule.priority,
            "execution_count": rule.execution_count,
            "success_count": rule.success_count,
            "failure_count": rule.failure_count,
            "created_at": rule.created_at.isoformat(),
            "last_executed": rule.last_executed.isoformat() if rule.last_executed else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/rules/{rule_id}")
async def update_rule(rule_id: str, updates: Dict[str, Any]):
    """Update an automation rule"""
    try:
        success = await intelligent_automation_engine.update_rule(rule_id, updates)
        if not success:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        return {"status": "updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str):
    """Delete an automation rule"""
    try:
        success = await intelligent_automation_engine.delete_rule(rule_id)
        if not success:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rules/{rule_id}/execute")
async def execute_rule_manually(rule_id: str):
    """Manually execute an automation rule"""
    try:
        result = await intelligent_automation_engine.execute_rule_manually(rule_id)
        return {"status": "executed", "result": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/executions")
async def get_execution_history(rule_id: Optional[str] = None):
    """Get execution history for automation rules"""
    try:
        executions = await intelligent_automation_engine.get_execution_history(rule_id)
        return {
            "executions": [
                {
                    "execution_id": exec.execution_id,
                    "rule_id": exec.rule_id,
                    "status": exec.status.value,
                    "started_at": exec.started_at.isoformat(),
                    "completed_at": exec.completed_at.isoformat() if exec.completed_at else None,
                    "execution_time": exec.execution_time,
                    "result": exec.result,
                    "error_message": exec.error_message
                }
                for exec in executions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_automation_metrics():
    """Get automation engine metrics"""
    try:
        metrics = await intelligent_automation_engine.get_metrics()
        return {
            "total_rules": metrics.total_rules,
            "active_rules": metrics.active_rules,
            "total_executions": metrics.total_executions,
            "successful_executions": metrics.successful_executions,
            "failed_executions": metrics.failed_executions,
            "average_execution_time": metrics.average_execution_time,
            "automation_efficiency": metrics.automation_efficiency,
            "last_updated": metrics.last_updated.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_engine_status():
    """Get automation engine status"""
    try:
        status = await intelligent_automation_engine.get_engine_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_automation_templates():
    """Get pre-built automation templates"""
    return {
        "templates": [
            {
                "id": "daily_backup",
                "name": "Daily Backup",
                "description": "Automatically backup data every day at 2 AM",
                "automation_type": "scheduled",
                "trigger_type": "time",
                "trigger_config": {
                    "schedule": {"hour": 2, "minute": 0}
                },
                "actions": [
                    {
                        "type": "backup_data",
                        "config": {
                            "target": "database",
                            "location": "backup/daily/",
                            "retention": 30
                        }
                    }
                ]
            },
            {
                "id": "performance_optimization",
                "name": "Performance Optimization",
                "description": "Optimize system performance when CPU usage is high",
                "automation_type": "conditional",
                "trigger_type": "condition",
                "conditions": [
                    {
                        "type": "performance_condition",
                        "config": {"cpu_usage": {"greater_than": 80}}
                    }
                ],
                "actions": [
                    {
                        "type": "optimize_system",
                        "config": {
                            "target": "performance",
                            "parameters": {"cache_cleanup": True}
                        }
                    }
                ]
            },
            {
                "id": "weekly_report",
                "name": "Weekly Report",
                "description": "Generate and send weekly reports every Monday",
                "automation_type": "scheduled",
                "trigger_type": "time",
                "trigger_config": {
                    "schedule": {"day_of_week": 0, "hour": 9, "minute": 0}
                },
                "actions": [
                    {
                        "type": "generate_report",
                        "config": {
                            "report_type": "weekly_summary",
                            "format": "pdf",
                            "recipients": ["admin@nexus.com"]
                        }
                    },
                    {
                        "type": "send_notification",
                        "config": {
                            "message": "Weekly report generated successfully",
                            "recipients": ["admin@nexus.com"]
                        }
                    }
                ]
            },
            {
                "id": "resource_cleanup",
                "name": "Resource Cleanup",
                "description": "Clean up temporary files and resources",
                "automation_type": "scheduled",
                "trigger_type": "time",
                "trigger_config": {
                    "interval": 3600  # Every hour
                },
                "actions": [
                    {
                        "type": "cleanup_resources",
                        "config": {
                            "target": "temp_files",
                            "age_threshold": 24  # 24 hours
                        }
                    }
                ]
            }
        ]
    }

@router.post("/templates/{template_id}/create")
async def create_rule_from_template(template_id: str, customizations: Dict[str, Any] = None):
    """Create a rule from a template with optional customizations"""
    try:
        # Get template
        templates_response = await get_automation_templates()
        template = next((t for t in templates_response["templates"] if t["id"] == template_id), None)
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Apply customizations
        rule_data = template.copy()
        if customizations:
            rule_data.update(customizations)
        
        # Remove template-specific fields
        rule_data.pop("id", None)
        
        # Create rule
        rule_id = await intelligent_automation_engine.create_rule(rule_data)
        return {"rule_id": rule_id, "status": "created_from_template"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/capabilities")
async def get_automation_capabilities():
    """Get available automation capabilities"""
    return {
        "automation_types": {
            "scheduled": "Time-based automation",
            "event_driven": "Event-triggered automation",
            "conditional": "Condition-based automation",
            "ai_driven": "AI-prediction based automation",
            "self_optimizing": "Self-improving automation"
        },
        "trigger_types": {
            "time": "Time-based triggers",
            "event": "Event-based triggers",
            "condition": "Condition-based triggers",
            "ai_prediction": "AI prediction triggers",
            "user_action": "User action triggers"
        },
        "action_types": {
            "send_notification": "Send notifications",
            "update_data": "Update data",
            "execute_workflow": "Execute workflows",
            "generate_report": "Generate reports",
            "optimize_system": "Optimize system",
            "backup_data": "Backup data",
            "cleanup_resources": "Clean up resources",
            "scale_resources": "Scale resources"
        },
        "condition_types": {
            "time_condition": "Time-based conditions",
            "data_condition": "Data-based conditions",
            "performance_condition": "Performance conditions",
            "resource_condition": "Resource conditions",
            "user_condition": "User-based conditions"
        }
    }
