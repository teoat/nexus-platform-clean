#!/usr/bin/env python3
"""
Frenly AI Brain Orchestrator
Central coordinator for 6-agent collective system with dynamic workflow management
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    STUCK = "stuck"
    REVIEWING = "reviewing"


class AgentRole(Enum):
    BRAIN = "brain"
    BUILDER = "builder"
    BACKEND = "backend"
    FRONTEND = "frontend"
    INTEGRATOR = "integrator"
    QUALITY_CHECKER = "quality_checker"
    AUTOMATION = "automation"


@dataclass
class Task:
    id: str
    title: str
    description: str
    assigned_agent: AgentRole
    status: TaskStatus
    priority: int  # 1-5, 5 being highest
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    dependencies: List[str] = None
    tags: List[str] = None
    progress: float = 0.0
    error_message: Optional[str] = None
    review_notes: List[str] = None


@dataclass
class Agent:
    role: AgentRole
    status: str
    current_task: Optional[str] = None
    workload: float = 0.0
    capabilities: List[str] = None
    last_activity: datetime = None
    performance_score: float = 1.0


class FrenlyBrainOrchestrator:
    """Central brain orchestrator for 6-agent collective system"""

    def __init__(self):
        self.agents = self._initialize_agents()
        self.tasks = {}
        self.task_queue = deque()
        self.completed_tasks = deque(maxlen=1000)
        self.workflow_cycles = deque(maxlen=100)
        self.peer_reviews = defaultdict(list)
        self.gemini_cli_usage = deque(maxlen=100)
        self.system_health = {
            "overall_status": "healthy",
            "active_agents": 0,
            "pending_tasks": 0,
            "failed_tasks": 0,
            "last_cycle": None,
        }

        # Workflow phases
        self.current_phase = "planning"
        self.phase_start_time = datetime.now()

        # Dynamic redistribution settings
        self.workload_threshold = 0.8
        self.stuck_task_timeout = 300  # 5 minutes
        self.peer_review_required = True

    def _initialize_agents(self) -> Dict[AgentRole, Agent]:
        """Initialize all 6 agents with their capabilities"""
        agents = {}

        agents[AgentRole.BRAIN] = Agent(
            role=AgentRole.BRAIN,
            status="active",
            capabilities=[
                "orchestration",
                "scheduling",
                "decision_making",
                "escalation",
            ],
            last_activity=datetime.now(),
        )

        agents[AgentRole.BUILDER] = Agent(
            role=AgentRole.BUILDER,
            status="idle",
            capabilities=["build_systems", "dependencies", "compilation", "runtime"],
            last_activity=datetime.now(),
        )

        agents[AgentRole.BACKEND] = Agent(
            role=AgentRole.BACKEND,
            status="idle",
            capabilities=["apis", "databases", "business_logic", "security"],
            last_activity=datetime.now(),
        )

        agents[AgentRole.FRONTEND] = Agent(
            role=AgentRole.FRONTEND,
            status="idle",
            capabilities=["ui_design", "ux", "responsive_design", "comic_avatar_ui"],
            last_activity=datetime.now(),
        )

        agents[AgentRole.INTEGRATOR] = Agent(
            role=AgentRole.INTEGRATOR,
            status="idle",
            capabilities=[
                "integration",
                "api_connectivity",
                "data_flow",
                "compatibility",
            ],
            last_activity=datetime.now(),
        )

        agents[AgentRole.QUALITY_CHECKER] = Agent(
            role=AgentRole.QUALITY_CHECKER,
            status="idle",
            capabilities=["testing", "linting", "code_review", "validation"],
            last_activity=datetime.now(),
        )

        agents[AgentRole.AUTOMATION] = Agent(
            role=AgentRole.AUTOMATION,
            status="idle",
            capabilities=["monitoring", "restart", "gemini_cli", "resilience"],
            last_activity=datetime.now(),
        )

        return agents

    async def start_workflow_cycle(self):
        """Start the main workflow cycle"""
        logger.info("🧠 Frenly Brain starting workflow cycle")

        while True:
            try:
                await self._execute_workflow_phase()
                await asyncio.sleep(10)  # Check every 10 seconds
            except Exception as e:
                logger.error(f"Workflow cycle error: {e}")
                await self._handle_critical_error(e)

    async def _execute_workflow_phase(self):
        """Execute current workflow phase"""
        current_time = datetime.now()

        # Phase 1: Planning
        if self.current_phase == "planning":
            await self._planning_phase()

        # Phase 2: Execution
        elif self.current_phase == "execution":
            await self._execution_phase()

        # Phase 3: Review
        elif self.current_phase == "review":
            await self._review_phase()

        # Phase 4: Resilience
        elif self.current_phase == "resilience":
            await self._resilience_phase()

        # Phase 5: Merge
        elif self.current_phase == "merge":
            await self._merge_phase()

        # Check for phase transitions
        await self._check_phase_transition()

    async def _planning_phase(self):
        """Phase 1: Break down tasks and assign to agents"""
        logger.info("📋 Planning phase: Breaking down tasks")

        # Check for new tasks to assign
        if self.task_queue:
            task = self.task_queue.popleft()
            await self._assign_task(task)

        # Check for dynamic redistribution
        await self._check_workload_balance()

        # Update system status
        self.system_health["pending_tasks"] = len(self.task_queue)
        self.system_health["active_agents"] = len(
            [a for a in self.agents.values() if a.status == "active"]
        )

    async def _execution_phase(self):
        """Phase 2: Agents work in parallel on assigned tasks"""
        logger.info("⚡ Execution phase: Agents working in parallel")

        # Monitor active agents
        for agent_role, agent in self.agents.items():
            if agent.status == "active" and agent.current_task:
                task = self.tasks.get(agent.current_task)
                if task:
                    await self._monitor_task_progress(task, agent)

        # Check for stuck tasks
        await self._detect_stuck_tasks()

    async def _review_phase(self):
        """Phase 3: Quality checker reviews all outputs"""
        logger.info("🔍 Review phase: Quality checking outputs")

        # Get all completed tasks that need review
        pending_review = [
            t
            for t in self.tasks.values()
            if t.status == TaskStatus.COMPLETED and not t.review_notes
        ]

        for task in pending_review:
            await self._initiate_peer_review(task)

    async def _resilience_phase(self):
        """Phase 4: Monitor for failures and trigger recovery"""
        logger.info("🛡️ Resilience phase: Monitoring system health")

        # Check for failed tasks
        failed_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.FAILED]

        for task in failed_tasks:
            await self._handle_failed_task(task)

        # Check for stuck processes
        await self._check_stuck_processes()

        # Update system health
        self.system_health["failed_tasks"] = len(failed_tasks)

    async def _merge_phase(self):
        """Phase 5: Merge validated outputs into system"""
        logger.info("🔗 Merge phase: Integrating validated outputs")

        # Get all reviewed and approved tasks
        ready_to_merge = [
            t
            for t in self.tasks.values()
            if t.status == TaskStatus.COMPLETED and t.review_notes
        ]

        for task in ready_to_merge:
            await self._merge_task_output(task)

    async def _check_phase_transition(self):
        """Check if we should transition to next phase"""
        current_time = datetime.now()
        phase_duration = (current_time - self.phase_start_time).total_seconds()

        # Phase transition logic
        if self.current_phase == "planning" and phase_duration > 30:
            self.current_phase = "execution"
            self.phase_start_time = current_time
            logger.info("🔄 Transitioning to execution phase")

        elif self.current_phase == "execution" and phase_duration > 300:  # 5 minutes
            self.current_phase = "review"
            self.phase_start_time = current_time
            logger.info("🔄 Transitioning to review phase")

        elif self.current_phase == "review" and phase_duration > 60:
            self.current_phase = "resilience"
            self.phase_start_time = current_time
            logger.info("🔄 Transitioning to resilience phase")

        elif self.current_phase == "resilience" and phase_duration > 30:
            self.current_phase = "merge"
            self.phase_start_time = current_time
            logger.info("🔄 Transitioning to merge phase")

        elif self.current_phase == "merge" and phase_duration > 60:
            self.current_phase = "planning"
            self.phase_start_time = current_time
            logger.info("🔄 Transitioning to planning phase")

    async def create_task(
        self,
        title: str,
        description: str,
        priority: int = 3,
        tags: List[str] = None,
        dependencies: List[str] = None,
    ) -> str:
        """Create a new task and add to queue"""
        task_id = f"task_{int(time.time())}_{len(self.tasks)}"

        task = Task(
            id=task_id,
            title=title,
            description=description,
            assigned_agent=AgentRole.BRAIN,  # Will be reassigned
            status=TaskStatus.PENDING,
            priority=priority,
            created_at=datetime.now(),
            tags=tags or [],
            dependencies=dependencies or [],
        )

        self.tasks[task_id] = task
        self.task_queue.append(task_id)

        logger.info(f"📝 Created task: {title} (ID: {task_id})")
        return task_id

    async def _assign_task(self, task_id: str):
        """Assign task to most suitable agent"""
        task = self.tasks[task_id]

        # Find best agent based on capabilities and workload
        best_agent = await self._find_best_agent_for_task(task)

        if best_agent:
            task.assigned_agent = best_agent
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now()

            # Update agent status
            self.agents[best_agent].status = "active"
            self.agents[best_agent].current_task = task_id
            self.agents[best_agent].last_activity = datetime.now()

            logger.info(f"👤 Assigned task {task.title} to {best_agent.value}")
        else:
            logger.warning(f"⚠️ No available agent for task {task.title}")

    async def _find_best_agent_for_task(self, task: Task) -> Optional[AgentRole]:
        """Find the best agent for a given task"""
        # Simple capability matching for now
        task_keywords = task.title.lower() + " " + task.description.lower()

        if any(
            keyword in task_keywords for keyword in ["build", "compile", "dependency"]
        ):
            return AgentRole.BUILDER
        elif any(
            keyword in task_keywords
            for keyword in ["api", "backend", "database", "server"]
        ):
            return AgentRole.BACKEND
        elif any(
            keyword in task_keywords
            for keyword in ["ui", "frontend", "design", "avatar"]
        ):
            return AgentRole.FRONTEND
        elif any(
            keyword in task_keywords for keyword in ["integrate", "connect", "bridge"]
        ):
            return AgentRole.INTEGRATOR
        elif any(
            keyword in task_keywords
            for keyword in ["test", "review", "quality", "lint"]
        ):
            return AgentRole.QUALITY_CHECKER
        else:
            # Default to least loaded agent
            return await self._get_least_loaded_agent()

    async def _get_least_loaded_agent(self) -> Optional[AgentRole]:
        """Get the agent with the least workload"""
        available_agents = [
            role
            for role, agent in self.agents.items()
            if agent.status == "idle" and role != AgentRole.BRAIN
        ]

        if not available_agents:
            return None

        return min(available_agents, key=lambda role: self.agents[role].workload)

    async def _check_workload_balance(self):
        """Check if agents need workload redistribution"""
        active_agents = [
            agent for agent in self.agents.values() if agent.status == "active"
        ]

        if not active_agents:
            return

        # Find overloaded and underloaded agents
        avg_workload = sum(agent.workload for agent in active_agents) / len(
            active_agents
        )

        overloaded = [
            agent for agent in active_agents if agent.workload > avg_workload * 1.5
        ]
        underloaded = [
            agent for agent in active_agents if agent.workload < avg_workload * 0.5
        ]

        # Redistribute work
        for overloaded_agent in overloaded:
            if underloaded:
                await self._redistribute_work(overloaded_agent, underloaded[0])

    async def _redistribute_work(self, from_agent: Agent, to_agent: Agent):
        """Redistribute work from overloaded to underloaded agent"""
        if from_agent.current_task:
            task = self.tasks[from_agent.current_task]

            # Reassign task
            task.assigned_agent = to_agent.role
            from_agent.current_task = None
            from_agent.status = "idle"

            to_agent.current_task = task.id
            to_agent.status = "active"
            to_agent.last_activity = datetime.now()

            logger.info(
                f"🔄 Redistributed task {task.title} from {from_agent.role.value} to {to_agent.role.value}"
            )

    async def _monitor_task_progress(self, task: Task, agent: Agent):
        """Monitor task progress and update status"""
        # Simulate progress monitoring
        if task.status == TaskStatus.IN_PROGRESS:
            # Update progress (simplified)
            task.progress = min(task.progress + 0.1, 1.0)

            if task.progress >= 1.0:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                agent.status = "idle"
                agent.current_task = None
                agent.workload = 0.0

                logger.info(f"✅ Task completed: {task.title}")

    async def _detect_stuck_tasks(self):
        """Detect tasks that are stuck and need intervention"""
        current_time = datetime.now()

        for task in self.tasks.values():
            if task.status == TaskStatus.IN_PROGRESS and task.started_at:
                stuck_duration = (current_time - task.started_at).total_seconds()

                if stuck_duration > self.stuck_task_timeout:
                    task.status = TaskStatus.STUCK
                    logger.warning(
                        f"⚠️ Task stuck: {task.title} (stuck for {stuck_duration}s)"
                    )

                    # Trigger automation agent
                    await self._trigger_automation_intervention(task)

    async def _trigger_automation_intervention(self, task: Task):
        """Trigger automation agent to handle stuck task"""
        automation_agent = self.agents[AgentRole.AUTOMATION]

        # Try to restart the task
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()
        task.progress = 0.0

        automation_agent.status = "active"
        automation_agent.current_task = task.id
        automation_agent.last_activity = datetime.now()

        logger.info(f"🔧 Automation agent intervening on stuck task: {task.title}")

    async def _initiate_peer_review(self, task: Task):
        """Initiate peer review for completed task"""
        if not self.peer_review_required:
            return

        # Assign to quality checker
        qc_agent = self.agents[AgentRole.QUALITY_CHECKER]
        qc_agent.status = "active"
        qc_agent.current_task = task.id

        task.status = TaskStatus.REVIEWING

        # Simulate review process
        review_notes = [
            f"Code quality: {'Good' if task.priority < 4 else 'Needs improvement'}",
            f"Performance: {'Optimal' if task.priority < 3 else 'Acceptable'}",
            f"Security: {'Secure' if 'security' not in task.tags else 'Needs review'}",
        ]

        task.review_notes = review_notes
        self.peer_reviews[task.id] = review_notes

        logger.info(f"🔍 Peer review initiated for task: {task.title}")

    async def _handle_failed_task(self, task: Task):
        """Handle failed task with recovery options"""
        logger.error(f"❌ Task failed: {task.title} - {task.error_message}")

        # Try to reassign to different agent
        if task.assigned_agent != AgentRole.AUTOMATION:
            await self._escalate_to_automation(task)
        else:
            # Escalate to Gemini CLI
            await self._escalate_to_gemini_cli(task)

    async def _escalate_to_automation(self, task: Task):
        """Escalate failed task to automation agent"""
        automation_agent = self.agents[AgentRole.AUTOMATION]

        # Reset task
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()
        task.progress = 0.0
        task.assigned_agent = AgentRole.AUTOMATION

        automation_agent.status = "active"
        automation_agent.current_task = task.id
        automation_agent.last_activity = datetime.now()

        logger.info(f"🔧 Escalated task to automation agent: {task.title}")

    async def _escalate_to_gemini_cli(self, task: Task):
        """Escalate to Gemini CLI as final fallback"""
        logger.info(f"🚀 Escalating to Gemini CLI: {task.title}")

        # Record Gemini CLI usage
        self.gemini_cli_usage.append(
            {
                "task_id": task.id,
                "task_title": task.title,
                "timestamp": datetime.now().isoformat(),
                "reason": "task_failure_escalation",
            }
        )

        # Try to execute Gemini CLI command
        try:
            result = await self._execute_gemini_cli_command(task)
            if result["success"]:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                logger.info(f"✅ Gemini CLI resolved task: {task.title}")
            else:
                logger.error(f"❌ Gemini CLI failed: {result['error']}")
        except Exception as e:
            logger.error(f"❌ Gemini CLI execution error: {e}")

    async def _execute_gemini_cli_command(self, task: Task) -> Dict[str, Any]:
        """Execute Gemini CLI command for task resolution"""
        # This would integrate with actual Gemini CLI
        # For now, simulate the command execution

        command = (
            f"gemini analyze --task '{task.title}' --description '{task.description}'"
        )

        try:
            # Simulate command execution
            result = {
                "success": True,
                "output": f"Gemini CLI analyzed task: {task.title}",
                "command": command,
            }

            logger.info(f"🔧 Executed Gemini CLI command: {command}")
            return result

        except Exception as e:
            return {"success": False, "error": str(e), "command": command}

    async def _check_stuck_processes(self):
        """Check for stuck processes and restart them"""
        # This would check actual system processes
        # For now, simulate the check
        pass

    async def _merge_task_output(self, task: Task):
        """Merge validated task output into system"""
        logger.info(f"🔗 Merging task output: {task.title}")

        # Move to completed tasks
        self.completed_tasks.append(task)

        # Update system health
        self.system_health["last_cycle"] = datetime.now().isoformat()

        # Log workflow cycle completion
        self.workflow_cycles.append(
            {
                "cycle_id": len(self.workflow_cycles) + 1,
                "completed_tasks": 1,
                "timestamp": datetime.now().isoformat(),
                "phase": self.current_phase,
            }
        )

    async def _handle_critical_error(self, error: Exception):
        """Handle critical system errors"""
        logger.error(f"💥 Critical error: {error}")

        # Reset all agents to idle
        for agent in self.agents.values():
            agent.status = "idle"
            agent.current_task = None

        # Reset workflow phase
        self.current_phase = "planning"
        self.phase_start_time = datetime.now()

        # Update system health
        self.system_health["overall_status"] = "error"


if __name__ == "__main__":
    # Test the orchestrator
    async def test_orchestrator():
        orchestrator = FrenlyBrainOrchestrator()

        # Create some test tasks
        await orchestrator.create_task(
            "Fix authentication bug",
            "Resolve JWT token validation issue in backend",
            priority=4,
            tags=["backend", "security", "bug"],
        )

        await orchestrator.create_task(
            "Implement Frenly AI avatar",
            "Create comic character avatar component for frontend",
            priority=5,
            tags=["frontend", "ui", "avatar"],
        )

        # Start workflow cycle
        await orchestrator.start_workflow_cycle()

    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_orchestrator())
