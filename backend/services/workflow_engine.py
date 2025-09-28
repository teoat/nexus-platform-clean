#!/usr/bin/env python3
"""
NEXUS Platform - Advanced Workflow Engine
Enterprise-grade workflow automation and orchestration
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from pathlib import Path
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"

class TaskType(Enum):
    ACTION = "action"
    CONDITION = "condition"
    LOOP = "loop"
    PARALLEL = "parallel"
    SEQUENCE = "sequence"
    TIMER = "timer"
    WEBHOOK = "webhook"
    API_CALL = "api_call"
    DATA_TRANSFORM = "data_transform"
    NOTIFICATION = "notification"

@dataclass
class TaskDefinition:
    task_id: str
    name: str
    task_type: TaskType
    config: Dict[str, Any]
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    retry_count: int = 0
    timeout_seconds: int = 300
    dependencies: List[str] = field(default_factory=list)

@dataclass
class TaskExecution:
    execution_id: str
    task_id: str
    workflow_id: str
    status: TaskStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    execution_context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowDefinition:
    workflow_id: str
    name: str
    description: str
    version: str
    status: WorkflowStatus
    tasks: List[TaskDefinition]
    variables: Dict[str, Any] = field(default_factory=dict)
    triggers: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "system"

@dataclass
class WorkflowExecution:
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    task_executions: List[TaskExecution] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    triggered_by: str = "manual"

class WorkflowEngine:
    """Advanced Workflow Engine for Enterprise Automation"""
    
    def __init__(self, db_path: str = "workflows.db"):
        self.db_path = db_path
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.task_registry: Dict[TaskType, Callable] = {}
        self.is_running = False
        self.executor = ThreadPoolExecutor(max_workers=10)
        self._init_database()
        self._register_default_tasks()
    
    def _init_database(self):
        """Initialize SQLite database for workflow persistence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create workflows table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                workflow_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                version TEXT NOT NULL,
                status TEXT NOT NULL,
                definition TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT
            )
        """)
        
        # Create executions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_executions (
                execution_id TEXT PRIMARY KEY,
                workflow_id TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                variables TEXT,
                result TEXT,
                error_message TEXT,
                triggered_by TEXT,
                FOREIGN KEY (workflow_id) REFERENCES workflows (workflow_id)
            )
        """)
        
        # Create task_executions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_executions (
                execution_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                workflow_execution_id TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                result TEXT,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                execution_context TEXT,
                FOREIGN KEY (workflow_execution_id) REFERENCES workflow_executions (execution_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _register_default_tasks(self):
        """Register default task implementations"""
        self.task_registry[TaskType.ACTION] = self._execute_action_task
        self.task_registry[TaskType.CONDITION] = self._execute_condition_task
        self.task_registry[TaskType.LOOP] = self._execute_loop_task
        self.task_registry[TaskType.PARALLEL] = self._execute_parallel_task
        self.task_registry[TaskType.SEQUENCE] = self._execute_sequence_task
        self.task_registry[TaskType.TIMER] = self._execute_timer_task
        self.task_registry[TaskType.WEBHOOK] = self._execute_webhook_task
        self.task_registry[TaskType.API_CALL] = self._execute_api_call_task
        self.task_registry[TaskType.DATA_TRANSFORM] = self._execute_data_transform_task
        self.task_registry[TaskType.NOTIFICATION] = self._execute_notification_task
    
    async def start(self):
        """Start the workflow engine"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("Workflow Engine started")
        
        # Load workflows from database
        await self._load_workflows_from_db()
        
        # Start execution processor
        asyncio.create_task(self._process_executions())
    
    async def stop(self):
        """Stop the workflow engine"""
        self.is_running = False
        self.executor.shutdown(wait=True)
        logger.info("Workflow Engine stopped")
    
    async def _load_workflows_from_db(self):
        """Load workflows from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT workflow_id, definition FROM workflows WHERE status = 'active'")
        rows = cursor.fetchall()
        
        for workflow_id, definition_json in rows:
            try:
                definition_data = json.loads(definition_json)
                workflow = self._deserialize_workflow(definition_data)
                self.workflows[workflow_id] = workflow
            except Exception as e:
                logger.error(f"Failed to load workflow {workflow_id}: {e}")
        
        conn.close()
        logger.info(f"Loaded {len(self.workflows)} active workflows")
    
    async def create_workflow(self, workflow_data: Dict[str, Any]) -> str:
        """Create a new workflow"""
        workflow_id = str(uuid.uuid4())
        
        # Parse tasks
        tasks = []
        for task_data in workflow_data.get("tasks", []):
            task = TaskDefinition(
                task_id=task_data["task_id"],
                name=task_data["name"],
                task_type=TaskType(task_data["task_type"]),
                config=task_data.get("config", {}),
                inputs=task_data.get("inputs", []),
                outputs=task_data.get("outputs", []),
                conditions=task_data.get("conditions", []),
                retry_count=task_data.get("retry_count", 0),
                timeout_seconds=task_data.get("timeout_seconds", 300),
                dependencies=task_data.get("dependencies", [])
            )
            tasks.append(task)
        
        workflow = WorkflowDefinition(
            workflow_id=workflow_id,
            name=workflow_data["name"],
            description=workflow_data.get("description", ""),
            version=workflow_data.get("version", "1.0.0"),
            status=WorkflowStatus.DRAFT,
            tasks=tasks,
            variables=workflow_data.get("variables", {}),
            triggers=workflow_data.get("triggers", []),
            created_by=workflow_data.get("created_by", "system")
        )
        
        self.workflows[workflow_id] = workflow
        await self._save_workflow_to_db(workflow)
        
        logger.info(f"Created workflow: {workflow_id}")
        return workflow_id
    
    async def execute_workflow(self, workflow_id: str, variables: Dict[str, Any] = None) -> str:
        """Execute a workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        execution_id = str(uuid.uuid4())
        
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            status=WorkflowStatus.ACTIVE,
            started_at=datetime.now(timezone.utc),
            variables=variables or {},
            triggered_by="manual"
        )
        
        self.executions[execution_id] = execution
        await self._save_execution_to_db(execution)
        
        # Start execution in background
        asyncio.create_task(self._execute_workflow(execution))
        
        logger.info(f"Started workflow execution: {execution_id}")
        return execution_id
    
    async def get_workflow_status(self) -> Dict[str, Any]:
        """Get workflow engine status"""
        total_workflows = len(self.workflows)
        active_executions = len([e for e in self.executions.values() if e.status == WorkflowStatus.ACTIVE])
        completed_executions = len([e for e in self.executions.values() if e.status == WorkflowStatus.COMPLETED])
        failed_executions = len([e for e in self.executions.values() if e.status == WorkflowStatus.FAILED])
        
        return {
            "engine_running": self.is_running,
            "total_workflows": total_workflows,
            "active_executions": active_executions,
            "completed_executions": completed_executions,
            "failed_executions": failed_executions,
            "registered_task_types": len(self.task_registry)
        }

# Global workflow engine instance
workflow_engine = WorkflowEngine()

    async def _execute_workflow(self, execution: WorkflowExecution):
        """Execute a workflow instance"""
        try:
            workflow = self.workflows[execution.workflow_id]
            
            # Execute tasks in dependency order
            executed_tasks = set()
            task_executions = {}
            
            while len(executed_tasks) < len(workflow.tasks):
                # Find tasks ready to execute
                ready_tasks = []
                for task in workflow.tasks:
                    if task.task_id in executed_tasks:
                        continue
                    
                    # Check if all dependencies are completed
                    dependencies_met = all(
                        dep in executed_tasks for dep in task.dependencies
                    )
                    
                    if dependencies_met:
                        ready_tasks.append(task)
                
                if not ready_tasks:
                    # Check for circular dependencies or missing tasks
                    remaining_tasks = [
                        t.task_id for t in workflow.tasks 
                        if t.task_id not in executed_tasks
                    ]
                    raise ValueError(f"Cannot resolve dependencies for tasks: {remaining_tasks}")
                
                # Execute ready tasks
                for task in ready_tasks:
                    task_execution = await self._execute_task(task, execution)
                    task_executions[task.task_id] = task_execution
                    execution.task_executions.append(task_execution)
                    executed_tasks.add(task.task_id)
            
            # Mark execution as completed
            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.now(timezone.utc)
            execution.result = {"status": "success", "tasks_completed": len(executed_tasks)}
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.completed_at = datetime.now(timezone.utc)
            execution.error_message = str(e)
            logger.error(f"Workflow execution {execution.execution_id} failed: {e}")
        
        await self._save_execution_to_db(execution)
    
    async def _execute_task(self, task: TaskDefinition, execution: WorkflowExecution) -> TaskExecution:
        """Execute a single task"""
        task_execution = TaskExecution(
            execution_id=str(uuid.uuid4()),
            task_id=task.task_id,
            workflow_id=execution.workflow_id,
            status=TaskStatus.PENDING
        )
        
        try:
            task_execution.status = TaskStatus.RUNNING
            task_execution.started_at = datetime.now(timezone.utc)
            
            # Get task executor
            executor_func = self.task_registry.get(task.task_type)
            if not executor_func:
                raise ValueError(f"No executor for task type: {task.task_type}")
            
            # Execute task
            result = await executor_func(task, execution, task_execution)
            
            task_execution.status = TaskStatus.COMPLETED
            task_execution.completed_at = datetime.now(timezone.utc)
            task_execution.result = result
            
        except Exception as e:
            task_execution.status = TaskStatus.FAILED
            task_execution.completed_at = datetime.now(timezone.utc)
            task_execution.error_message = str(e)
            logger.error(f"Task {task.task_id} execution failed: {e}")
        
        await self._save_task_execution_to_db(task_execution)
        return task_execution
    
    # Task Executors
    async def _execute_action_task(self, task: TaskDefinition, execution: WorkflowExecution, task_execution: TaskExecution) -> Dict[str, Any]:
        """Execute an action task"""
        action_type = task.config.get("action_type", "custom")
        
        if action_type == "log":
            message = task.config.get("message", "Action executed")
            logger.info(f"Workflow Action: {message}")
            return {"message": message, "timestamp": datetime.now().isoformat()}
        
        elif action_type == "data_processing":
            # Simulate data processing
            data = task.config.get("data", {})
            processed_data = {k: f"processed_{v}" for k, v in data.items()}
            return {"processed_data": processed_data}
        
        else:
            # Custom action
            return {"action": "executed", "config": task.config}
    
    async def _execute_condition_task(self, task: TaskDefinition, execution: WorkflowExecution, task_execution: TaskExecution) -> Dict[str, Any]:
        """Execute a condition task"""
        condition = task.config.get("condition", "true")
        variables = execution.variables
        
        # Simple condition evaluation (in production, use a proper expression evaluator)
        try:
            result = eval(condition, {"variables": variables})
            return {"condition_result": bool(result), "condition": condition}
        except Exception as e:
            return {"condition_result": False, "condition": condition, "error": str(e)}
    
    async def _execute_loop_task(self, task: TaskDefinition, execution: WorkflowExecution, task_execution: TaskExecution) -> Dict[str, Any]:
        """Execute a loop task"""
        loop_count = task.config.get("count", 1)
        loop_items = task.config.get("items", [])
        
        results = []
        for i in range(loop_count):
            if loop_items:
                for item in loop_items:
                    results.append({"iteration": i, "item": item})
            else:
                results.append({"iteration": i})
        
        return {"loop_results": results, "total_iterations": len(results)}
    
    async def _execute_parallel_task(self, task: TaskDefinition, execution: WorkflowExecution, task_execution: TaskExecution) -> Dict[str, Any]:
        """Execute parallel tasks"""
        parallel_tasks = task.config.get("tasks", [])
        
        # Execute tasks in parallel
        results = []
        for parallel_task in parallel_tasks:
            # Simulate parallel execution
            result = await asyncio.sleep(0.1)  # Simulate work
            results.append({"task": parallel_task, "result": "completed"})
        
        return {"parallel_results": results}
    
    async def _execute_sequence_task(self, task: TaskDefinition, execution: WorkflowExecution, task_execution: TaskExecution) -> Dict[str, Any]:
        """Execute sequence tasks"""
        sequence_tasks = task.config.get("tasks", [])
        
        results = []
        for seq_task in sequence_tasks:
            # Simulate sequential execution
            result = await asyncio.sleep(0.1)  # Simulate work
            results.append({"task": seq_task, "result": "completed"})
        
        return {"sequence_results": results}
    
    async def _execute_timer_task(self, task: TaskDefinition, execution: WorkflowExecution, task_execution: TaskExecution) -> Dict[str, Any]:
        """Execute a timer task"""
        delay_seconds = task.config.get("delay_seconds", 1)
        
        await asyncio.sleep(delay_seconds)
        
        return {"delay_completed": delay_seconds, "timestamp": datetime.now().isoformat()}
    
    async def _execute_webhook_task(self, task: TaskDefinition, execution: WorkflowExecution, task_execution: TaskExecution) -> Dict[str, Any]:
        """Execute a webhook task"""
        url = task.config.get("url", "")
        method = task.config.get("method", "POST")
        payload = task.config.get("payload", {})
        
        # Simulate webhook call
        return {
            "webhook_called": True,
            "url": url,
            "method": method,
            "payload": payload,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _execute_api_call_task(self, task: TaskDefinition, execution: WorkflowExecution, task_execution: TaskExecution) -> Dict[str, Any]:
        """Execute an API call task"""
        endpoint = task.config.get("endpoint", "")
        method = task.config.get("method", "GET")
        data = task.config.get("data", {})
        
        # Simulate API call
        return {
            "api_call_made": True,
            "endpoint": endpoint,
            "method": method,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _execute_data_transform_task(self, task: TaskDefinition, execution: WorkflowExecution, task_execution: TaskExecution) -> Dict[str, Any]:
        """Execute a data transform task"""
        transform_type = task.config.get("transform_type", "map")
        input_data = task.config.get("input_data", {})
        
        if transform_type == "map":
            transformed_data = {f"transformed_{k}": v for k, v in input_data.items()}
        elif transform_type == "filter":
            transformed_data = {k: v for k, v in input_data.items() if v}
        else:
            transformed_data = input_data
        
        return {"transformed_data": transformed_data, "transform_type": transform_type}
    
    async def _execute_notification_task(self, task: TaskDefinition, execution: WorkflowExecution, task_execution: TaskExecution) -> Dict[str, Any]:
        """Execute a notification task"""
        notification_type = task.config.get("type", "email")
        message = task.config.get("message", "Workflow notification")
        recipients = task.config.get("recipients", [])
        
        # Simulate notification
        return {
            "notification_sent": True,
            "type": notification_type,
            "message": message,
            "recipients": recipients,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _process_executions(self):
        """Process workflow executions"""
        while self.is_running:
            try:
                # Process any pending executions
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error processing executions: {e}")
                await asyncio.sleep(5)
    
    async def _save_workflow_to_db(self, workflow: WorkflowDefinition):
        """Save workflow to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        definition_json = json.dumps(self._serialize_workflow(workflow))
        
        cursor.execute("""
            INSERT OR REPLACE INTO workflows 
            (workflow_id, name, description, version, status, definition, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            workflow.workflow_id,
            workflow.name,
            workflow.description,
            workflow.version,
            workflow.status.value,
            definition_json,
            workflow.created_by
        ))
        
        conn.commit()
        conn.close()
    
    async def _save_execution_to_db(self, execution: WorkflowExecution):
        """Save execution to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        variables_json = json.dumps(execution.variables)
        result_json = json.dumps(execution.result) if execution.result else None
        
        cursor.execute("""
            INSERT OR REPLACE INTO workflow_executions 
            (execution_id, workflow_id, status, started_at, completed_at, variables, result, error_message, triggered_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            execution.execution_id,
            execution.workflow_id,
            execution.status.value,
            execution.started_at.isoformat(),
            execution.completed_at.isoformat() if execution.completed_at else None,
            variables_json,
            result_json,
            execution.error_message,
            execution.triggered_by
        ))
        
        conn.commit()
        conn.close()
    
    async def _save_task_execution_to_db(self, task_execution: TaskExecution):
        """Save task execution to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        result_json = json.dumps(task_execution.result) if task_execution.result else None
        context_json = json.dumps(task_execution.execution_context)
        
        cursor.execute("""
            INSERT OR REPLACE INTO task_executions 
            (execution_id, task_id, workflow_execution_id, status, started_at, completed_at, result, error_message, retry_count, execution_context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_execution.execution_id,
            task_execution.task_id,
            task_execution.workflow_id,
            task_execution.status.value,
            task_execution.started_at.isoformat() if task_execution.started_at else None,
            task_execution.completed_at.isoformat() if task_execution.completed_at else None,
            result_json,
            task_execution.error_message,
            task_execution.retry_count,
            context_json
        ))
        
        conn.commit()
        conn.close()
    
    def _serialize_workflow(self, workflow: WorkflowDefinition) -> Dict[str, Any]:
        """Serialize workflow to dictionary"""
        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "description": workflow.description,
            "version": workflow.version,
            "status": workflow.status.value,
            "tasks": [
                {
                    "task_id": task.task_id,
                    "name": task.name,
                    "task_type": task.task_type.value,
                    "config": task.config,
                    "inputs": task.inputs,
                    "outputs": task.outputs,
                    "conditions": task.conditions,
                    "retry_count": task.retry_count,
                    "timeout_seconds": task.timeout_seconds,
                    "dependencies": task.dependencies
                }
                for task in workflow.tasks
            ],
            "variables": workflow.variables,
            "triggers": workflow.triggers,
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat(),
            "created_by": workflow.created_by
        }
    
    def _deserialize_workflow(self, data: Dict[str, Any]) -> WorkflowDefinition:
        """Deserialize workflow from dictionary"""
        tasks = []
        for task_data in data["tasks"]:
            task = TaskDefinition(
                task_id=task_data["task_id"],
                name=task_data["name"],
                task_type=TaskType(task_data["task_type"]),
                config=task_data["config"],
                inputs=task_data.get("inputs", []),
                outputs=task_data.get("outputs", []),
                conditions=task_data.get("conditions", []),
                retry_count=task_data.get("retry_count", 0),
                timeout_seconds=task_data.get("timeout_seconds", 300),
                dependencies=task_data.get("dependencies", [])
            )
            tasks.append(task)
        
        return WorkflowDefinition(
            workflow_id=data["workflow_id"],
            name=data["name"],
            description=data["description"],
            version=data["version"],
            status=WorkflowStatus(data["status"]),
            tasks=tasks,
            variables=data.get("variables", {}),
            triggers=data.get("triggers", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            created_by=data.get("created_by", "system")
        )
