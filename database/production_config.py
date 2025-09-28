#!/usr/bin/env python3
"""
NEXUS Platform - Production Database Configuration
Production-ready database setup with security, performance, and monitoring
"""

import logging
import os

from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


class ProductionDatabaseConfig:
    """Production database configuration manager"""

    def __init__(self):
        self.config = self._load_config()
        self.engine = None

    def _load_config(self) -> Dict[str, Any]:
        """Load production database configuration"""
        return {
            # Database connection
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "database": os.getenv("DB_NAME", "nexus_prod"),
            "username": os.getenv("DB_USER", "nexus_prod"),
            "password": os.getenv("DB_PASSWORD"),
            # Connection pooling
            "pool_size": int(os.getenv("DB_POOL_SIZE", "20")),
            "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "30")),
            "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
            "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "3600")),
            "pool_pre_ping": True,
            # Performance settings
            "echo": os.getenv("DB_ECHO", "false").lower() == "true",
            "echo_pool": os.getenv("DB_ECHO_POOL", "false").lower() == "true",
            # Security settings
            "ssl_mode": os.getenv("DB_SSL_MODE", "require"),
            "ssl_cert": os.getenv("DB_SSL_CERT"),
            "ssl_key": os.getenv("DB_SSL_KEY"),
            "ssl_rootcert": os.getenv("DB_SSL_ROOTCERT"),
            # Monitoring
            "slow_query_threshold": int(os.getenv("DB_SLOW_QUERY_THRESHOLD", "1000")),
            "connection_monitoring": os.getenv(
                "DB_CONNECTION_MONITORING", "true"
            ).lower()
            == "true",
        }

    def create_engine(self) -> Engine:
        """Create production database engine"""
        try:
            # Build connection string
            connection_string = self._build_connection_string()

            # Create engine with production settings
            self.engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=self.config["pool_size"],
                max_overflow=self.config["max_overflow"],
                pool_timeout=self.config["pool_timeout"],
                pool_recycle=self.config["pool_recycle"],
                pool_pre_ping=self.config["pool_pre_ping"],
                echo=self.config["echo"],
                echo_pool=self.config["echo_pool"],
                connect_args=self._get_connect_args(),
            )

            logger.info("Production database engine created successfully")
            return self.engine

        except Exception as e:
            logger.error(f"Failed to create production database engine: {e}")
            raise

    def _build_connection_string(self) -> str:
        """Build database connection string"""
        if not self.config["password"]:
            raise ValueError("Database password is required for production")

        # Base connection string
        connection_string = (
            f"postgresql://{self.config['username']}:{self.config['password']}"
            f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
        )

        return connection_string

    def _get_connect_args(self) -> Dict[str, Any]:
        """Get connection arguments for SSL and other settings"""
        connect_args = {}

        # SSL configuration
        if self.config["ssl_mode"] != "disable":
            connect_args["sslmode"] = self.config["ssl_mode"]

            if self.config["ssl_cert"]:
                connect_args["sslcert"] = self.config["ssl_cert"]
            if self.config["ssl_key"]:
                connect_args["sslkey"] = self.config["ssl_key"]
            if self.config["ssl_rootcert"]:
                connect_args["sslrootcert"] = self.config["ssl_rootcert"]

        return connect_args

    def setup_production_database(self) -> bool:
        """Set up production database with optimal settings"""
        try:
            if not self.engine:
                self.engine = self.create_engine()

            with self.engine.connect() as conn:
                # Set up production database settings
                self._configure_database_settings(conn)
                self._create_indexes(conn)
                self._set_up_monitoring(conn)
                self._configure_security(conn)

            logger.info("Production database setup completed successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to setup production database: {e}")
            return False

    def _configure_database_settings(self, conn):
        """Configure database settings for production"""
        settings = [
            # Performance settings
            "SET shared_buffers = '256MB'",
            "SET effective_cache_size = '1GB'",
            "SET maintenance_work_mem = '64MB'",
            "SET checkpoint_completion_target = 0.9",
            "SET wal_buffers = '16MB'",
            "SET default_statistics_target = 100",
            # Connection settings
            "SET max_connections = 200",
            "SET shared_preload_libraries = 'pg_stat_statements'",
            # Logging settings
            "SET log_statement = 'mod'",
            "SET log_min_duration_statement = 1000",
            "SET log_checkpoints = on",
            "SET log_connections = on",
            "SET log_disconnections = on",
            # Security settings
            "SET ssl = on",
            "SET password_encryption = 'scram-sha-256'",
        ]

        for setting in settings:
            try:
                conn.execute(text(setting))
            except SQLAlchemyError as e:
                logger.warning(f"Failed to set database setting '{setting}': {e}")

    def _create_indexes(self, conn):
        """Create production indexes for performance"""
        indexes = [
            # User indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email_active ON users(email, is_active)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_username_active ON users(username, is_active)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_role_active ON users(role, is_active)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_last_login ON users(last_login)",
            # Session indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_sessions_user_active ON user_sessions(user_id, is_active)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_sessions_expires ON user_sessions(expires_at)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token)",
            # Transaction indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_account_date ON transactions(account_id, transaction_date)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_type_status ON transactions(type, status)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_amount ON transactions(amount)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_risk_score ON transactions(risk_score)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_fraud_score ON transactions(fraud_score)",
            # Account indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_accounts_number_active ON accounts(account_number, is_active)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_accounts_type_status ON accounts(account_type, status)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_accounts_risk_level ON accounts(risk_level)",
            # Audit log indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_action ON audit_logs(action)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(created_at)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_resource ON audit_logs(resource_type, resource_id)",
            # Performance metrics indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_performance_metrics_name ON performance_metrics(metric_name)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_performance_metrics_service ON performance_metrics(service_name)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(timestamp)",
        ]

        for index_sql in indexes:
            try:
                conn.execute(text(index_sql))
                logger.info(
                    f"Created index: {index_sql.split('idx_')[1].split(' ')[0]}"
                )
            except SQLAlchemyError as e:
                logger.warning(f"Failed to create index: {e}")

    def _set_up_monitoring(self, conn):
        """Set up database monitoring"""
        try:
            # Enable pg_stat_statements extension
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_stat_statements"))

            # Create monitoring views
            monitoring_views = [
                """
                CREATE OR REPLACE VIEW db_performance_stats AS
                SELECT
                    query,
                    calls,
                    total_time,
                    mean_time,
                    stddev_time,
                    rows,
                    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
                FROM pg_stat_statements
                ORDER BY total_time DESC
                LIMIT 20
                """,
                """
                CREATE OR REPLACE VIEW db_connection_stats AS
                SELECT
                    state,
                    count(*) as connection_count,
                    max(now() - state_change) as max_idle_time
                FROM pg_stat_activity
                WHERE state IS NOT NULL
                GROUP BY state
                ORDER BY connection_count DESC
                """,
                """
                CREATE OR REPLACE VIEW db_table_stats AS
                SELECT
                    schemaname,
                    tablename,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes,
                    n_live_tup as live_tuples,
                    n_dead_tup as dead_tuples,
                    last_vacuum,
                    last_autovacuum,
                    last_analyze,
                    last_autoanalyze
                FROM pg_stat_user_tables
                ORDER BY n_live_tup DESC
                """,
            ]

            for view_sql in monitoring_views:
                conn.execute(text(view_sql))

            logger.info("Database monitoring setup completed")

        except SQLAlchemyError as e:
            logger.warning(f"Failed to setup database monitoring: {e}")

    def _configure_security(self, conn):
        """Configure database security settings"""
        try:
            # Create production user with limited privileges
            security_commands = [
                # Create read-only user for monitoring
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'nexus_monitor') THEN
                        CREATE ROLE nexus_monitor WITH LOGIN PASSWORD 'monitor_password';
                    END IF;
                END
                $$;
                """,
                # Grant monitoring privileges
                "GRANT CONNECT ON DATABASE nexus_prod TO nexus_monitor",
                "GRANT USAGE ON SCHEMA public TO nexus_monitor",
                "GRANT SELECT ON ALL TABLES IN SCHEMA public TO nexus_monitor",
                "GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO nexus_monitor",
                # Set up row level security (if needed)
                "ALTER TABLE users ENABLE ROW LEVEL SECURITY",
                "ALTER TABLE transactions ENABLE ROW LEVEL SECURITY",
                "ALTER TABLE accounts ENABLE ROW LEVEL SECURITY",
            ]

            for command in security_commands:
                try:
                    conn.execute(text(command))
                except SQLAlchemyError as e:
                    logger.warning(f"Failed to execute security command: {e}")

            logger.info("Database security configuration completed")

        except SQLAlchemyError as e:
            logger.warning(f"Failed to configure database security: {e}")


# Global production database config instance
production_db_config = ProductionDatabaseConfig()


def setup_production_database() -> bool:
    """Set up production database"""
    return production_db_config.setup_production_database()
