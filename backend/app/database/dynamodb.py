from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from boto3.dynamodb.conditions import Attr, Key

import aioboto3
from botocore.exceptions import ClientError

from app.config import settings


class DynamoDBClient:
    def __init__(self):
        self.session = aioboto3.Session()
        self._resource = None
        self._client = None

    async def get_resource(self):
        if self._resource is None:
            self._resource = await self.session.resource(
                "dynamodb",
                region_name=settings.AWS_REGION,
                endpoint_url=settings.AWS_DYNAMODB_ENDPOINT,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            ).__aenter__()
        return self._resource

    async def get_client(self):
        if self._client is None:
            self._client = await self.session.client(
                "dynamodb",
                region_name=settings.AWS_REGION,
                endpoint_url=settings.AWS_DYNAMODB_ENDPOINT,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            ).__aenter__()
        return self._client

    async def close(self):
        if self._resource:
            await self._resource.__aexit__(None, None, None)
        if self._client:
            await self._client.__aexit__(None, None, None)


dynamodb_client = DynamoDBClient()


TABLE_NAMES = {
    "locations": "climatify-locations",
    "observations": "climatify-observations",
    "risk_assessments": "climatify-risk-assessments",
    "incidents": "climatify-incidents",
    "incident_observations": "climatify-incident-observations",
    "simulations": "climatify-simulations",
}


def _to_dynamodb(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _to_dynamodb(item) for key, item in value.items() if item is not None}
    if isinstance(value, (list, tuple)):
        return [_to_dynamodb(item) for item in value]
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "model_dump"):
        return _to_dynamodb(value.model_dump(mode="json"))
    return value


