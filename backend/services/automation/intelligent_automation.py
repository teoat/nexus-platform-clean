#!/usr/bin/env python3
"""
NEXUS Platform - Intelligent Automation Engine
Advanced automation with AI-driven decision making and self-optimization
"""
import asyncio
import logging
import json
import yaml
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

class AutomationType(Enum):
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"
    CONDITIONAL = "conditional"
    AI_DRIVEN = "ai_driven"
    SELF_OPTIMIZING = "self_optimizing"

class AutomationStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    DISABLED = "disabled"

class TriggerType(Enum):
    TIME = "time"
    EVENT = "event"
    CONDITION = "condition"
    AI_PREDICTION = "ai_prediction"
    USER_ACTION = "user_action"

@dataclass
class AutomationRule:
    rule_id: str
    name: str
    description: str
    automation_type: AutomationType
    trigger_type: TriggerType
    trigger_config: Dict[str, Any]
    actions: List[Dict[str, Any]]
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    priority: int = 1
    enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_executed: Optional[datetime] = None
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0

@dataclass
class AutomationExecution:
    execution_id: str
    rule_id: str
    status: AutomationStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None

@dataclass
class AutomationMetrics:
    total_rules: int
    active_rules: int
    total_executions: int
    successful_executions: int
    failed_executions: int
    average_execution_time: float
    automation_efficiency: float
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class IntelligentAutomationEngine:
    def __init__(self):
        self.rules: Dict[str, AutomationRule] = {}
        self.executions: Dict[str, AutomationExecution] = {}
        self.is_running = False
        self.metrics = AutomationMetrics(0, 0, 0, 0, 0, 0.0, 0.0)
        self.action_handlers: Dict[str, Callable] = {}
        self.condition_evaluators: Dict[str, Callable] = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default action handlers and condition evaluators"""
        self.action_handlers.update({
            "send_notification": self._handle_send_notification,
            "update_data": self._handle_update_data,
            "execute_workflow": self._handle_execute_workflow,
            "generate_report": self._handle_generate_report,
            "optimize_system": self._handle_optimize_system,
            "backup_data": self._handle_backup_data,
            "cleanup_resources": self._handle_cleanup_resources,
            "scale_resources": self._handle_scale_resources
        })
        
        self.condition_evaluators.update({
            "time_condition": self._evaluate_time_condition,
            "data_condition": self._evaluate_data_condition,
            "performance_condition": self._evaluate_performance_condition,
            "resource_condition": self._evaluate_resource_condition,
            "user_condition": self._evaluate_user_condition
        })
    
    async def start(self):
        if self.is_running:
            return
        self.is_running = True
        logger.info("Intelligent Automation Engine started")
        asyncio.create_task(self._process_automations())
        asyncio.create_task(self._update_metrics())
    
    async def stop(self):
        self.is_running = False
        logger.info("Intelligent Automation Engine stopped")
    
    async def _process_automations(self):
        while self.is_running:
            try:
                active_rules = [rule for rule in self.rules.values() if rule.enabled]
                
                for rule in active_rules:
                    if await self._should_execute_rule(rule):
                        asyncio.create_task(self._execute_rule(rule))
                
                await asyncio.sleep(1)  # Check every second
            except Exception as e:
                logger.error(f"Error processing automations: {e}")
                await asyncio.sleep(5)
    
    async def _should_execute_rule(self, rule: AutomationRule) -> bool:
        """Determine if a rule should be executed based on its trigger conditions"""
        try:
            if rule.trigger_type == TriggerType.TIME:
                return await self._evaluate_time_trigger(rule)
            elif rule.trigger_type == TriggerType.EVENT:
                return await self._evaluate_event_trigger(rule)
            elif rule.trigger_type == TriggerType.CONDITION:
                return await self._evaluate_condition_trigger(rule)
            elif rule.trigger_type == TriggerType.AI_PREDICTION:
                return await self._evaluate_ai_trigger(rule)
            elif rule.trigger_type == TriggerType.USER_ACTION:
                return await self._evaluate_user_trigger(rule)
            
            return False
        except Exception as e:
            logger.error(f"Error evaluating rule {rule.rule_id}: {e}")
            return False
    
    async def _evaluate_time_trigger(self, rule: AutomationRule) -> bool:
        """Evaluate time-based triggers"""
        config = rule.trigger_config
        now = datetime.now(timezone.utc)
        
        if "interval" in config:
            interval = timedelta(seconds=config["interval"])
            if rule.last_executed is None or now - rule.last_executed >= interval:
                return True
        
        if "schedule" in config:
            schedule = config["schedule"]
            if "hour" in schedule and now.hour == schedule["hour"]:
                if "minute" in schedule and now.minute == schedule["minute"]:
                    return True
                elif "minute" not in schedule:
                    return True
        
        return False
    
    async def _evaluate_event_trigger(self, rule: AutomationRule) -> bool:
        """Evaluate event-based triggers"""
        # This would integrate with the event system
        # For now, return False as events need to be triggered externally
        return False
    
    async def _evaluate_condition_trigger(self, rule: AutomationRule) -> bool:
        """Evaluate condition-based triggers"""
        for condition in rule.conditions:
            if not await self._evaluate_condition(condition):
                return False
        return True
    
    async def _evaluate_ai_trigger(self, rule: AutomationRule) -> bool:
        """Evaluate AI prediction-based triggers"""
        # This would integrate with the AI services
        # For now, return False as AI predictions need to be provided
        return False
    
    async def _evaluate_user_trigger(self, rule: AutomationRule) -> bool:
        """Evaluate user action-based triggers"""
        # This would integrate with user action tracking
        # For now, return False as user actions need to be tracked
        return False
    
    async def _evaluate_condition(self, condition: Dict[str, Any]) -> bool:
        """Evaluate a single condition"""
        condition_type = condition.get("type")
        evaluator = self.condition_evaluators.get(condition_type)
        
        if evaluator:
            return await evaluator(condition)
        
        return False
    
    async def _execute_rule(self, rule: AutomationRule):
        """Execute an automation rule"""
        execution_id = f"exec_{int(datetime.now().timestamp())}"
        execution = AutomationExecution(
            execution_id=execution_id,
            rule_id=rule.rule_id,
            status=AutomationStatus.ACTIVE,
            started_at=datetime.now(timezone.utc)
        )
        
        self.executions[execution_id] = execution
        rule.last_executed = execution.started_at
        rule.execution_count += 1
        
        try:
            # Check conditions before execution
            conditions_met = True
            for condition in rule.conditions:
                if not await self._evaluate_condition(condition):
                    conditions_met = False
                    break
            
            if not conditions_met:
                execution.status = AutomationStatus.FAILED
                execution.error_message = "Conditions not met"
                rule.failure_count += 1
                return
            
            # Execute actions
            results = []
            for action in rule.actions:
                action_type = action.get("type")
                handler = self.action_handlers.get(action_type)
                
                if handler:
                    try:
                        result = await handler(action.get("config", {}))
                        results.append({"action": action_type, "result": result, "success": True})
                    except Exception as e:
                        results.append({"action": action_type, "error": str(e), "success": False})
                        logger.error(f"Action {action_type} failed: {e}")
                else:
                    logger.warning(f"No handler for action type: {action_type}")
            
            # Update execution status
            execution.status = AutomationStatus.COMPLETED
            execution.completed_at = datetime.now(timezone.utc)
            execution.execution_time = (execution.completed_at - execution.started_at).total_seconds()
            execution.result = {"actions": results}
            
            rule.success_count += 1
            logger.info(f"Rule {rule.rule_id} executed successfully")
            
        except Exception as e:
            execution.status = AutomationStatus.FAILED
            execution.completed_at = datetime.now(timezone.utc)
            execution.execution_time = (execution.completed_at - execution.started_at).total_seconds()
            execution.error_message = str(e)
            
            rule.failure_count += 1
            logger.error(f"Rule {rule.rule_id} execution failed: {e}")
    
    # Action Handlers
    async def _handle_send_notification(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send notification action"""
        return {
            "type": "notification",
            "message": config.get("message", "Automation notification"),
            "recipients": config.get("recipients", []),
            "priority": config.get("priority", "normal")
        }
    
    async def _handle_update_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update data action"""
        return {
            "type": "data_update",
            "target": config.get("target"),
            "operation": config.get("operation", "update"),
            "data": config.get("data", {})
        }
    
    async def _handle_execute_workflow(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle execute workflow action"""
        return {
            "type": "workflow",
            "workflow_id": config.get("workflow_id"),
            "parameters": config.get("parameters", {})
        }
    
    async def _handle_generate_report(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generate report action"""
        return {
            "type": "report",
            "report_type": config.get("report_type", "summary"),
            "format": config.get("format", "pdf"),
            "parameters": config.get("parameters", {})
        }
    
    async def _handle_optimize_system(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle optimize system action"""
        return {
            "type": "optimization",
            "target": config.get("target", "performance"),
            "parameters": config.get("parameters", {})
        }
    
    async def _handle_backup_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle backup data action"""
        return {
            "type": "backup",
            "target": config.get("target", "database"),
            "location": config.get("location", "backup/"),
            "retention": config.get("retention", 30)
        }
    
    async def _handle_cleanup_resources(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle cleanup resources action"""
        return {
            "type": "cleanup",
            "target": config.get("target", "temp_files"),
            "age_threshold": config.get("age_threshold", 7)
        }
    
    async def _handle_scale_resources(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle scale resources action"""
        return {
            "type": "scaling",
            "target": config.get("target", "containers"),
            "action": config.get("action", "scale_up"),
            "amount": config.get("amount", 1)
        }
    
    # Condition Evaluators
    async def _evaluate_time_condition(self, condition: Dict[str, Any]) -> bool:
        """Evaluate time-based conditions"""
        now = datetime.now(timezone.utc)
        condition_time = condition.get("time")
        
        if condition_time:
            if "before" in condition_time:
                return now.hour < condition_time["before"]
            elif "after" in condition_time:
                return now.hour > condition_time["after"]
            elif "between" in condition_time:
                start, end = condition_time["between"]
                return start <= now.hour <= end
        
        return True
    
    async def _evaluate_data_condition(self, condition: Dict[str, Any]) -> bool:
        """Evaluate data-based conditions"""
        # This would check actual data conditions
        # For now, return True as a placeholder
        return True
    
    async def _evaluate_performance_condition(self, condition: Dict[str, Any]) -> bool:
        """Evaluate performance-based conditions"""
        # This would check system performance metrics
        # For now, return True as a placeholder
        return True
    
    async def _evaluate_resource_condition(self, condition: Dict[str, Any]) -> bool:
        """Evaluate resource-based conditions"""
        # This would check system resource usage
        # For now, return True as a placeholder
        return True
    
    async def _evaluate_user_condition(self, condition: Dict[str, Any]) -> bool:
        """Evaluate user-based conditions"""
        # This would check user-related conditions
        # For now, return True as a placeholder
        return True
    
    # Public API Methods
    async def create_rule(self, rule_data: Dict[str, Any]) -> str:
        """Create a new automation rule"""
        rule_id = f"rule_{int(datetime.now().timestamp())}"
        
        rule = AutomationRule(
            rule_id=rule_id,
            name=rule_data["name"],
            description=rule_data.get("description", ""),
            automation_type=AutomationType(rule_data["automation_type"]),
            trigger_type=TriggerType(rule_data["trigger_type"]),
            trigger_config=rule_data["trigger_config"],
            actions=rule_data["actions"],
            conditions=rule_data.get("conditions", []),
            priority=rule_data.get("priority", 1),
            enabled=rule_data.get("enabled", True)
        )
        
        self.rules[rule_id] = rule
        logger.info(f"Automation rule {rule_id} created")
        return rule_id
    
    async def update_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing automation rule"""
        if rule_id not in self.rules:
            return False
        
        rule = self.rules[rule_id]
        for key, value in updates.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        
        logger.info(f"Automation rule {rule_id} updated")
        return True
    
    async def delete_rule(self, rule_id: str) -> bool:
        """Delete an automation rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Automation rule {rule_id} deleted")
            return True
        return False
    
    async def execute_rule_manually(self, rule_id: str) -> str:
        """Manually execute an automation rule"""
        if rule_id not in self.rules:
            raise ValueError(f"Rule {rule_id} not found")
        
        rule = self.rules[rule_id]
        await self._execute_rule(rule)
        return f"Rule {rule_id} executed manually"
    
    async def get_rule(self, rule_id: str) -> Optional[AutomationRule]:
        """Get an automation rule by ID"""
        return self.rules.get(rule_id)
    
    async def get_all_rules(self) -> List[AutomationRule]:
        """Get all automation rules"""
        return list(self.rules.values())
    
    async def get_execution_history(self, rule_id: Optional[str] = None) -> List[AutomationExecution]:
        """Get execution history for rules"""
        if rule_id:
            return [exec for exec in self.executions.values() if exec.rule_id == rule_id]
        return list(self.executions.values())
    
    async def _update_metrics(self):
        """Update automation metrics"""
        while self.is_running:
            try:
                self.metrics.total_rules = len(self.rules)
                self.metrics.active_rules = len([r for r in self.rules.values() if r.enabled])
                self.metrics.total_executions = len(self.executions)
                self.metrics.successful_executions = len([e for e in self.executions.values() 
                                                        if e.status == AutomationStatus.COMPLETED])
                self.metrics.failed_executions = len([e for e in self.executions.values() 
                                                    if e.status == AutomationStatus.FAILED])
                
                if self.executions:
                    execution_times = [e.execution_time for e in self.executions.values() 
                                    if e.execution_time is not None]
                    if execution_times:
                        self.metrics.average_execution_time = sum(execution_times) / len(execution_times)
                
                if self.metrics.total_executions > 0:
                    self.metrics.automation_efficiency = (
                        self.metrics.successful_executions / self.metrics.total_executions
                    )
                
                self.metrics.last_updated = datetime.now(timezone.utc)
                await asyncio.sleep(30)  # Update every 30 seconds
            except Exception as e:
                logger.error(f"Error updating metrics: {e}")
                await asyncio.sleep(30)
    
    async def get_metrics(self) -> AutomationMetrics:
        """Get automation metrics"""
        return self.metrics
    
    async def get_engine_status(self) -> Dict[str, Any]:
        """Get automation engine status"""
        return {
            "engine_running": self.is_running,
            "total_rules": len(self.rules),
            "active_rules": len([r for r in self.rules.values() if r.enabled]),
            "total_executions": len(self.executions),
            "metrics": self.metrics
        }

intelligent_automation_engine = IntelligentAutomationEngine()
