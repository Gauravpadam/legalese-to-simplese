from fastapi import APIRouter, Depends
from services.health_service import get_health_status

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/", summary="Health check", description="Returns OK if the service is alive")
async def health(status: dict = Depends(get_health_status)):
    return status
