from pydantic import BaseModel


class RegionStat(BaseModel):
    place: str
    count: int
    mean_price: float
    median_price: float
    min_price: float
    max_price: float
    avg_area: float


class RegionStatsResponse(BaseModel):
    regions: list[RegionStat]


class OverviewStats(BaseModel):
    total_houses: int
    total_regions: int
    global_mean: float
    global_median: float
    global_min: float
    global_max: float
    price_std: float
    type_distribution: dict[str, int]
    avg_area_overall: float
