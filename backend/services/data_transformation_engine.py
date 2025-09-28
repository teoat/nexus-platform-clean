#!/usr/bin/env python3
"""
NEXUS Platform - Data Transformation and Mapping Engine
Advanced data transformation, mapping, and processing capabilities
"""

import asyncio
import copy
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class TransformationType(Enum):
    """Data transformation type enumeration"""

    MAPPING = "mapping"
    FILTERING = "filtering"
    AGGREGATION = "aggregation"
    VALIDATION = "validation"
    ENRICHMENT = "enrichment"
    NORMALIZATION = "normalization"
    MASKING = "masking"
    CUSTOM = "custom"


class MappingType(Enum):
    """Data mapping type enumeration"""

    DIRECT = "direct"
    LOOKUP = "lookup"
    EXPRESSION = "expression"
    CONDITIONAL = "conditional"
    TRANSFORMATION = "transformation"


@dataclass
class DataMapping:
    """Data mapping configuration"""

    source_field: str
    target_field: str
    mapping_type: MappingType
    default_value: Any = None
    lookup_table: Optional[Dict[str, Any]] = None
    expression: Optional[str] = None
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    transformation_function: Optional[str] = None
    required: bool = False
    validation_rules: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TransformationRule:
    """Data transformation rule"""

    rule_id: str
    name: str
    description: str
    transformation_type: TransformationType
    source_schema: Dict[str, Any]
    target_schema: Dict[str, Any]
    mappings: List[DataMapping]
    filters: List[Dict[str, Any]] = field(default_factory=list)
    aggregations: List[Dict[str, Any]] = field(default_factory=list)
    validations: List[Dict[str, Any]] = field(default_factory=list)
    enrichments: List[Dict[str, Any]] = field(default_factory=list)
    custom_logic: Optional[str] = None
    active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class TransformationResult:
    """Result of data transformation"""

    success: bool
    transformed_data: Any
    original_data: Any
    applied_rules: List[str]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: Optional[float] = None
    processed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class DataTransformationEngine:
    """Advanced data transformation and mapping engine"""

    def __init__(self):
        self.transformation_rules: Dict[str, TransformationRule] = {}
        self.custom_functions: Dict[str, Callable] = {}

        # Register built-in transformation functions
        self._register_builtin_functions()

    def _register_builtin_functions(self):
        """Register built-in transformation functions"""
        self.custom_functions = {
            "uppercase": lambda x: str(x).upper() if x is not None else None,
            "lowercase": lambda x: str(x).lower() if x is not None else None,
            "trim": lambda x: str(x).strip() if x is not None else None,
            "length": lambda x: len(str(x)) if x is not None else 0,
            "hash_md5": self._hash_md5,
            "format_date": self._format_date,
            "extract_domain": self._extract_domain,
            "mask_email": self._mask_email,
            "normalize_phone": self._normalize_phone,
        }

    async def create_transformation_rule(
        self,
        rule_id: str,
        name: str,
        description: str,
        transformation_type: TransformationType,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        mappings: List[Dict[str, Any]],
    ) -> Optional[str]:
        """Create a new transformation rule"""
        try:
            # Convert dict mappings to DataMapping objects
            mapping_objects = []
            for mapping_dict in mappings:
                mapping = DataMapping(
                    source_field=mapping_dict["source_field"],
                    target_field=mapping_dict["target_field"],
                    mapping_type=MappingType(mapping_dict["mapping_type"]),
                    default_value=mapping_dict.get("default_value"),
                    lookup_table=mapping_dict.get("lookup_table"),
                    expression=mapping_dict.get("expression"),
                    conditions=mapping_dict.get("conditions", []),
                    transformation_function=mapping_dict.get("transformation_function"),
                    required=mapping_dict.get("required", False),
                    validation_rules=mapping_dict.get("validation_rules", []),
                )
                mapping_objects.append(mapping)

            rule = TransformationRule(
                rule_id=rule_id,
                name=name,
                description=description,
                transformation_type=transformation_type,
                source_schema=source_schema,
                target_schema=target_schema,
                mappings=mapping_objects,
            )

            self.transformation_rules[rule_id] = rule
            logger.info(f"Transformation rule {rule_id} created")
            return rule_id

        except Exception as e:
            logger.error(f"Failed to create transformation rule: {e}")
            return None

    async def apply_transformation(
        self, rule_id: str, data: Any, additional_context: Dict[str, Any] = None
    ) -> TransformationResult:
        """Apply a transformation rule to data"""
        start_time = datetime.now(timezone.utc)

        try:
            if rule_id not in self.transformation_rules:
                return TransformationResult(
                    success=False,
                    transformed_data=None,
                    original_data=data,
                    applied_rules=[],
                    errors=[f"Transformation rule {rule_id} not found"],
                )

            rule = self.transformation_rules[rule_id]
            context = additional_context or {}

            # Apply transformations based on type
            if rule.transformation_type == TransformationType.MAPPING:
                result = await self._apply_mapping_transformation(rule, data, context)
            elif rule.transformation_type == TransformationType.FILTERING:
                result = await self._apply_filtering_transformation(rule, data, context)
            elif rule.transformation_type == TransformationType.AGGREGATION:
                result = await self._apply_aggregation_transformation(
                    rule, data, context
                )
            elif rule.transformation_type == TransformationType.VALIDATION:
                result = await self._apply_validation_transformation(
                    rule, data, context
                )
            elif rule.transformation_type == TransformationType.ENRICHMENT:
                result = await self._apply_enrichment_transformation(
                    rule, data, context
                )
            elif rule.transformation_type == TransformationType.NORMALIZATION:
                result = await self._apply_normalization_transformation(
                    rule, data, context
                )
            elif rule.transformation_type == TransformationType.MASKING:
                result = await self._apply_masking_transformation(rule, data, context)
            elif rule.transformation_type == TransformationType.CUSTOM:
                result = await self._apply_custom_transformation(rule, data, context)
            else:
                result = data

            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()

            return TransformationResult(
                success=True,
                transformed_data=result,
                original_data=data,
                applied_rules=[rule_id],
                metadata={"rule_type": rule.transformation_type.value},
                execution_time=execution_time,
            )

        except Exception as e:
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.error(f"Transformation failed: {e}")
            return TransformationResult(
                success=False,
                transformed_data=None,
                original_data=data,
                applied_rules=[rule_id],
                errors=[str(e)],
                execution_time=execution_time,
            )

    async def _apply_mapping_transformation(
        self, rule: TransformationRule, data: Any, context: Dict[str, Any]
    ) -> Any:
        """Apply mapping transformation"""
        if isinstance(data, dict):
            result = {}
            for mapping in rule.mappings:
                value = await self._resolve_mapping_value(mapping, data, context)
                if value is not None or not mapping.required:
                    result[mapping.target_field] = value
            return result
        elif isinstance(data, list):
            return [
                await self._apply_mapping_transformation(rule, item, context)
                for item in data
            ]
        else:
            return data

    async def _resolve_mapping_value(
        self, mapping: DataMapping, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Any:
        """Resolve the value for a mapping"""
        try:
            if mapping.mapping_type == MappingType.DIRECT:
                return self._get_nested_value(data, mapping.source_field)

            elif mapping.mapping_type == MappingType.LOOKUP:
                source_value = self._get_nested_value(data, mapping.source_field)
                if mapping.lookup_table and source_value in mapping.lookup_table:
                    return mapping.lookup_table[source_value]
                return mapping.default_value

            elif mapping.mapping_type == MappingType.EXPRESSION:
                if mapping.expression:
                    return self._evaluate_expression(mapping.expression, data, context)
                return mapping.default_value

            elif mapping.mapping_type == MappingType.CONDITIONAL:
                for condition in mapping.conditions:
                    if self._evaluate_condition(condition, data, context):
                        return condition.get("value", mapping.default_value)
                return mapping.default_value

            elif mapping.mapping_type == MappingType.TRANSFORMATION:
                source_value = self._get_nested_value(data, mapping.source_field)
                if (
                    mapping.transformation_function
                    and mapping.transformation_function in self.custom_functions
                ):
                    func = self.custom_functions[mapping.transformation_function]
                    return func(source_value)
                return source_value

            return mapping.default_value

        except Exception as e:
            logger.warning(f"Failed to resolve mapping value: {e}")
            return mapping.default_value

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get nested value from dictionary using dot notation"""
        keys = path.split(".")
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current

    def _evaluate_expression(
        self, expression: str, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Any:
        """Safely evaluate an expression"""
        try:
            # Create a safe evaluation context
            safe_globals = {
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "abs": abs,
                "max": max,
                "min": min,
                "sum": sum,
                "round": round,
            }

            safe_locals = {
                "data": data,
                "context": context,
                **data,  # Allow direct access to data fields
                **context,
            }

            # Simple expression evaluation (in production, use a proper expression evaluator)
            result = eval(expression, safe_globals, safe_locals)
            return result

        except Exception as e:
            logger.warning(f"Expression evaluation failed: {e}")
            return None

    def _evaluate_condition(
        self, condition: Dict[str, Any], data: Dict[str, Any], context: Dict[str, Any]
    ) -> bool:
        """Evaluate a condition"""
        try:
            field = condition.get("field")
            operator = condition.get("operator", "equals")
            value = condition.get("value")

            if not field:
                return False

            actual_value = self._get_nested_value(data, field)

            if operator == "equals":
                return actual_value == value
            elif operator == "not_equals":
                return actual_value != value
            elif operator == "contains":
                return str(value) in str(actual_value)
            elif operator == "greater_than":
                return actual_value > value
            elif operator == "less_than":
                return actual_value < value
            elif operator == "is_null":
                return actual_value is None
            elif operator == "is_not_null":
                return actual_value is not None

            return False

        except Exception as e:
            logger.warning(f"Condition evaluation failed: {e}")
            return False

    async def _apply_filtering_transformation(
        self, rule: TransformationRule, data: Any, context: Dict[str, Any]
    ) -> Any:
        """Apply filtering transformation"""
        if not isinstance(data, list):
            return data

        filtered_data = []
        for item in data:
            include_item = True
            for filter_rule in rule.filters:
                if not self._evaluate_condition(filter_rule, item, context):
                    include_item = False
                    break
            if include_item:
                filtered_data.append(item)

        return filtered_data

    async def _apply_aggregation_transformation(
        self, rule: TransformationRule, data: Any, context: Dict[str, Any]
    ) -> Any:
        """Apply aggregation transformation"""
        if not isinstance(data, list):
            return data

        result = {}
        for agg_rule in rule.aggregations:
            field = agg_rule.get("field")
            operation = agg_rule.get("operation", "count")
            group_by = agg_rule.get("group_by")

            if group_by:
                # Grouped aggregation
                groups = {}
                for item in data:
                    group_key = self._get_nested_value(item, group_by)
                    if group_key not in groups:
                        groups[group_key] = []
                    groups[group_key].append(item)

                for group_key, group_data in groups.items():
                    result[f"{group_key}_{operation}"] = self._perform_aggregation(
                        group_data, field, operation
                    )
            else:
                # Simple aggregation
                result[operation] = self._perform_aggregation(data, field, operation)

        return result

    def _perform_aggregation(
        self, data: List[Dict[str, Any]], field: str, operation: str
    ) -> Any:
        """Perform aggregation operation"""
        if not field:
            values = data
        else:
            values = [
                self._get_nested_value(item, field)
                for item in data
                if self._get_nested_value(item, field) is not None
            ]

        if operation == "count":
            return len(values)
        elif operation == "sum":
            return sum(float(v) for v in values if isinstance(v, (int, float)))
        elif operation == "avg":
            numeric_values = [float(v) for v in values if isinstance(v, (int, float))]
            return sum(numeric_values) / len(numeric_values) if numeric_values else 0
        elif operation == "max":
            return max(values) if values else None
        elif operation == "min":
            return min(values) if values else None

        return None

    async def _apply_validation_transformation(
        self, rule: TransformationRule, data: Any, context: Dict[str, Any]
    ) -> Any:
        """Apply validation transformation"""
        # Validation doesn't change data, just validates it
        # This would typically be used in combination with other transformations
        return data

    async def _apply_enrichment_transformation(
        self, rule: TransformationRule, data: Any, context: Dict[str, Any]
    ) -> Any:
        """Apply enrichment transformation"""
        if isinstance(data, dict):
            enriched_data = copy.deepcopy(data)
            for enrichment in rule.enrichments:
                field = enrichment.get("field")
                value = enrichment.get("value")
                expression = enrichment.get("expression")

                if expression:
                    value = self._evaluate_expression(expression, data, context)

                if field and value is not None:
                    self._set_nested_value(enriched_data, field, value)

            return enriched_data
        elif isinstance(data, list):
            return [
                await self._apply_enrichment_transformation(rule, item, context)
                for item in data
            ]

        return data

    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any):
        """Set nested value in dictionary using dot notation"""
        keys = path.split(".")
        current = data

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    async def _apply_normalization_transformation(
        self, rule: TransformationRule, data: Any, context: Dict[str, Any]
    ) -> Any:
        """Apply normalization transformation"""
        # Apply standard normalization rules
        if isinstance(data, dict):
            normalized = copy.deepcopy(data)
            for key, value in normalized.items():
                if isinstance(value, str):
                    normalized[key] = value.strip()
                elif isinstance(value, (int, float)):
                    # Normalize numeric values if needed
                    pass
            return normalized
        elif isinstance(data, list):
            return [
                await self._apply_normalization_transformation(rule, item, context)
                for item in data
            ]

        return data

    async def _apply_masking_transformation(
        self, rule: TransformationRule, data: Any, context: Dict[str, Any]
    ) -> Any:
        """Apply masking transformation"""
        if isinstance(data, dict):
            masked = copy.deepcopy(data)
            for key, value in masked.items():
                if isinstance(value, str) and any(
                    pattern in key.lower() for pattern in ["email", "ssn", "phone"]
                ):
                    masked[key] = self._mask_sensitive_data(value, key)
            return masked
        elif isinstance(data, list):
            return [
                await self._apply_masking_transformation(rule, item, context)
                for item in data
            ]

        return data

    async def _apply_custom_transformation(
        self, rule: TransformationRule, data: Any, context: Dict[str, Any]
    ) -> Any:
        """Apply custom transformation logic"""
        if rule.custom_logic:
            try:
                # Execute custom logic (in production, use a safer approach)
                exec_globals = {
                    "data": data,
                    "context": context,
                    "result": None,
                }
                exec(rule.custom_logic, exec_globals)
                return exec_globals.get("result", data)
            except Exception as e:
                logger.error(f"Custom transformation failed: {e}")
                return data

        return data

    # Built-in transformation functions
    def _hash_md5(self, value: Any) -> str:
        """Generate MD5 hash of value"""
        import hashlib

        return hashlib.md5(str(value).encode()).hexdigest()

    def _format_date(self, value: Any) -> str:
        """Format date value"""
        from datetime import datetime

        try:
            if isinstance(value, str):
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            elif isinstance(value, datetime):
                dt = value
            else:
                return str(value)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return str(value)

    def _extract_domain(self, value: Any) -> str:
        """Extract domain from email or URL"""
        import re

        email_pattern = r"@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
        url_pattern = r"https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"

        value_str = str(value)
        match = re.search(email_pattern, value_str) or re.search(url_pattern, value_str)
        return match.group(1) if match else value_str

    def _mask_email(self, value: Any) -> str:
        """Mask email address"""
        email = str(value)
        if "@" in email:
            local, domain = email.split("@", 1)
            masked_local = (
                local[0] + "*" * (len(local) - 2) + local[-1]
                if len(local) > 2
                else local[0] + "*"
            )
            return f"{masked_local}@{domain}"
        return email

    def _mask_sensitive_data(self, value: str, field_name: str) -> str:
        """Mask sensitive data based on field name"""
        if "email" in field_name.lower():
            return self._mask_email(value)
        elif "ssn" in field_name.lower():
            return "***-**-****"
        elif "phone" in field_name.lower():
            return self._normalize_phone(value)  # Phone normalization also masks
        else:
            return "*" * len(value)

    def _normalize_phone(self, value: Any) -> str:
        """Normalize phone number"""
        import re

        phone = re.sub(r"\D", "", str(value))
        if len(phone) == 10:
            return f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
        elif len(phone) == 11 and phone[0] == "1":
            return f"({phone[1:4]}) {phone[4:7]}-{phone[7:]}"
        return str(value)

    async def register_custom_function(self, name: str, function: Callable) -> bool:
        """Register a custom transformation function"""
        try:
            self.custom_functions[name] = function
            logger.info(f"Custom function {name} registered")
            return True
        except Exception as e:
            logger.error(f"Failed to register custom function: {e}")
            return False

    def list_transformation_rules(self) -> List[Dict[str, Any]]:
        """List all transformation rules"""
        return [
            {
                "rule_id": rule.rule_id,
                "name": rule.name,
                "description": rule.description,
                "type": rule.transformation_type.value,
                "active": rule.active,
                "created_at": rule.created_at.isoformat(),
                "updated_at": rule.updated_at.isoformat(),
            }
            for rule in self.transformation_rules.values()
        ]


# Global data transformation engine instance
data_transformation_engine = DataTransformationEngine()
