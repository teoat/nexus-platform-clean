#!/usr/bin/env python3
"""
NEXUS Platform - Data Schema Validation Service
Validates data consistency across all platforms and services
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import asyncpg
import redis.asyncio as redis
import yaml
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.config.settings import get_settings

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Validation status enumeration"""

    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class ValidationResult:
    """Data class for validation results"""

    service: str
    table: str
    status: ValidationStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


class DataSchemaValidator:
    """Service for validating data schema consistency across platforms"""

    def __init__(self):
        self.settings = get_settings()
        self.validation_config = self._load_validation_config()
        self.db_engine = None
        self.redis_client = None

    def _load_validation_config(self) -> Dict[str, Any]:
        """Load data validation configuration"""
        config_path = Path("config/data_validation.yaml")
        if config_path.exists():
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default validation configuration"""
        return {
            "validation_rules": {
                "required_tables": [
                    "users",
                    "accounts",
                    "transactions",
                    "audit_logs",
                    "ssot_api_contracts",
                    "ssot_api_aliases",
                    "ssot_audit_logs",
                ],
                "required_columns": {
                    "users": ["id", "username", "email", "created_at", "updated_at"],
                    "accounts": [
                        "id",
                        "user_id",
                        "account_name",
                        "balance",
                        "created_at",
                    ],
                    "transactions": [
                        "id",
                        "account_id",
                        "amount",
                        "transaction_type",
                        "created_at",
                    ],
                    "ssot_api_contracts": [
                        "id",
                        "canonical_name",
                        "version",
                        "base_url",
                        "status",
                    ],
                    "ssot_api_aliases": [
                        "id",
                        "contract_id",
                        "alias_name",
                        "context",
                        "is_active",
                    ],
                },
                "data_types": {
                    "users.id": "uuid",
                    "users.username": "varchar",
                    "users.email": "varchar",
                    "accounts.balance": "decimal",
                    "transactions.amount": "decimal",
                },
                "constraints": {
                    "users": ["username_unique", "email_unique"],
                    "accounts": ["user_id_foreign_key"],
                    "transactions": ["account_id_foreign_key"],
                },
            },
            "validation_settings": {
                "check_data_integrity": True,
                "check_referential_integrity": True,
                "check_constraints": True,
                "check_indexes": True,
                "sample_data_validation": True,
                "sample_size": 1000,
            },
        }

    async def initialize_connections(self) -> None:
        """Initialize database and Redis connections"""
        try:
            # Initialize database connection
            database_url = self.settings.DATABASE_URL
            self.db_engine = create_async_engine(database_url, echo=False)

            # Initialize Redis connection
            redis_url = self.settings.REDIS_URL
            self.redis_client = redis.from_url(redis_url, decode_responses=True)

            logger.info("Database and Redis connections initialized")
        except Exception as e:
            logger.error(f"Failed to initialize connections: {str(e)}")
            raise

    async def validate_all_schemas(self) -> Dict[str, Any]:
        """Validate all data schemas across platforms"""
        logger.info("Starting comprehensive data schema validation")

        validation_results = {
            "success": True,
            "total_validations": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "skipped": 0,
            "results": [],
            "validation_time": None,
            "errors": [],
        }

        start_time = datetime.now(timezone.utc)

        try:
            await self.initialize_connections()

            # Validate database schema
            db_results = await self._validate_database_schema()
            validation_results["results"].extend(db_results)

            # Validate Redis schema
            redis_results = await self._validate_redis_schema()
            validation_results["results"].extend(redis_results)

            # Validate data integrity
            integrity_results = await self._validate_data_integrity()
            validation_results["results"].extend(integrity_results)

            # Validate referential integrity
            referential_results = await self._validate_referential_integrity()
            validation_results["results"].extend(referential_results)

            # Validate constraints
            constraint_results = await self._validate_constraints()
            validation_results["results"].extend(constraint_results)

            # Validate indexes
            index_results = await self._validate_indexes()
            validation_results["results"].extend(index_results)

            # Validate cross-platform consistency
            cross_platform_results = await self._validate_cross_platform_consistency()
            validation_results["results"].extend(cross_platform_results)

            # Calculate summary statistics
            for result in validation_results["results"]:
                validation_results["total_validations"] += 1
                if result.status == ValidationStatus.PASSED:
                    validation_results["passed"] += 1
                elif result.status == ValidationStatus.FAILED:
                    validation_results["failed"] += 1
                elif result.status == ValidationStatus.WARNING:
                    validation_results["warnings"] += 1
                else:
                    validation_results["skipped"] += 1

            # Check overall success
            if validation_results["failed"] > 0:
                validation_results["success"] = False
                logger.warning(
                    f"Schema validation completed with {validation_results['failed']} failures"
                )
            else:
                logger.info("All schema validations passed successfully")

        except Exception as e:
            logger.error(f"Schema validation failed: {str(e)}")
            validation_results["success"] = False
            validation_results["errors"].append(str(e))

        finally:
            end_time = datetime.now(timezone.utc)
            validation_results["validation_time"] = (
                end_time - start_time
            ).total_seconds()

            # Close connections
            await self._close_connections()

        return validation_results

    async def _validate_database_schema(self) -> List[ValidationResult]:
        """Validate database schema structure"""
        logger.info("Validating database schema")
        results = []

        try:
            async with self.db_engine.begin() as conn:
                # Get all tables
                inspector = inspect(self.db_engine.sync_engine)
                tables = inspector.get_table_names()

                # Check required tables
                required_tables = self.validation_config["validation_rules"][
                    "required_tables"
                ]
                for table in required_tables:
                    if table in tables:
                        results.append(
                            ValidationResult(
                                service="database",
                                table=table,
                                status=ValidationStatus.PASSED,
                                message=f"Required table '{table}' exists",
                            )
                        )
                    else:
                        results.append(
                            ValidationResult(
                                service="database",
                                table=table,
                                status=ValidationStatus.FAILED,
                                message=f"Required table '{table}' is missing",
                            )
                        )

                # Check table structures
                for table in tables:
                    if table in required_tables:
                        table_results = await self._validate_table_structure(
                            conn, table
                        )
                        results.extend(table_results)

        except Exception as e:
            logger.error(f"Database schema validation failed: {str(e)}")
            results.append(
                ValidationResult(
                    service="database",
                    table="schema",
                    status=ValidationStatus.FAILED,
                    message=f"Database schema validation error: {str(e)}",
                )
            )

        return results

    async def _validate_table_structure(
        self, conn, table: str
    ) -> List[ValidationResult]:
        """Validate structure of a specific table"""
        results = []

        try:
            # Get table columns
            inspector = inspect(self.db_engine.sync_engine)
            columns = inspector.get_columns(table)
            column_names = [col["name"] for col in columns]

            # Check required columns
            required_columns = self.validation_config["validation_rules"][
                "required_columns"
            ].get(table, [])
            for column in required_columns:
                if column in column_names:
                    results.append(
                        ValidationResult(
                            service="database",
                            table=table,
                            status=ValidationStatus.PASSED,
                            message=f"Required column '{column}' exists in table '{table}'",
                        )
                    )
                else:
                    results.append(
                        ValidationResult(
                            service="database",
                            table=table,
                            status=ValidationStatus.FAILED,
                            message=f"Required column '{column}' is missing from table '{table}'",
                        )
                    )

            # Check data types
            data_types = self.validation_config["validation_rules"]["data_types"]
            for column, expected_type in data_types.items():
                table_name, column_name = column.split(".", 1)
                if table_name == table:
                    column_info = next(
                        (col for col in columns if col["name"] == column_name), None
                    )
                    if column_info:
                        actual_type = str(column_info["type"]).lower()
                        if expected_type.lower() in actual_type:
                            results.append(
                                ValidationResult(
                                    service="database",
                                    table=table,
                                    status=ValidationStatus.PASSED,
                                    message=f"Column '{column_name}' has correct data type",
                                )
                            )
                        else:
                            results.append(
                                ValidationResult(
                                    service="database",
                                    table=table,
                                    status=ValidationStatus.WARNING,
                                    message=f"Column '{column_name}' type mismatch: expected {expected_type}, got {actual_type}",
                                )
                            )

        except Exception as e:
            logger.error(f"Table structure validation failed for {table}: {str(e)}")
            results.append(
                ValidationResult(
                    service="database",
                    table=table,
                    status=ValidationStatus.FAILED,
                    message=f"Table structure validation error: {str(e)}",
                )
            )

        return results

    async def _validate_redis_schema(self) -> List[ValidationResult]:
        """Validate Redis schema and data structure"""
        logger.info("Validating Redis schema")
        results = []

        try:
            # Test Redis connection
            await self.redis_client.ping()
            results.append(
                ValidationResult(
                    service="redis",
                    table="connection",
                    status=ValidationStatus.PASSED,
                    message="Redis connection successful",
                )
            )

            # Check Redis keys and data types
            keys = await self.redis_client.keys("*")
            if keys:
                results.append(
                    ValidationResult(
                        service="redis",
                        table="keys",
                        status=ValidationStatus.PASSED,
                        message=f"Found {len(keys)} Redis keys",
                    )
                )

                # Validate key patterns
                key_patterns = {
                    "session:*": "user sessions",
                    "cache:*": "application cache",
                    "lock:*": "distributed locks",
                    "queue:*": "message queues",
                }

                for pattern, description in key_patterns.items():
                    pattern_keys = await self.redis_client.keys(pattern)
                    if pattern_keys:
                        results.append(
                            ValidationResult(
                                service="redis",
                                table="keys",
                                status=ValidationStatus.PASSED,
                                message=f"Found {len(pattern_keys)} {description} keys",
                            )
                        )
                    else:
                        results.append(
                            ValidationResult(
                                service="redis",
                                table="keys",
                                status=ValidationStatus.WARNING,
                                message=f"No {description} keys found",
                            )
                        )
            else:
                results.append(
                    ValidationResult(
                        service="redis",
                        table="keys",
                        status=ValidationStatus.WARNING,
                        message="No Redis keys found",
                    )
                )

        except Exception as e:
            logger.error(f"Redis schema validation failed: {str(e)}")
            results.append(
                ValidationResult(
                    service="redis",
                    table="schema",
                    status=ValidationStatus.FAILED,
                    message=f"Redis schema validation error: {str(e)}",
                )
            )

        return results

    async def _validate_data_integrity(self) -> List[ValidationResult]:
        """Validate data integrity across tables"""
        logger.info("Validating data integrity")
        results = []

        if not self.validation_config["validation_settings"]["check_data_integrity"]:
            results.append(
                ValidationResult(
                    service="database",
                    table="data_integrity",
                    status=ValidationStatus.SKIPPED,
                    message="Data integrity validation disabled",
                )
            )
            return results

        try:
            async with self.db_engine.begin() as conn:
                # Check for null values in required columns
                null_checks = [
                    ("users", "username", "username IS NULL"),
                    ("users", "email", "email IS NULL"),
                    ("accounts", "user_id", "user_id IS NULL"),
                    ("transactions", "account_id", "account_id IS NULL"),
                ]

                for table, column, condition in null_checks:
                    query = f"SELECT COUNT(*) FROM {table} WHERE {condition}"
                    result = await conn.execute(text(query))
                    null_count = result.scalar()

                    if null_count == 0:
                        results.append(
                            ValidationResult(
                                service="database",
                                table=table,
                                status=ValidationStatus.PASSED,
                                message=f"No null values found in required column '{column}'",
                            )
                        )
                    else:
                        results.append(
                            ValidationResult(
                                service="database",
                                table=table,
                                status=ValidationStatus.FAILED,
                                message=f"Found {null_count} null values in required column '{column}'",
                            )
                        )

                # Check for duplicate values in unique columns
                duplicate_checks = [
                    ("users", "username", "username"),
                    ("users", "email", "email"),
                    ("accounts", "account_number", "account_number"),
                ]

                for table, column, column_name in duplicate_checks:
                    query = f"""
                        SELECT {column_name}, COUNT(*) as count
                        FROM {table}
                        GROUP BY {column_name}
                        HAVING COUNT(*) > 1
                    """
                    result = await conn.execute(text(query))
                    duplicates = result.fetchall()

                    if not duplicates:
                        results.append(
                            ValidationResult(
                                service="database",
                                table=table,
                                status=ValidationStatus.PASSED,
                                message=f"No duplicate values found in unique column '{column_name}'",
                            )
                        )
                    else:
                        results.append(
                            ValidationResult(
                                service="database",
                                table=table,
                                status=ValidationStatus.FAILED,
                                message=f"Found {len(duplicates)} duplicate values in unique column '{column_name}'",
                            )
                        )

        except Exception as e:
            logger.error(f"Data integrity validation failed: {str(e)}")
            results.append(
                ValidationResult(
                    service="database",
                    table="data_integrity",
                    status=ValidationStatus.FAILED,
                    message=f"Data integrity validation error: {str(e)}",
                )
            )

        return results

    async def _validate_referential_integrity(self) -> List[ValidationResult]:
        """Validate referential integrity between tables"""
        logger.info("Validating referential integrity")
        results = []

        if not self.validation_config["validation_settings"][
            "check_referential_integrity"
        ]:
            results.append(
                ValidationResult(
                    service="database",
                    table="referential_integrity",
                    status=ValidationStatus.SKIPPED,
                    message="Referential integrity validation disabled",
                )
            )
            return results

        try:
            async with self.db_engine.begin() as conn:
                # Check foreign key relationships
                fk_checks = [
                    ("accounts", "user_id", "users", "id"),
                    ("transactions", "account_id", "accounts", "id"),
                    ("ssot_api_aliases", "contract_id", "ssot_api_contracts", "id"),
                ]

                for child_table, child_column, parent_table, parent_column in fk_checks:
                    query = f"""
                        SELECT COUNT(*)
                        FROM {child_table} c
                        LEFT JOIN {parent_table} p ON c.{child_column} = p.{parent_column}
                        WHERE p.{parent_column} IS NULL
                    """
                    result = await conn.execute(text(query))
                    orphaned_count = result.scalar()

                    if orphaned_count == 0:
                        results.append(
                            ValidationResult(
                                service="database",
                                table=child_table,
                                status=ValidationStatus.PASSED,
                                message=f"All {child_table}.{child_column} references are valid",
                            )
                        )
                    else:
                        results.append(
                            ValidationResult(
                                service="database",
                                table=child_table,
                                status=ValidationStatus.FAILED,
                                message=f"Found {orphaned_count} orphaned records in {child_table}.{child_column}",
                            )
                        )

        except Exception as e:
            logger.error(f"Referential integrity validation failed: {str(e)}")
            results.append(
                ValidationResult(
                    service="database",
                    table="referential_integrity",
                    status=ValidationStatus.FAILED,
                    message=f"Referential integrity validation error: {str(e)}",
                )
            )

        return results

    async def _validate_constraints(self) -> List[ValidationResult]:
        """Validate database constraints"""
        logger.info("Validating database constraints")
        results = []

        if not self.validation_config["validation_settings"]["check_constraints"]:
            results.append(
                ValidationResult(
                    service="database",
                    table="constraints",
                    status=ValidationStatus.SKIPPED,
                    message="Constraint validation disabled",
                )
            )
            return results

        try:
            async with self.db_engine.begin() as conn:
                # Check unique constraints
                unique_checks = [
                    ("users", "username"),
                    ("users", "email"),
                    ("accounts", "account_number"),
                    ("ssot_api_contracts", "canonical_name"),
                ]

                for table, column in unique_checks:
                    query = f"""
                        SELECT COUNT(*)
                        FROM (
                            SELECT {column}, COUNT(*) as count
                            FROM {table}
                            GROUP BY {column}
                            HAVING COUNT(*) > 1
                        ) duplicates
                    """
                    result = await conn.execute(text(query))
                    duplicate_count = result.scalar()

                    if duplicate_count == 0:
                        results.append(
                            ValidationResult(
                                service="database",
                                table=table,
                                status=ValidationStatus.PASSED,
                                message=f"Unique constraint on '{column}' is valid",
                            )
                        )
                    else:
                        results.append(
                            ValidationResult(
                                service="database",
                                table=table,
                                status=ValidationStatus.FAILED,
                                message=f"Unique constraint violation on '{column}': {duplicate_count} duplicates",
                            )
                        )

        except Exception as e:
            logger.error(f"Constraint validation failed: {str(e)}")
            results.append(
                ValidationResult(
                    service="database",
                    table="constraints",
                    status=ValidationStatus.FAILED,
                    message=f"Constraint validation error: {str(e)}",
                )
            )

        return results

    async def _validate_indexes(self) -> List[ValidationResult]:
        """Validate database indexes"""
        logger.info("Validating database indexes")
        results = []

        if not self.validation_config["validation_settings"]["check_indexes"]:
            results.append(
                ValidationResult(
                    service="database",
                    table="indexes",
                    status=ValidationStatus.SKIPPED,
                    message="Index validation disabled",
                )
            )
            return results

        try:
            async with self.db_engine.begin() as conn:
                # Get all indexes
                inspector = inspect(self.db_engine.sync_engine)
                tables = inspector.get_table_names()

                for table in tables:
                    indexes = inspector.get_indexes(table)

                    if indexes:
                        results.append(
                            ValidationResult(
                                service="database",
                                table=table,
                                status=ValidationStatus.PASSED,
                                message=f"Found {len(indexes)} indexes on table '{table}'",
                            )
                        )
                    else:
                        results.append(
                            ValidationResult(
                                service="database",
                                table=table,
                                status=ValidationStatus.WARNING,
                                message=f"No indexes found on table '{table}'",
                            )
                        )

        except Exception as e:
            logger.error(f"Index validation failed: {str(e)}")
            results.append(
                ValidationResult(
                    service="database",
                    table="indexes",
                    status=ValidationStatus.FAILED,
                    message=f"Index validation error: {str(e)}",
                )
            )

        return results

    async def _validate_cross_platform_consistency(self) -> List[ValidationResult]:
        """Validate data consistency across different platforms (DB, Redis, API)"""
        logger.info("Validating cross-platform data consistency")
        results = []

        try:
            # Test 1: Check if critical data exists in both database and cache
            user_count_db = await self._get_database_count("users")
            user_count_cache = await self._get_cache_count("users:*")

            if (
                abs(user_count_db - user_count_cache) <= 1
            ):  # Allow small difference due to timing
                results.append(
                    ValidationResult(
                        service="cross_platform",
                        table="users",
                        status=ValidationStatus.PASSED,
                        message=f"User count consistent: DB={user_count_db}, Cache={user_count_cache}",
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        service="cross_platform",
                        table="users",
                        status=ValidationStatus.FAILED,
                        message=f"User count mismatch: DB={user_count_db}, Cache={user_count_cache}",
                        details={
                            "db_count": user_count_db,
                            "cache_count": user_count_cache,
                        },
                    )
                )

            # Test 2: Check API contract consistency
            contract_count_db = await self._get_database_count("ssot_api_contracts")
            contract_count_cache = await self._get_cache_count("api_contracts:*")

            if contract_count_db == contract_count_cache:
                results.append(
                    ValidationResult(
                        service="cross_platform",
                        table="ssot_api_contracts",
                        status=ValidationStatus.PASSED,
                        message=f"API contract count consistent: DB={contract_count_db}, Cache={contract_count_cache}",
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        service="cross_platform",
                        table="ssot_api_contracts",
                        status=ValidationStatus.WARNING,
                        message=f"API contract count differs: DB={contract_count_db}, Cache={contract_count_cache}",
                        details={
                            "db_count": contract_count_db,
                            "cache_count": contract_count_cache,
                        },
                    )
                )

            # Test 3: Check alias consistency
            alias_count_db = await self._get_database_count("ssot_api_aliases")
            alias_count_cache = await self._get_cache_count("api_aliases:*")

            if alias_count_db == alias_count_cache:
                results.append(
                    ValidationResult(
                        service="cross_platform",
                        table="ssot_api_aliases",
                        status=ValidationStatus.PASSED,
                        message=f"API alias count consistent: DB={alias_count_db}, Cache={alias_count_cache}",
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        service="cross_platform",
                        table="ssot_api_aliases",
                        status=ValidationStatus.WARNING,
                        message=f"API alias count differs: DB={alias_count_db}, Cache={alias_count_cache}",
                        details={
                            "db_count": alias_count_db,
                            "cache_count": alias_count_cache,
                        },
                    )
                )

            # Test 4: Validate sample data integrity across platforms
            sample_validation = await self._validate_sample_data_consistency()
            results.extend(sample_validation)

        except Exception as e:
            logger.error(f"Cross-platform validation failed: {str(e)}")
            results.append(
                ValidationResult(
                    service="cross_platform",
                    table="consistency_check",
                    status=ValidationStatus.FAILED,
                    message=f"Cross-platform validation error: {str(e)}",
                )
            )

        return results

    async def _get_database_count(self, table: str) -> int:
        """Get record count from database"""
        try:
            async with self.db_engine.begin() as conn:
                query = f"SELECT COUNT(*) FROM {table}"
                result = await conn.execute(text(query))
                return result.scalar()
        except Exception:
            return 0

    async def _get_cache_count(self, pattern: str) -> int:
        """Get key count from Redis cache"""
        try:
            if not self.redis_client:
                return 0
            keys = await self.redis_client.keys(pattern)
            return len(keys)
        except Exception:
            return 0

    async def _validate_sample_data_consistency(self) -> List[ValidationResult]:
        """Validate sample data consistency across platforms"""
        results = []

        try:
            # Get sample users from database
            async with self.db_engine.begin() as conn:
                query = "SELECT id, username, email FROM users LIMIT 10"
                result = await conn.execute(text(query))
                db_users = result.fetchall()

            for user in db_users:
                user_id = str(user[0])
                cache_key = f"users:{user_id}"

                # Check if user exists in cache
                cache_data = (
                    await self.redis_client.get(cache_key)
                    if self.redis_client
                    else None
                )

                if cache_data:
                    try:
                        cache_user = json.loads(cache_data)
                        # Compare critical fields
                        if (
                            cache_user.get("username") == user[1]
                            and cache_user.get("email") == user[2]
                        ):
                            results.append(
                                ValidationResult(
                                    service="cross_platform",
                                    table="users",
                                    status=ValidationStatus.PASSED,
                                    message=f"User {user_id} data consistent between DB and cache",
                                )
                            )
                        else:
                            results.append(
                                ValidationResult(
                                    service="cross_platform",
                                    table="users",
                                    status=ValidationStatus.FAILED,
                                    message=f"User {user_id} data mismatch between DB and cache",
                                    details={
                                        "db_data": {
                                            "username": user[1],
                                            "email": user[2],
                                        },
                                        "cache_data": cache_user,
                                    },
                                )
                            )
                    except json.JSONDecodeError:
                        results.append(
                            ValidationResult(
                                service="cross_platform",
                                table="users",
                                status=ValidationStatus.FAILED,
                                message=f"User {user_id} cache data is not valid JSON",
                            )
                        )
                else:
                    results.append(
                        ValidationResult(
                            service="cross_platform",
                            table="users",
                            status=ValidationStatus.WARNING,
                            message=f"User {user_id} not found in cache",
                        )
                    )

        except Exception as e:
            logger.error(f"Sample data consistency validation failed: {str(e)}")
            results.append(
                ValidationResult(
                    service="cross_platform",
                    table="sample_data",
                    status=ValidationStatus.FAILED,
                    message=f"Sample data validation error: {str(e)}",
                )
            )

        return results

    async def _close_connections(self) -> None:
        """Close database and Redis connections"""
        try:
            if self.db_engine:
                await self.db_engine.dispose()
            if self.redis_client:
                await self.redis_client.close()
            logger.info("Database and Redis connections closed")
        except Exception as e:
            logger.error(f"Error closing connections: {str(e)}")

    async def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary statistics"""
        try:
            results = await self.validate_all_schemas()

            return {
                "total_validations": results["total_validations"],
                "passed": results["passed"],
                "failed": results["failed"],
                "warnings": results["warnings"],
                "skipped": results["skipped"],
                "success_rate": (results["passed"] / results["total_validations"] * 100)
                if results["total_validations"] > 0
                else 0,
                "validation_time": results["validation_time"],
                "last_validation": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get validation summary: {str(e)}")
            return {"error": str(e)}


# Global instance
data_schema_validator = DataSchemaValidator()
