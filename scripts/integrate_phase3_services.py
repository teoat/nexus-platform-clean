#!/usr/bin/env python3
"""
NEXUS Platform - Phase 3 Services Integration
Integrate AI optimization, performance monitoring, security hardening,
deployment automation, and analytics services
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from services.ai_optimizer import AISSOTOptimizer
from services.analytics_engine import AIAnalyticsEngine, AnalyticsType
from services.deployment_automation import DeploymentAutomationService
from services.performance_monitor import PerformanceMonitor
from services.security_hardening import SecurityHardeningService

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Phase3IntegrationService:
    """Integration service for Phase 3 optimization services"""

    def __init__(self):
        self.services = {}
        self.integration_results = {}

    async def initialize_services(self) -> Dict[str, Any]:
        """Initialize all Phase 3 services"""
        logger.info("Initializing Phase 3 services")

        results = {"success": True, "services": {}, "errors": []}

        try:
            # Initialize AI Optimizer
            logger.info("Initializing AI SSOT Optimizer")
            self.services["ai_optimizer"] = AISSOTOptimizer(
                ssot_registry=None,  # Would be actual registry instance
                config={
                    "ml_enabled": True,
                    "optimization_threshold": 0.1,
                    "confidence_threshold": 0.8,
                },
            )
            results["services"]["ai_optimizer"] = "initialized"

            # Initialize Performance Monitor
            logger.info("Initializing Performance Monitor")
            self.services["performance_monitor"] = PerformanceMonitor(
                config={
                    "collection_interval": 30,
                    "alert_thresholds": {
                        "cpu_percent": 80.0,
                        "memory_percent": 85.0,
                        "response_time": 2.0,
                        "error_rate": 0.05,
                    },
                }
            )
            results["services"]["performance_monitor"] = "initialized"

            # Initialize Security Hardening
            logger.info("Initializing Security Hardening Service")
            self.services["security_hardening"] = SecurityHardeningService(
                config={
                    "password_min_length": 12,
                    "session_timeout": 1800,
                    "max_login_attempts": 3,
                }
            )
            results["services"]["security_hardening"] = "initialized"

            # Initialize Deployment Automation
            logger.info("Initializing Deployment Automation Service")
            self.services["deployment_automation"] = DeploymentAutomationService(
                config={
                    "health_check_endpoints": [
                        "http://localhost:8000/health",
                        "http://localhost:3000/health",
                    ],
                    "rollback_timeout": 300,
                }
            )
            results["services"]["deployment_automation"] = "initialized"

            # Initialize Analytics Engine
            logger.info("Initializing AI Analytics Engine")
            self.services["analytics_engine"] = AIAnalyticsEngine(
                config={
                    "anomaly_threshold": 2.0,
                    "trend_window": 7,
                    "min_data_points": 10,
                }
            )
            results["services"]["analytics_engine"] = "initialized"

            logger.info("All Phase 3 services initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing services: {e}")
            results["success"] = False
            results["errors"].append(str(e))

        return results

    async def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run comprehensive analysis using all services"""
        logger.info("Running comprehensive Phase 3 analysis")

        analysis_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": True,
            "analysis": {},
            "recommendations": [],
            "errors": [],
        }

        try:
            # Performance Analysis
            logger.info("Running performance analysis")
            performance_metrics = await self.services[
                "performance_monitor"
            ].collect_metrics()
            analysis_results["analysis"]["performance"] = {
                "metrics": performance_metrics.__dict__
                if performance_metrics
                else None,
                "summary": self.services[
                    "performance_monitor"
                ].get_performance_summary(),
            }

            # Security Analysis
            logger.info("Running security analysis")
            vulnerabilities = await self.services[
                "security_hardening"
            ].run_security_scan()
            compliance_checks = await self.services[
                "security_hardening"
            ].run_compliance_checks()
            security_report = self.services[
                "security_hardening"
            ].generate_security_report()

            analysis_results["analysis"]["security"] = {
                "vulnerabilities": len(vulnerabilities),
                "compliance_checks": len(compliance_checks),
                "report": security_report,
            }

            # AI Optimization Analysis
            logger.info("Running AI optimization analysis")
            optimization_opportunities = await self.services[
                "ai_optimizer"
            ].get_optimization_opportunities()
            analysis_results["analysis"]["optimization"] = {
                "opportunities": len(optimization_opportunities),
                "recommendations": [
                    {
                        "id": opp.id,
                        "type": opp.type.value,
                        "description": opp.description,
                        "performance_gain": opp.performance_gain,
                        "confidence_score": opp.confidence_score,
                    }
                    for opp in optimization_opportunities
                ],
            }

            # Analytics Analysis
            logger.info("Running analytics analysis")
            time_range = (
                datetime.now(timezone.utc) - timedelta(days=7),
                datetime.now(timezone.utc),
            )

            usage_insights = await self.services[
                "analytics_engine"
            ].analyze_usage_patterns(time_range)
            predictive_insights = await self.services[
                "analytics_engine"
            ].generate_predictive_insights()

            analysis_results["analysis"]["analytics"] = {
                "usage_insights": len(usage_insights),
                "predictive_insights": len(predictive_insights),
                "insights_summary": await self.services[
                    "analytics_engine"
                ].get_insights_summary(),
            }

            # Generate Recommendations
            analysis_results["recommendations"] = await self._generate_recommendations(
                analysis_results
            )

        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            analysis_results["success"] = False
            analysis_results["errors"].append(str(e))

        return analysis_results

    async def _generate_recommendations(
        self, analysis_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []

        # Performance recommendations
        if "performance" in analysis_results["analysis"]:
            perf_data = analysis_results["analysis"]["performance"]
            if perf_data.get("summary", {}).get("average_cpu", 0) > 70:
                recommendations.append(
                    {
                        "category": "performance",
                        "priority": "high",
                        "title": "High CPU Usage",
                        "description": "CPU usage is above 70%, consider scaling or optimization",
                        "action": "Scale horizontally or optimize resource usage",
                    }
                )

        # Security recommendations
        if "security" in analysis_results["analysis"]:
            sec_data = analysis_results["analysis"]["security"]
            if sec_data.get("vulnerabilities", 0) > 0:
                recommendations.append(
                    {
                        "category": "security",
                        "priority": "critical",
                        "title": "Security Vulnerabilities",
                        "description": f"Found {sec_data['vulnerabilities']} security vulnerabilities",
                        "action": "Address vulnerabilities immediately",
                    }
                )

        # Optimization recommendations
        if "optimization" in analysis_results["analysis"]:
            opt_data = analysis_results["analysis"]["optimization"]
            if opt_data.get("opportunities", 0) > 0:
                recommendations.append(
                    {
                        "category": "optimization",
                        "priority": "medium",
                        "title": "Optimization Opportunities",
                        "description": f"Found {opt_data['opportunities']} optimization opportunities",
                        "action": "Review and apply optimization recommendations",
                    }
                )

        return recommendations

    async def start_monitoring_services(self):
        """Start all monitoring services"""
        logger.info("Starting monitoring services")

        tasks = []

        # Start performance monitoring
        if "performance_monitor" in self.services:
            task = asyncio.create_task(
                self.services["performance_monitor"].start_monitoring()
            )
            tasks.append(task)

        # Start AI optimization monitoring
        if "ai_optimizer" in self.services:
            task = asyncio.create_task(
                self.services["ai_optimizer"].run_continuous_optimization()
            )
            tasks.append(task)

        # Start analytics monitoring
        if "analytics_engine" in self.services:
            task = asyncio.create_task(self._run_analytics_monitoring())
            tasks.append(task)

        logger.info(f"Started {len(tasks)} monitoring services")
        return tasks

    async def _run_analytics_monitoring(self):
        """Run continuous analytics monitoring"""
        while True:
            try:
                # Generate analytics insights every hour
                time_range = (
                    datetime.now(timezone.utc) - timedelta(hours=1),
                    datetime.now(timezone.utc),
                )

                insights = await self.services[
                    "analytics_engine"
                ].analyze_usage_patterns(time_range)
                logger.info(f"Generated {len(insights)} analytics insights")

                await asyncio.sleep(3600)  # Wait 1 hour

            except Exception as e:
                logger.error(f"Error in analytics monitoring: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def generate_integration_report(self) -> Dict[str, Any]:
        """Generate comprehensive integration report"""
        logger.info("Generating Phase 3 integration report")

        report = {
            "integration_timestamp": datetime.now(timezone.utc).isoformat(),
            "services_status": {},
            "capabilities": [],
            "next_steps": [],
        }

        # Check service status
        for service_name, service in self.services.items():
            report["services_status"][service_name] = "active"

        # List capabilities
        report["capabilities"] = [
            "AI-driven SSOT optimization",
            "Real-time performance monitoring",
            "Automated security hardening",
            "Blue-green deployment automation",
            "AI-powered analytics and insights",
            "Predictive performance analysis",
            "Compliance checking (GDPR, SOX, PCI-DSS)",
            "Automated vulnerability scanning",
            "Usage pattern analysis",
            "Deployment rollback automation",
        ]

        # Next steps
        report["next_steps"] = [
            "Configure production monitoring dashboards",
            "Set up alerting for critical metrics",
            "Implement automated security scanning schedule",
            "Configure deployment pipelines",
            "Set up analytics dashboards",
            "Train AI models with production data",
            "Implement automated rollback triggers",
            "Set up compliance reporting",
        ]

        return report


async def main():
    """Main function to run Phase 3 integration"""
    logger.info("Starting Phase 3 services integration")

    integration_service = Phase3IntegrationService()

    try:
        # Initialize services
        init_results = await integration_service.initialize_services()

        if not init_results["success"]:
            logger.error("Failed to initialize services")
            logger.error(f"Errors: {init_results['errors']}")
            sys.exit(1)

        logger.info("Services initialized successfully")

        # Run comprehensive analysis
        analysis_results = await integration_service.run_comprehensive_analysis()

        if not analysis_results["success"]:
            logger.error("Analysis failed")
            logger.error(f"Errors: {analysis_results['errors']}")
            sys.exit(1)

        logger.info("Comprehensive analysis completed")

        # Generate integration report
        report = await integration_service.generate_integration_report()

        # Save results
        results_file = Path("phase3_integration_results.json")
        with open(results_file, "w") as f:
            json.dump(
                {
                    "initialization": init_results,
                    "analysis": analysis_results,
                    "report": report,
                },
                f,
                indent=2,
                default=str,
            )

        logger.info(f"Integration results saved to: {results_file}")

        # Print summary
        print("\n" + "=" * 60)
        print("PHASE 3 INTEGRATION RESULTS")
        print("=" * 60)
        print(f"Services Initialized: {len(init_results['services'])}")
        print(f"Analysis Success: {analysis_results['success']}")
        print(f"Recommendations: {len(analysis_results['recommendations'])}")
        print(f"Capabilities: {len(report['capabilities'])}")
        print("=" * 60)

        # Start monitoring services (optional)
        if "--monitor" in sys.argv:
            logger.info("Starting monitoring services...")
            monitoring_tasks = await integration_service.start_monitoring_services()

            try:
                await asyncio.gather(*monitoring_tasks)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")

    except Exception as e:
        logger.critical(f"Phase 3 integration failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
