"""
NEXUS Platform - Configuration Manager
This module provides centralized configuration management with validation.
"""

import logging
import os

import yaml

logger = logging.getLogger(__name__)


@dataclass
class ConfigValidationError(Exception):
    """Custom exception for configuration validation errors"""

    field: str
    value: Any
    reason: str


class ConfigManager:
    """
    Centralized configuration manager for the NEXUS platform.

    This class handles loading, merging, and validating configuration
    from multiple sources with proper precedence.
    """

    def __init__(self, environment: str = None, config_dir: str = None):
        """
        Initialize the configuration manager.

        Args:
            environment: Environment name (development, staging, production)
            config_dir: Path to configuration directory
        """
        self.environment = environment or os.getenv("APP_ENV", "development")
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent
        self._config = None
        self._load_config()

    def _load_config(self) -> None:
        """Load and merge configuration from all sources"""
        try:
            # Start with default configuration
            self._config = DEFAULT_CONFIG.copy()

            # Load base configuration
            base_config = self._load_yaml_file(self.config_dir / "base.yaml")
            if base_config:
                self._deep_merge(self._config, base_config)

            # Load environment-specific configuration
            env_config_path = (
                self.config_dir / "environments" / f"{self.environment}.yaml"
            )
            env_config = self._load_yaml_file(env_config_path)
            if env_config:
                self._deep_merge(self._config, env_config)

            # Load environment variables
            self._load_environment_variables()

            # Validate configuration
            self._validate_config()

            logger.info(
                f"Configuration loaded successfully for environment: {self.environment}"
            )

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise

    def _load_yaml_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load YAML configuration file"""
        try:
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            return None
        except Exception as e:
            logger.warning(f"Failed to load config file {file_path}: {e}")
            return None

    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> None:
        """Deep merge two dictionaries"""
        for key, value in update.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def _load_environment_variables(self) -> None:
        """Load configuration from environment variables"""
        # Database configuration
        db_config = self._config.get("database", {})
        db_config["host"] = os.getenv("DB_HOST", db_config.get("host"))
        db_config["port"] = int(os.getenv("DB_PORT", db_config.get("port", 5432)))
        db_config["name"] = os.getenv("DB_NAME", db_config.get("name"))
        db_config["user"] = os.getenv("DB_USER", db_config.get("user"))
        db_config["password"] = os.getenv("DB_PASSWORD", db_config.get("password"))

        # API configuration
        api_config = self._config.get("api", {})
        api_config["host"] = os.getenv("API_HOST", api_config.get("host", "localhost"))
        api_config["port"] = int(os.getenv("API_PORT", api_config.get("port", 8000)))
        api_config["debug"] = os.getenv("API_DEBUG", "false").lower() == "true"

        # Security configuration
        security_config = self._config.get("security", {})
        security_config["jwt_secret_key"] = os.getenv(
            "JWT_SECRET_KEY", security_config.get("jwt_secret_key")
        )
        security_config["enable_encryption"] = (
            os.getenv("ENABLE_ENCRYPTION", "false").lower() == "true"
        )
        security_config["enable_authentication"] = (
            os.getenv("ENABLE_AUTHENTICATION", "false").lower() == "true"
        )

        # Logging configuration
        logging_config = self._config.get("logging", {})
        logging_config["level"] = os.getenv(
            "LOG_LEVEL", logging_config.get("level", "INFO")
        )

    def _validate_config(self) -> None:
        """Validate configuration values"""
        # Database validation
        db_config = self._config.get("database", {})
        if not db_config.get("host"):
            raise ConfigValidationError(
                "database.host", db_config.get("host"), "Database host is required"
            )
        if not db_config.get("name"):
            raise ConfigValidationError(
                "database.name", db_config.get("name"), "Database name is required"
            )

        # Security validation
        security_config = self._config.get("security", {})
        if security_config.get("enable_authentication") and not security_config.get(
            "jwt_secret_key"
        ):
            raise ConfigValidationError(
                "security.jwt_secret_key",
                None,
                "JWT secret key is required when authentication is enabled",
            )

        # API validation
        api_config = self._config.get("api", {})
        if api_config.get("port", 0) <= 0 or api_config.get("port", 0) > 65535:
            raise ConfigValidationError(
                "api.port", api_config.get("port"), "Invalid port number"
            )

        # Performance validation
        performance_config = self._config.get("performance", {})
        if (
            performance_config.get("enable_profiling")
            and performance_config.get("profile_interval", 0) <= 0
        ):
            raise ConfigValidationError(
                "performance.profile_interval",
                performance_config.get("profile_interval"),
                "Profile interval must be positive",
            )

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key: Configuration key (e.g., "database.host")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self._config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def reload_config(self) -> None:
        """Reload configuration from files"""
        logger.info("Reloading configuration...")
        self._load_config()


# Global configuration instance
_config_manager = None


def get_config_manager(environment: str = None) -> ConfigManager:
    """Get or create global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(environment)
    return _config_manager


def reload_config() -> None:
    """Convenience function to reload configuration"""
    get_config_manager().reload_config()


# Example usage and testing
if __name__ == "__main__":
    # Test configuration loading
    config = get_config_manager("development")

    print("Database Host:", config.get("database.host"))
    print("API Port:", config.get("api.port"))
    print("Features:", config.get("features"))
    print("Environment:", config.environment)
