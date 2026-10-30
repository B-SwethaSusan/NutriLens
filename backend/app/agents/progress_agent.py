from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.base import AgentResult
from app.models import HealthProfile, ProgressLog, User
from app.services.progress import ProgressService


class ProgressAgent:
    """Reads logged progress, computes the trend, and flags drift from goal."""

    async def handle(self, db: Session, user: User) -> AgentResult:
        logs = list(db.scalars(select(ProgressLog).where(ProgressLog.owner_id == user.id).order_by(ProgressLog.log_date)))
        profile = db.scalar(select(HealthProfile).where(HealthProfile.owner_id == user.id))
        trend = ProgressService.compute_trend(logs, profile)
        warnings = []
        if trend is None:
            warnings.append("Not enough logged entries yet to compute a trend (need at least 3 weight logs).")
        elif trend["on_track"] is False:
            warnings.append("Progress is tracking below the stated goal pace.")
        return AgentResult(agent="progress", content={"logs_count": len(logs), "trend": trend}, warnings=warnings)
