"""Small, provider-neutral hybrid ranking primitives used by retrieval."""
from dataclasses import dataclass


@dataclass(frozen=True)
class HybridScore:
    vector: float
    lexical: float
    combined: float


def combine_scores(vector_score: float, lexical_score: float, vector_weight: float = 0.75) -> HybridScore:
    vector_weight = max(0.0, min(1.0, vector_weight))
    return HybridScore(vector_score, lexical_score, round(vector_weight * vector_score + (1 - vector_weight) * lexical_score, 6))
