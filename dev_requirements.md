# ClimateOps Backend - Development Requirements

## Required from User / Environment

### 1. Groq AI Configuration
| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GROQ_API_KEY` | For AI explanations | Groq API key | Obtain from https://console.groq.com/keys |
| `GROQ_MODEL` | No | Groq model | `llama-3.3-70b-versatile` |

### 2. AWS Credentials & Configuration
| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | Production only | AWS access key for DynamoDB/S3 | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | Production only | AWS secret access key | `...` |
| `AWS_REGION` | For DynamoDB | AWS region | `us-east-1` |
| `AWS_DYNAMODB_ENDPOINT` | Local only | Local DynamoDB endpoint (leave empty for AWS) | `http://localhost:8000` |
| `AWS_S3_BUCKET` | If using S3 | S3 bucket for raw/historical data | `climatify-data` |

### 3. External API Keys
| Variable | Required | Description | Source |
|----------|----------|-------------|--------|
| `OPENWEATHER_API_KEY` | Yes | Current weather, forecasts globally | https://openweathermap.org/api |
| `NASA_POWER_API_KEY` | Optional | Historical climate data (free tier) | https://power.larc.nasa.gov/ |
| `GEONAMES_USERNAME` | Yes | Global location search | http://www.geonames.org/ |
| `OPENSTREETMAP_NOMINATIM_EMAIL` | Yes | Contact email for Nominatim rate limits | `dev@yourdomain.com` |

### 4. India-Specific Data Sources
| Variable | Required | Description | Notes |
|----------|----------|-------------|-------|
| `IMD_API_BASE_URL` | Yes | IMD API base URL | `https://mausam.imd.gov.in` |
| `IMD_API_KEY` | If auth needed | IMD API key if required | Check IMD API docs |
| `CWC_API_BASE_URL` | Phase 8 | CWC API base URL | Future integration |
| `CWC_API_KEY` | Phase 8 | CWC API key if required | Future integration |

### 5. Database & Cache
| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Local dev | SQLite/PostgreSQL connection string | `sqlite:///./climatify.db` |
| `REDIS_URL` | Yes | Redis connection for Celery/cache | `redis://localhost:6379/0` |

### 6. Application Settings
| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `APP_ENV` | Yes | Environment: `development`, `staging`, `production` | `development` |
| `APP_DEBUG` | No | Enable debug mode | `true` |
| `APP_HOST` | No | Host to bind | `0.0.0.0` |
| `APP_PORT` | No | Port to bind | `8000` |
| `SECRET_KEY` | Yes | JWT signing key (32+ chars) | Generate with `openssl rand -hex 32` |
| `CORS_ORIGINS` | Yes | Comma-separated allowed origins | `http://localhost:3000,http://localhost:5173` |

### 7. Monitoring & Scheduler
| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `MONITORING_INTERVAL_MINUTES` | No | Incident reassessment interval | `5` |
| `MONITORED_LOCATIONS_CONFIG` | Yes | Path to monitored locations JSON | `config/monitored_locations.json` |
| `SIMULATION_MODE_ENABLED` | No | Enable simulation mode flag | `true` |

### 8. Notification / WebSocket
| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `WEBSOCKET_HEARTBEAT_INTERVAL` | No | WS ping interval (seconds) | `30` |
| `SSE_RETRY_MS` | No | SSE retry interval (milliseconds) | `3000` |

---

## Required Files from User

### 1. Monitored Locations Configuration
**File**: `config/monitored_locations.json`
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
    },
    {
      "locationId": "IN-RJ-JAI",
      "country": "India",
      "state": "Rajasthan",
      "district": "Jaipur",
      "city": "Jaipur",
      "latitude": 26.9124,
      "longitude": 75.7873,
      "monitoringEnabled": true,
      "riskTypes": ["HEAT", "DROUGHT", "WATER_STRESS"]
    }
  ]
}
```
**Need**: At least 10-15 key Indian locations covering flood-prone, heat-prone, and drought-prone areas.

### 2. Risk Thresholds Configuration (Optional - can use defaults)
**File**: `config/risk_thresholds.json`
```json
{
  "heat": {
    "thresholds": {"low": 30, "medium": 60, "high": 80},
    "temperature_critical": 40,
    "humidity_factor": 0.3
  },
  "flood": {
    "thresholds": {"low": 30, "medium": 60, "high": 80},
    "rainfall_24h_critical_mm": 100,
    "river_level_rising_weight": 0.4
  },
  "water_stress": {
    "thresholds": {"low": 30, "medium": 60, "high": 80},
    "rainfall_deficit_weight": 0.5,
    "groundwater_decline_weight": 0.5
  },
  "drought": {
    "thresholds": {"low": 30, "medium": 60, "high": 80},
    "spi_threshold": -1.5
  }
}
```

---

## Local Development Setup

### Prerequisites to Install
```bash
# Python 3.11+
python --version

# Docker & Docker Compose (for DynamoDB Local, Redis)
docker --version
docker-compose --version

# AWS CLI (for real AWS resources)
aws --version

