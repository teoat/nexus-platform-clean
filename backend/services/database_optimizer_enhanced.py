#!/usr/bin/env python3
"""
Enhanced Database Optimizer Service
Advanced database optimization with connection pooling, query optimization, and performance monitoring for PostgreSQL
"""

import asyncio
import json
import logging
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import aiomysql
import aioredis
import asyncpg
import psutil
from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from database.database import get_db
from database.query_optimizer import QueryOptimizer

logger = logging.getLogger(__name__)


class DatabaseType(Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"


class OptimizationType(Enum):
    CONNECTION_POOLING = "connection_pooling"
    QUERY_OPTIMIZATION = "query_optimization"
    INDEX_OPTIMIZATION = "index_optimization"
    CACHE_OPTIMIZATION = "cache_optimization"
    SCHEMA_OPTIMIZATION = "schema_optimization"


@dataclass
class DatabaseMetrics:
    """Database performance metrics"""

    connections_active: int
    connections_idle: int
    connections_total: int
    query_count: int
    slow_queries: int
    cache_hit_ratio: float
    avg_query_time: float
    memory_usage: int
    disk_usage: int
    timestamp: datetime


@dataclass
class OptimizationResult:
    """Result of an optimization operation"""

    optimization_type: OptimizationType
    success: bool
    improvements: Dict[str, Any]
    recommendations: List[str]
    execution_time: float
    timestamp: datetime


class EnhancedDatabaseOptimizer:
    """Enhanced database optimization service with connection pooling and advanced features"""

    def __init__(self):
        self.db_type = DatabaseType.POSTGRESQL  # Default to PostgreSQL
        self.connection_pools = {}
        self.performance_history: List[DatabaseMetrics] = []
        self.optimization_results: List[OptimizationResult] = []
        self.query_optimizer = QueryOptimizer()

        # Optimization configuration
        self.config = {
            "pool_size": 20,
            "max_overflow": 30,
            "pool_timeout": 30,
            "pool_recycle": 3600,
            "echo": False,
            "slow_query_threshold": 1000,  # ms
            "optimization_interval": 300,  # 5 minutes
            "metrics_retention_days": 7,
        }

    async def initialize(self):
        """Initialize database optimizer"""
        logger.info("Initializing enhanced database optimizer...")

        # Setup connection pooling
        await self._setup_connection_pooling()

        # Start background optimization tasks
        asyncio.create_task(self._background_optimization())
        asyncio.create_task(self._performance_monitoring())

        logger.info("Enhanced database optimizer initialized")

    async def _setup_connection_pooling(self):
        """Setup optimized connection pooling"""
        try:
            # Get database URL from environment
            database_url = self._get_database_url()

            if not database_url:
                logger.warning("No database URL configured")
                return

            # Create optimized SQLAlchemy engine
            engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=self.config["pool_size"],
                max_overflow=self.config["max_overflow"],
                pool_timeout=self.config["pool_timeout"],
                pool_recycle=self.config["pool_recycle"],
                echo=self.config["echo"],
                pool_pre_ping=True,  # Test connections before use
                pool_use_lifo=True,  # Use LIFO for better performance
            )

            # Create session factory
            self.session_factory = sessionmaker(bind=engine)

            # Store connection pool reference
            self.connection_pools["main"] = engine.pool

            logger.info(
                f"Connection pooling configured: pool_size={self.config['pool_size']}, max_overflow={self.config['max_overflow']}"
            )

        except Exception as e:
            logger.error(f"Failed to setup connection pooling: {e}")

    def _get_database_url(self) -> Optional[str]:
        """Get database URL from configuration"""
        # Try environment variables first
        url = os.getenv("DATABASE_URL")
        if url:
            return url

        # Try individual components
        db_type = os.getenv("DB_TYPE", "postgresql")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        name = os.getenv("DB_NAME", "nexus")
        user = os.getenv("DB_USER", "nexus")
        password = os.getenv("DB_PASSWORD", "")

        if db_type == "postgresql":
            return f"postgresql://{user}:{password}@{host}:{port}/{name}"
        elif db_type == "mysql":
            return f"mysql://{user}:{password}@{host}:{port}/{name}"
        elif db_type == "sqlite":
            return f"sqlite:///{name}.db"

        return None

    async def optimize_database_performance(self) -> Dict[str, Any]:
        """Run comprehensive database optimization"""
        logger.info("Starting comprehensive database optimization...")

        start_time = datetime.now()
        results = {
            "timestamp": start_time.isoformat(),
            "optimizations": {},
            "overall_improvement": {},
            "recommendations": [],
        }

        try:
            # Run different types of optimizations
            optimizations = [
                self._optimize_connection_pooling,
                self._optimize_query_performance,
                self._optimize_indexes,
                self._optimize_caching,
                self._optimize_schema,
            ]

            for optimization_func in optimizations:
                try:
                    opt_result = await optimization_func()
                    results["optimizations"][optimization_func.__name__] = opt_result

                    # Store optimization result
                    self.optimization_results.append(
                        OptimizationResult(
                            optimization_type=OptimizationType(
                                optimization_func.__name__.replace("_optimize_", "")
                            ),
                            success=opt_result.get("success", False),
                            improvements=opt_result.get("improvements", {}),
                            recommendations=opt_result.get("recommendations", []),
                            execution_time=opt_result.get("execution_time", 0),
                            timestamp=datetime.now(),
                        )
                    )

                except Exception as e:
                    logger.error(
                        f"Optimization {optimization_func.__name__} failed: {e}"
                    )
                    results["optimizations"][optimization_func.__name__] = {
                        "error": str(e)
                    }

            # Calculate overall improvement
            results["overall_improvement"] = self._calculate_overall_improvement(
                results["optimizations"]
            )

            # Generate recommendations
            results["recommendations"] = self._generate_optimization_recommendations(
                results["optimizations"]
            )

            execution_time = (datetime.now() - start_time).total_seconds()
            results["total_execution_time"] = execution_time

            logger.info(
                f"Database optimization completed in {execution_time:.2f} seconds"
            )
            return results

        except Exception as e:
            logger.error(f"Database optimization failed: {e}")
            return {"error": str(e), "timestamp": start_time.isoformat()}

    async def _optimize_connection_pooling(self) -> Dict[str, Any]:
        """Optimize database connection pooling"""
        start_time = datetime.now()

        try:
            db = next(get_db())

            # Get current connection statistics
            if self.db_type == DatabaseType.POSTGRESQL:
                conn_stats_query = text(
                    """
                    SELECT
                        count(*) as total_connections,
                        count(*) filter (where state = 'active') as active_connections,
                        count(*) filter (where state = 'idle') as idle_connections
                    FROM pg_stat_activity
                    WHERE datname = current_database()
                """
                )

                result = db.execute(conn_stats_query).first()

                current_stats = {
                    "total_connections": result.total_connections,
                    "active_connections": result.active_connections,
                    "idle_connections": result.idle_connections,
                }

            # Calculate optimal pool settings
            system_memory = psutil.virtual_memory().total
            cpu_count = psutil.cpu_count()

            optimal_settings = {
                "pool_size": min(50, max(10, cpu_count * 2)),
                "max_overflow": min(100, max(20, cpu_count * 4)),
                "pool_timeout": 30,
                "pool_recycle": 3600,
            }

            # Apply optimizations if needed
            improvements = {}
            recommendations = []

            if (
                current_stats["active_connections"]
                > optimal_settings["pool_size"] * 1.5
            ):
                recommendations.append(
                    "Consider increasing pool_size for high connection demand"
                )
                improvements["connection_pooling"] = "high_demand_detected"

            if current_stats["idle_connections"] > optimal_settings["pool_size"]:
                recommendations.append(
                    "High number of idle connections - consider connection pooling optimization"
                )
                improvements["idle_connections"] = current_stats["idle_connections"]

            execution_time = (datetime.now() - start_time).total_seconds()

            return {
                "success": True,
                "current_stats": current_stats,
                "optimal_settings": optimal_settings,
                "improvements": improvements,
                "recommendations": recommendations,
                "execution_time": execution_time,
            }

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return {"success": False, "error": str(e), "execution_time": execution_time}

    async def _optimize_query_performance(self) -> Dict[str, Any]:
        """Optimize query performance"""
        start_time = datetime.now()

        try:
            db = next(get_db())

            # Run query optimization
            query_results = await self.query_optimizer.run_query_optimization(db)

            # Analyze slow queries
            slow_queries = await self.query_optimizer.analyze_slow_queries(db)

            improvements = {}
            recommendations = []

            if slow_queries:
                improvements["slow_queries_found"] = len(slow_queries)
                recommendations.append(
                    f"Found {len(slow_queries)} slow queries requiring optimization"
                )

                # Analyze query patterns
                high_impact_queries = [q for q in slow_queries if q["mean_time"] > 5000]
                if high_impact_queries:
                    recommendations.append(
                        f"{len(high_impact_queries)} queries with mean execution time > 5 seconds"
                    )

            # Check cache hit ratio
            perf_metrics = await self.query_optimizer.get_database_performance_metrics(
                db
            )
            cache_hit_ratio = perf_metrics.get("cache_hit_ratio", 0)

            if cache_hit_ratio < 0.95:
                recommendations.append(f"Cache hit ratio: {cache_hit_ratio:.2f}")
            else:
                improvements["good_cache_ratio"] = True

            execution_time = (datetime.now() - start_time).total_seconds()

            return {
                "success": True,
                "query_optimization_results": query_results,
                "slow_queries": slow_queries,
                "cache_hit_ratio": cache_hit_ratio,
                "improvements": improvements,
                "recommendations": recommendations,
                "execution_time": execution_time,
            }

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return {"success": False, "error": str(e), "execution_time": execution_time}

    async def _optimize_indexes(self) -> Dict[str, Any]:
        """Optimize database indexes"""
        start_time = datetime.now()

        try:
            db = next(get_db())

            improvements = {}
            recommendations = []

            if self.db_type == DatabaseType.POSTGRESQL:
                # Check for unused indexes
                unused_indexes_query = text(
                    """
                    SELECT
                        schemaname,
                        tablename,
                        indexname,
                        idx_scan as scans
                    FROM pg_stat_user_indexes
                    WHERE idx_scan = 0
                    AND schemaname NOT IN ('pg_catalog', 'information_schema')
                    ORDER BY pg_relation_size(indexrelid) DESC
                """
                )

                unused_result = db.execute(unused_indexes_query)
                unused_indexes = [row for row in unused_result]

                if unused_indexes:
                    improvements["unused_indexes"] = len(unused_indexes)
                    recommendations.append(
                        f"Found {len(unused_indexes)} potentially unused indexes"
                    )

                # Check for missing indexes on foreign keys
                missing_fk_indexes_query = text(
                    """
                    SELECT
                        tc.table_name,
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                    WHERE constraint_type = 'FOREIGN KEY'
                    AND NOT EXISTS (
                        SELECT 1 FROM pg_indexes
                        WHERE tablename = tc.table_name
                        AND indexdef LIKE '%' || kcu.column_name || '%'
                    )
                """
                )

                missing_fk_result = db.execute(missing_fk_indexes_query)
                missing_fk_indexes = [row for row in missing_fk_result]

                if missing_fk_indexes:
                    improvements["missing_fk_indexes"] = len(missing_fk_indexes)
                    recommendations.append(
                        f"Found {len(missing_fk_indexes)} foreign keys without indexes"
                    )

            execution_time = (datetime.now() - start_time).total_seconds()

            return {
                "success": True,
                "unused_indexes": len(unused_indexes)
                if "unused_indexes" in locals()
                else 0,
                "missing_fk_indexes": len(missing_fk_indexes)
                if "missing_fk_indexes" in locals()
                else 0,
                "improvements": improvements,
                "recommendations": recommendations,
                "execution_time": execution_time,
            }

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return {"success": False, "error": str(e), "execution_time": execution_time}

    async def _optimize_caching(self) -> Dict[str, Any]:
        """Optimize database caching"""
        start_time = datetime.now()

        try:
            improvements = {}
            recommendations = []

            # Check Redis cache if available
            try:
                import redis.asyncio as redis

                redis_client = redis.from_url(
                    "redis://localhost:6379", decode_responses=True
                )
                await redis_client.ping()

                # Get Redis stats
                info = await redis_client.info()
                cache_keys = await redis_client.dbsize()
                memory_usage = info.get("used_memory", 0)

                improvements["redis_connected"] = True
                improvements["cache_keys"] = cache_keys
                improvements["memory_usage"] = memory_usage

                # Check if cache is being utilized effectively
                if cache_keys < 100:
                    recommendations.append(
                        "Low cache utilization - consider preloading frequently accessed data"
                    )

                await redis_client.close()

            except Exception as e:
                recommendations.append("Redis cache not available or not optimized")

            execution_time = (datetime.now() - start_time).total_seconds()

            return {
                "success": True,
                "cache_type": "redis",
                "improvements": improvements,
                "recommendations": recommendations,
                "execution_time": execution_time,
            }

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return {"success": False, "error": str(e), "execution_time": execution_time}

    async def _optimize_schema(self) -> Dict[str, Any]:
        """Optimize database schema"""
        start_time = datetime.now()

        try:
            db = next(get_db())

            improvements = {}
            recommendations = []

            if self.db_type == DatabaseType.POSTGRESQL:
                # Check table bloat
                bloat_query = text(
                    """
                    SELECT
                        schemaname,
                        tablename,
                        n_dead_tup,
                        n_live_tup,
                        CASE WHEN n_live_tup > 0 THEN round((n_dead_tup::float / n_live_tup::float) * 100, 2) ELSE 0 END as bloat_ratio
                    FROM pg_stat_user_tables
                    WHERE n_dead_tup > 1000
                    ORDER BY n_dead_tup DESC
                    LIMIT 10
                """
                )

                bloat_result = db.execute(bloat_query)
                bloated_tables = [row for row in bloat_result if row.bloat_ratio > 20]

                if bloated_tables:
                    improvements["bloated_tables"] = len(bloated_tables)
                    recommendations.append(
                        f"Found {len(bloated_tables)} tables with high bloat (>20%) - consider VACUUM"
                    )

                # Check for tables without primary keys
                no_pk_query = text(
                    """
                    SELECT
                        schemaname,
                        tablename
                    FROM pg_tables t
                    WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                    AND NOT EXISTS (
                        SELECT 1 FROM pg_constraint c
                        WHERE c.conrelid = (t.schemaname || '.' || t.tablename)::regclass
                        AND c.contype = 'p'
                    )
                """
                )

                no_pk_result = db.execute(no_pk_query)
                tables_without_pk = [row for row in no_pk_result]

                if tables_without_pk:
                    improvements["tables_without_pk"] = len(tables_without_pk)
                    recommendations.append(
                        f"Found {len(tables_without_pk)} tables without primary keys"
                    )

            execution_time = (datetime.now() - start_time).total_seconds()

            return {
                "success": True,
                "bloated_tables": len(bloated_tables)
                if "bloated_tables" in locals()
                else 0,
                "tables_without_pk": len(tables_without_pk)
                if "tables_without_pk" in locals()
                else 0,
                "improvements": improvements,
                "recommendations": recommendations,
                "execution_time": execution_time,
            }

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return {"success": False, "error": str(e), "execution_time": execution_time}

    def _calculate_overall_improvement(
        self, optimizations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate overall improvement from all optimizations"""
        total_improvements = 0
        total_recommendations = 0

        for opt_name, opt_result in optimizations.items():
            if isinstance(opt_result, dict) and opt_result.get("success"):
                total_improvements += len(opt_result.get("improvements", {}))
                total_recommendations += len(opt_result.get("recommendations", []))

        return {
            "total_optimizations_run": len(optimizations),
            "successful_optimizations": sum(
                1
                for opt in optimizations.values()
                if isinstance(opt, dict) and opt.get("success")
            ),
            "total_improvements": total_improvements,
            "total_recommendations": total_recommendations,
            "optimization_success_rate": sum(
                1
                for opt in optimizations.values()
                if isinstance(opt, dict) and opt.get("success")
            )
            / len(optimizations)
            if optimizations
            else 0,
        }

    def _generate_optimization_recommendations(
        self, optimizations: Dict[str, Any]
    ) -> List[str]:
        """Generate overall recommendations from optimization results"""
        recommendations = []

        # Collect all recommendations
        for opt_result in optimizations.values():
            if isinstance(opt_result, dict) and "recommendations" in opt_result:
                recommendations.extend(opt_result["recommendations"])

        # Prioritize critical recommendations
        critical_keywords = ["critical", "high", "error", "failed", "missing"]
        prioritized_recommendations = []

        for rec in recommendations:
            if any(keyword in rec.lower() for keyword in critical_keywords):
                prioritized_recommendations.insert(0, f"CRITICAL: {rec}")
            else:
                prioritized_recommendations.append(rec)

        return prioritized_recommendations[:10]  # Top 10 recommendations

    async def get_database_metrics(self) -> DatabaseMetrics:
        """Get current database performance metrics"""
        try:
            db = next(get_db())

            # Get connection stats
            if self.db_type == DatabaseType.POSTGRESQL:
                conn_query = text(
                    """
                    SELECT
                        count(*) as total,
                        count(*) filter (where state = 'active') as active,
                        count(*) filter (where state = 'idle') as idle
                    FROM pg_stat_activity
                    WHERE datname = current_database()
                """
                )

                conn_result = db.execute(conn_query).first()

                # Get query performance stats
                perf_query = text(
                    """
                    SELECT
                        sum(calls) as query_count,
                        avg(mean_time) as avg_query_time
                    FROM pg_stat_statements
                    WHERE calls > 0
                """
                )

                perf_result = db.execute(perf_query).first()

                # Get slow query count
                slow_query = text(
                    f"""
                    SELECT count(*) as slow_count
                    FROM pg_stat_statements
                    WHERE mean_time > {self.config['slow_query_threshold']}
                """
                )

                slow_result = db.execute(slow_query).first()

                # Get cache hit ratio
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

            metrics = DatabaseMetrics(
                connections_active=conn_result.active,
                connections_idle=conn_result.idle,
                connections_total=conn_result.total,
                query_count=perf_result.query_count or 0,
                slow_queries=slow_result.slow_count or 0,
                cache_hit_ratio=float(cache_result.cache_hit_ratio or 0),
                avg_query_time=float(perf_result.avg_query_time or 0),
                memory_usage=psutil.virtual_memory().used,
                disk_usage=psutil.disk_usage("/").used,
                timestamp=datetime.now(),
            )

            # Store in history
            self.performance_history.append(metrics)

            # Keep only recent history
            cutoff = datetime.now() - timedelta(
                days=self.config["metrics_retention_days"]
            )
            self.performance_history = [
                m for m in self.performance_history if m.timestamp > cutoff
            ]

            return metrics

        except Exception as e:
            logger.error(f"Failed to get database metrics: {e}")
            return DatabaseMetrics(0, 0, 0, 0, 0, 0.0, 0.0, 0, 0, datetime.now())

    async def _background_optimization(self):
        """Background optimization task"""
        while True:
            try:
                await asyncio.sleep(self.config["optimization_interval"])

                # Run periodic optimization
                logger.info("Running background database optimization...")
                results = await self.optimize_database_performance()

                if (
                    results.get("overall_improvement", {}).get(
                        "optimization_success_rate", 0
                    )
                    < 0.8
                ):
                    logger.warning("Database optimization success rate below 80%")

            except Exception as e:
                logger.error(f"Background optimization failed: {e}")
                await asyncio.sleep(60)  # Wait before retry

    async def _performance_monitoring(self):
        """Background performance monitoring"""
        while True:
            try:
                await asyncio.sleep(60)  # Monitor every minute

                # Collect metrics
                metrics = await self.get_database_metrics()

                # Check for performance issues
                if metrics.slow_queries > 10:
                    logger.warning(
                        f"High number of slow queries detected: {metrics.slow_queries}"
                    )

                if metrics.cache_hit_ratio < 0.9:
                    logger.warning(
                        f"Low cache hit ratio: {metrics.cache_hit_ratio:.2f}"
                    )
                if metrics.connections_active > self.config["pool_size"] * 2:
                    logger.warning(
                        f"High connection usage: {metrics.connections_active} active connections"
                    )

            except Exception as e:
                logger.error(f"Performance monitoring failed: {e}")
                await asyncio.sleep(60)

    async def get_optimization_history(
        self, limit: int = 10
    ) -> List[OptimizationResult]:
        """Get optimization history"""
        return sorted(
            self.optimization_results, key=lambda x: x.timestamp, reverse=True
        )[:limit]

    async def get_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance trends over time"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in self.performance_history if m.timestamp > cutoff]

        if not recent_metrics:
            return {"error": "No recent metrics available"}

        # Calculate trends
        trends = {
            "connections_active": [m.connections_active for m in recent_metrics],
            "query_count": [m.query_count for m in recent_metrics],
            "slow_queries": [m.slow_queries for m in recent_metrics],
            "cache_hit_ratio": [m.cache_hit_ratio for m in recent_metrics],
            "avg_query_time": [m.avg_query_time for m in recent_metrics],
        }

        # Calculate statistics
        stats = {}
        for metric_name, values in trends.items():
            if values:
                stats[metric_name] = {
                    "current": values[-1],
                    "average": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "trend": "increasing"
                    if len(values) > 1 and values[-1] > values[0]
                    else "decreasing"
                    if len(values) > 1 and values[-1] < values[0]
                    else "stable",
                }

        return {
            "time_range_hours": hours,
            "data_points": len(recent_metrics),
            "statistics": stats,
            "timestamps": [m.timestamp.isoformat() for m in recent_metrics],
        }


# Global instance
database_optimizer = EnhancedDatabaseOptimizer()
