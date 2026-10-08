import aiosqlite
import pytest

from app.database import sqlite


@pytest.mark.asyncio
async def test_simulation_repository_round_trips_json(tmp_path, monkeypatch):
    monkeypatch.setattr(sqlite, "DB_PATH", str(tmp_path / "test.db"))
    await sqlite.init_sqlite()
    await sqlite.SQLiteLocationsRepository().upsert(
        {
            "locationId": "TEST-LOCATION",
            "country": "Test",
            "latitude": 0,
            "longitude": 0,
        }
    )
    repository = sqlite.SQLiteSimulationsRepository()
    simulation = {
        "simulationId": "SIM-TEST",
        "locationId": "TEST-LOCATION",
        "originalData": {"weather": {"temperature": 30}},
        "simulatedData": {"weather": {"temperature": 35}},
        "originalRisks": {"heat": 20},
        "simulatedRisks": {"heat": 40},
        "aiExplanation": {"summary": "Higher heat risk"},
    }

    await repository.save(simulation)
    stored = await repository.get_by_id("SIM-TEST")

    assert {key: stored[key] for key in simulation} == simulation


@pytest.mark.asyncio
async def test_sqlite_migrates_legacy_bedrock_column(tmp_path, monkeypatch):
    database_path = str(tmp_path / "legacy.db")
    monkeypatch.setattr(sqlite, "DB_PATH", database_path)
    async with aiosqlite.connect(database_path) as db:
        await db.execute(
            """
            CREATE TABLE simulation_runs (
                simulationId TEXT PRIMARY KEY,
                locationId TEXT NOT NULL,
                originalData TEXT NOT NULL,
                simulatedData TEXT NOT NULL,
                originalRisks TEXT NOT NULL,
                simulatedRisks TEXT NOT NULL,
                bedrockExplanation TEXT,
                createdAt TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await db.commit()

    await sqlite.init_sqlite()

    async with aiosqlite.connect(database_path) as db:
        cursor = await db.execute("PRAGMA table_info(simulation_runs)")
        columns = {row[1] for row in await cursor.fetchall()}
    assert "aiExplanation" in columns
    assert "bedrockExplanation" not in columns
