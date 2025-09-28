#!/usr/bin/env python3
"""
Frenly AI WebSocket Server
Real-time communication hub for Frenly AI avatar interactions
"""

import asyncio
import json
import logging
from datetime import datetime

import websockets
from websockets.server import WebSocketServerProtocol

logger = logging.getLogger(__name__)


class FrenlyWebSocketServer:
    """WebSocket server for Frenly AI real-time communication"""

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.frenly_agent = FrenlyMetaAgent()
        self.message_history: List[Dict] = []

    async def register_client(self, websocket: WebSocketServerProtocol):
        """Register a new client connection"""
        self.clients.add(websocket)
        logger.info(f"New client connected. Total clients: {len(self.clients)}")

        # Send welcome message
        welcome_message = {
            "type": "welcome",
            "message": "Connected to Frenly AI WebSocket server",
            "agent_id": self.frenly_agent.agent_id,
            "timestamp": datetime.now().isoformat(),
        }
        await websocket.send(json.dumps(welcome_message))

    async def unregister_client(self, websocket: WebSocketServerProtocol):
        """Unregister a client connection"""
        self.clients.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.clients)}")

    async def handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            message_type = data.get("type", "unknown")

            logger.info(f"Received message type: {message_type}")

            if message_type == "context_update":
                await self.handle_context_update(websocket, data)
            elif message_type == "insight_request":
                await self.handle_insight_request(websocket, data)
            elif message_type == "avatar_interaction":
                await self.handle_avatar_interaction(websocket, data)
            elif message_type == "ping":
                await self.handle_ping(websocket, data)
            else:
                await self.handle_unknown_message(websocket, data)

        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
            await websocket.send(
                json.dumps(
                    {
                        "type": "error",
                        "message": "Invalid JSON format",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            )
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await websocket.send(
                json.dumps(
                    {
                        "type": "error",
                        "message": f"Server error: {str(e)}",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            )

    async def handle_context_update(
        self, websocket: WebSocketServerProtocol, data: Dict
    ):
        """Handle context updates from frontend"""
        context = data.get("context", {})

        # Generate insights based on context
        insights = await self.frenly_agent.generate_maximized_insight(context)

        # Send insights back to client
        response = {
            "type": "insights",
            "data": insights,
            "timestamp": datetime.now().isoformat(),
        }

        await websocket.send(json.dumps(response))

        # Store in message history
        self.message_history.append(
            {
                "type": "context_update",
                "context": context,
                "response": insights,
                "timestamp": datetime.now().isoformat(),
            }
        )

    async def handle_insight_request(
        self, websocket: WebSocketServerProtocol, data: Dict
    ):
        """Handle explicit insight requests"""
        context = data.get("context", {})
        user_role = data.get("userRole", "user")

        # Add user role to context
        context["userRole"] = user_role

        # Generate role-specific insights
        insights = await self.frenly_agent.generate_maximized_insight(context)

        # Send insights back to client
        response = {
            "type": "insights",
            "data": insights,
            "timestamp": datetime.now().isoformat(),
        }

        await websocket.send(json.dumps(response))

    async def handle_avatar_interaction(
        self, websocket: WebSocketServerProtocol, data: Dict
    ):
        """Handle avatar interaction events"""
        interaction_type = data.get("interaction", "click")
        context = data.get("context", {})

        # Generate comic character response
        comic_response = self.frenly_agent._generate_comic_response(context, {})

        # Send comic response back to client
        response = {
            "type": "comic_response",
            "data": comic_response,
            "timestamp": datetime.now().isoformat(),
        }

        await websocket.send(json.dumps(response))

    async def handle_ping(self, websocket: WebSocketServerProtocol, data: Dict):
        """Handle ping messages"""
        response = {
            "type": "pong",
            "timestamp": datetime.now().isoformat(),
            "server_status": "healthy",
        }
        await websocket.send(json.dumps(response))

    async def handle_unknown_message(
        self, websocket: WebSocketServerProtocol, data: Dict
    ):
        """Handle unknown message types"""
        response = {
            "type": "error",
            "message": f"Unknown message type: {data.get('type', 'unknown')}",
            "timestamp": datetime.now().isoformat(),
        }
        await websocket.send(json.dumps(response))

    async def broadcast_to_all(self, message: Dict):
        """Broadcast a message to all connected clients"""
        if self.clients:
            message_str = json.dumps(message)
            await asyncio.gather(
                *[client.send(message_str) for client in self.clients],
                return_exceptions=True,
            )

    async def health_check(self):
        """Periodic health check and status broadcast"""
        while True:
            try:
                health_status = await self.frenly_agent.get_system_status()

                health_message = {
                    "type": "health_update",
                    "data": health_status,
                    "timestamp": datetime.now().isoformat(),
                }

                await self.broadcast_to_all(health_message)

                # Wait 30 seconds before next health check
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(30)

    async def websocket_handler(self, websocket: WebSocketServerProtocol, path: str):
        """Main WebSocket connection handler"""
        await self.register_client(websocket)

        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client connection closed")
        except Exception as e:
            logger.error(f"WebSocket handler error: {e}")
        finally:
            await self.unregister_client(websocket)

    async def start_server(self):
        """Start the WebSocket server"""
        logger.info(f"Starting Frenly AI WebSocket server on {self.host}:{self.port}")

        # Start health check task
        health_task = asyncio.create_task(self.health_check())

        # Start WebSocket server
        server = await websockets.serve(self.websocket_handler, self.host, self.port)

        logger.info(f"Frenly AI WebSocket server started successfully")

        # Keep server running
        await server.wait_closed()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    server = FrenlyWebSocketServer()
    asyncio.run(server.start_server())
