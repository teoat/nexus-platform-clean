#!/usr/bin/env python3
"""
NEXUS Platform - Automated Compliance Reporting
Generate and distribute compliance reports automatically
"""

import asyncio
import json
import logging
import smtplib
import sys
import time
from datetime import datetime, timedelta, timezone
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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


class AutomatedComplianceReporter:
    """Automated compliance reporting service"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.security_service = SecurityHardeningService(config)
        self.report_history = []

        # Reporting configuration
        self.report_recipients = self.config.get("report_recipients", [])
        self.smtp_config = self.config.get("smtp_config", {})
        self.report_formats = self.config.get("report_formats", ["json", "pdf", "html"])

        # Compliance standards to report on
        self.compliance_standards = [
            ComplianceStandard.GDPR,
            ComplianceStandard.SOX,
            ComplianceStandard.PCI_DSS,
            ComplianceStandard.HIPAA,
            ComplianceStandard.ISO27001,
        ]

    async def generate_compliance_report(
        self, report_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Generate compliance report"""
        logger.info(f"Generating {report_type} compliance report")

        try:
            # Run security scan
            vulnerabilities = await self.security_service.run_security_scan()

            # Run compliance checks
            compliance_checks = await self.security_service.run_compliance_checks()

            # Generate security report
            security_report = self.security_service.generate_security_report()

            # Generate compliance report
            compliance_report = {
                "report_id": f"compliance_report_{int(datetime.now().timestamp())}",
                "report_type": report_type,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "compliance_standards": [
                    std.value for std in self.compliance_standards
                ],
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
                    "details": [
                        {
                            "id": v.id,
                            "level": v.level.value,
                            "title": v.title,
                            "description": v.description,
                            "affected_component": v.affected_component,
                            "remediation": v.remediation,
                            "detected_at": v.detected_at.isoformat(),
                        }
                        for v in vulnerabilities
                    ],
                },
                "compliance_checks": {
                    "total": len(compliance_checks),
                    "passed": len([c for c in compliance_checks if c.status == "pass"]),
                    "failed": len([c for c in compliance_checks if c.status == "fail"]),
                    "by_standard": self._group_checks_by_standard(compliance_checks),
                    "details": [
                        {
                            "standard": c.standard.value,
                            "check_name": c.check_name,
                            "status": c.status,
                            "details": c.details,
                            "last_checked": c.last_checked.isoformat(),
                        }
                        for c in compliance_checks
                    ],
                },
                "security_policies": {
                    "password_policy": self.security_service.security_policies[
                        "password_policy"
                    ],
                    "session_policy": self.security_service.security_policies[
                        "session_policy"
                    ],
                    "access_control": self.security_service.security_policies[
                        "access_control"
                    ],
                    "data_protection": self.security_service.security_policies[
                        "data_protection"
                    ],
                },
                "recommendations": security_report.get("recommendations", []),
                "summary": {
                    "overall_compliance_score": self._calculate_compliance_score(
                        compliance_checks
                    ),
                    "security_risk_level": self._calculate_security_risk_level(
                        vulnerabilities
                    ),
                    "compliance_status": self._determine_compliance_status(
                        compliance_checks
                    ),
                    "next_review_date": (
                        datetime.now(timezone.utc) + timedelta(days=30)
                    ).isoformat(),
                },
            }

            # Store report
            self.report_history.append(compliance_report)

            logger.info(
                f"Compliance report generated successfully. "
                f"Vulnerabilities: {len(vulnerabilities)}, "
                f"Compliance checks: {len(compliance_checks)}"
            )

            return compliance_report

        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            return {"error": str(e)}

    def _group_checks_by_standard(
        self, compliance_checks: List[Any]
    ) -> Dict[str, Dict[str, int]]:
        """Group compliance checks by standard"""
        grouped = {}
        for check in compliance_checks:
            standard = check.standard.value
            if standard not in grouped:
                grouped[standard] = {"total": 0, "passed": 0, "failed": 0}

            grouped[standard]["total"] += 1
            if check.status == "pass":
                grouped[standard]["passed"] += 1
            else:
                grouped[standard]["failed"] += 1

        return grouped

    def _calculate_compliance_score(self, compliance_checks: List[Any]) -> float:
        """Calculate overall compliance score"""
        if not compliance_checks:
            return 0.0

        passed_checks = len([c for c in compliance_checks if c.status == "pass"])
        total_checks = len(compliance_checks)

        return (passed_checks / total_checks) * 100

    def _calculate_security_risk_level(self, vulnerabilities: List[Any]) -> str:
        """Calculate security risk level"""
        critical_count = len(
            [v for v in vulnerabilities if v.level.value == "critical"]
        )
        high_count = len([v for v in vulnerabilities if v.level.value == "high"])

        if critical_count > 0:
            return "CRITICAL"
        elif high_count > 3:
            return "HIGH"
        elif high_count > 0:
            return "MEDIUM"
        else:
            return "LOW"

    def _determine_compliance_status(self, compliance_checks: List[Any]) -> str:
        """Determine overall compliance status"""
        if not compliance_checks:
            return "UNKNOWN"

        failed_checks = len([c for c in compliance_checks if c.status == "fail"])
        total_checks = len(compliance_checks)

        if failed_checks == 0:
            return "COMPLIANT"
        elif failed_checks / total_checks < 0.1:  # Less than 10% failed
            return "MOSTLY_COMPLIANT"
        else:
            return "NON_COMPLIANT"

    async def generate_report_files(self, report: Dict[str, Any]) -> Dict[str, str]:
        """Generate report files in different formats"""
        report_files = {}

        try:
            # Generate JSON report
            if "json" in self.report_formats:
                json_file = f"reports/compliance_report_{report['report_id']}.json"
                Path(json_file).parent.mkdir(parents=True, exist_ok=True)
                with open(json_file, "w") as f:
                    json.dump(report, f, indent=2, default=str)
                report_files["json"] = json_file

            # Generate HTML report
            if "html" in self.report_formats:
                html_file = f"reports/compliance_report_{report['report_id']}.html"
                html_content = self._generate_html_report(report)
                Path(html_file).parent.mkdir(parents=True, exist_ok=True)
                with open(html_file, "w") as f:
                    f.write(html_content)
                report_files["html"] = html_file

            # Generate PDF report (placeholder)
            if "pdf" in self.report_formats:
                pdf_file = f"reports/compliance_report_{report['report_id']}.pdf"
                # In a real implementation, you would use a library like reportlab
                # to generate PDF reports
                report_files["pdf"] = pdf_file

            logger.info(f"Generated report files: {list(report_files.keys())}")

        except Exception as e:
            logger.error(f"Error generating report files: {e}")

        return report_files

    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generate HTML compliance report"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>NEXUS Compliance Report - {report['report_id']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .vulnerability {{ background-color: #ffe6e6; padding: 10px; margin: 5px 0; border-radius: 3px; }}
                .compliance-check {{ background-color: #e6f3ff; padding: 10px; margin: 5px 0; border-radius: 3px; }}
                .passed {{ background-color: #e6ffe6; }}
                .failed {{ background-color: #ffe6e6; }}
                .summary {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>NEXUS Compliance Report</h1>
                <p><strong>Report ID:</strong> {report['report_id']}</p>
                <p><strong>Generated:</strong> {report['generated_at']}</p>
                <p><strong>Type:</strong> {report['report_type']}</p>
            </div>

            <div class="section">
                <h2>Summary</h2>
                <div class="summary">
                    <p><strong>Overall Compliance Score:</strong> {report['summary']['overall_compliance_score']:.1f}%</p>
                    <p><strong>Security Risk Level:</strong> {report['summary']['security_risk_level']}</p>
                    <p><strong>Compliance Status:</strong> {report['summary']['compliance_status']}</p>
                    <p><strong>Next Review Date:</strong> {report['summary']['next_review_date']}</p>
                </div>
            </div>

            <div class="section">
                <h2>Vulnerabilities ({report['vulnerabilities']['total']})</h2>
                <p><strong>Critical:</strong> {report['vulnerabilities']['by_severity']['critical']} |
                   <strong>High:</strong> {report['vulnerabilities']['by_severity']['high']} |
                   <strong>Medium:</strong> {report['vulnerabilities']['by_severity']['medium']} |
                   <strong>Low:</strong> {report['vulnerabilities']['by_severity']['low']}</p>
        """

        for vuln in report["vulnerabilities"]["details"]:
            html += f"""
                <div class="vulnerability">
                    <h4>{vuln['title']} ({vuln['level'].upper()})</h4>
                    <p><strong>Description:</strong> {vuln['description']}</p>
                    <p><strong>Affected Component:</strong> {vuln['affected_component']}</p>
                    <p><strong>Remediation:</strong> {vuln['remediation']}</p>
                    <p><strong>Detected:</strong> {vuln['detected_at']}</p>
                </div>
            """

        html += """
            </div>

            <div class="section">
                <h2>Compliance Checks</h2>
        """

        for check in report["compliance_checks"]["details"]:
            status_class = "passed" if check["status"] == "pass" else "failed"
            html += f"""
                <div class="compliance-check {status_class}">
                    <h4>{check['check_name']} ({check['standard']})</h4>
                    <p><strong>Status:</strong> {check['status'].upper()}</p>
                    <p><strong>Details:</strong> {check['details']}</p>
                    <p><strong>Last Checked:</strong> {check['last_checked']}</p>
                </div>
            """

        html += """
            </div>

            <div class="section">
                <h2>Recommendations</h2>
                <ul>
        """

        for rec in report["recommendations"]:
            html += f"<li>{rec}</li>"

        html += """
                </ul>
            </div>
        </body>
        </html>
        """

        return html

    async def send_compliance_report(
        self, report: Dict[str, Any], report_files: Dict[str, str]
    ):
        """Send compliance report via email"""
        if not self.report_recipients or not self.smtp_config:
            logger.info("No email configuration, skipping email notification")
            return

        try:
            # Create email message
            msg = MIMEMultipart()
            msg["From"] = self.smtp_config.get(
                "from_email", "nexus-compliance@company.com"
            )
            msg["To"] = ", ".join(self.report_recipients)
            msg["Subject"] = f"NEXUS Compliance Report - {report['report_id']}"

            # Email body
            body = f"""
            NEXUS Compliance Report

            Report ID: {report['report_id']}
            Generated: {report['generated_at']}
            Type: {report['report_type']}

            Summary:
            - Overall Compliance Score: {report['summary']['overall_compliance_score']:.1f}%
            - Security Risk Level: {report['summary']['security_risk_level']}
            - Compliance Status: {report['summary']['compliance_status']}

            Vulnerabilities: {report['vulnerabilities']['total']}
            - Critical: {report['vulnerabilities']['by_severity']['critical']}
            - High: {report['vulnerabilities']['by_severity']['high']}
            - Medium: {report['vulnerabilities']['by_severity']['medium']}
            - Low: {report['vulnerabilities']['by_severity']['low']}

            Compliance Checks: {report['compliance_checks']['total']}
            - Passed: {report['compliance_checks']['passed']}
            - Failed: {report['compliance_checks']['failed']}

            Please review the attached report files for detailed information.
            """

            msg.attach(MIMEText(body, "plain"))

            # Attach report files
            for format_type, file_path in report_files.items():
                if Path(file_path).exists():
                    with open(file_path, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename= {Path(file_path).name}",
                        )
                        msg.attach(part)

            # Send email
            server = smtplib.SMTP(
                self.smtp_config["smtp_server"], self.smtp_config["smtp_port"]
            )
            server.starttls()
            server.login(self.smtp_config["username"], self.smtp_config["password"])
            text = msg.as_string()
            server.sendmail(msg["From"], self.report_recipients, text)
            server.quit()

            logger.info(
                f"Compliance report sent to {len(self.report_recipients)} recipients"
            )

        except Exception as e:
            logger.error(f"Error sending compliance report: {e}")

    async def run_daily_compliance_check(self):
        """Run daily compliance check and report"""
        logger.info("Running daily compliance check")

        try:
            # Generate report
            report = await self.generate_compliance_report("daily")

            if "error" in report:
                logger.error(f"Failed to generate compliance report: {report['error']}")
                return

            # Generate report files
            report_files = await self.generate_report_files(report)

            # Send report if there are critical issues
            if report["summary"]["security_risk_level"] in ["CRITICAL", "HIGH"]:
                await self.send_compliance_report(report, report_files)

            logger.info("Daily compliance check completed")

        except Exception as e:
            logger.error(f"Daily compliance check failed: {e}")

    async def run_weekly_compliance_report(self):
        """Run weekly comprehensive compliance report"""
        logger.info("Running weekly compliance report")

        try:
            # Generate comprehensive report
            report = await self.generate_compliance_report("weekly")

            if "error" in report:
                logger.error(f"Failed to generate compliance report: {report['error']}")
                return

            # Generate report files
            report_files = await self.generate_report_files(report)

            # Always send weekly report
            await self.send_compliance_report(report, report_files)

            logger.info("Weekly compliance report completed")

        except Exception as e:
            logger.error(f"Weekly compliance report failed: {e}")

    async def run_monthly_compliance_audit(self):
        """Run monthly compliance audit"""
        logger.info("Running monthly compliance audit")

        try:
            # Generate audit report
            report = await self.generate_compliance_report("monthly_audit")

            if "error" in report:
                logger.error(f"Failed to generate compliance report: {report['error']}")
                return

            # Generate report files
            report_files = await self.generate_report_files(report)

            # Send audit report
            await self.send_compliance_report(report, report_files)

            logger.info("Monthly compliance audit completed")

        except Exception as e:
            logger.error(f"Monthly compliance audit failed: {e}")

    def setup_schedule(self):
        """Setup automated compliance reporting schedule"""
        logger.info("Setting up automated compliance reporting schedule")

        # Daily compliance check at 6 AM
        schedule.every().day.at("06:00").do(
            lambda: asyncio.create_task(self.run_daily_compliance_check())
        )

        # Weekly report on Mondays at 7 AM
        schedule.every().monday.at("07:00").do(
            lambda: asyncio.create_task(self.run_weekly_compliance_report())
        )

        # Monthly audit on the 1st at 8 AM
        schedule.every().month.do(
            lambda: asyncio.create_task(self.run_monthly_compliance_audit())
        )

        logger.info("Compliance reporting schedule configured")

    def run_scheduler(self):
        """Run the compliance reporting scheduler"""
        logger.info("Starting compliance reporting scheduler")

        self.setup_schedule()

        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


async def main():
    """Main function to run automated compliance reporting"""
    logger.info("Starting automated compliance reporting service")

    # Configuration
    config = {
        "report_recipients": [
            "compliance-team@company.com",
            "devops-team@company.com",
            "security-team@company.com",
        ],
        "smtp_config": {
            "smtp_server": "smtp.company.com",
            "smtp_port": 587,
            "username": "nexus-compliance@company.com",
            "password": "password",
            "from_email": "nexus-compliance@company.com",
        },
        "report_formats": ["json", "html", "pdf"],
    }

    reporter = AutomatedComplianceReporter(config)

    if "--run-once" in sys.argv:
        # Run compliance report once for testing
        logger.info("Running compliance report once for testing")
        report = await reporter.generate_compliance_report("test")
        report_files = await reporter.generate_report_files(report)
        await reporter.send_compliance_report(report, report_files)

        # Print results
        print(json.dumps(report, indent=2, default=str))
    else:
        # Run continuous scheduler
        reporter.run_scheduler()


if __name__ == "__main__":
    asyncio.run(main())
