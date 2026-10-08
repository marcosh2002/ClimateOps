import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    from app.config import Settings
    return Settings(
        APP_ENV="testing",
        APP_DEBUG=True,
        APP_HOST="0.0.0.0",
        APP_PORT=8000,
        SECRET_KEY="test-secret-key-for-testing-only-32chars",
        CORS_ORIGINS="http://localhost:3000",
        AWS_REGION="us-east-1",
        AWS_DYNAMODB_ENDPOINT="http://localhost:8000",
        AWS_S3_BUCKET="test-bucket",
        GROQ_API_KEY="test-groq-key",
        GROQ_MODEL="llama-3.3-70b-versatile",
        DATABASE_URL="sqlite:///./test.db",
        REDIS_URL="redis://localhost:6379/0",
        OPENWEATHER_API_KEY="test",
        NASA_POWER_API_KEY=None,
        GEONAMES_USERNAME="test",
        OPENSTREETMAP_NOMINATIM_EMAIL="test@test.com",
        IMD_API_BASE_URL="https://test.imd.gov.in",
        IMD_API_KEY=None,
        CWC_API_BASE_URL=None,
        CWC_API_KEY=None,
        MONITORING_INTERVAL_MINUTES=5,
        MONITORED_LOCATIONS_CONFIG="config/monitored_locations.json",
        SIMULATION_MODE_ENABLED=True,
        WEBSOCKET_HEARTBEAT_INTERVAL=30,
        SSE_RETRY_MS=3000,
        LOG_LEVEL="DEBUG",
        LOG_FORMAT="console",
    )


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def mock_dynamodb():
    mock = AsyncMock()
    mock.Table = AsyncMock()
    return mock