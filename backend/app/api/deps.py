from functools import lru_cache
 
from app.database import (
    LocationsRepository,
    ObservationsRepository,
    RiskAssessmentsRepository,
    IncidentsRepository,
    IncidentObservationsRepository,
    SimulationsRepository,
)
from app.services.location_service import LocationService
from app.services.weather_service import WeatherService
from app.services.monitoring_service import MonitoringService
from app.services.notification_service import NotificationService, connection_manager


def get_locations_repo() -> LocationsRepository:
    return LocationsRepository()


def get_observations_repo() -> ObservationsRepository:
    return ObservationsRepository()


def get_risk_assessments_repo() -> RiskAssessmentsRepository:
    return RiskAssessmentsRepository()


def get_incidents_repo() -> IncidentsRepository:
    return IncidentsRepository()


def get_incident_obs_repo() -> IncidentObservationsRepository:
    return IncidentObservationsRepository()


def get_simulations_repo() -> SimulationsRepository:
    return SimulationsRepository()


def get_location_service() -> LocationService:
    return LocationService(get_locations_repo())


def get_weather_service() -> WeatherService:
    return WeatherService(get_observations_repo(), get_risk_assessments_repo())


@lru_cache
def get_monitoring_service() -> MonitoringService:
    locations_repo = get_locations_repo()
    location_service = LocationService(locations_repo)
    weather_service = get_weather_service()
    return MonitoringService(
        get_incidents_repo(),
        get_incident_obs_repo(),
        locations_repo,
        weather_service,
        location_service,
    )


def get_notification_service() -> NotificationService:
    from app.services.notification_service import notification_service
    return notification_service