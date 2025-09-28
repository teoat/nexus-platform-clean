#!/usr/bin/env python3
"""
NEXUS Platform - AI Orchestrator Service
Advanced AI agent orchestration and task management
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field
import uuid
import json
from pathlib import Path

from .ssot_registry import SSOTRegistry
from .performance_optimization import PerformanceOptimizer
from .audit_logging import AuditLogQueryEngine, AuditLogLevel, OperationType
from backend.config.settings import get_settings

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Types of AI agents"""
    SSOT_MANAGER = "ssot_manager"
    DATA_OPTIMIZER = "data_optimizer"
    SECURITY_AUDITOR = "security_auditor"
    PERFORMANCE_MONITOR = "performance_monitor"
    DEPLOYMENT_AUTOMATOR = "deployment_automator"
    FRENLY_AI = "frenly_ai"

class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AgentTask:
    """Represents a task for an AI agent"""
    task_id: str
    agent_type: AgentType
    task_type: str
    description: str
    priority: TaskPriority
    data: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

class AIAgent:
    """Base class for AI agents"""
    
    def __init__(self, agent_type: AgentType, name: str):
        self.agent_type = agent_type
        self.name = name
        self.status = "idle"
        self.current_task: Optional[AgentTask] = None
        self.task_history: List[AgentTask] = []
        self.performance_metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_execution_time": 0.0,
            "success_rate": 0.0
        }
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a task - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement execute_task")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_type": self.agent_type.value,
            "name": self.name,
            "status": self.status,
            "current_task": self.current_task.task_id if self.current_task else None,
            "performance_metrics": self.performance_metrics,
            "task_history_count": len(self.task_history)
        }

class SSOTManagerAgent(AIAgent):
    """SSOT Management AI Agent"""
    
    def __init__(self):
        super().__init__(AgentType.SSOT_MANAGER, "SSOT Manager")
        self.registry = SSOTRegistry()
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute SSOT management task"""
        try:
            self.status = "running"
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now(timezone.utc)
            
            if task.task_type == "validate_consistency":
                result = await self._validate_ssot_consistency(task.data)
            elif task.task_type == "resolve_conflicts":
                result = await self._resolve_conflicts(task.data)
            elif task.task_type == "optimize_aliases":
                result = await self._optimize_aliases(task.data)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
            task.result = result
            self.status = "idle"
            
            # Update performance metrics
            self._update_metrics(task, True)
            
            return result
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now(timezone.utc)
            self.status = "idle"
            self._update_metrics(task, False)
            raise
    
    async def _validate_ssot_consistency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate SSOT consistency"""
        # Implementation for SSOT validation
        await asyncio.sleep(0.1)  # Simulate work
        return {
            "valid": True,
            "issues_found": 0,
            "validation_time": 0.1
        }
    
    async def _resolve_conflicts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve SSOT conflicts"""
        # Implementation for conflict resolution
        await asyncio.sleep(0.2)  # Simulate work
        return {
            "conflicts_resolved": 3,
            "resolution_time": 0.2
        }
    
    async def _optimize_aliases(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize SSOT aliases"""
        # Implementation for alias optimization
        await asyncio.sleep(0.15)  # Simulate work
        return {
            "aliases_optimized": 5,
            "optimization_time": 0.15
        }
    
    def _update_metrics(self, task: AgentTask, success: bool):
        """Update performance metrics"""
        if success:
            self.performance_metrics["tasks_completed"] += 1
        else:
            self.performance_metrics["tasks_failed"] += 1
        
        total_tasks = self.performance_metrics["tasks_completed"] + self.performance_metrics["tasks_failed"]
        self.performance_metrics["success_rate"] = (
            self.performance_metrics["tasks_completed"] / total_tasks * 100
        ) if total_tasks > 0 else 0

