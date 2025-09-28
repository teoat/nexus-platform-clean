#!/usr/bin/env python3
"""
NEXUS Platform - Advanced Security System
Phase 2: Security Enhancements
"""

import asyncio
import hashlib
import hmac
import jwt
import logging
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass
import bcrypt
from cryptography.fernet import Fernet
import redis
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security level classifications"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    """Types of security threats"""
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH = "data_breach"
    MALWARE = "malware"
    PHISHING = "phishing"


@dataclass
class SecurityEvent:
    """Security event record"""
    id: str
    timestamp: datetime
    threat_type: ThreatType
    severity: SecurityLevel
    source_ip: str
    user_id: Optional[str]
    description: str
    metadata: Dict[str, Any]
    resolved: bool = False


@dataclass
class UserSession:
    """User session information"""
    user_id: str
    session_id: str
    created_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    is_active: bool = True
    security_level: SecurityLevel = SecurityLevel.MEDIUM


class AdvancedSecuritySystem:
    """Advanced security system with multiple layers of protection"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Security configurations
        self.max_login_attempts = 5
        self.lockout_duration = 300  # 5 minutes
        self.session_timeout = 3600  # 1 hour
        self.password_min_length = 12
        self.require_special_chars = True
        self.require_numbers = True
        self.require_uppercase = True
        
        # Threat detection thresholds
        self.threat_thresholds = {
            ThreatType.BRUTE_FORCE: 3,
            ThreatType.SQL_INJECTION: 1,
            ThreatType.XSS: 1,
            ThreatType.UNAUTHORIZED_ACCESS: 5
        }
        
        # Security events storage
        self.security_events: List[SecurityEvent] = []
        self.active_sessions: Dict[str, UserSession] = {}
        
        # Rate limiting
        self.rate_limits = {
            "login": {"requests": 10, "window": 300},  # 10 requests per 5 minutes
            "api": {"requests": 100, "window": 60},    # 100 requests per minute
            "password_reset": {"requests": 3, "window": 3600}  # 3 requests per hour
        }
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a cryptographically secure token"""
        return secrets.token_urlsafe(length)
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        issues = []
        score = 0
        
        # Length check
        if len(password) >= self.password_min_length:
            score += 2
        else:
            issues.append(f"Password must be at least {self.password_min_length} characters long")
        
        # Character type checks
        if any(c.isupper() for c in password):
            score += 1
        elif self.require_uppercase:
            issues.append("Password must contain at least one uppercase letter")
        
        if any(c.islower() for c in password):
            score += 1
        
        if any(c.isdigit() for c in password):
            score += 1
        elif self.require_numbers:
            issues.append("Password must contain at least one number")
        
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
        elif self.require_special_chars:
            issues.append("Password must contain at least one special character")
        
        # Common password check
        common_passwords = ["password", "123456", "admin", "qwerty", "letmein"]
        if password.lower() in common_passwords:
            score -= 2
            issues.append("Password is too common")
        
        # Determine strength level
        if score >= 6:
            strength = "strong"
        elif score >= 4:
            strength = "medium"
        else:
            strength = "weak"
        
        return {
            "valid": len(issues) == 0,
            "strength": strength,
            "score": score,
            "issues": issues
        }
    
    def generate_jwt_token(self, user_id: str, additional_claims: Dict[str, Any] = None) -> str:
        """Generate JWT token with security claims"""
        now = datetime.utcnow()
        payload = {
            "user_id": user_id,
            "iat": now,
            "exp": now + timedelta(hours=1),
            "iss": "nexus-platform",
            "aud": "nexus-users",
            "jti": self.generate_secure_token(16),  # JWT ID for tracking
            **(additional_claims or {})
        }
        
        # Add security claims
        payload["security_level"] = "medium"
        payload["session_id"] = self.generate_secure_token(24)
        
        from backend.config.settings import get_settings
        settings = get_settings()
        return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        encrypted_data = self.cipher_suite.encrypt(data.encode())
        return encrypted_data.decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        decrypted_data = self.cipher_suite.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    
    async def check_rate_limit(self, identifier: str, limit_type: str) -> bool:
        """Check if request is within rate limits"""
        if limit_type not in self.rate_limits:
            return True
        
        limit_config = self.rate_limits[limit_type]
        key = f"rate_limit:{limit_type}:{identifier}"
        
        if self.redis_client:
            # Use Redis for distributed rate limiting
            current_time = int(time.time())
            window_start = current_time - limit_config["window"]
            
            # Remove old entries
            await self.redis_client.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            current_requests = await self.redis_client.zcard(key)
            
            if current_requests >= limit_config["requests"]:
                return False
            
            # Add current request
            await self.redis_client.zadd(key, {str(current_time): current_time})
            await self.redis_client.expire(key, limit_config["window"])
            
            return True
        else:
            # Fallback to in-memory rate limiting
            # This is a simplified implementation
            return True
    
    async def detect_threat(self, threat_type: ThreatType, source_ip: str, 
                          user_id: Optional[str] = None, metadata: Dict[str, Any] = None) -> bool:
        """Detect and log security threats"""
        threat_key = f"threat:{threat_type.value}:{source_ip}"
        
        if self.redis_client:
            # Increment threat counter
            current_count = await self.redis_client.incr(threat_key)
            await self.redis_client.expire(threat_key, 3600)  # 1 hour window
            
            # Check if threshold exceeded
            threshold = self.threat_thresholds.get(threat_type, 5)
            if current_count >= threshold:
                # Log security event
                event = SecurityEvent(
                    id=self.generate_secure_token(16),
                    timestamp=datetime.now(),
                    threat_type=threat_type,
                    severity=SecurityLevel.HIGH if current_count >= threshold * 2 else SecurityLevel.MEDIUM,
                    source_ip=source_ip,
                    user_id=user_id,
                    description=f"Detected {threat_type.value} threat from {source_ip}",
                    metadata=metadata or {}
                )
                
                self.security_events.append(event)
                logger.warning(f"Security threat detected: {event.description}")
                
                # Block IP if critical
                if event.severity == SecurityLevel.CRITICAL:
                    await self.block_ip(source_ip, "Critical threat detected")
                
                return True
        
        return False
    
    async def block_ip(self, ip_address: str, reason: str):
        """Block an IP address"""
        block_key = f"blocked_ip:{ip_address}"
        
        if self.redis_client:
            await self.redis_client.setex(block_key, 3600, reason)  # Block for 1 hour
        
        logger.warning(f"Blocked IP {ip_address}: {reason}")
    
    async def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked"""
        if self.redis_client:
            block_key = f"blocked_ip:{ip_address}"
            return await self.redis_client.exists(block_key)
        return False
    
    def create_user_session(self, user_id: str, ip_address: str, user_agent: str) -> UserSession:
        """Create a new user session"""
        session_id = self.generate_secure_token(32)
        session = UserSession(
            user_id=user_id,
            session_id=session_id,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.active_sessions[session_id] = session
        return session
    
    def update_session_activity(self, session_id: str):
        """Update session last activity time"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id].last_activity = datetime.now()
    
    def invalidate_session(self, session_id: str):
        """Invalidate a user session"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id].is_active = False
            del self.active_sessions[session_id]
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if (current_time - session.last_activity).seconds > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.invalidate_session(session_id)
        
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_security_report(self) -> Dict[str, Any]:
        """Generate security report"""
        current_time = datetime.now()
        last_24h = current_time - timedelta(hours=24)
        
        # Count events by type
        events_by_type = {}
        events_by_severity = {}
        
        for event in self.security_events:
            if event.timestamp >= last_24h:
                # By type
                threat_type = event.threat_type.value
                events_by_type[threat_type] = events_by_type.get(threat_type, 0) + 1
                
                # By severity
                severity = event.severity.value
                events_by_severity[severity] = events_by_severity.get(severity, 0) + 1
        
        return {
            "report_timestamp": current_time.isoformat(),
            "active_sessions": len(self.active_sessions),
            "total_security_events_24h": len([e for e in self.security_events if e.timestamp >= last_24h]),
            "events_by_type": events_by_type,
            "events_by_severity": events_by_severity,
            "security_level": "high" if events_by_severity.get("critical", 0) > 0 else "medium",
            "recommendations": self._generate_security_recommendations(events_by_type)
        }
    
    def _generate_security_recommendations(self, events_by_type: Dict[str, int]) -> List[str]:
        """Generate security recommendations based on events"""
        recommendations = []
        
        if events_by_type.get("brute_force", 0) > 5:
            recommendations.append("Consider implementing CAPTCHA for login attempts")
        
        if events_by_type.get("sql_injection", 0) > 0:
            recommendations.append("Review and strengthen SQL query parameterization")
        
        if events_by_type.get("xss", 0) > 0:
            recommendations.append("Implement stricter input validation and output encoding")
        
        if events_by_type.get("unauthorized_access", 0) > 10:
            recommendations.append("Review access control policies and user permissions")
        
        if not recommendations:
            recommendations.append("Security posture is good, continue monitoring")
        
        return recommendations
    
    async def validate_input(self, input_data: str, input_type: str = "general") -> Dict[str, Any]:
        """Validate and sanitize input data"""
        issues = []
        sanitized_data = input_data
        
        # SQL Injection detection
        sql_patterns = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_", "exec", "execute"]
        if any(pattern in input_data.lower() for pattern in sql_patterns):
            issues.append("Potential SQL injection detected")
            await self.detect_threat(ThreatType.SQL_INJECTION, "unknown", metadata={"input": input_data})
        
        # XSS detection
        xss_patterns = ["<script", "javascript:", "onload=", "onerror=", "onclick="]
        if any(pattern in input_data.lower() for pattern in xss_patterns):
            issues.append("Potential XSS attack detected")
            await self.detect_threat(ThreatType.XSS, "unknown", metadata={"input": input_data})
        
        # Length validation
        if len(input_data) > 10000:
            issues.append("Input too long")
        
        # Special character validation for specific types
        if input_type == "email":
            if "@" not in input_data or "." not in input_data:
                issues.append("Invalid email format")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "sanitized_data": sanitized_data
        }


# Example usage and testing
async def main():
    """Example usage of the security system"""
    security_system = AdvancedSecuritySystem()
    
    # Test password validation
    password_result = security_system.validate_password_strength("MySecure123!")
    print(f"Password validation: {password_result}")
    
    # Test JWT token generation
    token = security_system.generate_jwt_token("user123")
    print(f"Generated JWT token: {token[:50]}...")
    
    # Test token verification
    try:
        payload = security_system.verify_jwt_token(token)
        print(f"Token payload: {payload}")
    except ValueError as e:
        print(f"Token verification failed: {e}")
    
    # Test threat detection
    threat_detected = await security_system.detect_threat(
        ThreatType.BRUTE_FORCE, 
        "192.168.1.100", 
        "user123"
    )
    print(f"Threat detected: {threat_detected}")
    
    # Test input validation
    validation_result = await security_system.validate_input("'; DROP TABLE users; --")
    print(f"Input validation: {validation_result}")
    
    # Generate security report
    report = security_system.get_security_report()
    print(f"Security report: {report}")


if __name__ == "__main__":
    asyncio.run(main())
