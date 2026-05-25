from fastapi import APIRouter

from app.api.v1.endpoints.upload import router as upload_router
from app.models.schema import HealthResponse

api_router = APIRouter()
api_router.include_router(upload_router, prefix="/drugs")


@api_router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service="drug-classification-api")
