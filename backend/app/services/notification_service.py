import asyncio
import json
from typing import Any, Dict, List, Set
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from collections import defaultdict
import structlog

logger = structlog.get_logger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        self.sse_connections: Dict[str, List[asyncio.Queue]] = defaultdict(list)

    async def connect_websocket(self, websocket: WebSocket, channel: str) -> None:
        await websocket.accept()
        self.subscribe_websocket(websocket, channel)

    def subscribe_websocket(self, websocket: WebSocket, channel: str) -> None:
        self.active_connections[channel].add(websocket)

    def disconnect_websocket(self, websocket: WebSocket, channel: str) -> None:
        self.active_connections[channel].discard(websocket)
        if not self.active_connections[channel]:
            del self.active_connections[channel]

    async def subscribe_sse(self, channel: str) -> asyncio.Queue:
        queue = asyncio.Queue()
        self.sse_connections[channel].append(queue)
        return queue

    def unsubscribe_sse(self, channel: str, queue: asyncio.Queue) -> None:
        if queue in self.sse_connections[channel]:
            self.sse_connections[channel].remove(queue)
        if not self.sse_connections[channel]:
            del self.sse_connections[channel]

    async def broadcast(self, channel: str, message: Dict[str, Any]) -> None:
        message_str = json.dumps(message, default=str)

        for websocket in self.active_connections.get(channel, set()).copy():
            try:
                await websocket.send_text(message_str)
            except WebSocketDisconnect:
                self.disconnect_websocket(websocket, channel)
            except RuntimeError as error:
                logger.warning("Removing unavailable WebSocket client", channel=channel, error=str(error))
                self.disconnect_websocket(websocket, channel)

        for queue in self.sse_connections.get(channel, []).copy():
            await queue.put(message_str)

    async def broadcast_to_all(self, message: Dict[str, Any]) -> None:
        for channel in list(self.active_connections.keys()):
            await self.broadcast(channel, message)
        for channel in list(self.sse_connections.keys()):
            await self.broadcast(channel, message)

    def get_connection_count(self, channel: str) -> int:
        ws_count = len(self.active_connections.get(channel, set()))
        sse_count = len(self.sse_connections.get(channel, []))
        return ws_count + sse_count


class NotificationService:
    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager

    async def notify_incident_created(self, incident_data: Dict[str, Any]) -> None:
        await self.manager.broadcast("incidents", {
            "type": "incident_created",
            "timestamp": datetime.utcnow().isoformat(),
            "data": incident_data,
        })
        await self.manager.broadcast(f"incident_{incident_data['incidentId']}", {
            "type": "incident_created",
            "timestamp": datetime.utcnow().isoformat(),
            "data": incident_data,
        })

    async def notify_incident_updated(self, incident_data: Dict[str, Any]) -> None:
        await self.manager.broadcast("incidents", {
            "type": "incident_updated",
            "timestamp": datetime.utcnow().isoformat(),
            "data": incident_data,
        })
        await self.manager.broadcast(f"incident_{incident_data['incidentId']}", {
            "type": "incident_updated",
            "timestamp": datetime.utcnow().isoformat(),
            "data": incident_data,
        })

    async def notify_incident_resolved(self, incident_id: str, incident_data: Dict[str, Any]) -> None:
        await self.manager.broadcast("incidents", {
            "type": "incident_resolved",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {"incidentId": incident_id, **incident_data},
        })
        await self.manager.broadcast(f"incident_{incident_id}", {
            "type": "incident_resolved",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {"incidentId": incident_id, **incident_data},
        })

    async def notify_risk_update(self, location_id: str, risk_data: Dict[str, Any]) -> None:
        await self.manager.broadcast(f"risk_{location_id}", {
            "type": "risk_update",
            "timestamp": datetime.utcnow().isoformat(),
            "locationId": location_id,
            "data": risk_data,
        })

    async def notify_summary_update(self, summary: Dict[str, Any]) -> None:
        await self.manager.broadcast("summary", {
            "type": "summary_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": summary,
        })

    async def send_heartbeat(self) -> None:
        await self.manager.broadcast_to_all({
            "type": "heartbeat",
            "timestamp": datetime.utcnow().isoformat(),
        })


connection_manager = ConnectionManager()
notification_service = NotificationService(connection_manager)