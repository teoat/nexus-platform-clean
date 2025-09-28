#!/usr/bin/env python3
# NEXUS SSOT Compliance Checking Script

"""
This script performs compliance checks for the NEXUS SSOT system.
It validates configurations, security settings, and operational standards.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import yaml

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/compliance.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class ComplianceChecker:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.issues = []
        self.passed = 0
        self.failed = 0

    def run_all_checks(self) -> Dict[str, any]:
        """
        Run all compliance checks.

        Returns:
            Dict[str, any]: Compliance report
        """
        logger.info("Starting compliance checks")

        self._check_configuration_files()
        self._check_security_settings()
        self._check_audit_logging()
        self._check_data_retention()
        self._check_access_controls()
        self._check_encryption()
        self._check_backup_procedures()

        report = {
            "timestamp": datetime.now().isoformat(),
            "total_checks": self.passed + self.failed,
            "passed": self.passed,
            "failed": self.failed,
            "issues": self.issues,
            "compliance_score": round(
                (self.passed / (self.passed + self.failed)) * 100, 2
            )
            if (self.passed + self.failed) > 0
            else 0,
        }

        logger.info(f"Compliance check completed. Score: {report['compliance_score']}%")
        return report

    def _check_configuration_files(self):
        """Check configuration files for compliance."""
        required_files = ["config/environments.yaml", "config/alias_governance.yaml"]

        for file_path in required_files:
            if not Path(file_path).exists():
                self._add_issue(
                    "CONFIG",
                    f"Missing required configuration file: {file_path}",
                    "HIGH",
                )
            else:
                self._add_pass("CONFIG", f"Configuration file exists: {file_path}")

    def _check_security_settings(self):
        """Check security settings for compliance."""
        try:
            if Path("config/environments.yaml").exists():
                with open("config/environments.yaml", "r") as f:
                    config = yaml.safe_load(f)

                # Check production security settings
                prod_config = config.get("production", {})
                security = prod_config.get("security", {})

                if not security.get("encryption_enabled", False):
                    self._add_issue(
                        "SECURITY", "Encryption not enabled in production", "HIGH"
                    )

                if security.get("token_expiration", 0) < 3600:
                    self._add_issue(
                        "SECURITY", "Token expiration too short in production", "MEDIUM"
                    )

                if not prod_config.get("api", {}).get("ssl_enabled", False):
                    self._add_issue(
                        "SECURITY", "SSL not enabled for production API", "HIGH"
                    )

                self._add_pass("SECURITY", "Security settings validated")
        except Exception as e:
            self._add_issue(
                "SECURITY", f"Error checking security settings: {e}", "HIGH"
            )

    def _check_audit_logging(self):
        """Check audit logging configuration."""
        try:
            # Check if audit service is configured
            if Path("backend/services/audit_retention.py").exists():
                self._add_pass("AUDIT", "Audit logging service exists")
            else:
                self._add_issue("AUDIT", "Audit logging service not found", "MEDIUM")

            # Check log retention
            if Path("config/environments.yaml").exists():
                with open("config/environments.yaml", "r") as f:
                    config = yaml.safe_load(f)

                prod_audit = (
                    config.get("services", {})
                    .get("audit_service", {})
                    .get("production", {})
                )
                retention_days = prod_audit.get("retention_days", 0)

                if retention_days >= 2555:  # 7 years
                    self._add_pass(
                        "AUDIT", f"Audit log retention: {retention_days} days"
                    )
                else:
                    self._add_issue(
                        "AUDIT",
                        f"Insufficient audit log retention: {retention_days} days",
                        "HIGH",
                    )

        except Exception as e:
            self._add_issue("AUDIT", f"Error checking audit logging: {e}", "MEDIUM")

    def _check_data_retention(self):
        """Check data retention policies."""
        try:
            # Check if retention policies are defined
            if Path("backend/services/audit_retention.py").exists():
                self._add_pass("RETENTION", "Data retention policies implemented")
            else:
                self._add_issue(
                    "RETENTION", "Data retention policies not implemented", "MEDIUM"
                )
        except Exception as e:
            self._add_issue(
                "RETENTION", f"Error checking data retention: {e}", "MEDIUM"
            )

    def _check_access_controls(self):
        """Check access control settings."""
        try:
            if Path("config/environments.yaml").exists():
                with open("config/environments.yaml", "r") as f:
                    config = yaml.safe_load(f)

                prod_api = config.get("production", {}).get("api", {})

                if "cors_origins" in prod_api:
                    self._add_pass("ACCESS", "CORS origins configured for production")
                else:
                    self._add_issue(
                        "ACCESS", "CORS origins not configured for production", "MEDIUM"
                    )

                if prod_api.get("rate_limit", 0) > 0:
                    self._add_pass(
                        "ACCESS",
                        f'Rate limiting configured: {prod_api["rate_limit"]} req/min',
                    )
                else:
                    self._add_issue(
                        "ACCESS",
                        "Rate limiting not configured for production",
                        "MEDIUM",
                    )

        except Exception as e:
            self._add_issue("ACCESS", f"Error checking access controls: {e}", "MEDIUM")

    def _check_encryption(self):
        """Check encryption settings."""
        try:
            if Path("config/environments.yaml").exists():
                with open("config/environments.yaml", "r") as f:
                    config = yaml.safe_load(f)

                prod_config = config.get("production", {})

                if prod_config.get("security", {}).get("encryption_enabled", False):
                    self._add_pass("ENCRYPTION", "Encryption enabled in production")
                else:
                    self._add_issue(
                        "ENCRYPTION", "Encryption not enabled in production", "HIGH"
                    )

                if prod_config.get("database", {}).get("ssl_mode") == "require":
                    self._add_pass("ENCRYPTION", "Database SSL enabled")
                else:
                    self._add_issue("ENCRYPTION", "Database SSL not required", "HIGH")

        except Exception as e:
            self._add_issue("ENCRYPTION", f"Error checking encryption: {e}", "HIGH")

    def _check_backup_procedures(self):
        """Check backup procedures."""
        try:
            if Path("scripts/backup_dr.py").exists():
                self._add_pass("BACKUP", "Backup procedures implemented")
            else:
                self._add_issue("BACKUP", "Backup procedures not implemented", "HIGH")

            if Path("config/environments.yaml").exists():
                with open("config/environments.yaml", "r") as f:
                    config = yaml.safe_load(f)

                prod_features = config.get("production", {}).get("features", {})

                if prod_features.get("backup_enabled", False):
                    self._add_pass("BACKUP", "Automated backups enabled")
                else:
                    self._add_issue("BACKUP", "Automated backups not enabled", "HIGH")

        except Exception as e:
            self._add_issue("BACKUP", f"Error checking backup procedures: {e}", "HIGH")

    def _add_issue(self, category: str, description: str, severity: str):
        """Add a compliance issue."""
        issue = {
            "category": category,
            "description": description,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
        }
        self.issues.append(issue)
        self.failed += 1
        logger.warning(f"Compliance issue [{category}]: {description} ({severity})")

    def _add_pass(self, category: str, description: str):
        """Add a passed compliance check."""
        self.passed += 1
        logger.info(f"Compliance check passed [{category}]: {description}")


def main():
    parser = argparse.ArgumentParser(description="NEXUS SSOT Compliance Checker")
    parser.add_argument(
        "--config-dir", default="config", help="Configuration directory"
    )
    parser.add_argument(
        "--output", default="compliance_report.json", help="Output report file"
    )
    parser.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )

    args = parser.parse_args()

    checker = ComplianceChecker(args.config_dir)
    report = checker.run_all_checks()

    if args.format == "json":
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Compliance report saved to {args.output}")
    else:
        print("\n=== NEXUS SSOT Compliance Report ===")
        print(f"Timestamp: {report['timestamp']}")
        print(f"Total Checks: {report['total_checks']}")
        print(f"Passed: {report['passed']}")
        print(f"Failed: {report['failed']}")
        print(f"Compliance Score: {report['compliance_score']}%")

        if report["failed"] > 0:
            print("\n=== Issues Found ===")
            for issue in report["issues"]:
                print(
                    f"[{issue['category']}] {issue['description']} ({issue['severity']})"
                )

        print("\n=== Recommendations ===")
        if report["compliance_score"] < 80:
            print("- Address high-severity issues immediately")
            print("- Implement missing security controls")
            print("- Review and update configurations")
        elif report["compliance_score"] < 95:
            print("- Address medium-severity issues")
            print("- Enhance monitoring and logging")
        else:
            print("- Maintain current compliance standards")
            print("- Regular reviews recommended")


if __name__ == "__main__":
    main()
