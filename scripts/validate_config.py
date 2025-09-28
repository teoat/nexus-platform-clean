#!/usr/bin/env python3
"""
NEXUS Platform - Configuration Validation Script
Validates production configuration and environment variables
"""

import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ConfigValidator:
    """Configuration validation for NEXUS Platform"""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.environment = os.getenv("NEXUS_MODE", "development")

    def validate_environment_variables(self) -> bool:
        """Validate required environment variables"""
        logger.info("Validating environment variables...")

        required_vars = {
            "production": [
                "JWT_SECRET_KEY",
                "ENCRYPTION_KEY",
                "DATABASE_URL",
                "REDIS_URL",
                "POSTGRES_PASSWORD",
                "REDIS_PASSWORD",
            ],
            "staging": [
                "JWT_SECRET_KEY",
                "DATABASE_URL",
                "REDIS_URL",
            ],
            "development": [
                "DATABASE_URL",
                "REDIS_URL",
            ],
        }

        env_required = required_vars.get(self.environment, [])

        for var in env_required:
            value = os.getenv(var)
            if not value:
                self.errors.append(f"Missing required environment variable: {var}")
            elif len(value) < 8 and var.endswith("_KEY"):
                self.errors.append(
                    f"Environment variable {var} is too short (minimum 8 characters)"
                )
            elif var == "JWT_SECRET_KEY" and len(value) < 32:
                self.errors.append(
                    f"JWT_SECRET_KEY is too short (minimum 32 characters)"
                )

        # Validate JWT secret key format
        jwt_secret = os.getenv("JWT_SECRET_KEY")
        if jwt_secret and not re.match(r"^[A-Za-z0-9+/=]{32,}$", jwt_secret):
            self.warnings.append("JWT_SECRET_KEY should be a secure random string")

        # Validate database URL format
        db_url = os.getenv("DATABASE_URL")
        if db_url and not db_url.startswith(("postgresql://", "postgres://")):
            self.errors.append(
                "DATABASE_URL must be a valid PostgreSQL connection string"
            )

        # Validate Redis URL format
        redis_url = os.getenv("REDIS_URL")
        if redis_url and not redis_url.startswith("redis://"):
            self.errors.append("REDIS_URL must be a valid Redis connection string")

        return len(self.errors) == 0

    def validate_file_permissions(self) -> bool:
        """Validate file and directory permissions"""
        logger.info("Validating file permissions...")

        critical_files = [
            "config/production.env",
            "config/security.yaml",
            "ssl/",
            "config/backup.json",
        ]

        for file_path in critical_files:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                # Check if file is world-readable (not secure)
                if bool(stat.st_mode & 0o004):
                    self.errors.append(f"File {file_path} is world-readable (insecure)")
                # Check if file is group-readable when it shouldn't be
                if file_path in ["config/production.env", "ssl/"] and bool(
                    stat.st_mode & 0o040
                ):
                    self.warnings.append(f"File {file_path} is group-readable")

        return len(self.errors) == 0

    def validate_network_connectivity(self) -> bool:
        """Validate network connectivity to required services"""
        logger.info("Validating network connectivity...")

        services = {
            "postgres": ("POSTGRES_HOST", "POSTGRES_PORT", 5432),
            "redis": ("REDIS_HOST", "REDIS_PORT", 6379),
        }

        for service_name, (host_env, port_env, default_port) in services.items():
            host = os.getenv(host_env, f"{service_name}")
            port = int(os.getenv(port_env, default_port))

            try:
                import socket

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((host, port))
                sock.close()

                if result != 0:
                    self.warnings.append(
                        f"Cannot connect to {service_name} at {host}:{port}"
                    )
            except Exception as e:
                self.warnings.append(
                    f"Error checking connectivity to {service_name}: {e}"
                )

        return True  # Warnings don't fail validation

    def validate_security_settings(self) -> bool:
        """Validate security-related settings"""
        logger.info("Validating security settings...")

        # Check debug mode
        if (
            os.getenv("DEBUG", "").lower() == "true"
            and self.environment == "production"
        ):
            self.errors.append("DEBUG mode should be disabled in production")

        # Check log level
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        if log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            self.warnings.append(f"Invalid LOG_LEVEL: {log_level}")

        # Check SSL settings
        ssl_enabled = os.getenv("SSL_ENABLED", "true").lower() == "true"
        if ssl_enabled and self.environment == "production":
            ssl_cert = os.getenv("SSL_CERT_FILE")
            ssl_key = os.getenv("SSL_KEY_FILE")
            if not ssl_cert or not ssl_key:
                self.errors.append(
                    "SSL is enabled but SSL_CERT_FILE or SSL_KEY_FILE not configured"
                )
            elif not os.path.exists(ssl_cert or ""):
                self.errors.append(f"SSL certificate file not found: {ssl_cert}")
            elif not os.path.exists(ssl_key or ""):
                self.errors.append(f"SSL key file not found: {ssl_key}")

        # Check rate limiting
        rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
        if not rate_limit_enabled and self.environment == "production":
            self.warnings.append("Rate limiting is disabled in production")

        return len(self.errors) == 0

    def validate_performance_settings(self) -> bool:
        """Validate performance-related settings"""
        logger.info("Validating performance settings...")

        # Check worker settings
        workers = int(os.getenv("WORKERS", "4"))
        if workers < 1:
            self.errors.append("WORKERS must be at least 1")
        elif workers > 8 and self.environment == "production":
            self.warnings.append(
                f"High worker count ({workers}) may impact performance"
            )

        # Check database pool settings
        db_pool_size = int(os.getenv("DB_POOL_SIZE", "20"))
        if db_pool_size < 5:
            self.warnings.append("Database pool size is very low")
        elif db_pool_size > 50:
            self.warnings.append("Database pool size is very high")

        # Check cache settings
        cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        if not cache_enabled:
            self.warnings.append("Caching is disabled, this may impact performance")

        return len(self.errors) == 0

    def validate_configuration_files(self) -> bool:
        """Validate configuration files"""
        logger.info("Validating configuration files...")

        config_files = [
            "config/security.yaml",
            "config/backup.json",
            "monitoring/prometheus/prometheus.yml",
            "k8s/production-manifests.yaml",
        ]

        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    if config_file.endswith(".yaml") or config_file.endswith(".yml"):
                        import yaml

                        with open(config_file, "r") as f:
                            yaml.safe_load(f)
                    elif config_file.endswith(".json"):
                        with open(config_file, "r") as f:
                            json.load(f)
                    logger.info(f"✓ {config_file} is valid")
                except Exception as e:
                    self.errors.append(f"Invalid configuration file {config_file}: {e}")
            else:
                self.warnings.append(f"Configuration file not found: {config_file}")

        return len(self.errors) == 0

    def generate_report(self) -> Dict[str, Any]:
        """Generate validation report"""
        return {
            "environment": self.environment,
            "timestamp": os.popen('date -u +"%Y-%m-%dT%H:%M:%SZ"').read().strip(),
            "errors": self.errors,
            "warnings": self.warnings,
            "status": "PASS" if not self.errors else "FAIL",
        }

    def run_validation(self) -> bool:
        """Run all validation checks"""
        logger.info(
            f"Starting configuration validation for {self.environment} environment"
        )

        checks = [
            self.validate_environment_variables,
            self.validate_file_permissions,
            self.validate_network_connectivity,
            self.validate_security_settings,
            self.validate_performance_settings,
            self.validate_configuration_files,
        ]

        for check in checks:
            try:
                check()
            except Exception as e:
                self.errors.append(f"Validation check failed: {e}")

        # Generate and save report
        report = self.generate_report()

        report_file = f"config_validation_report_{self.environment}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Validation report saved to {report_file}")

        # Print summary
        print(f"\n{'='*50}")
        print(f"CONFIGURATION VALIDATION REPORT - {self.environment.upper()}")
        print(f"{'='*50}")
        print(f"Status: {report['status']}")
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"Timestamp: {report['timestamp']}")

        if self.errors:
            print(f"\n❌ ERRORS:")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")

        print(f"{'='*50}\n")

        return len(self.errors) == 0


def main():
    """Main entry point"""
    validator = ConfigValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
