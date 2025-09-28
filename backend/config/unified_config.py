#!/usr/bin/env python3
"""
NEXUS Platform - Unified Configuration System
Centralized configuration management for all services
"""

import hashlib
import json
import logging
import os
import re
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigSource(Enum):
    """Configuration source enumeration"""

    ENVIRONMENT = "environment"
    FILE = "file"
    DATABASE = "database"
    CONSUL = "consul"
    ETCD = "etcd"
    VAULT = "vault"


class ConfigType(Enum):
    """Configuration type enumeration"""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


@dataclass
class ConfigValue:
    """Configuration value with metadata"""

    key: str
    value: Any
    config_type: ConfigType
    source: ConfigSource
    description: str = ""
    required: bool = False
    default_value: Any = None
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    sensitive: bool = False
    last_updated: datetime = field(default_factory=datetime.now)
    version: int = 1


@dataclass
class ServiceConfig:
    """Service-specific configuration"""

    service_name: str
    config_values: Dict[str, ConfigValue] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    environment: str = "development"
    version: str = "1.0.0"


class ConfigValidator:
    """Configuration validation utilities"""

    @staticmethod
    def validate_string(value: Any, rules: Dict[str, Any]) -> bool:
        """Validate string value"""
        if not isinstance(value, str):
            return False

        min_length = rules.get("min_length", 0)
        max_length = rules.get("max_length", float("inf"))
        pattern = rules.get("pattern")

        if len(value) < min_length or len(value) > max_length:
            return False

        if pattern and not re.match(pattern, value):
            return False

        return True

    @staticmethod
    def validate_integer(value: Any, rules: Dict[str, Any]) -> bool:
        """Validate integer value"""
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            return False

        min_value = rules.get("min_value", float("-inf"))
        max_value = rules.get("max_value", float("inf"))

        return min_value <= int_value <= max_value

    @staticmethod
    def validate_float(value: Any, rules: Dict[str, Any]) -> bool:
        """Validate float value"""
        try:
            float_value = float(value)
        except (ValueError, TypeError):
            return False

        min_value = rules.get("min_value", float("-inf"))
        max_value = rules.get("max_value", float("inf"))

        return min_value <= float_value <= max_value

    @staticmethod
    def validate_boolean(value: Any, rules: Dict[str, Any]) -> bool:
        """Validate boolean value"""
        if isinstance(value, bool):
            return True

        if isinstance(value, str):
            return value.lower() in ["true", "false", "1", "0", "yes", "no"]

        return False

    @staticmethod
    def validate_array(value: Any, rules: Dict[str, Any]) -> bool:
        """Validate array value"""
        if not isinstance(value, list):
            return False

        min_length = rules.get("min_length", 0)
        max_length = rules.get("max_length", float("inf"))
        item_type = rules.get("item_type")

        if len(value) < min_length or len(value) > max_length:
            return False

        if item_type:
            for item in value:
                if not isinstance(item, item_type):
                    return False

        return True

    @staticmethod
    def validate_object(value: Any, rules: Dict[str, Any]) -> bool:
        """Validate object value"""
        if not isinstance(value, dict):
            return False

        required_keys = rules.get("required_keys", [])
        for key in required_keys:
            if key not in value:
                return False

        return True


