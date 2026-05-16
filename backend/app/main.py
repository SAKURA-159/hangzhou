import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.router import api_router
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.middleware.error_handler import generic_error_handler

logger.remove()
logger.add(sys.stderr, level=settings.log_level)


def _seed_from_csv():
    """Auto-seed database from CSV if empty."""
    import pandas as pd
    from app.models.house import House

    csv_path = Path(__file__).resolve().parent.parent / "data" / "hangzhou_house_cleaned.csv"
    if not csv_path.exists():
        logger.info("No seed CSV found, skipping auto-seed")
        return

    db = SessionLocal()
    try:
        if db.query(House).count() > 0:
            logger.info("Database already has data, skipping auto-seed")
            return

        logger.info(f"Auto-seeding from {csv_path} ...")
        for enc in ["utf-8-sig", "utf-8", "gbk", "gb18030"]:
            try:
                df = pd.read_csv(csv_path, encoding=enc)
                break
            except UnicodeDecodeError:
                continue

        df = df.drop_duplicates()
        column_map = {
            "House name": "name", "House place": "place",
            "House price": "price", "House introduction": "introduction",
            "room_count": "room_count", "min_area": "min_area",
            "max_area": "max_area", "avg_area": "avg_area",
            "property_type": "property_type", "price_flag": "price_flag",
        }
        df = df.rename(columns=column_map)
        keep_cols = [v for v in column_map.values() if v in df.columns]
        df = df[keep_cols]

        if "price" in df.columns:
            df["price"] = pd.to_numeric(df["price"], errors="coerce")
            df = df.dropna(subset=["price"])
        for col in ("room_count", "min_area", "max_area", "avg_area"):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        records = df.to_dict(orient="records")
        for rec in records:
            db.add(House(**rec))
        db.commit()
        logger.info(f"Auto-seed complete: {db.query(House).count()} houses")
    except Exception as e:
        logger.error(f"Auto-seed failed: {e}")
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    data_dir = Path(settings.database_url.replace("sqlite:///", ""))
    if not data_dir.parent.exists():
        data_dir.parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    logger.info(f"Database tables ready at {settings.database_url}")
    _seed_from_csv()
    yield


app = FastAPI(
    title="杭州房价分析 API",
    description="RESTful API for Hangzhou housing price analysis",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(Exception, generic_error_handler)

app.include_router(api_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
