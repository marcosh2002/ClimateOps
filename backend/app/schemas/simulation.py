from typing import Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from app.database.models import SimulationRun


class SimulationRequest(BaseModel):
    temperature_change: Optional[float] = Field(None, ge=-20, le=20)
    humidity_change: Optional[float] = Field(None, ge=-50, le=50)
    rainfall_change_pct: Optional[float] = Field(None, ge=-100, le=500)
    rainfall_change_mm: Optional[float] = Field(None, ge=-500, le=500)
    river_level_change: Optional[float] = Field(None, ge=-50, le=50)
    river_trend: Optional[str] = Field(None, pattern="^(RISING|FALLING|STABLE)$")
    add_alert: Optional[Dict[str, Any]] = None
    remove_alert_type: Optional[str] = None


class SimulationResponse(BaseModel):
    simulationId: str
    locationId: str
    scenario: SimulationRequest
    originalRisks: Dict[str, int]
    simulatedRisks: Dict[str, int]
    comparison: Dict[str, Any]
    summary: str
    aiExplanation: Optional[Dict[str, Any]] = None
    createdAt: str


class SimulationRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    simulationId: str
    locationId: str
    originalData: Dict[str, Any]
    simulatedData: Dict[str, Any]
    originalRisks: Dict[str, int]
    simulatedRisks: Dict[str, int]
    aiExplanation: Optional[Dict[str, Any]] = None
    createdAt: datetime