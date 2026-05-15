from math import ceil

from sqlalchemy.orm import Session

from app.models.house import House
from app.schemas.house import HouseCreate, HouseUpdate


class HouseService:
    def __init__(self, db: Session):
        self.db = db

    def list_houses(
        self,
        page: int = 1,
        page_size: int = 20,
        region: str | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        property_type: str | None = None,
        sort_by: str = "price",
        sort_order: str = "asc",
        search: str | None = None,
    ) -> dict:
        query = self.db.query(House)

        if region:
            query = query.filter(House.place == region)
        if price_min is not None:
            query = query.filter(House.price >= price_min)
        if price_max is not None:
            query = query.filter(House.price <= price_max)
        if property_type:
            query = query.filter(House.property_type == property_type)
        if search:
            query = query.filter(House.name.contains(search))

        sort_column = getattr(House, sort_by, House.price)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        total = query.count()
        total_pages = max(1, ceil(total / page_size))
        items = query.offset((page - 1) * page_size).limit(page_size).all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    def get_house(self, house_id: int) -> House | None:
        return self.db.query(House).filter(House.id == house_id).first()

    def create_house(self, data: HouseCreate) -> House:
        house = House(**data.model_dump())
        self.db.add(house)
        self.db.commit()
        self.db.refresh(house)
        return house

    def update_house(self, house_id: int, data: HouseUpdate) -> House | None:
        house = self.get_house(house_id)
        if not house:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(house, key, value)
        self.db.commit()
        self.db.refresh(house)
        return house

    def delete_house(self, house_id: int) -> bool:
        house = self.get_house(house_id)
        if not house:
            return False
        self.db.delete(house)
        self.db.commit()
        return True

    def bulk_import(self, records: list[dict]) -> dict:
        imported = 0
        skipped = 0
        errors: list[str] = []
        for i, record in enumerate(records):
            try:
                house = House(**record)
                self.db.add(house)
                imported += 1
            except Exception as e:
                skipped += 1
                errors.append(f"Row {i + 1}: {str(e)}")
        self.db.commit()
        return {"imported": imported, "skipped": skipped, "errors": errors}
