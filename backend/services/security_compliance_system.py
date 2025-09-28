#!/usr/bin/env python3
"""
NUC Security & Compliance System
Provides comprehensive security monitoring, access control, and compliance reporting
"""

import asyncio
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import stat

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceStandard(Enum):
    """Compliance standards"""
    GDPR = "gdpr"
    SOX = "sox"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"


@dataclass
class SecurityEvent:
    """Security event record"""
    event_id: str
    timestamp: datetime
    event_type: str
    severity: SecurityLevel
    file_path: str
    user: str
    action: str
    details: Dict[str, Any]
    compliance_tags: List[ComplianceStandard] = field(default_factory=list)


@dataclass
class AccessControlRule:
    """Access control rule"""
    rule_id: str
    name: str
    file_pattern: str
    allowed_users: List[str]
    allowed_actions: List[str]
    security_level: SecurityLevel
    compliance_requirements: List[ComplianceStandard] = field(default_factory=list)
    created_at: datetime
    expires_at: Optional[datetime] = None


@dataclass
class ComplianceReport:
    """Compliance report"""
    report_id: str
    standard: ComplianceStandard
    generated_at: datetime
    compliance_score: float
    violations: List[Dict[str, Any]]
    recommendations: List[str]
    status: str


class SecurityComplianceSystem:
    """Security and Compliance System for NUC Workspace Management"""
    
    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        self.base_path = Path(base_path)
        self.db_path = self.base_path / "data" / "security_compliance.db"
        self.security_events: List[SecurityEvent] = []
        self.access_rules: List[AccessControlRule] = []
        
        # Initialize database
        self._init_database()
        
        # Security configuration
        self.security_config = {
            "audit_enabled": True,
            "access_control_enabled": True,
            "compliance_monitoring_enabled": True,
            "real_time_alerts": True,
            "encryption_required": True,
            "backup_encryption": True
        }
        
        # Compliance requirements
        self.compliance_requirements = {
            ComplianceStandard.GDPR: {
                "data_encryption": True,
                "access_logging": True,
                "data_retention": 7 * 365,  # 7 years
                "consent_tracking": True,
                "right_to_be_forgotten": True
            },
            ComplianceStandard.SOX: {
                "audit_trail": True,
                "change_control": True,
                "segregation_of_duties": True,
                "data_integrity": True,
                "retention_period": 7 * 365
            },
            ComplianceStandard.HIPAA: {
                "data_encryption": True,
                "access_controls": True,
                "audit_logs": True,
                "breach_notification": True,
                "minimum_necessary": True
            }
        }
        
        # Load existing data
        self._load_security_events()
        self._load_access_rules()
    
    def _init_database(self):
        """Initialize security and compliance database"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Security events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_events (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                file_path TEXT NOT NULL,
                user TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                compliance_tags TEXT
            )
        """)
        
        # Access control rules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS access_control_rules (
                rule_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                file_pattern TEXT NOT NULL,
                allowed_users TEXT NOT NULL,
                allowed_actions TEXT NOT NULL,
                security_level TEXT NOT NULL,
                compliance_requirements TEXT,
                created_at TEXT NOT NULL,
                expires_at TEXT
            )
        """)
        
        # Compliance reports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compliance_reports (
                report_id TEXT PRIMARY KEY,
                standard TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                compliance_score REAL NOT NULL,
                violations TEXT NOT NULL,
                recommendations TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)
        
        # File integrity table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_integrity (
                file_path TEXT PRIMARY KEY,
                checksum TEXT NOT NULL,
                last_checked TEXT NOT NULL,
                permissions TEXT NOT NULL,
                owner TEXT NOT NULL,
                group TEXT NOT NULL,
                security_level TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_security_events(self):
        """Load security events from database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM security_events ORDER BY timestamp DESC LIMIT 1000")
            rows = cursor.fetchall()
            
            for row in rows:
                event = SecurityEvent(
                    event_id=row[0],
                    timestamp=datetime.fromisoformat(row[1]),
                    event_type=row[2],
                    severity=SecurityLevel(row[3]),
                    file_path=row[4],
                    user=row[5],
                    action=row[6],
                    details=json.loads(row[7]),
                    compliance_tags=[ComplianceStandard(tag) for tag in json.loads(row[8])] if row[8] else []
                )
                self.security_events.append(event)
            
            conn.close()
            logger.info(f"Loaded {len(self.security_events)} security events")
            
        except Exception as e:
            logger.error(f"Error loading security events: {e}")
    
    def _load_access_rules(self):
        """Load access control rules from database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM access_control_rules")
            rows = cursor.fetchall()
            
            for row in rows:
                rule = AccessControlRule(
                    rule_id=row[0],
                    name=row[1],
                    file_pattern=row[2],
                    allowed_users=json.loads(row[3]),
                    allowed_actions=json.loads(row[4]),
                    security_level=SecurityLevel(row[5]),
                    compliance_requirements=[ComplianceStandard(req) for req in json.loads(row[6])] if row[6] else [],
                    created_at=datetime.fromisoformat(row[7]),
                    expires_at=datetime.fromisoformat(row[8]) if row[8] else None
                )
                self.access_rules.append(rule)
            
            conn.close()
            logger.info(f"Loaded {len(self.access_rules)} access control rules")
            
        except Exception as e:
            logger.error(f"Error loading access rules: {e}")
    
    async def log_security_event(self, event_type: str, file_path: str, user: str, 
                               action: str, severity: SecurityLevel = SecurityLevel.MEDIUM,
                               details: Optional[Dict[str, Any]] = None):
        """Log a security event"""
        try:
            event_id = self._generate_event_id(event_type, file_path, user)
            
            event = SecurityEvent(
                event_id=event_id,
                timestamp=datetime.now(),
                event_type=event_type,
                severity=severity,
                file_path=file_path,
                user=user,
                action=action,
                details=details or {},
                compliance_tags=self._get_compliance_tags(file_path, action)
            )
            
            # Store in database
            await self._store_security_event(event)
            
            # Add to memory
            self.security_events.append(event)
            
            # Check for real-time alerts
            if self.security_config["real_time_alerts"]:
                await self._check_real_time_alerts(event)
            
            logger.info(f"🔒 Logged security event: {event_type} on {file_path}")
            
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
    
    def _generate_event_id(self, event_type: str, file_path: str, user: str) -> str:
        """Generate unique event ID"""
        event_str = f"{event_type}_{file_path}_{user}_{datetime.now().isoformat()}"
        return hashlib.md5(event_str.encode()).hexdigest()[:16]
    
    def _get_compliance_tags(self, file_path: str, action: str) -> List[ComplianceStandard]:
        """Get compliance tags for file and action"""
        tags = []
        
        # GDPR tags
        if any(pattern in file_path.lower() for pattern in ["personal", "user", "customer", "email"]):
            tags.append(ComplianceStandard.GDPR)
        
        # SOX tags
        if any(pattern in file_path.lower() for pattern in ["financial", "accounting", "audit"]):
            tags.append(ComplianceStandard.SOX)
        
        # HIPAA tags
        if any(pattern in file_path.lower() for pattern in ["medical", "health", "patient"]):
            tags.append(ComplianceStandard.HIPAA)
        
        return tags
    
    async def _store_security_event(self, event: SecurityEvent):
        """Store security event in database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO security_events 
                (event_id, timestamp, event_type, severity, file_path, user, action, details, compliance_tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id,
                event.timestamp.isoformat(),
                event.event_type,
                event.severity.value,
                event.file_path,
                event.user,
                event.action,
                json.dumps(event.details),
                json.dumps([tag.value for tag in event.compliance_tags])
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing security event: {e}")
    
    async def _check_real_time_alerts(self, event: SecurityEvent):
        """Check for real-time security alerts"""
        try:
            # Critical events
            if event.severity == SecurityLevel.CRITICAL:
                await self._send_alert(f"CRITICAL: {event.event_type} on {event.file_path}", event)
            
            # Unauthorized access attempts
            if event.event_type == "unauthorized_access":
                await self._send_alert(f"Unauthorized access attempt: {event.user} -> {event.file_path}", event)
            
            # Suspicious patterns
            if await self._detect_suspicious_pattern(event):
                await self._send_alert(f"Suspicious activity detected: {event.event_type}", event)
            
        except Exception as e:
            logger.error(f"Error checking real-time alerts: {e}")
    
    async def _detect_suspicious_pattern(self, event: SecurityEvent) -> bool:
        """Detect suspicious patterns in security events"""
        try:
            # Check for rapid successive access attempts
            recent_events = [
                e for e in self.security_events 
                if e.user == event.user and 
                (event.timestamp - e.timestamp).seconds < 60
            ]
            
            if len(recent_events) > 10:  # More than 10 events in 1 minute
                return True
            
            # Check for access to sensitive files
            sensitive_patterns = [".env", "password", "secret", "key", "token"]
            if any(pattern in event.file_path.lower() for pattern in sensitive_patterns):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting suspicious patterns: {e}")
            return False
    
    async def _send_alert(self, message: str, event: SecurityEvent):
        """Send security alert"""
        logger.warning(f"🚨 SECURITY ALERT: {message}")
        # In a real implementation, this would send to monitoring systems, email, Slack, etc.
    
    async def create_access_rule(self, name: str, file_pattern: str, allowed_users: List[str],
                               allowed_actions: List[str], security_level: SecurityLevel,
                               compliance_requirements: Optional[List[ComplianceStandard]] = None):
        """Create access control rule"""
        try:
            rule_id = self._generate_rule_id(name, file_pattern)
            
            rule = AccessControlRule(
                rule_id=rule_id,
                name=name,
                file_pattern=file_pattern,
                allowed_users=allowed_users,
                allowed_actions=allowed_actions,
                security_level=security_level,
                compliance_requirements=compliance_requirements or [],
                created_at=datetime.now()
            )
            
            # Store in database
            await self._store_access_rule(rule)
            
            # Add to memory
            self.access_rules.append(rule)
            
            logger.info(f"✅ Created access rule: {name}")
            return rule_id
            
        except Exception as e:
            logger.error(f"Error creating access rule: {e}")
            return None
    
    def _generate_rule_id(self, name: str, file_pattern: str) -> str:
        """Generate unique rule ID"""
        rule_str = f"{name}_{file_pattern}_{datetime.now().isoformat()}"
        return hashlib.md5(rule_str.encode()).hexdigest()[:12]
    
    async def _store_access_rule(self, rule: AccessControlRule):
        """Store access control rule in database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO access_control_rules 
                (rule_id, name, file_pattern, allowed_users, allowed_actions, security_level, 
                 compliance_requirements, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rule.rule_id,
                rule.name,
                rule.file_pattern,
                json.dumps(rule.allowed_users),
                json.dumps(rule.allowed_actions),
                rule.security_level.value,
                json.dumps([req.value for req in rule.compliance_requirements]),
                rule.created_at.isoformat(),
                rule.expires_at.isoformat() if rule.expires_at else None
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing access rule: {e}")
    
    async def check_access_permission(self, user: str, file_path: str, action: str) -> bool:
        """Check if user has permission to perform action on file"""
        try:
            # Find applicable rules
            applicable_rules = []
            for rule in self.access_rules:
                if self._file_matches_pattern(file_path, rule.file_pattern):
                    if not rule.expires_at or rule.expires_at > datetime.now():
                        applicable_rules.append(rule)
            
            if not applicable_rules:
                # No rules found - default deny
                await self.log_security_event(
                    "access_denied", file_path, user, action, 
                    SecurityLevel.MEDIUM, {"reason": "no_rules_found"}
                )
                return False
            
            # Check if user and action are allowed
            for rule in applicable_rules:
                if user in rule.allowed_users and action in rule.allowed_actions:
                    await self.log_security_event(
                        "access_granted", file_path, user, action, 
                        SecurityLevel.LOW, {"rule_id": rule.rule_id}
                    )
                    return True
            
            # Access denied
            await self.log_security_event(
                "access_denied", file_path, user, action, 
                SecurityLevel.MEDIUM, {"reason": "not_in_allowed_users_or_actions"}
            )
            return False
            
        except Exception as e:
            logger.error(f"Error checking access permission: {e}")
            return False
    
    def _file_matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches pattern"""
        import fnmatch
        return fnmatch.fnmatch(file_path, pattern)
    
    async def generate_compliance_report(self, standard: ComplianceStandard) -> ComplianceReport:
        """Generate compliance report for specific standard"""
        logger.info(f"📋 Generating {standard.value.upper()} compliance report...")
        
        try:
            report_id = self._generate_report_id(standard)
            violations = []
            recommendations = []
            
            # Check compliance requirements
            requirements = self.compliance_requirements.get(standard, {})
            
            # Data encryption check
            if requirements.get("data_encryption"):
                encryption_violations = await self._check_encryption_compliance()
                violations.extend(encryption_violations)
                if encryption_violations:
                    recommendations.append("Implement encryption for all sensitive data files")
            
            # Access logging check
            if requirements.get("access_logging"):
                logging_violations = await self._check_access_logging_compliance()
                violations.extend(logging_violations)
                if logging_violations:
                    recommendations.append("Ensure all file access is properly logged")
            
            # Audit trail check
            if requirements.get("audit_trail"):
                audit_violations = await self._check_audit_trail_compliance()
                violations.extend(audit_violations)
                if audit_violations:
                    recommendations.append("Implement comprehensive audit trail for all operations")
            
            # Calculate compliance score
            total_checks = len(requirements)
            passed_checks = total_checks - len(violations)
            compliance_score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
            
            # Determine status
            if compliance_score >= 90:
                status = "compliant"
            elif compliance_score >= 70:
                status = "mostly_compliant"
            else:
                status = "non_compliant"
            
            report = ComplianceReport(
                report_id=report_id,
                standard=standard,
                generated_at=datetime.now(),
                compliance_score=compliance_score,
                violations=violations,
                recommendations=recommendations,
                status=status
            )
            
            # Store report
            await self._store_compliance_report(report)
            
            logger.info(f"✅ Generated compliance report: {compliance_score:.1f}% compliance")
            return report
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            return ComplianceReport(
                report_id="error",
                standard=standard,
                generated_at=datetime.now(),
                compliance_score=0.0,
                violations=[{"error": str(e)}],
                recommendations=["Fix system errors"],
                status="error"
            )
    
    def _generate_report_id(self, standard: ComplianceStandard) -> str:
        """Generate unique report ID"""
        report_str = f"{standard.value}_{datetime.now().isoformat()}"
        return hashlib.md5(report_str.encode()).hexdigest()[:16]
    
    async def _check_encryption_compliance(self) -> List[Dict[str, Any]]:
        """Check encryption compliance"""
        violations = []
        
        try:
            # Check for unencrypted sensitive files
            sensitive_patterns = [".env", "password", "secret", "key", "token", "credential"]
            
            for file_path in self.base_path.rglob("*"):
                if file_path.is_file():
                    file_str = str(file_path.relative_to(self.base_path))
                    if any(pattern in file_str.lower() for pattern in sensitive_patterns):
                        # Check if file is encrypted (simplified check)
                        if not self._is_file_encrypted(file_path):
                            violations.append({
                                "type": "unencrypted_sensitive_data",
                                "file": file_str,
                                "severity": "high",
                                "description": "Sensitive data file is not encrypted"
                            })
            
        except Exception as e:
            logger.error(f"Error checking encryption compliance: {e}")
        
        return violations
    
    def _is_file_encrypted(self, file_path: Path) -> bool:
        """Check if file is encrypted (simplified implementation)"""
        # In a real implementation, this would check file headers, extensions, etc.
        # For now, assume files with .enc, .gpg, .pgp extensions are encrypted
        encrypted_extensions = [".enc", ".gpg", ".pgp", ".aes"]
        return any(file_path.suffix.lower() in encrypted_extensions for ext in encrypted_extensions)
    
    async def _check_access_logging_compliance(self) -> List[Dict[str, Any]]:
        """Check access logging compliance"""
        violations = []
        
        try:
            # Check if we have sufficient access logs
            recent_events = [
                e for e in self.security_events 
                if e.timestamp > datetime.now() - timedelta(days=30)
            ]
            
            if len(recent_events) < 100:  # Minimum expected events
                violations.append({
                    "type": "insufficient_access_logging",
                    "severity": "medium",
                    "description": "Insufficient access logging detected"
                })
            
        except Exception as e:
            logger.error(f"Error checking access logging compliance: {e}")
        
        return violations
    
    async def _check_audit_trail_compliance(self) -> List[Dict[str, Any]]:
        """Check audit trail compliance"""
        violations = []
        
        try:
            # Check for complete audit trail
            event_types = set(e.event_type for e in self.security_events)
            required_event_types = {"file_access", "file_modification", "file_deletion", "permission_change"}
            
            missing_types = required_event_types - event_types
            if missing_types:
                violations.append({
                    "type": "incomplete_audit_trail",
                    "severity": "high",
                    "description": f"Missing audit events: {', '.join(missing_types)}"
                })
            
        except Exception as e:
            logger.error(f"Error checking audit trail compliance: {e}")
        
        return violations
    
    async def _store_compliance_report(self, report: ComplianceReport):
        """Store compliance report in database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO compliance_reports 
                (report_id, standard, generated_at, compliance_score, violations, recommendations, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                report.report_id,
                report.standard.value,
                report.generated_at.isoformat(),
                report.compliance_score,
                json.dumps(report.violations),
                json.dumps(report.recommendations),
                report.status
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing compliance report: {e}")
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get security system status"""
        return {
            "total_events": len(self.security_events),
            "critical_events": len([e for e in self.security_events if e.severity == SecurityLevel.CRITICAL]),
            "access_rules": len(self.access_rules),
            "active_rules": len([r for r in self.access_rules if not r.expires_at or r.expires_at > datetime.now()]),
            "audit_enabled": self.security_config["audit_enabled"],
            "access_control_enabled": self.security_config["access_control_enabled"],
            "compliance_monitoring_enabled": self.security_config["compliance_monitoring_enabled"],
            "recent_violations": len([e for e in self.security_events if e.event_type == "access_denied" and e.timestamp > datetime.now() - timedelta(days=1)])
        }


# Global security compliance system instance
security_compliance_system = SecurityComplianceSystem()


async def main():
    """Main entry point for testing"""
    try:
        # Log some security events
        await security_compliance_system.log_security_event(
            "file_access", "config/database.yaml", "admin", "read", SecurityLevel.LOW
        )
        
        # Create access rule
        rule_id = await security_compliance_system.create_access_rule(
            "Database Config Access",
            "config/database.*",
            ["admin", "dba"],
            ["read"],
            SecurityLevel.HIGH,
            [ComplianceStandard.SOX]
        )
        
        # Generate compliance report
        report = await security_compliance_system.generate_compliance_report(ComplianceStandard.GDPR)
        
        print("🔒 SECURITY & COMPLIANCE SYSTEM STATUS")
        print("=" * 50)
        status = security_compliance_system.get_security_status()
        print(f"Total Events: {status['total_events']}")
        print(f"Access Rules: {status['access_rules']}")
        print(f"GDPR Compliance: {report.compliance_score:.1f}%")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
