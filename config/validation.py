"""
NEXUS Platform - Configuration Validation
This module provides comprehensive validation for configuration files.
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of configuration validation"""

    is_valid: bool
    errors: List[str]
    warnings: List[str]


class ConfigValidator:
    """
    Comprehensive configuration validator for the NEXUS platform.
    """

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_config(self, config: Dict[str, Any]) -> ValidationResult:
        """
        Validate complete configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            ValidationResult with validation status and messages
        """
        self.errors = []
        self.warnings = []

        # Validate each section
        self._validate_system_config(config.get("system", {}))
        self._validate_database_config(config.get("database", {}))
        self._validate_api_config(config.get("api", {}))
        self._validate_security_config(config.get("security", {}))
        self._validate_performance_config(config.get("performance", {}))
        self._validate_monitoring_config(config.get("monitoring", {}))
        self._validate_logging_config(config.get("logging", {}))
        self._validate_file_management_config(config.get("file_management", {}))
        self._validate_workers_config(config.get("workers", {}))
        self._validate_processing_config(config.get("processing", {}))
        self._validate_features_config(config.get("features", {}))

        # Validate environment variables
        self._validate_environment_variables()

        # Cross-section validation
        self._validate_cross_section_constraints(config)

        return ValidationResult(
            is_valid=len(self.errors) == 0,
            errors=self.errors.copy(),
            warnings=self.warnings.copy(),
        )

    def _validate_system_config(self, config: Dict[str, Any]) -> None:
        """Validate system configuration section"""
        if not config.get("name"):
            self.errors.append("system.name is required")

        if not config.get("version"):
            self.errors.append("system.version is required")

        workspace_path = config.get("workspace_path")
        if workspace_path and not Path(workspace_path).exists():
            self.warnings.append(
                f"system.workspace_path may not exist: {workspace_path}"
            )

    def _validate_database_config(self, config: Dict[str, Any]) -> None:
        """Validate database configuration section"""
        required_fields = ["host", "name", "user"]
        for field in required_fields:
            if not config.get(field):
                self.errors.append(f"database.{field} is required")

        port = config.get("port")
        if port is not None:
            if not isinstance(port, int) or not (1 <= port <= 65535):
                self.errors.append(
                    f"database.port must be an integer between 1 and 65535, got: {port}"
                )

        connection_timeout = config.get("connection_timeout")
        if connection_timeout is not None:
            if (
                not isinstance(connection_timeout, (int, float))
                or connection_timeout <= 0
            ):
                self.errors.append(
                    f"database.connection_timeout must be a positive number, got: {connection_timeout}"
                )

        pool_size_min = config.get("pool_size_min")
        pool_size_max = config.get("pool_size_max")
        if pool_size_min is not None and pool_size_max is not None:
            if pool_size_min > pool_size_max:
                self.errors.append(
                    "database.pool_size_min cannot be greater than pool_size_max"
                )

    def _validate_api_config(self, config: Dict[str, Any]) -> None:
        """Validate API configuration section"""
        port = config.get("port")
        if port is not None:
            if not isinstance(port, int) or not (1 <= port <= 65535):
                self.errors.append(
                    f"api.port must be an integer between 1 and 65535, got: {port}"
                )

        timeout = config.get("timeout")
        if timeout is not None:
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                self.errors.append(
                    f"api.timeout must be a positive number, got: {timeout}"
                )

        rate_limit = config.get("rate_limit")
        if rate_limit is not None:
            if not isinstance(rate_limit, int) or rate_limit <= 0:
                self.errors.append(
                    f"api.rate_limit must be a positive integer, got: {rate_limit}"
                )

        max_requests = config.get("max_requests_per_minute")
        if max_requests is not None:
            if not isinstance(max_requests, int) or max_requests <= 0:
                self.errors.append(
                    f"api.max_requests_per_minute must be a positive integer, got: {max_requests}"
                )

    def _validate_security_config(self, config: Dict[str, Any]) -> None:
        """Validate security configuration section"""
        if config.get("enable_authentication"):
            if not config.get("jwt_secret_key"):
                self.errors.append(
                    "security.jwt_secret_key is required when authentication is enabled"
                )

            if len(config.get("jwt_secret_key", "")) < 32:
                self.warnings.append(
                    "security.jwt_secret_key should be at least 32 characters long"
                )

        password_min_length = config.get("password_min_length")
        if password_min_length is not None:
            if not isinstance(password_min_length, int) or password_min_length < 8:
                self.errors.append(
                    f"security.password_min_length must be an integer >= 8, got: {password_min_length}"
                )

        jwt_expiry = config.get("jwt_expiry_hours")
        if jwt_expiry is not None:
            if not isinstance(jwt_expiry, (int, float)) or jwt_expiry <= 0:
                self.errors.append(
                    f"security.jwt_expiry_hours must be a positive number, got: {jwt_expiry}"
                )

    def _validate_performance_config(self, config: Dict[str, Any]) -> None:
        """Validate performance configuration section"""
        profile_interval = config.get("profile_interval")
        if profile_interval is not None:
            if not isinstance(profile_interval, (int, float)) or profile_interval <= 0:
                self.errors.append(
                    f"performance.profile_interval must be a positive number, got: {profile_interval}"
                )

    def _validate_monitoring_config(self, config: Dict[str, Any]) -> None:
        """Validate monitoring configuration section"""
        interval = config.get("interval")
        if interval is not None:
            if not isinstance(interval, (int, float)) or interval <= 0:
                self.errors.append(
                    f"monitoring.interval must be a positive number, got: {interval}"
                )

        metrics_history_size = config.get("metrics_history_size")
        if metrics_history_size is not None:
            if not isinstance(metrics_history_size, int) or metrics_history_size <= 0:
                self.errors.append(
                    f"monitoring.metrics_history_size must be a positive integer, got: {metrics_history_size}"
                )

        thresholds = config.get("alert_thresholds", {})
        for threshold_name, threshold_value in thresholds.items():
            if not isinstance(threshold_value, (int, float)) or threshold_value < 0:
                self.errors.append(
                    f"monitoring.alert_thresholds.{threshold_name} must be a non-negative number, got: {threshold_value}"
                )

    def _validate_logging_config(self, config: Dict[str, Any]) -> None:
        """Validate logging configuration section"""
        level = config.get("level")
        if level:
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if level not in valid_levels:
                self.errors.append(
                    f"logging.level must be one of {valid_levels}, got: {level}"
                )

        backup_count = config.get("backup_count")
        if backup_count is not None:
            if not isinstance(backup_count, int) or backup_count < 0:
                self.errors.append(
                    f"logging.backup_count must be a non-negative integer, got: {backup_count}"
                )

    def _validate_file_management_config(self, config: Dict[str, Any]) -> None:
        """Validate file management configuration section"""
        batch_size = config.get("batch_size")
        if batch_size is not None:
            if not isinstance(batch_size, int) or batch_size <= 0:
                self.errors.append(
                    f"file_management.batch_size must be a positive integer, got: {batch_size}"
                )

        update_interval = config.get("update_interval")
        if update_interval is not None:
            if not isinstance(update_interval, (int, float)) or update_interval <= 0:
                self.errors.append(
                    f"file_management.update_interval must be a positive number, got: {update_interval}"
                )

        backup_interval = config.get("backup_interval")
        if backup_interval is not None:
            if not isinstance(backup_interval, (int, float)) or backup_interval <= 0:
                self.errors.append(
                    f"file_management.backup_interval must be a positive number, got: {backup_interval}"
                )

    def _validate_workers_config(self, config: Dict[str, Any]) -> None:
        """Validate workers configuration section"""
        min_workers = config.get("min_workers")
        max_workers = config.get("max_workers")

        if min_workers is not None and max_workers is not None:
            if not isinstance(min_workers, int) or min_workers <= 0:
                self.errors.append(
                    f"workers.min_workers must be a positive integer, got: {min_workers}"
                )
            if not isinstance(max_workers, int) or max_workers <= 0:
                self.errors.append(
                    f"workers.max_workers must be a positive integer, got: {max_workers}"
                )
            if min_workers > max_workers:
                self.errors.append(
                    "workers.min_workers cannot be greater than max_workers"
                )

        target_cpu = config.get("target_cpu")
        if target_cpu is not None:
            if not isinstance(target_cpu, (int, float)) or not (0 <= target_cpu <= 100):
                self.errors.append(
                    f"workers.target_cpu must be a number between 0 and 100, got: {target_cpu}"
                )

        scaling = config.get("scaling", {})
        if scaling:
            for key in ["cpu_threshold_low", "cpu_threshold_high", "memory_threshold"]:
                if key in scaling:
                    value = scaling[key]
                    if not isinstance(value, (int, float)) or not (0 <= value <= 100):
                        self.errors.append(
                            f"workers.scaling.{key} must be a number between 0 and 100, got: {value}"
                        )

    def _validate_processing_config(self, config: Dict[str, Any]) -> None:
        """Validate processing configuration section"""
        cycle_duration = config.get("cycle_duration")
        if cycle_duration is not None:
            if not isinstance(cycle_duration, (int, float)) or cycle_duration <= 0:
                self.errors.append(
                    f"processing.cycle_duration must be a positive number, got: {cycle_duration}"
                )

        max_retries = config.get("max_retries")
        if max_retries is not None:
            if not isinstance(max_retries, int) or max_retries < 0:
                self.errors.append(
                    f"processing.max_retries must be a non-negative integer, got: {max_retries}"
                )

        retry_delay = config.get("retry_delay")
        if retry_delay is not None:
            if not isinstance(retry_delay, (int, float)) or retry_delay <= 0:
                self.errors.append(
                    f"processing.retry_delay must be a positive number, got: {retry_delay}"
                )

    def _validate_features_config(self, config: Dict[str, Any]) -> None:
        """Validate features configuration section"""
        # All feature flags should be boolean
        for key, value in config.items():
            if not isinstance(value, bool):
                self.warnings.append(
                    f"features.{key} should be a boolean, got: {type(value).__name__}"
                )

    def _validate_environment_variables(self) -> None:
        """Validate critical environment variables"""
        # Example: Check for DATABASE_URL
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            self.errors.append("Environment variable DATABASE_URL is required.")
        elif not database_url.startswith(
            "postgresql://"
        ) and not database_url.startswith("sqlite:///"):
            self.errors.append(
                "Environment variable DATABASE_URL must be a valid PostgreSQL or SQLite URL."
            )

        # Example: Check for API_KEY
        api_key = os.getenv("API_KEY")
        if not api_key:
            self.errors.append("Environment variable API_KEY is required.")
        elif len(api_key) < 16:
            self.warnings.append(
                "Environment variable API_KEY is too short, consider a longer key for security."
            )

        # Example: Check for DEBUG mode
        debug_mode = os.getenv("DEBUG", "False").lower()
        if debug_mode not in ["true", "false"]:
            self.errors.append("Environment variable DEBUG must be 'true' or 'false'.")

    def _validate_cross_section_constraints(self, config: Dict[str, Any]) -> None:
        """Validate constraints that span multiple sections"""
        # If authentication is enabled, ensure JWT secret is set
        security_config = config.get("security", {})
        if security_config.get("enable_authentication"):
            if not security_config.get("jwt_secret_key"):
                self.errors.append(
                    "JWT secret key is required when authentication is enabled"
                )

        # If profiling is enabled, ensure reasonable interval
        performance_config = config.get("performance", {})
        if performance_config.get("enable_profiling"):
            interval = performance_config.get("profile_interval", 0)
            if interval < 10:
                self.warnings.append(
                    "Profile interval is very low (< 10 seconds), consider increasing for better performance"
                )

        # If monitoring is enabled, ensure reasonable interval
        monitoring_config = config.get("monitoring", {})
        interval = monitoring_config.get("interval", 0)
        if interval > 60:
            self.warnings.append(
                "Monitoring interval is high (> 60 seconds), consider reducing for better responsiveness"
            )


# Example usage
if __name__ == "__main__":
    # Test validation
    validator = ConfigValidator()

    # Test with sample config
    test_config = {
        "system": {"name": "Test", "version": "1.0.0"},
        "database": {"host": "localhost", "name": "test"},
        "api": {"port": 8000},
        "security": {"enable_authentication": True, "jwt_secret_key": "test-key"},
        "features": {"test_feature": True},
    }

    result = validator.validate_config(test_config)
    print("Validation Result:")
    print(f"Valid: {result.is_valid}")
    print(f"Errors: {result.errors}")
    print(f"Warnings: {result.warnings}")
