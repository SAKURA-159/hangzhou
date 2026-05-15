from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.house import House


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
    return sorted_vals[mid]


class StatsService:
    def __init__(self, db: Session):
        self.db = db

    def _apply_filters(self, query, regions=None, price_min=None, price_max=None, property_type=None):
        if regions:
            query = query.filter(House.place.in_(regions))
        if price_min is not None:
            query = query.filter(House.price >= price_min)
        if price_max is not None:
            query = query.filter(House.price <= price_max)
        if property_type:
            query = query.filter(House.property_type == property_type)
        return query

    def get_region_stats(
        self,
        regions: list[str] | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        property_type: str | None = None,
    ) -> list[dict]:
        query = self.db.query(House)
        query = self._apply_filters(query, regions, price_min, price_max, property_type)

        houses = query.all()
        grouped: dict[str, list[House]] = {}
        for h in houses:
            grouped.setdefault(h.place, []).append(h)

        result = []
        for place, group in grouped.items():
            prices = [h.price for h in group]
            areas = [h.avg_area for h in group if h.avg_area is not None]
            result.append({
                "place": place,
                "count": len(group),
                "mean_price": round(sum(prices) / len(prices), 2) if prices else 0,
                "median_price": round(_median(prices), 2),
                "min_price": round(min(prices), 2),
                "max_price": round(max(prices), 2),
                "avg_area": round(sum(areas) / len(areas), 2) if areas else 0,
            })

        result.sort(key=lambda x: x["median_price"], reverse=True)
        return result

    def get_overview_stats(
        self,
        regions: list[str] | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        property_type: str | None = None,
    ) -> dict:
        query = self.db.query(House)
        query = self._apply_filters(query, regions, price_min, price_max, property_type)

        houses = query.all()
        prices = [h.price for h in houses]
        areas = [h.avg_area for h in houses if h.avg_area is not None]

        type_dist: dict[str, int] = {}
        for h in houses:
            if h.property_type:
                type_dist[h.property_type] = type_dist.get(h.property_type, 0) + 1

        regions_set = set(h.place for h in houses)

        if not prices:
            return {
                "total_houses": 0, "total_regions": 0,
                "global_mean": 0, "global_median": 0, "global_min": 0,
                "global_max": 0, "price_std": 0,
                "type_distribution": {}, "avg_area_overall": 0,
            }

        mean = sum(prices) / len(prices)
        variance = sum((p - mean) ** 2 for p in prices) / len(prices)

        return {
            "total_houses": len(houses),
            "total_regions": len(regions_set),
            "global_mean": round(mean, 2),
            "global_median": round(_median(prices), 2),
            "global_min": round(min(prices), 2),
            "global_max": round(max(prices), 2),
            "price_std": round(variance ** 0.5, 2),
            "type_distribution": type_dist,
            "avg_area_overall": round(sum(areas) / len(areas), 2) if areas else 0,
        }
