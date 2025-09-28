#!/usr/bin/env python3
"""
NEXUS Production Database Setup
Comprehensive database setup and configuration
"""

import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path

import asyncpg
import redis
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NEXUSDatabaseSetup:
    """NEXUS Production Database Setup Manager"""

    def __init__(self, config_path: str = "config/database.yaml"):
        self.config_path = Path(config_path)
        self.config = {}
        self.db_connection = None
        self.redis_connection = None

    async def load_config(self):
        """Load database configuration"""
        try:
            with open(self.config_path, "r") as f:
                self.config = yaml.safe_load(f)
            logger.info("✅ Database configuration loaded")
        except Exception as e:
            logger.error(f"❌ Failed to load database config: {e}")
            raise

    async def setup_postgresql(self):
        """Setup PostgreSQL database"""
        logger.info("🐘 Setting up PostgreSQL database...")

        primary_config = self.config["primary"]

        # Parse environment variables
        host = os.getenv(
            "DB_HOST", primary_config["host"].replace("${DB_HOST:", "").replace("}", "")
        )
        port = int(
            os.getenv(
                "DB_PORT",
                primary_config["port"].replace("${DB_PORT:", "").replace("}", ""),
            )
        )
        username = os.getenv(
            "DB_USER",
            primary_config["username"].replace("${DB_USER:", "").replace("}", ""),
        )
        password = os.getenv(
            "DB_PASSWORD",
            primary_config["password"].replace("${DB_PASSWORD:", "").replace("}", ""),
        )
        db_name = os.getenv(
            "DB_NAME", primary_config["name"].replace("${DB_NAME:", "").replace("}", "")
        )

        try:
            # Connect to PostgreSQL
            self.db_connection = await asyncpg.connect(
                host=host,
                port=port,
                user=username,
                password=password,
                database="postgres",  # Connect to default database first
            )

            # Create database if it doesn't exist
            await self.db_connection.execute(f"CREATE DATABASE {db_name}")
            logger.info(f"✅ Database '{db_name}' created")

            # Close connection to default database
            await self.db_connection.close()

            # Connect to the new database
            self.db_connection = await asyncpg.connect(
                host=host, port=port, user=username, password=password, database=db_name
            )

            # Create tables
            await self.create_tables()

            # Create indexes
            await self.create_indexes()

            # Insert initial data
            await self.insert_initial_data()

            logger.info("✅ PostgreSQL database setup complete")

        except Exception as e:
            logger.error(f"❌ PostgreSQL setup failed: {e}")
            raise

    async def create_tables(self):
        """Create database tables"""
        logger.info("📋 Creating database tables...")

        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                is_active BOOLEAN DEFAULT true,
                is_admin BOOLEAN DEFAULT false,
                mfa_enabled BOOLEAN DEFAULT false,
                mfa_secret VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS user_sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                session_token VARCHAR(255) UNIQUE NOT NULL,
                ip_address INET,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT true
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS system_metrics (
                id SERIAL PRIMARY KEY,
                metric_name VARCHAR(100) NOT NULL,
                metric_value DECIMAL(15,4) NOT NULL,
                metric_unit VARCHAR(20),
                tags JSONB,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS security_events (
                id SERIAL PRIMARY KEY,
                event_type VARCHAR(50) NOT NULL,
                severity VARCHAR(20) NOT NULL,
                user_id INTEGER REFERENCES users(id),
                ip_address INET,
                user_agent TEXT,
                details JSONB,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                action VARCHAR(100) NOT NULL,
                resource_type VARCHAR(50),
                resource_id VARCHAR(100),
                old_values JSONB,
                new_values JSONB,
                ip_address INET,
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS system_configurations (
                id SERIAL PRIMARY KEY,
                config_key VARCHAR(100) UNIQUE NOT NULL,
                config_value JSONB NOT NULL,
                config_type VARCHAR(50) DEFAULT 'string',
                description TEXT,
                is_encrypted BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS feature_flags (
                id SERIAL PRIMARY KEY,
                flag_name VARCHAR(100) UNIQUE NOT NULL,
                is_enabled BOOLEAN DEFAULT false,
                description TEXT,
                target_users JSONB,
                target_percentage INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS api_keys (
                id SERIAL PRIMARY KEY,
                key_name VARCHAR(100) NOT NULL,
                key_hash VARCHAR(255) UNIQUE NOT NULL,
                user_id INTEGER REFERENCES users(id),
                permissions JSONB,
                last_used TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
        ]

        for table_sql in tables:
            await self.db_connection.execute(table_sql)

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
            INSERT INTO users (username, email, password_hash, first_name, last_name, is_admin, is_active)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (email) DO NOTHING
        """,
            "admin",
            "admin@nexus-platform.com",
            admin_password_hash,
            "System",
            "Administrator",
            True,
            True,
        )

        # Insert default system configurations
        default_configs = [
            ("system.version", "1.0.0", "string", "System version"),
            ("system.environment", "production", "string", "Environment"),
            ("security.mfa_required", "true", "boolean", "MFA requirement"),
            ("monitoring.enabled", "true", "boolean", "Monitoring enabled"),
            ("cache.redis_enabled", "true", "boolean", "Redis cache enabled"),
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
                INSERT INTO system_configurations (config_key, config_value, config_type, description)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (config_key) DO NOTHING
            """,
                key,
                value,
                config_type,
                description,
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
                INSERT INTO feature_flags (flag_name, is_enabled, description)
                VALUES ($1, $2, $3)
                ON CONFLICT (flag_name) DO NOTHING
            """,
                flag_name,
                is_enabled,
                description,
            )

        logger.info("✅ Initial data inserted")

    async def setup_redis(self):
        """Setup Redis cache"""
        logger.info("🔴 Setting up Redis cache...")

        redis_config = self.config["redis"]

        # Parse environment variables
        redis_host = os.getenv(
            "REDIS_HOST",
            redis_config["host"].replace("${REDIS_HOST:", "").replace("}", ""),
        )
        redis_port = int(
            os.getenv(
                "REDIS_PORT",
                redis_config["port"].replace("${REDIS_PORT:", "").replace("}", ""),
            )
        )
        redis_password = os.getenv(
            "REDIS_PASSWORD",
            redis_config["password"].replace("${REDIS_PASSWORD:", "").replace("}", ""),
        )

        try:
            self.redis_connection = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password if redis_password else None,
                db=redis_config["db"],
                decode_responses=True,
            )

            # Test connection
            await self.redis_connection.ping()

            # Set initial cache configurations
            await self.redis_connection.set("nexus:system:status", "active")
            await self.redis_connection.set(
                "nexus:system:startup_time", datetime.now().isoformat()
            )
            await self.redis_connection.set("nexus:cache:version", "1.0.0")

            logger.info("✅ Redis cache setup complete")

        except Exception as e:
            logger.error(f"❌ Redis setup failed: {e}")
            raise

    async def verify_setup(self):
        """Verify database setup"""
        logger.info("🔍 Verifying database setup...")

        # Test PostgreSQL connection
        result = await self.db_connection.fetchval("SELECT COUNT(*) FROM users")
        logger.info(f"✅ PostgreSQL: {result} users found")

        # Test Redis connection
        redis_status = await self.redis_connection.get("nexus:system:status")
        logger.info(f"✅ Redis: Status = {redis_status}")

        # Test table existence
        tables = await self.db_connection.fetch(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
        """
        )
        logger.info(f"✅ PostgreSQL: {len(tables)} tables created")

        logger.info("✅ Database setup verification complete")

    async def cleanup(self):
        """Cleanup connections"""
        if self.db_connection:
            await self.db_connection.close()
        if self.redis_connection:
            await self.redis_connection.close()

    async def run_setup(self):
        """Run complete database setup"""
        try:
            logger.info("🚀 Starting NEXUS Production Database Setup")
            logger.info("=" * 60)

            await self.load_config()
            await self.setup_postgresql()
            await self.setup_redis()
            await self.verify_setup()

            logger.info("\n" + "=" * 60)
            logger.info("🎉 NEXUS Production Database Setup Complete!")
            logger.info("=" * 60)
            logger.info("✅ PostgreSQL database configured")
            logger.info("✅ Redis cache configured")
            logger.info("✅ Tables and indexes created")
            logger.info("✅ Initial data inserted")
            logger.info("✅ System ready for production")

        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            raise
        finally:
            await self.cleanup()


async def main():
    """Main entry point"""
    setup = NEXUSDatabaseSetup()
    await setup.run_setup()


if __name__ == "__main__":
    asyncio.run(main())
