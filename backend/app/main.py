import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.router import api_router
from app.config import settings
from app.database import Base, engine
from app.middleware.error_handler import generic_error_handler

logger.remove()
logger.add(sys.stderr, level=settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    data_dir = Path(settings.database_url.replace("sqlite:///", ""))
    if not data_dir.parent.exists():
        data_dir.parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    logger.info(f"Database tables ready at {settings.database_url}")
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
