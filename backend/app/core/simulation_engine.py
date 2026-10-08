from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
import uuid
import copy

from app.core.risk_engine import assess_all_risks, RiskThresholds
from app.database.models import EnvironmentalObservation, SimulationRun, WeatherData, WaterData, AlertData


@dataclass
class SimulationParams:
    temperature_change: Optional[float] = None
    humidity_change: Optional[float] = None
    rainfall_change_pct: Optional[float] = None
    rainfall_change_mm: Optional[float] = None
    river_level_change: Optional[float] = None
    river_trend: Optional[str] = None
    add_alert: Optional[Dict[str, Any]] = None
    remove_alert_type: Optional[str] = None


def apply_simulation(
    observation: EnvironmentalObservation,
    params: SimulationParams,
) -> EnvironmentalObservation:
    simulated = copy.deepcopy(observation)

    if simulated.weather is None:
        simulated.weather = WeatherData()

    if params.temperature_change is not None:
        if simulated.weather.temperature is not None:
            simulated.weather.temperature += params.temperature_change
        else:
            simulated.weather.temperature = params.temperature_change

    if params.humidity_change is not None:
        if simulated.weather.humidity is not None:
            simulated.weather.humidity = max(0, min(100, simulated.weather.humidity + params.humidity_change))
        else:
            simulated.weather.humidity = max(0, min(100, params.humidity_change))

    if params.rainfall_change_pct is not None:
        if simulated.weather.rainfall is not None:
            simulated.weather.rainfall = max(0, simulated.weather.rainfall * (1 + params.rainfall_change_pct / 100))
    elif params.rainfall_change_mm is not None:
        if simulated.weather.rainfall is not None:
            simulated.weather.rainfall = max(0, simulated.weather.rainfall + params.rainfall_change_mm)
        else:
            simulated.weather.rainfall = max(0, params.rainfall_change_mm)

    if simulated.water is None:
        simulated.water = WaterData()

    if params.river_level_change is not None:
        if simulated.water.riverLevel is not None:
            simulated.water.riverLevel = max(0, simulated.water.riverLevel + params.river_level_change)
        else:
            simulated.water.riverLevel = max(0, params.river_level_change)

    if params.river_trend is not None:
        simulated.water.riverLevelTrend = params.river_trend

    if params.add_alert:
        alert = AlertData(**params.add_alert)
        simulated.alerts.append(alert)

    if params.remove_alert_type:
        simulated.alerts = [a for a in simulated.alerts if params.remove_alert_type.lower() not in a.type.lower()]

    simulated.timestamp = datetime.utcnow()
    simulated.source = "simulation"

    return simulated


def run_simulation(
    observation: EnvironmentalObservation,
    params: SimulationParams,
    risk_thresholds: Optional[RiskThresholds] = None,
) -> tuple[EnvironmentalObservation, SimulationRun]:
    simulated_obs = apply_simulation(observation, params)

    original_risks = assess_all_risks(observation, risk_thresholds)
    simulated_risks = assess_all_risks(simulated_obs, risk_thresholds)

    original_risk_dict = {
        "heat": original_risks.heatRisk,
        "flood": original_risks.floodRisk,
        "water_stress": original_risks.waterStressRisk,
        "drought": original_risks.droughtRisk,
    }

    simulated_risk_dict = {
        "heat": simulated_risks.heatRisk,
        "flood": simulated_risks.floodRisk,
        "water_stress": simulated_risks.waterStressRisk,
        "drought": simulated_risks.droughtRisk,
    }

    simulation = SimulationRun(
        simulationId=f"SIM-{uuid.uuid4().hex[:8].upper()}",
        locationId=observation.locationId,
        originalData=observation.model_dump(),
        simulatedData=simulated_obs.model_dump(),
        originalRisks=original_risk_dict,
        simulatedRisks=simulated_risk_dict,
        aiExplanation=None,
        createdAt=datetime.utcnow(),
    )

    return simulated_obs, simulation


def get_risk_comparison(original: Dict[str, int], simulated: Dict[str, int]) -> Dict[str, Dict[str, Any]]:
    comparison = {}
    for risk_type in ["heat", "flood", "water_stress", "drought"]:
        orig = original.get(risk_type, 0)
        sim = simulated.get(risk_type, 0)
        change = sim - orig
        comparison[risk_type] = {
            "original": orig,
            "simulated": sim,
            "change": change,
            "change_pct": round((change / orig * 100) if orig > 0 else 0, 1),
            "worsened": change > 0,
        }
    return comparison


def generate_simulation_summary(
    observation: EnvironmentalObservation,
    simulated_obs: EnvironmentalObservation,
    comparison: Dict[str, Dict[str, Any]],
) -> str:
    lines = []
    lines.append("SIMULATION SCENARIO")
    lines.append("=" * 40)

    if observation.weather and simulated_obs.weather:
        if observation.weather.temperature != simulated_obs.weather.temperature:
            diff = simulated_obs.weather.temperature - observation.weather.temperature
            lines.append(f"Temperature: {observation.weather.temperature:.1f}°C → {simulated_obs.weather.temperature:.1f}°C ({diff:+.1f}°C)")

        if observation.weather.humidity != simulated_obs.weather.humidity:
            diff = simulated_obs.weather.humidity - observation.weather.humidity
            lines.append(f"Humidity: {observation.weather.humidity:.0f}% → {simulated_obs.weather.humidity:.0f}% ({diff:+.0f}%)")

        if observation.weather.rainfall != simulated_obs.weather.rainfall:
            diff = simulated_obs.weather.rainfall - observation.weather.rainfall
            lines.append(f"Rainfall: {observation.weather.rainfall:.1f}mm → {simulated_obs.weather.rainfall:.1f}mm ({diff:+.1f}mm)")

    if observation.water and simulated_obs.water:
        if observation.water.riverLevel != simulated_obs.water.riverLevel:
            diff = simulated_obs.water.riverLevel - observation.water.riverLevel
            lines.append(f"River Level: {observation.water.riverLevel:.1f}m → {simulated_obs.water.riverLevel:.1f}m ({diff:+.1f}m)")

        if observation.water.riverLevelTrend != simulated_obs.water.riverLevelTrend:
            lines.append(f"River Trend: {observation.water.riverLevelTrend} → {simulated_obs.water.riverLevelTrend}")

    lines.append("")
    lines.append("RISK COMPARISON")
    lines.append("-" * 40)

    for risk_type, data in comparison.items():
        risk_name = risk_type.replace("_", " ").title()
        lines.append(f"{risk_name:15} {data['original']:3d}% → {data['simulated']:3d}% ({data['change']:+d}%)")

    lines.append("")
    worsened = [k for k, v in comparison.items() if v["worsened"]]
    improved = [k for k, v in comparison.items() if not v["worsened"] and v["change"] != 0]

    if worsened:
        lines.append(f"⚠ Risks worsening: {', '.join(worsened)}")
    if improved:
        lines.append(f"✓ Risks improving: {', '.join(improved)}")

    return "\n".join(lines)