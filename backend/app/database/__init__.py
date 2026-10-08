from app.config import settings

if settings.use_local_dynamodb() or settings.is_development():
    from app.database.sqlite import (
        SQLiteLocationsRepository as LocationsRepository,
        SQLiteObservationsRepository as ObservationsRepository,
        SQLiteRiskAssessmentsRepository as RiskAssessmentsRepository,
        SQLiteIncidentsRepository as IncidentsRepository,
        SQLiteIncidentObservationsRepository as IncidentObservationsRepository,
        SQLiteSimulationsRepository as SimulationsRepository,
        init_sqlite,
        close_sqlite,
        get_db,
    )
else:
    from app.database.dynamodb import (
        LocationsRepository,
        ObservationsRepository,
        RiskAssessmentsRepository,
        IncidentsRepository,
        IncidentObservationsRepository,
        SimulationsRepository,
        init_dynamodb as init_sqlite,
        close_dynamodb as close_sqlite,
    )
    from app.database.dynamodb import get_db  # type: ignore

__all__ = [
    "LocationsRepository",
    "ObservationsRepository",
    "RiskAssessmentsRepository",
    "IncidentsRepository",
    "IncidentObservationsRepository",
    "SimulationsRepository",
    "init_sqlite",
    "close_sqlite",
    "get_db",
]