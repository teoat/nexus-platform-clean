from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

from backend.services.alias_manager import AliasManager

# Dependency
def get_alias_manager():
    # In a real application, this would provide a properly initialized AliasManager
    # e.g., from a global app state or a dependency injection container.
    # For now, we'll use a simple instance.
    return AliasManager()

router = APIRouter()

# Pydantic models for request/response bodies
class AliasCreate(BaseModel):
    alias_name: str
    canonical_name: str
    context: str = "global"
    expires_at: Optional[datetime] = None

class AliasUpdate(BaseModel):
    canonical_name: Optional[str] = None
    context: Optional[str] = None
    expires_at: Optional[datetime] = None

class AliasResponse(BaseModel):
    alias_name: str
    canonical_name: str
    context: str
    created_at: datetime
    expires_at: Optional[datetime]
    status: str
    updated_at: Optional[datetime] = None
    deactivated_at: Optional[datetime] = None
    deactivation_reason: Optional[str] = None

@router.post("/alias", response_model=AliasResponse)
async def create_alias_endpoint(alias_data: AliasCreate, alias_manager: AliasManager = Depends(get_alias_manager)) -> AliasResponse:
    try:
        alias = alias_manager.create_alias(**alias_data.dict())
        return AliasResponse(alias_name=alias_data.alias_name, **alias)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/alias/{alias_name}", response_model=AliasResponse)
async def get_alias_details_endpoint(alias_name: str, alias_manager: AliasManager = Depends(get_alias_manager)) -> AliasResponse:
    try:
        alias = alias_manager.get_alias(alias_name)
        if not alias:
            raise HTTPException(status_code=404, detail=f"Alias '{alias_name}' not found or expired.")
        return AliasResponse(alias_name=alias_name, **alias)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.put("/alias/{alias_name}", response_model=AliasResponse)
async def update_alias_endpoint(alias_name: str, alias_data: AliasUpdate, alias_manager: AliasManager = Depends(get_alias_manager)) -> AliasResponse:
    try:
        updated_alias = alias_manager.update_alias(alias_name, **alias_data.dict(exclude_unset=True))
        return AliasResponse(alias_name=alias_name, **updated_alias)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.delete("/alias/{alias_name}", status_code=204)
async def deactivate_alias_endpoint(alias_name: str, alias_manager: AliasManager = Depends(get_alias_manager)):
    try:
        alias_manager.deactivate_alias(alias_name)
        return
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/resolve/{context}/{alias_name}", response_model=Dict[str, str])
async def resolve_alias_endpoint(
    context: str,
    alias_name: str,
    alias_manager: AliasManager = Depends(get_alias_manager)
) -> Dict[str, str]:
    """Resolves an alias to its canonical name within a given context."""
    try:
        canonical_name = alias_manager.resolve_alias(alias_name, context)
        if not canonical_name:
            raise HTTPException(status_code=404, detail=f"Alias '{alias_name}' not found or resolved in context '{context}'")
        return {"canonical_name": canonical_name}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
