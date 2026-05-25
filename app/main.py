import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import (
    AppException,
    FileTooLargeException,
    InvalidFileTypeException,
    MissingDrugColumnException,
)
from app.core.logging import LoggingMiddleware, configure_logging
from app.models.schema import ErrorResponse

settings = get_settings()
configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.exception_handler(InvalidFileTypeException)
@app.exception_handler(MissingDrugColumnException)
@app.exception_handler(FileTooLargeException)
async def app_known_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(detail=exc.message).model_dump(),
   )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_exception", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(detail="Internal server error").model_dump(),
    )
