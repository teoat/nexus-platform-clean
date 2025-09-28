#!/usr/bin/env python3
"""
NEXUS SQLite Database Setup
Simplified database setup using SQLite for development
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path

import aiosqlite
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NEXUSSQLiteSetup:
    """NEXUS SQLite Database Setup Manager"""

    def __init__(self, db_path: str = "nexus_platform.db"):
        self.db_path = Path(db_path)
        self.db_connection = None

    async def initialize(self):
        """Initialize SQLite database"""
        logger.info("🗄️ Initializing NEXUS SQLite Database...")

        try:
            self.db_connection = await aiosqlite.connect(self.db_path)
            await self.create_tables()
            await self.insert_initial_data()
            await self.create_indexes()

            logger.info("✅ NEXUS SQLite Database initialized successfully")

        except Exception as e:
            logger.error(f"❌ SQLite database initialization failed: {e}")
            raise

    async def create_tables(self):
        """Create database tables"""
        logger.info("📋 Creating database tables...")

        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                is_active BOOLEAN DEFAULT 1,
                is_admin BOOLEAN DEFAULT 0,
                mfa_enabled BOOLEAN DEFAULT 0,
                mfa_secret TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                session_token TEXT UNIQUE NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT,
                tags TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                user_id INTEGER REFERENCES users(id),
                ip_address TEXT,
                user_agent TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                action TEXT NOT NULL,
                resource_type TEXT,
                resource_id TEXT,
                old_values TEXT,
                new_values TEXT,
                ip_address TEXT,
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS system_configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT UNIQUE NOT NULL,
                config_value TEXT NOT NULL,
                config_type TEXT DEFAULT 'string',
                description TEXT,
                is_encrypted BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS feature_flags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flag_name TEXT UNIQUE NOT NULL,
                is_enabled BOOLEAN DEFAULT 0,
                description TEXT,
                target_users TEXT,
                target_percentage INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_name TEXT NOT NULL,
                key_hash TEXT UNIQUE NOT NULL,
                user_id INTEGER REFERENCES users(id),
                permissions TEXT,
                last_used TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
        ]

        for table_sql in tables:
            await self.db_connection.execute(table_sql)

        await self.db_connection.commit()
        logger.info("✅ Database tables created")

    async def create_indexes(self):
        """Create database indexes for performance"""
        logger.info("🔍 Creating database indexes...")

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token)",
            "CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions(expires_at)",
            "CREATE INDEX IF NOT EXISTS idx_system_metrics_name ON system_metrics(metric_name)",
            "CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_security_events_type ON security_events(event_type)",
            "CREATE INDEX IF NOT EXISTS idx_security_events_timestamp ON security_events(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action)",
            "CREATE INDEX IF NOT EXISTS idx_configurations_key ON system_configurations(config_key)",
            "CREATE INDEX IF NOT EXISTS idx_feature_flags_name ON feature_flags(flag_name)",
            "CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash)",
            "CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id)",
        ]

        for index_sql in indexes:
            await self.db_connection.execute(index_sql)

        await self.db_connection.commit()
        logger.info("✅ Database indexes created")

    async def insert_initial_data(self):
        """Insert initial data"""
        logger.info("📊 Inserting initial data...")

        # Insert default admin user
        admin_password_hash = (
            "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/9Qz8K2"  # 'admin123'
        )
        await self.db_connection.execute(
            """
            INSERT OR IGNORE INTO users (username, email, password_hash, first_name, last_name, is_admin, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "admin",
                "admin@nexus-platform.com",
                admin_password_hash,
                "System",
                "Administrator",
                1,
                1,
            ),
        )

        # Insert default system configurations
        default_configs = [
            ("system.version", "1.0.0", "string", "System version"),
            ("system.environment", "production", "string", "Environment"),
            ("security.mfa_required", "true", "boolean", "MFA requirement"),
            ("monitoring.enabled", "true", "boolean", "Monitoring enabled"),
            ("cache.redis_enabled", "false", "boolean", "Redis cache enabled"),
            ("api.rate_limit_default", "100", "integer", "Default API rate limit"),
            (
                "security.session_timeout",
                "28800",
                "integer",
                "Session timeout in seconds",
            ),
            (
                "monitoring.metrics_retention_days",
                "90",
                "integer",
                "Metrics retention period",
            ),
        ]

        for key, value, config_type, description in default_configs:
            await self.db_connection.execute(
                """
                INSERT OR IGNORE INTO system_configurations (config_key, config_value, config_type, description)
                VALUES (?, ?, ?, ?)
            """,
                (key, value, config_type, description),
            )

        # Insert default feature flags
        feature_flags = [
            ("performance_monitoring", True, "Performance monitoring feature"),
            ("security_monitoring", True, "Security monitoring feature"),
            ("ai_insights", True, "AI insights feature"),
            ("advanced_analytics", False, "Advanced analytics feature"),
            ("real_time_notifications", True, "Real-time notifications"),
            ("dark_mode", False, "Dark mode UI theme"),
        ]

        for flag_name, is_enabled, description in feature_flags:
            await self.db_connection.execute(
                """
                INSERT OR IGNORE INTO feature_flags (flag_name, is_enabled, description)
                VALUES (?, ?, ?)
            """,
                (flag_name, is_enabled, description),
            )

        await self.db_connection.commit()
        logger.info("✅ Initial data inserted")

    async def verify_setup(self):
        """Verify database setup"""
        logger.info("🔍 Verifying database setup...")

        # Test database connection
        cursor = await self.db_connection.execute("SELECT COUNT(*) FROM users")
        result = await cursor.fetchone()
        logger.info(f"✅ SQLite: {result[0]} users found")

        # Test table existence
        cursor = await self.db_connection.execute(
            """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """
        )
        tables = await cursor.fetchall()
        logger.info(f"✅ SQLite: {len(tables)} tables created")

        logger.info("✅ Database setup verification complete")

    async def cleanup(self):
        """Cleanup database connection"""
        if self.db_connection:
            await self.db_connection.close()

    async def run_setup(self):
        """Run complete database setup"""
        try:
            logger.info("🚀 Starting NEXUS SQLite Database Setup")
            logger.info("=" * 60)

            await self.initialize()
            await self.verify_setup()

            logger.info("\n" + "=" * 60)
            logger.info("🎉 NEXUS SQLite Database Setup Complete!")
            logger.info("=" * 60)
            logger.info("✅ SQLite database configured")
            logger.info("✅ Tables and indexes created")
            logger.info("✅ Initial data inserted")
            logger.info("✅ System ready for development")

        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            raise
        finally:
            await self.cleanup()


async def main():
    """Main entry point"""
    setup = NEXUSSQLiteSetup()
    await setup.run_setup()


if __name__ == "__main__":
    asyncio.run(main())
