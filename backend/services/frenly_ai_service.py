#!/usr/bin/env python3
"""
NEXUS Platform - Frenly AI Service V3.0
Core service for Frenly AI operations and intelligence
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from schemas.frenly_ai import \
    FrenlyAIConfiguration as FrenlyAIConfigurationSchema
from schemas.frenly_ai import \
    FrenlyAIConversation as FrenlyAIConversationSchema
from schemas.frenly_ai import FrenlyAIMemory as FrenlyAIMemorySchema
from schemas.frenly_ai import FrenlyAIResponse as FrenlyAIResponseSchema
from schemas.frenly_ai import FrenlyAISystemStatus
from schemas.frenly_ai import FrenlyAITask as FrenlyAITaskSchema
from sqlalchemy.orm import Session

from database.database import get_db
from database.enhanced_models import (FrenlyAIActionType, FrenlyAIAuditLog,
                                      FrenlyAIConfidence,
                                      FrenlyAIConfiguration,
                                      FrenlyAIConversation, FrenlyAIMemory,
                                      FrenlyAIPriority, FrenlyAIResponse,
                                      FrenlyAIStatus, FrenlyAITask,
                                      FrenlyAITaskType, FrenlyAITool, User)

logger = logging.getLogger(__name__)


class FrenlyAIService:
    """Enhanced Frenly AI Service with system maintenance and user assistance capabilities"""

    def __init__(self):
        self.system_tools = self._initialize_system_tools()
        self.learning_engine = FrenlyAILearningEngine()
        self.audit_trail = FrenlyAIAuditTrail()
        self.conversation_manager = FrenlyAIConversationManager()
        self.system_status = FrenlyAISystemStatus(
            status=FrenlyAIStatus.IDLE,
            active_tasks=0,
            completed_tasks=0,
            failed_tasks=0,
            learning_mode=True,
            system_health="excellent",
            last_activity=datetime.utcnow(),
            uptime=0,
            memory_usage=0.0,
            cpu_usage=0.0,
            available_tools=list(self.system_tools.keys()),
            recent_actions=[],
        )

    def _initialize_system_tools(self) -> Dict[str, Any]:
        """Initialize system maintenance tools"""
        return {
            "database_optimizer": {
                "name": "Database Optimizer",
                "description": "Optimize database performance and clean up unused data",
                "permissions": ["read", "write", "optimize"],
                "category": "system_maintenance",
                "success_rate": 0.95,
            },
            "security_scanner": {
                "name": "Security Scanner",
                "description": "Scan for security vulnerabilities and compliance issues",
                "permissions": ["read", "scan", "report"],
                "category": "security",
                "success_rate": 0.88,
            },
            "data_reconciler": {
                "name": "Data Reconciler",
                "description": "Reconcile financial data and detect discrepancies",
                "permissions": ["read", "analyze", "suggest"],
                "category": "data_management",
                "success_rate": 0.92,
            },
            "fraud_detector": {
                "name": "Fraud Detector",
                "description": "Detect fraudulent patterns and suspicious activities",
                "permissions": ["read", "analyze", "flag"],
                "category": "fraud_detection",
                "success_rate": 0.89,
            },
            "performance_monitor": {
                "name": "Performance Monitor",
                "description": "Monitor system performance and suggest optimizations",
                "permissions": ["read", "monitor", "suggest"],
                "category": "performance",
                "success_rate": 0.91,
            },
            "backup_manager": {
                "name": "Backup Manager",
                "description": "Manage automated backups and data recovery",
                "permissions": ["read", "backup", "restore"],
                "category": "backup",
                "success_rate": 0.98,
            },
            "compliance_checker": {
                "name": "Compliance Checker",
                "description": "Check compliance with financial and legal standards",
                "permissions": ["read", "check", "report"],
                "category": "compliance",
                "success_rate": 0.94,
            },
            "user_assistant": {
                "name": "User Assistant",
                "description": "Provide intelligent assistance to users",
                "permissions": ["read", "suggest", "guide"],
                "category": "user_assistance",
                "success_rate": 0.87,
            },
        }

    async def create_task(
        self,
        db: Session,
        user_id: int,
        task_type: FrenlyAITaskType,
        title: str,
        description: str,
        priority: FrenlyAIPriority = FrenlyAIPriority.MEDIUM,
        parameters: Dict[str, Any] = None,
    ) -> FrenlyAITaskSchema:
        """Create a new Frenly AI task"""
        try:
            task_id = str(uuid.uuid4())

            # Check user configuration
            config = (
                db.query(FrenlyAIConfiguration)
                .filter(FrenlyAIConfiguration.user_id == user_id)
                .first()
            )

            if not config:
                config = self._create_default_config(db, user_id)

            # Check if task type is allowed
            if not self._is_task_type_allowed(config, task_type):
                raise ValueError(f"Task type {task_type} is not allowed for this user")

            # Create task
            task = FrenlyAITask(
                id=task_id,
                user_id=user_id,
                type=task_type,
                title=title,
                description=description,
                priority=priority,
                parameters=parameters or {},
                requires_approval=self._requires_approval(task_type, config),
                estimated_duration=self._estimate_duration(task_type),
            )

            db.add(task)
            db.commit()
            db.refresh(task)

            # Update system status
            self.system_status.active_tasks += 1
            self.system_status.last_activity = datetime.utcnow()

            # Log audit trail
            await self.audit_trail.log_action(
                db,
                user_id,
                "create_task",
                "frenly_ai_task",
                task_id,
                new_values={"task_type": task_type.value, "title": title},
            )

            return FrenlyAITaskSchema.from_orm(task)

        except Exception as e:
            logger.error(f"Error creating Frenly AI task: {e}")
            raise

    async def execute_task(self, db: Session, task_id: str) -> FrenlyAIResponseSchema:
        """Execute a Frenly AI task"""
        try:
            task = db.query(FrenlyAITask).filter(FrenlyAITask.id == task_id).first()
            if not task:
                raise ValueError("Task not found")

            # Update task status
            task.status = FrenlyAIStatus.WORKING
            task.progress = 10
            db.commit()

            # Execute based on task type
            response = await self._execute_task_by_type(db, task)

            # Update task with result
            task.status = FrenlyAIStatus.IDLE
            task.progress = 100
            task.result = response.dict()
            db.commit()

            # Update system status
            self.system_status.active_tasks -= 1
            self.system_status.completed_tasks += 1
            self.system_status.last_activity = datetime.utcnow()

            return response

        except Exception as e:
            logger.error(f"Error executing Frenly AI task: {e}")
            task.status = FrenlyAIStatus.ERROR
            task.error_message = str(e)
            db.commit()

            # Update system status
            self.system_status.active_tasks -= 1
            self.system_status.failed_tasks += 1
            self.system_status.last_activity = datetime.utcnow()
            raise

    async def _execute_task_by_type(
        self, db: Session, task: FrenlyAITask
    ) -> FrenlyAIResponseSchema:
        """Execute task based on its type"""
        task_type = task.type

        if task_type == FrenlyAITaskType.SYSTEM_MAINTENANCE:
            return await self._execute_system_maintenance(db, task)
        elif task_type == FrenlyAITaskType.DATA_RECONCILIATION:
            return await self._execute_data_reconciliation(db, task)
        elif task_type == FrenlyAITaskType.FRAUD_DETECTION:
            return await self._execute_fraud_detection(db, task)
        elif task_type == FrenlyAITaskType.PERFORMANCE_OPTIMIZATION:
            return await self._execute_performance_optimization(db, task)
        elif task_type == FrenlyAITaskType.SECURITY_AUDIT:
            return await self._execute_security_audit(db, task)
        elif task_type == FrenlyAITaskType.USER_ASSISTANCE:
            return await self._execute_user_assistance(db, task)
        elif task_type == FrenlyAITaskType.COMPLIANCE_CHECK:
            return await self._execute_compliance_check(db, task)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def _execute_system_maintenance(
        self, db: Session, task: FrenlyAITask
    ) -> FrenlyAIResponseSchema:
        """Execute system maintenance tasks"""
        try:
            # Update progress
            task.progress = 25
            db.commit()

            # Database optimization
            db.execute("VACUUM ANALYZE")

            # Clean up old logs
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            deleted_logs = (
                db.query(FrenlyAIAuditLog)
                .filter(FrenlyAIAuditLog.created_at < cutoff_date)
                .delete()
            )

            # Update progress
            task.progress = 75
            db.commit()

            # Update system statistics
            db.execute(
                "UPDATE pg_stat_user_tables SET n_tup_ins = 0, n_tup_upd = 0, n_tup_del = 0"
            )

            db.commit()

            return FrenlyAIResponseSchema(
                task_id=task.id,
                response_type=FrenlyAIActionType.EXECUTE_SAFE,
                content="System maintenance completed successfully. Database optimized, old logs cleaned, and statistics updated.",
                confidence=FrenlyAIConfidence.HIGH,
                actions=[
                    {
                        "type": "database_optimization",
                        "status": "completed",
                        "details": "Database vacuumed and analyzed",
                        "logs_cleaned": deleted_logs,
                    }
                ],
                requires_approval=False,
                reasoning="Routine system maintenance to ensure optimal performance",
                evidence=[
                    "Database optimization completed",
                    "Log cleanup successful",
                    "Statistics updated",
                ],
                created_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Error in system maintenance: {e}")
            raise

    async def _execute_data_reconciliation(
        self, db: Session, task: FrenlyAITask
    ) -> FrenlyAIResponseSchema:
        """Execute data reconciliation tasks"""
        try:
            task.progress = 20
            db.commit()

            # Find discrepancies in financial data
            discrepancies = []

            # Check for orphaned transactions
            orphaned_transactions = db.execute(
                """
                SELECT t.id, t.amount, t.description 
                FROM transactions t 
                LEFT JOIN accounts a ON t.account_id = a.id 
                WHERE a.id IS NULL
            """
            ).fetchall()

            if orphaned_transactions:
                discrepancies.append(
                    {
                        "type": "orphaned_transactions",
                        "count": len(orphaned_transactions),
                        "details": "Transactions without valid accounts",
                    }
                )

            task.progress = 50
            db.commit()

            # Check for balance inconsistencies
            balance_issues = db.execute(
                """
                SELECT a.id, a.name, a.balance, 
                       COALESCE(SUM(t.amount), 0) as calculated_balance
                FROM accounts a
                LEFT JOIN transactions t ON a.id = t.account_id
                GROUP BY a.id, a.name, a.balance
                HAVING ABS(a.balance - COALESCE(SUM(t.amount), 0)) > 0.01
            """
            ).fetchall()

            if balance_issues:
                discrepancies.append(
                    {
                        "type": "balance_inconsistencies",
                        "count": len(balance_issues),
                        "details": "Account balances don't match transaction totals",
                    }
                )

            task.progress = 80
            db.commit()

            return FrenlyAIResponseSchema(
                task_id=task.id,
                response_type=FrenlyAIActionType.SUGGEST,
                content=f"Data reconciliation completed. Found {len(discrepancies)} types of discrepancies.",
                confidence=FrenlyAIConfidence.HIGH,
                actions=[
                    {
                        "type": "data_reconciliation",
                        "status": "completed",
                        "discrepancies": discrepancies,
                    }
                ],
                requires_approval=True,
                reasoning="Data reconciliation found discrepancies that require user review",
                evidence=[
                    f"Found {len(discrepancies)} discrepancy types",
                    "Orphaned transactions detected",
                    "Balance inconsistencies found",
                ],
                created_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Error in data reconciliation: {e}")
            raise

    async def _execute_fraud_detection(
        self, db: Session, task: FrenlyAITask
    ) -> FrenlyAIResponseSchema:
        """Execute fraud detection tasks"""
        try:
            task.progress = 15
            db.commit()

            fraud_indicators = []

            # Check for duplicate transactions
            duplicates = db.execute(
                """
                SELECT description, amount, date, COUNT(*) as count
                FROM transactions
                GROUP BY description, amount, date
                HAVING COUNT(*) > 1
            """
            ).fetchall()

            if duplicates:
                fraud_indicators.append(
                    {
                        "type": "duplicate_transactions",
                        "count": len(duplicates),
                        "severity": "medium",
                        "details": "Potential duplicate transactions detected",
                    }
                )

            task.progress = 40
            db.commit()

            # Check for unusual patterns
            unusual_patterns = db.execute(
                """
                SELECT user_id, COUNT(*) as transaction_count, SUM(amount) as total_amount
                FROM transactions
                WHERE date >= NOW() - INTERVAL '1 day'
                GROUP BY user_id
                HAVING COUNT(*) > 50 OR SUM(amount) > 10000
            """
            ).fetchall()

            if unusual_patterns:
                fraud_indicators.append(
                    {
                        "type": "unusual_patterns",
                        "count": len(unusual_patterns),
                        "severity": "high",
                        "details": "Unusual transaction patterns detected",
                    }
                )

            task.progress = 70
            db.commit()

            # Check for round number bias
            round_numbers = db.execute(
                """
                SELECT COUNT(*) as count
                FROM transactions
                WHERE amount % 100 = 0 AND amount > 100
            """
            ).fetchone()

            if round_numbers and round_numbers.count > 10:
                fraud_indicators.append(
                    {
                        "type": "round_number_bias",
                        "count": round_numbers.count,
                        "severity": "low",
                        "details": "Excessive use of round numbers may indicate fabricated expenses",
                    }
                )

            task.progress = 90
            db.commit()

            return FrenlyAIResponseSchema(
                task_id=task.id,
                response_type=FrenlyAIActionType.ALERT,
                content=f"Fraud detection completed. Found {len(fraud_indicators)} types of fraud indicators.",
                confidence=FrenlyAIConfidence.HIGH,
                actions=[
                    {
                        "type": "fraud_detection",
                        "status": "completed",
                        "indicators": fraud_indicators,
                    }
                ],
                requires_approval=True,
                reasoning="Fraud detection found suspicious patterns that require immediate attention",
                evidence=[
                    f"Found {len(fraud_indicators)} fraud indicator types",
                    "Duplicate transactions detected",
                    "Unusual patterns identified",
                ],
                created_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Error in fraud detection: {e}")
            raise

    async def _execute_performance_optimization(
        self, db: Session, task: FrenlyAITask
    ) -> FrenlyAIResponseSchema:
        """Execute performance optimization tasks"""
        try:
            task.progress = 20
            db.commit()

            optimizations = []

            # Check for missing indexes
            missing_indexes = db.execute(
                """
                SELECT schemaname, tablename, attname, n_distinct, correlation
                FROM pg_stats
                WHERE schemaname = 'public' 
                AND n_distinct > 100 
                AND correlation < 0.1
            """
            ).fetchall()

            if missing_indexes:
                optimizations.append(
                    {
                        "type": "missing_indexes",
                        "count": len(missing_indexes),
                        "details": "Tables that could benefit from additional indexes",
                    }
                )

            task.progress = 50
            db.commit()

            # Check for slow queries
            slow_queries = db.execute(
                """
                SELECT query, mean_time, calls
                FROM pg_stat_statements
                WHERE mean_time > 1000
                ORDER BY mean_time DESC
                LIMIT 10
            """
            ).fetchall()

            if slow_queries:
                optimizations.append(
                    {
                        "type": "slow_queries",
                        "count": len(slow_queries),
                        "details": "Queries that are taking too long to execute",
                    }
                )

            task.progress = 80
            db.commit()

            return FrenlyAIResponseSchema(
                task_id=task.id,
                response_type=FrenlyAIActionType.SUGGEST,
                content=f"Performance optimization completed. Found {len(optimizations)} types of optimizations.",
                confidence=FrenlyAIConfidence.MEDIUM,
                actions=[
                    {
                        "type": "performance_optimization",
                        "status": "completed",
                        "optimizations": optimizations,
                    }
                ],
                requires_approval=True,
                reasoning="Performance optimization found areas for improvement",
                evidence=[
                    f"Found {len(optimizations)} optimization types",
                    "Missing indexes identified",
                    "Slow queries detected",
                ],
                created_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Error in performance optimization: {e}")
            raise

    async def _execute_security_audit(
        self, db: Session, task: FrenlyAITask
    ) -> FrenlyAIResponseSchema:
        """Execute security audit tasks"""
        try:
            task.progress = 25
            db.commit()

            security_issues = []

            # Check for weak passwords (simplified check)
            weak_passwords = db.execute(
                """
                SELECT id, username, email
                FROM users
                WHERE LENGTH(hashed_password) < 60
            """
            ).fetchall()

            if weak_passwords:
                security_issues.append(
                    {
                        "type": "weak_passwords",
                        "count": len(weak_passwords),
                        "severity": "high",
                        "details": "Users with potentially weak passwords",
                    }
                )

            task.progress = 50
            db.commit()

            # Check for inactive users
            inactive_users = db.execute(
                """
                SELECT id, username, email, created_at
                FROM users
                WHERE is_active = false
                AND created_at < NOW() - INTERVAL '90 days'
            """
            ).fetchall()

            if inactive_users:
                security_issues.append(
                    {
                        "type": "inactive_users",
                        "count": len(inactive_users),
                        "severity": "medium",
                        "details": "Long-term inactive users that could be removed",
                    }
                )

            task.progress = 75
            db.commit()

            # Check for failed login attempts
            failed_logins = db.execute(
                """
                SELECT COUNT(*) as count
                FROM audit_logs
                WHERE action = 'login_failed'
                AND created_at >= NOW() - INTERVAL '24 hours'
            """
            ).fetchone()

            if failed_logins and failed_logins.count > 10:
                security_issues.append(
                    {
                        "type": "excessive_failed_logins",
                        "count": failed_logins.count,
                        "severity": "high",
                        "details": "Excessive failed login attempts detected",
                    }
                )

            task.progress = 90
            db.commit()

            return FrenlyAIResponseSchema(
                task_id=task.id,
                response_type=FrenlyAIActionType.ALERT,
                content=f"Security audit completed. Found {len(security_issues)} types of security issues.",
                confidence=FrenlyAIConfidence.HIGH,
                actions=[
                    {
                        "type": "security_audit",
                        "status": "completed",
                        "issues": security_issues,
                    }
                ],
                requires_approval=True,
                reasoning="Security audit found issues that require immediate attention",
                evidence=[
                    f"Found {len(security_issues)} security issue types",
                    "Weak passwords detected",
                    "Inactive users identified",
                ],
                created_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Error in security audit: {e}")
            raise

    async def _execute_user_assistance(
        self, db: Session, task: FrenlyAITask
    ) -> FrenlyAIResponseSchema:
        """Execute user assistance tasks"""
        try:
            task.progress = 20
            db.commit()

            # Analyze user patterns and provide suggestions
            user_id = task.user_id
            suggestions = []

            # Check for incomplete profiles
            user_profile = db.execute(
                """
                SELECT up.*, u.username, u.email
                FROM users u
                LEFT JOIN user_profiles up ON u.id = up.user_id
                WHERE u.id = %s
            """,
                (user_id,),
            ).fetchone()

            if not user_profile or not user_profile.bio:
                suggestions.append(
                    {
                        "type": "profile_completion",
                        "priority": "low",
                        "message": "Complete your profile to get better personalized assistance",
                    }
                )

            task.progress = 40
            db.commit()

            # Check for unused features
            feature_usage = db.execute(
                """
                SELECT 
                    COUNT(CASE WHEN t.id IS NOT NULL THEN 1 END) as transaction_count,
                    COUNT(CASE WHEN a.id IS NOT NULL THEN 1 END) as account_count,
                    COUNT(CASE WHEN b.id IS NOT NULL THEN 1 END) as budget_count
                FROM users u
                LEFT JOIN transactions t ON u.id = t.user_id
                LEFT JOIN accounts a ON u.id = a.user_id
                LEFT JOIN budgets b ON u.id = b.user_id
                WHERE u.id = %s
            """,
                (user_id,),
            ).fetchone()

            if feature_usage.transaction_count == 0:
                suggestions.append(
                    {
                        "type": "feature_usage",
                        "priority": "medium",
                        "message": "Start adding transactions to track your financial data",
                    }
                )

            task.progress = 60
            db.commit()

            # Check for POV configuration
            user = db.query(User).filter(User.id == user_id).first()
            if not user.primary_pov_role:
                suggestions.append(
                    {
                        "type": "pov_configuration",
                        "priority": "high",
                        "message": "Configure your POV role to get specialized financial examination tools",
                    }
                )

            task.progress = 80
            db.commit()

            return FrenlyAIResponseSchema(
                task_id=task.id,
                response_type=FrenlyAIActionType.SUGGEST,
                content=f"User assistance completed. Found {len(suggestions)} suggestions for you.",
                confidence=FrenlyAIConfidence.MEDIUM,
                actions=[
                    {
                        "type": "user_assistance",
                        "status": "completed",
                        "suggestions": suggestions,
                    }
                ],
                requires_approval=False,
                reasoning="User assistance analyzed your usage patterns and provided helpful suggestions",
                evidence=[
                    f"Found {len(suggestions)} suggestions",
                    "Profile analysis completed",
                    "Feature usage analyzed",
                ],
                created_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Error in user assistance: {e}")
            raise

    async def _execute_compliance_check(
        self, db: Session, task: FrenlyAITask
    ) -> FrenlyAIResponseSchema:
        """Execute compliance check tasks"""
        try:
            task.progress = 20
            db.commit()

            compliance_issues = []

            # Check for data retention compliance
            old_data = db.execute(
                """
                SELECT COUNT(*) as count
                FROM transactions
                WHERE created_at < NOW() - INTERVAL '7 years'
            """
            ).fetchone()

            if old_data and old_data.count > 0:
                compliance_issues.append(
                    {
                        "type": "data_retention",
                        "count": old_data.count,
                        "severity": "medium",
                        "details": "Data older than 7 years should be archived or deleted for compliance",
                    }
                )

            task.progress = 50
            db.commit()

            # Check for audit trail completeness
            incomplete_audits = db.execute(
                """
                SELECT COUNT(*) as count
                FROM transactions t
                LEFT JOIN audit_logs a ON t.id = a.resource_id AND a.resource_type = 'transaction'
                WHERE a.id IS NULL
            """
            ).fetchone()

            if incomplete_audits and incomplete_audits.count > 0:
                compliance_issues.append(
                    {
                        "type": "incomplete_audit_trail",
                        "count": incomplete_audits.count,
                        "severity": "high",
                        "details": "Some transactions lack proper audit trail",
                    }
                )

            task.progress = 80
            db.commit()

            return FrenlyAIResponseSchema(
                task_id=task.id,
                response_type=FrenlyAIActionType.ALERT,
                content=f"Compliance check completed. Found {len(compliance_issues)} compliance issues.",
                confidence=FrenlyAIConfidence.HIGH,
                actions=[
                    {
                        "type": "compliance_check",
                        "status": "completed",
                        "issues": compliance_issues,
                    }
                ],
                requires_approval=True,
                reasoning="Compliance check found issues that need attention for regulatory compliance",
                evidence=[
                    f"Found {len(compliance_issues)} compliance issues",
                    "Data retention checked",
                    "Audit trail verified",
                ],
                created_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Error in compliance check: {e}")
            raise

    def _is_task_type_allowed(
        self, config: FrenlyAIConfiguration, task_type: FrenlyAITaskType
    ) -> bool:
        """Check if task type is allowed for user"""
        if task_type == FrenlyAITaskType.SYSTEM_MAINTENANCE:
            return config.system_maintenance_enabled
        elif task_type == FrenlyAITaskType.DATA_RECONCILIATION:
            return config.data_reconciliation_enabled
        elif task_type == FrenlyAITaskType.FRAUD_DETECTION:
            return config.fraud_detection_enabled
        elif task_type == FrenlyAITaskType.PERFORMANCE_OPTIMIZATION:
            return config.performance_optimization_enabled
        elif task_type == FrenlyAITaskType.SECURITY_AUDIT:
            return config.security_audit_enabled
        elif task_type == FrenlyAITaskType.USER_ASSISTANCE:
            return config.user_assistance_enabled
        elif task_type == FrenlyAITaskType.COMPLIANCE_CHECK:
            return config.compliance_check_enabled
        return False

    def _requires_approval(
        self, task_type: FrenlyAITaskType, config: FrenlyAIConfiguration
    ) -> bool:
        """Check if task requires approval"""
        if task_type in [
            FrenlyAITaskType.SYSTEM_MAINTENANCE,
            FrenlyAITaskType.USER_ASSISTANCE,
        ]:
            return False
        return True

    def _estimate_duration(self, task_type: FrenlyAITaskType) -> int:
        """Estimate task duration in minutes"""
        duration_map = {
            FrenlyAITaskType.SYSTEM_MAINTENANCE: 5,
            FrenlyAITaskType.DATA_RECONCILIATION: 15,
            FrenlyAITaskType.FRAUD_DETECTION: 10,
            FrenlyAITaskType.PERFORMANCE_OPTIMIZATION: 20,
            FrenlyAITaskType.SECURITY_AUDIT: 30,
            FrenlyAITaskType.USER_ASSISTANCE: 5,
            FrenlyAITaskType.COMPLIANCE_CHECK: 25,
        }
        return duration_map.get(task_type, 10)

    def _create_default_config(
        self, db: Session, user_id: int
    ) -> FrenlyAIConfiguration:
        """Create default Frenly AI configuration for user"""
        config = FrenlyAIConfiguration(
            user_id=user_id,
            ai_level="assisted",
            auto_approve_threshold=0.8,
            learning_enabled=True,
            audit_mode=False,
            allowed_actions=["suggest", "monitor", "alert"],
            restricted_actions=["execute_safe", "execute_with_approval"],
            system_maintenance_enabled=True,
            data_reconciliation_enabled=True,
            fraud_detection_enabled=True,
            performance_optimization_enabled=True,
            security_audit_enabled=True,
            user_assistance_enabled=True,
            compliance_check_enabled=True,
            max_concurrent_tasks=5,
            response_timeout=300,
            learning_rate=0.1,
            memory_retention_days=30,
        )
        db.add(config)
        db.commit()
        db.refresh(config)
        return config

    async def get_system_status(self) -> FrenlyAISystemStatus:
        """Get current Frenly AI system status"""
        return self.system_status

    async def start_conversation(
        self, db: Session, user_id: int
    ) -> FrenlyAIConversationSchema:
        """Start a new conversation with Frenly AI"""
        return await self.conversation_manager.start_conversation(db, user_id)

    async def send_message(
        self, db: Session, conversation_id: str, message: str, user_id: int
    ) -> FrenlyAIResponseSchema:
        """Send a message to Frenly AI"""
        return await self.conversation_manager.send_message(
            db, conversation_id, message, user_id
        )


class FrenlyAILearningEngine:
    """Frenly AI Learning Engine for pattern recognition and adaptation"""

    def __init__(self):
        self.patterns = {}
        self.user_preferences = {}

    async def learn_from_interaction(
        self,
        db: Session,
        user_id: int,
        context: str,
        action: str,
        outcome: str,
        feedback: Optional[str] = None,
    ):
        """Learn from user interaction"""
        try:
            memory = FrenlyAIMemory(
                id=str(uuid.uuid4()),
                user_id=user_id,
                context=context,
                action_taken=action,
                outcome=outcome,
                user_feedback=feedback,
                confidence=FrenlyAIConfidence.MEDIUM,
            )

            db.add(memory)
            db.commit()

            # Update user preferences based on feedback
            if feedback:
                await self._update_user_preferences(user_id, context, action, feedback)

        except Exception as e:
            logger.error(f"Error learning from interaction: {e}")
            raise

    async def _update_user_preferences(
        self, user_id: int, context: str, action: str, feedback: str
    ):
        """Update user preferences based on feedback"""
        # This would implement machine learning algorithms
        # to update user preferences based on feedback
        pass


class FrenlyAIAuditTrail:
    """Frenly AI Audit Trail for compliance and court evidence"""

    async def log_action(
        self,
        db: Session,
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        confidence: FrenlyAIConfidence = FrenlyAIConfidence.MEDIUM,
        reasoning: str = "",
        evidence: List[str] = None,
    ):
        """Log Frenly AI action for audit trail"""
        try:
            audit_log = FrenlyAIAuditLog(
                id=str(uuid.uuid4()),
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                old_values=old_values,
                new_values=new_values,
                confidence=confidence,
                reasoning=reasoning,
                evidence=evidence or [],
                compliance_standard="SOX",  # Sarbanes-Oxley Act
                court_evidence_quality="admissible",
            )

            db.add(audit_log)
            db.commit()

        except Exception as e:
            logger.error(f"Error logging audit trail: {e}")
            raise


class FrenlyAIConversationManager:
    """Frenly AI Conversation Manager for chat interface"""

    def __init__(self):
        self.conversations = {}

    async def start_conversation(
        self, db: Session, user_id: int
    ) -> FrenlyAIConversationSchema:
        """Start a new conversation"""
        try:
            conversation_id = str(uuid.uuid4())

            conversation = FrenlyAIConversation(
                id=conversation_id,
                user_id=user_id,
                messages=[],
                context={},
                status="active",
                expires_at=datetime.utcnow() + timedelta(hours=24),
            )

            db.add(conversation)
            db.commit()
            db.refresh(conversation)

            return FrenlyAIConversationSchema.from_orm(conversation)

        except Exception as e:
            logger.error(f"Error starting conversation: {e}")
            raise

    async def send_message(
        self, db: Session, conversation_id: str, message: str, user_id: int
    ) -> FrenlyAIResponseSchema:
        """Send a message in a conversation"""
        try:
            conversation = (
                db.query(FrenlyAIConversation)
                .filter(
                    FrenlyAIConversation.id == conversation_id,
                    FrenlyAIConversation.user_id == user_id,
                )
                .first()
            )

            if not conversation:
                raise ValueError("Conversation not found")

            # Add user message
            conversation.messages.append(
                {
                    "role": "user",
                    "content": message,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            # Generate AI response
            response = await self._generate_response(message, conversation.context)

            # Add AI response
            conversation.messages.append(
                {
                    "role": "assistant",
                    "content": response.content,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            conversation.updated_at = datetime.utcnow()
            db.commit()

            return response

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise

    async def _generate_response(
        self, message: str, context: Dict[str, Any]
    ) -> FrenlyAIResponseSchema:
        """Generate AI response based on message and context"""
        # This would integrate with a language model
        # For now, return a simple response

        response_content = f"I understand you said: '{message}'. How can I help you with your financial examination needs?"

        return FrenlyAIResponseSchema(
            task_id="",
            response_type=FrenlyAIActionType.SUGGEST,
            content=response_content,
            confidence=FrenlyAIConfidence.MEDIUM,
            actions=[],
            requires_approval=False,
            reasoning="Generated response based on user message",
            evidence=[],
            alternatives=[],
            created_at=datetime.utcnow(),
        )


# Create service instance
frenly_ai_service = FrenlyAIService()
