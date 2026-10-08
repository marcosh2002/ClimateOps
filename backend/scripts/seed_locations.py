import asyncio
import json
from pathlib import Path
from app.config import settings
from app.database import LocationsRepository
from app.database.models import LocationCreate


INDIAN_LOCATIONS = [
    {
        "locationId": "IN-AS-GUW",
        "country": "India",
        "state": "Assam",
        "district": "Kamrup Metropolitan",
        "city": "Guwahati",
        "latitude": 26.1445,
        "longitude": 91.7362,
        "monitoringEnabled": True,
        "riskTypes": ["FLOOD", "HEAVY_RAIN", "WATER_STRESS"],
    },
    {
        "locationId": "IN-RJ-JAI",
        "country": "India",
        "state": "Rajasthan",
        "district": "Jaipur",
        "city": "Jaipur",
        "latitude": 26.9124,
        "longitude": 75.7873,
        "monitoringEnabled": True,
        "riskTypes": ["HEAT", "DROUGHT", "WATER_STRESS"],
    },
    {
        "locationId": "IN-MH-MUM",
        "country": "India",
        "state": "Maharashtra",
        "district": "Mumbai City",
        "city": "Mumbai",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "monitoringEnabled": True,
        "riskTypes": ["FLOOD", "HEAVY_RAIN", "HEAT"],
    },
    {
        "locationId": "IN-DL-DEL",
        "country": "India",
        "state": "Delhi",
        "district": "New Delhi",
        "city": "New Delhi",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "monitoringEnabled": True,
        "riskTypes": ["HEAT", "WATER_STRESS", "DROUGHT"],
    },
    {
        "locationId": "IN-WB-KOL",
        "country": "India",
        "state": "West Bengal",
        "district": "Kolkata",
        "city": "Kolkata",
        "latitude": 22.5726,
        "longitude": 88.3639,
        "monitoringEnabled": True,
        "riskTypes": ["FLOOD", "HEAVY_RAIN", "HEAT", "WATER_STRESS"],
    },
    {
        "locationId": "IN-TN-CHE",
        "country": "India",
        "state": "Tamil Nadu",
        "district": "Chennai",
        "city": "Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "monitoringEnabled": True,
        "riskTypes": ["HEAT", "WATER_STRESS", "DROUGHT", "FLOOD"],
    },
    {
        "locationId": "IN-KA-BLR",
        "country": "India",
        "state": "Karnataka",
        "district": "Bangalore Urban",
        "city": "Bengaluru",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "monitoringEnabled": True,
        "riskTypes": ["WATER_STRESS", "DROUGHT", "HEAT"],
    },
    {
        "locationId": "IN-UP-LKO",
        "country": "India",
        "state": "Uttar Pradesh",
        "district": "Lucknow",
        "city": "Lucknow",
        "latitude": 26.8467,
        "longitude": 80.9462,
        "monitoringEnabled": True,
        "riskTypes": ["HEAT", "FLOOD", "WATER_STRESS"],
    },
    {
        "locationId": "IN-BR-PAT",
        "country": "India",
        "state": "Bihar",
        "district": "Patna",
        "city": "Patna",
        "latitude": 25.5941,
        "longitude": 85.1376,
        "monitoringEnabled": True,
        "riskTypes": ["FLOOD", "HEAVY_RAIN", "HEAT"],
    },
    {
        "locationId": "IN-GJ-AHM",
        "country": "India",
        "state": "Gujarat",
        "district": "Ahmedabad",
        "city": "Ahmedabad",
        "latitude": 23.0225,
        "longitude": 72.5714,
        "monitoringEnabled": True,
        "riskTypes": ["HEAT", "DROUGHT", "WATER_STRESS"],
    },
    {
        "locationId": "IN-OR-BHU",
        "country": "India",
        "state": "Odisha",
        "district": "Khordha",
        "city": "Bhubaneswar",
        "latitude": 20.2961,
        "longitude": 85.8245,
        "monitoringEnabled": True,
        "riskTypes": ["HEAT", "FLOOD", "HEAVY_RAIN"],
    },
    {
        "locationId": "IN-KL-KOC",
        "country": "India",
        "state": "Kerala",
        "district": "Ernakulam",
        "city": "Kochi",
        "latitude": 9.9312,
        "longitude": 76.2673,
        "monitoringEnabled": True,
        "riskTypes": ["FLOOD", "HEAVY_RAIN", "HEAT", "WATER_STRESS"],
    },
    {
        "locationId": "IN-PB-AMR",
        "country": "India",
        "state": "Punjab",
        "district": "Amritsar",
        "city": "Amritsar",
        "latitude": 31.6340,
        "longitude": 74.8723,
        "monitoringEnabled": True,
        "riskTypes": ["HEAT", "WATER_STRESS", "DROUGHT"],
    },
    {
        "locationId": "IN-HR-GUR",
        "country": "India",
        "state": "Haryana",
        "district": "Gurugram",
        "city": "Gurugram",
        "latitude": 28.4595,
        "longitude": 77.0266,
        "monitoringEnabled": True,
        "riskTypes": ["HEAT", "WATER_STRESS", "DROUGHT"],
    },
    {
        "locationId": "IN-MP-BHO",
        "country": "India",
        "state": "Madhya Pradesh",
        "district": "Bhopal",
        "city": "Bhopal",
        "latitude": 23.2599,
        "longitude": 77.4126,
        "monitoringEnabled": True,
        "riskTypes": ["HEAT", "DROUGHT", "WATER_STRESS"],
    },
]


async def seed_locations():
    repo = LocationsRepository()
    print(f"Seeding {len(INDIAN_LOCATIONS)} monitored locations...")

    for loc_data in INDIAN_LOCATIONS:
        location = LocationCreate(**loc_data)
        await repo.upsert(location.model_dump())
        print(f"  ✓ {location.city}, {location.state} ({location.locationId})")

    print("Seeding complete!")


async def main():
    await seed_locations()


if __name__ == "__main__":
    asyncio.run(main())