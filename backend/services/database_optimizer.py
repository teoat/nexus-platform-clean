#!/usr/bin/env python3
"""
NEXUS Platform - Database Optimization Service
Database indexing, query optimization, and performance monitoring
"""

import logging
import sqlite3
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """Service for database optimization and performance monitoring"""

    def __init__(self, db_path: str = "nexus.db"):
        self.db_path = db_path
        self.init_optimization()

    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_optimization(self):
        """Initialize database optimization settings"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Enable WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")

        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys=ON")

        # Set cache size (negative value means KB)
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache

        # Set synchronous mode for better performance
        cursor.execute("PRAGMA synchronous=NORMAL")

        # Set temp store to memory
        cursor.execute("PRAGMA temp_store=MEMORY")

        conn.commit()
        conn.close()
        logger.info("Database optimization settings applied")

    def create_indexes(self):
        """Create performance indexes"""
        conn = self.get_connection()
        cursor = conn.cursor()

        indexes = [
            # Users table indexes
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)",
            # Accounts table indexes
            "CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_accounts_type ON accounts(account_type)",
            "CREATE INDEX IF NOT EXISTS idx_accounts_balance ON accounts(balance)",
            # Transactions table indexes
            "CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_amount ON transactions(amount)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category)",
            # Notifications table indexes
            "CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_date ON notifications(created_at)",
            # Files table indexes
            "CREATE INDEX IF NOT EXISTS idx_files_user_id ON files(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_files_type ON files(file_type)",
            "CREATE INDEX IF NOT EXISTS idx_files_date ON files(created_at)",
            # MFA settings indexes
            "CREATE INDEX IF NOT EXISTS idx_mfa_user_id ON mfa_settings(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_mfa_enabled ON mfa_settings(is_enabled)",
            # MFA attempts indexes
            "CREATE INDEX IF NOT EXISTS idx_mfa_attempts_user_id ON mfa_attempts(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_mfa_attempts_type ON mfa_attempts(attempt_type)",
            "CREATE INDEX IF NOT EXISTS idx_mfa_attempts_success ON mfa_attempts(success)",
            "CREATE INDEX IF NOT EXISTS idx_mfa_attempts_date ON mfa_attempts(created_at)",
        ]

        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                logger.info(
                    f"Created index: {index_sql.split('idx_')[1].split(' ')[0]}"
                )
            except Exception as e:
                logger.error(f"Failed to create index: {e}")

        conn.commit()
        conn.close()
        logger.info("Database indexes created successfully")

    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get table sizes
        cursor.execute(
            """
            SELECT name, 
                   (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=m.name) as table_count,
                   (SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name LIKE '%' || m.name || '%') as index_count
            FROM sqlite_master m
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """
        )
        tables = cursor.fetchall()

        # Get database size
        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]
        db_size = page_count * page_size

        # Get cache hit ratio
        cursor.execute("PRAGMA cache_size")
        cache_size = cursor.fetchone()[0]

        conn.close()

        return {
            "database_size_bytes": db_size,
            "database_size_mb": round(db_size / (1024 * 1024), 2),
            "tables": [dict(table) for table in tables],
            "cache_size": cache_size,
            "timestamp": datetime.now().isoformat(),
        }

    def create_composite_indexes(self):
        """Create composite indexes for common query patterns"""
        conn = self.get_connection()
        cursor = conn.cursor()

        composite_indexes = [
            # User account queries
            "CREATE INDEX IF NOT EXISTS idx_accounts_user_type ON accounts(user_id, account_type)",
            # Transaction queries
            "CREATE INDEX IF NOT EXISTS idx_transactions_account_date ON transactions(account_id, created_at)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_type_date ON transactions(transaction_type, created_at)",
            # Notification queries
            "CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_user_type ON notifications(user_id, type)",
            # MFA attempt queries
            "CREATE INDEX IF NOT EXISTS idx_mfa_attempts_user_success ON mfa_attempts(user_id, success)",
            "CREATE INDEX IF NOT EXISTS idx_mfa_attempts_user_date ON mfa_attempts(user_id, created_at)",
        ]

        for index_sql in composite_indexes:
            try:
                cursor.execute(index_sql)
                logger.info(
                    f"Created composite index: {index_sql.split('idx_')[1].split(' ')[0]}"
                )
            except Exception as e:
                logger.error(f"Failed to create composite index: {e}")

        conn.commit()
        conn.close()
        logger.info("Composite indexes created successfully")

    def monitor_query_performance(
        self, query: str, params: tuple = ()
    ) -> Dict[str, Any]:
        """Monitor query performance with detailed metrics"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get query plan
        cursor.execute("EXPLAIN QUERY PLAN " + query, params)
        query_plan = cursor.fetchall()

        # Measure execution time
        start_time = time.time()
        cursor.execute(query, params)
        results = cursor.fetchall()
        execution_time = time.time() - start_time

        # Check if indexes are being used
        uses_index = any("INDEX" in str(step) for step in query_plan)

        # Get result count
        result_count = len(results)

        conn.close()

        return {
            "query": query,
            "execution_time_ms": round(execution_time * 1000, 2),
            "result_count": result_count,
            "uses_index": uses_index,
            "query_plan": [dict(row) for row in query_plan],
            "performance_rating": self._rate_performance(
                execution_time, uses_index, result_count
            ),
        }

    def _rate_performance(
        self, execution_time: float, uses_index: bool, result_count: int
    ) -> str:
        """Rate query performance"""
        if execution_time < 0.01:  # < 10ms
            return "excellent"
        elif execution_time < 0.1:  # < 100ms
            return "good"
        elif execution_time < 0.5:  # < 500ms
            return "fair"
        else:
            return "poor"

    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get database optimization recommendations"""
        recommendations = []

        # Check for missing indexes
        conn = self.get_connection()
        cursor = conn.cursor()

        # Check if common indexes exist
        cursor.execute(
            """
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name LIKE 'idx_%'
        """
        )
        existing_indexes = [row[0] for row in cursor.fetchall()]

        required_indexes = [
            "idx_users_username",
            "idx_users_email",
            "idx_accounts_user_id",
            "idx_transactions_account_id",
            "idx_transactions_date",
            "idx_notifications_user_id",
        ]

        missing_indexes = [
            idx for idx in required_indexes if idx not in existing_indexes
        ]

        if missing_indexes:
            recommendations.append(
                {
                    "type": "missing_indexes",
                    "priority": "high",
                    "description": "Missing critical indexes",
                    "details": missing_indexes,
                    "action": "Run create_indexes() method",
                }
            )

        # Check database size
        stats = self.get_database_stats()
        if stats["database_size_mb"] > 100:  # > 100MB
            recommendations.append(
                {
                    "type": "database_size",
                    "priority": "medium",
                    "description": "Database size is large",
                    "details": f"Current size: {stats['database_size_mb']}MB",
                    "action": "Consider archiving old data or running VACUUM",
                }
            )

        conn.close()

        return recommendations


# Example usage
if __name__ == "__main__":
    optimizer = DatabaseOptimizer()

    # Create indexes
    optimizer.create_indexes()
    optimizer.create_composite_indexes()

    # Get database stats
    stats = optimizer.get_database_stats()
    print(f"Database stats: {stats}")

    # Get optimization recommendations
    recommendations = optimizer.get_optimization_recommendations()
    print(f"Recommendations: {recommendations}")

    # Test query performance
    query = "SELECT * FROM accounts WHERE user_id = ?"
    performance = optimizer.monitor_query_performance(query, (1,))
    print(f"Query performance: {performance}")
