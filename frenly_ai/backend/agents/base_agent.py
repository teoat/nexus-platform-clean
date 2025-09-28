#!/usr/bin/env python3
"""
Base Agent Class
Foundation for all 6 agents in the Frenly AI collective
"""

import json
import logging
from datetime import datetime

import websockets

logger = logging.getLogger(__name__)


@dataclass
class AgentCapabilities:
    """Agent capabilities and skills"""

    primary_skills: List[str]
    secondary_skills: List[str]
    collaboration_skills: List[str]
    escalation_threshold: float = 0.8


class BaseAgent(ABC):
    """Base class for all Frenly AI agents"""

    def __init__(self, agent_id: str, agent_role: str, capabilities: AgentCapabilities):
        self.agent_id = agent_id
        self.agent_role = agent_role
        self.capabilities = capabilities
        self.status = "idle"
        self.current_task = None
        self.workload = 0.0
        self.performance_score = 1.0
        self.collaboration_partners = []
        self.message_handlers = {}
        self.websocket = None
        self.hub_url = "ws://localhost:8766"

        # Initialize message handlers
        self._setup_message_handlers()

    def _setup_message_handlers(self):
        """Setup message handlers for different message types"""
        self.message_handlers = {
            "task_assignment": self._handle_task_assignment,
            "collaboration_request": self._handle_collaboration_request,
            "peer_review": self._handle_peer_review,
            "escalation": self._handle_escalation,
            "workload_redistribution": self._handle_workload_redistribution,
            "system_status": self._handle_system_status,
            "gemini_cli_execution": self._handle_gemini_cli_execution,
        }

    async def connect_to_hub(self):
        """Connect to the agent communication hub"""
        try:
            self.websocket = await websockets.connect(self.hub_url)

            # Register with hub
            registration = {
                "type": "agent_registration",
                "agent_id": self.agent_id,
                "agent_role": self.agent_role,
                "capabilities": self.capabilities.primary_skills,
                "timestamp": datetime.now().isoformat(),
            }

            await self.websocket.send(json.dumps(registration))
            logger.info(f"🤖 {self.agent_id} connected to communication hub")

            # Start listening for messages
            await self._listen_for_messages()

        except Exception as e:
            logger.error(f"Error connecting {self.agent_id} to hub: {e}")

    async def _listen_for_messages(self):
        """Listen for messages from the communication hub"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._process_message(data)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received by {self.agent_id}")
                except Exception as e:
                    logger.error(f"Error processing message in {self.agent_id}: {e}")

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed for {self.agent_id}")
        except Exception as e:
            logger.error(f"Error in message listener for {self.agent_id}: {e}")

    async def _process_message(self, data: Dict[str, Any]):
        """Process incoming message"""
        message_type = data.get("type")

        if message_type in self.message_handlers:
            await self.message_handlers[message_type](data)
        else:
            logger.warning(
                f"Unknown message type received by {self.agent_id}: {message_type}"
            )

    async def _handle_task_assignment(self, data: Dict[str, Any]):
        """Handle task assignment"""
        task = data.get("task")
        if task:
            self.current_task = task
            self.status = "active"
            self.workload = 0.0

            logger.info(f"📋 {self.agent_id} received task: {task.get('title')}")

            # Start working on task
            await self._work_on_task(task)

    async def _handle_collaboration_request(self, data: Dict[str, Any]):
        """Handle collaboration request"""
        task_id = data.get("task_id")
        required_capabilities = data.get("required_capabilities", [])

        # Check if we have required capabilities
        if any(
            cap in self.capabilities.primary_skills for cap in required_capabilities
        ):
            if (
                self.status == "idle"
                or self.workload < self.capabilities.escalation_threshold
            ):
                # Accept collaboration
                await self._send_message(
                    {
                        "type": "collaboration_acceptance",
                        "from": self.agent_id,
                        "task_id": task_id,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                self.collaboration_partners.append(data.get("from"))
                logger.info(
                    f"🤝 {self.agent_id} accepted collaboration on task {task_id}"
                )
            else:
                # Decline due to workload
                await self._send_message(
                    {
                        "type": "collaboration_decline",
                        "from": self.agent_id,
                        "task_id": task_id,
                        "reason": "high_workload",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

    async def _handle_peer_review(self, data: Dict[str, Any]):
        """Handle peer review request"""
        task_id = data.get("task_id")
        review_data = data.get("review_data")

        # Perform peer review
        review_result = await self._perform_peer_review(task_id, review_data)

        await self._send_message(
            {
                "type": "peer_review_result",
                "from": self.agent_id,
                "task_id": task_id,
                "review_result": review_result,
                "timestamp": datetime.now().isoformat(),
            }
        )

    async def _handle_escalation(self, data: Dict[str, Any]):
        """Handle escalation request"""
        task_id = data.get("task_id")
        reason = data.get("reason")

        logger.info(f"🚨 {self.agent_id} handling escalation: {reason}")

        # Try to resolve the escalated task
        resolution = await self._handle_escalated_task(task_id, reason)

        await self._send_message(
            {
                "type": "escalation_resolution",
                "from": self.agent_id,
                "task_id": task_id,
                "resolution": resolution,
                "timestamp": datetime.now().isoformat(),
            }
        )

    async def _handle_workload_redistribution(self, data: Dict[str, Any]):
        """Handle workload redistribution"""
        task_id = data.get("task_id")

        if self.status == "idle" or self.workload < 0.5:
            # Accept redistributed task
            await self._send_message(
                {
                    "type": "redistribution_acceptance",
                    "from": self.agent_id,
                    "task_id": task_id,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            logger.info(f"⚖️ {self.agent_id} accepted redistributed task {task_id}")

    async def _handle_system_status(self, data: Dict[str, Any]):
        """Handle system status request"""
        status = {
            "agent_id": self.agent_id,
            "agent_role": self.agent_role,
            "status": self.status,
            "workload": self.workload,
            "current_task": self.current_task,
            "performance_score": self.performance_score,
            "timestamp": datetime.now().isoformat(),
        }

        await self._send_message(
            {
                "type": "agent_status_response",
                "from": self.agent_id,
                "status": status,
                "timestamp": datetime.now().isoformat(),
            }
        )

    async def _handle_gemini_cli_execution(self, data: Dict[str, Any]):
        """Handle Gemini CLI execution request"""
        task_id = data.get("task_id")
        command = data.get("command")

        logger.info(f"🔧 {self.agent_id} executing Gemini CLI: {command}")

        # Execute Gemini CLI command
        result = await self._execute_gemini_cli(command)

        await self._send_message(
            {
                "type": "gemini_cli_result",
                "from": self.agent_id,
                "task_id": task_id,
                "command": command,
                "result": result,
                "timestamp": datetime.now().isoformat(),
            }
        )

    @abstractmethod
    async def _work_on_task(self, task: Dict[str, Any]):
        """Work on assigned task - must be implemented by subclasses"""
        pass

    @abstractmethod
    async def _perform_peer_review(
        self, task_id: str, review_data: Any
    ) -> Dict[str, Any]:
        """Perform peer review - must be implemented by subclasses"""
        pass

    async def _handle_escalated_task(self, task_id: str, reason: str) -> Dict[str, Any]:
        """Handle escalated task - can be overridden by subclasses"""
        return {
            "status": "escalated",
            "reason": reason,
            "action": "forwarded_to_automation",
        }

    async def _execute_gemini_cli(self, command: str) -> Dict[str, Any]:
        """Execute Gemini CLI command - can be overridden by subclasses"""
        # Default implementation - would integrate with actual Gemini CLI
        return {
            "success": True,
            "output": f"Gemini CLI command executed: {command}",
            "command": command,
        }

    async def _send_message(self, message: Dict[str, Any]):
        """Send message to communication hub"""
        if self.websocket:
            try:
                await self.websocket.send(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message from {self.agent_id}: {e}")

    async def update_task_progress(
        self, task_id: str, progress: float, status: str = "in_progress"
    ):
        """Update task progress"""
        self.workload = progress

        await self._send_message(
            {
                "type": "task_update",
                "from": self.agent_id,
                "task_id": task_id,
                "status": status,
                "progress": progress,
                "timestamp": datetime.now().isoformat(),
            }
        )

    async def complete_task(self, task_id: str, result: Dict[str, Any]):
        """Complete task and send result"""
        self.status = "idle"
        self.current_task = None
        self.workload = 0.0

        await self._send_message(
            {
                "type": "task_completion",
                "from": self.agent_id,
                "task_id": task_id,
                "result": result,
                "timestamp": datetime.now().isoformat(),
            }
        )

        logger.info(f"✅ {self.agent_id} completed task {task_id}")

    async def request_collaboration(
        self, task_id: str, required_capabilities: List[str]
    ):
        """Request collaboration from other agents"""
        await self._send_message(
            {
                "type": "collaboration_request",
                "from": self.agent_id,
                "task_id": task_id,
                "capabilities": required_capabilities,
                "timestamp": datetime.now().isoformat(),
            }
        )

    async def escalate_task(self, task_id: str, reason: str, level: str = "automation"):
        """Escalate task to higher level"""
        await self._send_message(
            {
                "type": "escalation",
                "from": self.agent_id,
                "task_id": task_id,
                "reason": reason,
                "level": level,
                "timestamp": datetime.now().isoformat(),
            }
        )

    async def start(self):
        """Start the agent"""
        logger.info(f"🚀 Starting {self.agent_id} ({self.agent_role})")
        await self.connect_to_hub()
