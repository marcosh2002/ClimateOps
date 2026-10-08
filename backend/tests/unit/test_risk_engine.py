import pytest
from datetime import datetime

from app.database.models import EnvironmentalObservation, WeatherData, WaterData, AlertData
from app.core.risk_engine import (
    assess_all_risks,
    calculate_heat_risk,
    calculate_flood_risk,
    calculate_water_stress_risk,
    calculate_drought_risk,
    RiskThresholds,
)


@pytest.fixture
def high_heat_observation():
    return EnvironmentalObservation(
        locationId="TEST-001",
        timestamp=datetime.utcnow(),
        weather=WeatherData(temperature=42.0, humidity=85, rainfall=0, windSpeed=10, pressure=1005),
        water=WaterData(riverLevel=10.0, riverLevelTrend="STABLE"),
        alerts=[],
        source="test",
    )


@pytest.fixture
def high_flood_observation():
    return EnvironmentalObservation(
        locationId="TEST-002",
        timestamp=datetime.utcnow(),
        weather=WeatherData(temperature=28.0, humidity=90, rainfall=150, windSpeed=15, pressure=995),
        water=WaterData(riverLevel=45.0, riverLevelTrend="RISING"),
        alerts=[AlertData(type="FLOOD", severity="SEVERE", description="Flood warning", issuedAt=datetime.utcnow())],
        source="test",
    )


@pytest.fixture
def drought_observation():
    return EnvironmentalObservation(
        locationId="TEST-003",
        timestamp=datetime.utcnow(),
        weather=WeatherData(temperature=38.0, humidity=30, rainfall=2, windSpeed=5, pressure=1015),
        water=WaterData(riverLevel=5.0, riverLevelTrend="FALLING"),
        alerts=[AlertData(type="DROUGHT", severity="MODERATE", description="Drought conditions", issuedAt=datetime.utcnow())],
        source="test",
    )


def test_calculate_heat_risk_high(high_heat_observation):
    score, severity, factors = calculate_heat_risk(high_heat_observation)
    assert score >= 80
    assert severity.value == "CRITICAL"
    assert any("Temperature" in f for f in factors)
    assert any("humidity" in f.lower() for f in factors)


def test_calculate_heat_risk_low():
    obs = EnvironmentalObservation(
        locationId="TEST-004",
        timestamp=datetime.utcnow(),
        weather=WeatherData(temperature=25.0, humidity=50, rainfall=10, windSpeed=5, pressure=1010),
        water=None,
        alerts=[],
        source="test",
    )
    score, severity, factors = calculate_heat_risk(obs)
    assert score <= 30
    assert severity.value == "LOW"


def test_calculate_flood_risk_high(high_flood_observation):
    score, severity, factors = calculate_flood_risk(high_flood_observation)
    assert score >= 80
    assert severity.value == "CRITICAL"
    assert any("rainfall" in f.lower() for f in factors)
    assert any("river" in f.lower() for f in factors)
    assert any("warning" in f.lower() for f in factors)


def test_calculate_flood_risk_no_warning():
    obs = EnvironmentalObservation(
        locationId="TEST-005",
        timestamp=datetime.utcnow(),
        weather=WeatherData(temperature=28.0, humidity=80, rainfall=80, windSpeed=10, pressure=1000),
        water=WaterData(riverLevel=20.0, riverLevelTrend="STABLE"),
        alerts=[],
        source="test",
    )
    score, severity, factors = calculate_flood_risk(obs)
    assert score < 80


def test_calculate_water_stress_risk():
    obs = EnvironmentalObservation(
        locationId="TEST-006",
        timestamp=datetime.utcnow(),
        weather=WeatherData(temperature=36.0, humidity=40, rainfall=5, windSpeed=10, pressure=1010),
        water=WaterData(riverLevel=8.0, riverLevelTrend="FALLING"),
        alerts=[],
        source="test",
    )
    score, severity, factors = calculate_water_stress_risk(obs)
    assert score >= 60
    assert any("rainfall" in f.lower() for f in factors)
    assert any("river" in f.lower() for f in factors)


def test_calculate_drought_risk_high(drought_observation):
    score, severity, factors = calculate_drought_risk(drought_observation)
    assert score >= 80
    assert severity.value == "CRITICAL"
    assert any("rainfall" in f.lower() for f in factors)
    assert any("heat" in f.lower() or "temperature" in f.lower() for f in factors)


def test_assess_all_risks(high_heat_observation):
    assessment = assess_all_risks(high_heat_observation)
    assert assessment.locationId == "TEST-001"
    assert assessment.heatRisk >= 80
    assert assessment.heatSeverity.value == "CRITICAL"
    assert "heat" in assessment.contributingFactors
    assert len(assessment.dataSources) > 0


def test_risk_thresholds_custom():
    custom = RiskThresholds(
        heat={"low": 20, "medium": 50, "high": 75},
        flood={"low": 20, "medium": 50, "high": 75},
        water_stress={"low": 20, "medium": 50, "high": 75},
        drought={"low": 20, "medium": 50, "high": 75},
    )
    obs = EnvironmentalObservation(
        locationId="TEST-007",
        timestamp=datetime.utcnow(),
        weather=WeatherData(temperature=38.0, humidity=70, rainfall=10, windSpeed=10, pressure=1005),
        water=None,
        alerts=[],
        source="test",
    )
    assessment = assess_all_risks(obs, custom)
    assert assessment.heatSeverity.value in ["HIGH", "CRITICAL"]