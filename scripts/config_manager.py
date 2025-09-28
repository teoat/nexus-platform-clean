#!/usr/bin/env python3
"""
NEXUS Platform - Configuration Management Script
Manages environment-specific configurations and secrets
"""

import argparse
import base64
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ConfigManager:
    """Configuration management for NEXUS Platform"""

    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.config_dir = Path("config")
        self.templates_dir = Path("config/templates")
        self.secrets_dir = Path("config/secrets")

        # Create directories if they don't exist
        self.config_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)
        self.secrets_dir.mkdir(exist_ok=True)

    def load_template(self, template_name: str) -> Dict[str, Any]:
        """Load configuration template"""
        template_file = self.templates_dir / f"{template_name}.json"
        if not template_file.exists():
            raise FileNotFoundError(f"Template not found: {template_file}")

        with open(template_file, "r") as f:
            return json.load(f)

    def generate_config(
        self, template_name: str, output_file: Optional[str] = None
    ) -> str:
        """Generate configuration from template"""
        template = self.load_template(template_name)

        # Replace environment variables
        config = self._replace_variables(template)

        # Set output file
        if not output_file:
            output_file = f"config/{self.environment}-{template_name}.json"

        # Write configuration
        output_path = Path(output_file)
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(config, f, indent=2)

        logger.info(f"Configuration generated: {output_path}")
        return str(output_path)

    def _replace_variables(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Replace environment variables in configuration"""
        if isinstance(config, dict):
            return {k: self._replace_variables(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._replace_variables(item) for item in config]
        elif (
            isinstance(config, str) and config.startswith("${") and config.endswith("}")
        ):
            var_name = config[2:-1]
            value = os.getenv(var_name)
            if value is None:
                logger.warning(f"Environment variable not set: {var_name}")
                return config
            return value
        else:
            return config

    def encrypt_secrets(
        self, input_file: str, output_file: Optional[str] = None
    ) -> str:
        """Encrypt secrets file"""
        if not output_file:
            output_file = f"config/secrets/{self.environment}-secrets.enc"

        # Use openssl for encryption
        key = os.getenv("CONFIG_ENCRYPTION_KEY")
        if not key:
            raise ValueError("CONFIG_ENCRYPTION_KEY environment variable not set")

        cmd = [
            "openssl",
            "enc",
            "-aes-256-cbc",
            "-salt",
            "-pbkdf2",
            "-in",
            input_file,
            "-out",
            output_file,
            "-k",
            key,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Encryption failed: {result.stderr}")

        logger.info(f"Secrets encrypted: {output_file}")
        return output_file

    def decrypt_secrets(
        self, input_file: str, output_file: Optional[str] = None
    ) -> str:
        """Decrypt secrets file"""
        if not output_file:
            output_file = f"config/secrets/{self.environment}-secrets.dec"

        key = os.getenv("CONFIG_ENCRYPTION_KEY")
        if not key:
            raise ValueError("CONFIG_ENCRYPTION_KEY environment variable not set")

        cmd = [
            "openssl",
            "enc",
            "-aes-256-cbc",
            "-d",
            "-pbkdf2",
            "-in",
            input_file,
            "-out",
            output_file,
            "-k",
            key,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Decryption failed: {result.stderr}")

        logger.info(f"Secrets decrypted: {output_file}")
        return output_file

    def create_kubernetes_secret(self, secret_name: str, data: Dict[str, str]) -> str:
        """Create Kubernetes secret manifest"""
        secret_data = {}
        for key, value in data.items():
            # Base64 encode the values
            secret_data[key] = base64.b64encode(value.encode()).decode()

        manifest = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": secret_name,
                "namespace": f"nexus-{self.environment}",
                "labels": {"app": "nexus-platform", "environment": self.environment},
            },
            "type": "Opaque",
            "data": secret_data,
        }

        output_file = f"k8s/secrets/{self.environment}-{secret_name}.yaml"
        Path(output_file).parent.mkdir(exist_ok=True)

        with open(output_file, "w") as f:
            import yaml

            yaml.dump(manifest, f, default_flow_style=False)

        logger.info(f"Kubernetes secret created: {output_file}")
        return output_file

    def validate_config(self, config_file: str) -> bool:
        """Validate configuration file"""
        try:
            with open(config_file, "r") as f:
                if config_file.endswith(".json"):
                    json.load(f)
                elif config_file.endswith((".yaml", ".yml")):
                    import yaml

                    yaml.safe_load(f)
                else:
                    raise ValueError("Unsupported file format")

            logger.info(f"Configuration validated: {config_file}")
            return True
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False

    def backup_config(
        self, source_dir: str = "config", backup_name: Optional[str] = None
    ) -> str:
        """Backup configuration directory"""
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"config_backup_{timestamp}"

        backup_file = f"backups/{backup_name}.tar.gz"

        # Create backup archive
        import tarfile

        with tarfile.open(backup_file, "w:gz") as tar:
            tar.add(source_dir, arcname="config")

        logger.info(f"Configuration backup created: {backup_file}")
        return backup_file

    def compare_configs(self, config1: str, config2: str) -> Dict[str, Any]:
        """Compare two configuration files"""

        def load_config(file_path: str) -> Dict:
            with open(file_path, "r") as f:
                if file_path.endswith(".json"):
                    return json.load(f)
                else:
                    import yaml

                    return yaml.safe_load(f)

        try:
            cfg1 = load_config(config1)
            cfg2 = load_config(config2)

            # Simple diff (can be enhanced)
            differences = {"added": [], "removed": [], "modified": []}

            # Compare keys
            keys1 = set(cfg1.keys())
            keys2 = set(cfg2.keys())

            differences["added"] = list(keys2 - keys1)
            differences["removed"] = list(keys1 - keys2)

            for key in keys1 & keys2:
                if cfg1[key] != cfg2[key]:
                    differences["modified"].append(key)

            return differences

        except Exception as e:
            logger.error(f"Config comparison failed: {e}")
            return {}


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="NEXUS Configuration Manager")
    parser.add_argument(
        "--environment",
        "-e",
        default="development",
        choices=["development", "staging", "production"],
        help="Target environment",
    )
    parser.add_argument(
        "--action",
        "-a",
        required=True,
        choices=[
            "generate",
            "encrypt",
            "decrypt",
            "k8s-secret",
            "validate",
            "backup",
            "compare",
        ],
        help="Action to perform",
    )

    # Action-specific arguments
    parser.add_argument("--template", help="Template name for generate action")
    parser.add_argument("--input", "-i", help="Input file")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--secret-name", help="Secret name for Kubernetes secret")
    parser.add_argument("--config1", help="First config file for comparison")
    parser.add_argument("--config2", help="Second config file for comparison")

    args = parser.parse_args()

    manager = ConfigManager(args.environment)

    try:
        if args.action == "generate":
            if not args.template:
                parser.error("--template is required for generate action")
            result = manager.generate_config(args.template, args.output)
            print(f"Configuration generated: {result}")

        elif args.action == "encrypt":
            if not args.input:
                parser.error("--input is required for encrypt action")
            result = manager.encrypt_secrets(args.input, args.output)
            print(f"Secrets encrypted: {result}")

        elif args.action == "decrypt":
            if not args.input:
                parser.error("--input is required for decrypt action")
            result = manager.decrypt_secrets(args.input, args.output)
            print(f"Secrets decrypted: {result}")

        elif args.action == "k8s-secret":
            if not args.secret_name or not args.input:
                parser.error(
                    "--secret-name and --input are required for k8s-secret action"
                )

            # Load data from input file
            with open(args.input, "r") as f:
                data = json.load(f)

            result = manager.create_kubernetes_secret(args.secret_name, data)
            print(f"Kubernetes secret created: {result}")

        elif args.action == "validate":
            if not args.input:
                parser.error("--input is required for validate action")
            valid = manager.validate_config(args.input)
            print(f"Configuration validation: {'PASS' if valid else 'FAIL'}")

        elif args.action == "backup":
            result = manager.backup_config(args.input or "config")
            print(f"Configuration backup created: {result}")

        elif args.action == "compare":
            if not args.config1 or not args.config2:
                parser.error("--config1 and --config2 are required for compare action")
            differences = manager.compare_configs(args.config1, args.config2)
            print("Configuration differences:")
            print(json.dumps(differences, indent=2))

    except Exception as e:
        logger.error(f"Action failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
