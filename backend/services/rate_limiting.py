#!/usr/bin/env python3
"""
NEXUS Platform - Rate Limiting Service
Implements API rate limiting and throttling
"""

import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""

    def __init__(self, retry_after: int, limit: int, window: int):
        self.retry_after = retry_after
        self.limit = limit
        self.window = window
        super().__init__(f"Rate limit exceeded. Retry after {retry_after} seconds")


class RateLimitRule:
    """Represents a rate limiting rule"""

    def __init__(self, requests: int, window_seconds: int, burst: Optional[int] = None):
        self.requests = requests
        self.window_seconds = window_seconds
        self.burst = burst or requests * 2  # Allow burst up to 2x normal rate


class SlidingWindowCounter:
    """Sliding window rate limiter using counter"""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, key: str) -> Tuple[bool, int]:
        """Check if request is allowed for the given key"""
        now = time.time()
        window_start = now - self.window_seconds

        # Remove old requests outside the window
        self.requests[key] = [t for t in self.requests[key] if t > window_start]

        # Check if under limit
        if len(self.requests[key]) < self.max_requests:
            self.requests[key].append(now)
            return True, 0

        # Calculate retry after time
        oldest_request = min(self.requests[key])
        retry_after = int(self.window_seconds - (now - oldest_request))

        return False, max(1, retry_after)

    def get_remaining_requests(self, key: str) -> int:
        """Get remaining requests for the key"""
        now = time.time()
        window_start = now - self.window_seconds
        self.requests[key] = [t for t in self.requests[key] if t > window_start]
        return max(0, self.max_requests - len(self.requests[key]))


class TokenBucketLimiter:
    """Token bucket rate limiter"""

    def __init__(self, rate_per_second: float, burst_size: int):
        self.rate_per_second = rate_per_second
        self.burst_size = burst_size
        self.tokens: Dict[str, float] = defaultdict(lambda: burst_size)
        self.last_update: Dict[str, float] = defaultdict(time.time)

    def is_allowed(self, key: str) -> Tuple[bool, int]:
        """Check if request is allowed using token bucket"""
        now = time.time()
        elapsed = now - self.last_update[key]

        # Add tokens based on elapsed time
        self.tokens[key] = min(
            self.burst_size, self.tokens[key] + elapsed * self.rate_per_second
        )

        self.last_update[key] = now

        if self.tokens[key] >= 1:
            self.tokens[key] -= 1
            return True, 0

        # Calculate retry after time
        tokens_needed = 1 - self.tokens[key]
        retry_after = int(tokens_needed / self.rate_per_second)

        return False, max(1, retry_after)

    def get_remaining_tokens(self, key: str) -> float:
        """Get remaining tokens for the key"""
        now = time.time()
        elapsed = now - self.last_update[key]
        self.tokens[key] = min(
            self.burst_size, self.tokens[key] + elapsed * self.rate_per_second
        )
        self.last_update[key] = now
        return self.tokens[key]


