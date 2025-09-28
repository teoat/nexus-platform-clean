#!/usr/bin/env python3
"""
NEXUS Configuration Service
Unified configuration system
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)


class NEXUSConfigurationService:
    """NEXUS Configuration Service"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.configs = {}
        self.is_active = False

    async def initialize(self):
        """Initialize configuration service"""
        logger.info("Initializing NEXUS Configuration Service")
        self.is_active = True

        # Load all configuration files
        await self.load_all_configs()

        logger.info("✅ NEXUS Configuration Service initialized")

    async def load_all_configs(self):
        """Load all configuration files"""
        config_files = [
            "system.yaml",
            "monitoring.yaml",
            "caching.yaml",
            "security.yaml",
            "database.yaml",
        ]

        for config_file in config_files:
            config_path = self.config_dir / config_file
            if config_path.exists():
                await self.load_config(config_file)
            else:
                logger.warning(f"Configuration file not found: {config_file}")

    async def load_config(self, config_name: str):
        """Load a specific configuration file"""
        config_path = self.config_dir / config_name

        try:
            if config_path.suffix == ".yaml" or config_path.suffix == ".yml":
                with open(config_path, "r") as f:
                    config_data = yaml.safe_load(f)
            elif config_path.suffix == ".json":
                with open(config_path, "r") as f:
                    config_data = json.load(f)
            else:
                logger.error(f"Unsupported config file format: {config_path.suffix}")
                return

            self.configs[config_name] = config_data
            logger.info(f"Loaded configuration: {config_name}")

        except Exception as e:
            logger.error(f"Error loading config {config_name}: {e}")

    async def get_config(self, config_name: str, key: str = None) -> Any:
        """Get configuration value"""
        if config_name not in self.configs:
            return None

        config_data = self.configs[config_name]

        if key is None:
            return config_data

        # Support dot notation for nested keys
        keys = key.split(".")
        value = config_data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None

        return value

    async def set_config(self, config_name: str, key: str, value: Any):
        """Set configuration value"""
        if config_name not in self.configs:
            self.configs[config_name] = {}

        # Support dot notation for nested keys
        keys = key.split(".")
        config_data = self.configs[config_name]

        for k in keys[:-1]:
            if k not in config_data:
                config_data[k] = {}
            config_data = config_data[k]

        config_data[keys[-1]] = value
        logger.info(f"Set config {config_name}.{key} = {value}")

    async def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "is_active": self.is_active,
            "loaded_configs": list(self.configs.keys()),
            "config_count": len(self.configs),
            "timestamp": datetime.now().isoformat(),
        }

    async def shutdown(self):
        """Shutdown configuration service"""
        logger.info("Shutting down NEXUS Configuration Service")
        self.is_active = False


# Global service instance
configuration_service = NEXUSConfigurationService()


async def main():
    """Main entry point"""
    await configuration_service.initialize()

    # Keep running
    try:
        while configuration_service.is_active:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await configuration_service.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
