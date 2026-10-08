from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.groq import groq_client
from app.api.deps import get_monitoring_service
from app.database import sqlite
from app.database.models import (
    EnvironmentalObservation,
    Incident,
    IncidentSeverity,
    IncidentStatus,
    IncidentType,
    Location,
    RiskAssessment,
    RiskLevel,
    WeatherData,
)
from app.main import app


@pytest.mark.asyncio
async def test_persistent_api_routes(monkeypatch, tmp_path):
    monkeypatch.setattr(sqlite, "DB_PATH", str(tmp_path / "api.db"))
    app.dependency_overrides.clear()
    await sqlite.init_sqlite()

    now = datetime.utcnow()
    location = Location(
        locationId="E2E-001",
        country="India",
        state="Delhi",
        district="New Delhi",
        city="New Delhi",
        latitude=28.6139,
        longitude=77.209,
        monitoringEnabled=False,
        riskTypes=["HEAT"],
        createdAt=now,
        updatedAt=now,
    )
    observation = EnvironmentalObservation(
        locationId=location.locationId,
        timestamp=now,
        weather=WeatherData(
            temperature=39,
            humidity=65,
            rainfall=3,
            windSpeed=4,
            pressure=1008,
        ),
        source="test",
    )
    risk = RiskAssessment(
        locationId=location.locationId,
        timestamp=now,
        heatRisk=75,
        floodRisk=10,
        waterStressRisk=25,
        droughtRisk=30,
        heatSeverity=RiskLevel.HIGH,
        floodSeverity=RiskLevel.LOW,
        waterStressSeverity=RiskLevel.LOW,
        droughtSeverity=RiskLevel.MEDIUM,
    )
    await sqlite.SQLiteLocationsRepository().upsert(location.model_dump(mode="json"))
    await sqlite.SQLiteObservationsRepository().save(observation.model_dump())
    await sqlite.SQLiteRiskAssessmentsRepository().save(risk.model_dump(mode="json"))

    incident = Incident(
        incidentId="INC-E2E001",
        locationId=location.locationId,
        type=IncidentType.HEAT,
        severity=IncidentSeverity.WARNING,
        status=IncidentStatus.WARNING,
        riskScore=75,
        source="test",
        createdAt=now,
        lastUpdated=now,
        lastChecked=now,
        nextCheck=now,
    )
    await sqlite.SQLiteIncidentsRepository().upsert(incident.model_dump(mode="json"))
    await sqlite.SQLiteIncidentObservationsRepository().add_observation(
        {
            "incidentId": incident.incidentId,
            "timestamp": now.isoformat(),
            "rainfall": 3,
            "temperature": 39,
            "riverLevel": None,
            "riskScore": 75,
            "severity": "WARNING",
            "source": "test",
        }
    )

    monitoring_service = get_monitoring_service()
    monkeypatch.setattr(
        monitoring_service.weather_service,
        "fetch_and_store_current",
        AsyncMock(return_value=[]),
    )

    async def no_ai(*args, **kwargs):
        return None

    monkeypatch.setattr(groq_client, "explain_simulation", no_ai)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        search = await client.get("/api/locations/search", params={"q": "new delhi", "limit": 1})
        climate = await client.get(f"/api/climate/{location.locationId}")
        history = await client.get(f"/api/climate/{location.locationId}/history")
        active_incidents = await client.get("/api/incidents/active")
        timeline = await client.get(f"/api/incidents/{incident.incidentId}/timeline")
        monitored_locations = await client.get("/api/monitoring/locations")
        monitoring = await client.get("/api/monitoring/status")
        trigger = await client.post("/api/monitoring/trigger")
        simulation = await client.post(
            f"/api/climate/{location.locationId}/simulate",
            json={"temperature_change": 2},
        )

        assert search.status_code == 200 and search.json()[0]["locationId"] == location.locationId
        assert climate.status_code == 200 and climate.json()["risk"]["heatRisk"] == 75
        assert history.status_code == 200 and len(history.json()["observations"]) == 1
        assert active_incidents.status_code == 200 and active_incidents.json()[0]["incidentId"] == incident.incidentId
        assert timeline.status_code == 200 and len(timeline.json()["timeline"]) == 1
        assert monitored_locations.status_code == 200 and len(monitored_locations.json()) > 0
        assert monitoring.status_code == 200 and monitoring.json()["summary"]["total"] == 1
        assert trigger.status_code == 200 and trigger.json()["locations_checked"] == 15
        assert len(trigger.json()["errors"]) == 15
        assert simulation.status_code == 200

        simulation_id = simulation.json()["simulationId"]
        stored_simulation = await client.get(f"/api/simulations/{simulation_id}")
        assert stored_simulation.status_code == 200
        assert stored_simulation.json()["simulatedData"]["weather"]["temperature"] == 41

    app.dependency_overrides.clear()
