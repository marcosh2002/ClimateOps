from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import asyncio
import json

from app.api.deps import get_monitoring_service, get_location_service, get_notification_service
from app.services.monitoring_service import MonitoringService
from app.services.location_service import LocationService
from app.services.notification_service import NotificationService
from app.database.models import Location

router = APIRouter()


@router.get("/locations", response_model=List[Dict[str, Any]])
async def get_monitored_locations(
    location_service: LocationService = Depends(get_location_service),
):
    locations = await location_service.get_monitored_locations()
    return [loc.model_dump() for loc in locations]


@router.post("/trigger")
async def trigger_monitoring(
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
):
    result = await monitoring_service.trigger_monitoring_now()
    return result


@router.get("/status")
async def get_monitoring_status(
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
):
    summary = await monitoring_service.get_active_incidents_summary()
    return {
        "monitoring_active": monitoring_service.is_running,
        "interval_minutes": monitoring_service.interval_minutes,
        "summary": summary,
    }


@router.websocket("/ws/incidents")
async def websocket_incidents(
    websocket: WebSocket,
    notification_service: NotificationService = Depends(get_notification_service),
):
    await notification_service.manager.connect_websocket(websocket, "incidents")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "subscribe":
                    channel = msg.get("channel", "incidents")
                    notification_service.manager.subscribe_websocket(websocket, channel)
                elif msg.get("type") == "ping":
                    await websocket.send_json({"type": "pong", "timestamp": msg.get("timestamp")})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        pass
    finally:
        for channel in list(notification_service.manager.active_connections.keys()):
            notification_service.manager.disconnect_websocket(websocket, channel)


@router.websocket("/ws/incidents/{incident_id}")
async def websocket_incident_detail(
    websocket: WebSocket,
    incident_id: str,
    notification_service: NotificationService = Depends(get_notification_service),
):
    channel = f"incident_{incident_id}"
    await notification_service.manager.connect_websocket(websocket, channel)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        notification_service.manager.disconnect_websocket(websocket, channel)


@router.get("/sse/incidents")
async def sse_incidents(
    notification_service: NotificationService = Depends(get_notification_service),
):
    queue = await notification_service.manager.subscribe_sse("incidents")

    async def event_generator():
        try:
            while True:
                message = await queue.get()
                yield f"data: {message}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            notification_service.manager.unsubscribe_sse("incidents", queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/sse/incidents/{incident_id}")
async def sse_incident_detail(
    incident_id: str,
    notification_service: NotificationService = Depends(get_notification_service),
):
    queue = await notification_service.manager.subscribe_sse(f"incident_{incident_id}")

    async def event_generator():
        try:
            while True:
                message = await queue.get()
                yield f"data: {message}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            notification_service.manager.unsubscribe_sse(f"incident_{incident_id}", queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )