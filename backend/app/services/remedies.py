import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.ayurvedic_home_remedies import AYURVEDIC_REMEDIES_SEED
from app.data.general_home_remedies import GENERAL_REMEDIES_SEED
from app.data.home_remedies_seed import HOME_REMEDIES_SEED
from app.data.life_stage_remedies import LIFE_STAGE_REMEDIES_SEED
from app.models.entities import HomeRemedy

logger = logging.getLogger(__name__)

ALL_CURATED_REMEDIES = (
    HOME_REMEDIES_SEED + AYURVEDIC_REMEDIES_SEED + GENERAL_REMEDIES_SEED + LIFE_STAGE_REMEDIES_SEED
)


def seed_home_remedies(db: Session) -> None:
    """Idempotent upsert: inserts each curated remedy if missing, or
    refreshes its fields (problem_tags, instructions, etc.) if the entry in
    ALL_CURATED_REMEDIES has changed since it was last seeded — so editing
    either source file and restarting the backend is enough to push a fix,
    no manual DB cleanup needed. Matches by exact title. Safe to call on
    every app startup."""
    for entry in ALL_CURATED_REMEDIES:
        existing = db.scalar(select(HomeRemedy).where(HomeRemedy.title == entry["title"]))
        if existing:
            for field, value in entry.items():
                setattr(existing, field, value)
        else:
            db.add(HomeRemedy(source="curated", status="approved", **entry))
    db.commit()
    logger.info("Home remedy seed check complete (%d curated entries defined)", len(ALL_CURATED_REMEDIES))


class RemedyService:
    @staticmethod
    def search(db: Session, query: str | None = None, tag: str | None = None, limit: int = 30) -> list[HomeRemedy]:
        statement = select(HomeRemedy).where(HomeRemedy.status == "approved")
        results = list(db.scalars(statement.order_by(HomeRemedy.upvotes.desc(), HomeRemedy.created_at.desc())))
        if tag:
            tag_lower = tag.lower()
            results = [r for r in results if any(tag_lower in t.lower() for t in r.problem_tags)]
        if query:
            query_lower = query.lower()
            results = [
                r for r in results
                if query_lower in r.title.lower()
                or any(query_lower in t.lower() for t in r.problem_tags)
                or query_lower in r.instructions.lower()
            ]
        return results[:limit]
