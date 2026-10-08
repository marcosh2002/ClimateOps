from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.api.deps import get_location_service
from app.database.models import Location
from app.main import app


@pytest.mark.asyncio
async def test_demo_incidents_are_explicitly_labeled_and_not_persisted():
    app.dependency_overrides.clear()
    location = Location(
        locationId="DEMO-LOCATION-1",
        country="India",
        state="Test State",
        district="Test District",
        city="Test City",
        latitude=28.6,
        longitude=77.2,
        monitoringEnabled=True,
        riskTypes=[],
        createdAt=datetime.now(timezone.utc),
        updatedAt=datetime.now(timezone.utc),
    )
    location_service = AsyncMock()
    location_service.get_monitored_locations.return_value = [location]
    app.dependency_overrides[get_location_service] = lambda: location_service

    from fastapi.testclient import TestClient

    try:
        response = TestClient(app).get("/api/incidents/demo-preview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    incidents = response.json()
    assert len(incidents) == 3
    assert all(incident["incidentId"].startswith("DEMO-") for incident in incidents)
    assert all(incident["source"].startswith("DEMO SCENARIO") for incident in incidents)
    assert all(incident["locationId"] == location.locationId for incident in incidents)
    location_service.get_monitored_locations.assert_awaited_once()
