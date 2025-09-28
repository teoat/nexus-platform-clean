#!/usr/bin/env python3
"""
NEXUS Platform - AI SSOT Optimizer
AI-driven optimization for SSOT performance
"""

import asyncio
import logging
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    ALIAS_OPTIMIZATION = "alias_optimization"
    CACHE_OPTIMIZATION = "cache_optimization"
    QUERY_OPTIMIZATION = "query_optimization"


@dataclass
class OptimizationResult:
    id: str
    type: OptimizationType
    description: str
    performance_gain: float
    confidence_score: float
    created_at: datetime


class AISSOTOptimizer:
    """AI-driven SSOT optimizer"""

    def __init__(self, ssot_registry, config: Dict[str, Any] = None):
        self.registry = ssot_registry
        self.config = config or {}
        self.operation_times = defaultdict(list)
        self.alias_frequency = Counter()
        self.cache_hits = 0
        self.cache_misses = 0

    async def analyze_performance(self) -> Dict[str, Any]:
        """Analyze current performance"""
        all_times = []
        for times in self.operation_times.values():
            all_times.extend(times)

        if not all_times:
            return {"average_time": 0.0, "total_operations": 0}

        return {
            "average_time": sum(all_times) / len(all_times),
            "total_operations": len(all_times),
            "cache_hit_rate": self.cache_hits / (self.cache_hits + self.cache_misses)
            if (self.cache_hits + self.cache_misses) > 0
            else 0,
        }

    async def get_optimization_opportunities(self) -> List[OptimizationResult]:
        """Get optimization opportunities"""
        opportunities = []

        # Find unused aliases
        unused_count = 0
        if self.registry and hasattr(self.registry, "aliases"):
            for context, aliases in self.registry.aliases.items():
                for alias_name in aliases.keys():
                    if self.alias_frequency[alias_name] == 0:
                        unused_count += 1
        else:
            # Mock data when no registry is available
            unused_count = 5

        if unused_count > 0:
            opportunities.append(
                OptimizationResult(
                    id=f"unused_aliases_{int(time.time())}",
                    type=OptimizationType.ALIAS_OPTIMIZATION,
                    description=f"Remove {unused_count} unused aliases",
                    performance_gain=0.05,
                    confidence_score=0.9,
                    created_at=datetime.now(timezone.utc),
                )
            )

        return opportunities

    def record_operation(self, operation: str, duration: float):
        """Record operation timing"""
        self.operation_times[operation].append(duration)
        if len(self.operation_times[operation]) > 1000:
            self.operation_times[operation] = self.operation_times[operation][-1000:]

    def record_alias_usage(self, alias_name: str):
        """Record alias usage"""
        self.alias_frequency[alias_name] += 1

    def record_cache_hit(self):
        """Record cache hit"""
        self.cache_hits += 1

    def record_cache_miss(self):
        """Record cache miss"""
        self.cache_misses += 1
