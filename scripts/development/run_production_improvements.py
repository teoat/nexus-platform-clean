#!/usr/bin/env python3
"""
NEXUS Platform - Production Improvements Runner
Execute all production readiness improvements
"""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_security_scan():
    """Run automated security scanning"""
    logger.info("🔍 Running security scan...")
    try:
        result = run_security_scan(str(project_root))

        logger.info(f"Security Score: {result['security_score']}/100")
        logger.info(f"Security Grade: {result['security_grade']}")
        logger.info(f"Vulnerabilities found: {result['total_vulnerabilities']}")

        return result
    except Exception as e:
        logger.error(f"Security scan failed: {e}")
        return None


def run_vulnerability_assessment():
    """Run vulnerability assessment"""
    logger.info("🔍 Running vulnerability assessment...")
    try:
        result = run_vulnerability_assessment(str(project_root))

        logger.info(f"Risk Score: {result['risk_score']}/100")
        logger.info(f"Risk Level: {result['risk_level']}")
        logger.info(f"Issues found: {result['total_issues']}")

        return result
    except Exception as e:
        logger.error(f"Vulnerability assessment failed: {e}")
        return None


def run_dead_code_cleanup():
    """Run dead code cleanup"""
    logger.info("🧹 Running dead code cleanup...")
    try:
        result = run_dead_code_cleanup(str(project_root))

        logger.info(f"Files removed: {result['files_removed']}")
        logger.info(f"Directories cleaned: {result['directories_cleaned']}")
        logger.info(f"Lines of code removed: {result['lines_removed']}")

        return result
    except Exception as e:
        logger.error(f"Dead code cleanup failed: {e}")
        return None


def run_postgresql_migration():
    """Run PostgreSQL migration"""
    logger.info("🔄 Running PostgreSQL migration...")
    try:
        # Check if PostgreSQL is available
        postgres_config = {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": os.getenv("POSTGRES_PORT", "5432"),
            "database": os.getenv("POSTGRES_DB", "nexus"),
            "user": os.getenv("POSTGRES_USER", "nexus"),
            "password": os.getenv("POSTGRES_PASSWORD", "nexus_password"),
        }

        result = run_postgresql_migration("nexus.db", postgres_config)

        if result["status"] == "success":
            logger.info("✅ PostgreSQL migration completed successfully")
            logger.info(f"Tables migrated: {result['summary']['tables_migrated']}")
        else:
            logger.error(f"❌ Migration failed: {result['error']}")

        return result
    except Exception as e:
        logger.error(f"PostgreSQL migration failed: {e}")
        return None


def update_response_standardization():
    """Update response standardization"""
    logger.info("📝 Updating response standardization...")
    try:
        # Update main.py to include response standardizer middleware
        main_py_path = project_root / "backend" / "main.py"

        if main_py_path.exists():
            with open(main_py_path, "r") as f:
                content = f.read()

            # Add response standardizer import
            if (
                "from backend.middleware.response_standardizer import response_standardizer_middleware"
                not in content
            ):
                content = content.replace(
                    "from backend.middleware.rate_limiter import rate_limit_middleware",
                    "from backend.middleware.rate_limiter import rate_limit_middleware\nfrom backend.middleware.response_standardizer import response_standardizer_middleware",
                )

            # Add response standardizer middleware
            if (
                'app.middleware("http")(response_standardizer_middleware)'
                not in content
            ):
                content = content.replace(
                    'app.middleware("http")(input_validation_middleware)',
                    'app.middleware("http")(input_validation_middleware)\napp.middleware("http")(response_standardizer_middleware)',
                )

            with open(main_py_path, "w") as f:
                f.write(content)

            logger.info("✅ Response standardization updated")
            return True
        else:
            logger.warning(
                "main.py not found, skipping response standardization update"
            )
            return False

    except Exception as e:
        logger.error(f"Response standardization update failed: {e}")
        return False


