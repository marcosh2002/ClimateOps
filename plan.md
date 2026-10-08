# ClimateOps Backend Execution Plan

## Project Overview
Build a FastAPI-based backend for ClimateOps - an AI-powered climate intelligence and emergency response platform focusing on heat, flood, water stress, and drought risks.

## Tech Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: DynamoDB (primary), SQLite (local dev)
- **Cache**: Redis
- **Queue**: Celery + Redis (for async tasks)
- **AI**: Groq-hosted language models via LangChain
- **Scheduler**: APScheduler (local), EventBridge Scheduler (AWS)
- **Validation**: Pydantic v2
- **Testing**: pytest + httpx
- **Linting**: ruff, mypy

## Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Settings management
│   ├── database/
│   │   ├── __init__.py
│   │   ├── dynamodb.py         # DynamoDB client & repositories
│   │   ├── sqlite.py           # Local SQLite for dev
│   │   └── models.py           # Pydantic models for DB
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── climate.py      # Climate intelligence endpoints
│   │   │   ├── incidents.py    # Emergency ops endpoints
│   │   │   ├── monitoring.py   # Live monitoring endpoints
│   │   │   └── simulation.py   # What-if simulation endpoints
│   │   └── deps.py             # Dependency injection
│   ├── core/
│   │   ├── __init__.py
│   │   ├── risk_engine.py      # Deterministic risk calculation
│   │   ├── emergency_engine.py # Incident creation logic
│   │   ├── simulation_engine.py# What-if simulation
│   │   └── groq.py             # Groq/LangChain integration
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base.py             # Base adapter interface
│   │   ├── imd.py              # IMD API adapter
│   │   └── cwc.py              # CWC API adapter (placeholder)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── location_service.py # Location search & resolution
│   │   ├── weather_service.py  # Environmental data aggregation
│   │   ├── monitoring_service.py # 5-min monitoring logic
│   │   └── notification_service.py # WebSocket/SSE notifications
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── climate.py          # Climate response schemas
│   │   ├── incidents.py        # Incident schemas
│   │   ├── simulation.py       # Simulation schemas
│   │   └── common.py           # Shared schemas
│   └── utils/
│       ├── __init__.py
│       ├── geo.py              # Geospatial utilities
│       └── datetime.py         # Date/time helpers
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_risk_engine.py
│   │   ├── test_emergency_engine.py
│   │   └── test_adapters.py
│   └── integration/
│       ├── test_climate_api.py
│       └── test_incidents_api.py
├── scripts/
│   ├── seed_locations.py       # Seed monitored locations
│   └── run_monitoring.py       # Manual monitoring trigger
├── alembic/                    # Migrations (if using SQL)
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Set up FastAPI project structure
- [ ] Configure settings with pydantic-settings
- [ ] Set up DynamoDB local / SQLite for development
- [ ] Create base Pydantic models for all entities
- [ ] Set up logging, error handling, middleware
- [ ] Configure CORS, rate limiting
- [ ] Write basic health check endpoint
- [ ] Set up pytest with test fixtures

### Phase 2: Climate Intelligence Core (Week 1-2)
- [ ] Implement location search (OpenStreetMap Nominatim / GeoNames)
- [ ] Build environmental data providers (OpenWeather, NASA POWER, etc.)
- [ ] Create data normalization layer
- [ ] Implement Risk Engine (Heat, Flood, Water Stress, Drought)
- [ ] Build `/api/climate/{locationId}` endpoint
- [ ] Integrate Groq via LangChain for explanations
- [ ] Add preventive recommendations endpoint

### Phase 3: What-if Simulation (Week 2)
- [ ] Implement Simulation Engine
- [ ] Build `/api/climate/{locationId}/simulate` endpoint
- [ ] Current vs simulated comparison logic
- [ ] Groq explanation for simulated scenarios
- [ ] Simulation mode flag for demo

### Phase 4: India Live Monitoring - Data Adapters (Week 2-3)
- [ ] Implement IMD API client (current weather, district rainfall, warnings)
- [ ] Create IMD Adapter with normalization
- [ ] Implement CWC Adapter (placeholder/stub)
- [ ] Configure monitored Indian locations (states/districts)
- [ ] Build `/api/monitoring/locations` endpoint

