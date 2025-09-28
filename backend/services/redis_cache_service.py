#!/usr/bin/env python3
"""
Redis Cache Service
High-performance caching layer for API responses and frequently accessed data
"""

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    WRITE_THROUGH = "write_through"  # Write to cache and DB simultaneously
    WRITE_BEHIND = "write_behind"  # Write to cache first, then DB


class CacheInvalidation(Enum):
    IMMEDIATE = "immediate"  # Invalidate immediately
    DELAYED = "delayed"  # Invalidate after delay
    PATTERN = "pattern"  # Invalidate by pattern
    CASCADE = "cascade"  # Invalidate related caches


@dataclass
class CacheEntry:
    """Cache entry with metadata"""

    key: str
    value: Any
    ttl: Optional[int]
    created_at: datetime
    accessed_at: datetime
    access_count: int
    size_bytes: int
    tags: List[str]


@dataclass
class CacheStats:
    """Cache performance statistics"""

    hits: int
    misses: int
    sets: int
    deletes: int
    evictions: int
    hit_rate: float
    total_keys: int
    memory_usage_bytes: int
    uptime_seconds: float


class RedisCacheService:
    """High-performance Redis caching service"""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.cache_stats = CacheStats(0, 0, 0, 0, 0, 0.0, 0, 0, 0)
        self.start_time = datetime.now()
        self.cache_prefix = "nexus_cache:"
        self.api_cache_prefix = "api_cache:"
        self.data_cache_prefix = "data_cache:"

        # Cache configuration
        self.config = {
            "host": "localhost",
            "port": 6379,
            "db": 0,
            "password": None,
            "max_connections": 20,
            "socket_timeout": 5,
            "socket_connect_timeout": 5,
            "retry_on_timeout": True,
            "default_ttl": 3600,  # 1 hour
            "api_cache_ttl": 300,  # 5 minutes for API responses
            "data_cache_ttl": 1800,  # 30 minutes for data
            "max_memory_policy": "allkeys-lru",
            "max_memory": "512mb",
        }

        # Cache warming patterns
        self.warmup_patterns = {
            "api_endpoints": [
                "/api/v3/health",
                "/api/v3/ssot/aliases",
                "/api/v3/system/config",
            ],
            "frequent_queries": [
                "user_profile_*",
                "system_config_*",
                "service_status_*",
            ],
        }

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                f"redis://{self.config['host']}:{self.config['port']}/{self.config['db']}",
                password=self.config["password"],
                max_connections=self.config["max_connections"],
                socket_timeout=self.config["socket_timeout"],
                socket_connect_timeout=self.config["socket_connect_timeout"],
                retry_on_timeout=self.config["retry_on_timeout"],
                decode_responses=True,
            )

            # Test connection
            await self.redis_client.ping()
            logger.info("Redis cache service initialized successfully")

            # Configure Redis memory policy
            await self.redis_client.config_set(
                "maxmemory-policy", self.config["max_memory_policy"]
            )
            await self.redis_client.config_set("maxmemory", self.config["max_memory"])

            # Start background tasks
            asyncio.create_task(self._stats_updater())
            asyncio.create_task(self._cache_warmer())

        except Exception as e:
            logger.error(f"Failed to initialize Redis cache service: {e}")
            self.redis_client = None

    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis cache service closed")

    # API Response Caching
    async def cache_api_response(
        self,
        method: str,
        path: str,
        query_params: Dict[str, Any],
        response_data: Any,
        ttl: Optional[int] = None,
    ) -> str:
        """Cache API response"""
        if not self.redis_client:
            return ""

        # Generate cache key
        cache_key = self._generate_api_cache_key(method, path, query_params)

        # Serialize response
        serialized_data = json.dumps(response_data, default=str)

        # Set TTL
        effective_ttl = ttl or self.config["api_cache_ttl"]

        # Store in cache
        await self.redis_client.setex(cache_key, effective_ttl, serialized_data)

        # Update stats
        self.cache_stats.sets += 1

        # Add to API cache set for invalidation
        api_pattern_key = f"{self.api_cache_prefix}pattern:{path.split('/')[1] if len(path.split('/')) > 1 else 'general'}"
        await self.redis_client.sadd(api_pattern_key, cache_key)

        logger.debug(f"Cached API response: {cache_key}")
        return cache_key

    async def get_cached_api_response(
        self, method: str, path: str, query_params: Dict[str, Any]
    ) -> Optional[Any]:
        """Get cached API response"""
        if not self.redis_client:
            return None

        cache_key = self._generate_api_cache_key(method, path, query_params)

        cached_data = await self.redis_client.get(cache_key)
        if cached_data:
            self.cache_stats.hits += 1
            try:
                return json.loads(cached_data)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in cache for key: {cache_key}")
                await self.redis_client.delete(cache_key)
                return None
        else:
            self.cache_stats.misses += 1
            return None

    async def invalidate_api_cache(
        self, path_pattern: str, method: Optional[str] = None
    ):
        """Invalidate API cache by path pattern"""
        if not self.redis_client:
            return

        pattern = f"{self.api_cache_prefix}pattern:{path_pattern.split('/')[1] if len(path_pattern.split('/')) > 1 else 'general'}"
        cache_keys = await self.redis_client.smembers(pattern)

        if cache_keys:
            # Filter by method if specified
            if method:
                filtered_keys = []
                for key in cache_keys:
                    if f":{method}:" in key:
                        filtered_keys.append(key)
                cache_keys = filtered_keys

            if cache_keys:
                await self.redis_client.delete(*cache_keys)
                await self.redis_client.delete(pattern)
                self.cache_stats.deletes += len(cache_keys)
                logger.info(
                    f"Invalidated {len(cache_keys)} API cache entries for pattern: {path_pattern}"
                )

    # Data Caching
    async def cache_data(
        self, key: str, data: Any, ttl: Optional[int] = None, tags: List[str] = None
    ) -> bool:
        """Cache arbitrary data"""
        if not self.redis_client:
            return False

        full_key = f"{self.data_cache_prefix}{key}"
        serialized_data = json.dumps(data, default=str)
        effective_ttl = ttl or self.config["data_cache_ttl"]

        success = await self.redis_client.setex(
            full_key, effective_ttl, serialized_data
        )
        if success:
            self.cache_stats.sets += 1

            # Add tags for invalidation
            if tags:
                for tag in tags:
                    tag_key = f"{self.cache_prefix}tag:{tag}"
                    await self.redis_client.sadd(tag_key, full_key)

        return bool(success)

    async def get_cached_data(self, key: str) -> Optional[Any]:
        """Get cached data"""
        if not self.redis_client:
            return None

        full_key = f"{self.data_cache_prefix}{key}"
        cached_data = await self.redis_client.get(full_key)

        if cached_data:
            self.cache_stats.hits += 1
            try:
                return json.loads(cached_data)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in data cache for key: {key}")
                await self.redis_client.delete(full_key)
                return None
        else:
            self.cache_stats.misses += 1
            return None

    async def invalidate_data_cache(self, tags: List[str] = None, pattern: str = None):
        """Invalidate data cache by tags or pattern"""
        if not self.redis_client:
            return

        keys_to_delete = []

        if tags:
            for tag in tags:
                tag_key = f"{self.cache_prefix}tag:{tag}"
                tagged_keys = await self.redis_client.smembers(tag_key)
                keys_to_delete.extend(tagged_keys)
                await self.redis_client.delete(tag_key)

        if pattern:
            pattern_key = f"{self.data_cache_prefix}{pattern}"
            matching_keys = await self.redis_client.keys(pattern_key)
            keys_to_delete.extend(matching_keys)

        if keys_to_delete:
            await self.redis_client.delete(*keys_to_delete)
            self.cache_stats.deletes += len(keys_to_delete)
            logger.info(f"Invalidated {len(keys_to_delete)} data cache entries")

    # Cache Management
    async def get_cache_stats(self) -> CacheStats:
        """Get cache statistics"""
        if not self.redis_client:
            return self.cache_stats

        try:
            # Get Redis info
            info = await self.redis_client.info()

            self.cache_stats.total_keys = info.get("db0", {}).get("keys", 0)
            self.cache_stats.memory_usage_bytes = info.get("used_memory", 0)
            self.cache_stats.uptime_seconds = (
                datetime.now() - self.start_time
            ).total_seconds()

            # Calculate hit rate
            total_requests = self.cache_stats.hits + self.cache_stats.misses
            if total_requests > 0:
                self.cache_stats.hit_rate = self.cache_stats.hits / total_requests

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")

        return self.cache_stats

    async def clear_cache(self, pattern: str = "*"):
        """Clear cache entries matching pattern"""
        if not self.redis_client:
            return 0

        pattern_key = f"{self.cache_prefix}{pattern}"
        keys = await self.redis_client.keys(pattern_key)

        if keys:
            deleted_count = await self.redis_client.delete(*keys)
            self.cache_stats.deletes += deleted_count
            logger.info(
                f"Cleared {deleted_count} cache entries matching pattern: {pattern}"
            )
            return deleted_count

        return 0

    async def warmup_cache(self):
        """Warm up cache with frequently accessed data"""
        if not self.redis_client:
            return

        logger.info("Starting cache warmup")

        # Warm up API endpoints
        for endpoint in self.warmup_patterns["api_endpoints"]:
            try:
                # This would typically make actual API calls
                # For now, we'll just log the intent
                logger.debug(f"Would warm up API endpoint: {endpoint}")
            except Exception as e:
                logger.warning(f"Failed to warm up endpoint {endpoint}: {e}")

        # Warm up frequent queries
        for pattern in self.warmup_patterns["frequent_queries"]:
            try:
                # This would typically preload data
                logger.debug(f"Would warm up data pattern: {pattern}")
            except Exception as e:
                logger.warning(f"Failed to warm up pattern {pattern}: {e}")

        logger.info("Cache warmup completed")

    # Utility Methods
    def _generate_api_cache_key(
        self, method: str, path: str, query_params: Dict[str, Any]
    ) -> str:
        """Generate cache key for API response"""
        # Normalize path (remove trailing slashes, etc.)
        normalized_path = path.rstrip("/")

        # Sort query parameters for consistent key generation
        sorted_params = "&".join(f"{k}={v}" for k, v in sorted(query_params.items()))

        # Create key components
        key_components = f"{method}:{normalized_path}:{sorted_params}"

        # Generate hash for consistent key length
        key_hash = hashlib.md5(key_components.encode()).hexdigest()[:16]

        return f"{self.api_cache_prefix}{key_hash}"

    async def _stats_updater(self):
        """Background task to update cache statistics"""
        while True:
            try:
                await self.get_cache_stats()
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"Error updating cache stats: {e}")
                await asyncio.sleep(60)

    async def _cache_warmer(self):
        """Background task to warm up cache"""
        await asyncio.sleep(300)  # Wait 5 minutes after startup

        while True:
            try:
                await self.warmup_cache()
                await asyncio.sleep(3600)  # Warm up every hour
            except Exception as e:
                logger.error(f"Error in cache warmer: {e}")
                await asyncio.sleep(3600)

    # Integration with FastAPI
    def get_cache_middleware(self):
        """Get FastAPI middleware for automatic caching"""
        from fastapi import Request, Response
        from starlette.middleware.base import BaseHTTPMiddleware

        class CacheMiddleware(BaseHTTPMiddleware):
            def __init__(self, app, cache_service: RedisCacheService):
                super().__init__(app)
                self.cache_service = cache_service

            async def dispatch(self, request: Request, call_next):
                # Only cache GET requests
                if request.method != "GET":
                    return await call_next(request)

                # Skip caching for certain paths
                skip_paths = ["/health", "/metrics", "/api/v3/auth"]
                if any(path in request.url.path for path in skip_paths):
                    return await call_next(request)

                # Try to get from cache
                query_params = dict(request.query_params)
                cached_response = await self.cache_service.get_cached_api_response(
                    request.method, request.url.path, query_params
                )

                if cached_response:
                    # Return cached response
                    from fastapi.responses import JSONResponse

                    return JSONResponse(content=cached_response)

                # Get fresh response
                response = await call_next(request)

                # Cache the response if successful
                if response.status_code == 200:
                    try:
                        response_body = response.body
                        if response_body:
                            response_data = json.loads(response_body.decode())
                            await self.cache_service.cache_api_response(
                                request.method,
                                request.url.path,
                                query_params,
                                response_data,
                            )
                    except Exception as e:
                        logger.debug(f"Failed to cache response: {e}")

                return response

        return CacheMiddleware


# Global instance
redis_cache_service = RedisCacheService()
