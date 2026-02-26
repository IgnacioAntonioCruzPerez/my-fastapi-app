"""Activity schemas (tree, max 3 levels)."""
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional


class ActivityBase(BaseModel):
    name: str
    parent_id: Optional[int] = None
    level: int  # 1, 2, or 3

    @field_validator("level")
    @classmethod
    def level_must_be_1_to_3(cls, v: int) -> int:
        if v not in (1, 2, 3):
            raise ValueError("Activity level must be 1, 2, or 3")
        return v


class ActivityCreate(ActivityBase):
    pass


class ActivityResponse(ActivityBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ActivityTree(ActivityResponse):
    """Activity with nested children (for tree display)."""
    children: list["ActivityTree"] = []


ActivityTree.model_rebuild()
