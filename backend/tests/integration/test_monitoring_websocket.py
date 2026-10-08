import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.notification_service import connection_manager


def test_incident_websocket_accepts_connection_and_answers_ping():
    client = TestClient(app)
    with client.websocket_connect("/api/monitoring/ws/incidents") as websocket:
        websocket.send_json({"type": "ping", "timestamp": "test-time"})

        assert websocket.receive_json() == {
            "type": "pong",
            "timestamp": "test-time",
        }


@pytest.mark.asyncio
async def test_sse_subscriber_receives_broadcast():
    queue = await connection_manager.subscribe_sse("incidents")
    try:
        await connection_manager.broadcast(
            "incidents",
            {"type": "incident_created", "data": {"incidentId": "INC-SSE"}},
        )
        message = json.loads(await queue.get())

        assert message["type"] == "incident_created"
        assert message["data"]["incidentId"] == "INC-SSE"
    finally:
        connection_manager.unsubscribe_sse("incidents", queue)
