#!/usr/bin/env python3
"""
NEXUS Platform - Data Standardization Service V3.0
Service for standardizing data before reconciliation
"""

import json
import logging
import re
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from schemas.enhanced_user import \
    DataQualityMetrics as DataQualityMetricsSchema
from schemas.enhanced_user import \
    DataStandardizationRule as DataStandardizationRuleSchema
from sqlalchemy.orm import Session

from database.database import get_db
from database.enhanced_models import (DataQualityMetrics,
                                      DataStandardizationRule)

logger = logging.getLogger(__name__)


class DataStandardizationService:
    """Service for standardizing and validating data before reconciliation"""

    def __init__(self):
        self.standardization_rules = self._initialize_standardization_rules()
        self.validation_rules = self._initialize_validation_rules()

    def _initialize_standardization_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize data standardization rules"""
        return {
            "date_format": {
                "id": "DS001",
                "name": "Date Format Standardization",
                "description": "Convert all dates to ISO8601 format",
                "field": "date",
                "transformation": "iso8601",
                "validation": "date_range",
                "priority": 1,
            },
            "currency_format": {
                "id": "DS002",
                "name": "Currency Format Standardization",
                "description": "Convert all currency values to standard format",
                "field": "amount",
                "transformation": "currency_standardize",
                "validation": "numeric_positive",
                "priority": 1,
            },
            "text_cleanup": {
                "id": "DS003",
                "name": "Text Cleanup",
                "description": "Clean and normalize text fields",
                "field": "description",
                "transformation": "text_clean",
                "validation": "text_length",
                "priority": 2,
            },
            "duplicate_removal": {
                "id": "DS004",
                "name": "Duplicate Removal",
                "description": "Remove duplicate entries",
                "field": "all",
                "transformation": "deduplicate",
                "validation": "uniqueness",
                "priority": 1,
            },
            "category_normalization": {
                "id": "DS005",
                "name": "Category Normalization",
                "description": "Normalize category names",
                "field": "category",
                "transformation": "category_normalize",
                "validation": "category_exists",
                "priority": 3,
            },
        }

    def _initialize_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize data validation rules"""
        return {
            "amount_validation": {
                "field": "amount",
                "type": "numeric",
                "min": 0.01,
                "max": 999999999.99,
                "required": True,
            },
            "date_validation": {
                "field": "date",
                "type": "date",
                "min_date": "2020-01-01",
                "max_date": "2030-12-31",
                "required": True,
            },
            "account_validation": {
                "field": "account_id",
                "type": "reference",
                "reference_table": "accounts",
                "required": True,
            },
            "description_validation": {
                "field": "description",
                "type": "text",
                "min_length": 1,
                "max_length": 255,
                "required": True,
            },
        }

    async def standardize_data(
        self, db: Session, raw_data: List[Dict[str, Any]], data_source: str
    ) -> Dict[str, Any]:
        """Standardize raw data according to rules"""
        try:
            standardized_data = []
            quality_metrics = DataQualityMetricsSchema(
                completeness=0.0,
                accuracy=0.0,
                consistency=0.0,
                timeliness=0.0,
                validity=0.0,
                uniqueness=0.0,
            )

            # Apply standardization rules
            for item in raw_data:
                standardized_item = await self._apply_standardization_rules(item)
                standardized_data.append(standardized_item)

            # Calculate quality metrics
            quality_metrics = await self._calculate_quality_metrics(
                standardized_data, data_source
            )

            # Store quality metrics
            await self._store_quality_metrics(db, data_source, quality_metrics)

            return {
                "standardized_data": standardized_data,
                "quality_metrics": quality_metrics,
                "rules_applied": list(self.standardization_rules.keys()),
                "processed_at": datetime.utcnow(),
            }

        except Exception as e:
            logger.error(f"Error standardizing data: {e}")
            raise

    async def _apply_standardization_rules(
        self, item: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply standardization rules to a single item"""
        try:
            standardized_item = item.copy()

            # Apply date format standardization
            if "date" in standardized_item:
                standardized_item["date"] = await self._standardize_date(
                    standardized_item["date"]
                )

            # Apply currency format standardization
            if "amount" in standardized_item:
                standardized_item["amount"] = await self._standardize_currency(
                    standardized_item["amount"]
                )

            # Apply text cleanup
            if "description" in standardized_item:
                standardized_item["description"] = await self._clean_text(
                    standardized_item["description"]
                )

            # Apply category normalization
            if "category" in standardized_item:
                standardized_item["category"] = await self._normalize_category(
                    standardized_item["category"]
                )

            return standardized_item

        except Exception as e:
            logger.error(f"Error applying standardization rules: {e}")
            raise

    async def _standardize_date(self, date_value: Any) -> str:
        """Standardize date to ISO8601 format"""
        try:
            if isinstance(date_value, str):
                # Try to parse various date formats
                date_formats = [
                    "%Y-%m-%d",
                    "%m/%d/%Y",
                    "%d/%m/%Y",
                    "%Y-%m-%d %H:%M:%S",
                    "%m/%d/%Y %H:%M:%S",
                    "%d/%m/%Y %H:%M:%S",
                ]

                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(date_value, fmt)
                        return parsed_date.isoformat()
                    except ValueError:
                        continue

                # If no format matches, try to parse as ISO format
                try:
                    parsed_date = datetime.fromisoformat(
                        date_value.replace("Z", "+00:00")
                    )
                    return parsed_date.isoformat()
                except ValueError:
                    pass

            elif isinstance(date_value, datetime):
                return date_value.isoformat()

            # If all else fails, return current date
            return datetime.utcnow().isoformat()

        except Exception as e:
            logger.error(f"Error standardizing date: {e}")
            return datetime.utcnow().isoformat()

    async def _standardize_currency(self, amount_value: Any) -> float:
        """Standardize currency to numeric format"""
        try:
            if isinstance(amount_value, (int, float)):
                return float(amount_value)

            if isinstance(amount_value, str):
                # Remove currency symbols and commas
                cleaned = re.sub(r"[^\d.-]", "", amount_value)
                return float(cleaned)

            return 0.0

        except Exception as e:
            logger.error(f"Error standardizing currency: {e}")
            return 0.0

    async def _clean_text(self, text_value: str) -> str:
        """Clean and normalize text"""
        try:
            if not isinstance(text_value, str):
                return str(text_value)

            # Remove extra whitespace
            cleaned = re.sub(r"\s+", " ", text_value.strip())

            # Remove special characters but keep alphanumeric and basic punctuation
            cleaned = re.sub(r"[^\w\s.,!?-]", "", cleaned)

            return cleaned

        except Exception as e:
            logger.error(f"Error cleaning text: {e}")
            return str(text_value) if text_value else ""

    async def _normalize_category(self, category_value: str) -> str:
        """Normalize category names"""
        try:
            if not isinstance(category_value, str):
                return "uncategorized"

            # Convert to lowercase and remove extra spaces
            normalized = category_value.lower().strip()

            # Map common variations
            category_mappings = {
                "food": ["meals", "dining", "restaurant", "groceries"],
                "transport": ["transportation", "travel", "gas", "fuel"],
                "utilities": ["utility", "electric", "water", "internet"],
                "entertainment": ["entertainment", "fun", "leisure", "hobby"],
                "health": ["healthcare", "medical", "pharmacy", "doctor"],
                "shopping": ["retail", "store", "purchase", "buy"],
            }

            for standard_category, variations in category_mappings.items():
                if normalized in variations or any(
                    var in normalized for var in variations
                ):
                    return standard_category

            return normalized

        except Exception as e:
            logger.error(f"Error normalizing category: {e}")
            return "uncategorized"

    async def _calculate_quality_metrics(
        self, data: List[Dict[str, Any]], data_source: str
    ) -> DataQualityMetricsSchema:
        """Calculate data quality metrics"""
        try:
            if not data:
                return DataQualityMetricsSchema()

            total_records = len(data)

            # Completeness: percentage of non-null required fields
            required_fields = ["amount", "date", "description"]
            complete_records = 0

            for record in data:
                if all(
                    record.get(field) is not None and record.get(field) != ""
                    for field in required_fields
                ):
                    complete_records += 1

            completeness = (
                (complete_records / total_records) * 100 if total_records > 0 else 0
            )

            # Accuracy: percentage of records that pass validation
            accurate_records = 0

            for record in data:
                if self._validate_record(record):
                    accurate_records += 1

            accuracy = (
                (accurate_records / total_records) * 100 if total_records > 0 else 0
            )

            # Consistency: check for consistent data patterns
            consistency = await self._calculate_consistency(data)

            # Timeliness: check if data is recent
            timeliness = await self._calculate_timeliness(data)

            # Validity: check if data conforms to expected formats
            validity = await self._calculate_validity(data)

            # Uniqueness: check for duplicate records
            uniqueness = await self._calculate_uniqueness(data)

            return DataQualityMetricsSchema(
                completeness=completeness,
                accuracy=accuracy,
                consistency=consistency,
                timeliness=timeliness,
                validity=validity,
                uniqueness=uniqueness,
            )

        except Exception as e:
            logger.error(f"Error calculating quality metrics: {e}")
            return DataQualityMetricsSchema()

    def _validate_record(self, record: Dict[str, Any]) -> bool:
        """Validate a single record against validation rules"""
        try:
            # Validate amount
            if "amount" in record:
                amount = record["amount"]
                if not isinstance(amount, (int, float)) or amount <= 0:
                    return False

            # Validate date
            if "date" in record:
                date_str = record["date"]
                try:
                    datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    return False

            # Validate description
            if "description" in record:
                desc = record["description"]
                if not isinstance(desc, str) or len(desc.strip()) == 0:
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating record: {e}")
            return False

    async def _calculate_consistency(self, data: List[Dict[str, Any]]) -> float:
        """Calculate consistency score"""
        try:
            if not data:
                return 0.0

            # Check for consistent date formats
            date_formats = set()
            for record in data:
                if "date" in record and record["date"]:
                    try:
                        date_obj = datetime.fromisoformat(
                            record["date"].replace("Z", "+00:00")
                        )
                        date_formats.add(date_obj.strftime("%Y-%m-%d"))
                    except (ValueError, TypeError):
                        pass

            # Consistency is higher when all dates follow the same format
            consistency = (
                100.0
                if len(date_formats) <= 1
                else max(0, 100 - (len(date_formats) - 1) * 20)
            )

            return consistency

        except Exception as e:
            logger.error(f"Error calculating consistency: {e}")
            return 0.0

    async def _calculate_timeliness(self, data: List[Dict[str, Any]]) -> float:
        """Calculate timeliness score"""
        try:
            if not data:
                return 0.0

            current_time = datetime.utcnow()
            timely_records = 0

            for record in data:
                if "date" in record and record["date"]:
                    try:
                        record_date = datetime.fromisoformat(
                            record["date"].replace("Z", "+00:00")
                        )
                        # Consider data timely if it's within the last 30 days
                        if (current_time - record_date).days <= 30:
                            timely_records += 1
                    except (ValueError, TypeError):
                        pass

            return (timely_records / len(data)) * 100 if data else 0.0

        except Exception as e:
            logger.error(f"Error calculating timeliness: {e}")
            return 0.0

    async def _calculate_validity(self, data: List[Dict[str, Any]]) -> float:
        """Calculate validity score"""
        try:
            if not data:
                return 0.0

            valid_records = 0

            for record in data:
                if self._validate_record(record):
                    valid_records += 1

            return (valid_records / len(data)) * 100 if data else 0.0

        except Exception as e:
            logger.error(f"Error calculating validity: {e}")
            return 0.0

    async def _calculate_uniqueness(self, data: List[Dict[str, Any]]) -> float:
        """Calculate uniqueness score"""
        try:
            if not data:
                return 0.0

            # Create a set of unique records based on key fields
            unique_records = set()

            for record in data:
                # Create a unique key based on amount, date, and description
                key = (
                    str(record.get("amount", "")),
                    str(record.get("date", "")),
                    str(record.get("description", "")).lower().strip(),
                )
                unique_records.add(key)

            return (len(unique_records) / len(data)) * 100 if data else 0.0

        except Exception as e:
            logger.error(f"Error calculating uniqueness: {e}")
            return 0.0

    async def _store_quality_metrics(
        self, db: Session, data_source: str, metrics: DataQualityMetricsSchema
    ):
        """Store quality metrics in database"""
        try:
            db_metrics = DataQualityMetrics(
                data_source=data_source,
                completeness=metrics.completeness,
                accuracy=metrics.accuracy,
                consistency=metrics.consistency,
                timeliness=metrics.timeliness,
                validity=metrics.validity,
                uniqueness=metrics.uniqueness,
                overall_score=(
                    metrics.completeness
                    + metrics.accuracy
                    + metrics.consistency
                    + metrics.timeliness
                    + metrics.validity
                    + metrics.uniqueness
                )
                / 6,
            )

            db.add(db_metrics)
            db.commit()

        except Exception as e:
            logger.error(f"Error storing quality metrics: {e}")
            raise

    async def get_quality_metrics(
        self, db: Session, data_source: str
    ) -> Optional[DataQualityMetricsSchema]:
        """Get quality metrics for a data source"""
        try:
            metrics = (
                db.query(DataQualityMetrics)
                .filter(DataQualityMetrics.data_source == data_source)
                .order_by(DataQualityMetrics.measured_at.desc())
                .first()
            )

            if metrics:
                return DataQualityMetricsSchema(
                    completeness=float(metrics.completeness),
                    accuracy=float(metrics.accuracy),
                    consistency=float(metrics.consistency),
                    timeliness=float(metrics.timeliness),
                    validity=float(metrics.validity),
                    uniqueness=float(metrics.uniqueness),
                )

            return None

        except Exception as e:
            logger.error(f"Error getting quality metrics: {e}")
            return None

    async def create_standardization_rule(
        self, db: Session, rule: DataStandardizationRuleSchema
    ) -> DataStandardizationRuleSchema:
        """Create a new standardization rule"""
        try:
            db_rule = DataStandardizationRule(
                id=rule.id,
                name=rule.name,
                description=rule.description,
                field=rule.field,
                transformation=json.dumps(rule.transformation),
                validation=json.dumps(rule.validation),
                priority=rule.priority,
            )

            db.add(db_rule)
            db.commit()
            db.refresh(db_rule)

            return DataStandardizationRuleSchema.from_orm(db_rule)

        except Exception as e:
            logger.error(f"Error creating standardization rule: {e}")
            raise


# Create service instance
data_standardization_service = DataStandardizationService()
