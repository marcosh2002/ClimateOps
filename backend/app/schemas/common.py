from typing import List, Any, Optional
from pydantic import BaseModel, ConfigDict


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    pageSize: int
    hasMore: bool


class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str