class DataOptimizerAgent(AIAgent):
    """Data Optimization AI Agent"""
    
    def __init__(self):
        super().__init__(AgentType.DATA_OPTIMIZER, "Data Optimizer")
        self.optimizer = PerformanceOptimizer()
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute data optimization task"""
        try:
            self.status = "running"
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now(timezone.utc)
            
            if task.task_type == "optimize_queries":
                result = await self._optimize_database_queries(task.data)
            elif task.task_type == "cache_optimization":
                result = await self._optimize_caching(task.data)
            elif task.task_type == "index_optimization":
                result = await self._optimize_indexes(task.data)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
            task.result = result
            self.status = "idle"
            
            self._update_metrics(task, True)
            return result
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now(timezone.utc)
            self.status = "idle"
            self._update_metrics(task, False)
            raise
    
    async def _optimize_database_queries(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize database queries"""
        await asyncio.sleep(0.3)  # Simulate work
        return {
            "queries_optimized": 10,
            "performance_improvement": "25%",
            "optimization_time": 0.3
        }
    
    async def _optimize_caching(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize caching strategy"""
        await asyncio.sleep(0.25)  # Simulate work
        return {
            "cache_hit_rate_improvement": "15%",
            "memory_usage_reduction": "20%",
            "optimization_time": 0.25
        }
    
    async def _optimize_indexes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize database indexes"""
        await asyncio.sleep(0.4)  # Simulate work
        return {
            "indexes_optimized": 8,
            "query_speed_improvement": "40%",
            "optimization_time": 0.4
        }
    
    def _update_metrics(self, task: AgentTask, success: bool):
        """Update performance metrics"""
        if success:
            self.performance_metrics["tasks_completed"] += 1
        else:
            self.performance_metrics["tasks_failed"] += 1
        
        total_tasks = self.performance_metrics["tasks_completed"] + self.performance_metrics["tasks_failed"]
        self.performance_metrics["success_rate"] = (
            self.performance_metrics["tasks_completed"] / total_tasks * 100
        ) if total_tasks > 0 else 0

class AIOrchestrator:
    """AI Orchestrator for managing multiple AI agents"""
    
    def __init__(self):
        self.settings = get_settings()
        self.agents: Dict[AgentType, AIAgent] = {}
        self.task_queue: List[AgentTask] = []
        self.task_history: List[AgentTask] = []
        self.is_running = False
        self._task_counter = 0
        self._lock = asyncio.Lock()

        # Initialize audit logging
        self.audit_engine = AuditLogQueryEngine()

        # Initialize agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all AI agents"""
        self.agents[AgentType.SSOT_MANAGER] = SSOTManagerAgent()
        self.agents[AgentType.DATA_OPTIMIZER] = DataOptimizerAgent()
        # Add more agents as needed
    
    async def start(self):
        """Start the AI orchestrator"""
        if self.is_running:
            logger.warning("Orchestrator is already running")
            return
        
        self.is_running = True
        logger.info("AI Orchestrator started")
        
        # Start task processing loop
        asyncio.create_task(self._process_tasks())
    
    async def stop(self):
        """Stop the AI orchestrator"""
        self.is_running = False
        logger.info("AI Orchestrator stopped")
    
    async def submit_task(
        self,
        agent_type: AgentType,
        task_type: str,
        description: str,
        priority: TaskPriority,
        data: Dict[str, Any] = None
    ) -> str:
        """Submit a new task to the orchestrator"""
        async with self._lock:
            task_id = str(uuid.uuid4())
            task = AgentTask(
                task_id=task_id,
                agent_type=agent_type,
                task_type=task_type,
                description=description,
                priority=priority,
                data=data or {}
            )
            
            # Insert task based on priority
            self._insert_task_by_priority(task)
            self._task_counter += 1

            logger.info(f"Task submitted: {task_id} for agent {agent_type.value}")

            # Audit log AI task submission
            try:
                await self.audit_engine.log_operation(
                    operation=OperationType.CREATE.value,
                    entity_type="AITask",
                    entity_id=task_id,
                    details={
                        "agent_type": agent_type.value,
                        "task_type": task_type,
                        "description": description,
                        "priority": priority.value,
                        "data": data,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                    performed_by="ai_orchestrator",
                    context="ai_operations",
                    log_level=AuditLogLevel.INFO,
                )
            except Exception as e:
                logger.error(f"Failed to audit log AI task submission: {e}")

            return task_id
    
    def _insert_task_by_priority(self, task: AgentTask):
        """Insert task into queue based on priority"""
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3
        }
        
        task_priority = priority_order[task.priority]
        
        # Find insertion point
        insert_index = 0
        for i, queued_task in enumerate(self.task_queue):
            if priority_order[queued_task.priority] > task_priority:
                insert_index = i
                break
            insert_index = i + 1
        
        self.task_queue.insert(insert_index, task)
    
    async def _process_tasks(self):
        """Process tasks from the queue"""
        while self.is_running:
            if not self.task_queue:
                await asyncio.sleep(1)
                continue
            
            # Get next task
            task = self.task_queue.pop(0)
            agent = self.agents.get(task.agent_type)
            
            if not agent:
                logger.error(f"No agent available for type: {task.agent_type}")
                task.status = TaskStatus.FAILED
                task.error = f"No agent available for type: {task.agent_type}"
                self.task_history.append(task)
                continue
            
            # Check if agent is available
            if agent.status != "idle":
                # Put task back in queue
                self.task_queue.insert(0, task)
                await asyncio.sleep(1)
                continue
            
            # Execute task
            try:
                agent.current_task = task
                result = await agent.execute_task(task)
                agent.task_history.append(task)
                self.task_history.append(task)

                logger.info(f"Task completed: {task.task_id}")

                # Audit log successful AI task completion
                try:
                    await self.audit_engine.log_operation(
                        operation=OperationType.UPDATE.value,
                        entity_type="AITask",
                        entity_id=task.task_id,
                        details={
                            "task_status": "completed",
                            "agent_type": task.agent_type.value,
                            "task_type": task.task_type,
                            "execution_time": (task.completed_at - task.started_at).total_seconds() if task.completed_at and task.started_at else None,
                            "result": result,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        },
                        performed_by="ai_orchestrator",
                        context="ai_operations",
                        log_level=AuditLogLevel.INFO,
                    )
                except Exception as e:
                    logger.error(f"Failed to audit log AI task completion: {e}")

            except Exception as e:
                logger.error(f"Task failed: {task.task_id}, error: {e}")

                # Retry logic
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    task.status = TaskStatus.PENDING
                    task.error = None
                    self._insert_task_by_priority(task)

                    # Audit log task retry
                    try:
                        await self.audit_engine.log_operation(
                            operation=OperationType.UPDATE.value,
                            entity_type="AITask",
                            entity_id=task.task_id,
                            details={
                                "task_status": "retry",
                                "retry_count": task.retry_count,
                                "max_retries": task.max_retries,
                                "error": str(e),
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                            },
                            performed_by="ai_orchestrator",
                            context="ai_operations",
                            log_level=AuditLogLevel.WARNING,
                        )
                    except Exception as audit_e:
                        logger.error(f"Failed to audit log AI task retry: {audit_e}")
                else:
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                    agent.task_history.append(task)
                    self.task_history.append(task)

                    # Audit log failed AI task
                    try:
                        await self.audit_engine.log_operation(
                            operation=OperationType.UPDATE.value,
                            entity_type="AITask",
                            entity_id=task.task_id,
                            details={
                                "task_status": "failed",
                                "agent_type": task.agent_type.value,
                                "task_type": task.task_type,
                                "error": str(e),
                                "retry_count": task.retry_count,
                                "max_retries": task.max_retries,
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                            },
                            performed_by="ai_orchestrator",
                            context="ai_operations",
                            log_level=AuditLogLevel.ERROR,
                        )
                    except Exception as audit_e:
                        logger.error(f"Failed to audit log AI task failure: {audit_e}")
            
            finally:
                agent.current_task = None
    
    async def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        agents_status = {}
        for agent_type, agent in self.agents.items():
            agents_status[agent_type.value] = await agent.get_status()
        
        return {
            "orchestrator_running": self.is_running,
            "agents": agents_status,
            "task_queue_size": len(self.task_queue),
            "completed_tasks": len([t for t in self.task_history if t.status == TaskStatus.COMPLETED]),
            "failed_tasks": len([t for t in self.task_history if t.status == TaskStatus.FAILED]),
            "system_metrics": {
                "total_tasks_processed": len(self.task_history),
                "active_agents": sum(1 for agent in self.agents.values() if agent.status == "running"),
                "idle_agents": sum(1 for agent in self.agents.values() if agent.status == "idle")
            }
        }
    
    async def get_task_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get task execution history"""
        recent_tasks = self.task_history[-limit:] if self.task_history else []
        
        return [
            {
                "task_id": task.task_id,
                "agent_type": task.agent_type.value,
                "task_type": task.task_type,
                "description": task.description,
                "priority": task.priority.value,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "result": task.result,
                "error": task.error,
                "retry_count": task.retry_count
            }
            for task in recent_tasks
        ]
    
    async def get_agent_metrics(self, agent_type: AgentType) -> Dict[str, Any]:
        """Get metrics for a specific agent"""
        agent = self.agents.get(agent_type)
        if not agent:
            return {"error": f"Agent not found: {agent_type.value}"}
        
        return await agent.get_status()

# Global orchestrator instance
orchestrator = AIOrchestrator()