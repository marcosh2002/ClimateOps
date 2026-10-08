from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentType(str, Enum):
    HEAT = "HEAT"
    FLOOD = "FLOOD"
    HEAVY_RAIN = "HEAVY_RAIN"
    WATER_STRESS = "WATER_STRESS"
    DROUGHT = "DROUGHT"


class IncidentSeverity(str, Enum):
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EXTREME = "EXTREME"


class IncidentStatus(str, Enum):
    MONITORING = "MONITORING"
    ACTIVE = "ACTIVE"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EXTREME = "EXTREME"
    RECOVERY = "RECOVERY"
    RESOLVED = "RESOLVED"


class RiverTrend(str, Enum):
    RISING = "RISING"
    FALLING = "FALLING"
    STABLE = "STABLE"


class LocationBase(BaseModel):
    country: str
    state: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class LocationCreate(LocationBase):
    locationId: str
    monitoringEnabled: bool = False
    riskTypes: List[str] = []


class Location(LocationBase):
    model_config = ConfigDict(from_attributes=True)

    locationId: str
    monitoringEnabled: bool = False
    riskTypes: List[str] = []
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WeatherData(BaseModel):
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    rainfall: Optional[float] = None
    windSpeed: Optional[float] = None
    pressure: Optional[float] = None


class WaterData(BaseModel):
    riverLevel: Optional[float] = None
    riverLevelTrend: Optional[RiverTrend] = None


class AlertData(BaseModel):
    type: str
    severity: str
    description: str
    issuedAt: datetime
    expiresAt: Optional[datetime] = None


class EnvironmentalObservation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    locationId: str
    timestamp: datetime
    weather: Optional[WeatherData] = None
    water: Optional[WaterData] = None
    alerts: List[AlertData] = []
    source: str
    rawData: Optional[Dict[str, Any]] = None


class RiskAssessment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    locationId: str
    timestamp: datetime
    heatRisk: int = Field(ge=0, le=100)
    floodRisk: int = Field(ge=0, le=100)
    waterStressRisk: int = Field(ge=0, le=100)
    droughtRisk: int = Field(ge=0, le=100)
    heatSeverity: RiskLevel
    floodSeverity: RiskLevel
    waterStressSeverity: RiskLevel
    droughtSeverity: RiskLevel
    contributingFactors: Dict[str, List[str]] = {}
    dataSources: List[str] = []


class IncidentBase(BaseModel):
    locationId: str
    type: IncidentType
    severity: IncidentSeverity
    status: IncidentStatus
    riskScore: int = Field(ge=0, le=100)
    source: Optional[str] = None


class IncidentCreate(IncidentBase):
    incidentId: str


class Incident(IncidentBase):
    model_config = ConfigDict(from_attributes=True)

    incidentId: str
    createdAt: datetime
    lastUpdated: datetime
    lastChecked: Optional[datetime] = None
    nextCheck: Optional[datetime] = None
    aiExplanation: Optional[Dict[str, Any]] = None


class IncidentObservation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    incidentId: str
    timestamp: datetime
    rainfall: Optional[float] = None
    temperature: Optional[float] = None
    riverLevel: Optional[float] = None
    riskScore: int = Field(ge=0, le=100)
    severity: IncidentSeverity
    source: str


class SimulationRun(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    simulationId: str
    locationId: str
    originalData: Dict[str, Any]
    simulatedData: Dict[str, Any]
    originalRisks: Dict[str, int]
    simulatedRisks: Dict[str, int]
    aiExplanation: Optional[Dict[str, Any]] = None
    createdAt: datetime


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    pageSize: int
    hasMore: bool