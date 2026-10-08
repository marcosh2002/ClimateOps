from dataclasses import dataclass, field
from typing import Dict, List, Optional

from app.database.models import EnvironmentalObservation, RiskAssessment, RiskLevel


@dataclass
class RiskThresholds:
    heat: Dict[str, float] = field(default_factory=lambda: {"low": 30, "medium": 60, "high": 80})
    flood: Dict[str, float] = field(default_factory=lambda: {"low": 30, "medium": 60, "high": 80})
    water_stress: Dict[str, float] = field(default_factory=lambda: {"low": 30, "medium": 60, "high": 80})
    drought: Dict[str, float] = field(default_factory=lambda: {"low": 30, "medium": 60, "high": 80})

    temperature_critical: float = 40.0
    humidity_factor: float = 0.3
    rainfall_24h_critical_mm: float = 100.0
    river_level_rising_weight: float = 0.4
    rainfall_deficit_weight: float = 0.5
    groundwater_decline_weight: float = 0.5
    spi_threshold: float = -1.5


DEFAULT_THRESHOLDS = RiskThresholds()


def calculate_severity(score: int, thresholds: Dict[str, float]) -> RiskLevel:
    if score <= thresholds["low"]:
        return RiskLevel.LOW
    elif score <= thresholds["medium"]:
        return RiskLevel.MEDIUM
    elif score <= thresholds["high"]:
        return RiskLevel.HIGH
    else:
        return RiskLevel.CRITICAL


def calculate_heat_risk(obs: EnvironmentalObservation, thresholds: RiskThresholds = DEFAULT_THRESHOLDS) -> tuple[int, RiskLevel, List[str]]:
    factors = []
    score = 0

    if not obs.weather or obs.weather.temperature is None:
        return 0, RiskLevel.LOW, ["No temperature data available"]

    temp = obs.weather.temperature
    humidity = obs.weather.humidity or 50

    if temp >= thresholds.temperature_critical:
        score += 40
        factors.append(f"Temperature {temp}°C exceeds critical threshold ({thresholds.temperature_critical}°C)")
    elif temp >= 35:
        score += 25
        factors.append(f"High temperature: {temp}°C")
    elif temp >= 30:
        score += 15
        factors.append(f"Elevated temperature: {temp}°C")

    if humidity >= 80:
        score += int(20 * thresholds.humidity_factor)
        factors.append(f"High humidity: {humidity}%")
    elif humidity >= 60:
        score += int(10 * thresholds.humidity_factor)
        factors.append(f"Moderate humidity: {humidity}%")

    if obs.weather.rainfall is not None and obs.weather.rainfall < 5:
        score += 10
        factors.append("Little to no recent rainfall")

    score = min(score, 100)
    severity = calculate_severity(score, thresholds.heat)
    return score, severity, factors


def calculate_flood_risk(obs: EnvironmentalObservation, thresholds: RiskThresholds = DEFAULT_THRESHOLDS) -> tuple[int, RiskLevel, List[str]]:
    factors = []
    score = 0

    if obs.weather and obs.weather.rainfall is not None:
        rainfall = obs.weather.rainfall
        if rainfall >= thresholds.rainfall_24h_critical_mm:
            score += 40
            factors.append(f"Heavy rainfall: {rainfall}mm (exceeds {thresholds.rainfall_24h_critical_mm}mm threshold)")
        elif rainfall >= 50:
            score += 25
            factors.append(f"Significant rainfall: {rainfall}mm")
        elif rainfall >= 20:
            score += 15
            factors.append(f"Moderate rainfall: {rainfall}mm")

    if obs.water and obs.water.riverLevel is not None:
        if obs.water.riverLevelTrend == "RISING":
            score += int(30 * thresholds.river_level_rising_weight)
            factors.append(f"River level rising: {obs.water.riverLevel}m")
        elif obs.water.riverLevelTrend == "FALLING":
            score += 5
            factors.append(f"River level falling: {obs.water.riverLevel}m")

    official_warnings = [a for a in obs.alerts if "flood" in a.type.lower() or "heavy rain" in a.type.lower()]
    if official_warnings:
        score += 25
        factors.append(f"Official flood warning active: {len(official_warnings)} alert(s)")

    score = min(score, 100)
    severity = calculate_severity(score, thresholds.flood)
    return score, severity, factors


