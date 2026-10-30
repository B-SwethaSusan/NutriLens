import re

from sqlalchemy.orm import Session

from app.agents.base import AgentResult
from app.services.remedies import RemedyService

_STOPWORDS = {"a", "i", "for", "the", "have", "got", "my", "me", "is", "has", "with", "of", "to", "and"}


class RemedyAgent:
    """Searches the curated + community-approved home-remedy library for
    whatever ailment the message mentions. Falls back to returning the
    most generically-tagged remedies if no keyword match is found, rather
    than returning nothing."""

    def handle(self, db: Session, message: str) -> AgentResult:
        words = [w for w in re.findall(r"[a-zA-Z]+", message.lower()) if w not in _STOPWORDS and len(w) > 2]
        matches = []
        for word in words:
            matches.extend(RemedyService.search(db, query=word, limit=5))
        seen_ids = set()
        unique_matches = []
        for remedy in matches:
            if remedy.id not in seen_ids:
                seen_ids.add(remedy.id)
                unique_matches.append(remedy)

        warnings = []
        if not unique_matches:
            warnings.append("No matching remedy found for this description — try different words, or submit one via POST /api/remedies if you know one.")

        return AgentResult(
            agent="remedy",
            content={"remedies": [
                {"id": r.id, "title": r.title, "problem_tags": r.problem_tags, "ingredients": r.ingredients,
                 "instructions": r.instructions, "caution": r.caution}
                for r in unique_matches[:5]
            ]},
            warnings=warnings,
        )
