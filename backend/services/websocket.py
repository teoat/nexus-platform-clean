#!/usr/bin/env python3
"""
NEXUS WebSocket Service
Enhanced WebSocket communication
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, Set

import websockets

logger = logging.getLogger(__name__)


class NEXUSWebSocketService:
    """NEXUS WebSocket Service"""

    def __init__(self):
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.rooms: Dict[str, Set[websockets.WebSocketServerProtocol]] = {}
        self.message_history: List[Dict[str, Any]] = []
        self.is_active = False

    async def initialize(self):
        """Initialize WebSocket service"""
        logger.info("Initializing NEXUS WebSocket Service")
        self.is_active = True
        logger.info("✅ NEXUS WebSocket Service initialized")

    async def register_client(self, websocket: websockets.WebSocketServerProtocol):
        """Register a new client"""
        self.clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.clients)}")

    async def unregister_client(self, websocket: websockets.WebSocketServerProtocol):
        """Unregister a client"""
        self.clients.discard(websocket)
        # Remove from all rooms
        for room_clients in self.rooms.values():
            room_clients.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.clients)}")

    async def join_room(self, websocket: websockets.WebSocketServerProtocol, room: str):
        """Join a room"""
        if room not in self.rooms:
            self.rooms[room] = set()
        self.rooms[room].add(websocket)
        logger.info(f"Client joined room: {room}")

    async def leave_room(
        self, websocket: websockets.WebSocketServerProtocol, room: str
    ):
        """Leave a room"""
        if room in self.rooms:
            self.rooms[room].discard(websocket)
        logger.info(f"Client left room: {room}")

    async def broadcast_message(self, message: Dict[str, Any], room: str = None):
        """Broadcast message to all clients or room"""
        message["timestamp"] = datetime.now().isoformat()
        self.message_history.append(message)

        if room and room in self.rooms:
            # Send to room
            disconnected = set()
            for client in self.rooms[room]:
                try:
                    await client.send(json.dumps(message))
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)

            # Remove disconnected clients
            for client in disconnected:
                await self.unregister_client(client)
        else:
            # Send to all clients
            disconnected = set()
            for client in self.clients:
                try:
                    await client.send(json.dumps(message))
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)

            # Remove disconnected clients
            for client in disconnected:
                await self.unregister_client(client)

    async def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "is_active": self.is_active,
            "connected_clients": len(self.clients),
            "active_rooms": len(self.rooms),
            "messages_sent": len(self.message_history),
            "timestamp": datetime.now().isoformat(),
        }

    async def shutdown(self):
        """Shutdown WebSocket service"""
        logger.info("Shutting down NEXUS WebSocket Service")
        self.is_active = False


# Global service instance
websocket_service = NEXUSWebSocketService()


async def main():
    """Main entry point"""
    await websocket_service.initialize()

    # Keep running
    try:
        while websocket_service.is_active:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await websocket_service.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
