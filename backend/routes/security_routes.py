#!/usr/bin/env python3
"""
NEXUS Platform - Security & Compliance API Routes
REST API endpoints for security management and compliance monitoring
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from services.zero_trust_security import (
    SecurityPolicy,
    AuditEvent,
    SecurityAlert,
    ComplianceCheck,
    SecurityLevel,
    ComplianceStandard,
    AuditEventType,
    ThreatLevel,
    zero_trust_security,
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/security", tags=["Security & Compliance"])


@router.get("/status")
async def get_security_status():
    """Get security framework status"""
    try:
        status = await zero_trust_security.get_security_status()
        return {
            "success": True,
            "data": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting security status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/audit/log")
async def log_audit_event(audit_data: Dict[str, Any]):
    """Log an audit event"""
    try:
        # Validate required fields
        required_fields = ["event_type", "action"]
        for field in required_fields:
            if field not in audit_data:
                raise HTTPException(
                    status_code=400, detail=f"Missing required field: {field}"
                )

        # Validate event type
        try:
            event_type = AuditEventType(audit_data["event_type"])
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid event type: {audit_data['event_type']}"
            )

        event_id = await zero_trust_security.log_audit_event(
            event_type=event_type,
            action=audit_data["action"],
            user_id=audit_data.get("user_id"),
            resource_id=audit_data.get("resource_id"),
            details=audit_data.get("details", {}),
            ip_address=audit_data.get("ip_address"),
            user_agent=audit_data.get("user_agent"),
            success=audit_data.get("success", True)
        )
        
        return {
            "success": True,
            "data": {
                "event_id": event_id,
                "message": "Audit event logged successfully",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging audit event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit/events")
async def get_audit_events(
    limit: int = 100,
    offset: int = 0,
    event_type: Optional[str] = None,
    user_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get audit events with filtering"""
    try:
        events = zero_trust_security.audit_events
        
        # Apply filters
        if event_type:
            try:
                event_type_enum = AuditEventType(event_type)
                events = [e for e in events if e.event_type == event_type_enum]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid event type: {event_type}")
        
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            events = [e for e in events if e.timestamp >= start_dt]
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            events = [e for e in events if e.timestamp <= end_dt]
        
        # Sort by timestamp (newest first)
        events.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply pagination
        total_events = len(events)
        events = events[offset:offset + limit]
        
        # Convert to response format
        event_list = []
        for event in events:
            event_list.append({
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "user_id": event.user_id,
                "resource_id": event.resource_id,
                "action": event.action,
                "details": event.details,
                "ip_address": event.ip_address,
                "user_agent": event.user_agent,
                "timestamp": event.timestamp.isoformat(),
                "success": event.success,
                "risk_score": event.risk_score,
            })
        
        return {
            "success": True,
            "data": {
                "events": event_list,
                "total_events": total_events,
                "limit": limit,
                "offset": offset,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_security_alerts(
    limit: int = 50,
    offset: int = 0,
    threat_level: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    resolved: Optional[bool] = None
):
    """Get security alerts with filtering"""
    try:
        alerts = zero_trust_security.security_alerts
        
        # Apply filters
        if threat_level:
            try:
                threat_level_enum = ThreatLevel(threat_level)
                alerts = [a for a in alerts if a.threat_level == threat_level_enum]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid threat level: {threat_level}")
        
        if acknowledged is not None:
            alerts = [a for a in alerts if a.acknowledged == acknowledged]
        
        if resolved is not None:
            alerts = [a for a in alerts if a.resolved == resolved]
        
        # Sort by timestamp (newest first)
        alerts.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply pagination
        total_alerts = len(alerts)
        alerts = alerts[offset:offset + limit]
        
        # Convert to response format
        alert_list = []
        for alert in alerts:
            alert_list.append({
                "alert_id": alert.alert_id,
                "threat_level": alert.threat_level.value,
                "alert_type": alert.alert_type,
                "title": alert.title,
                "description": alert.description,
                "source": alert.source,
                "details": alert.details,
                "timestamp": alert.timestamp.isoformat(),
                "acknowledged": alert.acknowledged,
                "resolved": alert.resolved,
                "assigned_to": alert.assigned_to,
            })
        
        return {
            "success": True,
            "data": {
                "alerts": alert_list,
                "total_alerts": total_alerts,
                "limit": limit,
                "offset": offset,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting security alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, assigned_to: Optional[str] = None):
    """Acknowledge a security alert"""
    try:
        alert = next((a for a in zero_trust_security.security_alerts if a.alert_id == alert_id), None)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.acknowledged = True
        if assigned_to:
            alert.assigned_to = assigned_to
        
        return {
            "success": True,
            "data": {
                "alert_id": alert_id,
                "message": "Alert acknowledged successfully",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Resolve a security alert"""
    try:
        alert = next((a for a in zero_trust_security.security_alerts if a.alert_id == alert_id), None)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.resolved = True
        
        return {
            "success": True,
            "data": {
                "alert_id": alert_id,
                "message": "Alert resolved successfully",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/policies")
async def get_security_policies():
    """Get security policies"""
    try:
        policies = []
        for policy in zero_trust_security.policies.values():
            policies.append({
                "policy_id": policy.policy_id,
                "name": policy.name,
                "description": policy.description,
                "policy_type": policy.policy_type,
                "rules": policy.rules,
                "compliance_standards": [std.value for std in policy.compliance_standards],
                "security_level": policy.security_level.value,
                "enabled": policy.enabled,
                "created_at": policy.created_at.isoformat(),
                "updated_at": policy.updated_at.isoformat(),
                "created_by": policy.created_by,
            })
        
        return {
            "success": True,
            "data": {
                "policies": policies,
                "total_policies": len(policies),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting security policies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compliance/checks")
async def get_compliance_checks():
    """Get compliance checks"""
    try:
        checks = []
        for check in zero_trust_security.compliance_checks.values():
            checks.append({
                "check_id": check.check_id,
                "standard": check.standard.value,
                "check_name": check.check_name,
                "description": check.description,
                "requirements": check.requirements,
                "status": check.status,
                "last_check": check.last_check.isoformat(),
                "next_check": check.next_check.isoformat(),
                "results": check.results,
                "violations": check.violations,
            })
        
        return {
            "success": True,
            "data": {
                "checks": checks,
                "total_checks": len(checks),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting compliance checks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compliance/checks/{check_id}/run")
async def run_compliance_check(check_id: str):
    """Run a specific compliance check"""
    try:
        check = zero_trust_security.compliance_checks.get(check_id)
        if not check:
            raise HTTPException(status_code=404, detail="Compliance check not found")
        
        await zero_trust_security._run_compliance_check(check)
        
        return {
            "success": True,
            "data": {
                "check_id": check_id,
                "message": "Compliance check completed",
                "status": check.status,
                "violations": check.violations,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running compliance check: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compliance/standards")
async def get_compliance_standards():
    """Get available compliance standards"""
    try:
        standards = [
            {
                "standard": standard.value,
                "name": standard.name,
                "description": f"Compliance standard: {standard.value}",
            }
            for standard in ComplianceStandard
        ]
        
        return {
            "success": True,
            "data": {
                "standards": standards,
                "total_standards": len(standards),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting compliance standards: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threat-levels")
async def get_threat_levels():
    """Get available threat levels"""
    try:
        threat_levels = [
            {
                "level": level.value,
                "name": level.name,
                "description": f"Threat level: {level.value}",
            }
            for level in ThreatLevel
        ]
        
        return {
            "success": True,
            "data": {
                "threat_levels": threat_levels,
                "total_levels": len(threat_levels),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting threat levels: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_security_framework(background_tasks: BackgroundTasks):
    """Start the security framework"""
    try:
        if zero_trust_security.is_running:
            return {
                "success": True,
                "data": {"message": "Security framework is already running"},
                "timestamp": datetime.utcnow().isoformat(),
            }
        
        background_tasks.add_task(zero_trust_security.start)
        
        return {
            "success": True,
            "data": {"message": "Security framework started successfully"},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error starting security framework: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_security_framework():
    """Stop the security framework"""
    try:
        await zero_trust_security.stop()
        return {
            "success": True,
            "data": {"message": "Security framework stopped successfully"},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error stopping security framework: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def security_health_check():
    """Security framework health check"""
    try:
        status = await zero_trust_security.get_security_status()
        return {
            "status": "healthy" if zero_trust_security.is_running else "stopped",
            "framework_running": zero_trust_security.is_running,
            "total_policies": status.get("total_policies", 0),
            "enabled_policies": status.get("enabled_policies", 0),
            "total_audit_events": status.get("total_audit_events", 0),
            "recent_audit_events": status.get("recent_audit_events", 0),
            "total_alerts": status.get("total_alerts", 0),
            "unacknowledged_alerts": status.get("unacknowledged_alerts", 0),
            "compliance_score": status.get("compliance_score", 0),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Security health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
