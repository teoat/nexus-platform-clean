#!/usr/bin/env python3
"""
NEXUS Platform - Advanced Parallel Task Processing System
Phase 2: Core Functionality Enhancement
"""

import asyncio
import logging
import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import json
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    RETRYING = "retrying"


@dataclass
class TaskResult:
    """Result of task execution"""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """Task definition"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    function: Optional[Callable] = None
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    timeout: Optional[float] = None
    max_retries: int = 3
    retry_delay: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    status: TaskStatus = TaskStatus.PENDING


class ParallelTaskProcessor:
    """Advanced parallel task processing system"""
    
    def __init__(self, 
                 max_workers: int = 10,
                 enable_threading: bool = True,
                 enable_multiprocessing: bool = False,
                 max_processes: int = 4):
        self.max_workers = max_workers
        self.enable_threading = enable_threading
        self.enable_multiprocessing = enable_multiprocessing
        self.max_processes = max_processes
        
        # Worker pools for different priorities
        self.worker_pools = {
            TaskPriority.CRITICAL: asyncio.Semaphore(2),
            TaskPriority.HIGH: asyncio.Semaphore(3),
            TaskPriority.MEDIUM: asyncio.Semaphore(3),
            TaskPriority.LOW: asyncio.Semaphore(2)
        }
        
        # Execution pools
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers) if enable_threading else None
        self.process_pool = ProcessPoolExecutor(max_workers=max_processes) if enable_multiprocessing else None
        
        # Task tracking
        self.tasks: Dict[str, Task] = {}
        self.results: Dict[str, TaskResult] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        
        # Statistics
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "total_execution_time": 0.0,
            "average_execution_time": 0.0
        }
    
    async def add_task(self, task: Task) -> str:
        """Add a task to the processor"""
        self.tasks[task.id] = task
        self.stats["total_tasks"] += 1
        logger.info(f"Added task: {task.name} (ID: {task.id})")
        return task.id
    
    async def add_tasks(self, tasks: List[Task]) -> List[str]:
        """Add multiple tasks to the processor"""
        task_ids = []
        for task in tasks:
            task_id = await self.add_task(task)
            task_ids.append(task_id)
        return task_ids
    
    def group_tasks_by_priority(self, tasks: List[Task]) -> Dict[TaskPriority, List[Task]]:
        """Group tasks by priority"""
        grouped = {
            TaskPriority.CRITICAL: [],
            TaskPriority.HIGH: [],
            TaskPriority.MEDIUM: [],
            TaskPriority.LOW: []
        }
        
        for task in tasks:
            grouped[task.priority].append(task)
        
        return grouped
    
    async def resolve_dependencies(self, tasks: List[Task]) -> List[Task]:
        """Resolve task dependencies and return execution order"""
        resolved = []
        remaining = tasks.copy()
        
        while remaining:
            # Find tasks with no unresolved dependencies
            ready_tasks = []
            for task in remaining:
                if all(dep_id in [t.id for t in resolved] for dep_id in task.dependencies):
                    ready_tasks.append(task)
            
            if not ready_tasks:
                # Circular dependency or missing dependency
                logger.error("Circular dependency or missing dependency detected")
                break
            
            # Add ready tasks to resolved list
            resolved.extend(ready_tasks)
            
            # Remove ready tasks from remaining
            for task in ready_tasks:
                remaining.remove(task)
        
        return resolved
    
    async def process_task_enhanced(self, task: Task) -> TaskResult:
        """Process a single task with enhanced error handling and retries"""
        start_time = time.time()
        task.status = TaskStatus.RUNNING
        
        logger.info(f"Processing task: {task.name} (Priority: {task.priority.value})")
        
        for attempt in range(task.max_retries + 1):
            try:
                # Execute the task
                if asyncio.iscoroutinefunction(task.function):
                    result = await asyncio.wait_for(
                        task.function(*task.args, **task.kwargs),
                        timeout=task.timeout
                    )
                else:
                    # Run in thread pool for blocking functions
                    if self.thread_pool:
                        result = await asyncio.get_event_loop().run_in_executor(
                            self.thread_pool,
                            lambda: task.function(*task.args, **task.kwargs)
                        )
                    else:
                        result = task.function(*task.args, **task.kwargs)
                
                # Task completed successfully
                execution_time = time.time() - start_time
                task_result = TaskResult(
                    task_id=task.id,
                    status=TaskStatus.COMPLETED,
                    result=result,
                    execution_time=execution_time,
                    retry_count=attempt,
                    metadata=task.metadata
                )
                
                self.results[task.id] = task_result
                self.stats["completed_tasks"] += 1
                self.stats["total_execution_time"] += execution_time
                
                logger.info(f"Task completed: {task.name} (Time: {execution_time:.2f}s)")
                return task_result
                
            except asyncio.TimeoutError:
                error_msg = f"Task timeout after {task.timeout}s"
                logger.warning(f"Task timeout: {task.name} (Attempt {attempt + 1})")
                
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Task error: {task.name} - {error_msg} (Attempt {attempt + 1})")
            
            # If this wasn't the last attempt, wait before retrying
            if attempt < task.max_retries:
                await asyncio.sleep(task.retry_delay * (2 ** attempt))  # Exponential backoff
        
        # All retries failed
        execution_time = time.time() - start_time
        task_result = TaskResult(
            task_id=task.id,
            status=TaskStatus.FAILED,
            error=error_msg,
            execution_time=execution_time,
            retry_count=task.max_retries,
            metadata=task.metadata
        )
        
        self.results[task.id] = task_result
        self.stats["failed_tasks"] += 1
        self.stats["total_execution_time"] += execution_time
        
        logger.error(f"Task failed: {task.name} - {error_msg}")
        return task_result
    
    async def process_priority_group(self, priority: TaskPriority, tasks: List[Task]) -> List[TaskResult]:
        """Process tasks within a priority group in parallel"""
        if not tasks:
            return []
        
        semaphore = self.worker_pools.get(priority, asyncio.Semaphore(self.max_workers))
        
        async def process_with_semaphore(task):
            async with semaphore:
                return await self.process_task_enhanced(task)
        
        # Create tasks for parallel execution
        task_futures = [process_with_semaphore(task) for task in tasks]
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*task_futures, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(TaskResult(
                    task_id=tasks[i].id,
                    status=TaskStatus.FAILED,
                    error=str(result),
                    metadata=tasks[i].metadata
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def process_tasks_parallel(self, tasks: List[Task]) -> List[TaskResult]:
        """Process tasks in parallel with priority-based worker allocation"""
        logger.info(f"Starting parallel processing of {len(tasks)} tasks")
        
        # Resolve dependencies
        resolved_tasks = await self.resolve_dependencies(tasks)
        
        # Group tasks by priority
        tasks_by_priority = self.group_tasks_by_priority(resolved_tasks)
        
        # Process each priority group in parallel
        all_results = []
        for priority in [TaskPriority.CRITICAL, TaskPriority.HIGH, TaskPriority.MEDIUM, TaskPriority.LOW]:
            priority_tasks = tasks_by_priority[priority]
            if priority_tasks:
                logger.info(f"Processing {len(priority_tasks)} {priority.value} priority tasks")
                priority_results = await self.process_priority_group(priority, priority_tasks)
                all_results.extend(priority_results)
        
        # Update statistics
        if self.stats["completed_tasks"] > 0:
            self.stats["average_execution_time"] = (
                self.stats["total_execution_time"] / self.stats["completed_tasks"]
            )
        
        logger.info(f"Parallel processing completed: {len(all_results)} results")
        return all_results
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            if task_id in self.tasks:
                self.tasks[task_id].status = TaskStatus.CANCELLED
            logger.info(f"Cancelled task: {task_id}")
            return True
        return False
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a task"""
        if task_id in self.tasks:
            return self.tasks[task_id].status
        return None
    
    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get the result of a completed task"""
        return self.results.get(task_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            **self.stats,
            "active_tasks": len(self.running_tasks),
            "pending_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
            "success_rate": (
                self.stats["completed_tasks"] / max(self.stats["total_tasks"], 1) * 100
            )
        }
    
    async def shutdown(self):
        """Shutdown the processor and clean up resources"""
        logger.info("Shutting down parallel task processor...")
        
        # Cancel all running tasks
        for task_id in list(self.running_tasks.keys()):
            await self.cancel_task(task_id)
        
        # Shutdown thread and process pools
        if self.thread_pool:
            self.thread_pool.shutdown(wait=True)
        
        if self.process_pool:
            self.process_pool.shutdown(wait=True)
        
        logger.info("Parallel task processor shutdown complete")


# Example usage and testing
async def example_task(name: str, duration: float = 1.0) -> str:
    """Example task function"""
    await asyncio.sleep(duration)
    return f"Task {name} completed in {duration}s"


async def main():
    """Example usage of the parallel task processor"""
    processor = ParallelTaskProcessor(max_workers=5)
    
    # Create example tasks
    tasks = [
        Task(
            name="Critical Task 1",
            priority=TaskPriority.CRITICAL,
            function=example_task,
            args=("Critical-1", 2.0)
        ),
        Task(
            name="High Priority Task 1",
            priority=TaskPriority.HIGH,
            function=example_task,
            args=("High-1", 1.5)
        ),
        Task(
            name="High Priority Task 2",
            priority=TaskPriority.HIGH,
            function=example_task,
            args=("High-2", 1.0)
        ),
        Task(
            name="Medium Priority Task 1",
            priority=TaskPriority.MEDIUM,
            function=example_task,
            args=("Medium-1", 0.5)
        ),
        Task(
            name="Medium Priority Task 2",
            priority=TaskPriority.MEDIUM,
            function=example_task,
            args=("Medium-2", 0.8)
        ),
        Task(
            name="Low Priority Task 1",
            priority=TaskPriority.LOW,
            function=example_task,
            args=("Low-1", 0.3)
        )
    ]
    
    # Process tasks in parallel
    start_time = time.time()
    results = await processor.process_tasks_parallel(tasks)
    total_time = time.time() - start_time
    
    # Display results
    print(f"\n🎉 Parallel Processing Complete!")
    print(f"Total execution time: {total_time:.2f}s")
    print(f"Tasks processed: {len(results)}")
    
    # Show statistics
    stats = processor.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"Success rate: {stats['success_rate']:.1f}%")
    print(f"Average execution time: {stats['average_execution_time']:.2f}s")
    
    # Show individual results
    print(f"\n📋 Task Results:")
    for result in results:
        status_emoji = "✅" if result.status == TaskStatus.COMPLETED else "❌"
        print(f"{status_emoji} {result.task_id}: {result.status.value} ({result.execution_time:.2f}s)")
    
    # Cleanup
    await processor.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
