from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.database.models import Incident, IncidentObservation, IncidentStatus, IncidentSeverity, IncidentType


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    incidentId: str
    locationId: str
    type: IncidentType
    severity: IncidentSeverity
    status: IncidentStatus
    riskScore: int
    source: Optional[str] = None
    createdAt: datetime
    lastUpdated: datetime
    lastChecked: Optional[datetime] = None
    nextCheck: Optional[datetime] = None
    aiExplanation: Optional[Dict[str, Any]] = None


class IncidentTimelineObservation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    incidentId: str
    timestamp: datetime
    rainfall: Optional[float] = None
    temperature: Optional[float] = None
    riverLevel: Optional[float] = None
    riskScore: int
    severity: IncidentSeverity
    source: str


class IncidentTimelineResponse(BaseModel):
    incidentId: str
    incident: IncidentResponse
    timeline: List[IncidentTimelineObservation]


class IncidentSummaryResponse(BaseModel):
    total: int
    by_type: Dict[str, int]
    by_severity: Dict[str, int]
    by_status: Dict[str, int]
    critical_count: int
    high_risk_count: int