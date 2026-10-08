from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.database.models import EnvironmentalObservation, WeatherData, WaterData, AlertData


class BaseAdapter(ABC):
    @abstractmethod
    async def fetch_current(self, location_id: str, lat: float, lon: float) -> EnvironmentalObservation:
        pass

    @abstractmethod
    async def fetch_forecast(self, location_id: str, lat: float, lon: float, hours: int = 48) -> List[EnvironmentalObservation]:
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        pass


class MockAdapter(BaseAdapter):
    def __init__(self):
        self.source_name = "mock"

    async def fetch_current(self, location_id: str, lat: float, lon: float) -> EnvironmentalObservation:
        import random
        return EnvironmentalObservation(
            locationId=location_id,
            timestamp=datetime.utcnow(),
            weather=WeatherData(
                temperature=round(random.uniform(25, 42), 1),
                humidity=round(random.uniform(40, 90), 1),
                rainfall=round(random.uniform(0, 150), 1),
                windSpeed=round(random.uniform(5, 25), 1),
                pressure=round(random.uniform(990, 1020), 1),
            ),
            water=WaterData(
                riverLevel=round(random.uniform(5, 50), 1),
                riverLevelTrend=random.choice(["RISING", "FALLING", "STABLE"]),
            ),
            alerts=[],
            source=self.source_name,
            rawData={"mock": True},
        )

    async def fetch_forecast(self, location_id: str, lat: float, lon: float, hours: int = 48) -> List[EnvironmentalObservation]:
        return [await self.fetch_current(location_id, lat, lon) for _ in range(hours // 6)]

    def get_source_name(self) -> str:
        return self.source_name


class OpenWeatherAdapter(BaseAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.source_name = "openweather"

    async def fetch_current(self, location_id: str, lat: float, lon: float) -> EnvironmentalObservation:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/weather",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": self.api_key,
                    "units": "metric",
                },
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

        rain_data = data.get("rain", {})
        rainfall = rain_data.get("3h", rain_data.get("1h"))
        weather = WeatherData(
            temperature=data["main"]["temp"],
            humidity=data["main"]["humidity"],
            rainfall=rainfall,
            windSpeed=data["wind"]["speed"],
            pressure=data["main"]["pressure"],
        )

        alerts = []
        if "alerts" in data:
            for alert in data["alerts"]:
                alerts.append(AlertData(
                    type=alert.get("event", "UNKNOWN"),
                    severity=alert.get("severity", "UNKNOWN"),
                    description=alert.get("description", ""),
                    issuedAt=datetime.fromtimestamp(alert["start"]),
                    expiresAt=datetime.fromtimestamp(alert["end"]) if "end" in alert else None,
                ))

        return EnvironmentalObservation(
            locationId=location_id,
            timestamp=datetime.utcnow(),
            weather=weather,
            water=None,
            alerts=alerts,
            source=self.source_name,
            rawData=data,
        )

    async def fetch_forecast(self, location_id: str, lat: float, lon: float, hours: int = 48) -> List[EnvironmentalObservation]:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/forecast",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": self.api_key,
                    "units": "metric",
                },
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

        observations = []
        for item in data["list"][:hours // 3]:
            weather = WeatherData(
                temperature=item["main"]["temp"],
                humidity=item["main"]["humidity"],
                rainfall=item.get("rain", {}).get("3h", 0),
                windSpeed=item["wind"]["speed"],
                pressure=item["main"]["pressure"],
            )

            alerts = []
            if "alerts" in data:
                for alert in data["alerts"]:
                    alerts.append(AlertData(
                        type=alert.get("event", "UNKNOWN"),
                        severity=alert.get("severity", "UNKNOWN"),
                        description=alert.get("description", ""),
                        issuedAt=datetime.fromtimestamp(alert["start"]),
                        expiresAt=datetime.fromtimestamp(alert["end"]) if "end" in alert else None,
                    ))

            observations.append(EnvironmentalObservation(
                locationId=location_id,
                timestamp=datetime.fromtimestamp(item["dt"]),
                weather=weather,
                water=None,
                alerts=alerts,
                source=self.source_name,
                rawData=item,
            ))

        return observations

    def get_source_name(self) -> str:
        return self.source_name


class IMDAdapter(BaseAdapter):
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.source_name = "imd"

    async def fetch_current(self, location_id: str, lat: float, lon: float) -> EnvironmentalObservation:
        import httpx
        district_code = self._get_district_code(location_id)

        async with httpx.AsyncClient() as client:
            params = {"district": district_code} if district_code else {"lat": lat, "lon": lon}
            if self.api_key:
                params["api_key"] = self.api_key

            response = await client.get(
                f"{self.base_url}/current_weather",
                params=params,
                timeout=15.0,
            )
            response.raise_for_status()
            data = response.json()

        return self._normalize_current(data, location_id)

    async def fetch_district_rainfall(self, district_code: str) -> Dict[str, Any]:
        import httpx
        async with httpx.AsyncClient() as client:
            params = {"district": district_code}
            if self.api_key:
                params["api_key"] = self.api_key

            response = await client.get(
                f"{self.base_url}/district_rainfall",
                params=params,
                timeout=15.0,
            )
            response.raise_for_status()
            return response.json()

    async def fetch_district_warnings(self, district_code: str) -> List[AlertData]:
        import httpx
        async with httpx.AsyncClient() as client:
            params = {"district": district_code}
            if self.api_key:
                params["api_key"] = self.api_key

            response = await client.get(
                f"{self.base_url}/district_warnings",
                params=params,
                timeout=15.0,
            )
            response.raise_for_status()
            data = response.json()

            alerts = []
            for warning in data.get("warnings", []):
                alerts.append(AlertData(
                    type=warning.get("type", "WARNING"),
                    severity=warning.get("severity", "WARNING"),
                    description=warning.get("description", ""),
                    issuedAt=datetime.fromisoformat(warning["issued_at"].replace("Z", "+00:00")),
                    expiresAt=datetime.fromisoformat(warning["expires_at"].replace("Z", "+00:00")) if "expires_at" in warning else None,
                ))
            return alerts

    async def fetch_forecast(self, location_id: str, lat: float, lon: float, hours: int = 48) -> List[EnvironmentalObservation]:
        district_code = self._get_district_code(location_id)
        if not district_code:
            return []

        import httpx
        async with httpx.AsyncClient() as client:
            params = {"district": district_code}
            if self.api_key:
                params["api_key"] = self.api_key

            response = await client.get(
                f"{self.base_url}/forecast",
                params=params,
                timeout=15.0,
            )
            response.raise_for_status()
            data = response.json()

        observations = []
        for forecast in data.get("forecasts", [])[:hours // 3]:
            weather = WeatherData(
                temperature=forecast.get("temperature"),
                humidity=forecast.get("humidity"),
                rainfall=forecast.get("rainfall"),
                windSpeed=forecast.get("wind_speed"),
                pressure=forecast.get("pressure"),
            )

            alerts = await self.fetch_district_warnings(district_code)

            observations.append(EnvironmentalObservation(
                locationId=location_id,
                timestamp=datetime.fromisoformat(forecast["timestamp"].replace("Z", "+00:00")),
                weather=weather,
                water=None,
                alerts=alerts,
                source=self.source_name,
                rawData=forecast,
            ))

        return observations

    def _normalize_current(self, data: Dict[str, Any], location_id: str) -> EnvironmentalObservation:
        weather = WeatherData(
            temperature=data.get("temperature"),
            humidity=data.get("humidity"),
            rainfall=data.get("rainfall"),
            windSpeed=data.get("wind_speed"),
            pressure=data.get("pressure"),
        )

        water = None
        if data.get("river_level") is not None:
            water = WaterData(
                riverLevel=data["river_level"],
                riverLevelTrend=data.get("river_trend", "STABLE"),
            )

        alerts = []
        for alert in data.get("alerts", []):
            alerts.append(AlertData(
                type=alert.get("type", "ALERT"),
                severity=alert.get("severity", "INFO"),
                description=alert.get("description", ""),
                issuedAt=datetime.fromisoformat(alert["issued_at"].replace("Z", "+00:00")) if "issued_at" in alert else datetime.utcnow(),
                expiresAt=datetime.fromisoformat(alert["expires_at"].replace("Z", "+00:00")) if "expires_at" in alert else None,
            ))

        return EnvironmentalObservation(
            locationId=location_id,
            timestamp=datetime.utcnow(),
            weather=weather,
            water=water,
            alerts=alerts,
            source=self.source_name,
            rawData=data,
        )

    def _get_district_code(self, location_id: str) -> Optional[str]:
        if location_id.startswith("IN-"):
            parts = location_id.split("-")
            if len(parts) >= 3:
                return f"{parts[1]}-{parts[2]}"
        return None

    def get_source_name(self) -> str:
        return self.source_name


class CWCAdapter(BaseAdapter):
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.source_name = "cwc"

    async def fetch_current(self, location_id: str, lat: float, lon: float) -> EnvironmentalObservation:
        station_code = self._get_station_code(location_id)

        import httpx
        async with httpx.AsyncClient() as client:
            params = {"station": station_code} if station_code else {}
            if self.api_key:
                params["api_key"] = self.api_key

            response = await client.get(
                f"{self.base_url}/river_level",
                params=params,
                timeout=15.0,
            )
            response.raise_for_status()
            data = response.json()

        return self._normalize(data, location_id)

    async def fetch_forecast(self, location_id: str, lat: float, lon: float, hours: int = 48) -> List[EnvironmentalObservation]:
        return []

    def _normalize(self, data: Dict[str, Any], location_id: str) -> EnvironmentalObservation:
        water = None
        if data.get("level") is not None:
            water = WaterData(
                riverLevel=data["level"],
                riverLevelTrend=data.get("trend", "STABLE"),
            )

        return EnvironmentalObservation(
            locationId=location_id,
            timestamp=datetime.utcnow(),
            weather=None,
            water=water,
            alerts=[],
            source=self.source_name,
            rawData=data,
        )

    def _get_station_code(self, location_id: str) -> Optional[str]:
        return None

    def get_source_name(self) -> str:
        return self.source_name


def create_adapters(
    openweather_key: str,
    imd_base_url: str,
    imd_api_key: Optional[str] = None,
    cwc_base_url: Optional[str] = None,
    cwc_api_key: Optional[str] = None,
) -> Dict[str, BaseAdapter]:
    adapters = {}
    if openweather_key:
        adapters["openweather"] = OpenWeatherAdapter(openweather_key)
    if imd_base_url:
        adapters["imd"] = IMDAdapter(imd_base_url, imd_api_key)

    if cwc_base_url:
        adapters["cwc"] = CWCAdapter(cwc_base_url, cwc_api_key)

    adapters["mock"] = MockAdapter()

    return adapters