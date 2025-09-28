#!/usr/bin/env python3
"""
Agent Communication Hub
Real-time communication system for 6-agent collective
"""

import asyncio
import json
import logging
from datetime import datetime

import websockets
from websockets.server import WebSocketServerProtocol

logger = logging.getLogger(__name__)


@dataclass
class AgentMessage:
    id: str
    from_agent: str
    to_agent: str
    message_type: str
    content: Any
    timestamp: datetime
    priority: int = 1  # 1-5, 5 being highest
    requires_response: bool = False
    response_to: Optional[str] = None


class AgentCommunicationHub:
    """Real-time communication hub for agent coordination"""

    def __init__(self, host: str = "localhost", port: int = 8766):
        self.host = host
        self.port = port
        self.connected_agents: Dict[str, WebSocketServerProtocol] = {}
        self.message_queue: deque = deque(maxlen=10000)
        self.message_handlers: Dict[str, Callable] = {}
        self.agent_status: Dict[str, Dict] = {}
        self.collaboration_sessions: Dict[str, List[str]] = {}

        # Message types
        self.MESSAGE_TYPES = {
            "task_assignment": self._handle_task_assignment,
            "task_update": self._handle_task_update,
            "collaboration_request": self._handle_collaboration_request,
            "peer_review": self._handle_peer_review,
            "escalation": self._handle_escalation,
            "workload_redistribution": self._handle_workload_redistribution,
            "system_status": self._handle_system_status,
            "gemini_cli_request": self._handle_gemini_cli_request,
        }

    async def start_hub(self):
        """Start the communication hub"""
        logger.info(f"🚀 Starting Agent Communication Hub on {self.host}:{self.port}")

        server = await websockets.serve(
            self._handle_agent_connection, self.host, self.port
        )

        logger.info("✅ Agent Communication Hub started successfully")
        await server.wait_closed()

    async def _handle_agent_connection(
        self, websocket: WebSocketServerProtocol, path: str
    ):
        """Handle new agent connection"""
        try:
            # Wait for agent registration
            message = await websocket.recv()
            data = json.loads(message)

            if data.get("type") == "agent_registration":
                agent_id = data.get("agent_id")
                agent_role = data.get("agent_role")

                if agent_id and agent_role:
                    await self._register_agent(websocket, agent_id, agent_role)
                    await self._handle_agent_messages(websocket, agent_id)
                else:
                    await websocket.close(code=1008, reason="Invalid registration")
            else:
                await websocket.close(code=1008, reason="Registration required")

        except websockets.exceptions.ConnectionClosed:
            logger.info("Agent connection closed")
        except Exception as e:
            logger.error(f"Error handling agent connection: {e}")

    async def _register_agent(
        self, websocket: WebSocketServerProtocol, agent_id: str, agent_role: str
    ):
        """Register a new agent"""
        self.connected_agents[agent_id] = websocket
        self.agent_status[agent_id] = {
            "role": agent_role,
            "status": "active",
            "last_activity": datetime.now().isoformat(),
            "workload": 0.0,
            "capabilities": self._get_agent_capabilities(agent_role),
        }

        logger.info(f"👤 Agent registered: {agent_id} ({agent_role})")

        # Send welcome message
        welcome_message = {
            "type": "welcome",
            "message": f"Welcome {agent_id}! You are now connected to the agent communication hub.",
            "agent_count": len(self.connected_agents),
            "timestamp": datetime.now().isoformat(),
        }

        await websocket.send(json.dumps(welcome_message))

    def _get_agent_capabilities(self, agent_role: str) -> List[str]:
        """Get capabilities for agent role"""
        capabilities = {
            "brain": ["orchestration", "scheduling", "decision_making", "escalation"],
            "builder": ["build_systems", "dependencies", "compilation", "runtime"],
            "backend": ["apis", "databases", "business_logic", "security"],
            "frontend": ["ui_design", "ux", "responsive_design", "comic_avatar_ui"],
            "integrator": [
                "integration",
                "api_connectivity",
                "data_flow",
                "compatibility",
            ],
            "quality_checker": ["testing", "linting", "code_review", "validation"],
            "automation": ["monitoring", "restart", "gemini_cli", "resilience"],
        }

        return capabilities.get(agent_role, [])

    async def _handle_agent_messages(
        self, websocket: WebSocketServerProtocol, agent_id: str
    ):
        """Handle messages from a specific agent"""
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self._process_agent_message(agent_id, data)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from agent {agent_id}")
                except Exception as e:
                    logger.error(f"Error processing message from {agent_id}: {e}")

        except websockets.exceptions.ConnectionClosed:
            await self._unregister_agent(agent_id)
        except Exception as e:
            logger.error(f"Error handling messages from {agent_id}: {e}")

    async def _unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.connected_agents:
            del self.connected_agents[agent_id]

        if agent_id in self.agent_status:
            self.agent_status[agent_id]["status"] = "disconnected"

        logger.info(f"👋 Agent unregistered: {agent_id}")

    async def _process_agent_message(self, agent_id: str, data: Dict[str, Any]):
        """Process a message from an agent"""
        message_type = data.get("type")

        if message_type in self.MESSAGE_TYPES:
            await self.MESSAGE_TYPES[message_type](agent_id, data)
        else:
            logger.warning(f"Unknown message type from {agent_id}: {message_type}")

    async def _handle_task_assignment(self, agent_id: str, data: Dict[str, Any]):
        """Handle task assignment message"""
        task_data = data.get("task")
        if task_data:
            # Forward to appropriate agent
            target_agent = task_data.get("assigned_agent")
            if target_agent in self.connected_agents:
                message = {
                    "type": "task_assignment",
                    "from": agent_id,
                    "task": task_data,
                    "timestamp": datetime.now().isoformat(),
                }
                await self._send_to_agent(target_agent, message)
                logger.info(
                    f"📋 Task assigned to {target_agent}: {task_data.get('title')}"
                )

    async def _handle_task_update(self, agent_id: str, data: Dict[str, Any]):
        """Handle task update message"""
        task_id = data.get("task_id")
        status = data.get("status")
        progress = data.get("progress", 0.0)

        # Update agent status
        if agent_id in self.agent_status:
            self.agent_status[agent_id]["workload"] = progress
            self.agent_status[agent_id]["last_activity"] = datetime.now().isoformat()

        # Broadcast update to all agents
        update_message = {
            "type": "task_update",
            "from": agent_id,
            "task_id": task_id,
            "status": status,
            "progress": progress,
            "timestamp": datetime.now().isoformat(),
        }

        await self._broadcast_to_all(update_message)
        logger.info(
            f"📊 Task update from {agent_id}: {task_id} - {status} ({progress}%)"
        )

    async def _handle_collaboration_request(self, agent_id: str, data: Dict[str, Any]):
        """Handle collaboration request"""
        task_id = data.get("task_id")
        required_capabilities = data.get("capabilities", [])

        # Find agents with required capabilities
        suitable_agents = []
        for aid, status in self.agent_status.items():
            if aid != agent_id and status["status"] == "active":
                agent_capabilities = status.get("capabilities", [])
                if any(cap in agent_capabilities for cap in required_capabilities):
                    suitable_agents.append(aid)

        # Send collaboration request to suitable agents
        for target_agent in suitable_agents:
            message = {
                "type": "collaboration_request",
                "from": agent_id,
                "task_id": task_id,
                "required_capabilities": required_capabilities,
                "timestamp": datetime.now().isoformat(),
            }
            await self._send_to_agent(target_agent, message)

        logger.info(
            f"🤝 Collaboration request from {agent_id} to {len(suitable_agents)} agents"
        )

    async def _handle_peer_review(self, agent_id: str, data: Dict[str, Any]):
        """Handle peer review request"""
        task_id = data.get("task_id")
        review_data = data.get("review_data")

        # Forward to quality checker
        qc_agents = [
            aid
            for aid, status in self.agent_status.items()
            if status.get("role") == "quality_checker" and status["status"] == "active"
        ]

        for qc_agent in qc_agents:
            message = {
                "type": "peer_review",
                "from": agent_id,
                "task_id": task_id,
                "review_data": review_data,
                "timestamp": datetime.now().isoformat(),
            }
            await self._send_to_agent(qc_agent, message)

        logger.info(f"🔍 Peer review request from {agent_id} to quality checkers")

    async def _handle_escalation(self, agent_id: str, data: Dict[str, Any]):
        """Handle escalation request"""
        task_id = data.get("task_id")
        escalation_reason = data.get("reason")
        escalation_level = data.get("level", "automation")

        if escalation_level == "automation":
            # Forward to automation agents
            automation_agents = [
                aid
                for aid, status in self.agent_status.items()
                if status.get("role") == "automation" and status["status"] == "active"
            ]

            for auto_agent in automation_agents:
                message = {
                    "type": "escalation",
                    "from": agent_id,
                    "task_id": task_id,
                    "reason": escalation_reason,
                    "level": escalation_level,
                    "timestamp": datetime.now().isoformat(),
                }
                await self._send_to_agent(auto_agent, message)

        elif escalation_level == "gemini_cli":
            # Forward to automation agents for Gemini CLI execution
            automation_agents = [
                aid
                for aid, status in self.agent_status.items()
                if status.get("role") == "automation" and status["status"] == "active"
            ]

            for auto_agent in automation_agents:
                message = {
                    "type": "gemini_cli_request",
                    "from": agent_id,
                    "task_id": task_id,
                    "reason": escalation_reason,
                    "timestamp": datetime.now().isoformat(),
                }
                await self._send_to_agent(auto_agent, message)

        logger.info(
            f"🚨 Escalation from {agent_id}: {escalation_reason} (level: {escalation_level})"
        )

    async def _handle_workload_redistribution(
        self, agent_id: str, data: Dict[str, Any]
    ):
        """Handle workload redistribution request"""
        overloaded_agent = data.get("overloaded_agent")
        underloaded_agent = data.get("underloaded_agent")
        task_id = data.get("task_id")

        if (
            overloaded_agent in self.connected_agents
            and underloaded_agent in self.connected_agents
        ):
            # Send redistribution message
            message = {
                "type": "workload_redistribution",
                "from": agent_id,
                "overloaded_agent": overloaded_agent,
                "underloaded_agent": underloaded_agent,
                "task_id": task_id,
                "timestamp": datetime.now().isoformat(),
            }

            await self._send_to_agent(underloaded_agent, message)
            logger.info(
                f"⚖️ Workload redistribution: {overloaded_agent} -> {underloaded_agent}"
            )

    async def _handle_system_status(self, agent_id: str, data: Dict[str, Any]):
        """Handle system status request"""
        status_data = {
            "type": "system_status_response",
            "connected_agents": len(self.connected_agents),
            "agent_status": self.agent_status,
            "message_queue_size": len(self.message_queue),
            "timestamp": datetime.now().isoformat(),
        }

        await self._send_to_agent(agent_id, status_data)
        logger.info(f"📊 System status sent to {agent_id}")

    async def _handle_gemini_cli_request(self, agent_id: str, data: Dict[str, Any]):
        """Handle Gemini CLI request"""
        task_id = data.get("task_id")
        command = data.get("command")

        # Forward to automation agents
        automation_agents = [
            aid
            for aid, status in self.agent_status.items()
            if status.get("role") == "automation" and status["status"] == "active"
        ]

        for auto_agent in automation_agents:
            message = {
                "type": "gemini_cli_execution",
                "from": agent_id,
                "task_id": task_id,
                "command": command,
                "timestamp": datetime.now().isoformat(),
            }
            await self._send_to_agent(auto_agent, message)

        logger.info(f"🔧 Gemini CLI request from {agent_id}: {command}")

    async def _send_to_agent(self, agent_id: str, message: Dict[str, Any]):
        """Send message to specific agent"""
        if agent_id in self.connected_agents:
            try:
                await self.connected_agents[agent_id].send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                await self._unregister_agent(agent_id)
            except Exception as e:
                logger.error(f"Error sending message to {agent_id}: {e}")

    async def _broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast message to all connected agents"""
        if self.connected_agents:
            disconnected_agents = []

            for agent_id, websocket in self.connected_agents.items():
                try:
                    await websocket.send(json.dumps(message))
                except websockets.exceptions.ConnectionClosed:
                    disconnected_agents.append(agent_id)
                except Exception as e:
                    logger.error(f"Error broadcasting to {agent_id}: {e}")

            # Clean up disconnected agents
            for agent_id in disconnected_agents:
                await self._unregister_agent(agent_id)


if __name__ == "__main__":
    # Test the communication hub
    async def test_hub():
        hub = AgentCommunicationHub()
        await hub.start_hub()

    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_hub())
