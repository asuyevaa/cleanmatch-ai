"""
Pydantic schemas: the shapes of data going in and out of the API.

Keeping these separate from the SQLAlchemy ORM model (housekeeper.py) is a
deliberate choice — it lets the API contract evolve independently of the
database table, and lets us validate input before it ever touches the DB.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class HousekeeperBase(BaseModel):
    name: str
    services: List[str] = Field(
        ..., description="e.g. ['deep_cleaning', 'ironing']"
    )
    experience_years: int = Field(..., ge=0)
    service_area: str
    price_per_hour: float = Field(..., gt=0)
    pet_friendly: bool = False
    availability: List[str] = Field(
        default_factory=list,
        description="Weekdays, e.g. ['Monday', 'Saturday']",
    )
    bio: Optional[str] = None
    cv_text: Optional[str] = None


class HousekeeperCreate(HousekeeperBase):
    pass


class HousekeeperUpdate(BaseModel):
    """All fields optional, so PUT can be used as a partial update too."""

    name: Optional[str] = None
    services: Optional[List[str]] = None
    experience_years: Optional[int] = Field(default=None, ge=0)
    service_area: Optional[str] = None
    price_per_hour: Optional[float] = Field(default=None, gt=0)
    pet_friendly: Optional[bool] = None
    availability: Optional[List[str]] = None
    bio: Optional[str] = None
    cv_text: Optional[str] = None


class HousekeeperOut(HousekeeperBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
