import asyncio
import sys
from app.config import settings
from app.database import (
    IncidentsRepository,
    IncidentObservationsRepository,
    LocationsRepository,
)
from app.services.weather_service import WeatherService
from app.services.location_service import LocationService
from app.services.monitoring_service import MonitoringService
from app.database import ObservationsRepository, RiskAssessmentsRepository


async def run_monitoring_once():
    print("Running one-time monitoring cycle...")

    locations_repo = LocationsRepository()
    observations_repo = ObservationsRepository()
    risk_assessments_repo = RiskAssessmentsRepository()
    incidents_repo = IncidentsRepository()
    incident_obs_repo = IncidentObservationsRepository()

    location_service = LocationService(locations_repo)
    weather_service = WeatherService(observations_repo, risk_assessments_repo)
    monitoring_service = MonitoringService(
        incidents_repo,
        incident_obs_repo,
        locations_repo,
        weather_service,
        location_service,
    )

    result = await monitoring_service.trigger_monitoring_now()
    print(f"Monitoring result: {result}")
    return result


async def run_continuous_monitoring():
    print("Starting continuous monitoring (Ctrl+C to stop)...")

    locations_repo = LocationsRepository()
    observations_repo = ObservationsRepository()
    risk_assessments_repo = RiskAssessmentsRepository()
    incidents_repo = IncidentsRepository()
    incident_obs_repo = IncidentObservationsRepository()

    location_service = LocationService(locations_repo)
    weather_service = WeatherService(observations_repo, risk_assessments_repo)
    monitoring_service = MonitoringService(
        incidents_repo,
        incident_obs_repo,
        locations_repo,
        weather_service,
        location_service,
    )

    await monitoring_service.start_monitoring()

    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        print("\nStopping monitoring...")
        await monitoring_service.stop_monitoring()


async def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        await run_continuous_monitoring()
    else:
        await run_monitoring_once()


if __name__ == "__main__":
    asyncio.run(main())