# Optional: LocalStack for full local AWS simulation
```

### Quick Start Commands
```bash
# 1. Clone and navigate
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Copy env template
cp .env.example .env
# Edit .env with your values

# 5. Start local infrastructure
docker-compose up -d  # Starts DynamoDB Local, Redis

# 6. Seed monitored locations
python scripts/seed_locations.py

# 7. Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 8. Run tests
pytest tests/ -v

# 9. Run monitoring manually (for testing)
python scripts/run_monitoring.py
```

### Docker Compose Services (docker-compose.yml)
```yaml
services:
  dynamodb:
    image: amazon/dynamodb-local:latest
    ports:
      - "8000:8000"
    command: "-jar DynamoDBLocal.jar -sharedDb -inMemory"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  localstack:  # Optional - full AWS local
    image: localstack/localstack:latest
    ports:
      - "4566:4566"
    environment:
      - SERVICES=dynamodb,s3,lambda,events
    volumes:
      - localstack_data:/var/lib/localstack

volumes:
  redis_data:
  localstack_data:
```

---

## AWS Resources to Provision (Production)

### 1. DynamoDB Tables
```bash
# Locations table
aws dynamodb create-table \
  --table-name climatify-locations \
  --attribute-definitions AttributeName=locationId,AttributeType=S \
  --key-schema AttributeName=locationId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# Environmental observations
aws dynamodb create-table \
  --table-name climatify-observations \
  --attribute-definitions AttributeName=locationId,AttributeType=S AttributeName=timestamp,AttributeType=S \
  --key-schema AttributeName=locationId,KeyType=HASH AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST

# Risk assessments
aws dynamodb create-table \
  --table-name climatify-risk-assessments \
  --attribute-definitions AttributeName=locationId,AttributeType=S AttributeName=timestamp,AttributeType=S \
  --key-schema AttributeName=locationId,KeyType=HASH AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST

# Incidents
aws dynamodb create-table \
  --table-name climatify-incidents \
  --attribute-definitions AttributeName=incidentId,AttributeType=S \
  --key-schema AttributeName=incidentId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# Incident observations (5-min monitoring)
aws dynamodb create-table \
  --table-name climatify-incident-observations \
  --attribute-definitions AttributeName=incidentId,AttributeType=S AttributeName=timestamp,AttributeType=S \
  --key-schema AttributeName=incidentId,KeyType=HASH AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST

# Simulation runs
aws dynamodb create-table \
  --table-name climatify-simulations \
  --attribute-definitions AttributeName=simulationId,AttributeType=S \
  --key-schema AttributeName=simulationId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

### 2. S3 Bucket
```bash
aws s3 mb s3://climatify-data --region us-east-1
aws s3api put-bucket-versioning --bucket climatify-data --versioning-configuration Status=Enabled
```

### 3. IAM Permissions Needed
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:*",
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

### 4. EventBridge Scheduler (Production)
```bash
# Create schedule for 5-minute monitoring
aws scheduler create-schedule \
  --name climatify-5min-monitoring \
  --schedule-expression "rate(5 minutes)" \
  --target '{
    "Arn": "arn:aws:lambda:us-east-1:ACCOUNT:function:climatify-monitoring",
    "RoleArn": "arn:aws:iam::ACCOUNT:role/EventBridgeSchedulerRole"
  }'
```

---

## API Keys Setup Instructions

### OpenWeatherMap
1. Sign up at https://openweathermap.org/api
2. Subscribe to "One Call API 3.0" (free tier: 1000 calls/day)
3. Copy API key to `OPENWEATHER_API_KEY`

### GeoNames
1. Register at http://www.geonames.org/login
2. Enable "Free Web Services" in account settings
3. Copy username to `GEONAMES_USERNAME`

### NASA POWER (Optional)
1. Register at https://power.larc.nasa.gov/
2. Free tier available, no key required for basic access
3. If using authenticated endpoints, add `NASA_POWER_API_KEY`

### IMD API
1. Review API documentation: https://mausam.imd.gov.in/imd_latest/contents/api.pdf
2. Some endpoints may require registration
3. Configure `IMD_API_BASE_URL` and `IMD_API_KEY` if needed

---

## Verification Checklist

Before starting development, confirm you have:

- [ ] Groq API key for AI explanations
- [ ] OpenWeatherMap API key
- [ ] GeoNames account
- [ ] Docker & Docker Compose installed
- [ ] Python 3.11+ installed
- [ ] `.env` file created with all required variables
- [ ] `config/monitored_locations.json` with 10+ Indian locations
- [ ] DynamoDB Local running (or AWS DynamoDB accessible)
- [ ] Redis running locally

---

## Support Contacts

| Component | Documentation |
|-----------|---------------|
| IMD API | https://mausam.imd.gov.in/imd_latest/contents/api.pdf |
| CWC Data | http://cwc.gov.in/ |
| OpenWeatherMap | https://openweathermap.org/api/one-call-3 |
| GeoNames | http://www.geonames.org/export/web-services.html |
| NASA POWER | https://power.larc.nasa.gov/docs/ |
| Groq | https://console.groq.com/docs |
| FastAPI | https://fastapi.tiangolo.com/ |