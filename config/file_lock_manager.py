"""
NEXUS Platform - File Lock Manager
This module provides centralized file locking for critical operations.
"""

import asyncio
import logging
import os
import threading
import time

logger = logging.getLogger(__name__)


@dataclass
class FileLockInfo:
    """Information about a file lock"""

    file_path: str
    lock_type: str  # 'exclusive' or 'shared'
    acquired_at: float
    acquired_by: str
    timeout: Optional[float] = None


class FileLockManager:
    """
    Centralized file locking manager for the NEXUS platform.

    Provides both synchronous and asynchronous file locking capabilities
    to prevent race conditions in file operations.
    """

    def __init__(self):
        self._active_locks: Dict[str, FileLockInfo] = {}
        self._lock_timeout = 30  # seconds
        self._max_wait_time = 60  # seconds
        self._lock = threading.RLock()

    def _get_lock_key(self, file_path: Union[str, Path]) -> str:
        """Generate a unique lock key for the file path"""
        return str(Path(file_path).resolve())

    def _is_lock_expired(self, lock_info: FileLockInfo) -> bool:
        """Check if a lock has expired"""
        if lock_info.timeout is None:
            return False
        return time.time() - lock_info.acquired_at > lock_info.timeout

    def _cleanup_expired_locks(self) -> None:
        """Clean up expired locks"""
        current_time = time.time()
        expired_keys = []

        for key, lock_info in self._active_locks.items():
            if (
                lock_info.timeout
                and current_time - lock_info.acquired_at > lock_info.timeout
            ):
                expired_keys.append(key)

        for key in expired_keys:
            del self._active_locks[key]
            logger.warning(f"Cleaned up expired lock for: {key}")

    @contextmanager
    def exclusive_lock(
        self, file_path: Union[str, Path], timeout: Optional[float] = None
    ):
        """
        Context manager for exclusive file locking.

        Args:
            file_path: Path to the file to lock
            timeout: Maximum time to wait for lock (seconds)
        """
        lock_key = self._get_lock_key(file_path)
        start_time = time.time()

        with self._lock:
            # Clean up expired locks
            self._cleanup_expired_locks()

            # Wait for lock acquisition
            while lock_key in self._active_locks:
                if timeout and time.time() - start_time > timeout:
                    raise TimeoutError(
                        f"Could not acquire exclusive lock for {file_path} within {timeout} seconds"
                    )

                # Check if existing lock is expired
                existing_lock = self._active_locks[lock_key]
                if self._is_lock_expired(existing_lock):
                    logger.warning(f"Removing expired lock for {file_path}")
                    del self._active_locks[lock_key]
                    break

                time.sleep(0.1)  # Small delay to prevent busy waiting

            # Acquire the lock
            lock_info = FileLockInfo(
                file_path=str(file_path),
                lock_type="exclusive",
                acquired_at=time.time(),
                acquired_by=threading.current_thread().name,
                timeout=timeout or self._lock_timeout,
            )
            self._active_locks[lock_key] = lock_info

        try:
            logger.debug(f"Acquired exclusive lock for: {file_path}")
            yield file_path
        finally:
            with self._lock:
                if lock_key in self._active_locks:
                    del self._active_locks[lock_key]
                    logger.debug(f"Released exclusive lock for: {file_path}")

    @contextmanager
    def shared_lock(self, file_path: Union[str, Path], timeout: Optional[float] = None):
        """
        Context manager for shared file locking.

        Args:
            file_path: Path to the file to lock
            timeout: Maximum time to wait for lock (seconds)
        """
        lock_key = self._get_lock_key(file_path)
        start_time = time.time()

        with self._lock:
            # Clean up expired locks
            self._cleanup_expired_locks()

            # Wait for lock acquisition (allow multiple shared locks)
            while lock_key in self._active_locks:
                existing_lock = self._active_locks[lock_key]
                if existing_lock.lock_type == "exclusive":
                    if timeout and time.time() - start_time > timeout:
                        raise TimeoutError(
                            f"Could not acquire shared lock for {file_path} within {timeout} seconds"
                        )

                    # Check if existing lock is expired
                    if self._is_lock_expired(existing_lock):
                        logger.warning(
                            f"Removing expired exclusive lock for {file_path}"
                        )
                        del self._active_locks[lock_key]
                        break

                    time.sleep(0.1)  # Small delay to prevent busy waiting

            # Acquire the lock
            lock_info = FileLockInfo(
                file_path=str(file_path),
                lock_type="shared",
                acquired_at=time.time(),
                acquired_by=threading.current_thread().name,
                timeout=timeout or self._lock_timeout,
            )
            self._active_locks[lock_key] = lock_info

        try:
            logger.debug(f"Acquired shared lock for: {file_path}")
            yield file_path
        finally:
            with self._lock:
                if lock_key in self._active_locks:
                    del self._active_locks[lock_key]
                    logger.debug(f"Released shared lock for: {file_path}")

    def is_locked(self, file_path: Union[str, Path]) -> bool:
        """Check if a file is currently locked"""
        lock_key = self._get_lock_key(file_path)
        with self._lock:
            self._cleanup_expired_locks()
            return lock_key in self._active_locks

    def get_lock_info(self, file_path: Union[str, Path]) -> Optional[FileLockInfo]:
        """Get information about the current lock on a file"""
        lock_key = self._get_lock_key(file_path)
        with self._lock:
            self._cleanup_expired_locks()
            return self._active_locks.get(lock_key)

    def get_all_locks(self) -> Dict[str, FileLockInfo]:
        """Get information about all active locks"""
        with self._lock:
            self._cleanup_expired_locks()
            return self._active_locks.copy()

    def clear_all_locks(self) -> None:
        """Clear all active locks (use with caution)"""
        with self._lock:
            self._active_locks.clear()
            logger.warning("All file locks have been cleared")


