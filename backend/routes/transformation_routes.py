#!/usr/bin/env python3
"""
NEXUS Platform - Data Transformation API Routes
REST API endpoints for managing data transformations
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..services.data_transformation_engine import (MappingType,
                                                   TransformationType,
                                                   data_transformation_engine)
from ..services.enhanced_auth_service import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/transformations", tags=["transformations"])


# Pydantic models for API requests/responses
class DataMappingRequest(BaseModel):
    source_field: str = Field(..., description="Source field path")
    target_field: str = Field(..., description="Target field path")
    mapping_type: MappingType = Field(..., description="Type of mapping")
    default_value: Optional[Any] = Field(
        None, description="Default value if source is missing"
    )
    lookup_table: Optional[Dict[str, Any]] = Field(
        None, description="Lookup table for mapping"
    )
    expression: Optional[str] = Field(None, description="Expression for mapping")
    conditions: List[Dict[str, Any]] = Field(
        default_factory=list, description="Conditional mapping rules"
    )
    transformation_function: Optional[str] = Field(
        None, description="Built-in transformation function"
    )
    required: bool = Field(False, description="Whether this mapping is required")
    validation_rules: List[Dict[str, Any]] = Field(
        default_factory=list, description="Validation rules"
    )


class TransformationRuleRequest(BaseModel):
    name: str = Field(..., description="Rule name")
    description: str = Field("", description="Rule description")
    transformation_type: TransformationType = Field(
        ..., description="Type of transformation"
    )
    source_schema: Dict[str, Any] = Field(..., description="Source data schema")
    target_schema: Dict[str, Any] = Field(..., description="Target data schema")
    mappings: List[DataMappingRequest] = Field(..., description="Field mappings")
    filters: List[Dict[str, Any]] = Field(
        default_factory=list, description="Filtering rules"
    )
    aggregations: List[Dict[str, Any]] = Field(
        default_factory=list, description="Aggregation rules"
    )
    validations: List[Dict[str, Any]] = Field(
        default_factory=list, description="Validation rules"
    )
    enrichments: List[Dict[str, Any]] = Field(
        default_factory=list, description="Data enrichment rules"
    )
    custom_logic: Optional[str] = Field(None, description="Custom transformation logic")


class TransformationRuleResponse(BaseModel):
    rule_id: str
    name: str
    description: str
    transformation_type: TransformationType
    source_schema: Dict[str, Any]
    target_schema: Dict[str, Any]
    mappings: List[Dict[str, Any]]
    filters: List[Dict[str, Any]]
    aggregations: List[Dict[str, Any]]
    validations: List[Dict[str, Any]]
    enrichments: List[Dict[str, Any]]
    custom_logic: Optional[str]
    active: bool
    created_at: datetime
    updated_at: datetime


class ApplyTransformationRequest(BaseModel):
    rule_id: str = Field(..., description="Transformation rule ID")
    data: Any = Field(..., description="Data to transform")
    additional_context: Dict[str, Any] = Field(
        default_factory=dict, description="Additional context"
    )


class TransformationResult(BaseModel):
    success: bool
    transformed_data: Optional[Any]
    original_data: Any
    applied_rules: List[str]
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]
    execution_time: Optional[float]
    processed_at: datetime


# API Endpoints
@router.post("/rules", response_model=dict)
async def create_transformation_rule(
    request: TransformationRuleRequest, current_user: str = Depends(get_current_user)
):
    """Create a new transformation rule"""
    try:
        # Convert mappings to dict format
        mappings_dict = []
        for mapping in request.mappings:
            mappings_dict.append(
                {
                    "source_field": mapping.source_field,
                    "target_field": mapping.target_field,
                    "mapping_type": mapping.mapping_type.value,
                    "default_value": mapping.default_value,
                    "lookup_table": mapping.lookup_table,
                    "expression": mapping.expression,
                    "conditions": mapping.conditions,
                    "transformation_function": mapping.transformation_function,
                    "required": mapping.required,
                    "validation_rules": mapping.validation_rules,
                }
            )

        rule_id = f"rule_{request.name.lower().replace(' ', '_')}_{int(datetime.utcnow().timestamp())}"

        success = await data_transformation_engine.create_transformation_rule(
            rule_id=rule_id,
            name=request.name,
            description=request.description,
            transformation_type=request.transformation_type,
            source_schema=request.source_schema,
            target_schema=request.target_schema,
            mappings=mappings_dict,
        )

        if not success:
            raise HTTPException(
                status_code=400, detail="Failed to create transformation rule"
            )

        return {
            "rule_id": rule_id,
            "message": "Transformation rule created successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create transformation rule: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to create transformation rule"
        )


@router.get("/rules", response_model=List[Dict[str, Any]])
async def list_transformation_rules(current_user: str = Depends(get_current_user)):
    """List all transformation rules"""
    try:
        return data_transformation_engine.list_transformation_rules()
    except Exception as e:
        logger.error(f"Failed to list transformation rules: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to list transformation rules"
        )


@router.get("/rules/{rule_id}", response_model=TransformationRuleResponse)
async def get_transformation_rule(
    rule_id: str, current_user: str = Depends(get_current_user)
):
    """Get a specific transformation rule"""
    try:
        if rule_id not in data_transformation_engine.transformation_rules:
            raise HTTPException(status_code=404, detail="Transformation rule not found")

        rule = data_transformation_engine.transformation_rules[rule_id]
        return TransformationRuleResponse(
            rule_id=rule.rule_id,
            name=rule.name,
            description=rule.description,
            transformation_type=rule.transformation_type,
            source_schema=rule.source_schema,
            target_schema=rule.target_schema,
            mappings=[
                {
                    "source_field": m.source_field,
                    "target_field": m.target_field,
                    "mapping_type": m.mapping_type.value,
                    "default_value": m.default_value,
                    "lookup_table": m.lookup_table,
                    "expression": m.expression,
                    "conditions": m.conditions,
                    "transformation_function": m.transformation_function,
                    "required": m.required,
                    "validation_rules": m.validation_rules,
                }
                for m in rule.mappings
            ],
            filters=rule.filters,
            aggregations=rule.aggregations,
            validations=rule.validations,
            enrichments=rule.enrichments,
            custom_logic=rule.custom_logic,
            active=rule.active,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transformation rule: {e}")
        raise HTTPException(status_code=500, detail="Failed to get transformation rule")


@router.delete("/rules/{rule_id}", response_model=dict)
async def delete_transformation_rule(
    rule_id: str, current_user: str = Depends(get_current_user)
):
    """Delete a transformation rule"""
    try:
        if rule_id not in data_transformation_engine.transformation_rules:
            raise HTTPException(status_code=404, detail="Transformation rule not found")

        del data_transformation_engine.transformation_rules[rule_id]
        return {"message": "Transformation rule deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete transformation rule: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to delete transformation rule"
        )


@router.post("/apply", response_model=TransformationResult)
async def apply_transformation(
    request: ApplyTransformationRequest, current_user: str = Depends(get_current_user)
):
    """Apply a transformation rule to data"""
    try:
        result = await data_transformation_engine.apply_transformation(
            rule_id=request.rule_id,
            data=request.data,
            additional_context=request.additional_context,
        )

        return TransformationResult(
            success=result.success,
            transformed_data=result.transformed_data,
            original_data=result.original_data,
            applied_rules=result.applied_rules,
            errors=result.errors,
            warnings=result.warnings,
            metadata=result.metadata,
            execution_time=result.execution_time,
            processed_at=result.processed_at,
        )
    except Exception as e:
        logger.error(f"Failed to apply transformation: {e}")
        raise HTTPException(status_code=500, detail="Failed to apply transformation")


@router.get("/functions", response_model=Dict[str, str])
async def list_builtin_functions(current_user: str = Depends(get_current_user)):
    """List available built-in transformation functions"""
    try:
        functions = {}
        for name, func in data_transformation_engine.custom_functions.items():
            functions[name] = f"{name}(value) -> transformed_value"
        return functions
    except Exception as e:
        logger.error(f"Failed to list built-in functions: {e}")
        raise HTTPException(status_code=500, detail="Failed to list built-in functions")


@router.post("/functions", response_model=dict)
async def register_custom_function(
    name: str, code: str, current_user: str = Depends(get_current_user)
):
    """Register a custom transformation function"""
    try:
        # In production, this should be properly validated and sandboxed
        exec_globals = {}
        exec_locals = {}
        exec(code, exec_globals, exec_locals)

        if "transform" not in exec_locals:
            raise HTTPException(
                status_code=400, detail="Function must define a 'transform' function"
            )

        success = await data_transformation_engine.register_custom_function(
            name=name, function=exec_locals["transform"]
        )

        if not success:
            raise HTTPException(
                status_code=400, detail="Failed to register custom function"
            )

        return {"message": f"Custom function '{name}' registered successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to register custom function: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to register custom function"
        )


@router.get("/types", response_model=Dict[str, List[str]])
async def get_transformation_types(current_user: str = Depends(get_current_user)):
    """Get available transformation and mapping types"""
    try:
        return {
            "transformation_types": [t.value for t in TransformationType],
            "mapping_types": [t.value for t in MappingType],
        }
    except Exception as e:
        logger.error(f"Failed to get transformation types: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get transformation types"
        )
