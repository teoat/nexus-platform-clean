#!/usr/bin/env python3
"""
NEXUS Ultimate Centralized (NUC) Single Source of Truth (SSOT) Manager
Manages SSOT across all system components with drift detection and auto-sync
"""

import asyncio
import hashlib
import json
import logging
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import aiofiles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SSOTType(Enum):
    """Types of SSOT data"""

    CONFIGURATION = "configuration"
    USER_DATA = "user_data"
    SYSTEM_STATE = "system_state"
    TASK_DATA = "task_data"
    DOCUMENTATION = "documentation"
    METADATA = "metadata"


class SyncStatus(Enum):
    """Synchronization status"""

    SYNCED = "synced"
    DRIFT_DETECTED = "drift_detected"
    CONFLICT = "conflict"
    PENDING = "pending"
    ERROR = "error"


@dataclass
class SSOTRecord:
    """SSOT record structure"""

    id: str
    type: SSOTType
    key: str
    value: Any
    version: int
    checksum: str
    created_at: datetime
    updated_at: datetime
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyncEvent:
    """Synchronization event"""

    id: str
    record_id: str
    action: str  # create, update, delete, sync
    timestamp: datetime
    source: str
    status: SyncStatus
    details: Dict[str, Any] = field(default_factory=dict)


class SSOTManager:
    """Single Source of Truth Manager with drift detection and auto-sync"""

    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        self.base_path = Path(base_path)
        self.db_path = self.base_path / "data" / "ssot.db"
        self.records: Dict[str, SSOTRecord] = {}
        self.sync_events: List[SyncEvent] = []
        self.drift_detection_active = True
        self.auto_sync_active = True
        self.sync_interval = 30  # seconds

        # Statistics
        self.stats = {
            "total_records": 0,
            "synced_records": 0,
            "drift_detected": 0,
            "conflicts_resolved": 0,
            "sync_errors": 0,
        }

        # Initialize database
        self._init_database()

        # Start background tasks
        self._start_background_tasks()

    def _init_database(self):
        """Initialize SSOT database"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Create tables
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ssot_records (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                version INTEGER NOT NULL,
                checksum TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                source TEXT NOT NULL,
                metadata TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sync_events (
                id TEXT PRIMARY KEY,
                record_id TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                source TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT
            )
        """
        )

        conn.commit()
        conn.close()

    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        asyncio.create_task(self._drift_detector())
        asyncio.create_task(self._auto_sync())
        asyncio.create_task(self._cleanup_old_events())

    async def create_record(
        self,
        record_id: str,
        ssot_type: SSOTType,
        key: str,
        value: Any,
        source: str,
        metadata: Dict[str, Any] = None,
    ) -> SSOTRecord:
        """Create a new SSOT record"""
        # Calculate checksum
        value_str = (
            json.dumps(value, sort_keys=True) if not isinstance(value, str) else value
        )
        checksum = hashlib.md5(value_str.encode()).hexdigest()

        record = SSOTRecord(
            id=record_id,
            type=ssot_type,
            key=key,
            value=value,
            version=1,
            checksum=checksum,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            source=source,
            metadata=metadata or {},
        )

        # Store in memory
        self.records[record_id] = record

        # Store in database
        await self._store_record(record)

        # Log sync event
        await self._log_sync_event(record_id, "create", source, SyncStatus.SYNCED)

        self.stats["total_records"] += 1
        logger.info(f"Created SSOT record: {record_id} ({ssot_type.value})")

        return record

    async def update_record(
        self, record_id: str, value: Any, source: str
    ) -> Optional[SSOTRecord]:
        """Update an existing SSOT record"""
        if record_id not in self.records:
            logger.warning(f"Record {record_id} not found for update")
            return None

        record = self.records[record_id]

        # Calculate new checksum
        value_str = (
            json.dumps(value, sort_keys=True) if not isinstance(value, str) else value
        )
        new_checksum = hashlib.md5(value_str.encode()).hexdigest()

        # Check for drift
        if record.checksum != new_checksum:
            # Update record
            record.value = value
            record.version += 1
            record.checksum = new_checksum
            record.updated_at = datetime.now()
            record.source = source

            # Store in database
            await self._store_record(record)

            # Log sync event
            await self._log_sync_event(record_id, "update", source, SyncStatus.SYNCED)

            logger.info(f"Updated SSOT record: {record_id} (version {record.version})")
            return record

        return record

    async def get_record(self, record_id: str) -> Optional[SSOTRecord]:
        """Get an SSOT record by ID"""
        return self.records.get(record_id)

    async def get_records_by_type(self, ssot_type: SSOTType) -> List[SSOTRecord]:
        """Get all records of a specific type"""
        return [record for record in self.records.values() if record.type == ssot_type]

    async def get_records_by_key(self, key: str) -> List[SSOTRecord]:
        """Get all records with a specific key"""
        return [record for record in self.records.values() if record.key == key]

    async def delete_record(self, record_id: str, source: str) -> bool:
        """Delete an SSOT record"""
        if record_id not in self.records:
            logger.warning(f"Record {record_id} not found for deletion")
            return False

        # Remove from memory
        del self.records[record_id]

        # Remove from database
        await self._delete_record_from_db(record_id)

        # Log sync event
        await self._log_sync_event(record_id, "delete", source, SyncStatus.SYNCED)

        logger.info(f"Deleted SSOT record: {record_id}")
        return True

    async def _store_record(self, record: SSOTRecord):
        """Store record in database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO ssot_records
            (id, type, key, value, version, checksum, created_at, updated_at, source, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                record.id,
                record.type.value,
                record.key,
                json.dumps(record.value),
                record.version,
                record.checksum,
                record.created_at.isoformat(),
                record.updated_at.isoformat(),
                record.source,
                json.dumps(record.metadata),
            ),
        )

        conn.commit()
        conn.close()

    async def _delete_record_from_db(self, record_id: str):
        """Delete record from database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("DELETE FROM ssot_records WHERE id = ?", (record_id,))

        conn.commit()
        conn.close()

    async def _log_sync_event(
        self,
        record_id: str,
        action: str,
        source: str,
        status: SyncStatus,
        details: Dict[str, Any] = None,
    ):
        """Log a synchronization event"""
        event = SyncEvent(
            id=f"{record_id}_{int(time.time())}",
            record_id=record_id,
            action=action,
            timestamp=datetime.now(),
            source=source,
            status=status,
            details=details or {},
        )

        self.sync_events.append(event)

        # Store in database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO sync_events
            (id, record_id, action, timestamp, source, status, details)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                event.id,
                event.record_id,
                event.action,
                event.timestamp.isoformat(),
                event.source,
                event.status.value,
                json.dumps(event.details),
            ),
        )

        conn.commit()
        conn.close()

    async def _drift_detector(self):
        """Background task to detect drift in SSOT records"""
        while True:
            try:
                if self.drift_detection_active:
                    await self._detect_drift()
                await asyncio.sleep(10)  # Check every 10 seconds
            except Exception as e:
                logger.error(f"Error in drift detector: {e}")
                await asyncio.sleep(30)

    async def _detect_drift(self):
        """Detect drift in SSOT records"""
        # In a real implementation, this would compare records across different sources
        # For now, we'll simulate drift detection
        current_time = datetime.now()

        for record in self.records.values():
            # Check if record is stale (older than 1 hour)
            if (current_time - record.updated_at).total_seconds() > 3600:
                logger.warning(f"Potential drift detected in record: {record.id}")
                self.stats["drift_detected"] += 1

                # Log drift event
                await self._log_sync_event(
                    record.id,
                    "drift_detected",
                    "system",
                    SyncStatus.DRIFT_DETECTED,
                    {"last_update": record.updated_at.isoformat()},
                )

    async def _auto_sync(self):
        """Background task for automatic synchronization"""
        while True:
            try:
                if self.auto_sync_active:
                    await self._sync_all_records()
                await asyncio.sleep(self.sync_interval)
            except Exception as e:
                logger.error(f"Error in auto sync: {e}")
                await asyncio.sleep(60)

    async def _sync_all_records(self):
        """Synchronize all records"""
        # In a real implementation, this would sync with external sources
        # For now, we'll just log the sync attempt
        logger.info(f"Auto-sync: {len(self.records)} records")
        self.stats["synced_records"] += len(self.records)

    async def _cleanup_old_events(self):
        """Clean up old sync events"""
        while True:
            try:
                # Keep only last 1000 events
                if len(self.sync_events) > 1000:
                    self.sync_events = self.sync_events[-1000:]

                await asyncio.sleep(300)  # Cleanup every 5 minutes
            except Exception as e:
                logger.error(f"Error in cleanup: {e}")
                await asyncio.sleep(600)

    def get_status(self) -> Dict[str, Any]:
        """Get SSOT manager status"""
        return {
            "total_records": len(self.records),
            "records_by_type": {
                ssot_type.value: len(
                    [r for r in self.records.values() if r.type == ssot_type]
                )
                for ssot_type in SSOTType
            },
            "stats": self.stats,
            "drift_detection": self.drift_detection_active,
            "auto_sync": self.auto_sync_active,
            "sync_interval": self.sync_interval,
        }

    def get_sync_events(self, limit: int = 100) -> List[SyncEvent]:
        """Get recent sync events"""
        return self.sync_events[-limit:] if self.sync_events else []

    async def export_records(self, file_path: str):
        """Export all records to a file"""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "records": [
                {
                    "id": record.id,
                    "type": record.type.value,
                    "key": record.key,
                    "value": record.value,
                    "version": record.version,
                    "checksum": record.checksum,
                    "created_at": record.created_at.isoformat(),
                    "updated_at": record.updated_at.isoformat(),
                    "source": record.source,
                    "metadata": record.metadata,
                }
                for record in self.records.values()
            ],
        }

        async with aiofiles.open(file_path, "w") as f:
            await f.write(json.dumps(export_data, indent=2))

        logger.info(f"Exported {len(self.records)} records to {file_path}")


async def main():
    """Main entry point for testing"""
    ssot_manager = SSOTManager()

    try:
        # Test creating records
        record1 = await ssot_manager.create_record(
            "test_config_1",
            SSOTType.CONFIGURATION,
            "database_url",
            "postgresql://localhost:5432/nexus",
            "system",
        )

        record2 = await ssot_manager.create_record(
            "test_user_1",
            SSOTType.USER_DATA,
            "user_preferences",
            {"theme": "dark", "language": "en"},
            "user_service",
        )

        # Test updating record
        await ssot_manager.update_record(
            "test_config_1", "postgresql://localhost:5432/nexus_prod", "config_service"
        )

        # Show status
        status = ssot_manager.get_status()
        print(f"SSOT Status: {json.dumps(status, indent=2)}")

        # Show sync events
        events = ssot_manager.get_sync_events(10)
        print(f"Recent events: {len(events)}")

    except Exception as e:
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
