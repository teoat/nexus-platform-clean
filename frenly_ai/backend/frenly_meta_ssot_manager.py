#!/usr/bin/env python3
"""
Frenly AI SSOT Manager
Single Source of Truth for system events and knowledge
"""

import asyncio
import hashlib
import logging
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

import json  # Added for persistence
import os  # Added for os.path.join


class SSOTManager:
    """Single Source of Truth manager for Frenly AI"""

    def __init__(self):
        self.ssot_index = {}
        self.evidence_links = defaultdict(list)
        self.audit_trail = deque(maxlen=10000)
        self.data_sources = {
            "system_events": deque(maxlen=1000),
            "user_actions": deque(maxlen=1000),
            "api_calls": deque(maxlen=1000),
            "errors": deque(maxlen=1000),
            "performance_metrics": deque(maxlen=1000),
        }
        self.ssot_file = os.path.join(
            os.path.dirname(__file__), "ssot_data.json"
        )  # File for persistence

        # Load existing SSOT data
        self._load_ssot_index()

        # Initialize with default system knowledge if SSOT is empty
        if not self.ssot_index:
            self._initialize_default_knowledge()

    def _save_ssot_index(self):
        """Save SSOT index to a JSON file for persistence"""
        try:
            # Convert deque to list for JSON serialization
            serializable_ssot_index = {}
            for key, value in self.ssot_index.items():
                serializable_ssot_index[key] = value

            with open(self.ssot_file, "w") as f:
                json.dump(serializable_ssot_index, f, indent=2)
            logger.debug(f"SSOT index saved to {self.ssot_file}")
        except Exception as e:
            logger.error(f"Error saving SSOT index: {e}")

    def _load_ssot_index(self):
        """Load SSOT index from a JSON file"""
        if os.path.exists(self.ssot_file):
            try:
                with open(self.ssot_file, "r") as f:
                    self.ssot_index = json.load(f)
                logger.debug(f"SSOT index loaded from {self.ssot_file}")
            except Exception as e:
                logger.error(f"Error loading SSOT index: {e}")
                self.ssot_index = {}  # Reset if loading fails

    def _initialize_default_knowledge(self):
        """Initialize with default system knowledge"""
        default_knowledge = {
            "system_info": {
                "platform": "NEXUS Platform",
                "version": "1.0.0",
                "architecture": "microservices",
                "deployment": "docker",
                "monitoring": "prometheus_grafana",
            },
            "security_policies": {
                "authentication": "JWT with RS256",
                "rate_limiting": "Redis-based sliding window",
                "cors": "restrictive origins",
                "security_headers": "CSP, HSTS, X-Frame-Options",
                "input_validation": "comprehensive sanitization",
            },
            "compliance": {
                "gdpr": "implemented",
                "data_retention": "configurable",
                "audit_logging": "comprehensive",
                "privacy_controls": "user consent management",
            },
            "performance": {
                "caching": "Redis",
                "database": "PostgreSQL with connection pooling",
                "monitoring": "real-time metrics",
                "optimization": "query optimization and indexing",
            },
        }

        for category, data in default_knowledge.items():
            self.ssot_index[category] = {
                "data": data,
                "last_updated": datetime.now().isoformat(),
                "source": "system_initialization",
                "version": "1.0.0",
            }
        self._save_ssot_index()  # Save after initializing default knowledge

    def get(self, key: str, default: Any = None) -> Any:
        """Get data from SSOT"""
        if key in self.ssot_index:
            return self.ssot_index[key]["data"]
        return default

    def set(self, key: str, data: Any, source: str = "unknown") -> bool:
        """Set data in SSOT"""
        try:
            self.ssot_index[key] = {
                "data": data,
                "last_updated": datetime.now().isoformat(),
                "source": source,
                "version": self._generate_version(data),
            }

            # Add to audit trail
            self.audit_trail.append(
                {
                    "action": "set",
                    "key": key,
                    "source": source,
                    "timestamp": datetime.now().isoformat(),
                    "data_hash": self._hash_data(data),
                }
            )

            self._save_ssot_index()  # Save after every set operation

            logger.info(f"SSOT updated: {key} from {source}")
            return True

        except Exception as e:
            logger.error(f"Error updating SSOT: {e}")
            return False

    def link_evidence(
        self,
        event_id: str,
        evidence_type: str,
        evidence_data: Any,
        confidence: float = 1.0,
    ) -> bool:
        """Link evidence to an event"""
        try:
            evidence_entry = {
                "event_id": event_id,
                "evidence_type": evidence_type,
                "evidence_data": evidence_data,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
                "hash": self._hash_data(evidence_data),
            }

            self.evidence_links[event_id].append(evidence_entry)

            # Add to audit trail
            self.audit_trail.append(
                {
                    "action": "link_evidence",
                    "event_id": event_id,
                    "evidence_type": evidence_type,
                    "confidence": confidence,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            logger.info(f"Evidence linked to event {event_id}: {evidence_type}")
            return True

        except Exception as e:
            logger.error(f"Error linking evidence: {e}")
            return False

    def get_evidence(self, event_id: str) -> List[Dict[str, Any]]:
        """Get all evidence for an event"""
        return self.evidence_links.get(event_id, [])

    def add_system_event(
        self, event_type: str, event_data: Any, source: str = "system"
    ) -> str:
        """Add a system event to SSOT"""
        event_id = self._generate_event_id(event_type, event_data)

        event_entry = {
            "event_id": event_id,
            "event_type": event_type,
            "event_data": event_data,
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "hash": self._hash_data(event_data),
        }

        self.data_sources["system_events"].append(event_entry)

        # Add to audit trail
        self.audit_trail.append(
            {
                "action": "add_system_event",
                "event_id": event_id,
                "event_type": event_type,
                "source": source,
                "timestamp": datetime.now().isoformat(),
            }
        )

        logger.info(f"System event added: {event_type} - {event_id}")
        return event_id

    def query_ssot(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Query SSOT data"""
        results = []

        # Search in SSOT index
        for key, data in self.ssot_index.items():
            if (
                query.lower() in key.lower()
                or query.lower() in str(data["data"]).lower()
            ):
                results.append(
                    {
                        "type": "ssot_index",
                        "key": key,
                        "data": data["data"],
                        "last_updated": data["last_updated"],
                        "source": data["source"],
                    }
                )

        # Search in data sources
        for source_name, source_data in self.data_sources.items():
            for entry in source_data:
                if query.lower() in str(entry).lower():
                    results.append(
                        {"type": "data_source", "source": source_name, "data": entry}
                    )

        # Limit results
        return results[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        """Get SSOT statistics"""
        return {
            "ssot_entries": len(self.ssot_index),
            "evidence_links": len(self.evidence_links),
            "audit_entries": len(self.audit_trail),
            "system_events": len(self.data_sources["system_events"]),
            "user_actions": len(self.data_sources["user_actions"]),
            "api_calls": len(self.data_sources["api_calls"]),
            "errors": len(self.data_sources["errors"]),
            "performance_metrics": len(self.data_sources["performance_metrics"]),
            "last_update": datetime.now().isoformat(),
        }

    def _generate_event_id(self, event_type: str, data: Any) -> str:
        """Generate unique event ID"""
        timestamp = datetime.now().isoformat()
        data_str = str(data)
        hash_input = f"{event_type}_{timestamp}_{data_str}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:16]

    def _generate_version(self, data: Any) -> str:
        """Generate version for data"""
        data_str = str(data)
        return hashlib.md5(data_str.encode()).hexdigest()[:8]

    def _hash_data(self, data: Any) -> str:
        """Hash data for integrity checking"""
        data_str = str(data)
        return hashlib.sha256(data_str.encode()).hexdigest()


if __name__ == "__main__":
    # Test SSOT manager
    async def test_ssot_manager():
        ssot = SSOTManager()

        # Test basic operations
        ssot.set("test_key", {"value": "test_data"}, "test_source")
        result = ssot.get("test_key")
        print(f"SSOT get result: {result}")

        # Test event addition
        event_id = ssot.add_system_event("test_event", {"test": "data"})
        print(f"System event ID: {event_id}")

        # Test evidence linking
        ssot.link_evidence(event_id, "log_entry", {"log": "data"}, 0.9)
        evidence = ssot.get_evidence(event_id)
        print(f"Evidence: {evidence}")

        # Test query
        results = ssot.query_ssot("test")
        print(f"Query results: {len(results)} entries")

        # Test statistics
        stats = ssot.get_statistics()
        print(f"Statistics: {stats}")

    asyncio.run(test_ssot_manager())
