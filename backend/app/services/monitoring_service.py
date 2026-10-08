import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
from app.config import settings
from app.database import (
    IncidentsRepository,
    IncidentObservationsRepository,
    LocationsRepository,
)
from app.database.models import Incident, IncidentObservation
from app.services.weather_service import WeatherService
from app.services.location_service import LocationService
from app.core import (
    run_emergency_detection,
    create_incident,
    update_incident,
    check_incident_resolution,
    resolve_incident,
    assess_all_risks,
)
from app.core.groq import groq_client
from app.services.notification_service import notification_service

logger = structlog.get_logger(__name__)

class MonitoringService:
    def __init__(
        self,
        incidents_repo: IncidentsRepository,
        incident_obs_repo: IncidentObservationsRepository,
        locations_repo: LocationsRepository,
        weather_service: WeatherService,
        location_service: LocationService,
    ):
        self.incidents_repo = incidents_repo
        self.incident_obs_repo = incident_obs_repo
        self.locations_repo = locations_repo
        self.weather_service = weather_service
        self.location_service = location_service
        self._running = False
        self._task: Optional[asyncio.Task] = None

    @property
    def is_running(self) -> bool:
        return self._running and self._task is not None and not self._task.done()

    @property
    def interval_minutes(self) -> int:
        return settings.MONITORING_INTERVAL_MINUTES

    async def start_monitoring(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._monitoring_loop())
        logger.info("Monitoring service started", interval_minutes=self.interval_minutes)

    async def stop_monitoring(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Monitoring service stopped")

    async def _monitoring_loop(self) -> None:
        while self._running:
            try:
                await self._run_monitoring_cycle()
            except Exception as e:
                logger.exception("Monitoring cycle failed", error=str(e))

            if self._running:
                await asyncio.sleep(self.interval_minutes * 60)

    async def _run_monitoring_cycle(self) -> None:
        monitored_locations = await self.location_service.get_monitored_locations()
        active_incidents = [
            Incident(**incident) for incident in await self.incidents_repo.get_active()
        ]

        for location in monitored_locations:
            if not location.monitoringEnabled:
                continue

            await self._monitor_location(location, active_incidents)

    async def _monitor_location(
        self, location, active_incidents: List[Incident]
    ) -> Dict[str, Any]:
        try:
            observations = await self.weather_service.fetch_and_store_current(
                location.locationId,
                location.latitude,
                location.longitude,
                adapter_names=["openweather"],
            )

            if not observations:
                return {
                    "locations_checked": 1,
                    "incidents_created": 0,
                    "incidents_updated": 0,
                    "incidents_resolved": 0,
                    "error": "No environmental data was returned by the configured providers",
                }

            combined_obs = observations[0]
            risk_assessment = assess_all_risks(combined_obs)
            await notification_service.notify_risk_update(
                location.locationId, risk_assessment.model_dump(mode="json")
            )

            location_incidents = [inc for inc in active_incidents if inc.locationId == location.locationId]
            counts = {
                "locations_checked": 1,
                "incidents_created": 0,
                "incidents_updated": 0,
                "incidents_resolved": 0,
            }

            detections = run_emergency_detection(risk_assessment, combined_obs, location_incidents)

            for detection in detections:
                if detection.existing_incident_id:
                    existing = next((inc for inc in location_incidents if inc.incidentId == detection.existing_incident_id), None)
                    if existing:
                        updated = update_incident(existing, detection, risk_assessment, combined_obs)
                        await self.incidents_repo.upsert(updated.model_dump(mode="json"))
                        await self._add_incident_observation(updated, combined_obs, risk_assessment)
                        counts["incidents_updated"] += 1
                        await notification_service.notify_incident_updated(
                            updated.model_dump(mode="json")
                        )
                        await self._maybe_generate_ai_explanation(updated, risk_assessment, location)
                else:
                    new_incident = create_incident(detection, risk_assessment, combined_obs)
                    await self.incidents_repo.upsert(new_incident.model_dump(mode="json"))
                    await self._add_incident_observation(new_incident, combined_obs, risk_assessment)
                    counts["incidents_created"] += 1
                    await notification_service.notify_incident_created(
                        new_incident.model_dump(mode="json")
                    )
                    await self._maybe_generate_ai_explanation(new_incident, risk_assessment, location)

            for incident in location_incidents:
                if check_incident_resolution(incident, risk_assessment):
                    resolved = resolve_incident(incident)
                    await self.incidents_repo.upsert(resolved.model_dump(mode="json"))
                    counts["incidents_resolved"] += 1
                    await notification_service.notify_incident_resolved(
                        resolved.incidentId, resolved.model_dump(mode="json")
                    )

            if any(counts[key] for key in ("incidents_created", "incidents_updated", "incidents_resolved")):
                await notification_service.notify_summary_update(
                    await self.get_active_incidents_summary()
                )
            return counts
        except Exception as e:
            logger.exception(
                "Monitoring failed for location",
                location_id=location.locationId,
                error=str(e),
            )
            return {
                "locations_checked": 1,
                "incidents_created": 0,
                "incidents_updated": 0,
                "incidents_resolved": 0,
                "error": str(e),
            }

    async def _add_incident_observation(
        self,
        incident: Incident,
        observation,
        risk_assessment,
    ) -> None:
        risk_map = {
            "HEAT": risk_assessment.heatRisk,
            "FLOOD": risk_assessment.floodRisk,
            "HEAVY_RAIN": risk_assessment.floodRisk,
            "WATER_STRESS": risk_assessment.waterStressRisk,
            "DROUGHT": risk_assessment.droughtRisk,
        }

        obs = IncidentObservation(
            incidentId=incident.incidentId,
            timestamp=datetime.utcnow(),
            rainfall=observation.weather.rainfall if observation.weather else None,
            temperature=observation.weather.temperature if observation.weather else None,
            riverLevel=observation.water.riverLevel if observation.water else None,
            riskScore=risk_map.get(incident.type.value, 0),
            severity=incident.severity,
            source=observation.source,
        )

        await self.incident_obs_repo.add_observation(obs.model_dump(mode="json"))

    async def _maybe_generate_ai_explanation(
        self,
        incident: Incident,
        risk_assessment,
        location,
    ) -> None:
        if settings.GROQ_API_KEY and incident.riskScore >= 80:
            try:
                explanation = await groq_client.explain_incident(
                    incident,
                    risk_assessment,
                    location.city or location.district or location.state,
                )
                if explanation:
                    incident.aiExplanation = explanation
                    await self.incidents_repo.upsert(incident.model_dump(mode="json"))
                    await notification_service.notify_incident_updated(
                        incident.model_dump(mode="json")
                    )
            except Exception as e:
                logger.warning(
                    "Failed to generate incident explanation",
                    incident_id=incident.incidentId,
                    error=str(e),
                )

    async def trigger_monitoring_now(self) -> Dict[str, Any]:
        monitored_locations = await self.location_service.get_monitored_locations()
        active_incidents = [
            Incident(**incident) for incident in await self.incidents_repo.get_active()
        ]

        results: Dict[str, Any] = {
            "locations_checked": 0,
            "incidents_created": 0,
            "incidents_updated": 0,
            "incidents_resolved": 0,
            "errors": [],
        }

        for location in monitored_locations:
            if not location.monitoringEnabled:
                continue

            location_result = await self._monitor_location(location, active_incidents)
            for key in (
                "locations_checked",
                "incidents_created",
                "incidents_updated",
                "incidents_resolved",
            ):
                results[key] += location_result[key]
            if location_result.get("error"):
                results.setdefault("errors", []).append(
                    {"locationId": location.locationId, "message": location_result["error"]}
                )

        if not results["errors"]:
            results.pop("errors")
        return results

    async def get_incident_timeline(self, incident_id: str) -> List[Dict[str, Any]]:
        return await self.incident_obs_repo.get_timeline(incident_id)

    async def get_active_incidents_summary(self) -> Dict[str, Any]:
        active = [
            Incident(**incident) for incident in await self.incidents_repo.get_active()
        ]

        summary = {
            "total": len(active),
            "by_type": {},
            "by_severity": {},
            "by_status": {},
            "critical_count": 0,
            "high_risk_count": 0,
        }

        for inc in active:
            inc_type = inc.type.value
            severity = inc.severity.value
            status = inc.status.value

            summary["by_type"][inc_type] = summary["by_type"].get(inc_type, 0) + 1
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
            summary["by_status"][status] = summary["by_status"].get(status, 0) + 1

            if inc.riskScore >= 80:
                summary["critical_count"] += 1
            elif inc.riskScore >= 60:
                summary["high_risk_count"] += 1

        return summary