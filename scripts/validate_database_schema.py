#!/usr/bin/env python3
"""
Database Schema Validation Script for NEXUS Platform
Validates database schema against defined models for consistency.
"""

import json
import os
import sys

from sqlalchemy import create_engine, inspect

from backend.database.models.ssot_models import Base


def validate_schema():
    """Validate database schema against models"""
    # Database connection
    database_url = os.getenv(
        "DATABASE_URL", "postgresql://nexus:nexus123@localhost:5432/nexus_platform"
    )

    # Create engine and inspector
    engine = create_engine(database_url)
    inspector = inspect(engine)

    # Get expected tables from models
    expected_tables = Base.metadata.tables.keys()

    # Get actual tables from database
    actual_tables = inspector.get_table_names()

    print("=== Database Schema Validation ===")
    print(f"Expected tables: {sorted(expected_tables)}")
    print(f"Actual tables: {sorted(actual_tables)}")

    # Check for missing tables
    missing_tables = expected_tables - set(actual_tables)
    if missing_tables:
        print(f"❌ Missing tables: {missing_tables}")
        return False
    else:
        print("✅ All expected tables exist")

    # Validate table schemas
    all_valid = True
    for table_name in expected_tables:
        expected_columns = Base.metadata.tables[table_name].columns.keys()
        actual_columns = [col["name"] for col in inspector.get_columns(table_name)]

        missing_columns = set(expected_columns) - set(actual_columns)
        extra_columns = set(actual_columns) - set(expected_columns)

        if missing_columns or extra_columns:
            print(f"❌ Schema mismatch for table '{table_name}':")
            if missing_columns:
                print(f"   Missing columns: {missing_columns}")
            if extra_columns:
                print(f"   Extra columns: {extra_columns}")
            all_valid = False
        else:
            print(f"✅ Schema valid for table '{table_name}'")

    if all_valid:
        print("🎉 Database schema validation passed!")
        return True
    else:
        print("❌ Database schema validation failed!")
        return False


def generate_schema_report():
    """Generate a schema report"""
    database_url = os.getenv(
        "DATABASE_URL", "postgresql://nexus:nexus123@localhost:5432/nexus_platform"
    )
    engine = create_engine(database_url)
    inspector = inspect(engine)

    report = {"tables": {}, "validation_status": "unknown"}

    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        report["tables"][table_name] = {
            "columns": {
                col["name"]: {
                    "type": str(col["type"]),
                    "nullable": col["nullable"],
                    "primary_key": col["primary_key"],
                }
                for col in columns
            }
        }

    # Write report to file
    with open("/tmp/schema_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("📄 Schema report generated: /tmp/schema_report.json")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        generate_schema_report()
    else:
        success = validate_schema()
        sys.exit(0 if success else 1)