# Async version for async operations
class AsyncFileLockManager:
    """
    Asynchronous file locking manager for async operations.
    """

    def __init__(self):
        self._sync_manager = FileLockManager()
        self._async_lock = asyncio.Lock()

    async def exclusive_lock(
        self, file_path: Union[str, Path], timeout: Optional[float] = None
    ):
        """Async context manager for exclusive file locking"""
        async with self._async_lock:
            # Use the sync manager within an executor for file operations
            loop = asyncio.get_event_loop()
            with self._sync_manager.exclusive_lock(file_path, timeout):
                yield file_path

    async def shared_lock(
        self, file_path: Union[str, Path], timeout: Optional[float] = None
    ):
        """Async context manager for shared file locking"""
        async with self._async_lock:
            loop = asyncio.get_event_loop()
            with self._sync_manager.shared_lock(file_path, timeout):
                yield file_path

    def is_locked(self, file_path: Union[str, Path]) -> bool:
        """Check if a file is currently locked"""
        return self._sync_manager.is_locked(file_path)

    def get_lock_info(self, file_path: Union[str, Path]) -> Optional[FileLockInfo]:
        """Get information about the current lock on a file"""
        return self._sync_manager.get_lock_info(file_path)

    def get_all_locks(self) -> Dict[str, FileLockInfo]:
        """Get information about all active locks"""
        return self._sync_manager.get_all_locks()

    def clear_all_locks(self) -> None:
        """Clear all active locks (use with caution)"""
        self._sync_manager.clear_all_locks()


# Global instances
_file_lock_manager = FileLockManager()
_async_file_lock_manager = AsyncFileLockManager()


def get_file_lock_manager() -> FileLockManager:
    """Get the global file lock manager instance"""
    return _file_lock_manager


def get_async_file_lock_manager() -> AsyncFileLockManager:
    """Get the global async file lock manager instance"""
    return _async_file_lock_manager


# Convenience functions for common operations
@contextmanager
def locked_file_write(
    file_path: Union[str, Path], content: str, timeout: Optional[float] = None
):
    """
    Convenience function for safely writing to a file with locking.

    Args:
        file_path: Path to the file
        content: Content to write
        timeout: Lock timeout in seconds
    """
    with get_file_lock_manager().exclusive_lock(file_path, timeout):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)


@contextmanager
def locked_file_read(file_path: Union[str, Path], timeout: Optional[float] = None):
    """
    Convenience function for safely reading from a file with locking.

    Args:
        file_path: Path to the file
        timeout: Lock timeout in seconds

    Yields:
        File content as string
    """
    with get_file_lock_manager().shared_lock(file_path, timeout):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        yield content


async def async_locked_file_write(
    file_path: Union[str, Path], content: str, timeout: Optional[float] = None
):
    """
    Async convenience function for safely writing to a file with locking.

    Args:
        file_path: Path to the file
        content: Content to write
        timeout: Lock timeout in seconds
    """
    async with get_async_file_lock_manager().exclusive_lock(file_path, timeout):
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(content)


async def async_locked_file_read(
    file_path: Union[str, Path], timeout: Optional[float] = None
):
    """
    Async convenience function for safely reading from a file with locking.

    Args:
        file_path: Path to the file
        timeout: Lock timeout in seconds

    Returns:
        File content as string
    """
    async with get_async_file_lock_manager().shared_lock(file_path, timeout):
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            content = await f.read()
        return content


# Example usage and testing
if __name__ == "__main__":
    import os
    import tempfile

    # Test synchronous locking
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        test_file = f.name

    try:
        # Test exclusive lock
        with get_file_lock_manager().exclusive_lock(test_file):
            print("Acquired exclusive lock")

            # Test shared lock
            with get_file_lock_manager().shared_lock(test_file):
                print("Acquired shared lock")

        print("All locks released successfully")

        # Test convenience functions
        locked_file_write(test_file, "Test content")
        print("File written with locking")

        content = locked_file_read(test_file)
        print(f"File read with locking: {content}")

    finally:
        os.unlink(test_file)
