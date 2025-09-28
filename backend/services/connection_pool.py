# NEXUS Platform - Database Connection Pool
# Implements connection pooling for better performance and resource management

import logging
import os
import sqlite3
import threading
import time
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DatabaseConnectionPool:
    """Thread-safe database connection pool"""

    def __init__(
        self, database_url: str, min_connections: int = 5, max_connections: int = 20
    ):
        self.database_url = database_url
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.connections = Queue(maxsize=max_connections)
        self.active_connections = 0
        self.lock = threading.Lock()
        self.connection_timeout = 30  # seconds

        # Initialize pool
        self._initialize_pool()

        # Start cleanup thread
        self.cleanup_thread = threading.Thread(
            target=self._cleanup_connections, daemon=True
        )
        self.cleanup_thread.start()

    def _initialize_pool(self):
        """Initialize the connection pool with minimum connections"""
        for _ in range(self.min_connections):
            conn = self._create_connection()
            if conn:
                self.connections.put(conn)
                self.active_connections += 1

    def _create_connection(self) -> Optional[sqlite3.Connection]:
        """Create a new database connection"""
        try:
            if self.database_url.startswith("sqlite:///"):
                db_path = self.database_url.replace("sqlite:///", "")
                conn = sqlite3.connect(db_path, timeout=30)
                conn.row_factory = sqlite3.Row
                # Enable WAL mode for better concurrency
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
                conn.execute("PRAGMA cache_size=10000")
                conn.execute("PRAGMA temp_store=MEMORY")
                return conn
            else:
                logger.error(f"Unsupported database URL: {self.database_url}")
                return None
        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            return None

    def get_connection(self, timeout: int = None) -> Optional[sqlite3.Connection]:
        """Get a connection from the pool"""
        if timeout is None:
            timeout = self.connection_timeout

        try:
            # Try to get existing connection
            conn = self.connections.get(timeout=timeout)
            return conn
        except Empty:
            # No available connections, try to create new one
            with self.lock:
                if self.active_connections < self.max_connections:
                    conn = self._create_connection()
                    if conn:
                        self.active_connections += 1
                        return conn

            # Pool is full, wait for a connection to be returned
            try:
                conn = self.connections.get(timeout=timeout)
                return conn
            except Empty:
                logger.error("Failed to get database connection: timeout")
                return None

    def return_connection(self, conn: sqlite3.Connection):
        """Return a connection to the pool"""
        if conn:
            try:
                # Check if connection is still valid
                conn.execute("SELECT 1")
                self.connections.put(conn, timeout=1)
            except Exception as e:
                logger.warning(f"Connection is invalid, creating new one: {e}")
                conn.close()
                with self.lock:
                    self.active_connections -= 1

                # Create replacement connection
                new_conn = self._create_connection()
                if new_conn:
                    self.connections.put(new_conn, timeout=1)
                    with self.lock:
                        self.active_connections += 1

    def _cleanup_connections(self):
        """Cleanup thread to remove stale connections"""
        while True:
            try:
                time.sleep(60)  # Check every minute

                # Get all connections and check their health
                temp_connections = []
                while not self.connections.empty():
                    try:
                        conn = self.connections.get_nowait()
                        try:
                            conn.execute("SELECT 1")
                            temp_connections.append(conn)
                        except Exception:
                            # Connection is stale, close it
                            conn.close()
                            with self.lock:
                                self.active_connections -= 1
                    except Empty:
                        break

                # Return healthy connections back to pool
                for conn in temp_connections:
                    self.connections.put(conn, timeout=1)

                # Ensure minimum connections
                with self.lock:
                    while self.active_connections < self.min_connections:
                        conn = self._create_connection()
                        if conn:
                            self.connections.put(conn, timeout=1)
                            self.active_connections += 1
                        else:
                            break

            except Exception as e:
                logger.error(f"Connection pool cleanup error: {e}")

    @contextmanager
    def get_connection_context(self, timeout: int = None):
        """Context manager for database connections"""
        conn = None
        try:
            conn = self.get_connection(timeout)
            if not conn:
                raise Exception("Failed to get database connection")
            yield conn
        finally:
            if conn:
                self.return_connection(conn)

    def get_pool_status(self) -> Dict[str, Any]:
        """Get connection pool status"""
        return {
            "active_connections": self.active_connections,
            "available_connections": self.connections.qsize(),
            "min_connections": self.min_connections,
            "max_connections": self.max_connections,
            "database_url": self.database_url,
        }


# Global connection pool instance
_connection_pool: Optional[DatabaseConnectionPool] = None
