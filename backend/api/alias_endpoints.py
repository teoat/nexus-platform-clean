#!/usr/bin/env python3
"""
NEXUS Platform - Alias Management API Endpoints
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.ssot.alias_manager import AliasManager
from backend.ssot.audit_system import AuditSystem

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/aliases", tags=["alias-management"])

# Initialize managers
alias_manager = AliasManager()
audit_system = AuditSystem()


@router.get("/")
async def list_aliases(
    context: Optional[str] = Query(None, description="Filter by context"),
    alias_type: Optional[str] = Query(None, description="Filter by alias type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(100, description="Maximum number of aliases to return"),
    offset: int = Query(0, description="Number of aliases to skip"),
):
    """List all aliases with optional filtering"""
    try:
        aliases = await alias_manager.list_aliases(
            context=context,
            alias_type=alias_type,
            is_active=is_active,
            limit=limit,
            offset=offset,
        )

        return {
            "aliases": aliases,
            "total": len(aliases),
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        logger.error(f"Error listing aliases: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{alias_name}")
async def get_alias(alias_name: str, context: Optional[str] = None):
    """Get specific alias by name"""
    try:
        alias = await alias_manager.get_alias(alias_name, context)
        if not alias:
            raise HTTPException(status_code=404, detail="Alias not found")

        return alias
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alias {alias_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_alias(alias_data: Dict[str, Any]):
    """Create a new alias"""
    try:
        # Validate required fields
        required_fields = ["alias_name", "canonical_name", "context", "alias_type"]
        for field in required_fields:
            if field not in alias_data:
                raise HTTPException(
                    status_code=400, detail=f"Missing required field: {field}"
                )

        # Check if alias already exists
        existing = await alias_manager.get_alias(
            alias_data["alias_name"], alias_data.get("context")
        )
        if existing:
            raise HTTPException(status_code=409, detail="Alias already exists")

        # Create alias
        alias = await alias_manager.create_alias(
            alias_name=alias_data["alias_name"],
            canonical_name=alias_data["canonical_name"],
            context=alias_data["context"],
            alias_type=alias_data["alias_type"],
            description=alias_data.get("description", ""),
            created_by=alias_data.get("created_by", "api_user"),
            expires_at=alias_data.get("expires_at"),
            metadata=alias_data.get("metadata", {}),
        )

        # Log audit event
        await audit_system.log_event(
            operation="create_alias",
            details={
                "alias_name": alias_data["alias_name"],
                "canonical_name": alias_data["canonical_name"],
            },
            requester=alias_data.get("created_by", "api_user"),
        )

        return alias

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating alias: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{alias_name}")
async def update_alias(
    alias_name: str, update_data: Dict[str, Any], context: Optional[str] = None
):
    """Update an existing alias"""
    try:
        # Check if alias exists
        existing = await alias_manager.get_alias(alias_name, context)
        if not existing:
            raise HTTPException(status_code=404, detail="Alias not found")

        # Update alias
        updated_alias = await alias_manager.update_alias(
            alias_name=alias_name,
            context=context,
            updates=update_data,
            updated_by=update_data.get("updated_by", "api_user"),
        )

        # Log audit event
        await audit_system.log_event(
            operation="update_alias",
            details={"alias_name": alias_name, "updates": update_data},
            requester=update_data.get("updated_by", "api_user"),
        )

        return updated_alias

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating alias {alias_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{alias_name}")
async def delete_alias(
    alias_name: str, context: Optional[str] = None, hard_delete: bool = False
):
    """Delete an alias (soft delete by default)"""
    try:
        # Check if alias exists
        existing = await alias_manager.get_alias(alias_name, context)
        if not existing:
            raise HTTPException(status_code=404, detail="Alias not found")

        # Delete alias
        if hard_delete:
            await alias_manager.hard_delete_alias(alias_name, context)
        else:
            await alias_manager.soft_delete_alias(alias_name, context)

        # Log audit event
        await audit_system.log_event(
            operation="delete_alias",
            details={"alias_name": alias_name, "hard_delete": hard_delete},
            requester="api_user",
        )

        return {"message": "Alias deleted successfully", "hard_delete": hard_delete}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting alias {alias_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{alias_name}/resolve")
async def resolve_alias(alias_name: str, context: Optional[str] = None):
    """Resolve alias to canonical name"""
    try:
        canonical = await alias_manager.resolve_alias(alias_name, context)
        if not canonical:
            raise HTTPException(status_code=404, detail="Alias not found")

        # Log audit event
        await audit_system.log_event(
            operation="resolve_alias",
            details={"alias_name": alias_name, "canonical_name": canonical},
            requester="api_user",
        )

        return {
            "alias_name": alias_name,
            "canonical_name": canonical,
            "resolved_at": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving alias {alias_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{alias_name}/history")
async def get_alias_history(alias_name: str, context: Optional[str] = None):
    """Get alias change history"""
    try:
        history = await alias_manager.get_alias_history(alias_name, context)
        return {"alias_name": alias_name, "context": context, "history": history}
    except Exception as e:
        logger.error(f"Error getting alias history for {alias_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_aliases(alias_data: List[Dict[str, Any]]):
    """Validate multiple aliases"""
    try:
        validation_results = []

        for alias_info in alias_data:
            result = await alias_manager.validate_alias(
                alias_name=alias_info.get("alias_name"),
                context=alias_info.get("context"),
                canonical_name=alias_info.get("canonical_name"),
            )
            validation_results.append(
                {
                    "alias_name": alias_info.get("alias_name"),
                    "context": alias_info.get("context"),
                    "valid": result,
                    "errors": [] if result else ["Invalid alias configuration"],
                }
            )

        return {
            "validation_results": validation_results,
            "total_validated": len(validation_results),
            "valid_count": sum(1 for r in validation_results if r["valid"]),
        }

    except Exception as e:
        logger.error(f"Error validating aliases: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_alias_stats():
    """Get alias statistics summary"""
    try:
        stats = await alias_manager.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting alias stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk/create")
async def bulk_create_aliases(aliases_data: List[Dict[str, Any]]):
    """Create multiple aliases in bulk"""
    try:
        created_aliases = []
        errors = []

        for alias_data in aliases_data:
            try:
                alias = await alias_manager.create_alias(
                    alias_name=alias_data["alias_name"],
                    canonical_name=alias_data["canonical_name"],
                    context=alias_data["context"],
                    alias_type=alias_data["alias_type"],
                    description=alias_data.get("description", ""),
                    created_by=alias_data.get("created_by", "api_user"),
                    expires_at=alias_data.get("expires_at"),
                    metadata=alias_data.get("metadata", {}),
                )
                created_aliases.append(alias)
            except Exception as e:
                errors.append(
                    {"alias_name": alias_data.get("alias_name"), "error": str(e)}
                )

        # Log audit event
        await audit_system.log_event(
            operation="bulk_create_aliases",
            details={
                "total_requested": len(aliases_data),
                "created": len(created_aliases),
                "errors": len(errors),
            },
            requester="api_user",
        )

        return {
            "created_aliases": created_aliases,
            "errors": errors,
            "total_requested": len(aliases_data),
            "success_count": len(created_aliases),
            "error_count": len(errors),
        }

    except Exception as e:
        logger.error(f"Error in bulk create aliases: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk/delete")
async def bulk_delete_aliases(
    alias_names: List[str], context: Optional[str] = None, hard_delete: bool = False
):
    """Delete multiple aliases in bulk"""
    try:
        deleted_aliases = []
        errors = []

        for alias_name in alias_names:
            try:
                if hard_delete:
                    await alias_manager.hard_delete_alias(alias_name, context)
                else:
                    await alias_manager.soft_delete_alias(alias_name, context)
                deleted_aliases.append(alias_name)
            except Exception as e:
                errors.append({"alias_name": alias_name, "error": str(e)})

        # Log audit event
        await audit_system.log_event(
            operation="bulk_delete_aliases",
            details={
                "total_requested": len(alias_names),
                "deleted": len(deleted_aliases),
                "errors": len(errors),
            },
            requester="api_user",
        )

        return {
            "deleted_aliases": deleted_aliases,
            "errors": errors,
            "total_requested": len(alias_names),
            "success_count": len(deleted_aliases),
            "error_count": len(errors),
        }

    except Exception as e:
        logger.error(f"Error in bulk delete aliases: {e}")
        raise HTTPException(status_code=500, detail=str(e))
