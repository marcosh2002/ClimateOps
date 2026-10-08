from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.services.monitoring_service import MonitoringService


@pytest.mark.asyncio
async def test_trigger_monitoring_aggregates_location_counts_without_double_counting():
    service = MonitoringService(
        incidents_repo=AsyncMock(get_active=AsyncMock(return_value=[])),
        incident_obs_repo=AsyncMock(),
        locations_repo=AsyncMock(),
        weather_service=AsyncMock(),
        location_service=AsyncMock(
            get_monitored_locations=AsyncMock(
                return_value=[
                    SimpleNamespace(locationId="LOC-1", monitoringEnabled=True),
                    SimpleNamespace(locationId="LOC-2", monitoringEnabled=True),
                    SimpleNamespace(locationId="LOC-3", monitoringEnabled=False),
                ]
            )
        ),
    )
    service._monitor_location = AsyncMock(
        return_value={
            "locations_checked": 1,
            "incidents_created": 2,
            "incidents_updated": 1,
            "incidents_resolved": 0,
        }
    )

    result = await service.trigger_monitoring_now()

    assert result == {
        "locations_checked": 2,
        "incidents_created": 4,
        "incidents_updated": 2,
        "incidents_resolved": 0,
    }
    assert service._monitor_location.await_count == 2
