from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.stats import OverviewStats, RegionStatsResponse
from app.services.stats_service import StatsService

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/regions", response_model=RegionStatsResponse)
def region_stats(
    regions: str | None = Query(None, description="Comma-separated region names"),
    price_min: float | None = None,
    price_max: float | None = None,
    property_type: str | None = None,
    db: Session = Depends(get_db),
):
    region_list = [r.strip() for r in regions.split(",")] if regions else None
    result = StatsService(db).get_region_stats(
        regions=region_list, price_min=price_min,
        price_max=price_max, property_type=property_type,
    )
    return {"regions": result}


@router.get("/overview", response_model=OverviewStats)
def overview_stats(
    regions: str | None = Query(None, description="Comma-separated region names"),
    price_min: float | None = None,
    price_max: float | None = None,
    property_type: str | None = None,
    db: Session = Depends(get_db),
):
    region_list = [r.strip() for r in regions.split(",")] if regions else None
    return StatsService(db).get_overview_stats(
        regions=region_list, price_min=price_min,
        price_max=price_max, property_type=property_type,
    )
