#!/usr/bin/env python3
"""
NEXUS Platform - Database Migration Runner
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import asyncpg
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """Database migration runner"""

    def __init__(self, config_path: str = "config/database.yaml"):
        self.config_path = config_path
        self.migrations_dir = Path(__file__).parent
        self.connection = None

    async def load_config(self) -> Dict[str, Any]:
        """Load database configuration"""
        try:
            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            # Use environment variables as fallback
            return {
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", "5432")),
                "database": os.getenv("DB_NAME", "nexus"),
                "user": os.getenv("DB_USER", "nexus"),
                "password": os.getenv("DB_PASSWORD", "nexus123"),
            }

    async def connect(self):
        """Connect to database"""
        config = await self.load_config()
        self.connection = await asyncpg.connect(
            host=config["host"],
            port=config["port"],
            database=config["database"],
            user=config["user"],
            password=config["password"],
        )
        logger.info("Connected to database")

    async def disconnect(self):
        """Disconnect from database"""
        if self.connection:
            await self.connection.close()
            logger.info("Disconnected from database")

    async def create_migrations_table(self):
        """Create migrations tracking table"""
        await self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                version VARCHAR(50) UNIQUE NOT NULL,
                description TEXT,
                applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                checksum VARCHAR(64)
            )
        """
        )
        logger.info("Created migrations table")

    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations"""
        try:
            rows = await self.connection.fetch(
                "SELECT version FROM schema_migrations ORDER BY version"
            )
            return [row["version"] for row in rows]
        except:
            return []

    async def get_pending_migrations(self) -> List[Path]:
        """Get list of pending migrations"""
        applied = await self.get_applied_migrations()
        pending = []

        for migration_file in sorted(self.migrations_dir.glob("*.sql")):
            version = migration_file.stem
            if version not in applied:
                pending.append(migration_file)

        return pending

    async def run_migration(self, migration_file: Path) -> bool:
        """Run a single migration"""
        try:
            logger.info(f"Running migration: {migration_file.name}")

            # Read migration file
            with open(migration_file, "r") as f:
                sql = f.read()

            # Calculate checksum
            import hashlib

            checksum = hashlib.md5(sql.encode()).hexdigest()

            # Run migration in transaction
            async with self.connection.transaction():
                await self.connection.execute(sql)

                # Record migration
                await self.connection.execute(
                    """
                    INSERT INTO schema_migrations (version, description, checksum)
                    VALUES ($1, $2, $3)
                """,
                    migration_file.stem,
                    f"Migration {migration_file.name}",
                    checksum,
                )

            logger.info(f"Successfully applied migration: {migration_file.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to apply migration {migration_file.name}: {e}")
            return False

    async def migrate(self, target_version: str = None) -> bool:
        """Run all pending migrations"""
        try:
            await self.connect()
            await self.create_migrations_table()

            pending = await self.get_pending_migrations()

            if not pending:
                logger.info("No pending migrations")
                return True

            logger.info(f"Found {len(pending)} pending migrations")

            success_count = 0
            for migration_file in pending:
                if await self.run_migration(migration_file):
                    success_count += 1
                else:
                    logger.error(f"Migration failed: {migration_file.name}")
                    break

            if success_count == len(pending):
                logger.info(f"Successfully applied {success_count} migrations")
                return True
            else:
                logger.error(f"Applied {success_count}/{len(pending)} migrations")
                return False

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
        finally:
            await self.disconnect()

    async def rollback(self, target_version: str) -> bool:
        """Rollback to target version"""
        try:
            await self.connect()

            # Get migrations to rollback
            applied = await self.get_applied_migrations()
            target_index = (
                applied.index(target_version) if target_version in applied else -1
            )

            if target_index == -1:
                logger.error(
                    f"Target version {target_version} not found in applied migrations"
                )
                return False

            # Rollback migrations (in reverse order)
            to_rollback = applied[target_index + 1 :]
            to_rollback.reverse()

            logger.info(
                f"Rolling back {len(to_rollback)} migrations to version {target_version}"
            )

            for version in to_rollback:
                # Find rollback file
                rollback_file = self.migrations_dir / f"{version}_rollback.sql"
                if rollback_file.exists():
                    logger.info(f"Rolling back migration: {version}")

                    with open(rollback_file, "r") as f:
                        sql = f.read()

                    async with self.connection.transaction():
                        await self.connection.execute(sql)
                        await self.connection.execute(
                            "DELETE FROM schema_migrations WHERE version = $1", version
                        )

                    logger.info(f"Successfully rolled back migration: {version}")
                else:
                    logger.warning(f"No rollback file found for version: {version}")

            logger.info(f"Successfully rolled back to version {target_version}")
            return True

        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
        finally:
            await self.disconnect()

    async def status(self) -> Dict[str, Any]:
        """Get migration status"""
        try:
            await self.connect()
            await self.create_migrations_table()

            applied = await self.get_applied_migrations()
            pending = await self.get_pending_migrations()

            return {
                "applied_migrations": applied,
                "pending_migrations": [m.stem for m in pending],
                "total_applied": len(applied),
                "total_pending": len(pending),
                "current_version": applied[-1] if applied else None,
            }

        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {"error": str(e)}
        finally:
            await self.disconnect()


async def main():
    """Main function"""
    migrator = DatabaseMigrator()

    if len(sys.argv) < 2:
        print("Usage: python migrate.py [migrate|rollback|status] [target_version]")
        sys.exit(1)

    command = sys.argv[1]
    target_version = sys.argv[2] if len(sys.argv) > 2 else None

    if command == "migrate":
        success = await migrator.migrate(target_version)
        sys.exit(0 if success else 1)
    elif command == "rollback":
        if not target_version:
            print("Target version required for rollback")
            sys.exit(1)
        success = await migrator.rollback(target_version)
        sys.exit(0 if success else 1)
    elif command == "status":
        status = await migrator.status()
        print(f"Migration Status: {status}")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