def install_dependencies():
    """Install required dependencies"""
    logger.info("📦 Installing dependencies...")
    try:
        # Install security tools
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "bandit", "safety", "semgrep"],
            check=True,
        )
        logger.info("✅ Security tools installed")

        # Install PostgreSQL driver
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "psycopg2-binary"], check=True
        )
        logger.info("✅ PostgreSQL driver installed")

        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Dependency installation failed: {e}")
        return False


def generate_final_report(results: dict):
    """Generate final improvement report"""
    report = {
        "improvement_timestamp": datetime.utcnow().isoformat() + "Z",
        "project_root": str(project_root),
        "improvements_completed": {
            "security_scanning": results.get("security_scan") is not None,
            "vulnerability_assessment": results.get("vulnerability_assessment")
            is not None,
            "dead_code_cleanup": results.get("dead_code_cleanup") is not None,
            "postgresql_migration": results.get("postgresql_migration", {}).get(
                "status"
            )
            == "success",
            "response_standardization": results.get("response_standardization", False),
            "dependencies_installed": results.get("dependencies_installed", False),
        },
        "results": results,
        "summary": {
            "total_improvements": len(
                [v for v in results.values() if v is not None and v is not False]
            ),
            "successful_improvements": len(
                [
                    v
                    for v in results.values()
                    if v is not None and v is not False and v is not True
                ]
            ),
            "production_ready": (
                (results.get("security_scan") or {}).get("security_score", 0) >= 80
                and (results.get("vulnerability_assessment") or {}).get("risk_score", 0)
                >= 60
                and (results.get("postgresql_migration") or {}).get("status")
                == "success"
            ),
        },
    }

    # Save report
    report_path = project_root / "production_improvements_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"📄 Final report saved to: {report_path}")
    return report


def main():
    """Main improvement runner"""
    logger.info("🚀 Starting NEXUS Platform Production Improvements...")

    results = {}

    # Step 1: Install dependencies
    results["dependencies_installed"] = install_dependencies()

    # Step 2: Run security scanning
    results["security_scan"] = run_security_scan()

    # Step 3: Run vulnerability assessment
    results["vulnerability_assessment"] = run_vulnerability_assessment()

    # Step 4: Run dead code cleanup
    results["dead_code_cleanup"] = run_dead_code_cleanup()

    # Step 5: Update response standardization
    results["response_standardization"] = update_response_standardization()

    # Step 6: Run PostgreSQL migration (optional)
    if os.getenv("ENABLE_POSTGRESQL_MIGRATION", "false").lower() == "true":
        results["postgresql_migration"] = run_postgresql_migration()
    else:
        logger.info(
            "PostgreSQL migration skipped (set ENABLE_POSTGRESQL_MIGRATION=true to enable)"
        )
        results["postgresql_migration"] = {"status": "skipped"}

    # Step 7: Generate final report
    try:
        final_report = generate_final_report(results)
    except Exception as e:
        logger.error(f"Failed to generate final report: {e}")
        final_report = {"status": "error", "message": str(e)}

    # Print summary
    logger.info("\n" + "=" * 50)
    logger.info("🎉 PRODUCTION IMPROVEMENTS COMPLETED")
    logger.info("=" * 50)
    logger.info(
        f"Security Score: {results.get('security_scan', {}).get('security_score', 'N/A')}/100"
    )
    logger.info(
        f"Risk Score: {results.get('vulnerability_assessment', {}).get('risk_score', 'N/A')}/100"
    )
    logger.info(
        f"Files Cleaned: {results.get('dead_code_cleanup', {}).get('files_removed', 'N/A')}"
    )
    logger.info(
        f"PostgreSQL Migration: {results.get('postgresql_migration', {}).get('status', 'N/A')}"
    )
    logger.info(f"Production Ready: {final_report['summary']['production_ready']}")
    logger.info("=" * 50)

    return final_report


if __name__ == "__main__":
    main()
