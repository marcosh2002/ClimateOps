from contextlib import asynccontextmanager
from datetime import date, datetime
from enum import Enum
import json
from typing import Any, AsyncGenerator, Dict, List, Optional

import aiosqlite
from app.config import settings

DB_PATH = settings.DATABASE_URL.replace("sqlite:///", "").replace("sqlite://", "")


def _json_value(value: Any) -> str:
    return json.dumps(value, default=_serialize_value)


def _serialize_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    raise TypeError(f"Cannot serialize {type(value).__name__} to JSON")


def _decode_json(value: Any, default: Any) -> Any:
    if value is None:
        return default
    if isinstance(value, str):
        return json.loads(value)
    return value


def _decode_location(row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if row is None:
        return None
    row["monitoringEnabled"] = bool(row.get("monitoringEnabled"))
    row["riskTypes"] = _decode_json(row.get("riskTypes"), [])
    return row


def _decode_observation(row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if row is None:
        return None
    row["weather"] = {
        "temperature": row.pop("temperature"),
        "humidity": row.pop("humidity"),
        "rainfall": row.pop("rainfall"),
        "windSpeed": row.pop("windSpeed"),
        "pressure": row.pop("pressure"),
    }
    row["water"] = {
        "riverLevel": row.pop("riverLevel"),
        "riverLevelTrend": row.pop("riverLevelTrend"),
    }
    row["alerts"] = _decode_json(row.get("alerts"), [])
    row["rawData"] = _decode_json(row.get("rawData"), None)
    return row


def _decode_assessment(row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if row is None:
        return None
    row["contributingFactors"] = _decode_json(row.get("contributingFactors"), {})
    row["dataSources"] = _decode_json(row.get("dataSources"), [])
    return row


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS locations (
    locationId TEXT PRIMARY KEY,
    country TEXT NOT NULL,
    state TEXT,
    district TEXT,
    city TEXT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    monitoringEnabled INTEGER DEFAULT 0,
    riskTypes TEXT,
    createdAt TEXT DEFAULT CURRENT_TIMESTAMP,
    updatedAt TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS environmental_observations (
    locationId TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    temperature REAL,
    humidity REAL,
    rainfall REAL,
    windSpeed REAL,
    pressure REAL,
    riverLevel REAL,
    riverLevelTrend TEXT,
    alerts TEXT,
    source TEXT,
    rawData TEXT,
    PRIMARY KEY (locationId, timestamp)
);

CREATE TABLE IF NOT EXISTS risk_assessments (
    locationId TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    heatRisk INTEGER,
    floodRisk INTEGER,
    waterStressRisk INTEGER,
    droughtRisk INTEGER,
    heatSeverity TEXT,
    floodSeverity TEXT,
    waterStressSeverity TEXT,
    droughtSeverity TEXT,
    contributingFactors TEXT,
    dataSources TEXT,
    PRIMARY KEY (locationId, timestamp)
);

CREATE TABLE IF NOT EXISTS incidents (
    incidentId TEXT PRIMARY KEY,
    locationId TEXT NOT NULL,
    type TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL,
    riskScore INTEGER,
    source TEXT,
    createdAt TEXT DEFAULT CURRENT_TIMESTAMP,
    lastUpdated TEXT DEFAULT CURRENT_TIMESTAMP,
    lastChecked TEXT,
    nextCheck TEXT,
    aiExplanation TEXT,
    FOREIGN KEY (locationId) REFERENCES locations(locationId)
);

CREATE TABLE IF NOT EXISTS incident_observations (
    incidentId TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    rainfall REAL,
    temperature REAL,
    riverLevel REAL,
    riskScore INTEGER,
    severity TEXT,
    source TEXT,
    PRIMARY KEY (incidentId, timestamp),
    FOREIGN KEY (incidentId) REFERENCES incidents(incidentId)
);

CREATE TABLE IF NOT EXISTS simulation_runs (
    simulationId TEXT PRIMARY KEY,
    locationId TEXT NOT NULL,
    originalData TEXT NOT NULL,
    simulatedData TEXT NOT NULL,
    originalRisks TEXT NOT NULL,
    simulatedRisks TEXT NOT NULL,
    aiExplanation TEXT,
    createdAt TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (locationId) REFERENCES locations(locationId)
);

CREATE INDEX IF NOT EXISTS idx_observations_location_time ON environmental_observations(locationId, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_risk_location_time ON risk_assessments(locationId, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_location ON incidents(locationId);
CREATE INDEX IF NOT EXISTS idx_incident_obs_incident_time ON incident_observations(incidentId, timestamp);
"""


async def init_sqlite() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)
        cursor = await db.execute("PRAGMA table_info(simulation_runs)")
        simulation_columns = {row[1] for row in await cursor.fetchall()}
        if "bedrockExplanation" in simulation_columns and "aiExplanation" not in simulation_columns:
            await db.execute(
                "ALTER TABLE simulation_runs RENAME COLUMN bedrockExplanation TO aiExplanation"
            )
        cursor = await db.execute("PRAGMA table_info(incidents)")
        incident_columns = {row[1] for row in await cursor.fetchall()}
        if "aiExplanation" not in incident_columns:
            await db.execute("ALTER TABLE incidents ADD COLUMN aiExplanation TEXT")
        await db.commit()


async def close_sqlite() -> None:
    pass


@asynccontextmanager
async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA foreign_keys = ON")
        yield db


class SQLiteBaseRepository:
    def __init__(self, table_name: str):
        self.table_name = table_name

    async def execute(self, query: str, params: tuple = ()) -> None:
        async with get_db() as db:
            await db.execute(query, params)
            await db.commit()

    async def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        async with get_db() as db:
            cursor = await db.execute(query, params)
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def fetchall(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        async with get_db() as db:
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


class SQLiteLocationsRepository(SQLiteBaseRepository):
    def __init__(self):
        super().__init__("locations")

    async def get_by_id(self, location_id: str) -> Optional[Dict[str, Any]]:
        return _decode_location(
            await self.fetchone("SELECT * FROM locations WHERE locationId = ?", (location_id,))
        )

    async def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        return [
            _decode_location(row)
            for row in await self.fetchall("SELECT * FROM locations LIMIT ?", (limit,))
        ]

    async def search_by_name(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        search_term = f"%{query.lower()}%"
        rows = await self.fetchall(
            """
            SELECT * FROM locations
            WHERE LOWER(city) LIKE ? OR LOWER(district) LIKE ? OR LOWER(state) LIKE ?
            LIMIT ?
            """,
            (search_term, search_term, search_term, limit),
        )
        return [_decode_location(row) for row in rows]

    async def upsert(self, location: Dict[str, Any]) -> Dict[str, Any]:
        await self.execute(
            """
            INSERT INTO locations (locationId, country, state, district, city, latitude, longitude, monitoringEnabled, riskTypes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(locationId) DO UPDATE SET
                country=excluded.country,
                state=excluded.state,
                district=excluded.district,
                city=excluded.city,
                latitude=excluded.latitude,
                longitude=excluded.longitude,
                monitoringEnabled=excluded.monitoringEnabled,
                riskTypes=excluded.riskTypes,
                updatedAt=CURRENT_TIMESTAMP
            """,
            (
                location["locationId"],
                location["country"],
                location.get("state"),
                location.get("district"),
                location.get("city"),
                location["latitude"],
                location["longitude"],
                location.get("monitoringEnabled", 0),
                _json_value(location.get("riskTypes", [])),
            ),
        )
        return location


class SQLiteObservationsRepository(SQLiteBaseRepository):
    def __init__(self):
        super().__init__("environmental_observations")

    async def get_latest(self, location_id: str) -> Optional[Dict[str, Any]]:
        return _decode_observation(
            await self.fetchone(
                "SELECT * FROM environmental_observations WHERE locationId = ? ORDER BY timestamp DESC LIMIT 1",
                (location_id,),
            )
        )

    async def get_history(self, location_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        from datetime import datetime, timedelta
        cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        rows = await self.fetchall(
            """
            SELECT * FROM environmental_observations
            WHERE locationId = ? AND timestamp >= ?
            ORDER BY timestamp DESC
            """,
            (location_id, cutoff),
        )
        return [_decode_observation(row) for row in rows]

    async def save(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        weather = observation.get("weather") or {}
        water = observation.get("water") or {}
        await self.execute(
            """
            INSERT INTO environmental_observations (
                locationId, timestamp, temperature, humidity, rainfall, windSpeed,
                pressure, riverLevel, riverLevelTrend, alerts, source, rawData
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                observation["locationId"],
                _serialize_value(observation["timestamp"]),
                weather.get("temperature"),
                weather.get("humidity"),
                weather.get("rainfall"),
                weather.get("windSpeed"),
                weather.get("pressure"),
                water.get("riverLevel"),
                water.get("riverLevelTrend"),
                _json_value(observation.get("alerts", [])),
                observation.get("source"),
                _json_value(observation.get("rawData")),
            ),
        )
        return observation


class SQLiteRiskAssessmentsRepository(SQLiteBaseRepository):
    def __init__(self):
        super().__init__("risk_assessments")

    async def get_latest(self, location_id: str) -> Optional[Dict[str, Any]]:
        return _decode_assessment(
            await self.fetchone(
                "SELECT * FROM risk_assessments WHERE locationId = ? ORDER BY timestamp DESC LIMIT 1",
                (location_id,),
            )
        )

    async def save(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        await self.execute(
            """
            INSERT INTO risk_assessments (
                locationId, timestamp, heatRisk, floodRisk, waterStressRisk, droughtRisk,
                heatSeverity, floodSeverity, waterStressSeverity, droughtSeverity,
                contributingFactors, dataSources
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                assessment["locationId"],
                _serialize_value(assessment["timestamp"]),
                assessment.get("heatRisk"),
                assessment.get("floodRisk"),
                assessment.get("waterStressRisk"),
                assessment.get("droughtRisk"),
                assessment.get("heatSeverity"),
                assessment.get("floodSeverity"),
                assessment.get("waterStressSeverity"),
                assessment.get("droughtSeverity"),
                _json_value(assessment.get("contributingFactors", {})),
                _json_value(assessment.get("dataSources", [])),
            ),
        )
        return assessment


class SQLiteIncidentsRepository(SQLiteBaseRepository):
    def __init__(self):
        super().__init__("incidents")

    async def get_active(self) -> List[Dict[str, Any]]:
        rows = await self.fetchall(
            """
            SELECT * FROM incidents
            WHERE status IN ('ACTIVE', 'WARNING', 'CRITICAL', 'EXTREME', 'RECOVERY')
            ORDER BY lastUpdated DESC
            """
        )
        return [self._decode_incident(row) for row in rows]

    async def get_by_id(self, incident_id: str) -> Optional[Dict[str, Any]]:
        return self._decode_incident(
            await self.fetchone("SELECT * FROM incidents WHERE incidentId = ?", (incident_id,))
        )

    async def get_by_location(self, location_id: str) -> List[Dict[str, Any]]:
        rows = await self.fetchall(
            "SELECT * FROM incidents WHERE locationId = ? ORDER BY createdAt DESC",
            (location_id,),
        )
        return [self._decode_incident(row) for row in rows]

    @staticmethod
    def _decode_incident(row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if row is not None:
            row["aiExplanation"] = _decode_json(row.get("aiExplanation"), None)
        return row

    async def upsert(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        await self.execute(
            """
            INSERT INTO incidents (
                incidentId, locationId, type, severity, status, riskScore, source,
                createdAt, lastUpdated, lastChecked, nextCheck, aiExplanation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(incidentId) DO UPDATE SET
                locationId=excluded.locationId,
                type=excluded.type,
                severity=excluded.severity,
                status=excluded.status,
                riskScore=excluded.riskScore,
                source=excluded.source,
                lastUpdated=CURRENT_TIMESTAMP,
                lastChecked=excluded.lastChecked,
                nextCheck=excluded.nextCheck,
                aiExplanation=excluded.aiExplanation
            """,
            (
                incident["incidentId"],
                incident["locationId"],
                incident["type"],
                incident["severity"],
                incident["status"],
                incident.get("riskScore"),
                incident.get("source"),
                _serialize_value(incident["createdAt"]),
                _serialize_value(incident["lastUpdated"]),
                _serialize_value(incident.get("lastChecked")),
                _serialize_value(incident.get("nextCheck")),
                _json_value(incident.get("aiExplanation"))
                if incident.get("aiExplanation") is not None
                else None,
            ),
        )
        return incident


class SQLiteIncidentObservationsRepository(SQLiteBaseRepository):
    def __init__(self):
        super().__init__("incident_observations")

    async def get_timeline(self, incident_id: str) -> List[Dict[str, Any]]:
        return await self.fetchall(
            "SELECT * FROM incident_observations WHERE incidentId = ? ORDER BY timestamp ASC",
            (incident_id,),
        )

    async def add_observation(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        await self.execute(
            """
            INSERT INTO incident_observations (
                incidentId, timestamp, rainfall, temperature, riverLevel, riskScore, severity, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                observation["incidentId"],
                _serialize_value(observation["timestamp"]),
                observation.get("rainfall"),
                observation.get("temperature"),
                observation.get("riverLevel"),
                observation.get("riskScore"),
                observation.get("severity"),
                observation.get("source"),
            ),
        )
        return observation


class SQLiteSimulationsRepository(SQLiteBaseRepository):
    def __init__(self):
        super().__init__("simulation_runs")

    async def get_by_id(self, simulation_id: str) -> Optional[Dict[str, Any]]:
        simulation = await self.fetchone(
            "SELECT * FROM simulation_runs WHERE simulationId = ?", (simulation_id,)
        )
        if simulation:
            for field in (
                "originalData",
                "simulatedData",
                "originalRisks",
                "simulatedRisks",
                "aiExplanation",
            ):
                value = simulation.get(field)
                if value is not None and isinstance(value, str):
                    try:
                        simulation[field] = json.loads(value)
                    except json.JSONDecodeError:
                        if field != "aiExplanation":
                            raise
                        simulation[field] = {"raw_response": value}
        return simulation

    async def save(self, simulation: Dict[str, Any]) -> Dict[str, Any]:
        await self.execute(
            """
            INSERT INTO simulation_runs (
                simulationId, locationId, originalData, simulatedData,
                originalRisks, simulatedRisks, aiExplanation
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                simulation["simulationId"],
                simulation["locationId"],
                _json_value(simulation["originalData"]),
                _json_value(simulation["simulatedData"]),
                _json_value(simulation["originalRisks"]),
                _json_value(simulation["simulatedRisks"]),
                _json_value(simulation["aiExplanation"])
                if simulation.get("aiExplanation") is not None
                else None,
            ),
        )
        return simulation