from unittest.mock import AsyncMock

import pytest

from app.services.location_service import LocationService


@pytest.mark.asyncio
async def test_search_locations_deduplicates_database_and_external_results():
    existing = {
        "locationId": "OSM-1",
        "city": "Mumbai",
        "country": "India",
        "latitude": 19.076,
        "longitude": 72.878,
    }
    external_duplicate = {**existing, "source": "openstreetmap"}
    nearby_duplicate = {
        **existing,
        "locationId": "OSM-2",
        "district": "",
        "latitude": 19.055,
        "longitude": 72.869,
        "source": "openstreetmap",
    }
    external_new = {
        "locationId": "OSM-3",
        "city": "Mumbai",
        "country": "India",
        "state": "Maharashtra",
        "latitude": 23.1,
        "longitude": 73.2,
        "source": "openstreetmap",
    }
    repository = AsyncMock()
    repository.search_by_name.return_value = [existing, existing, nearby_duplicate]
    service = LocationService(repository)
    service._search_external = AsyncMock(
        return_value=[external_duplicate, nearby_duplicate, external_new]
    )

    results = await service.search_locations("Mumbai", limit=3)

    assert [result["locationId"] for result in results] == ["OSM-1", "OSM-3"]
    service._search_external.assert_awaited_once_with("Mumbai", 3)
    repository.upsert.assert_awaited_once()
    repository.upsert.assert_awaited_with(
        {
            **external_new,
            "monitoringEnabled": False,
            "riskTypes": [],
        }
    )
