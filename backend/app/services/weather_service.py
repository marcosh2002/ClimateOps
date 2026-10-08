from typing import List, Optional, Dict, Any
from datetime import datetime

import structlog

from app.adapters import create_adapters
from app.config import settings
from app.database.models import EnvironmentalObservation
from app.database import ObservationsRepository
from app.core import assess_all_risks
from app.database import RiskAssessmentsRepository
from app.database.models import RiskAssessment

logger = structlog.get_logger(__name__)


class WeatherService:
    def __init__(
        self,
        observations_repo: ObservationsRepository,
        risk_assessments_repo: RiskAssessmentsRepository,
    ):
        self.observations_repo = observations_repo
        self.risk_assessments_repo = risk_assessments_repo
        self.adapters = create_adapters(
            openweather_key=settings.OPENWEATHER_API_KEY or "",
            imd_base_url=settings.IMD_API_BASE_URL,
            imd_api_key=settings.IMD_API_KEY,
            cwc_base_url=settings.CWC_API_BASE_URL,
            cwc_api_key=settings.CWC_API_KEY,
        )

    async def get_latest_observation(self, location_id: str) -> Optional[EnvironmentalObservation]:
        data = await self.observations_repo.get_latest(location_id)
        return EnvironmentalObservation(**data) if data else None

    async def fetch_and_store_current(
        self,
        location_id: str,
        lat: float,
        lon: float,
        adapter_names: Optional[List[str]] = None,
    ) -> List[EnvironmentalObservation]:
        if adapter_names is None:
            adapter_names = ["openweather"]

        observations = []
        for name in adapter_names:
            adapter = self.adapters.get(name)
            if not adapter:
                continue

            try:
                obs = await adapter.fetch_current(location_id, lat, lon)
                await self.observations_repo.save(obs.model_dump())
                observations.append(obs)
            except Exception as e:
                logger.warning(
                    "Environmental provider fetch failed",
                    provider=name,
                    location_id=location_id,
                    error=str(e),
                )

        if observations:
            combined = self._combine_observations(observations)
            await self.observations_repo.save(combined.model_dump())
            await self._assess_and_store_risk(combined)
            return [combined] + observations

        return []

    async def fetch_and_store_forecast(
        self,
        location_id: str,
        lat: float,
        lon: float,
        hours: int = 48,
        adapter_name: str = "openweather",
    ) -> List[EnvironmentalObservation]:
        adapter = self.adapters.get(adapter_name)
        if not adapter:
            return []

        try:
            forecasts = await adapter.fetch_forecast(location_id, lat, lon, hours)
            for forecast in forecasts:
                await self.observations_repo.save(forecast.model_dump())
            return forecasts
        except Exception as e:
            logger.warning(
                "Forecast provider fetch failed",
                provider=adapter_name,
                location_id=location_id,
                error=str(e),
            )
            return []

    def _combine_observations(self, observations: List[EnvironmentalObservation]) -> EnvironmentalObservation:
        if not observations:
            raise ValueError("No observations to combine")

        primary = observations[0]
        combined_weather = primary.weather
        combined_water = primary.water
        combined_alerts = list(primary.alerts)
        combined_sources = [primary.source]

        for obs in observations[1:]:
            combined_sources.append(obs.source)

            if obs.weather:
                if combined_weather is None:
                    combined_weather = obs.weather
                else:
                    if obs.weather.temperature is not None:
                        combined_weather.temperature = obs.weather.temperature
                    if obs.weather.humidity is not None:
                        combined_weather.humidity = obs.weather.humidity
                    if obs.weather.rainfall is not None and obs.weather.rainfall > (combined_weather.rainfall or 0):
                        combined_weather.rainfall = obs.weather.rainfall
                    if obs.weather.windSpeed is not None:
                        combined_weather.windSpeed = obs.weather.windSpeed
                    if obs.weather.pressure is not None:
                        combined_weather.pressure = obs.weather.pressure

            if obs.water:
                if combined_water is None:
                    combined_water = obs.water
                else:
                    if obs.water.riverLevel is not None:
                        combined_water.riverLevel = obs.water.riverLevel
                    if obs.water.riverLevelTrend is not None:
                        combined_water.riverLevelTrend = obs.water.riverLevelTrend

            for alert in obs.alerts:
                if not any(a.type == alert.type and a.description == alert.description for a in combined_alerts):
                    combined_alerts.append(alert)

        return EnvironmentalObservation(
            locationId=primary.locationId,
            timestamp=datetime.utcnow(),
            weather=combined_weather,
            water=combined_water,
            alerts=combined_alerts,
            source="+".join(combined_sources),
            rawData={src: obs.rawData for src, obs in zip(combined_sources, observations)},
        )

    async def _assess_and_store_risk(self, observation: EnvironmentalObservation) -> None:
        assessment = assess_all_risks(observation)
        await self.risk_assessments_repo.save(assessment.model_dump(mode="json"))

    async def get_latest_risk_assessment(self, location_id: str) -> Optional[Dict[str, Any]]:
        data = await self.risk_assessments_repo.get_latest(location_id)
        if data:
            return RiskAssessment(**data).model_dump(mode="json")
        return None

    async def get_observation_history(self, location_id: str, hours: int = 24) -> List[EnvironmentalObservation]:
        data = await self.observations_repo.get_history(location_id, hours)
        return [EnvironmentalObservation(**d) for d in data]

    async def get_monitored_locations_data(self) -> Dict[str, Dict[str, Any]]:
        from app.services.location_service import LocationService
        from app.database import LocationsRepository

        locations_repo = LocationsRepository()
        location_service = LocationService(locations_repo)
        monitored = await location_service.get_monitored_locations()

        result = {}
        for location in monitored:
            obs = await self.get_latest_observation(location.locationId)
            risk = await self.get_latest_risk_assessment(location.locationId)
            result[location.locationId] = {
                "location": location.model_dump(),
                "observation": obs.model_dump() if obs else None,
                "risk": risk,
            }

        return result