#!/usr/bin/env python3
"""
NEXUS Platform - Comprehensive Audit Logging API Routes
Advanced audit logging with query capabilities and comprehensive reporting
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from services.audit_logging import (
    AuditLogQueryEngine,
    AuditLogLevel,
    AuditQuery,
    OperationType,
    ReportFormat,
)
from services.audit_compliance_service import audit_compliance_service, ComplianceFramework
from services.security import verify_admin_access

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/audit", tags=["audit"])

# Initialize audit query engine
audit_engine = AuditLogQueryEngine()


class AuditLogRequest(BaseModel):
    """Request model for logging audit events"""

    operation: str = Field(..., description="Operation type (create, read, update, delete, etc.)")
    entity_type: str = Field(..., description="Type of entity being operated on")
    entity_id: str = Field(..., description="ID of the entity")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional operation details")
    performed_by: str = Field(..., description="User or system that performed the operation")
    context: str = Field(default="system", description="Context of the operation")
    log_level: str = Field(default="info", description="Log level (debug, info, warning, error, critical)")
    ip_address: Optional[str] = Field(None, description="IP address of the request")
    user_agent: Optional[str] = Field(None, description="User agent string")
    session_id: Optional[str] = Field(None, description="Session ID")


class AuditQueryRequest(BaseModel):
    """Request model for querying audit logs"""

    start_date: Optional[datetime] = Field(None, description="Start date for query")
    end_date: Optional[datetime] = Field(None, description="End date for query")
    operation_types: Optional[List[str]] = Field(None, description="Filter by operation types")
    entity_types: Optional[List[str]] = Field(None, description="Filter by entity types")
    entity_ids: Optional[List[str]] = Field(None, description="Filter by entity IDs")
    performed_by: Optional[List[str]] = Field(None, description="Filter by performers")
    contexts: Optional[List[str]] = Field(None, description="Filter by contexts")
    log_levels: Optional[List[str]] = Field(None, description="Filter by log levels")
    search_text: Optional[str] = Field(None, description="Text search in details")
    limit: Optional[int] = Field(100, description="Maximum number of results")
    offset: Optional[int] = Field(0, description="Pagination offset")
    sort_by: Optional[str] = Field("timestamp", description="Sort field")
    sort_order: Optional[str] = Field("desc", description="Sort order (asc/desc)")


class AuditReportRequest(BaseModel):
    """Request model for generating audit reports"""

    query: AuditQueryRequest = Field(..., description="Query parameters for the report")
    title: str = Field(..., description="Report title")
    description: str = Field(..., description="Report description")
    format: str = Field("json", description="Report format (json, csv, html, pdf, excel)")
    generated_by: Optional[str] = Field(None, description="User generating the report")


@router.post("/log")
async def log_audit_event(
    request: AuditLogRequest,
    current_user: str = Depends(verify_admin_access)
) -> Dict[str, Any]:
    """
    Log an audit event to the audit database
    """
    try:
        # Validate log level
        try:
            log_level = AuditLogLevel(request.log_level.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid log level: {request.log_level}. Must be one of: {[l.value for l in AuditLogLevel]}"
            )

        # Log the operation
        log_id = await audit_engine.log_operation(
            operation=request.operation,
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            details=request.details,
            performed_by=request.performed_by,
            context=request.context,
            log_level=log_level,
            ip_address=request.ip_address,
            user_agent=request.user_agent,
            session_id=request.session_id,
        )

        return {
            "success": True,
            "data": {
                "log_id": log_id,
                "message": "Audit event logged successfully",
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging audit event: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to log audit event: {str(e)}")


@router.post("/query")
async def query_audit_logs(
    query_request: AuditQueryRequest,
    current_user: str = Depends(verify_admin_access)
) -> Dict[str, Any]:
    """
    Query audit logs with advanced filtering and pagination
    """
    try:
        # Convert string lists to enum lists
        operation_types = None
        if query_request.operation_types:
            try:
                operation_types = [OperationType(op.lower()) for op in query_request.operation_types]
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid operation type: {e}")

        log_levels = None
        if query_request.log_levels:
            try:
                log_levels = [AuditLogLevel(level.lower()) for level in query_request.log_levels]
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid log level: {e}")

        # Build query
        query = AuditQuery(
            start_date=query_request.start_date,
            end_date=query_request.end_date,
            operation_types=operation_types,
            entity_types=query_request.entity_types,
            entity_ids=query_request.entity_ids,
            performed_by=query_request.performed_by,
            contexts=query_request.contexts,
            log_levels=log_levels,
            search_text=query_request.search_text,
            limit=query_request.limit,
            offset=query_request.offset,
            sort_by=query_request.sort_by,
            sort_order=query_request.sort_order,
        )

        # Execute query
        results = await audit_engine.query_audit_logs(query)

        return {
            "success": True,
            "data": results,
            "query": {
                "total_results": len(results),
                "limit": query_request.limit,
                "offset": query_request.offset,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying audit logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to query audit logs: {str(e)}")


@router.get("/logs")
async def get_audit_logs(
    # Query parameters
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    operation: Optional[str] = Query(None, description="Filter by operation type"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[str] = Query(None, description="Filter by entity ID"),
    performed_by: Optional[str] = Query(None, description="Filter by performer"),
    context: Optional[str] = Query(None, description="Filter by context"),
    log_level: Optional[str] = Query(None, description="Filter by log level"),
    search: Optional[str] = Query(None, description="Text search"),
    limit: int = Query(100, description="Maximum results", ge=1, le=1000),
    offset: int = Query(0, description="Pagination offset", ge=0),
    sort_by: str = Query("timestamp", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order"),
    current_user: str = Depends(verify_admin_access)
) -> Dict[str, Any]:
    """
    Get audit logs with GET parameters (alternative to POST /query)
    """
    try:
        # Parse dates
        start_dt = None
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format")

        end_dt = None
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format")

        # Convert single values to lists for query
        operation_types = [operation] if operation else None
        entity_types = [entity_type] if entity_type else None
        entity_ids = [entity_id] if entity_id else None
        performed_by_list = [performed_by] if performed_by else None
        contexts = [context] if context else None
        log_levels = [log_level] if log_level else None

        # Validate enums
        if operation_types:
            try:
                operation_types = [OperationType(op.lower()) for op in operation_types]
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid operation type: {e}")

        if log_levels:
            try:
                log_levels = [AuditLogLevel(level.lower()) for level in log_levels]
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid log level: {e}")

        # Build and execute query
        query = AuditQuery(
            start_date=start_dt,
            end_date=end_dt,
            operation_types=operation_types,
            entity_types=entity_types,
            entity_ids=entity_ids,
            performed_by=performed_by_list,
            contexts=contexts,
            log_levels=log_levels,
            search_text=search,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        results = await audit_engine.query_audit_logs(query)

        return {
            "success": True,
            "data": results,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total_results": len(results),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving audit logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve audit logs: {str(e)}")


@router.get("/statistics")
async def get_audit_statistics(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    context: Optional[str] = Query(None, description="Filter by context"),
    current_user: str = Depends(verify_admin_access)
) -> Dict[str, Any]:
    """
    Get comprehensive audit statistics
    """
    try:
        # Parse dates
        start_dt = None
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format")

        end_dt = None
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format")

        # Build query
        query = AuditQuery(
            start_date=start_dt,
            end_date=end_dt,
            contexts=[context] if context else None,
        )

        # Get statistics
        stats = await audit_engine.get_audit_statistics(query)

        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving audit statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve audit statistics: {str(e)}")


@router.post("/reports")
async def generate_audit_report(
    report_request: AuditReportRequest,
    current_user: str = Depends(verify_admin_access)
) -> Dict[str, Any]:
    """
    Generate a comprehensive audit report
    """
    try:
        # Validate report format
        try:
            format_enum = ReportFormat(report_request.format.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid report format: {report_request.format}. Must be one of: {[f.value for f in ReportFormat]}"
            )

        # Convert query request to AuditQuery
        query_req = report_request.query
        operation_types = None
        if query_req.operation_types:
            try:
                operation_types = [OperationType(op.lower()) for op in query_req.operation_types]
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid operation type: {e}")

        log_levels = None
        if query_req.log_levels:
            try:
                log_levels = [AuditLogLevel(level.lower()) for level in query_req.log_levels]
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid log level: {e}")

        query = AuditQuery(
            start_date=query_req.start_date,
            end_date=query_req.end_date,
            operation_types=operation_types,
            entity_types=query_req.entity_types,
            entity_ids=query_req.entity_ids,
            performed_by=query_req.performed_by,
            contexts=query_req.contexts,
            log_levels=log_levels,
            search_text=query_req.search_text,
            limit=query_req.limit,
            offset=query_req.offset,
            sort_by=query_req.sort_by,
            sort_order=query_req.sort_order,
        )

        # Generate report
        report = await audit_engine.generate_report(
            query=query,
            title=report_request.title,
            description=report_request.description,
            format=format_enum,
            generated_by=report_request.generated_by or current_user,
        )

        return {
            "success": True,
            "data": {
                "report_id": report.id,
                "title": report.title,
                "description": report.description,
                "generated_at": report.generated_at.isoformat(),
                "generated_by": report.generated_by,
                "total_records": report.total_records,
                "format": report.format.value,
                "file_path": report.file_path,
                "summary": report.summary,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating audit report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate audit report: {str(e)}")


@router.delete("/cleanup")
async def cleanup_old_audit_logs(
    retention_days: int = Query(365, description="Retention period in days", ge=30, le=3650),
    current_user: str = Depends(verify_admin_access)
) -> Dict[str, Any]:
    """
    Clean up audit logs older than the specified retention period
    """
    try:
        deleted_count = await audit_engine.cleanup_old_logs(retention_days)

        return {
            "success": True,
            "data": {
                "deleted_count": deleted_count,
                "retention_days": retention_days,
                "message": f"Cleaned up {deleted_count} audit logs older than {retention_days} days",
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Error cleaning up audit logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cleanup audit logs: {str(e)}")


@router.get("/health")
async def audit_system_health() -> Dict[str, Any]:
    """
    Check audit logging system health
    """
    try:
        # Basic health check - try to query recent logs
        query = AuditQuery(limit=1, sort_order="desc")
        recent_logs = await audit_engine.query_audit_logs(query)

        return {
            "status": "healthy",
            "service": "audit_logging",
            "database_connected": True,
            "recent_logs_count": len(recent_logs),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Audit system health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "audit_logging",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@router.post("/compliance/{framework}")
async def generate_compliance_report(
    framework: str,
    start_date: str = Query(..., description="Start date (ISO format)"),
    end_date: str = Query(..., description="End date (ISO format)"),
    include_details: bool = Query(True, description="Include detailed findings"),
    current_user: str = Depends(verify_admin_access)
) -> Dict[str, Any]:
    """
    Generate a compliance report for a specific regulatory framework
    """
    try:
        # Validate framework
        try:
            framework_enum = ComplianceFramework(framework.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid framework: {framework}. Supported: {[f.value for f in ComplianceFramework]}"
            )

        # Parse dates
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")

        # Generate report
        report = await audit_compliance_service.generate_compliance_report(
            framework_enum, start_dt, end_dt, include_details
        )

        return {
            "success": True,
            "data": report,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating compliance report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate compliance report: {str(e)}")


@router.get("/compliance/frameworks")
async def get_supported_frameworks() -> Dict[str, Any]:
    """
    Get list of supported compliance frameworks
    """
    frameworks = {
        framework.value: {
            "name": framework.value.upper(),
            "description": f"Compliance framework for {framework.value.upper()}",
            "requirements": [req.value for req in audit_compliance_service.framework_requirements.get(framework, [])],
        }
        for framework in ComplianceFramework
    }

    return {
        "success": True,
        "data": frameworks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/compliance/{framework}/export")
async def export_compliance_report(
    framework: str,
    start_date: str = Query(..., description="Start date (ISO format)"),
    end_date: str = Query(..., description="End date (ISO format)"),
    format: str = Query("json", description="Export format (json, csv, html, excel)"),
    current_user: str = Depends(verify_admin_access)
) -> Dict[str, Any]:
    """
    Export a compliance report to file
    """
    try:
        # Validate framework
        try:
            framework_enum = ComplianceFramework(framework.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid framework: {framework}. Supported: {[f.value for f in ComplianceFramework]}"
            )

        # Validate format
        try:
            format_enum = ReportFormat(format.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format: {format}. Supported: {[f.value for f in ReportFormat]}"
            )

        # Parse dates
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")

        # Export report
        filename = await audit_compliance_service.export_compliance_report(
            framework_enum, start_dt, end_dt, format_enum
        )

        return {
            "success": True,
            "data": {
                "filename": filename,
                "framework": framework,
                "format": format,
                "message": f"Compliance report exported to {filename}",
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting compliance report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export compliance report: {str(e)}")