### Phase 5: Emergency Engine (Week 3)
- [ ] Implement Emergency Engine detection logic
- [ ] Heatwave detection (temperature + humidity thresholds)
- [ ] Flood detection (rainfall + river level + warnings)
- [ ] Water stress detection
- [ ] Drought detection
- [ ] Incident creation & lifecycle management
- [ ] Incident deduplication (update vs create)

### Phase 6: Continuous Monitoring (Week 3-4)
- [ ] Set up APScheduler for 5-minute checks
- [ ] Build monitoring service that:
  - Fetches latest data for active incidents
  - Runs Risk Engine
  - Updates incident status
  - Triggers Groq for significant changes
- [ ] Implement incident timeline/history
- [ ] Add WebSocket/SSE for live updates

### Phase 7: API Endpoints & Integration (Week 4)
- [ ] `/api/incidents/active` - List active incidents
- [ ] `/api/incidents/{incidentId}` - Incident details
- [ ] `/api/incidents/{incidentId}/timeline` - Incident timeline
- [ ] `/api/incidents/simulate` - Emergency simulation
- [ ] WebSocket endpoint for live dashboard
- [ ] Comprehensive error handling & validation

### Phase 8: Testing & Polish (Week 4)
- [ ] Unit tests for Risk Engine, Emergency Engine
- [ ] Integration tests for all API endpoints
- [ ] Load testing for monitoring loops
- [ ] Documentation (OpenAPI/Swagger)
- [ ] Dockerize application
- [ ] CI/CD pipeline setup

## Key Design Decisions

1. **Risk Engine is Deterministic** - No ML in MVP, pure threshold-based logic
2. **Adapter Pattern** - External APIs never touch Risk Engine directly
3. **Incident Deduplication** - Same incident updated, not recreated
4. **Groq as Decision Support** - Explains, never decides
5. **Simulation Uses Same Engine** - Consistency between real and simulated
6. **Local-First Development** - SQLite + Mock adapters for offline dev

## API Contract Summary

### Climate Intelligence
```
GET  /api/locations/search?q={query}
GET  /api/climate/{locationId}
POST /api/climate/{locationId}/simulate
```

### Emergency Ops
```
GET  /api/incidents/active
GET  /api/incidents/{incidentId}
GET  /api/incidents/{incidentId}/timeline
GET  /api/monitoring/locations
POST /api/incidents/simulate
WS   /ws/incidents/{incidentId}
```

## Data Models (DynamoDB)

| Table | Key | Purpose |
|-------|-----|---------|
| locations | locationId (PK) | Global + monitored locations |
| environmental_observations | locationId (PK), timestamp (SK) | Raw normalized data |
| risk_assessments | locationId (PK), timestamp (SK) | Calculated risks |
| incidents | incidentId (PK) | Active/resolved incidents |
| incident_observations | incidentId (PK), timestamp (SK) | 5-min monitoring history |
| simulation_runs | simulationId (PK) | What-if simulation records |

## Risk Thresholds (Initial)

| Risk Type | LOW | MEDIUM | HIGH | CRITICAL |
|-----------|-----|--------|------|----------|
| Heat | 0-30 | 31-60 | 61-80 | 81-100 |
| Flood | 0-30 | 31-60 | 61-80 | 81-100 |
| Water Stress | 0-30 | 31-60 | 61-80 | 81-100 |
| Drought | 0-30 | 31-60 | 61-80 | 81-100 |

### Emergency Trigger Thresholds
- **Heat Emergency**: Heat Risk >= 80 AND temp > 40°C
- **Flood Emergency**: Flood Risk >= 80 AND official warning
- **Water Stress Emergency**: Water Stress >= 80
- **Drought Emergency**: Drought Risk >= 80

## Next Steps
1. Create `dev_requirements.md` with environment variables needed
2. Scaffold project structure
3. Install dependencies
4. Begin Phase 1 implementation