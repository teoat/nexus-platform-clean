#!/usr/bin/env python3
"""
NEXUS Platform - Automated Security Scanning
Scheduled security scanning and compliance checking
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import schedule

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from services.security_hardening import (ComplianceStandard,
                                         SecurityHardeningService)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AutomatedSecurityScanner:
    """Automated security scanning and compliance checking"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.security_service = SecurityHardeningService(config)
        self.scan_results = []

        # Scanning schedule configuration
        self.daily_scan_time = self.config.get("daily_scan_time", "02:00")
        self.weekly_scan_time = self.config.get("weekly_scan_time", "03:00")
        self.monthly_scan_time = self.config.get("monthly_scan_time", "04:00")

        # Notification configuration
        self.notification_webhook = self.config.get("notification_webhook")
        self.critical_threshold = self.config.get("critical_threshold", 1)
        self.high_threshold = self.config.get("high_threshold", 3)

    async def run_daily_security_scan(self):
        """Run daily security scan"""
        logger.info("Starting daily security scan")

        try:
            # Run vulnerability scan
            vulnerabilities = await self.security_service.run_security_scan()

            # Run compliance checks
            compliance_checks = await self.security_service.run_compliance_checks()

            # Generate security report
            security_report = self.security_service.generate_security_report()

            # Store results
            scan_result = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "scan_type": "daily",
                "vulnerabilities": len(vulnerabilities),
                "compliance_checks": len(compliance_checks),
                "report": security_report,
                "status": "completed",
            }

            self.scan_results.append(scan_result)

            # Check for critical issues
            critical_vulns = [v for v in vulnerabilities if v.level.value == "critical"]
            if critical_vulns:
                await self._send_critical_alert(scan_result, critical_vulns)

            # Check for high priority issues
            high_vulns = [v for v in vulnerabilities if v.level.value == "high"]
            if len(high_vulns) >= self.high_threshold:
                await self._send_high_priority_alert(scan_result, high_vulns)

            logger.info(
                f"Daily security scan completed. Found {len(vulnerabilities)} vulnerabilities, {len(compliance_checks)} compliance checks"
            )

        except Exception as e:
            logger.error(f"Daily security scan failed: {e}")
            await self._send_error_alert("Daily security scan failed", str(e))

    async def run_weekly_compliance_scan(self):
        """Run weekly comprehensive compliance scan"""
        logger.info("Starting weekly compliance scan")

        try:
            # Run all compliance checks
            compliance_standards = [
                ComplianceStandard.GDPR,
                ComplianceStandard.SOX,
                ComplianceStandard.PCI_DSS,
                ComplianceStandard.HIPAA,
                ComplianceStandard.ISO27001,
            ]

            all_compliance_checks = []
            for standard in compliance_standards:
                checks = await self.security_service.run_compliance_checks()
                all_compliance_checks.extend(checks)

            # Generate compliance report
            compliance_report = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "scan_type": "weekly_compliance",
                "standards_checked": [s.value for s in compliance_standards],
                "total_checks": len(all_compliance_checks),
                "passed_checks": len(
                    [c for c in all_compliance_checks if c.status == "pass"]
                ),
                "failed_checks": len(
                    [c for c in all_compliance_checks if c.status == "fail"]
                ),
                "status": "completed",
            }

            self.scan_results.append(compliance_report)

            # Check for compliance failures
            failed_checks = [c for c in all_compliance_checks if c.status == "fail"]
            if failed_checks:
                await self._send_compliance_alert(compliance_report, failed_checks)

            logger.info(
                f"Weekly compliance scan completed. {compliance_report['passed_checks']}/{compliance_report['total_checks']} checks passed"
            )

        except Exception as e:
            logger.error(f"Weekly compliance scan failed: {e}")
            await self._send_error_alert("Weekly compliance scan failed", str(e))

    async def run_monthly_security_audit(self):
        """Run monthly comprehensive security audit"""
        logger.info("Starting monthly security audit")

        try:
            # Run comprehensive security scan
            vulnerabilities = await self.security_service.run_security_scan()

            # Run all compliance checks
            compliance_checks = await self.security_service.run_compliance_checks()

            # Generate comprehensive security report
            security_report = self.security_service.generate_security_report()

            # Generate audit summary
            audit_summary = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "scan_type": "monthly_audit",
                "vulnerabilities": {
                    "total": len(vulnerabilities),
                    "by_severity": {
                        "critical": len(
                            [v for v in vulnerabilities if v.level.value == "critical"]
                        ),
                        "high": len(
                            [v for v in vulnerabilities if v.level.value == "high"]
                        ),
                        "medium": len(
                            [v for v in vulnerabilities if v.level.value == "medium"]
                        ),
                        "low": len(
                            [v for v in vulnerabilities if v.level.value == "low"]
                        ),
                    },
                },
                "compliance": {
                    "total_checks": len(compliance_checks),
                    "passed": len([c for c in compliance_checks if c.status == "pass"]),
                    "failed": len([c for c in compliance_checks if c.status == "fail"]),
                },
                "recommendations": security_report.get("recommendations", []),
                "status": "completed",
            }

            self.scan_results.append(audit_summary)

            # Send monthly audit report
            await self._send_monthly_audit_report(audit_summary)

            logger.info(
                f"Monthly security audit completed. {audit_summary['vulnerabilities']['total']} vulnerabilities, {audit_summary['compliance']['total_checks']} compliance checks"
            )

        except Exception as e:
            logger.error(f"Monthly security audit failed: {e}")
            await self._send_error_alert("Monthly security audit failed", str(e))

    async def _send_critical_alert(
        self, scan_result: Dict[str, Any], critical_vulns: List[Any]
    ):
        """Send critical security alert"""
        logger.warning(
            f"Sending critical security alert for {len(critical_vulns)} vulnerabilities"
        )

        alert_data = {
            "type": "critical_security_alert",
            "timestamp": scan_result["timestamp"],
            "vulnerabilities": len(critical_vulns),
            "details": [
                {"title": v.title, "description": v.description} for v in critical_vulns
            ],
        }

        await self._send_notification(alert_data)

    async def _send_high_priority_alert(
        self, scan_result: Dict[str, Any], high_vulns: List[Any]
    ):
        """Send high priority security alert"""
        logger.warning(
            f"Sending high priority security alert for {len(high_vulns)} vulnerabilities"
        )

        alert_data = {
            "type": "high_priority_security_alert",
            "timestamp": scan_result["timestamp"],
            "vulnerabilities": len(high_vulns),
            "details": [
                {"title": v.title, "description": v.description} for v in high_vulns
            ],
        }

        await self._send_notification(alert_data)

    async def _send_compliance_alert(
        self, compliance_report: Dict[str, Any], failed_checks: List[Any]
    ):
        """Send compliance failure alert"""
        logger.warning(
            f"Sending compliance alert for {len(failed_checks)} failed checks"
        )

        alert_data = {
            "type": "compliance_failure_alert",
            "timestamp": compliance_report["timestamp"],
            "failed_checks": len(failed_checks),
            "details": [
                {"standard": c.standard.value, "check": c.check_name}
                for c in failed_checks
            ],
        }

        await self._send_notification(alert_data)

    async def _send_monthly_audit_report(self, audit_summary: Dict[str, Any]):
        """Send monthly audit report"""
        logger.info("Sending monthly security audit report")

        report_data = {
            "type": "monthly_security_audit",
            "timestamp": audit_summary["timestamp"],
            "summary": audit_summary,
            "recommendations": audit_summary.get("recommendations", []),
        }

        await self._send_notification(report_data)

    async def _send_error_alert(self, error_type: str, error_message: str):
        """Send error alert"""
        logger.error(f"Sending error alert: {error_type}")

        alert_data = {
            "type": "security_scan_error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error_type": error_type,
            "error_message": error_message,
        }

        await self._send_notification(alert_data)

    async def _send_notification(self, data: Dict[str, Any]):
        """Send notification via webhook"""
        if not self.notification_webhook:
            logger.info("No notification webhook configured, skipping notification")
            return

        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.notification_webhook, json=data
                ) as response:
                    if response.status == 200:
                        logger.info("Notification sent successfully")
                    else:
                        logger.error(f"Failed to send notification: {response.status}")
        except Exception as e:
            logger.error(f"Error sending notification: {e}")

    def setup_schedule(self):
        """Setup automated scanning schedule"""
        logger.info("Setting up automated security scanning schedule")

        # Daily security scan at 2 AM
        schedule.every().day.at(self.daily_scan_time).do(
            lambda: asyncio.create_task(self.run_daily_security_scan())
        )

        # Weekly compliance scan on Sundays at 3 AM
        schedule.every().sunday.at(self.weekly_scan_time).do(
            lambda: asyncio.create_task(self.run_weekly_compliance_scan())
        )

        # Monthly security audit on the 1st at 4 AM
        schedule.every().month.do(
            lambda: asyncio.create_task(self.run_monthly_security_audit())
        )

        logger.info("Security scanning schedule configured")
        logger.info(f"Daily scans: {self.daily_scan_time}")
        logger.info(f"Weekly scans: Sunday {self.weekly_scan_time}")
        logger.info(f"Monthly audits: 1st of month {self.monthly_scan_time}")

    def run_scheduler(self):
        """Run the security scanning scheduler"""
        logger.info("Starting security scanning scheduler")

        self.setup_schedule()

        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def get_scan_history(self) -> List[Dict[str, Any]]:
        """Get scan history"""
        return self.scan_results

    def get_latest_scan_results(self) -> Dict[str, Any]:
        """Get latest scan results"""
        if not self.scan_results:
            return {"error": "No scan results available"}

        latest = self.scan_results[-1]
        return {
            "latest_scan": latest,
            "total_scans": len(self.scan_results),
            "scan_types": list(set(scan["scan_type"] for scan in self.scan_results)),
        }


async def main():
    """Main function to run automated security scanning"""
    logger.info("Starting automated security scanning service")

    # Configuration
    config = {
        "daily_scan_time": "02:00",
        "weekly_scan_time": "03:00",
        "monthly_scan_time": "04:00",
        "notification_webhook": "http://localhost:5001/security-alerts",
        "critical_threshold": 1,
        "high_threshold": 3,
    }

    scanner = AutomatedSecurityScanner(config)

    if "--run-once" in sys.argv:
        # Run scans once for testing
        logger.info("Running security scans once for testing")
        await scanner.run_daily_security_scan()
        await scanner.run_weekly_compliance_scan()
        await scanner.run_monthly_security_audit()

        # Print results
        results = scanner.get_latest_scan_results()
        print(json.dumps(results, indent=2, default=str))
    else:
        # Run continuous scheduler
        scanner.run_scheduler()


if __name__ == "__main__":
    asyncio.run(main())