class RateLimitingService:
    """Comprehensive rate limiting service"""

    def __init__(self):
        self.rules: Dict[str, RateLimitRule] = {}
        self.limiters: Dict[str, Any] = {}
        self.exempt_ips: set = set()
        self.exempt_users: set = set()

        # Default rate limits
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Setup default rate limiting rules"""
        # API endpoints
        self.rules["api_general"] = RateLimitRule(
            requests=100, window_seconds=60
        )  # 100 req/min
        self.rules["api_auth"] = RateLimitRule(
            requests=10, window_seconds=60
        )  # 10 req/min for auth
        self.rules["api_admin"] = RateLimitRule(
            requests=50, window_seconds=60
        )  # 50 req/min for admin

        # Create limiters
        for rule_name, rule in self.rules.items():
            self.limiters[rule_name] = SlidingWindowCounter(
                rule.requests, rule.window_seconds
            )

    def add_rule(
        self, name: str, rule: RateLimitRule, algorithm: str = "sliding_window"
    ):
        """Add a rate limiting rule"""
        self.rules[name] = rule

        if algorithm == "sliding_window":
            self.limiters[name] = SlidingWindowCounter(
                rule.requests, rule.window_seconds
            )
        elif algorithm == "token_bucket":
            # Convert to token bucket parameters
            rate_per_second = rule.requests / rule.window_seconds
            self.limiters[name] = TokenBucketLimiter(rate_per_second, rule.burst)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

        logger.info(
            f"Added rate limit rule: {name} ({rule.requests} req/{rule.window_seconds}s)"
        )

    def exempt_ip(self, ip: str):
        """Exempt an IP address from rate limiting"""
        self.exempt_ips.add(ip)
        logger.info(f"Exempted IP from rate limiting: {ip}")

    def exempt_user(self, user_id: str):
        """Exempt a user from rate limiting"""
        self.exempt_users.add(user_id)
        logger.info(f"Exempted user from rate limiting: {user_id}")

    def remove_exemption(self, identifier: str, type_: str = "ip"):
        """Remove an exemption"""
        if type_ == "ip":
            self.exempt_ips.discard(identifier)
        elif type_ == "user":
            self.exempt_users.discard(identifier)
        logger.info(f"Removed {type_} exemption: {identifier}")

    async def check_rate_limit(
        self,
        key: str,
        rule_name: str = "api_general",
        client_ip: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is within rate limits"""
        # Check exemptions
        if client_ip in self.exempt_ips or user_id in self.exempt_users:
            return True, {
                "allowed": True,
                "exempt": True,
                "rule": rule_name,
                "remaining": -1,
                "reset_in": -1,
            }

        # Get the limiter
        if rule_name not in self.limiters:
            logger.warning(f"Rate limit rule not found: {rule_name}, using default")
            rule_name = "api_general"

        limiter = self.limiters[rule_name]
        rule = self.rules[rule_name]

        # Check rate limit
        allowed, retry_after = limiter.is_allowed(key)

        if allowed:
            remaining = (
                limiter.get_remaining_requests(key)
                if hasattr(limiter, "get_remaining_requests")
                else 0
            )
            reset_in = rule.window_seconds
        else:
            remaining = 0
            reset_in = retry_after

        result = {
            "allowed": allowed,
            "exempt": False,
            "rule": rule_name,
            "limit": rule.requests,
            "remaining": remaining,
            "reset_in": reset_in,
            "retry_after": retry_after if not allowed else 0,
        }

        if not allowed:
            logger.warning(f"Rate limit exceeded for key {key} on rule {rule_name}")

        return allowed, result

    def get_rate_limit_headers(self, rate_limit_info: Dict[str, Any]) -> Dict[str, str]:
        """Get rate limit headers for HTTP response"""
        headers = {}

        if rate_limit_info["allowed"]:
            headers["X-RateLimit-Limit"] = str(rate_limit_info["limit"])
            headers["X-RateLimit-Remaining"] = str(rate_limit_info["remaining"])
            headers["X-RateLimit-Reset"] = str(
                int(time.time()) + rate_limit_info["reset_in"]
            )
        else:
            headers["X-RateLimit-Limit"] = str(rate_limit_info["limit"])
            headers["X-RateLimit-Remaining"] = "0"
            headers["X-RateLimit-Reset"] = str(
                int(time.time()) + rate_limit_info["retry_after"]
            )
            headers["Retry-After"] = str(rate_limit_info["retry_after"])

        return headers

    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        stats = {
            "rules": {},
            "exemptions": {
                "ips": len(self.exempt_ips),
                "users": len(self.exempt_users),
            },
            "timestamp": datetime.now().isoformat(),
        }

        for rule_name, rule in self.rules.items():
            limiter = self.limiters[rule_name]
            if hasattr(limiter, "requests"):
                # Sliding window stats
                total_requests = sum(
                    len(requests) for requests in limiter.requests.values()
                )
                active_keys = len(limiter.requests)
            else:
                # Token bucket stats
                total_requests = 0  # Token bucket doesn't track total requests
                active_keys = len(limiter.tokens)

            stats["rules"][rule_name] = {
                "limit": rule.requests,
                "window_seconds": rule.window_seconds,
                "burst": rule.burst,
                "active_keys": active_keys,
                "total_requests": total_requests,
            }

        return stats

    def cleanup_expired_entries(self, max_age_seconds: int = 3600):
        """Clean up expired rate limiting entries"""
        cutoff_time = time.time() - max_age_seconds

        for limiter in self.limiters.values():
            if hasattr(limiter, "requests"):
                # Clean up sliding window
                for key in list(limiter.requests.keys()):
                    limiter.requests[key] = [
                        t for t in limiter.requests[key] if t > cutoff_time
                    ]
                    if not limiter.requests[key]:
                        del limiter.requests[key]
            elif hasattr(limiter, "last_update"):
                # Clean up token bucket
                for key in list(limiter.last_update.keys()):
                    if limiter.last_update[key] < cutoff_time:
                        del limiter.last_update[key]
                        if key in limiter.tokens:
                            del limiter.tokens[key]

        logger.info("Cleaned up expired rate limiting entries")


# Global instance
rate_limiting = RateLimitingService()
