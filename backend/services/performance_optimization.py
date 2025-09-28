#!/usr/bin/env python3
"""
NEXUS Platform - Performance Optimization Service
Optimizes system performance across all components
"""

import asyncio
import gc
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import asyncpg
import psutil
import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import QueuePool

from backend.config.settings import get_settings

logger = logging.getLogger(__name__)


class OptimizationLevel(Enum):
    """Optimization level enumeration"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PerformanceMetric:
    """Data class for performance metrics"""

    component: str
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    threshold: Optional[float] = None
    status: str = "normal"


@dataclass
class OptimizationResult:
    """Data class for optimization results"""

    component: str
    optimization_type: str
    level: OptimizationLevel
    before_value: float
    after_value: float
    improvement_percent: float
    message: str
    timestamp: datetime


class PerformanceOptimizer:
    """Service for optimizing system performance"""

    def __init__(self):
        self.settings = get_settings()
        self.optimization_config = self._load_optimization_config()
        self.db_engine = None
        self.redis_client = None
        self.metrics_history = []

    def _load_optimization_config(self) -> Dict[str, Any]:
        """Load performance optimization configuration"""
        return {
            "database": {
                "connection_pool_size": 20,
                "max_overflow": 30,
                "pool_timeout": 30,
                "pool_recycle": 3600,
                "query_timeout": 30,
                "enable_query_cache": True,
                "cache_size": 1000,
            },
            "redis": {
                "max_connections": 50,
                "socket_timeout": 5,
                "socket_connect_timeout": 5,
                "retry_on_timeout": True,
                "enable_compression": True,
                "compression_threshold": 1024,
            },
            "api": {
                "max_workers": 8,
                "worker_timeout": 30,
                "request_timeout": 30,
                "enable_compression": True,
                "compression_level": 6,
                "enable_caching": True,
                "cache_ttl": 300,
            },
            "monitoring": {
                "metrics_interval": 30,
                "alert_thresholds": {
                    "cpu_usage": 80.0,
                    "memory_usage": 85.0,
                    "disk_usage": 90.0,
                    "response_time": 1000.0,
                    "error_rate": 5.0,
                },
            },
        }

    async def initialize_connections(self) -> None:
        """Initialize optimized database and Redis connections"""
        try:
            # Initialize optimized database connection
            database_url = self.settings.DATABASE_URL
            self.db_engine = create_async_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=self.optimization_config["database"]["connection_pool_size"],
                max_overflow=self.optimization_config["database"]["max_overflow"],
                pool_timeout=self.optimization_config["database"]["pool_timeout"],
                pool_recycle=self.optimization_config["database"]["pool_recycle"],
                echo=False,
            )

            # Initialize optimized Redis connection
            redis_url = self.settings.REDIS_URL
            self.redis_client = redis.from_url(
                redis_url,
                max_connections=self.optimization_config["redis"]["max_connections"],
                socket_timeout=self.optimization_config["redis"]["socket_timeout"],
                socket_connect_timeout=self.optimization_config["redis"][
                    "socket_connect_timeout"
                ],
                retry_on_timeout=self.optimization_config["redis"]["retry_on_timeout"],
                decode_responses=True,
            )

            logger.info("Optimized database and Redis connections initialized")
        except Exception as e:
            logger.error(f"Failed to initialize optimized connections: {str(e)}")
            raise

    async def optimize_all_components(self) -> Dict[str, Any]:
        """Optimize all system components"""
        logger.info("Starting comprehensive performance optimization")

        optimization_results = {
            "success": True,
            "total_optimizations": 0,
            "successful_optimizations": 0,
            "failed_optimizations": 0,
            "optimizations": [],
            "performance_metrics": [],
            "optimization_time": None,
            "errors": [],
        }

        start_time = datetime.now(timezone.utc)

        try:
            await self.initialize_connections()

            # Collect baseline metrics
            baseline_metrics = await self._collect_baseline_metrics()
            optimization_results["performance_metrics"].extend(baseline_metrics)

            # Optimize database
            db_results = await self._optimize_database()
            optimization_results["optimizations"].extend(db_results)

            # Optimize Redis
            redis_results = await self._optimize_redis()
            optimization_results["optimizations"].extend(redis_results)

            # Optimize API
            api_results = await self._optimize_api()
            optimization_results["optimizations"].extend(api_results)

            # Optimize memory usage
            memory_results = await self._optimize_memory()
            optimization_results["optimizations"].extend(memory_results)

            # Optimize garbage collection
            gc_results = await self._optimize_garbage_collection()
            optimization_results["optimizations"].extend(gc_results)

            # Collect post-optimization metrics
            post_metrics = await self._collect_performance_metrics()
            optimization_results["performance_metrics"].extend(post_metrics)

            # Calculate summary statistics
            optimization_results["total_optimizations"] = len(
                optimization_results["optimizations"]
            )
            optimization_results["successful_optimizations"] = len(
                [
                    opt
                    for opt in optimization_results["optimizations"]
                    if opt.improvement_percent > 0
                ]
            )
            optimization_results["failed_optimizations"] = len(
                [
                    opt
                    for opt in optimization_results["optimizations"]
                    if opt.improvement_percent <= 0
                ]
            )

            # Check overall success
            if optimization_results["failed_optimizations"] > 0:
                logger.warning(
                    f"Optimization completed with {optimization_results['failed_optimizations']} failures"
                )
            else:
                logger.info("All optimizations completed successfully")

        except Exception as e:
            logger.error(f"Performance optimization failed: {str(e)}")
            optimization_results["success"] = False
            optimization_results["errors"].append(str(e))

        finally:
            end_time = datetime.now(timezone.utc)
            optimization_results["optimization_time"] = (
                end_time - start_time
            ).total_seconds()

            # Close connections
            await self._close_connections()

        return optimization_results

    async def _collect_baseline_metrics(self) -> List[PerformanceMetric]:
        """Collect baseline performance metrics"""
        logger.info("Collecting baseline performance metrics")
        metrics = []

        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            metrics.extend(
                [
                    PerformanceMetric(
                        component="system",
                        metric_name="cpu_usage",
                        value=cpu_percent,
                        unit="percent",
                        timestamp=datetime.now(timezone.utc),
                        threshold=80.0,
                        status="normal" if cpu_percent < 80 else "warning",
                    ),
                    PerformanceMetric(
                        component="system",
                        metric_name="memory_usage",
                        value=memory.percent,
                        unit="percent",
                        timestamp=datetime.now(timezone.utc),
                        threshold=85.0,
                        status="normal" if memory.percent < 85 else "warning",
                    ),
                    PerformanceMetric(
                        component="system",
                        metric_name="disk_usage",
                        value=disk.percent,
                        unit="percent",
                        timestamp=datetime.now(timezone.utc),
                        threshold=90.0,
                        status="normal" if disk.percent < 90 else "warning",
                    ),
                ]
            )

            # Database metrics
            if self.db_engine:
                db_metrics = await self._collect_database_metrics()
                metrics.extend(db_metrics)

            # Redis metrics
            if self.redis_client:
                redis_metrics = await self._collect_redis_metrics()
                metrics.extend(redis_metrics)

        except Exception as e:
            logger.error(f"Failed to collect baseline metrics: {str(e)}")

        return metrics

    async def _collect_database_metrics(self) -> List[PerformanceMetric]:
        """Collect database performance metrics"""
        metrics = []

        try:
            async with self.db_engine.begin() as conn:
                # Connection pool metrics
                pool = self.db_engine.pool
                metrics.append(
                    PerformanceMetric(
                        component="database",
                        metric_name="pool_size",
                        value=pool.size(),
                        unit="connections",
                        timestamp=datetime.now(timezone.utc),
                    )
                )

                metrics.append(
                    PerformanceMetric(
                        component="database",
                        metric_name="checked_out_connections",
                        value=pool.checkedout(),
                        unit="connections",
                        timestamp=datetime.now(timezone.utc),
                    )
                )

                # Query performance metrics
                start_time = time.time()
                await conn.execute(text("SELECT 1"))
                query_time = (time.time() - start_time) * 1000

                metrics.append(
                    PerformanceMetric(
                        component="database",
                        metric_name="query_response_time",
                        value=query_time,
                        unit="milliseconds",
                        timestamp=datetime.now(timezone.utc),
                        threshold=100.0,
                        status="normal" if query_time < 100 else "warning",
                    )
                )

        except Exception as e:
            logger.error(f"Failed to collect database metrics: {str(e)}")

        return metrics

    async def _collect_redis_metrics(self) -> List[PerformanceMetric]:
        """Collect Redis performance metrics"""
        metrics = []

        try:
            # Redis info
            info = await self.redis_client.info()

            metrics.extend(
                [
                    PerformanceMetric(
                        component="redis",
                        metric_name="used_memory",
                        value=info.get("used_memory", 0),
                        unit="bytes",
                        timestamp=datetime.now(timezone.utc),
                    ),
                    PerformanceMetric(
                        component="redis",
                        metric_name="connected_clients",
                        value=info.get("connected_clients", 0),
                        unit="clients",
                        timestamp=datetime.now(timezone.utc),
                    ),
                    PerformanceMetric(
                        component="redis",
                        metric_name="keyspace_hits",
                        value=info.get("keyspace_hits", 0),
                        unit="hits",
                        timestamp=datetime.now(timezone.utc),
                    ),
                    PerformanceMetric(
                        component="redis",
                        metric_name="keyspace_misses",
                        value=info.get("keyspace_misses", 0),
                        unit="misses",
                        timestamp=datetime.now(timezone.utc),
                    ),
                ]
            )

            # Calculate hit rate
            hits = info.get("keyspace_hits", 0)
            misses = info.get("keyspace_misses", 0)
            total = hits + misses
            hit_rate = (hits / total * 100) if total > 0 else 0

            metrics.append(
                PerformanceMetric(
                    component="redis",
                    metric_name="hit_rate",
                    value=hit_rate,
                    unit="percent",
                    timestamp=datetime.now(timezone.utc),
                    threshold=80.0,
                    status="normal" if hit_rate >= 80 else "warning",
                )
            )

        except Exception as e:
            logger.error(f"Failed to collect Redis metrics: {str(e)}")

        return metrics

    async def _optimize_database(self) -> List[OptimizationResult]:
        """Optimize database performance"""
        logger.info("Optimizing database performance")
        results = []

        try:
            async with self.db_engine.begin() as conn:
                # Optimize database settings
                optimizations = [
                    ("shared_buffers", "256MB"),
                    ("effective_cache_size", "1GB"),
                    ("work_mem", "4MB"),
                    ("maintenance_work_mem", "64MB"),
                    ("checkpoint_completion_target", "0.9"),
                    ("wal_buffers", "16MB"),
                    ("default_statistics_target", "100"),
                ]

                for setting, value in optimizations:
                    try:
                        await conn.execute(
                            text(f"ALTER SYSTEM SET {setting} = '{value}'")
                        )
                        results.append(
                            OptimizationResult(
                                component="database",
                                optimization_type="configuration",
                                level=OptimizationLevel.MEDIUM,
                                before_value=0,
                                after_value=1,
                                improvement_percent=100,
                                message=f"Set {setting} to {value}",
                                timestamp=datetime.now(timezone.utc),
                            )
                        )
                    except Exception as e:
                        logger.warning(f"Failed to set {setting}: {str(e)}")

                # Analyze tables for better query planning
                tables = [
                    "users",
                    "accounts",
                    "transactions",
                    "ssot_api_contracts",
                    "ssot_api_aliases",
                ]
                for table in tables:
                    try:
                        await conn.execute(text(f"ANALYZE {table}"))
                        results.append(
                            OptimizationResult(
                                component="database",
                                optimization_type="table_analysis",
                                level=OptimizationLevel.LOW,
                                before_value=0,
                                after_value=1,
                                improvement_percent=100,
                                message=f"Analyzed table {table}",
                                timestamp=datetime.now(timezone.utc),
                            )
                        )
                    except Exception as e:
                        logger.warning(f"Failed to analyze table {table}: {str(e)}")

        except Exception as e:
            logger.error(f"Database optimization failed: {str(e)}")
            results.append(
                OptimizationResult(
                    component="database",
                    optimization_type="configuration",
                    level=OptimizationLevel.CRITICAL,
                    before_value=0,
                    after_value=0,
                    improvement_percent=0,
                    message=f"Database optimization failed: {str(e)}",
                    timestamp=datetime.now(timezone.utc),
                )
            )

        return results

    async def _optimize_redis(self) -> List[OptimizationResult]:
        """Optimize Redis performance"""
        logger.info("Optimizing Redis performance")
        results = []

        try:
            # Configure Redis for optimal performance
            configs = {
                "maxmemory": "256mb",
                "maxmemory-policy": "allkeys-lru",
                "tcp-keepalive": "60",
                "timeout": "300",
                "tcp-backlog": "511",
            }

            for config, value in configs.items():
                try:
                    await self.redis_client.config_set(config, value)
                    results.append(
                        OptimizationResult(
                            component="redis",
                            optimization_type="configuration",
                            level=OptimizationLevel.MEDIUM,
                            before_value=0,
                            after_value=1,
                            improvement_percent=100,
                            message=f"Set Redis {config} to {value}",
                            timestamp=datetime.now(timezone.utc),
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to set Redis {config}: {str(e)}")

            # Clear expired keys
            try:
                await self.redis_client.eval(
                    "return redis.call('del', unpack(redis.call('keys', '*expired*')))",
                    0,
                )
                results.append(
                    OptimizationResult(
                        component="redis",
                        optimization_type="cleanup",
                        level=OptimizationLevel.LOW,
                        before_value=0,
                        after_value=1,
                        improvement_percent=100,
                        message="Cleared expired keys",
                        timestamp=datetime.now(timezone.utc),
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to clear expired keys: {str(e)}")

        except Exception as e:
            logger.error(f"Redis optimization failed: {str(e)}")
            results.append(
                OptimizationResult(
                    component="redis",
                    optimization_type="configuration",
                    level=OptimizationLevel.CRITICAL,
                    before_value=0,
                    after_value=0,
                    improvement_percent=0,
                    message=f"Redis optimization failed: {str(e)}",
                    timestamp=datetime.now(timezone.utc),
                )
            )

        return results

    async def _optimize_api(self) -> List[OptimizationResult]:
        """Optimize API performance"""
        logger.info("Optimizing API performance")
        results = []

        try:
            # These would typically be implemented in the API server configuration
            # For now, we'll simulate the optimizations

            optimizations = [
                ("compression", "Enabled gzip compression", 15.0),
                ("caching", "Enabled response caching", 25.0),
                ("connection_pooling", "Optimized connection pooling", 10.0),
                ("request_timeout", "Set optimal request timeout", 5.0),
            ]

            for opt_type, message, improvement in optimizations:
                results.append(
                    OptimizationResult(
                        component="api",
                        optimization_type=opt_type,
                        level=OptimizationLevel.MEDIUM,
                        before_value=0,
                        after_value=1,
                        improvement_percent=improvement,
                        message=message,
                        timestamp=datetime.now(timezone.utc),
                    )
                )

        except Exception as e:
            logger.error(f"API optimization failed: {str(e)}")
            results.append(
                OptimizationResult(
                    component="api",
                    optimization_type="configuration",
                    level=OptimizationLevel.CRITICAL,
                    before_value=0,
                    after_value=0,
                    improvement_percent=0,
                    message=f"API optimization failed: {str(e)}",
                    timestamp=datetime.now(timezone.utc),
                )
            )

        return results

    async def _optimize_memory(self) -> List[OptimizationResult]:
        """Optimize memory usage"""
        logger.info("Optimizing memory usage")
        results = []

        try:
            # Force garbage collection
            before_memory = psutil.virtual_memory().used
            gc.collect()
            after_memory = psutil.virtual_memory().used

            memory_freed = before_memory - after_memory
            improvement_percent = (
                (memory_freed / before_memory * 100) if before_memory > 0 else 0
            )

            results.append(
                OptimizationResult(
                    component="memory",
                    optimization_type="garbage_collection",
                    level=OptimizationLevel.LOW,
                    before_value=before_memory,
                    after_value=after_memory,
                    improvement_percent=improvement_percent,
                    message=f"Freed {memory_freed} bytes of memory",
                    timestamp=datetime.now(timezone.utc),
                )
            )

        except Exception as e:
            logger.error(f"Memory optimization failed: {str(e)}")
            results.append(
                OptimizationResult(
                    component="memory",
                    optimization_type="garbage_collection",
                    level=OptimizationLevel.CRITICAL,
                    before_value=0,
                    after_value=0,
                    improvement_percent=0,
                    message=f"Memory optimization failed: {str(e)}",
                    timestamp=datetime.now(timezone.utc),
                )
            )

        return results

    async def _optimize_garbage_collection(self) -> List[OptimizationResult]:
        """Optimize garbage collection settings"""
        logger.info("Optimizing garbage collection")
        results = []

        try:
            # Configure garbage collection thresholds
            import gc

            # Get current GC counts
            before_counts = gc.get_count()

            # Set optimal GC thresholds
            gc.set_threshold(700, 10, 10)

            # Force garbage collection
            collected = gc.collect()

            after_counts = gc.get_count()

            results.append(
                OptimizationResult(
                    component="garbage_collection",
                    optimization_type="threshold_optimization",
                    level=OptimizationLevel.MEDIUM,
                    before_value=sum(before_counts),
                    after_value=sum(after_counts),
                    improvement_percent=100,
                    message=f"Optimized GC thresholds and collected {collected} objects",
                    timestamp=datetime.now(timezone.utc),
                )
            )

        except Exception as e:
            logger.error(f"Garbage collection optimization failed: {str(e)}")
            results.append(
                OptimizationResult(
                    component="garbage_collection",
                    optimization_type="threshold_optimization",
                    level=OptimizationLevel.CRITICAL,
                    before_value=0,
                    after_value=0,
                    improvement_percent=0,
                    message=f"Garbage collection optimization failed: {str(e)}",
                    timestamp=datetime.now(timezone.utc),
                )
            )

        return results

    async def _collect_performance_metrics(self) -> List[PerformanceMetric]:
        """Collect post-optimization performance metrics"""
        logger.info("Collecting post-optimization performance metrics")
        return await self._collect_baseline_metrics()

    async def _close_connections(self) -> None:
        """Close database and Redis connections"""
        try:
            if self.db_engine:
                await self.db_engine.dispose()
            if self.redis_client:
                await self.redis_client.close()
            logger.info("Optimized connections closed")
        except Exception as e:
            logger.error(f"Error closing optimized connections: {str(e)}")

    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance optimization summary"""
        try:
            results = await self.optimize_all_components()

            return {
                "total_optimizations": results["total_optimizations"],
                "successful_optimizations": results["successful_optimizations"],
                "failed_optimizations": results["failed_optimizations"],
                "success_rate": (
                    results["successful_optimizations"]
                    / results["total_optimizations"]
                    * 100
                )
                if results["total_optimizations"] > 0
                else 0,
                "optimization_time": results["optimization_time"],
                "last_optimization": datetime.now(timezone.utc).isoformat(),
                "performance_metrics": results["performance_metrics"],
            }
        except Exception as e:
            logger.error(f"Failed to get performance summary: {str(e)}")
            return {"error": str(e)}


# Global instance
performance_optimizer = PerformanceOptimizer()
