# Consolidated file from startup_checks.py
# Generated on 2025-09-24T15:09:04.067249

# === startup_checks.py ===
#!/usr/bin/env python3
"""
NEXUS Platform - Startup Security Checks
Performs security validation on application startup
"""

import logging
import os
import sys

from nexus_backend.security.security_validator import security_validator

logger = logging.getLogger(__name__)


def perform_startup_security_checks() -> bool:
    """Perform security checks on startup"""
    logger.info("Performing startup security checks...")

    try:
        # Validate environment configuration
        validation_result = security_validator.validate_environment()

        if not validation_result["valid"]:
            logger.error("Security validation failed:")
            for error in validation_result["errors"]:
                logger.error(f"  - {error}")

            # In production, fail startup if security validation fails
            if os.getenv("ENVIRONMENT") == "production":
                logger.error(
                    "Production environment security validation failed. Exiting."
                )
                sys.exit(1)
            else:
                logger.warning(
                    "Development environment security validation failed. Continuing with warnings."
                )

        # Log warnings
        for warning in validation_result["warnings"]:
            logger.warning(f"Security warning: {warning}")

        # Check for hardcoded secrets
        hardcoded_secrets = security_validator.check_hardcoded_secrets()
        if hardcoded_secrets:
            logger.warning("Potential hardcoded secrets detected. Please review:")
            for secret in hardcoded_secrets:
                logger.warning(f"  - {secret}")

        logger.info("Startup security checks completed")
        return validation_result["valid"]

    except Exception as e:
        logger.error(f"Failed to perform startup security checks: {e}")
        return False


def generate_development_keys():
    """Generate secure keys for development environment"""
    if os.getenv("ENVIRONMENT") == "development":
        logger.info("Generating secure keys for development...")
        keys = security_validator.generate_secure_keys()

        if keys:
            logger.info("Generated secure keys. Please update your .env file with:")
            for key, value in keys.items():
                logger.info(f"{key.upper()}={value}")
        else:
            logger.error("Failed to generate secure keys")


if __name__ == "__main__":
    # Run security checks
    perform_startup_security_checks()

    # Generate development keys if needed
    generate_development_keys()


# === startup_checks.py ===
#!/usr/bin/env python3
"""
NEXUS Platform - Startup Security Checks
Performs security validation on application startup
"""

import logging
import os
import sys

from nexus_backend.security.security_validator import security_validator

logger = logging.getLogger(__name__)


def perform_startup_security_checks() -> bool:
    """Perform security checks on startup"""
    logger.info("Performing startup security checks...")

    try:
        # Validate environment configuration
        validation_result = security_validator.validate_environment()

        if not validation_result["valid"]:
            logger.error("Security validation failed:")
            for error in validation_result["errors"]:
                logger.error(f"  - {error}")

            # In production, fail startup if security validation fails
            if os.getenv("ENVIRONMENT") == "production":
                logger.error(
                    "Production environment security validation failed. Exiting."
                )
                sys.exit(1)
            else:
                logger.warning(
                    "Development environment security validation failed. Continuing with warnings."
                )

        # Log warnings
        for warning in validation_result["warnings"]:
            logger.warning(f"Security warning: {warning}")

        # Check for hardcoded secrets
        hardcoded_secrets = security_validator.check_hardcoded_secrets()
        if hardcoded_secrets:
            logger.warning("Potential hardcoded secrets detected. Please review:")
            for secret in hardcoded_secrets:
                logger.warning(f"  - {secret}")

        logger.info("Startup security checks completed")
        return validation_result["valid"]

    except Exception as e:
        logger.error(f"Failed to perform startup security checks: {e}")
        return False


def generate_development_keys():
    """Generate secure keys for development environment"""
    if os.getenv("ENVIRONMENT") == "development":
        logger.info("Generating secure keys for development...")
        keys = security_validator.generate_secure_keys()

        if keys:
            logger.info("Generated secure keys. Please update your .env file with:")
            for key, value in keys.items():
                logger.info(f"{key.upper()}={value}")
        else:
            logger.error("Failed to generate secure keys")


if __name__ == "__main__":
    # Run security checks
    perform_startup_security_checks()

    # Generate development keys if needed
    generate_development_keys()
