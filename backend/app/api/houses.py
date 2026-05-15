from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.common import DeleteResponse
from app.schemas.house import HouseCreate, HouseOut, HouseUpdate, PaginatedHouses
from app.services.house_service import HouseService

router = APIRouter(prefix="/api/houses", tags=["houses"])


@router.get("", response_model=PaginatedHouses)
def list_houses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=10000),
    region: str | None = None,
    price_min: float | None = None,
    price_max: float | None = None,
    property_type: str | None = None,
    sort_by: str = Query("price", pattern="^(name|place|price|avg_area|property_type|created_at)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    search: str | None = None,
    db: Session = Depends(get_db),
):
    return HouseService(db).list_houses(
        page=page, page_size=page_size, region=region,
        price_min=price_min, price_max=price_max,
        property_type=property_type, sort_by=sort_by,
        sort_order=sort_order, search=search,
    )


@router.get("/{house_id}", response_model=HouseOut)
def get_house(house_id: int, db: Session = Depends(get_db)):
    house = HouseService(db).get_house(house_id)
    if not house:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="House not found")
    return house


@router.post("", response_model=HouseOut, status_code=status.HTTP_201_CREATED)
def create_house(
    data: HouseCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    return HouseService(db).create_house(data)


@router.put("/{house_id}", response_model=HouseOut)
def update_house(
    house_id: int,
    data: HouseUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    house = HouseService(db).update_house(house_id, data)
    if not house:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="House not found")
    return house


@router.delete("/{house_id}", response_model=DeleteResponse)
def delete_house(
    house_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    success = HouseService(db).delete_house(house_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="House not found")
    return {"message": "House deleted successfully"}
