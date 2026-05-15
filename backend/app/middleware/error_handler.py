from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
