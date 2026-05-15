"""Seed the database with CSV data from the data/ directory."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from app.database import Base, SessionLocal, engine
from app.models.house import House

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


def load_csv(path: Path) -> pd.DataFrame:
    for enc in ["utf-8-sig", "utf-8", "gbk", "gb18030"]:
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Cannot decode {path}")


def main():
    project_root = Path(__file__).resolve().parent.parent.parent
    data_dir = project_root / "data"

    cleaned_path = data_dir / "hangzhou_house_cleaned.csv"
    raw_path = data_dir / "hangzhouhouseprice.csv"

    csv_path = cleaned_path if cleaned_path.exists() else raw_path
    if not csv_path.exists():
        print(f"Error: No CSV found at {cleaned_path} or {raw_path}")
        sys.exit(1)

    print(f"Loading {csv_path.name} ...")
    df = load_csv(csv_path)
    df = df.drop_duplicates()
    df = df.rename(columns=CSV_COLUMN_MAP)

    keep_cols = [v for v in CSV_COLUMN_MAP.values() if v in df.columns]
    df = df[keep_cols]

    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df = df.dropna(subset=["price"])
    if "introduction" in df.columns:
        df["introduction"] = df["introduction"].fillna("未知")
    # Clean numeric columns that may contain string values
    for col in ("room_count", "min_area", "max_area", "avg_area"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing = db.query(House).count()
        if existing > 0:
            print(f"Database already has {existing} houses. Skipping import.")
            return

        records = df.to_dict(orient="records")
        for i, record in enumerate(records):
            house = House(**record)
            db.add(house)
            if (i + 1) % 500 == 0:
                print(f"  Inserted {i + 1}/{len(records)} ...")

        db.commit()
        total = db.query(House).count()
        print(f"Done! Imported {total} houses into database.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
