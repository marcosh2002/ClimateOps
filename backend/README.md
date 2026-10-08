# ClimateOps Backend

FastAPI-based backend for ClimateOps - Climate Intelligence & Emergency Response Platform.

## Features

- **Global Climate Intelligence**: Search any location worldwide, get climate risk assessments (heat, flood, water stress, drought)
- **What-if Simulation**: Simulate environmental changes and see risk impact
- **India Live Emergency Ops**: Continuous monitoring of Indian locations using IMD data
- **Automatic Incident Detection**: Risk engine detects emergencies and creates incidents
- **5-Minute Monitoring**: Continuous reassessment of active incidents
- **AI Explanations**: Groq-hosted language model via LangChain for risk explanations and recommendations
- **Real-time Updates**: WebSocket/SSE for live dashboard updates

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Groq API key (for AI explanations)
- AWS account (only for production DynamoDB/S3)
- OpenWeatherMap API Key
- GeoNames Account

### Local Development

1. **Clone and setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and AWS credentials
   ```

3. **Start infrastructure**
   ```bash
   docker-compose up -d
   ```

4. **Seed monitored locations**
   ```bash
   python scripts/seed_locations.py
   ```

5. **Run development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access API docs**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Running Tests

```bash
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html
```

### Linting & Type Checking

```bash
ruff check app/
mypy app/
```

## API Endpoints

### Climate Intelligence
```
GET  /api/locations/search?q={query}           # Global location search
GET  /api/climate/{locationId}                 # Climate risk dashboard
GET  /api/climate/{locationId}/history         # Historical observations
POST /api/climate/{locationId}/simulate        # What-if simulation
GET  /api/simulations/{simulationId}            # Retrieve a saved simulation
```

### Emergency Operations
```
GET  /api/incidents/active                     # Active incidents list
GET  /api/incidents/summary                    # Incident summary stats
GET  /api/incidents/{incidentId}               # Incident details
GET  /api/incidents/{incidentId}/timeline      # Incident timeline
POST /api/incidents/simulate                   # Simulate emergency
```

### Live Monitoring
```
GET  /api/monitoring/locations                 # Monitored locations
GET  /api/monitoring/status                    # Monitoring status
POST /api/monitoring/trigger                   # Manual trigger
WS   /api/monitoring/ws/incidents               # WebSocket for all incidents
WS   /api/monitoring/ws/incidents/{incidentId}  # WebSocket for specific incident
SSE  /api/monitoring/sse/incidents              # SSE for all incidents
SSE  /api/monitoring/sse/incidents/{incidentId} # SSE for specific incident
```

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Settings management
│   ├── api/
│   │   ├── routes/             # API route handlers
│   │   └── deps.py             # Dependency injection
│   ├── core/
│   │   ├── risk_engine.py      # Deterministic risk calculation
│   │   ├── emergency_engine.py # Incident detection logic
│   │   ├── simulation_engine.py# What-if simulation
│   │   └── groq.py             # Groq/LangChain AI integration
│   ├── adapters/               # External API adapters
│   │   ├── base.py             # Base adapter + implementations
│   │   └── __init__.py
│   ├── services/               # Business logic services
│   │   ├── location_service.py
│   │   ├── weather_service.py
│   │   ├── monitoring_service.py
│   │   └── notification_service.py
│   ├── database/
│   │   ├── dynamodb.py         # DynamoDB repositories
│   │   ├── sqlite.py           # SQLite repositories (local dev)
│   │   └── models.py           # Pydantic models
│   ├── schemas/                # Request/Response schemas
│   └── utils/                  # Utility functions
├── tests/
├── scripts/
├── config/
├── requirements.txt
└── requirements-dev.txt
```

## Configuration

Key environment variables (see `.env.example`):

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Groq API key for AI explanations |
| `GROQ_MODEL` | Groq model (default: `llama-3.3-70b-versatile`) |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | AWS credentials for production DynamoDB/S3 |
| `OPENWEATHER_API_KEY` | OpenWeatherMap API key |
| `GEONAMES_USERNAME` | GeoNames username |
| `IMD_API_BASE_URL` | IMD API endpoint |
| `MONITORING_INTERVAL_MINUTES` | Monitoring interval (default: 5) |
| `SIMULATION_MODE_ENABLED` | Enable simulation mode (default: true) |

## Monitoring Locations

Configure monitored Indian locations in `config/monitored_locations.json`:

```json
{
  "locations": [
    {
      "locationId": "IN-AS-GUW",
      "country": "India",
      "state": "Assam",
      "district": "Kamrup Metropolitan",
      "city": "Guwahati",
      "latitude": 26.1445,
      "longitude": 91.7362,
      "monitoringEnabled": true,
      "riskTypes": ["FLOOD", "HEAVY_RAIN"]
    }
  ]
}
```

## Risk Engine

Deterministic risk calculation with thresholds:

| Risk | LOW | MEDIUM | HIGH | CRITICAL |
|------|-----|--------|------|----------|
| All | 0-30 | 31-60 | 61-80 | 81-100 |

Emergency triggers:
- **Heat**: Risk ≥ 80% AND temp ≥ 40°C
- **Flood**: Risk ≥ 80% AND official warning
- **Water Stress**: Risk ≥ 80%
- **Drought**: Risk ≥ 80%

## Deployment

### Docker
```bash
docker-compose up -d --build
```

### AWS (Production)
1. Provision DynamoDB tables (see `dev_requirements.md`)
2. Create S3 bucket
3. Configure EventBridge Scheduler for 5-min Lambda
4. Set up API Gateway
5. Deploy with appropriate IAM roles

## License

MIT