def calculate_water_stress_risk(obs: EnvironmentalObservation, thresholds: RiskThresholds = DEFAULT_THRESHOLDS) -> tuple[int, RiskLevel, List[str]]:
    factors = []
    score = 0

    if obs.weather and obs.weather.rainfall is not None:
        if obs.weather.rainfall < 10:
            score += int(30 * thresholds.rainfall_deficit_weight)
            factors.append(f"Rainfall deficit: {obs.weather.rainfall}mm")
        elif obs.weather.rainfall < 50:
            score += int(15 * thresholds.rainfall_deficit_weight)
            factors.append(f"Below average rainfall: {obs.weather.rainfall}mm")

    if obs.water and obs.water.riverLevel is not None:
        if obs.water.riverLevelTrend == "FALLING":
            score += int(25 * thresholds.groundwater_decline_weight)
            factors.append(f"River level declining: {obs.water.riverLevel}m")
        elif obs.water.riverLevelTrend == "STABLE" and obs.water.riverLevel < 10:
            score += 15
            factors.append(f"Low river level: {obs.water.riverLevel}m")

    if obs.weather and obs.weather.temperature is not None and obs.weather.temperature > 35:
        score += 15
        factors.append(f"High temperature increasing evaporation: {obs.weather.temperature}°C")

    score = min(score, 100)
    severity = calculate_severity(score, thresholds.water_stress)
    return score, severity, factors


def calculate_drought_risk(obs: EnvironmentalObservation, thresholds: RiskThresholds = DEFAULT_THRESHOLDS) -> tuple[int, RiskLevel, List[str]]:
    factors = []
    score = 0

    if obs.weather and obs.weather.rainfall is not None:
        if obs.weather.rainfall < 5:
            score += 35
            factors.append(f"Severe rainfall deficit: {obs.weather.rainfall}mm")
        elif obs.weather.rainfall < 20:
            score += 20
            factors.append(f"Rainfall deficit: {obs.weather.rainfall}mm")

    if obs.weather and obs.weather.temperature is not None:
        if obs.weather.temperature > 40:
            score += 25
            factors.append(f"Extreme heat: {obs.weather.temperature}°C")
        elif obs.weather.temperature > 35:
            score += 15
            factors.append(f"High temperature: {obs.weather.temperature}°C")

    if obs.water and obs.water.riverLevel is not None and obs.water.riverLevelTrend == "FALLING":
        score += 20
        factors.append("River level continuously falling")

    official_drought = [a for a in obs.alerts if "drought" in a.type.lower()]
    if official_drought:
        score += 20
        factors.append("Official drought declaration")

    score = min(score, 100)
    severity = calculate_severity(score, thresholds.drought)
    return score, severity, factors


def assess_all_risks(
    obs: EnvironmentalObservation,
    thresholds: Optional[RiskThresholds] = None,
) -> RiskAssessment:
    thresholds = thresholds or DEFAULT_THRESHOLDS
    heat_score, heat_severity, heat_factors = calculate_heat_risk(obs, thresholds)
    flood_score, flood_severity, flood_factors = calculate_flood_risk(obs, thresholds)
    water_stress_score, water_stress_severity, water_stress_factors = calculate_water_stress_risk(obs, thresholds)
    drought_score, drought_severity, drought_factors = calculate_drought_risk(obs, thresholds)

    all_factors = {
        "heat": heat_factors,
        "flood": flood_factors,
        "water_stress": water_stress_factors,
        "drought": drought_factors,
    }

    data_sources = [obs.source] if obs.source else []
    if obs.rawData:
        data_sources.append("raw_api")

    return RiskAssessment(
        locationId=obs.locationId,
        timestamp=obs.timestamp,
        heatRisk=heat_score,
        floodRisk=flood_score,
        waterStressRisk=water_stress_score,
        droughtRisk=drought_score,
        heatSeverity=heat_severity,
        floodSeverity=flood_severity,
        waterStressSeverity=water_stress_severity,
        droughtSeverity=drought_severity,
        contributingFactors=all_factors,
        dataSources=list(set(data_sources)),
    )


def get_overall_risk_level(assessment: RiskAssessment) -> RiskLevel:
    scores = [
        assessment.heatRisk,
        assessment.floodRisk,
        assessment.waterStressRisk,
        assessment.droughtRisk,
    ]
    max_score = max(scores)
    return calculate_severity(max_score, DEFAULT_THRESHOLDS.heat)