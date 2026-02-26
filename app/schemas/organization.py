"""Organization schemas used in this project."""
from pydantic import BaseModel, ConfigDict
from typing import List

from app.schemas.building import BuildingResponse
from app.schemas.activity import ActivityResponse


class OrganizationResponse(BaseModel):
    """Full organization for get-by-id."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    building_id: int
    building: BuildingResponse | None = None
    activities: List[ActivityResponse] = []
    phone_numbers: List[str] = []


class OrganizationList(BaseModel):
    """Lightweight org for list endpoints (lists/search)."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    building_name: str
    phone_numbers: List[str] = []
    activity_names: List[str] = []
