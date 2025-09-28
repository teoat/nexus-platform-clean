#!/usr/bin/env python3
"""
NEXUS Platform - Database Service
Handles database connections, pooling, and operations
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
import redis
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nexus_platform.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Create base class for models
Base = declarative_base()

class DatabaseService:
    """Database service with connection pooling and async support"""
    
    def __init__(self):
        self.engine = None
        self.async_engine = None
        self.session_factory = None
        self.async_session_factory = None
        self.redis_client = None
        self.async_redis_client = None
        
    async def initialize(self):
        """Initialize database connections"""
        try:
            # Create sync engine with connection pooling
            self.engine = create_engine(
                DATABASE_URL,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )
            
            # Create async engine
            if DATABASE_URL.startswith("postgresql"):
                async_url = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
            else:
                async_url = DATABASE_URL
            
            self.async_engine = create_async_engine(
                async_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )
            
            # Create session factories
            self.session_factory = sessionmaker(bind=self.engine)
            self.async_session_factory = async_sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Initialize Redis
            self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)
            self.async_redis_client = Redis.from_url(REDIS_URL, decode_responses=True)
            
            # Test connections
            await self.test_connections()
            
            logger.info("Database service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database service: {e}")
            raise
    
    async def test_connections(self):
        """Test database and Redis connections"""
        try:
            # Test database connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # Test async database connection
            async with self.async_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            # Test Redis connection
            await self.async_redis_client.ping()
            
            logger.info("All database connections tested successfully")
            
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            raise
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session"""
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    def get_sync_session(self):
        """Get sync database session"""
        return self.session_factory()
    
    async def get_redis(self) -> Redis:
        """Get async Redis client"""
        return self.async_redis_client
    
    def get_sync_redis(self):
        """Get sync Redis client"""
        return self.redis_client
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a query and return results"""
        async with self.get_async_session() as session:
            result = await session.execute(text(query), params or {})
            return result.fetchall()
    
    async def execute_scalar(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a query and return scalar result"""
        async with self.get_async_session() as session:
            result = await session.execute(text(query), params or {})
            return result.scalar()
    
    async def cache_set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set cache value"""
        try:
            await self.async_redis_client.set(key, value, ex=expire)
            return True
        except Exception as e:
            logger.error(f"Failed to set cache: {e}")
            return False
    
    async def cache_get(self, key: str) -> Optional[Any]:
        """Get cache value"""
        try:
            return await self.async_redis_client.get(key)
        except Exception as e:
            logger.error(f"Failed to get cache: {e}")
            return None
    
    async def cache_delete(self, key: str) -> bool:
        """Delete cache value"""
        try:
            await self.async_redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Failed to delete cache: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database and Redis health"""
        health_status = {
            "database": "unknown",
            "redis": "unknown",
            "timestamp": None
        }
        
        try:
            # Test database
            async with self.async_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            health_status["database"] = "healthy"
        except Exception as e:
            health_status["database"] = f"unhealthy: {e}"
        
        try:
            # Test Redis
            await self.async_redis_client.ping()
            health_status["redis"] = "healthy"
        except Exception as e:
            health_status["redis"] = f"unhealthy: {e}"
        
        from datetime import datetime
        health_status["timestamp"] = datetime.now().isoformat()
        
        return health_status
    
    async def close(self):
        """Close all connections"""
        try:
            if self.async_engine:
                await self.async_engine.dispose()
            if self.async_redis_client:
                await self.async_redis_client.close()
            if self.engine:
                self.engine.dispose()
            if self.redis_client:
                self.redis_client.close()
            logger.info("Database service closed successfully")
        except Exception as e:
            logger.error(f"Error closing database service: {e}")


# Global database service instance
db_service = DatabaseService()

# Dependency for FastAPI
async def get_database_service() -> DatabaseService:
    """Get database service dependency"""
    return db_service

# Initialize database service on module import
async def init_database():
    """Initialize database service"""
    await db_service.initialize()

# Close database service on module cleanup
async def close_database():
    """Close database service"""
    await db_service.close()
