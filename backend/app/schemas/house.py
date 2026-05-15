from datetime import datetime
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, Field


def _dt_to_str(v: Any) -> str | None:
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.isoformat()
    return str(v)


def _safe_int(v: Any) -> int | None:
    if v is None:
        return None
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return None


def _safe_float(v: Any) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


DateTimeStr = Annotated[str | None, BeforeValidator(_dt_to_str)]
SafeInt = Annotated[int | None, BeforeValidator(_safe_int)]
SafeFloat = Annotated[float | None, BeforeValidator(_safe_float)]


class HouseBase(BaseModel):
    name: str
    place: str
    price: float = Field(gt=0)
    introduction: str | None = None
    room_count: SafeInt = None
    min_area: SafeFloat = None
    max_area: SafeFloat = None
    avg_area: SafeFloat = None
    property_type: str | None = None
    price_flag: str | None = None


class HouseCreate(HouseBase):
    pass


class HouseUpdate(BaseModel):
    name: str | None = None
    place: str | None = None
    price: float | None = Field(default=None, gt=0)
    introduction: str | None = None
    room_count: int | None = None
    min_area: float | None = None
    max_area: float | None = None
    avg_area: float | None = None
    property_type: str | None = None
    price_flag: str | None = None


class HouseOut(HouseBase):
    id: int
    created_at: DateTimeStr = None
    updated_at: DateTimeStr = None

    model_config = {"from_attributes": True}


class PaginatedHouses(BaseModel):
    items: list[HouseOut]
    total: int
    page: int
    page_size: int
    total_pages: int
