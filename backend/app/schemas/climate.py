from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.database.models import Location, EnvironmentalObservation, RiskAssessment, RiskLevel


class LocationSearchResult(BaseModel):
    locationId: str
    country: str
    state: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    latitude: float
    longitude: float
    source: str = "database"


class ClimateRiskResponse(BaseModel):
    location: Location
    observation: EnvironmentalObservation
    risk: RiskAssessment


class RiskFactorDetail(BaseModel):
    score: int
    severity: RiskLevel
    factors: List[str]


class ClimateRiskDetail(BaseModel):
    heat: RiskFactorDetail
    flood: RiskFactorDetail
    water_stress: RiskFactorDetail
    drought: RiskFactorDetail