import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import structlog

from app.config import settings
from app.database import LocationsRepository
from app.database.models import Location, LocationCreate

logger = structlog.get_logger(__name__)


class LocationService:
    def __init__(self, locations_repo: LocationsRepository):
        self.locations_repo = locations_repo
        self._monitored_locations_cache: Optional[List[Location]] = None

    async def search_locations(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        local_results = await self.locations_repo.search_by_name(query, limit)
        results_by_id: Dict[str, Dict[str, Any]] = {}
        for location in local_results:
            location_id = location.get("locationId")
            if not location_id or location_id in results_by_id:
                continue
            if any(self._is_duplicate_location(location, existing) for existing in results_by_id.values()):
                continue
            results_by_id[location_id] = location

        if len(results_by_id) >= limit:
            return list(results_by_id.values())[:limit]

        try:
            external_results = await self._search_external(query, limit)
        except Exception as e:
            logger.warning("External location search failed", query=query, error=str(e))
            return list(results_by_id.values())[:limit]

        for result in external_results:
            location_id = result.get("locationId")
            if not location_id or location_id in results_by_id:
                continue
            if any(self._is_duplicate_location(result, existing) for existing in results_by_id.values()):
                continue

            await self.locations_repo.upsert(
                {
                    **result,
                    "monitoringEnabled": False,
                    "riskTypes": [],
                }
            )
            results_by_id[location_id] = result

        return list(results_by_id.values())[:limit]

    @classmethod
    def _is_duplicate_location(
        cls,
        candidate: Dict[str, Any],
        existing: Dict[str, Any],
    ) -> bool:
        candidate_id = candidate.get("locationId")
        if candidate_id and candidate_id == existing.get("locationId"):
            return True

        candidate_name = str(candidate.get("city") or candidate.get("district") or "").strip().casefold()
        existing_name = str(existing.get("city") or existing.get("district") or "").strip().casefold()
        if not candidate_name or candidate_name != existing_name:
            return False

        for field in ("state", "country"):
            candidate_value = str(candidate.get(field) or "").strip().casefold()
            existing_value = str(existing.get(field) or "").strip().casefold()
            if candidate_value != existing_value:
                return False

        try:
            distance_km = cls._haversine(
                float(candidate["latitude"]),
                float(candidate["longitude"]),
                float(existing["latitude"]),
                float(existing["longitude"]),
            )
        except (KeyError, TypeError, ValueError):
            return False

        return distance_km <= 5

    async def _search_external(self, query: str, limit: int) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": query,
                    "format": "json",
                    "limit": limit,
                    "addressdetails": 1,
                },
                headers={"User-Agent": f"ClimateOps/1.0 ({settings.OPENSTREETMAP_NOMINATIM_EMAIL})"},
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

        results = []
        for item in data:
            results.append({
                "locationId": f"OSM-{item['place_id']}",
                "country": item.get("address", {}).get("country", ""),
                "state": item.get("address", {}).get("state", ""),
                "district": item.get("address", {}).get("county", item.get("address", {}).get("district", "")),
                "city": item.get("address", {}).get("city", item.get("address", {}).get("town", item.get("address", {}).get("village", ""))),
                "latitude": float(item["lat"]),
                "longitude": float(item["lon"]),
                "source": "openstreetmap",
            })

        return results

    async def get_location(self, location_id: str) -> Optional[Location]:
        data = await self.locations_repo.get_by_id(location_id)
        return Location(**data) if data else None

    async def get_or_create_location(self, location_data: LocationCreate) -> Location:
        existing = await self.locations_repo.get_by_id(location_data.locationId)
        if existing:
            return Location(**existing)

        await self.locations_repo.upsert(location_data.model_dump())
        return location_data

    async def get_monitored_locations(self) -> List[Location]:
        if self._monitored_locations_cache is not None:
            return self._monitored_locations_cache

        config_path = Path(settings.MONITORED_LOCATIONS_CONFIG)
        if not config_path.is_absolute():
            config_path = Path(__file__).resolve().parents[2] / config_path
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)

            locations = []
            for loc_data in config.get("locations", []):
                location = Location(**loc_data)
                locations.append(location)
                await self.locations_repo.upsert(loc_data)

            self._monitored_locations_cache = locations
            return locations

        all_locations = await self.locations_repo.get_all()
        monitored = [Location(**loc) for loc in all_locations if loc.get("monitoringEnabled")]
        self._monitored_locations_cache = monitored
        return monitored

    async def refresh_monitored_locations(self) -> List[Location]:
        self._monitored_locations_cache = None
        return await self.get_monitored_locations()

    async def get_location_by_coords(self, lat: float, lon: float, radius_km: float = 50) -> Optional[Location]:
        all_locations = await self.locations_repo.get_all()
        for loc_data in all_locations:
            loc = Location(**loc_data)
            distance = self._haversine(lat, lon, loc.latitude, loc.longitude)
            if distance <= radius_km:
                return loc
        return None

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        from math import atan2, cos, radians, sin, sqrt
        R = 6371
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        return 2 * R * atan2(sqrt(a), sqrt(1 - a))