class UnifiedConfig:
    """Unified configuration management system"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.services: Dict[str, ServiceConfig] = {}
        self.global_config: Dict[str, ConfigValue] = {}
        self.config_sources: Dict[ConfigSource, Dict[str, Any]] = {}
        self.validators = ConfigValidator()
        self.lock = threading.RLock()
        self.watchers: List[callable] = []

        # Initialize default sources
        self._init_default_sources()

        # Load configurations
        self._load_configurations()

    def _init_default_sources(self):
        """Initialize default configuration sources"""
        # Environment variables
        self.config_sources[ConfigSource.ENVIRONMENT] = {
            "prefix": "NEXUS_",
            "case_sensitive": False,
        }

        # File system
        self.config_sources[ConfigSource.FILE] = {
            "config_dir": self.config_dir,
            "supported_formats": [".json", ".yaml", ".yml", ".env"],
        }

    def _load_configurations(self):
        """Load configurations from all sources"""
        try:
            # Load from environment
            self._load_from_environment()

            # Load from files
            self._load_from_files()

            logger.info("Configurations loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load configurations: {e}")

    def _load_from_environment(self):
        """Load configuration from environment variables"""
        prefix = self.config_sources[ConfigSource.ENVIRONMENT]["prefix"]

        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix) :].lower()

                # Determine type
                config_type = self._infer_type(value)

                # Create config value
                config_value = ConfigValue(
                    key=config_key,
                    value=self._convert_value(value, config_type),
                    config_type=config_type,
                    source=ConfigSource.ENVIRONMENT,
                )

                self.global_config[config_key] = config_value

    def _load_from_files(self):
        """Load configuration from files"""
        config_dir = self.config_sources[ConfigSource.FILE]["config_dir"]
        supported_formats = self.config_sources[ConfigSource.FILE]["supported_formats"]

        if not config_dir.exists():
            logger.warning(f"Config directory {config_dir} does not exist")
            return

        for file_path in config_dir.rglob("*"):
            if file_path.suffix in supported_formats:
                try:
                    self._load_config_file(file_path)
                except Exception as e:
                    logger.error(f"Failed to load config file {file_path}: {e}")

    def _load_config_file(self, file_path: Path):
        """Load configuration from a specific file"""
        with open(file_path, "r") as f:
            if file_path.suffix in [".yaml", ".yml"]:
                data = yaml.safe_load(f)
            elif file_path.suffix == ".json":
                data = json.load(f)
            elif file_path.suffix == ".env":
                data = self._parse_env_file(f)
            else:
                return

        # Process configuration data
        if isinstance(data, dict):
            for key, value in data.items():
                config_type = self._infer_type(value)
                config_value = ConfigValue(
                    key=key,
                    value=value,
                    config_type=config_type,
                    source=ConfigSource.FILE,
                )
                self.global_config[key] = config_value

    def _parse_env_file(self, file_content) -> Dict[str, str]:
        """Parse .env file content"""
        env_vars = {}
        for line in file_content:
            line = line.strip()
            if line and not line.startswith("#"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
        return env_vars

    def _infer_type(self, value: Any) -> ConfigType:
        """Infer configuration type from value"""
        if isinstance(value, bool):
            return ConfigType.BOOLEAN
        elif isinstance(value, int):
            return ConfigType.INTEGER
        elif isinstance(value, float):
            return ConfigType.FLOAT
        elif isinstance(value, list):
            return ConfigType.ARRAY
        elif isinstance(value, dict):
            return ConfigType.OBJECT
        else:
            return ConfigType.STRING

    def _convert_value(self, value: str, config_type: ConfigType) -> Any:
        """Convert string value to appropriate type"""
        if config_type == ConfigType.BOOLEAN:
            return value.lower() in ["true", "1", "yes", "on"]
        elif config_type == ConfigType.INTEGER:
            return int(value)
        elif config_type == ConfigType.FLOAT:
            return float(value)
        elif config_type == ConfigType.ARRAY:
            return json.loads(value) if value.startswith("[") else value.split(",")
        elif config_type == ConfigType.OBJECT:
            return json.loads(value) if value.startswith("{") else {}
        else:
            return value

    def get(self, key: str, default: Any = None, service: str = None) -> Any:
        """Get configuration value"""
        with self.lock:
            # Check service-specific config first
            if service and service in self.services:
                service_config = self.services[service]
                if key in service_config.config_values:
                    return service_config.config_values[key].value

            # Check global config
            if key in self.global_config:
                return self.global_config[key].value

            return default

    def get_string(self, key: str, default: str = "", service: str = None) -> str:
        """Get string configuration value"""
        value = self.get(key, default, service)
        return str(value) if value is not None else default

    def get_int(self, key: str, default: int = 0, service: str = None) -> int:
        """Get integer configuration value"""
        value = self.get(key, default, service)
        try:
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            return default

    def get_float(self, key: str, default: float = 0.0, service: str = None) -> float:
        """Get float configuration value"""
        value = self.get(key, default, service)
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default

    def get_bool(self, key: str, default: bool = False, service: str = None) -> bool:
        """Get boolean configuration value"""
        value = self.get(key, default, service)
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            return value.lower() in ["true", "1", "yes", "on"]
        else:
            return bool(value) if value is not None else default

    def get_list(self, key: str, default: List = None, service: str = None) -> List:
        """Get list configuration value"""
        value = self.get(key, default, service)
        if isinstance(value, list):
            return value
        elif isinstance(value, str):
            try:
                return json.loads(value) if value.startswith("[") else value.split(",")
            except:
                return value.split(",")
        else:
            return default or []

    def get_dict(self, key: str, default: Dict = None, service: str = None) -> Dict:
        """Get dictionary configuration value"""
        value = self.get(key, default, service)
        if isinstance(value, dict):
            return value
        elif isinstance(value, str):
            try:
                return json.loads(value) if value.startswith("{") else {}
            except:
                return {}
        else:
            return default or {}

    def set(
        self,
        key: str,
        value: Any,
        service: str = None,
        source: ConfigSource = ConfigSource.ENVIRONMENT,
    ):
        """Set configuration value"""
        with self.lock:
            config_type = self._infer_type(value)
            config_value = ConfigValue(
                key=key, value=value, config_type=config_type, source=source
            )

            if service:
                if service not in self.services:
                    self.services[service] = ServiceConfig(service_name=service)
                self.services[service].config_values[key] = config_value
            else:
                self.global_config[key] = config_value

            # Notify watchers
            self._notify_watchers(key, value, service)

    def register_service(
        self, service_name: str, config_values: Dict[str, ConfigValue] = None
    ):
        """Register a service with its configuration"""
        with self.lock:
            if service_name not in self.services:
                self.services[service_name] = ServiceConfig(service_name=service_name)

            if config_values:
                self.services[service_name].config_values.update(config_values)

    def validate_config(self, service: str = None) -> List[str]:
        """Validate configuration and return errors"""
        errors = []

        with self.lock:
            config_values = self.global_config.copy()
            if service and service in self.services:
                config_values.update(self.services[service].config_values)

            for key, config_value in config_values.items():
                if config_value.required and config_value.value is None:
                    errors.append(f"Required configuration '{key}' is missing")
                    continue

                if config_value.validation_rules:
                    if not self._validate_config_value(config_value):
                        errors.append(f"Configuration '{key}' validation failed")

        return errors

    def _validate_config_value(self, config_value: ConfigValue) -> bool:
        """Validate a single configuration value"""
        validator_map = {
            ConfigType.STRING: self.validators.validate_string,
            ConfigType.INTEGER: self.validators.validate_integer,
            ConfigType.FLOAT: self.validators.validate_float,
            ConfigType.BOOLEAN: self.validators.validate_boolean,
            ConfigType.ARRAY: self.validators.validate_array,
            ConfigType.OBJECT: self.validators.validate_object,
        }

        validator = validator_map.get(config_value.config_type)
        if validator:
            return validator(config_value.value, config_value.validation_rules)

        return True

    def add_watcher(self, watcher: callable):
        """Add configuration change watcher"""
        self.watchers.append(watcher)

    def remove_watcher(self, watcher: callable):
        """Remove configuration change watcher"""
        if watcher in self.watchers:
            self.watchers.remove(watcher)

    def _notify_watchers(self, key: str, value: Any, service: str = None):
        """Notify watchers of configuration changes"""
        for watcher in self.watchers:
            try:
                watcher(key, value, service)
            except Exception as e:
                logger.error(f"Error in configuration watcher: {e}")

    def export_config(self, service: str = None, format: str = "json") -> str:
        """Export configuration to string"""
        with self.lock:
            if service and service in self.services:
                config_data = {
                    key: value.value
                    for key, value in self.services[service].config_values.items()
                }
            else:
                config_data = {
                    key: value.value for key, value in self.global_config.items()
                }

            if format == "json":
                return json.dumps(config_data, indent=2)
            elif format == "yaml":
                return yaml.dump(config_data, default_flow_style=False)
            else:
                return str(config_data)

    def import_config(
        self, config_data: str, service: str = None, format: str = "json"
    ):
        """Import configuration from string"""
        try:
            if format == "json":
                data = json.loads(config_data)
            elif format == "yaml":
                data = yaml.safe_load(config_data)
            else:
                return False

            for key, value in data.items():
                self.set(key, value, service)

            return True
        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            return False

    def get_service_config(self, service_name: str) -> Optional[ServiceConfig]:
        """Get service configuration"""
        return self.services.get(service_name)

    def list_services(self) -> List[str]:
        """List all registered services"""
        return list(self.services.keys())

    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        with self.lock:
            return {
                "total_services": len(self.services),
                "global_config_count": len(self.global_config),
                "services": {
                    name: {
                        "config_count": len(service.config_values),
                        "environment": service.environment,
                        "version": service.version,
                    }
                    for name, service in self.services.items()
                },
            }


# Global configuration instance
config = UnifiedConfig()


# Helper functions
def get_config(key: str, default: Any = None, service: str = None) -> Any:
    """Helper function to get configuration"""
    return config.get(key, default, service)


def set_config(key: str, value: Any, service: str = None):
    """Helper function to set configuration"""
    config.set(key, value, service)


def get_service_config(service_name: str) -> Optional[ServiceConfig]:
    """Helper function to get service configuration"""
    return config.get_service_config(service_name)


if __name__ == "__main__":
    # Example usage
    config = UnifiedConfig()

    # Set some global configurations
    config.set("database_url", "postgresql://localhost:5432/nexus")
    config.set("redis_url", "redis://localhost:6379")
    config.set("api_port", 8000)
    config.set("debug", True)

    # Register a service
    config.register_service("auth-service")
    config.set("jwt_secret", "your-secret-key", service="auth-service")
    config.set("token_expiry", 3600, service="auth-service")

    # Get configurations
    print(f"Database URL: {config.get('database_url')}")
    print(f"API Port: {config.get_int('api_port')}")
    print(f"Debug Mode: {config.get_bool('debug')}")
    print(f"JWT Secret: {config.get('jwt_secret', service='auth-service')}")

    # Export configuration
    exported = config.export_config(format="json")
    print(f"Exported config: {exported}")

    # Get summary
    summary = config.get_config_summary()
    print(f"Config summary: {summary}")
