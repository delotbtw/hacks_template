import logging

from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import SessionDep
from app.core.errors import ErrorResponse
from app.core.redis import redis_client
from app.schemas.health import HealthRead, Status

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthRead, responses={500: {"model": ErrorResponse}})
async def health(session: SessionDep) -> HealthRead:
    db: Status = "ok"
    redis: Status = "ok"
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        logger.warning("DB health check failed")
        db = "error"
    try:
        await redis_client.ping()
    except Exception:
        logger.warning("Redis health check failed")
        redis = "error"
    return HealthRead(status="ok" if db == redis == "ok" else "error", db=db, redis=redis)
