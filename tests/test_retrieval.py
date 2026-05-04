"""RET-01 unit + integration tests."""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pytest
from sentence_transformers import util

from src.ingestion import Chunk
from src.retrieval import ChunkEmbeddingRetriever


# === Helpers / stubs =====================================================


def _make_chunk(chunk_id: str, corpus_tag: str = "REG", text: str = "body") -> Chunk:
    return Chunk(
        chunk_id=chunk_id, parent_document_id=chunk_id,
        corpus_tag=corpus_tag, document_id=chunk_id, section_reference=chunk_id,
        source_url="", chunk_text=text,
        file_path=f"{corpus_tag.lower()}/{chunk_id}.txt", sha256_short="abc",
        sentences=(text,),
    )


class _StubModel:
    """Fake SentenceTransformer-shaped object for unit tests.

    Returns a deterministic vector based on the input string hash; never
    touches the real network or disk.
    """

    def encode(self, query, **kwargs):
        rng = np.random.default_rng(abs(hash(query)) % (2**32))
        v = rng.standard_normal(8).astype(np.float32)
        v /= np.linalg.norm(v)
        return v


# === Unit tests ===========================================================


def test_init_rejects_mismatched_chunks_and_chunk_ids() -> None:
    chunks = [_make_chunk("a"), _make_chunk("b")]
    embeddings = np.zeros((2, 8), dtype=np.float32)
    with pytest.raises(ValueError, match="length mismatch"):
        ChunkEmbeddingRetriever(chunks, embeddings, ["a"], _StubModel())


def test_init_rejects_mismatched_embeddings_rows() -> None:
    chunks = [_make_chunk("a"), _make_chunk("b")]
    embeddings = np.zeros((3, 8), dtype=np.float32)
    with pytest.raises(ValueError, match="length mismatch"):
        ChunkEmbeddingRetriever(chunks, embeddings, ["a", "b"], _StubModel())


def test_init_rejects_misaligned_chunk_ids() -> None:
    chunks = [_make_chunk("a"), _make_chunk("b")]
    embeddings = np.zeros((2, 8), dtype=np.float32)
    with pytest.raises(ValueError, match="alignment broken"):
        ChunkEmbeddingRetriever(chunks, embeddings, ["a", "wrong"], _StubModel())


def _retriever_with_n(n: int, corpus_tag: str = "REG") -> ChunkEmbeddingRetriever:
    chunks = [_make_chunk(f"c{i}", corpus_tag, f"body {i}") for i in range(n)]
    embeddings = np.random.rand(n, 8).astype(np.float32)
    embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
    chunk_ids = [c.chunk_id for c in chunks]
    return ChunkEmbeddingRetriever(chunks, embeddings, chunk_ids, _StubModel())


def test_retrieve_top_k_zero_returns_empty() -> None:
    r = _retriever_with_n(5)
    assert r.retrieve("anything", top_k=0) == []


def test_retrieve_filter_with_no_matches_returns_empty() -> None:
    r = _retriever_with_n(5, corpus_tag="REG")
    assert r.retrieve("anything", top_k=5, corpus_filter="DEP") == []


def test_retrieve_top_k_larger_than_corpus_returns_all() -> None:
    r = _retriever_with_n(3)
    out = r.retrieve("anything", top_k=10)
    assert len(out) == 3


def test_retrieve_results_sorted_by_score_descending() -> None:
    r = _retriever_with_n(20)
    out = r.retrieve("anything", top_k=5)
    scores = [s for _c, s in out]
    assert scores == sorted(scores, reverse=True)


def test_retrieve_filter_string_and_tuple_equivalent() -> None:
    chunks = [_make_chunk(f"r{i}", "REG") for i in range(3)] + \
             [_make_chunk(f"o{i}", "OPS") for i in range(3)]
    embeddings = np.random.rand(6, 8).astype(np.float32)
    embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
    ids = [c.chunk_id for c in chunks]
    r = ChunkEmbeddingRetriever(chunks, embeddings, ids, _StubModel())

    by_str = r.retrieve("q", top_k=10, corpus_filter="REG")
    by_tup = r.retrieve("q", top_k=10, corpus_filter=("REG",))
    assert [c.chunk_id for c, _ in by_str] == [c.chunk_id for c, _ in by_tup]


def test_retrieve_scores_match_dot_score_directly() -> None:
    chunks = [_make_chunk(f"c{i}") for i in range(5)]
    embeddings = np.random.rand(5, 8).astype(np.float32)
    embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
    ids = [c.chunk_id for c in chunks]
    model = _StubModel()
    r = ChunkEmbeddingRetriever(chunks, embeddings, ids, model)

    out = r.retrieve("q", top_k=5)
    q_emb = model.encode("q")
    direct = util.dot_score(q_emb, embeddings)[0].tolist()
    out_scores = {c.chunk_id: s for c, s in out}
    assert all(abs(out_scores[ids[i]] - direct[i]) < 1e-5 for i in range(5))


# === Integration tests (real corpus, session-scoped fixture) =============


