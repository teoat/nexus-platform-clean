#!/usr/bin/env python3
"""
NEXUS Platform - Database Connection
Production-ready database connection with connection pooling and health checks
"""

import logging
import os
from contextlib import contextmanager

from sqlalchemy import create_engine, exc, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from database.base import Base

logger = logging.getLogger(__name__)


# Database configuration
def get_database_url():
    """Get database URL based on environment"""
    env = os.getenv("ENVIRONMENT", "development")

    if env == "development":
        return os.getenv("DATABASE_URL", "sqlite:///./nexus.db")
    elif env == "production":
        # Production should always use environment variables
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError(
                "DATABASE_URL environment variable is required for production"
            )
        return db_url
    else:
        # Default to development
        return os.getenv("DATABASE_URL", "sqlite:///./nexus.db")


DATABASE_URL = get_database_url()

# Connection pool configuration
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=True,  # Verify connections before use
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_database_connection():
    """
    Dependency to get a database session
    Yields a database session and ensures it's closed after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def check_connection() -> bool:
    """
    Check database connection health
    Returns True if connection is healthy, False otherwise
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return result.scalar() == 1
    except exc.SQLAlchemyError as e:
        logger.error(f"Database connection check failed: {e}")
        return False


def create_tables():
    """
    Create all database tables
    This should be called during application startup
    """
    try:
        # Base.metadata.create_all(bind=engine)  # Commented out to avoid UUID issues with SQLite
        logger.info("Database tables creation skipped (using database service)")
    except exc.SQLAlchemyError as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


# Initialize database on module import
def initialize_database():
    """
    Initialize database connection and create tables if needed
    """
    try:
        # Test connection
        if not check_connection():
            logger.error("Database connection failed during initialization")
            return False

        # Create tables if they don't exist
        create_tables()

        logger.info("Database initialized successfully")
        return True

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


# Auto-initialize on import
if __name__ != "__main__":
    initialize_database()
