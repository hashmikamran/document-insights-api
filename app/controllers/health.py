from fastapi import APIRouter, HTTPException
from app.database import db, redis_client

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    health = {"mongodb": "connected", "redis": "connected"}
    try:
        await db.command("ping")
    except Exception:
        health["mongodb"] = "disconnected"

    try:
        redis_client.ping()
    except Exception:
        health["redis"] = "disconnected"

    if "disconnected" in health.values():
        raise HTTPException(status_code=500, detail=health)
    return health