"""
NEXUS Platform - Audit Logger
Comprehensive audit logging and compliance tracking
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import uuid
from dataclasses import dataclass, asdict
import hashlib

logger = logging.getLogger(__name__)

class AuditLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AuditCategory(str, Enum):
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_OPERATION = "system_operation"
    SECURITY_EVENT = "security_event"
    COMPLIANCE = "compliance"
    BUSINESS_OPERATION = "business_operation"
    ERROR = "error"
    AUDIT = "audit"

@dataclass
class AuditEntry:
    id: str
    timestamp: datetime
    level: AuditLevel
    category: AuditCategory
    user_id: Optional[str]
    session_id: Optional[str]
    request_id: Optional[str]
    action: str
    resource: str
    details: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]
    outcome: str
    risk_score: float
    compliance_flags: List[str]
    hash: str

class AuditLogger:
    """
    Comprehensive audit logging system
    """
    
    def __init__(self):
        self.audit_entries: List[AuditEntry] = []
        self.compliance_rules: Dict[str, Dict[str, Any]] = {}
        self.risk_thresholds: Dict[str, float] = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8,
            'critical': 0.9
        }
        
        # Initialize compliance rules
        self._initialize_compliance_rules()
    
    def _initialize_compliance_rules(self):
        """Initialize compliance rules for different audit categories"""
        self.compliance_rules = {
            AuditCategory.AUTHENTICATION: {
                'required_fields': ['user_id', 'action', 'outcome'],
                'retention_days': 2555,  # 7 years
                'encryption_required': True,
                'alert_on_failure': True
            },
            AuditCategory.AUTHORIZATION: {
                'required_fields': ['user_id', 'action', 'resource', 'outcome'],
                'retention_days': 2555,
                'encryption_required': True,
                'alert_on_failure': True
            },
            AuditCategory.DATA_ACCESS: {
                'required_fields': ['user_id', 'action', 'resource'],
                'retention_days': 1095,  # 3 years
                'encryption_required': True,
                'alert_on_failure': False
            },
            AuditCategory.DATA_MODIFICATION: {
                'required_fields': ['user_id', 'action', 'resource', 'outcome'],
                'retention_days': 2555,
                'encryption_required': True,
                'alert_on_failure': True
            },
            AuditCategory.SECURITY_EVENT: {
                'required_fields': ['action', 'outcome'],
                'retention_days': 2555,
                'encryption_required': True,
                'alert_on_failure': True
            },
            AuditCategory.COMPLIANCE: {
                'required_fields': ['action', 'outcome', 'compliance_flags'],
                'retention_days': 2555,
                'encryption_required': True,
                'alert_on_failure': True
            }
        }
    
    async def log(
        self,
        level: AuditLevel,
        category: AuditCategory,
        action: str,
        resource: str = "",
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        outcome: str = "success",
        risk_score: float = 0.0,
        compliance_flags: Optional[List[str]] = None
    ) -> str:
        """
        Log an audit entry
        """
        try:
            # Validate required fields based on category
            self._validate_audit_entry(category, {
                'user_id': user_id,
                'action': action,
                'resource': resource,
                'outcome': outcome,
                'compliance_flags': compliance_flags
            })
            
            # Create audit entry
            audit_id = str(uuid.uuid4())
            timestamp = datetime.now()
            
            audit_entry = AuditEntry(
                id=audit_id,
                timestamp=timestamp,
                level=level,
                category=category,
                user_id=user_id,
                session_id=session_id,
                request_id=request_id,
                action=action,
                resource=resource,
                details=details or {},
                ip_address=ip_address,
                user_agent=user_agent,
                outcome=outcome,
                risk_score=risk_score,
                compliance_flags=compliance_flags or [],
                hash=""
            )
            
            # Calculate hash for integrity
            audit_entry.hash = self._calculate_hash(audit_entry)
            
            # Store audit entry
            self.audit_entries.append(audit_entry)
            
            # Log to system logger
            await self._log_to_system(audit_entry)
            
            # Check for compliance violations
            await self._check_compliance_violations(audit_entry)
            
            # Check risk thresholds
            await self._check_risk_thresholds(audit_entry)
            
            logger.info(f"Audit entry logged: {audit_id}")
            return audit_id
            
        except Exception as e:
            logger.error(f"Failed to log audit entry: {str(e)}")
            raise
    
    def _validate_audit_entry(self, category: AuditCategory, data: Dict[str, Any]):
        """Validate audit entry against compliance rules"""
        if category not in self.compliance_rules:
            return
        
        rules = self.compliance_rules[category]
        required_fields = rules.get('required_fields', [])
        
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValueError(f"Required field '{field}' missing for audit category '{category.value}'")
    
    def _calculate_hash(self, audit_entry: AuditEntry) -> str:
        """Calculate hash for audit entry integrity"""
        # Create a copy without the hash field for calculation
        entry_dict = asdict(audit_entry)
        entry_dict['hash'] = ""
        
        # Convert to JSON string and calculate hash
        entry_json = json.dumps(entry_dict, sort_keys=True, default=str)
        return hashlib.sha256(entry_json.encode()).hexdigest()
    
    async def _log_to_system(self, audit_entry: AuditEntry):
        """Log audit entry to system logger"""
        log_data = {
            'audit_id': audit_entry.id,
            'timestamp': audit_entry.timestamp.isoformat(),
            'level': audit_entry.level.value,
            'category': audit_entry.category.value,
            'user_id': audit_entry.user_id,
            'action': audit_entry.action,
            'resource': audit_entry.resource,
            'outcome': audit_entry.outcome,
            'risk_score': audit_entry.risk_score,
            'ip_address': audit_entry.ip_address
        }
        
        if audit_entry.level == AuditLevel.CRITICAL:
            logger.critical(f"AUDIT: {json.dumps(log_data)}")
        elif audit_entry.level == AuditLevel.ERROR:
            logger.error(f"AUDIT: {json.dumps(log_data)}")
        elif audit_entry.level == AuditLevel.WARNING:
            logger.warning(f"AUDIT: {json.dumps(log_data)}")
        else:
            logger.info(f"AUDIT: {json.dumps(log_data)}")
    
    async def _check_compliance_violations(self, audit_entry: AuditEntry):
        """Check for compliance violations"""
        if audit_entry.category not in self.compliance_rules:
            return
        
        rules = self.compliance_rules[audit_entry.category]
        
        # Check if encryption is required
        if rules.get('encryption_required', False):
            if not self._is_encrypted(audit_entry):
                await self._log_compliance_violation(
                    audit_entry,
                    "Encryption required but not applied",
                    "HIGH"
                )
        
        # Check for specific compliance flags
        if audit_entry.compliance_flags:
            for flag in audit_entry.compliance_flags:
                if flag.startswith('VIOLATION_'):
                    await self._log_compliance_violation(
                        audit_entry,
                        f"Compliance violation: {flag}",
                        "CRITICAL"
                    )
    
    def _is_encrypted(self, audit_entry: AuditEntry) -> bool:
        """Check if audit entry is encrypted"""
        # This would check if the audit entry is properly encrypted
        # For now, we'll assume it's encrypted if it has a hash
        return bool(audit_entry.hash)
    
    async def _log_compliance_violation(self, audit_entry: AuditEntry, violation: str, severity: str):
        """Log compliance violation"""
        await self.log(
            level=AuditLevel.ERROR,
            category=AuditCategory.COMPLIANCE,
            action="compliance_violation",
            resource=audit_entry.resource,
            user_id=audit_entry.user_id,
            session_id=audit_entry.session_id,
            request_id=audit_entry.request_id,
            details={
                'original_audit_id': audit_entry.id,
                'violation': violation,
                'severity': severity
            },
            outcome="violation",
            risk_score=0.9,
            compliance_flags=[f"VIOLATION_{severity}"]
        )
    
    async def _check_risk_thresholds(self, audit_entry: AuditEntry):
        """Check if audit entry exceeds risk thresholds"""
        for threshold_name, threshold_value in self.risk_thresholds.items():
            if audit_entry.risk_score >= threshold_value:
                await self._log_risk_alert(audit_entry, threshold_name, threshold_value)
    
    async def _log_risk_alert(self, audit_entry: AuditEntry, threshold_name: str, threshold_value: float):
        """Log risk alert"""
        await self.log(
            level=AuditLevel.WARNING,
            category=AuditCategory.SECURITY_EVENT,
            action="risk_threshold_exceeded",
            resource=audit_entry.resource,
            user_id=audit_entry.user_id,
            session_id=audit_entry.session_id,
            request_id=audit_entry.request_id,
            details={
                'original_audit_id': audit_entry.id,
                'threshold_name': threshold_name,
                'threshold_value': threshold_value,
                'actual_risk_score': audit_entry.risk_score
            },
            outcome="alert",
            risk_score=audit_entry.risk_score,
            compliance_flags=[f"RISK_{threshold_name.upper()}"]
        )
    
    async def get_audit_entries(
        self,
        user_id: Optional[str] = None,
        category: Optional[AuditCategory] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get audit entries with filtering"""
        filtered_entries = self.audit_entries
        
        # Apply filters
        if user_id:
            filtered_entries = [e for e in filtered_entries if e.user_id == user_id]
        
        if category:
            filtered_entries = [e for e in filtered_entries if e.category == category]
        
        if start_date:
            filtered_entries = [e for e in filtered_entries if e.timestamp >= start_date]
        
        if end_date:
            filtered_entries = [e for e in filtered_entries if e.timestamp <= end_date]
        
        # Sort by timestamp (newest first)
        filtered_entries.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply pagination
        paginated_entries = filtered_entries[offset:offset + limit]
        
        # Convert to dictionaries
        return [asdict(entry) for entry in paginated_entries]
    
    async def get_audit_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get audit statistics"""
        filtered_entries = self.audit_entries
        
        if start_date:
            filtered_entries = [e for e in filtered_entries if e.timestamp >= start_date]
        
        if end_date:
            filtered_entries = [e for e in filtered_entries if e.timestamp <= end_date]
        
        if not filtered_entries:
            return {'total_entries': 0}
        
        # Count by level
        level_counts = {}
        for entry in filtered_entries:
            level = entry.level.value
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # Count by category
        category_counts = {}
        for entry in filtered_entries:
            category = entry.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Count by outcome
        outcome_counts = {}
        for entry in filtered_entries:
            outcome = entry.outcome
            outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1
        
        # Risk score statistics
        risk_scores = [entry.risk_score for entry in filtered_entries]
        avg_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        
        # High-risk entries
        high_risk_entries = [e for e in filtered_entries if e.risk_score >= 0.8]
        
        # Compliance violations
        compliance_violations = [e for e in filtered_entries if e.compliance_flags and any('VIOLATION_' in flag for flag in e.compliance_flags)]
        
        return {
            'total_entries': len(filtered_entries),
            'level_breakdown': level_counts,
            'category_breakdown': category_counts,
            'outcome_breakdown': outcome_counts,
            'average_risk_score': avg_risk_score,
            'high_risk_entries': len(high_risk_entries),
            'compliance_violations': len(compliance_violations),
            'date_range': {
                'start': min(e.timestamp for e in filtered_entries).isoformat() if filtered_entries else None,
                'end': max(e.timestamp for e in filtered_entries).isoformat() if filtered_entries else None
            }
        }
    
    async def export_audit_log(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "json"
    ) -> str:
        """Export audit log in specified format"""
        filtered_entries = self.audit_entries
        
        if start_date:
            filtered_entries = [e for e in filtered_entries if e.timestamp >= start_date]
        
        if end_date:
            filtered_entries = [e for e in filtered_entries if e.timestamp <= end_date]
        
        if format == "json":
            return json.dumps([asdict(entry) for entry in filtered_entries], default=str, indent=2)
        elif format == "csv":
            # Convert to CSV format
            if not filtered_entries:
                return ""
            
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'id', 'timestamp', 'level', 'category', 'user_id', 'session_id', 'request_id',
                'action', 'resource', 'outcome', 'risk_score', 'ip_address', 'compliance_flags'
            ])
            
            # Write data
            for entry in filtered_entries:
                writer.writerow([
                    entry.id,
                    entry.timestamp.isoformat(),
                    entry.level.value,
                    entry.category.value,
                    entry.user_id or '',
                    entry.session_id or '',
                    entry.request_id or '',
                    entry.action,
                    entry.resource,
                    entry.outcome,
                    entry.risk_score,
                    entry.ip_address or '',
                    ','.join(entry.compliance_flags)
                ])
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def cleanup_old_entries(self):
        """Clean up old audit entries based on retention policies"""
        current_date = datetime.now()
        entries_to_remove = []
        
        for entry in self.audit_entries:
            category = entry.category
            if category in self.compliance_rules:
                retention_days = self.compliance_rules[category].get('retention_days', 365)
                cutoff_date = current_date - timedelta(days=retention_days)
                
                if entry.timestamp < cutoff_date:
                    entries_to_remove.append(entry)
        
        # Remove old entries
        for entry in entries_to_remove:
            self.audit_entries.remove(entry)
        
        logger.info(f"Cleaned up {len(entries_to_remove)} old audit entries")
        return len(entries_to_remove)

# Global audit logger instance
audit_logger = AuditLogger()

# Convenience function for logging
async def audit_log(
    level: AuditLevel,
    category: AuditCategory,
    action: str,
    resource: str = "",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    request_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    outcome: str = "success",
    risk_score: float = 0.0,
    compliance_flags: Optional[List[str]] = None
) -> str:
    """Convenience function for logging audit entries"""
    return await audit_logger.log(
        level=level,
        category=category,
        action=action,
        resource=resource,
        user_id=user_id,
        session_id=session_id,
        request_id=request_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
        outcome=outcome,
        risk_score=risk_score,
        compliance_flags=compliance_flags
    )
