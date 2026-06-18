from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from ...dependencies import DbSessionDep
from ..schemas.common import HealthCheckResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", summary="Health Check")
async def health_check(db: DbSessionDep):
    try:
        await db.execute(text("SELECT 1"))
        return HealthCheckResponse(status="healthy", database="connected")
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected"},
        )