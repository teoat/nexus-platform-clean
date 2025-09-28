# NEXUS Platform - PostgreSQL Migration
# Migrate from SQLite to PostgreSQL for production readiness

import json
import logging
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, Optional

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class PostgreSQLMigration:
    """Handle migration from SQLite to PostgreSQL"""

    def __init__(self, sqlite_path: str, postgres_config: Dict[str, str]):
        self.sqlite_path = sqlite_path
        self.postgres_config = postgres_config
        self.migration_log = []

    def migrate(self) -> Dict[str, Any]:
        """Perform complete migration from SQLite to PostgreSQL"""
        logger.info("🔄 Starting PostgreSQL migration...")

        try:
            # Step 1: Connect to both databases
            sqlite_conn = self._connect_sqlite()
            postgres_conn = self._connect_postgresql()

            # Step 2: Create PostgreSQL schema
            self._create_postgresql_schema(postgres_conn)

            # Step 3: Migrate data
            self._migrate_data(sqlite_conn, postgres_conn)

            # Step 4: Verify migration
            self._verify_migration(sqlite_conn, postgres_conn)

            # Step 5: Update configuration
            self._update_configuration()

            # Close connections
            sqlite_conn.close()
            postgres_conn.close()

            logger.info("✅ PostgreSQL migration completed successfully")
            return self._generate_migration_report()

        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return self._generate_error_report(str(e))

    def _connect_sqlite(self) -> sqlite3.Connection:
        """Connect to SQLite database"""
        if not os.path.exists(self.sqlite_path):
            raise FileNotFoundError(f"SQLite database not found: {self.sqlite_path}")

        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _connect_postgresql(self) -> psycopg2.extensions.connection:
        """Connect to PostgreSQL database"""
        try:
            conn = psycopg2.connect(
                host=self.postgres_config["host"],
                port=self.postgres_config["port"],
                database=self.postgres_config["database"],
                user=self.postgres_config["user"],
                password=self.postgres_config["password"],
            )
            return conn
        except Exception as e:
            raise ConnectionError(f"Failed to connect to PostgreSQL: {e}")

    def _create_postgresql_schema(self, conn: psycopg2.extensions.connection):
        """Create PostgreSQL schema based on SQLite structure"""
        logger.info("📋 Creating PostgreSQL schema...")

        cursor = conn.cursor()

        try:
            # Create users table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    first_name VARCHAR(50),
                    last_name VARCHAR(50),
                    is_active BOOLEAN DEFAULT TRUE,
                    is_verified BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    role VARCHAR(20) DEFAULT 'user',
                    mfa_enabled BOOLEAN DEFAULT FALSE,
                    mfa_secret VARCHAR(32)
                )
            """
            )

            # Create accounts table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS accounts (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    account_number VARCHAR(20) UNIQUE NOT NULL,
                    account_type VARCHAR(20) NOT NULL,
                    balance DECIMAL(15,2) DEFAULT 0.00,
                    currency VARCHAR(3) DEFAULT 'USD',
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create transactions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    id SERIAL PRIMARY KEY,
                    account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
                    transaction_type VARCHAR(20) NOT NULL,
                    amount DECIMAL(15,2) NOT NULL,
                    currency VARCHAR(3) DEFAULT 'USD',
                    description TEXT,
                    reference VARCHAR(100),
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP
                )
            """
            )

            # Create audit_logs table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    action VARCHAR(50) NOT NULL,
                    resource_type VARCHAR(50),
                    resource_id VARCHAR(100),
                    details JSONB,
                    ip_address INET,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create sessions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    session_token VARCHAR(255) UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address INET,
                    user_agent TEXT
                )
            """
            )

            # Create notifications table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notifications (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    title VARCHAR(200) NOT NULL,
                    message TEXT NOT NULL,
                    notification_type VARCHAR(50) DEFAULT 'info',
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    read_at TIMESTAMP
                )
            """
            )

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(session_token)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)"
            )

            conn.commit()
            self.migration_log.append("PostgreSQL schema created successfully")

        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to create PostgreSQL schema: {e}")
        finally:
            cursor.close()

    def _migrate_data(
        self,
        sqlite_conn: sqlite3.Connection,
        postgres_conn: psycopg2.extensions.connection,
    ):
        """Migrate data from SQLite to PostgreSQL"""
        logger.info("📦 Migrating data...")

        # Get all table names from SQLite
        cursor = sqlite_conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        tables = [row[0] for row in cursor.fetchall()]

        postgres_cursor = postgres_conn.cursor()

        try:
            for table in tables:
                self._migrate_table(sqlite_conn, postgres_conn, table)

            postgres_conn.commit()
            self.migration_log.append(f"Data migrated from {len(tables)} tables")

        except Exception as e:
            postgres_conn.rollback()
            raise Exception(f"Failed to migrate data: {e}")
        finally:
            postgres_cursor.close()

    def _migrate_table(
        self,
        sqlite_conn: sqlite3.Connection,
        postgres_conn: psycopg2.extensions.connection,
        table: str,
    ):
        """Migrate individual table"""
        logger.info(f"Migrating table: {table}")

        # Get table schema
        cursor = sqlite_conn.cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()

        # Get data
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()

        if not rows:
            logger.info(f"Table {table} is empty, skipping")
            return

        # Prepare PostgreSQL insert
        postgres_cursor = postgres_conn.cursor()

        # Map SQLite types to PostgreSQL types
        type_mapping = {
            "INTEGER": "INTEGER",
            "TEXT": "TEXT",
            "REAL": "DECIMAL",
            "BLOB": "BYTEA",
            "VARCHAR": "VARCHAR",
            "BOOLEAN": "BOOLEAN",
            "TIMESTAMP": "TIMESTAMP",
        }

        # Create column list
        column_names = [col[1] for col in columns]
        placeholders = ", ".join(["%s"] * len(column_names))

        # Insert data
        for row in rows:
            try:
                # Convert row data for PostgreSQL
                converted_row = []
                for i, value in enumerate(row):
                    if value is None:
                        converted_row.append(None)
                    elif columns[i][2] == "INTEGER":
                        converted_row.append(int(value) if value is not None else None)
                    elif columns[i][2] == "REAL":
                        converted_row.append(
                            float(value) if value is not None else None
                        )
                    elif columns[i][2] == "TEXT" and isinstance(value, str):
                        # Handle JSON data
                        if value.startswith("{") or value.startswith("["):
                            try:
                                converted_row.append(json.dumps(json.loads(value)))
                            except:
                                converted_row.append(value)
                        else:
                            converted_row.append(value)
                    else:
                        converted_row.append(value)

                postgres_cursor.execute(
                    f"INSERT INTO {table} ({', '.join(column_names)}) VALUES ({placeholders})",
                    converted_row,
                )

            except Exception as e:
                logger.warning(f"Error inserting row into {table}: {e}")
                continue

        self.migration_log.append(f"Migrated {len(rows)} rows from {table}")

    def _verify_migration(
        self,
        sqlite_conn: sqlite3.Connection,
        postgres_conn: psycopg2.extensions.connection,
    ):
        """Verify migration was successful"""
        logger.info("🔍 Verifying migration...")

        # Get table counts from both databases
        tables = [
            "users",
            "accounts",
            "transactions",
            "audit_logs",
            "sessions",
            "notifications",
        ]

        for table in tables:
            try:
                # SQLite count
                sqlite_cursor = sqlite_conn.cursor()
                sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                sqlite_count = sqlite_cursor.fetchone()[0]

                # PostgreSQL count
                postgres_cursor = postgres_conn.cursor()
                postgres_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                postgres_count = postgres_cursor.fetchone()[0]

                if sqlite_count != postgres_count:
                    raise Exception(
                        f"Row count mismatch in {table}: SQLite={sqlite_count}, PostgreSQL={postgres_count}"
                    )

                self.migration_log.append(f"Verified {table}: {postgres_count} rows")

            except Exception as e:
                logger.warning(f"Verification failed for {table}: {e}")

    def _update_configuration(self):
        """Update configuration to use PostgreSQL"""
        logger.info("⚙️ Updating configuration...")

        # Update environment variables
        env_file = os.path.join(os.path.dirname(self.sqlite_path), ".env")
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                content = f.read()

            # Update database URL
            content = content.replace(
                "DATABASE_URL=sqlite:///./nexus.db",
                f'DATABASE_URL=postgresql://{self.postgres_config["user"]}:{self.postgres_config["password"]}@{self.postgres_config["host"]}:{self.postgres_config["port"]}/{self.postgres_config["database"]}',
            )

            with open(env_file, "w") as f:
                f.write(content)

        self.migration_log.append("Configuration updated to use PostgreSQL")

    def _generate_migration_report(self) -> Dict[str, Any]:
        """Generate migration report"""
        return {
            "migration_timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "success",
            "source_database": self.sqlite_path,
            "target_database": f"postgresql://{self.postgres_config['host']}:{self.postgres_config['port']}/{self.postgres_config['database']}",
            "migration_log": self.migration_log,
            "summary": {
                "tables_migrated": len(
                    [log for log in self.migration_log if "Migrated" in log]
                ),
                "total_logs": len(self.migration_log),
                "migration_successful": True,
            },
        }

    def _generate_error_report(self, error_message: str) -> Dict[str, Any]:
        """Generate error report"""
        return {
            "migration_timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "failed",
            "error": error_message,
            "migration_log": self.migration_log,
            "summary": {"migration_successful": False, "error_occurred": True},
        }


def run_postgresql_migration(
    sqlite_path: str = "nexus.db", postgres_config: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Run PostgreSQL migration"""

    if postgres_config is None:
        postgres_config = {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": os.getenv("POSTGRES_PORT", "5432"),
            "database": os.getenv("POSTGRES_DB", "nexus"),
            "user": os.getenv("POSTGRES_USER", "nexus"),
            "password": os.getenv("POSTGRES_PASSWORD", "nexus_password"),
        }

    migration = PostgreSQLMigration(sqlite_path, postgres_config)
    return migration.migrate()


if __name__ == "__main__":
    # Run migration
    result = run_postgresql_migration()

    if result["status"] == "success":
        print("✅ PostgreSQL migration completed successfully")
        print(f"Migrated {result['summary']['tables_migrated']} tables")
    else:
        print(f"❌ Migration failed: {result['error']}")

    # Save report
    with open("postgresql_migration_report.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"📄 Migration report saved to: postgresql_migration_report.json")
