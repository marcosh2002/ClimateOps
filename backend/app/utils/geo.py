from math import radians, sin, cos, sqrt, atan2
from typing import Tuple, List, Dict, Any


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))


def find_nearest_location(
    lat: float,
    lon: float,
    locations: List[Dict[str, Any]],
    max_distance_km: float = 100,
) -> Dict[str, Any]:
    nearest = None
    min_distance = float("inf")

    for loc in locations:
        distance = haversine_distance(lat, lon, loc["latitude"], loc["longitude"])
        if distance < min_distance and distance <= max_distance_km:
            min_distance = distance
            nearest = {**loc, "distance_km": distance}

    return nearest


def bbox_contains(lat: float, lon: float, bbox: Tuple[float, float, float, float]) -> bool:
    min_lat, min_lon, max_lat, max_lon = bbox
    return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon


def calculate_bounding_box(lat: float, lon: float, radius_km: float) -> Tuple[float, float, float, float]:
    lat_delta = radius_km / 111.0
    lon_delta = radius_km / (111.0 * cos(radians(lat)))
    return (
        lat - lat_delta,
        lon - lon_delta,
        lat + lat_delta,
        lon + lon_delta,
    )


def format_coordinates(lat: float, lon: float, precision: int = 4) -> str:
    lat_dir = "N" if lat >= 0 else "S"
    lon_dir = "E" if lon >= 0 else "W"
    return f"{abs(lat):.{precision}f}°{lat_dir}, {abs(lon):.{precision}f}°{lon_dir}"