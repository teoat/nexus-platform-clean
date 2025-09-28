# Scripts Directory Documentation

This directory contains various scripts used for deployment, development, testing, and utility tasks within the NEXUS Platform.

## Table of Contents

- [Deployment Scripts](#deployment-scripts)
- [Development Scripts](#development-scripts)
- [Testing Scripts](#testing-scripts)
- [Backup Scripts](#backup-scripts)
- [Monitoring Scripts](#monitoring-scripts)
- [Utility Scripts](#utility-scripts)
- [Agent-Related Scripts](#agent-related-scripts)
- [Outdated/Redundant Scripts](#outdatedredundant-scripts)

---

## Deployment Scripts

Scripts related to deploying the NEXUS Platform to various environments.

- `deploy-production.sh`: Main script for deploying the NEXUS Platform to a production environment using Docker Compose.
- `deploy_all_next_steps.sh`: Orchestrates multiple deployment steps.
- `deploy_infrastructure.py`: Python script for deploying infrastructure (likely cloud resources).
- `deploy_local.py`: Python script for local deployment.
- `deploy_phase1.py`: Script for a specific phase of deployment.
- `deploy_production_complete.py`: Comprehensive production deployment script (Python).
- `deploy_production.py`: Python script for production deployment.
- `deploy_to_aws.py`: Python script for deploying to AWS.
- `deploy-eks.sh`: Script for deploying to Amazon EKS (Kubernetes).
- `deploy-infrastructure.sh`: Generic infrastructure deployment script.
- `deploy-k8s.sh`: Script for deploying to Kubernetes.
- `deploy-optimized.sh`: Optimized deployment script.
- `deploy.sh`: Generic deployment script.
- `deployment_config.py`: Python script for deployment configuration.
- `fix_and_deploy.sh`: Script to fix issues and then deploy.
- `quick_deploy.sh`: Quick deployment script.
- `simple_deploy.sh`: Simple deployment script.
- `test_deployment.sh`: Script to test deployments.
- `setup-production-ssl.sh`: Automates SSL certificate generation and renewal using Certbot with Nginx.

## Development Scripts

Scripts to assist with local development workflows.

- `dev.sh`: Development environment setup script.
- `consolidated_run_backend.py`: Runs the backend in a consolidated manner.
- `consolidated_startup_checks_backend.py`: Performs startup checks for the backend.
- `run_automated_security_scan.sh`: Runs an automated security scan.
- `run_production_improvements.py`: Applies production improvements.
- `run_security_audit.sh`: Runs a security audit.
- `setup_local_dev.py`: Sets up the local development environment.
- `start_all_services.sh`: Starts all services.
- `start_enhanced_system.py`: Starts an enhanced system.
- `start_local_dev.py`: Starts the local development environment.
- `start_simple_dev.py`: Starts a simple development environment.
- `start-hub.sh`: Starts the coordination hub.
- `__pip-runner__.py`: Internal pip runner script.

## Testing Scripts

Scripts for running various tests.

- `run-tests.sh`: Generic script to run tests.
- `run_performance_tests.sh`: Runs performance tests.
- `run-uv-pytest.sh`: Runs pytest with uvicorn.
- `setup-uv-pytest.sh`: Sets up pytest with uvicorn.
- `test_backup_restore.sh`: Tests backup and restore functionality.
- `test_outputs.py`: Tests script outputs.
- `consolidated_conftest_backend.py`: Consolidated conftest for backend tests.
- `consolidated_run_tests_backend.py`: Consolidated script to run backend tests.
- `consolidated_test_auth_backend.py`: Consolidated authentication backend tests.
- `consolidated_test_backend_backend.py`: Consolidated general backend tests.
- `consolidated_test_caching_backend.py`: Consolidated caching backend tests.
- `consolidated_test_final_comprehensive_backend.py`: Consolidated comprehensive backend tests.
- `consolidated_test_monitoring_backend.py`: Consolidated monitoring backend tests.
- `consolidated_test_performance_backend.py`: Consolidated performance backend tests.
- `consolidated_test_simple_backend.py`: Consolidated simple backend tests.
- `load_testing.py`: Python script for load testing.
- `qwen_code.py`: Related to Qwen code (AI model).
- `solution.sh`: Generic solution script (purpose unclear).

## Backup Scripts

Scripts for managing backups.

- `automated_backup.py`: Python script for automated backups.
- `backup_strategy.py`: Python script defining backup strategies.
- `backup-strategy.sh`: Shell script for backup strategies.
- `backup.py`: Python backup script.
- `gdpr_compliance.py`: Python script for GDPR compliance related to backups.
- `run_backup.sh`: Runs a backup.
- `setup_cron.sh`: Sets up cron jobs for backups.
- `setup_financial_config.py`: Sets up financial configuration (might be related to data for backups).

## Monitoring Scripts

Scripts for monitoring the platform.

- `anomaly_detection_model.py`: Python script for anomaly detection.
- `predictive_analytics.py`: Python script for predictive analytics.
- `risk_assessment_model.py`: Python script for risk assessment.
- `smart_alerting.py`: Python script for smart alerting.
- `start-monitoring.sh`: Starts the monitoring system.

## Utility Scripts

General utility scripts.

- `aggressive_cleanup_script.py`: Aggressive cleanup script.
- `automated_security_scan.py`: Automated security scan.
- `check_prerequisites.sh`: Checks deployment prerequisites.
- `check_services_health.sh`: Checks health of services.
- `ci_orchestration.py`: CI orchestration script.
- `cleanup_dead_code.py`: Cleans up dead code.
- `comprehensive_system_fix.py`: Comprehensive system fix script.
- `create_alias.sh`: Creates shell aliases.
- `database_migration.py`: Database migration script.
- `disaster-recovery.sh`: Disaster recovery script.
- `generate_api_docs.py`: Generates API documentation.
- `generate_secrets.py`: Generates secrets.
- `generate-ssl.sh`: Generates SSL certificates (potentially redundant with `setup-production-ssl.sh`).
- `health-check.sh`: Performs a health check.
- `implement_next_week.py`: Script for implementing next week's tasks.
- `launch_nexus_ssot.py`: Launches Nexus SSOT.
- `migrate_to_postgres.py`: Migrates to PostgreSQL.
- `nexus_automation_ssot.py`: Nexus automation SSOT.
- `performance_tuning.py`: Performance tuning script.
- `pr-triage.sh`: Pull request triage script.
- `quality-dashboard.py`: Quality dashboard script.
- `scripts.py`: Generic scripts file (likely a collection of functions).
- `security_audit.py`: Security audit script.
- `security-scan.py`: Security scan script.
- `setup_postgresql.py`: Sets up PostgreSQL.
- `setup_production_domain.sh`: Sets up production domain.
- `setup_production_environment.sh`: Sets up production environment.
- `setup_production.py`: Sets up production.
- `setup-monorepo.sh`: Sets up monorepo.
- `staging_validation.py`: Staging validation script.
- `stop_all_services.sh`: Stops all services.
- `stop-hub.sh`: Stops the coordination hub.
- `stop.sh`: Stops services.
- `todo_quality_checker.py`: TODO quality checker.
- `validate_naming_conventions.py`: Validates naming conventions.
- `validate_naming.py`: Validates naming.
- `validate_production.py`: Validates production.

## Agent-Related Scripts

Scripts related to agent coordination and management.

- `agent-connect.js`: JavaScript script for agent connection.
- `agent-coordination.js`: JavaScript script for agent coordination.
- `job-queue.js`: JavaScript script for job queue management.
- `load-balancer.js`: JavaScript script for agent load balancing.
- `load-testing.js`: JavaScript script for load testing.
- `performance-monitor.js`: JavaScript script for performance monitoring.
- `send-coordination-messages.js`: Sends coordination messages.
- `start-all-agents.js`: Starts all agents.
- `start-hub.js`: Starts the coordination hub.
- `test-hub.js`: Tests the coordination hub.

## Outdated/Redundant Scripts

These scripts appear to be redundant or have been superseded by other scripts or tools. I recommend reviewing them for potential archiving or removal.

- `deploy-local.sh`: Likely superseded by `deploy_local.py` or other deployment scripts.
- `deploy.sh`: Generic deployment script, likely superseded by more specific ones.
- `run-tests.sh`: Generic test runner, likely superseded by `consolidated_run_tests_backend.py` or CI/CD.
- `security_audit.py`: There are multiple security audit/scan scripts. Review for consolidation.
- `generate-ssl.sh`: Redundant with `setup-production-ssl.sh`.
- `scripts.py`: Generic name, likely contains functions that could be integrated elsewhere or removed.
- `stop.sh`: Generic stop script, likely superseded by `stop_all_services.sh` or Docker Compose commands.
- `start-local-dev.sh`: Likely superseded by `start_local_dev.py` or other development scripts.
- `optimize-production-build.sh`: Review if this is still needed with the new Docker Compose setup.
- `dependency-manager.py`: Review its functionality and if it's still relevant with Poetry.
- `qwen_code.py`: Unclear purpose, review for relevance.
- `solution.sh`: Unclear purpose, review for relevance.
- `disaster-recovery.sh`: There's also `scripts/utilities/disaster-recovery.sh`. Review for consolidation.
