from fastapi import APIRouter
from sqlalchemy import text

from app.config import get_settings
from app.database.session import engine

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    database = "ok"
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        database = "degraded"
    return {"status": "ok" if database == "ok" else "degraded", "database": database, "environment": get_settings().environment}
