from typing import Any, Dict, Optional

import structlog
from fastapi import APIRouter, Body, Depends, HTTPException, Path
from pydantic import BaseModel, Field

from app.api.deps import get_location_service, get_simulations_repo, get_weather_service
from app.core import (
    SimulationParams,
    generate_simulation_summary,
    get_risk_comparison,
    run_simulation,
)
from app.core.groq import groq_client
from app.database import SimulationsRepository
from app.services.location_service import LocationService
from app.services.weather_service import WeatherService

router = APIRouter()
simulation_lookup_router = APIRouter()
logger = structlog.get_logger(__name__)


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


@router.post("/{location_id}/simulate", response_model=SimulationResponse)
async def simulate_climate(
    location_id: str = Path(..., description="Location ID"),
    request: SimulationRequest = Body(...),
    weather_service: WeatherService = Depends(get_weather_service),
    location_service: LocationService = Depends(get_location_service),
    simulations_repo: SimulationsRepository = Depends(get_simulations_repo),
):
    location = await location_service.get_location(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    observation = await weather_service.get_latest_observation(location_id)
    if not observation:
        await weather_service.fetch_and_store_current(
            location_id, location.latitude, location.longitude
        )
        observation = await weather_service.get_latest_observation(location_id)

    if not observation:
        raise HTTPException(status_code=503, detail="Unable to fetch environmental data")

    params = SimulationParams(
        temperature_change=request.temperature_change,
        humidity_change=request.humidity_change,
        rainfall_change_pct=request.rainfall_change_pct,
        rainfall_change_mm=request.rainfall_change_mm,
        river_level_change=request.river_level_change,
        river_trend=request.river_trend,
        add_alert=request.add_alert,
        remove_alert_type=request.remove_alert_type,
    )

    simulated_obs, simulation_record = run_simulation(observation, params)

    comparison = get_risk_comparison(simulation_record.originalRisks, simulation_record.simulatedRisks)
    summary = generate_simulation_summary(observation, simulated_obs, comparison)

    scenario_desc_parts = []
    if request.temperature_change:
        scenario_desc_parts.append(f"Temperature {request.temperature_change:+.1f}°C")
    if request.humidity_change:
        scenario_desc_parts.append(f"Humidity {request.humidity_change:+.0f}%")
    if request.rainfall_change_pct:
        scenario_desc_parts.append(f"Rainfall {request.rainfall_change_pct:+.0f}%")
    if request.rainfall_change_mm:
        scenario_desc_parts.append(f"Rainfall {request.rainfall_change_mm:+.1f}mm")
    if request.river_level_change:
        scenario_desc_parts.append(f"River level {request.river_level_change:+.1f}m")
    if request.river_trend:
        scenario_desc_parts.append(f"River trend {request.river_trend}")
    scenario_desc = "; ".join(scenario_desc_parts) if scenario_desc_parts else "No changes"

    ai_explanation = None
    try:
        ai_explanation = await groq_client.explain_simulation(
            simulation_record.originalRisks,
            simulation_record.simulatedRisks,
            location.city or location.district or location.state,
            scenario_desc,
        )
    except Exception as e:
        logger.warning("Groq simulation explanation failed", error=str(e))

    simulation_record.aiExplanation = ai_explanation
    await simulations_repo.save(simulation_record.model_dump())

    return SimulationResponse(
        simulationId=simulation_record.simulationId,
        locationId=location_id,
        scenario=request,
        originalRisks=simulation_record.originalRisks,
        simulatedRisks=simulation_record.simulatedRisks,
        comparison=comparison,
        summary=summary,
        aiExplanation=ai_explanation,
        createdAt=simulation_record.createdAt.isoformat(),
    )


@simulation_lookup_router.get("/simulations/{simulation_id}")
async def get_simulation(
    simulation_id: str = Path(..., description="Simulation ID"),
    simulations_repo: SimulationsRepository = Depends(get_simulations_repo),
):
    simulation = await simulations_repo.get_by_id(simulation_id)
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return simulation