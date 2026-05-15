import csv
from io import StringIO

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user
from app.database import get_db
from app.models.user import User
from app.schemas.common import ImportResponse
from app.services.house_service import HouseService

router = APIRouter(prefix="/api/import", tags=["import"])

CSV_COLUMN_MAP = {
    "House name": "name",
    "House place": "place",
    "House price": "price",
    "House introduction": "introduction",
    "room_count": "room_count",
    "min_area": "min_area",
    "max_area": "max_area",
    "avg_area": "avg_area",
    "property_type": "property_type",
    "price_flag": "price_flag",
}


def _detect_encoding(content: bytes) -> str:
    for enc in ["utf-8-sig", "utf-8", "gbk", "gb18030"]:
        try:
            content.decode(enc)
            return enc
        except (UnicodeDecodeError, LookupError):
            continue
    return "utf-8"


@router.post("/csv", response_model=ImportResponse)
def import_csv(
    file: UploadFile,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload a CSV file",
        )

    content = file.file.read()
    encoding = _detect_encoding(content)
    text = content.decode(encoding)

    df = pd.read_csv(StringIO(text))
    df = df.drop_duplicates()

    df = df.rename(columns=CSV_COLUMN_MAP)
    keep_cols = [v for v in CSV_COLUMN_MAP.values() if v in df.columns]
    df = df[keep_cols]

    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df = df.dropna(subset=["price"])

    records = df.to_dict(orient="records")
    result = HouseService(db).bulk_import(records)
    return result
