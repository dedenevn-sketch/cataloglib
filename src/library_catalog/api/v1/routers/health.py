from sqlalchemy import text
from fastapi import APIRouter

from ...dependencies import DbSessionDep
from ..schemas.common import HealthCheckResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", response_model=HealthCheckResponse, summary="Health Check")
async def health_check(db: DbSessionDep):
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return HealthCheckResponse(status="healthy", database=db_status)
