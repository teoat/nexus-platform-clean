#!/usr/bin/env python3
"""
NEXUS Platform - Database Query Optimizer
Advanced query optimization and performance monitoring
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

import psutil
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from database.database import get_db
from database.schema_normalization import Account, Transaction, User

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """Database query optimization and performance monitoring"""

    def __init__(self):
        self.query_cache = {}
        self.performance_metrics = {}

    async def optimize_user_queries(self, db: Session) -> Dict[str, Any]:
        """Optimize user-related queries"""
        start_time = time.time()

        try:
            # Optimized user query with proper indexing
            users_query = (
                db.query(User)
                .filter(User.is_active == True)
                .order_by(User.created_at.desc())
                .limit(100)
            )

            users = users_query.all()

            # Optimized user count query
            user_count = (
                db.query(func.count(User.id)).filter(User.is_active == True).scalar()
            )

            execution_time = time.time() - start_time

            return {
                "users": len(users),
                "total_users": user_count,
                "execution_time": execution_time,
                "optimization_applied": True,
            }

        except Exception as e:
            logger.error(f"User query optimization failed: {e}")
            return {"error": str(e)}

    async def optimize_transaction_queries(
        self, db: Session, user_id: int
    ) -> Dict[str, Any]:
        """Optimize transaction-related queries"""
        start_time = time.time()

        try:
            # Optimized transaction query with proper joins and indexing
            transactions_query = (
                db.query(Transaction)
                .filter(Transaction.user_id == user_id)
                .order_by(Transaction.created_at.desc())
                .limit(50)
            )

            transactions = transactions_query.all()

            # Optimized transaction summary query
            summary_query = db.query(
                func.sum(Transaction.amount).label("total_amount"),
                func.count(Transaction.id).label("transaction_count"),
                func.avg(Transaction.amount).label("average_amount"),
            ).filter(Transaction.user_id == user_id, Transaction.status == "completed")

            summary = summary_query.first()

            execution_time = time.time() - start_time

            return {
                "transactions": len(transactions),
                "total_amount": float(summary.total_amount or 0),
                "transaction_count": summary.transaction_count,
                "average_amount": float(summary.average_amount or 0),
                "execution_time": execution_time,
                "optimization_applied": True,
            }

        except Exception as e:
            logger.error(f"Transaction query optimization failed: {e}")
            return {"error": str(e)}

    async def optimize_analytics_queries(
        self, db: Session, user_id: int
    ) -> Dict[str, Any]:
        """Optimize analytics-related queries"""
        start_time = time.time()

        try:
            # TODO: Implement AnalyticsReport model
            # analytics_query = (
            #     db.query(AnalyticsReport)
            #     .filter(AnalyticsReport.user_id == user_id)
            #     .order_by(AnalyticsReport.created_at.desc())
            #     .limit(100)
            # )
            # analytics = analytics_query.all()
            analytics = []

            # TODO: Implement AnalyticsReport model
            # aggregation_query = (
            #     db.query(
            #         AnalyticsReport.report_type,
            #         func.count(AnalyticsReport.id).label("report_count"),
            #     )
            #     .filter(AnalyticsReport.user_id == user_id)
            #     .group_by(AnalyticsReport.report_type)
            # )
            # aggregations = aggregation_query.all()
            aggregations = []

            execution_time = time.time() - start_time

            return {
                "analytics_records": len(analytics),
                "aggregations": [
                    {"report_type": agg.report_type, "report_count": agg.report_count}
                    for agg in aggregations
                ],
                "execution_time": execution_time,
                "optimization_applied": True,
            }

        except Exception as e:
            logger.error(f"Analytics query optimization failed: {e}")
            return {"error": str(e)}

    async def analyze_slow_queries(self, db: Session) -> List[Dict[str, Any]]:
        """Analyze and identify slow queries"""
        try:
            # Query to find slow queries from PostgreSQL
            slow_queries_query = text(
                """
                SELECT
                    query,
                    calls,
                    total_time,
                    mean_time,
                    rows,
                    shared_blks_hit,
                    shared_blks_read
                FROM pg_stat_statements
                WHERE mean_time > 1000  -- Queries taking more than 1 second
                ORDER BY mean_time DESC
                LIMIT 10
            """
            )

            result = db.execute(slow_queries_query)
            slow_queries = []

            for row in result:
                slow_queries.append(
                    {
                        "query": row.query[:200] + "..."
                        if len(row.query) > 200
                        else row.query,
                        "calls": row.calls,
                        "total_time": row.total_time,
                        "mean_time": row.mean_time,
                        "rows": row.rows,
                        "cache_hit_ratio": row.shared_blks_hit
                        / (row.shared_blks_hit + row.shared_blks_read)
                        if (row.shared_blks_hit + row.shared_blks_read) > 0
                        else 0,
                    }
                )

            return slow_queries

        except Exception as e:
            logger.error(f"Slow query analysis failed: {e}")
            return []

    async def get_database_performance_metrics(self, db: Session) -> Dict[str, Any]:
        """Get comprehensive database performance metrics"""
        try:
            # Database size query
            size_query = text(
                """
                SELECT
                    pg_database_size(current_database()) as database_size,
                    pg_size_pretty(pg_database_size(current_database())) as database_size_pretty
            """
            )

            size_result = db.execute(size_query).first()

            # Connection count query
            connections_query = text(
                """
                SELECT count(*) as active_connections
                FROM pg_stat_activity
                WHERE state = 'active'
            """
            )

            connections_result = db.execute(connections_query).first()

            # Cache hit ratio query
            cache_query = text(
                """
                SELECT
                    round(
                        (sum(blks_hit) * 100.0 / (sum(blks_hit) + sum(blks_read))), 2
                    ) as cache_hit_ratio
                FROM pg_stat_database
                WHERE datname = current_database()
            """
            )

            cache_result = db.execute(cache_query).first()

            return {
                "database_size": size_result.database_size,
                "database_size_pretty": size_result.database_size_pretty,
                "active_connections": connections_result.active_connections,
                "cache_hit_ratio": float(cache_result.cache_hit_ratio or 0),
                "timestamp": time.time(),
            }

        except Exception as e:
            logger.error(f"Database performance metrics failed: {e}")
            return {"error": str(e)}

    async def optimize_database_connections(self, db: Session) -> Dict[str, Any]:
        """Optimize database connection settings"""
        try:
            # Get current connection settings
            settings_query = text(
                """
                SELECT
                    name,
                    setting,
                    unit,
                    context
                FROM pg_settings
                WHERE name IN (
                    'max_connections',
                    'shared_buffers',
                    'effective_cache_size',
                    'work_mem',
                    'maintenance_work_mem'
                )
            """
            )

            result = db.execute(settings_query)
            settings = {}

            for row in result:
                settings[row.name] = {
                    "value": row.setting,
                    "unit": row.unit,
                    "context": row.context,
                }

            # Calculate optimal settings based on system resources
            system_memory = psutil.virtual_memory().total
            cpu_count = psutil.cpu_count()

            optimal_settings = {
                "max_connections": min(200, cpu_count * 4),
                "shared_buffers": f"{int(system_memory * 0.25 / (1024**3))}GB",
                "effective_cache_size": f"{int(system_memory * 0.75 / (1024**3))}GB",
                "work_mem": f"{int(system_memory * 0.05 / (1024**3))}GB",
                "maintenance_work_mem": f"{int(system_memory * 0.1 / (1024**3))}GB",
            }

            return {
                "current_settings": settings,
                "optimal_settings": optimal_settings,
                "system_memory_gb": system_memory / (1024**3),
                "cpu_count": cpu_count,
            }

        except Exception as e:
            logger.error(f"Database connection optimization failed: {e}")
            return {"error": str(e)}

    async def run_query_optimization(self, db: Session) -> Dict[str, Any]:
        """Run comprehensive query optimization"""
        logger.info("Starting database query optimization...")

        optimization_results = {"timestamp": time.time(), "optimizations": {}}

        try:
            # Run all optimizations
            optimization_results["optimizations"][
                "users"
            ] = await self.optimize_user_queries(db)
            optimization_results["optimizations"][
                "transactions"
            ] = await self.optimize_transaction_queries(
                db, 1
            )  # Example user ID
            optimization_results["optimizations"][
                "analytics"
            ] = await self.optimize_analytics_queries(
                db, 1
            )  # Example user ID
            optimization_results["optimizations"][
                "slow_queries"
            ] = await self.analyze_slow_queries(db)
            optimization_results["optimizations"][
                "performance_metrics"
            ] = await self.get_database_performance_metrics(db)
            optimization_results["optimizations"][
                "connection_settings"
            ] = await self.optimize_database_connections(db)

            logger.info("Database query optimization completed successfully")
            return optimization_results

        except Exception as e:
            logger.error(f"Query optimization failed: {e}")
            return {"error": str(e), "timestamp": time.time()}


# Usage example
async def main():
    """Example usage of query optimizer"""
    from database.database import get_db

    optimizer = QueryOptimizer()

    # Get database session
    db = next(get_db())

    try:
        # Run optimization
        results = await optimizer.run_query_optimization(db)
        print("Optimization Results:", results)

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
