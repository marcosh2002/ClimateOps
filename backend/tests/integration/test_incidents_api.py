import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from datetime import datetime

from app.main import app
from app.api.deps import (
    get_incidents_repo as incidents_repo_dependency,
    get_monitoring_service as monitoring_service_dependency,
    get_location_service as location_service_dependency,
    get_weather_service as weather_service_dependency,
)
from app.database.models import (
    EnvironmentalObservation,
    Incident,
    IncidentType,
    IncidentSeverity,
    IncidentStatus,
    Location,
    WeatherData,
)


@pytest.fixture
async def async_client():
    app.dependency_overrides.clear()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_incident():
    return Incident(
        incidentId="INC-TEST001",
        locationId="TEST-001",
        type=IncidentType.FLOOD,
        severity=IncidentSeverity.CRITICAL,
        status=IncidentStatus.CRITICAL,
        riskScore=90,
        source="test",
        createdAt=datetime.utcnow(),
        lastUpdated=datetime.utcnow(),
        lastChecked=datetime.utcnow(),
        nextCheck=datetime.utcnow(),
    )


class TestIncidentsAPI:
    @pytest.mark.asyncio
    async def test_get_active_incidents(self, async_client, mock_incident):
        with patch("app.api.deps.get_incidents_repo") as mock_repo:
            mock = AsyncMock()
            mock.get_active.return_value = [mock_incident.model_dump()]
            mock_repo.return_value = mock
            app.dependency_overrides[incidents_repo_dependency] = lambda: mock

            response = await async_client.get("/api/incidents/active")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["incidentId"] == "INC-TEST001"
            assert data[0]["type"] == "FLOOD"

    @pytest.mark.asyncio
    async def test_get_incident_summary(self, async_client):
        with patch("app.api.deps.get_monitoring_service") as mock_service:
            mock = AsyncMock()
            mock.get_active_incidents_summary.return_value = {
                "total": 2,
                "by_type": {"FLOOD": 1, "HEAT": 1},
                "by_severity": {"CRITICAL": 2},
                "by_status": {"CRITICAL": 2},
                "critical_count": 2,
                "high_risk_count": 0,
            }
            mock_service.return_value = mock
            app.dependency_overrides[monitoring_service_dependency] = lambda: mock

            response = await async_client.get("/api/incidents/summary")
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 2
            assert data["by_type"]["FLOOD"] == 1

    @pytest.mark.asyncio
    async def test_get_incident_by_id(self, async_client, mock_incident):
        with patch("app.api.deps.get_incidents_repo") as mock_repo:
            mock = AsyncMock()
            mock.get_by_id.return_value = mock_incident.model_dump()
            mock_repo.return_value = mock
            app.dependency_overrides[incidents_repo_dependency] = lambda: mock

            response = await async_client.get("/api/incidents/INC-TEST001")
            assert response.status_code == 200
            data = response.json()
            assert data["incidentId"] == "INC-TEST001"

    @pytest.mark.asyncio
    async def test_get_incident_not_found(self, async_client):
        with patch("app.api.deps.get_incidents_repo") as mock_repo:
            mock = AsyncMock()
            mock.get_by_id.return_value = None
            mock_repo.return_value = mock
            app.dependency_overrides[incidents_repo_dependency] = lambda: mock

            response = await async_client.get("/api/incidents/NONEXISTENT")
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_incident_timeline(self, async_client, mock_incident):
        with patch("app.api.deps.get_monitoring_service") as mock_service:
            mock = AsyncMock()
            mock.incidents_repo.get_by_id.return_value = mock_incident.model_dump()
            mock.get_incident_timeline.return_value = [
                {
                    "incidentId": "INC-TEST001",
                    "timestamp": datetime.utcnow().isoformat(),
                    "rainfall": 100.0,
                    "temperature": 28.0,
                    "riverLevel": 45.0,
                    "riskScore": 90,
                    "severity": "CRITICAL",
                    "source": "test",
                }
            ]
            mock_service.return_value = mock
            app.dependency_overrides[monitoring_service_dependency] = lambda: mock

            response = await async_client.get("/api/incidents/INC-TEST001/timeline")
            assert response.status_code == 200
            data = response.json()
            assert data["incidentId"] == "INC-TEST001"
            assert len(data["timeline"]) == 1

    @pytest.mark.asyncio
    async def test_simulate_incident(self, async_client):
        with patch("app.api.deps.get_location_service") as mock_loc_service, \
             patch("app.api.deps.get_weather_service") as mock_weather_service, \
             patch("app.api.deps.get_incidents_repo") as mock_inc_repo:

            mock_loc = AsyncMock()
            mock_loc.get_location.return_value = Location(
                locationId="TEST-001",
                country="India",
                state="Test",
                district="Test",
                city="Test City",
                latitude=28.6,
                longitude=77.2,
                monitoringEnabled=True,
                riskTypes=["FLOOD"],
                createdAt=datetime.utcnow(),
                updatedAt=datetime.utcnow(),
            )
            mock_loc_service.return_value = mock_loc
            app.dependency_overrides[location_service_dependency] = lambda: mock_loc

            mock_weather = AsyncMock()
            mock_weather.get_latest_observation.return_value = EnvironmentalObservation(
                locationId="TEST-001",
                timestamp=datetime.utcnow(),
                weather=WeatherData(
                    temperature=28,
                    humidity=80,
                    rainfall=50,
                    windSpeed=10,
                    pressure=1005,
                ),
                alerts=[],
                source="test",
            )
            mock_weather.fetch_and_store_current = AsyncMock()
            mock_weather_service.return_value = mock_weather
            app.dependency_overrides[weather_service_dependency] = lambda: mock_weather

            mock_inc = AsyncMock()
            mock_inc_repo.return_value = mock_inc

            response = await async_client.post(
                "/api/incidents/simulate",
                params={"location_id": "TEST-001", "incident_type": "FLOOD", "severity": "WARNING"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["simulation"] is True
            assert "incident" in data