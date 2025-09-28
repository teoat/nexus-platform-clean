#!/usr/bin/env python3
"""
NEXUS Ultimate Centralized (NUC) Advanced Lock Manager
Distributed locking with timeout, healing, and deadlock detection
"""

import asyncio
import json
import logging
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LockType(Enum):
    """Types of locks"""

    READ = "read"
    WRITE = "write"
    EXCLUSIVE = "exclusive"
    SHARED = "shared"


class LockPriority(Enum):
    """Lock priority levels"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class LockRequest:
    """Lock request information"""

    id: str
    resource: str
    lock_type: LockType
    priority: LockPriority
    requester: str
    timestamp: datetime
    timeout: int = 30
    metadata: Dict[str, Any] = None


@dataclass
class Lock:
    """Active lock information"""

    id: str
    resource: str
    lock_type: LockType
    owner: str
    acquired_at: datetime
    expires_at: datetime
    metadata: Dict[str, Any] = None


class AdvancedLockManager:
    """Advanced distributed lock manager with deadlock detection and healing"""

    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        self.base_path = Path(base_path)
        self.active_locks: Dict[str, Lock] = {}
        self.lock_queue: List[LockRequest] = []
        self.lock_history: List[Dict[str, Any]] = []
        self.deadlock_detection_active = True
        self.healing_active = True

        # Statistics
        self.stats = {
            "locks_granted": 0,
            "locks_released": 0,
            "deadlocks_detected": 0,
            "locks_healed": 0,
            "timeouts": 0,
        }

        # Start background tasks
        self._start_background_tasks()

    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        asyncio.create_task(self._deadlock_detector())
        asyncio.create_task(self._lock_healer())
        asyncio.create_task(self._queue_processor())
        asyncio.create_task(self._cleanup_expired_locks())

    async def acquire_lock(
        self,
        resource: str,
        lock_type: LockType,
        requester: str,
        priority: LockPriority = LockPriority.NORMAL,
        timeout: int = 30,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """Acquire a lock on a resource"""
        lock_id = str(uuid.uuid4())

        request = LockRequest(
            id=lock_id,
            resource=resource,
            lock_type=lock_type,
            priority=priority,
            requester=requester,
            timestamp=datetime.now(),
            timeout=timeout,
            metadata=metadata or {},
        )

        logger.info(f"Lock request: {lock_id} for {resource} by {requester}")

        # Check if lock can be granted immediately
        if await self._can_grant_lock(request):
            return await self._grant_lock(request)
        else:
            # Add to queue
            self.lock_queue.append(request)
            self.lock_queue.sort(
                key=lambda x: (x.priority.value, x.timestamp), reverse=True
            )

            # Wait for lock with timeout
            return await self._wait_for_lock(request)

    async def _can_grant_lock(self, request: LockRequest) -> bool:
        """Check if a lock can be granted immediately"""
        resource = request.resource

        # Check for existing locks on the resource
        existing_locks = [
            lock for lock in self.active_locks.values() if lock.resource == resource
        ]

        if not existing_locks:
            return True

        # Check compatibility
        for existing_lock in existing_locks:
            if not self._are_locks_compatible(
                request.lock_type, existing_lock.lock_type
            ):
                return False

        return True

    def _are_locks_compatible(self, lock_type1: LockType, lock_type2: LockType) -> bool:
        """Check if two lock types are compatible"""
        compatibility_matrix = {
            LockType.READ: {
                LockType.READ: True,
                LockType.SHARED: True,
                LockType.WRITE: False,
                LockType.EXCLUSIVE: False,
            },
            LockType.WRITE: {
                LockType.READ: False,
                LockType.SHARED: False,
                LockType.WRITE: False,
                LockType.EXCLUSIVE: False,
            },
            LockType.SHARED: {
                LockType.READ: True,
                LockType.SHARED: True,
                LockType.WRITE: False,
                LockType.EXCLUSIVE: False,
            },
            LockType.EXCLUSIVE: {
                LockType.READ: False,
                LockType.SHARED: False,
                LockType.WRITE: False,
                LockType.EXCLUSIVE: False,
            },
        }

        return compatibility_matrix.get(lock_type1, {}).get(lock_type2, False)

    async def _grant_lock(self, request: LockRequest) -> str:
        """Grant a lock to a requester"""
        lock = Lock(
            id=request.id,
            resource=request.resource,
            lock_type=request.lock_type,
            owner=request.requester,
            acquired_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=request.timeout),
            metadata=request.metadata,
        )

        self.active_locks[request.id] = lock
        self.stats["locks_granted"] += 1

        # Log lock acquisition
        self.lock_history.append(
            {
                "action": "acquired",
                "lock_id": request.id,
                "resource": request.resource,
                "requester": request.requester,
                "timestamp": datetime.now().isoformat(),
            }
        )

        logger.info(
            f"Lock granted: {request.id} for {request.resource} to {request.requester}"
        )
        return request.id

    async def _wait_for_lock(self, request: LockRequest) -> str:
        """Wait for a lock to become available"""
        start_time = time.time()

        while time.time() - start_time < request.timeout:
            # Check if lock can be granted now
            if await self._can_grant_lock(request):
                # Remove from queue
                if request in self.lock_queue:
                    self.lock_queue.remove(request)
                return await self._grant_lock(request)

            # Wait a bit before checking again
            await asyncio.sleep(0.1)

        # Timeout
        self.stats["timeouts"] += 1
        if request in self.lock_queue:
            self.lock_queue.remove(request)

        raise TimeoutError(f"Lock request {request.id} timed out")

    async def release_lock(self, lock_id: str, requester: str) -> bool:
        """Release a lock"""
        if lock_id not in self.active_locks:
            logger.warning(f"Lock {lock_id} not found")
            return False

        lock = self.active_locks[lock_id]

        if lock.owner != requester:
            logger.warning(f"Lock {lock_id} not owned by {requester}")
            return False

        # Remove lock
        del self.active_locks[lock_id]
        self.stats["locks_released"] += 1

        # Log lock release
        self.lock_history.append(
            {
                "action": "released",
                "lock_id": lock_id,
                "resource": lock.resource,
                "requester": requester,
                "timestamp": datetime.now().isoformat(),
            }
        )

        logger.info(f"Lock released: {lock_id} by {requester}")
        return True

    async def _deadlock_detector(self):
        """Background task to detect deadlocks"""
        while True:
            try:
                if self.deadlock_detection_active:
                    await self._detect_deadlocks()
                await asyncio.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logger.error(f"Error in deadlock detector: {e}")
                await asyncio.sleep(10)

    async def _detect_deadlocks(self):
        """Detect potential deadlocks"""
        # Simple deadlock detection based on waiting time
        current_time = datetime.now()

        for request in self.lock_queue:
            wait_time = (current_time - request.timestamp).total_seconds()

            if wait_time > 60:  # Waited more than 1 minute
                logger.warning(
                    f"Potential deadlock detected: {request.id} waiting {wait_time}s"
                )
                self.stats["deadlocks_detected"] += 1

                # In a real implementation, you would implement deadlock resolution
                # For now, we'll just log it

    async def _lock_healer(self):
        """Background task to heal stuck locks"""
        while True:
            try:
                if self.healing_active:
                    await self._heal_stuck_locks()
                await asyncio.sleep(10)  # Check every 10 seconds
            except Exception as e:
                logger.error(f"Error in lock healer: {e}")
                await asyncio.sleep(15)

    async def _heal_stuck_locks(self):
        """Heal stuck or expired locks"""
        current_time = datetime.now()
        locks_to_remove = []

        for lock_id, lock in self.active_locks.items():
            if current_time > lock.expires_at:
                logger.warning(f"Healing expired lock: {lock_id}")
                locks_to_remove.append(lock_id)
                self.stats["locks_healed"] += 1

        for lock_id in locks_to_remove:
            del self.active_locks[lock_id]

    async def _queue_processor(self):
        """Background task to process lock queue"""
        while True:
            try:
                await self._process_lock_queue()
                await asyncio.sleep(1)  # Check every second
            except Exception as e:
                logger.error(f"Error in queue processor: {e}")
                await asyncio.sleep(5)

    async def _process_lock_queue(self):
        """Process pending lock requests"""
        if not self.lock_queue:
            return

        # Process queue in priority order
        for request in self.lock_queue[
            :
        ]:  # Copy to avoid modification during iteration
            if await self._can_grant_lock(request):
                self.lock_queue.remove(request)
                await self._grant_lock(request)

    async def _cleanup_expired_locks(self):
        """Clean up expired locks and old history"""
        while True:
            try:
                await self._cleanup_locks()
                await self._cleanup_history()
                await asyncio.sleep(60)  # Cleanup every minute
            except Exception as e:
                logger.error(f"Error in cleanup: {e}")
                await asyncio.sleep(120)

    async def _cleanup_locks(self):
        """Clean up expired locks"""
        current_time = datetime.now()
        expired_locks = [
            lock_id
            for lock_id, lock in self.active_locks.items()
            if current_time > lock.expires_at
        ]

        for lock_id in expired_locks:
            del self.active_locks[lock_id]
            logger.info(f"Cleaned up expired lock: {lock_id}")

    async def _cleanup_history(self):
        """Clean up old lock history"""
        # Keep only last 1000 entries
        if len(self.lock_history) > 1000:
            self.lock_history = self.lock_history[-1000:]

    def get_status(self) -> Dict[str, Any]:
        """Get lock manager status"""
        return {
            "active_locks": len(self.active_locks),
            "pending_requests": len(self.lock_queue),
            "stats": self.stats,
            "deadlock_detection": self.deadlock_detection_active,
            "healing": self.healing_active,
        }

    def get_locks_for_resource(self, resource: str) -> List[Lock]:
        """Get all locks for a specific resource"""
        return [
            lock for lock in self.active_locks.values() if lock.resource == resource
        ]

    def get_locks_for_owner(self, owner: str) -> List[Lock]:
        """Get all locks for a specific owner"""
        return [lock for lock in self.active_locks.values() if lock.owner == owner]


async def main():
    """Main entry point for testing"""
    lock_manager = AdvancedLockManager()

    try:
        # Test lock acquisition
        lock_id = await lock_manager.acquire_lock(
            "test_resource", LockType.WRITE, "test_owner", LockPriority.HIGH
        )

        print(f"Lock acquired: {lock_id}")

        # Wait a bit
        await asyncio.sleep(2)

        # Release lock
        success = await lock_manager.release_lock(lock_id, "test_owner")
        print(f"Lock released: {success}")

        # Show status
        status = lock_manager.get_status()
        print(f"Status: {json.dumps(status, indent=2)}")

    except Exception as e:
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