def _from_dynamodb(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _from_dynamodb(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_from_dynamodb(item) for item in value]
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    return value


async def init_dynamodb() -> None:
    client = await dynamodb_client.get_client()

    existing_tables = await client.list_tables()
    existing_table_names = set(existing_tables.get("TableNames", []))

    for logical_name, physical_name in TABLE_NAMES.items():
        if physical_name not in existing_table_names:
            await _create_table(client, logical_name, physical_name)
        else:
            print(f"Table {physical_name} already exists")

    print("DynamoDB initialization complete")


async def _create_table(client, logical_name: str, physical_name: str) -> None:
    table_configs = {
        "locations": {
            "KeySchema": [{"AttributeName": "locationId", "KeyType": "HASH"}],
            "AttributeDefinitions": [{"AttributeName": "locationId", "AttributeType": "S"}],
        },
        "observations": {
            "KeySchema": [
                {"AttributeName": "locationId", "KeyType": "HASH"},
                {"AttributeName": "timestamp", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "locationId", "AttributeType": "S"},
                {"AttributeName": "timestamp", "AttributeType": "S"},
            ],
        },
        "risk_assessments": {
            "KeySchema": [
                {"AttributeName": "locationId", "KeyType": "HASH"},
                {"AttributeName": "timestamp", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "locationId", "AttributeType": "S"},
                {"AttributeName": "timestamp", "AttributeType": "S"},
            ],
        },
        "incidents": {
            "KeySchema": [{"AttributeName": "incidentId", "KeyType": "HASH"}],
            "AttributeDefinitions": [{"AttributeName": "incidentId", "AttributeType": "S"}],
        },
        "incident_observations": {
            "KeySchema": [
                {"AttributeName": "incidentId", "KeyType": "HASH"},
                {"AttributeName": "timestamp", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "incidentId", "AttributeType": "S"},
                {"AttributeName": "timestamp", "AttributeType": "S"},
            ],
        },
        "simulations": {
            "KeySchema": [{"AttributeName": "simulationId", "KeyType": "HASH"}],
            "AttributeDefinitions": [{"AttributeName": "simulationId", "AttributeType": "S"}],
        },
    }

    config = table_configs.get(logical_name)
    if not config:
        raise ValueError(f"Unknown table: {logical_name}")

    await client.create_table(
        TableName=physical_name,
        KeySchema=config["KeySchema"],
        AttributeDefinitions=config["AttributeDefinitions"],
        BillingMode="PAY_PER_REQUEST",
    )

    waiter = client.get_waiter("table_exists")
    await waiter.wait(TableName=physical_name)
    print(f"Created table: {physical_name}")


async def close_dynamodb() -> None:
    await dynamodb_client.close()


class BaseRepository:
    def __init__(self, table_name: str):
        self.table_name = TABLE_NAMES[table_name]

    async def _get_table(self):
        resource = await dynamodb_client.get_resource()
        return await resource.Table(self.table_name)

    async def put_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        table = await self._get_table()
        await table.put_item(Item=_to_dynamodb(item))
        return item

    async def get_item(self, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        table = await self._get_table()
        response = await table.get_item(Key=key)
        item = response.get("Item")
        return _from_dynamodb(item) if item else None

    async def query(
        self,
        key_condition_expression: Any,
        scan_index_forward: bool = True,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        table = await self._get_table()
        items: List[Dict[str, Any]] = []
        last_key = None
        while True:
            kwargs = {
                "KeyConditionExpression": key_condition_expression,
                "ScanIndexForward": scan_index_forward,
            }
            if last_key:
                kwargs["ExclusiveStartKey"] = last_key
            if limit:
                kwargs["Limit"] = limit - len(items)
            response = await table.query(**kwargs)
            items.extend(response.get("Items", []))
            last_key = response.get("LastEvaluatedKey")
            if not last_key or (limit and len(items) >= limit):
                break
        return _from_dynamodb(items)

    async def scan(
        self,
        filter_expression: Any = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        table = await self._get_table()
        items: List[Dict[str, Any]] = []
        last_key = None
        while True:
            kwargs = {}
            if filter_expression is not None:
                kwargs["FilterExpression"] = filter_expression
            if last_key:
                kwargs["ExclusiveStartKey"] = last_key
            if limit:
                kwargs["Limit"] = limit - len(items)
            response = await table.scan(**kwargs)
            items.extend(response.get("Items", []))
            last_key = response.get("LastEvaluatedKey")
            if not last_key or (limit and len(items) >= limit):
                break
        return _from_dynamodb(items)

    async def update_item(
        self,
        key: Dict[str, Any],
        update_expression: str,
        expression_attribute_values: Dict[str, Any],
        expression_attribute_names: Optional[Dict[str, str]] = None,
        return_values: str = "ALL_NEW",
    ) -> Optional[Dict[str, Any]]:
        table = await self._get_table()
        kwargs = {
            "Key": key,
            "UpdateExpression": update_expression,
            "ExpressionAttributeValues": _to_dynamodb(expression_attribute_values),
            "ReturnValues": return_values,
        }
        if expression_attribute_names:
            kwargs["ExpressionAttributeNames"] = expression_attribute_names

        try:
            response = await table.update_item(**kwargs)
            return _from_dynamodb(response.get("Attributes"))
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                return None
            raise

    async def delete_item(self, key: Dict[str, Any]) -> bool:
        table = await self._get_table()
        await table.delete_item(Key=key)
        return True


class LocationsRepository(BaseRepository):
    def __init__(self):
        super().__init__("locations")

    async def get_by_id(self, location_id: str) -> Optional[Dict[str, Any]]:
        return await self.get_item({"locationId": location_id})

    async def upsert(self, location: Dict[str, Any]) -> Dict[str, Any]:
        return await self.put_item(location)

    async def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        return await self.scan(limit=limit)

    async def search_by_name(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        normalized_query = query.casefold()
        locations = await self.scan()
        matches = [
            location
            for location in locations
            if any(
                normalized_query in str(location.get(field) or "").casefold()
                for field in ("city", "district", "state")
            )
        ]
        return matches[:limit]


class ObservationsRepository(BaseRepository):
    def __init__(self):
        super().__init__("observations")

    async def get_latest(self, location_id: str) -> Optional[Dict[str, Any]]:
        items = await self.query(
            key_condition_expression=Key("locationId").eq(location_id),
            scan_index_forward=False,
            limit=1,
        )
        return items[0] if items else None

    async def get_history(self, location_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        from datetime import datetime, timedelta
        cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        return await self.query(
            key_condition_expression=Key("locationId").eq(location_id)
            & Key("timestamp").gte(cutoff),
            scan_index_forward=False,
        )


class RiskAssessmentsRepository(BaseRepository):
    def __init__(self):
        super().__init__("risk_assessments")

    async def get_latest(self, location_id: str) -> Optional[Dict[str, Any]]:
        items = await self.query(
            key_condition_expression=Key("locationId").eq(location_id),
            scan_index_forward=False,
            limit=1,
        )
        return items[0] if items else None

    async def save(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        return await self.put_item(assessment)


class IncidentsRepository(BaseRepository):
    def __init__(self):
        super().__init__("incidents")

    async def upsert(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        return await self.put_item(incident)

    async def get_active(self) -> List[Dict[str, Any]]:
        return await self.scan(
            filter_expression=Attr("status").is_in(
                ["ACTIVE", "WARNING", "CRITICAL", "EXTREME", "RECOVERY"]
            )
        )

    async def get_by_id(self, incident_id: str) -> Optional[Dict[str, Any]]:
        return await self.get_item({"incidentId": incident_id})

    async def get_by_location(self, location_id: str) -> List[Dict[str, Any]]:
        return await self.scan(
            filter_expression=Attr("locationId").eq(location_id)
        )


class IncidentObservationsRepository(BaseRepository):
    def __init__(self):
        super().__init__("incident_observations")

    async def get_timeline(self, incident_id: str) -> List[Dict[str, Any]]:
        return await self.query(
            key_condition_expression=Key("incidentId").eq(incident_id),
            scan_index_forward=True,
        )

    async def add_observation(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        return await self.put_item(observation)


class SimulationsRepository(BaseRepository):
    def __init__(self):
        super().__init__("simulations")

    async def get_by_id(self, simulation_id: str) -> Optional[Dict[str, Any]]:
        simulation = await self.get_item({"simulationId": simulation_id})
        if simulation and "bedrockExplanation" in simulation and "aiExplanation" not in simulation:
            simulation["aiExplanation"] = simulation.pop("bedrockExplanation")
        return simulation

    async def save(self, simulation: Dict[str, Any]) -> Dict[str, Any]:
        return await self.put_item(simulation)