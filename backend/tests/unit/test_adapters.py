import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from app.adapters import MockAdapter, OpenWeatherAdapter, IMDAdapter, BaseAdapter
from app.database.models import EnvironmentalObservation, WeatherData, WaterData, AlertData


@pytest.fixture
def mock_adapter():
    return MockAdapter()


@pytest.mark.asyncio
async def test_mock_adapter_fetch_current(mock_adapter):
    obs = await mock_adapter.fetch_current("TEST-001", 28.6, 77.2)
    assert isinstance(obs, EnvironmentalObservation)
    assert obs.locationId == "TEST-001"
    assert obs.weather is not None
    assert obs.weather.temperature is not None
    assert 20 <= obs.weather.temperature <= 45
    assert obs.source == "mock"


@pytest.mark.asyncio
async def test_mock_adapter_fetch_forecast(mock_adapter):
    forecasts = await mock_adapter.fetch_forecast("TEST-001", 28.6, 77.2, hours=24)
    assert len(forecasts) == 4
    for obs in forecasts:
        assert isinstance(obs, EnvironmentalObservation)


def test_openweather_adapter_initialization():
    adapter = OpenWeatherAdapter("test-api-key")
    assert adapter.api_key == "test-api-key"
    assert adapter.get_source_name() == "openweather"


def test_imd_adapter_initialization():
    adapter = IMDAdapter("https://api.imd.gov.in", "test-key")
    assert adapter.base_url == "https://api.imd.gov.in"
    assert adapter.api_key == "test-key"
    assert adapter.get_source_name() == "imd"


@pytest.mark.asyncio
async def test_openweather_adapter_normalization():
    adapter = OpenWeatherAdapter("test-key")
    mock_response = {
        "main": {
            "temp": 30.5,
            "humidity": 65,
            "pressure": 1012,
        },
        "wind": {"speed": 5.2},
        "rain": {"1h": 2.5},
        "alerts": [
            {
                "event": "Heat Wave",
                "severity": "Moderate",
                "description": "High temperatures expected",
                "start": int(datetime.utcnow().timestamp()),
                "end": int(datetime.utcnow().timestamp()) + 3600,
            }
        ],
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = MagicMock(
            raise_for_status=lambda: None,
            json=lambda: mock_response,
        )
        obs = await adapter.fetch_current("TEST-002", 28.6, 77.2)

    assert obs.weather.temperature == 30.5
    assert obs.weather.humidity == 65
    assert obs.weather.rainfall == 2.5
    assert obs.weather.windSpeed == 5.2
    assert obs.weather.pressure == 1012
    assert len(obs.alerts) == 1
    assert obs.alerts[0].type == "Heat Wave"


@pytest.mark.asyncio
async def test_imd_adapter_district_code():
    adapter = IMDAdapter("https://api.imd.gov.in")
    assert adapter._get_district_code("IN-AS-GUW") == "AS-GUW"
    assert adapter._get_district_code("IN-RJ-JAI") == "RJ-JAI"
    assert adapter._get_district_code("INVALID") is None


def test_adapter_interface():
    assert hasattr(BaseAdapter, "fetch_current")
    assert hasattr(BaseAdapter, "fetch_forecast")
    assert hasattr(BaseAdapter, "get_source_name")