def test_retrieve_full_corpus_returns_5(corpus_retriever) -> None:
    out = corpus_retriever.retrieve("Article 22", top_k=5)
    assert len(out) == 5


def test_retrieve_scores_in_cosine_range(corpus_retriever) -> None:
    out = corpus_retriever.retrieve("Article 22", top_k=10)
    for _c, score in out:
        assert -1.0 <= score <= 1.0


def test_retrieve_descending_order(corpus_retriever) -> None:
    out = corpus_retriever.retrieve("data protection", top_k=10)
    scores = [s for _c, s in out]
    assert scores == sorted(scores, reverse=True)


def test_retrieve_filter_reg_only(corpus_retriever) -> None:
    out = corpus_retriever.retrieve("Article 22", top_k=10, corpus_filter="REG")
    for chunk, _s in out:
        assert chunk.corpus_tag == "REG"


def test_retrieve_filter_deployer_side_excludes_regulation(corpus_retriever) -> None:
    out = corpus_retriever.retrieve(
        "automated decision making", top_k=10,
        corpus_filter=("DEP", "DEP_EXTRAS", "OPS"),
    )
    for chunk, _s in out:
        assert chunk.corpus_tag != "REG"


def test_retrieve_on_topic_query_scores_above_floor(corpus_retriever) -> None:
    out = corpus_retriever.retrieve(
        "red-teaming for high-risk AI systems", top_k=1
    )
    assert len(out) == 1
    assert out[0][1] >= 0.4


def test_retrieve_off_topic_query_scores_below_floor(corpus_retriever) -> None:
    out = corpus_retriever.retrieve("recipe for chocolate cake", top_k=1)
    assert len(out) == 1
    # Off-topic should not exceed τ=0.35 by much; loose 0.4 ceiling.
    assert out[0][1] <= 0.4


def test_retrieve_under_200ms(corpus_retriever) -> None:
    # Warm-up call (first call pays cold-import / initial-tensor cost).
    corpus_retriever.retrieve("warm-up", top_k=5)
    start = time.perf_counter()
    corpus_retriever.retrieve("Article 22 automated decisions", top_k=5)
    elapsed = time.perf_counter() - start
    assert elapsed < 0.2, f"top-5 retrieval took {elapsed:.3f}s"


def test_retrieve_smoke_recall_on_test_queries(corpus_retriever) -> None:
    """For each of the 5 hand-written test queries, at least one chunk
    in the top-5 must come from one of the expected document_ids.

    Lenient sanity floor; the spec's full ≥60% recall target is
    freeze-gate work, not unit-test bar.
    """
    test_queries = [
        # Q1 — multi-facet AI Act + GDPR Art 22
        ("TalentLens compliance under EU AI Act Annex III on employment "
         "AI — am I covered on Article 13 deployer instructions, Article "
         "14 human oversight, Article 26 logs and worker information?",
         {"eu-ai-act-2024-1689", "uk-gdpr-art-22"}),
        # Q2 — strong-match red-teaming
        ("Does our policy address the red-teaming requirements before "
         "deploying a high-risk AI system to production?",
         {"novara-ai-policy-v3.1", "eu-ai-act-2024-1689"}),
        # Q3 — Art 22 sub-clauses
        ("How do we meet GDPR Article 22 requirements on solely "
         "automated decisions affecting candidates?",
         {"uk-gdpr-art-22", "07-article-22-fairness", "10-human-review"}),
        # Q4 — ambiguous transparency
        ("Are we doing enough on transparency for candidates assessed "
         "by TalentLens?",
         {"uk-gdpr-art-13", "uk-gdpr-art-14", "novara-talentlens-transparency-notice", "03-transparency"}),
        # Q5 — FRIA silence target
        ("Have we performed a Fundamental Rights Impact Assessment "
         "under EU AI Act Article 27 for TalentLens as a deployer of "
         "an Annex III high-risk system?",
         {"eu-ai-act-2024-1689"}),
    ]
    for query, expected_doc_ids in test_queries:
        out = corpus_retriever.retrieve(query, top_k=5)
        retrieved_doc_ids = {c.document_id for c, _ in out}
        # Lenient: at least one expected doc_id appears in top-5.
        assert retrieved_doc_ids & expected_doc_ids, (
            f"Q: {query[:60]}…\n"
            f"  expected any of: {expected_doc_ids}\n"
            f"  got: {retrieved_doc_ids}"
        )


def test_retrieve_q5_finds_article_27(corpus_retriever) -> None:
    """Q5 demo target — FRIA. An Article-27 chunk must surface in top-5."""
    out = corpus_retriever.retrieve(
        "Fundamental Rights Impact Assessment under Article 27 high-risk AI",
        top_k=5,
    )
    has_art27 = any(
        c.section_reference.startswith("EU AI Act Article 27") for c, _ in out
    )
    assert has_art27, (
        "Article 27 should be in top-5 for an explicit FRIA query.\n"
        "Got:\n  " + "\n  ".join(c.section_reference for c, _ in out)
    )
