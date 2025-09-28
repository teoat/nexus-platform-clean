#!/usr/bin/env python3
"""
NEXUS Platform - Advanced Security & Compliance Framework
Zero Trust Architecture, Compliance Automation, and Security Monitoring
"""

import asyncio
import json
import logging
import uuid
import hashlib
import hmac
import secrets
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import sqlite3
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import re
import ipaddress
import socket

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComplianceStandard(Enum):
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    SOC_2 = "soc_2"
    NIST = "nist"

class AuditEventType(Enum):
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_ACCESS = "system_access"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_EVENT = "security_event"
    COMPLIANCE_CHECK = "compliance_check"

class ThreatLevel(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityPolicy:
    policy_id: str
    name: str
    description: str
    policy_type: str
    rules: List[Dict[str, Any]]
    compliance_standards: List[ComplianceStandard]
    security_level: SecurityLevel
    enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "system"

@dataclass
class AuditEvent:
    event_id: str
    event_type: AuditEventType
    user_id: Optional[str]
    resource_id: Optional[str]
    action: str
    details: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    success: bool = True
    risk_score: float = 0.0

@dataclass
class SecurityAlert:
    alert_id: str
    threat_level: ThreatLevel
    alert_type: str
    title: str
    description: str
    source: str
    details: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    acknowledged: bool = False
    resolved: bool = False
    assigned_to: Optional[str] = None

@dataclass
class ComplianceCheck:
    check_id: str
    standard: ComplianceStandard
    check_name: str
    description: str
    requirements: List[str]
    status: str
    last_check: datetime
    next_check: datetime
    results: Dict[str, Any] = field(default_factory=dict)
    violations: List[str] = field(default_factory=list)

class ZeroTrustSecurity:
    """Zero Trust Security Framework Implementation"""
    
    def __init__(self, db_path: str = "security.db"):
        self.db_path = db_path
        self.policies: Dict[str, SecurityPolicy] = {}
        self.audit_events: List[AuditEvent] = []
        self.security_alerts: List[SecurityAlert] = []
        self.compliance_checks: Dict[str, ComplianceCheck] = {}
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.jwt_secret = secrets.token_urlsafe(32)
        self.is_running = False
        self._init_database()
        self._load_default_policies()
        self._init_compliance_checks()
    
    def _init_database(self):
        """Initialize SQLite database for security persistence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create security_policies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_policies (
                policy_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                policy_type TEXT NOT NULL,
                rules TEXT NOT NULL,
                compliance_standards TEXT NOT NULL,
                security_level TEXT NOT NULL,
                enabled BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT
            )
        """)
        
        # Create audit_events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                user_id TEXT,
                resource_id TEXT,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT TRUE,
                risk_score REAL DEFAULT 0.0
            )
        """)
        
        # Create security_alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_alerts (
                alert_id TEXT PRIMARY KEY,
                threat_level TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                source TEXT NOT NULL,
                details TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                acknowledged BOOLEAN DEFAULT FALSE,
                resolved BOOLEAN DEFAULT FALSE,
                assigned_to TEXT
            )
        """)
        
        # Create compliance_checks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compliance_checks (
                check_id TEXT PRIMARY KEY,
                standard TEXT NOT NULL,
                check_name TEXT NOT NULL,
                description TEXT NOT NULL,
                requirements TEXT NOT NULL,
                status TEXT NOT NULL,
                last_check TIMESTAMP,
                next_check TIMESTAMP,
                results TEXT,
                violations TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_default_policies(self):
        """Load default security policies"""
        default_policies = [
            {
                "policy_id": "auth_policy_001",
                "name": "Authentication Policy",
                "description": "Multi-factor authentication and session management",
                "policy_type": "authentication",
                "rules": [
                    {"rule": "require_mfa", "enabled": True},
                    {"rule": "session_timeout", "value": 3600},
                    {"rule": "password_complexity", "min_length": 12},
                    {"rule": "account_lockout", "max_attempts": 5}
                ],
                "compliance_standards": [ComplianceStandard.GDPR, ComplianceStandard.SOC_2],
                "security_level": SecurityLevel.HIGH
            },
            {
                "policy_id": "data_policy_001",
                "name": "Data Protection Policy",
                "description": "Data encryption and access control",
                "policy_type": "data_protection",
                "rules": [
                    {"rule": "encrypt_at_rest", "enabled": True},
                    {"rule": "encrypt_in_transit", "enabled": True},
                    {"rule": "data_classification", "enabled": True},
                    {"rule": "access_logging", "enabled": True}
                ],
                "compliance_standards": [ComplianceStandard.GDPR, ComplianceStandard.HIPAA],
                "security_level": SecurityLevel.CRITICAL
            },
            {
                "policy_id": "network_policy_001",
                "name": "Network Security Policy",
                "description": "Network access control and monitoring",
                "policy_type": "network_security",
                "rules": [
                    {"rule": "firewall_enabled", "enabled": True},
                    {"rule": "vpn_required", "enabled": True},
                    {"rule": "network_monitoring", "enabled": True},
                    {"rule": "intrusion_detection", "enabled": True}
                ],
                "compliance_standards": [ComplianceStandard.ISO_27001, ComplianceStandard.NIST],
                "security_level": SecurityLevel.HIGH
            }
        ]
        
        for policy_data in default_policies:
            policy = SecurityPolicy(
                policy_id=policy_data["policy_id"],
                name=policy_data["name"],
                description=policy_data["description"],
                policy_type=policy_data["policy_type"],
                rules=policy_data["rules"],
                compliance_standards=policy_data["compliance_standards"],
                security_level=policy_data["security_level"]
            )
            self.policies[policy.policy_id] = policy
    
    def _init_compliance_checks(self):
        """Initialize compliance checks"""
        compliance_checks = [
            {
                "check_id": "gdpr_data_protection",
                "standard": ComplianceStandard.GDPR,
                "check_name": "GDPR Data Protection",
                "description": "Check GDPR compliance for data protection",
                "requirements": [
                    "Data encryption at rest",
                    "Data encryption in transit",
                    "Access logging enabled",
                    "Data retention policies",
                    "User consent management"
                ],
                "status": "pending",
                "last_check": datetime.now(timezone.utc),
                "next_check": datetime.now(timezone.utc) + timedelta(days=1)
            },
            {
                "check_id": "hipaa_security",
                "standard": ComplianceStandard.HIPAA,
                "check_name": "HIPAA Security Controls",
                "description": "Check HIPAA compliance for healthcare data",
                "requirements": [
                    "Administrative safeguards",
                    "Physical safeguards",
                    "Technical safeguards",
                    "Audit controls",
                    "Access controls"
                ],
                "status": "pending",
                "last_check": datetime.now(timezone.utc),
                "next_check": datetime.now(timezone.utc) + timedelta(days=1)
            },
            {
                "check_id": "pci_dss_payment",
                "standard": ComplianceStandard.PCI_DSS,
                "check_name": "PCI DSS Payment Security",
                "description": "Check PCI DSS compliance for payment data",
                "requirements": [
                    "Secure network architecture",
                    "Cardholder data protection",
                    "Vulnerability management",
                    "Access control measures",
                    "Network monitoring"
                ],
                "status": "pending",
                "last_check": datetime.now(timezone.utc),
                "next_check": datetime.now(timezone.utc) + timedelta(days=1)
            }
        ]
        
        for check_data in compliance_checks:
            check = ComplianceCheck(
                check_id=check_data["check_id"],
                standard=check_data["standard"],
                check_name=check_data["check_name"],
                description=check_data["description"],
                requirements=check_data["requirements"],
                status=check_data["status"],
                last_check=check_data["last_check"],
                next_check=check_data["next_check"]
            )
            self.compliance_checks[check.check_id] = check
    
    async def start(self):
        """Start the security framework"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("Zero Trust Security Framework started")
        
        # Start compliance monitoring
        asyncio.create_task(self._monitor_compliance())
        
        # Start security monitoring
        asyncio.create_task(self._monitor_security())
    
    async def stop(self):
        """Stop the security framework"""
        self.is_running = False
        logger.info("Zero Trust Security Framework stopped")
    
    async def log_audit_event(
        self,
        event_type: AuditEventType,
        action: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Dict[str, Any] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True
    ) -> str:
        """Log an audit event"""
        event_id = str(uuid.uuid4())
        
        # Calculate risk score
        risk_score = await self._calculate_risk_score(event_type, action, details, success)
        
        event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            user_id=user_id,
            resource_id=resource_id,
            action=action,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            risk_score=risk_score
        )
        
        self.audit_events.append(event)
        await self._save_audit_event_to_db(event)
        
        # Check for security alerts
        await self._check_security_alerts(event)
        
        logger.info(f"Audit event logged: {event_id}")
        return event_id
    
    async def _calculate_risk_score(
        self,
        event_type: AuditEventType,
        action: str,
        details: Dict[str, Any],
        success: bool
    ) -> float:
        """Calculate risk score for an event"""
        base_score = 0.0
        
        # Event type risk weights
        event_weights = {
            AuditEventType.AUTHENTICATION: 0.3,
            AuditEventType.AUTHORIZATION: 0.4,
            AuditEventType.DATA_ACCESS: 0.5,
            AuditEventType.DATA_MODIFICATION: 0.7,
            AuditEventType.SYSTEM_ACCESS: 0.6,
            AuditEventType.CONFIGURATION_CHANGE: 0.8,
            AuditEventType.SECURITY_EVENT: 0.9,
            AuditEventType.COMPLIANCE_CHECK: 0.2
        }
        
        base_score += event_weights.get(event_type, 0.5)
        
        # Action-specific risk
        if "failed" in action.lower() or "denied" in action.lower():
            base_score += 0.3
        
        if not success:
            base_score += 0.4
        
        # Time-based risk (off-hours access)
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:
            base_score += 0.2
        
        # IP-based risk
        if details and "ip_address" in details:
            ip_address = details["ip_address"]
            if await self._is_suspicious_ip(ip_address):
                base_score += 0.3
        
        return min(base_score, 1.0)
    
    async def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP address is suspicious"""
        try:
            # Check if IP is in private range (less suspicious)
            ip = ipaddress.ip_address(ip_address)
            if ip.is_private:
                return False
            
            # Check if IP is in known malicious ranges (simplified)
            # In production, this would check against threat intelligence feeds
            suspicious_ranges = [
                "192.0.2.0/24",  # Test network
                "198.51.100.0/24",  # Test network
                "203.0.113.0/24"  # Test network
            ]
            
            for range_str in suspicious_ranges:
                if ip in ipaddress.ip_network(range_str):
                    return True
            
            return False
        except:
            return True  # Invalid IP addresses are suspicious
    
    async def _check_security_alerts(self, event: AuditEvent):
        """Check if event should trigger security alerts"""
        if event.risk_score > 0.7:
            await self._create_security_alert(
                threat_level=ThreatLevel.HIGH,
                alert_type="high_risk_event",
                title=f"High Risk Event: {event.action}",
                description=f"High risk event detected: {event.action} by user {event.user_id}",
                source="audit_monitor",
                details={
                    "event_id": event.event_id,
                    "event_type": event.event_type.value,
                    "risk_score": event.risk_score,
                    "action": event.action,
                    "user_id": event.user_id,
                    "ip_address": event.ip_address
                }
            )
        
        if event.event_type == AuditEventType.AUTHENTICATION and not event.success:
            await self._create_security_alert(
                threat_level=ThreatLevel.MEDIUM,
                alert_type="failed_authentication",
                title="Failed Authentication Attempt",
                description=f"Failed authentication attempt by user {event.user_id}",
                source="auth_monitor",
                details={
                    "event_id": event.event_id,
                    "user_id": event.user_id,
                    "ip_address": event.ip_address,
                    "user_agent": event.user_agent
                }
            )
    
    async def _create_security_alert(
        self,
        threat_level: ThreatLevel,
        alert_type: str,
        title: str,
        description: str,
        source: str,
        details: Dict[str, Any]
    ) -> str:
        """Create a security alert"""
        alert_id = str(uuid.uuid4())
        
        alert = SecurityAlert(
            alert_id=alert_id,
            threat_level=threat_level,
            alert_type=alert_type,
            title=title,
            description=description,
            source=source,
            details=details
        )
        
        self.security_alerts.append(alert)
        await self._save_security_alert_to_db(alert)
        
        logger.warning(f"Security alert created: {alert_id} - {title}")
        return alert_id
    
    async def _monitor_compliance(self):
        """Monitor compliance checks"""
        while self.is_running:
            try:
                for check in self.compliance_checks.values():
                    if datetime.now(timezone.utc) >= check.next_check:
                        await self._run_compliance_check(check)
                
                await asyncio.sleep(3600)  # Check every hour
            except Exception as e:
                logger.error(f"Error monitoring compliance: {e}")
                await asyncio.sleep(3600)
    
    async def _monitor_security(self):
        """Monitor security events"""
        while self.is_running:
            try:
                # Check for patterns in audit events
                await self._analyze_security_patterns()
                
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                logger.error(f"Error monitoring security: {e}")
                await asyncio.sleep(300)
    
    async def _run_compliance_check(self, check: ComplianceCheck):
        """Run a compliance check"""
        try:
            check.last_check = datetime.now(timezone.utc)
            check.next_check = datetime.now(timezone.utc) + timedelta(days=1)
            
            # Simulate compliance check
            violations = []
            results = {}
            
            for requirement in check.requirements:
                # Simulate check result
                is_compliant = await self._check_requirement(requirement)
                results[requirement] = is_compliant
                
                if not is_compliant:
                    violations.append(requirement)
            
            check.results = results
            check.violations = violations
            
            if violations:
                check.status = "non_compliant"
                await self._create_security_alert(
                    threat_level=ThreatLevel.MEDIUM,
                    alert_type="compliance_violation",
                    title=f"Compliance Violation: {check.check_name}",
                    description=f"Compliance violations detected in {check.standard.value}",
                    source="compliance_monitor",
                    details={
                        "check_id": check.check_id,
                        "standard": check.standard.value,
                        "violations": violations
                    }
                )
            else:
                check.status = "compliant"
            
            await self._save_compliance_check_to_db(check)
            
        except Exception as e:
            logger.error(f"Error running compliance check {check.check_id}: {e}")
    
    async def _check_requirement(self, requirement: str) -> bool:
        """Check if a requirement is met"""
        # Simulate requirement checking
        # In production, this would check actual system configurations
        
        if "encryption" in requirement.lower():
            return True  # Assume encryption is enabled
        elif "logging" in requirement.lower():
            return True  # Assume logging is enabled
        elif "access" in requirement.lower():
            return True  # Assume access controls are in place
        else:
            return True  # Default to compliant
    
    async def _analyze_security_patterns(self):
        """Analyze security patterns in audit events"""
        # Look for suspicious patterns
        recent_events = [
            event for event in self.audit_events
            if (datetime.now(timezone.utc) - event.timestamp).total_seconds() < 3600
        ]
        
        # Check for multiple failed authentication attempts
        failed_auth_events = [
            event for event in recent_events
            if event.event_type == AuditEventType.AUTHENTICATION and not event.success
        ]
        
        if len(failed_auth_events) > 5:
            await self._create_security_alert(
                threat_level=ThreatLevel.HIGH,
                alert_type="brute_force_attempt",
                title="Potential Brute Force Attack",
                description=f"Multiple failed authentication attempts detected: {len(failed_auth_events)}",
                source="pattern_analysis",
                details={
                    "failed_attempts": len(failed_auth_events),
                    "time_window": "1 hour"
                }
            )
    
    async def _save_audit_event_to_db(self, event: AuditEvent):
        """Save audit event to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO audit_events 
            (event_id, event_type, user_id, resource_id, action, details, 
             ip_address, user_agent, timestamp, success, risk_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.event_id,
            event.event_type.value,
            event.user_id,
            event.resource_id,
            event.action,
            json.dumps(event.details),
            event.ip_address,
            event.user_agent,
            event.timestamp.isoformat(),
            event.success,
            event.risk_score
        ))
        
        conn.commit()
        conn.close()
    
    async def _save_security_alert_to_db(self, alert: SecurityAlert):
        """Save security alert to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO security_alerts 
            (alert_id, threat_level, alert_type, title, description, source, 
             details, timestamp, acknowledged, resolved, assigned_to)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alert.alert_id,
            alert.threat_level.value,
            alert.alert_type,
            alert.title,
            alert.description,
            alert.source,
            json.dumps(alert.details),
            alert.timestamp.isoformat(),
            alert.acknowledged,
            alert.resolved,
            alert.assigned_to
        ))
        
        conn.commit()
        conn.close()
    
    async def _save_compliance_check_to_db(self, check: ComplianceCheck):
        """Save compliance check to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO compliance_checks 
            (check_id, standard, check_name, description, requirements, status, 
             last_check, next_check, results, violations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            check.check_id,
            check.standard.value,
            check.check_name,
            check.description,
            json.dumps(check.requirements),
            check.status,
            check.last_check.isoformat(),
            check.next_check.isoformat(),
            json.dumps(check.results),
            json.dumps(check.violations)
        ))
        
        conn.commit()
        conn.close()
    
    async def get_security_status(self) -> Dict[str, Any]:
        """Get security framework status"""
        total_policies = len(self.policies)
        enabled_policies = len([p for p in self.policies.values() if p.enabled])
        total_audit_events = len(self.audit_events)
        recent_audit_events = len([
            e for e in self.audit_events
            if (datetime.now(timezone.utc) - e.timestamp).total_seconds() < 3600
        ])
        total_alerts = len(self.security_alerts)
        unacknowledged_alerts = len([a for a in self.security_alerts if not a.acknowledged])
        total_compliance_checks = len(self.compliance_checks)
        compliant_checks = len([c for c in self.compliance_checks.values() if c.status == "compliant"])
        
        return {
            "framework_running": self.is_running,
            "total_policies": total_policies,
            "enabled_policies": enabled_policies,
            "total_audit_events": total_audit_events,
            "recent_audit_events": recent_audit_events,
            "total_alerts": total_alerts,
            "unacknowledged_alerts": unacknowledged_alerts,
            "total_compliance_checks": total_compliance_checks,
            "compliant_checks": compliant_checks,
            "compliance_score": (compliant_checks / total_compliance_checks * 100) if total_compliance_checks > 0 else 0
        }

# Global security framework instance
zero_trust_security = ZeroTrustSecurity()
