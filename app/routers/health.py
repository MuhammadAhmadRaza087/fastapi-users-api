import time
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlmodel import Session

from app import __version__
from app.database import get_session

router = APIRouter(tags=["health"])
STARTED_AT = time.time()


def _base() -> dict:
    return {
        "version": __version__,
        "uptime_seconds": int(time.time() - STARTED_AT),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health/live")
def liveness():
    """Process is up. No dependencies checked."""
    return {"status": "ok", **_base()}


@router.get("/health")
def health(session: Annotated[Session, Depends(get_session)]):
    """Full check: app is up and the database answers. 503 if the DB is down."""
    try:
        session.connection().execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    healthy = db_status == "ok"
    return JSONResponse(
        status_code=200 if healthy else 503,
        content={"status": "ok" if healthy else "degraded", "database": db_status, **_base()},
    )
