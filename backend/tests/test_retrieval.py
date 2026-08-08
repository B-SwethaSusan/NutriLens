from app.rag.hybrid import combine_scores
from app.services.retrieval import cosine_similarity, lexical_score


def test_hybrid_score_weights_are_bounded_and_combined():
    score = combine_scores(0.8, 0.4)
    assert score.combined == 0.7
    assert combine_scores(0.8, 0.4, vector_weight=2).combined == 0.8


def test_local_similarity_primitives():
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == 1.0
    assert lexical_score("fiber protein", "Fiber is discussed") == 0.5
