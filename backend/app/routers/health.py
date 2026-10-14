from fastapi import APIRouter, Response
from sqlalchemy import text

from ..db import SessionLocal
from ..schemas import HealthOut

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthOut, responses={503: {"model": HealthOut}}, summary="Liveness and database check")
def health(response: Response):
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return HealthOut(status="ok", database="ok", version="0.2.0")
    except Exception:
        response.status_code = 503
        return HealthOut(status="degraded", database="unavailable", version="0.2.0")
