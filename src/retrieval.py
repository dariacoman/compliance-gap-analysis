"""RET-01, RET-02 — multi-corpus chunk retrieval.

Provides the retriever class the chain reads against. Accepts a query
plus an optional corpus filter (regulation / policy / extras / guidance)
and returns top-k chunks with cosine similarity scores via
`util.dot_score` + `torch.topk` (RET-01). Sentence-level retrieval with
mean/min/max aggregation modes is the FLEX-3 intermediate step,
exercised at the retrieval-config freeze gate only if RET-01 chunk-level
retrieval underperforms (RET-02).

The retriever exposes raw cosine similarity scores so CHN-04 can apply
the silence threshold τ deterministically without any LLM call.

Default `top_k = 5` everywhere (decisions.md §6).

Reference: compliance-gap-analysis-spec.md § Group: Retrieval.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
import torch
from sentence_transformers import SentenceTransformer, util

from src.ingestion import Chunk


class ChunkEmbeddingRetriever:
    """Multi-corpus chunk retrieval over a pre-embedded corpus.

    Conceptually mirrors the week-7 RAG-tutorial ParagraphEmbeddingRetriever
    extended for the four-bucket architecture. Cosine similarity via
    util.dot_score; top-k via torch.topk; raw scores exposed to caller
    so CHN-04 silence detection can threshold τ deterministically.
    """

    def __init__(
        self,
        chunks: list[Chunk],
        embeddings: np.ndarray,
        chunk_ids: list[str],
        model: SentenceTransformer,
    ) -> None:
        if len(chunks) != len(chunk_ids):
            raise ValueError(
                f"chunks ({len(chunks)}) and chunk_ids ({len(chunk_ids)}) "
                f"length mismatch"
            )
        if embeddings.shape[0] != len(chunks):
            raise ValueError(
                f"embeddings rows ({embeddings.shape[0]}) and chunks "
                f"({len(chunks)}) length mismatch"
            )
        for i, (c, cid) in enumerate(zip(chunks, chunk_ids)):
            if c.chunk_id != cid:
                raise ValueError(
                    f"chunk[{i}].chunk_id ({c.chunk_id!r}) != "
                    f"chunk_ids[{i}] ({cid!r}) — alignment broken"
                )
        self.chunks = chunks
        self.embeddings = embeddings
        self.chunk_ids = chunk_ids
        self.model = model

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        corpus_filter: str | Sequence[str] | None = None,
    ) -> list[tuple[Chunk, float]]:
        """Return the top-k chunks for `query`, optionally filtered by
        corpus_tag. Scores are raw cosine similarity (vectors are
        already L2-normalised by `multi-qa-MiniLM-L6-cos-v1`)."""
        if top_k <= 0:
            return []

        if corpus_filter is None:
            filter_idx = list(range(len(self.chunks)))
        else:
            tags = (
                (corpus_filter,) if isinstance(corpus_filter, str)
                else tuple(corpus_filter)
            )
            filter_idx = [
                i for i, c in enumerate(self.chunks) if c.corpus_tag in tags
            ]

        if not filter_idx:
            return []

        # Keep query on CPU as numpy. `convert_to_tensor=True` would
        # produce an MPS tensor on Apple Silicon while the chunk
        # embeddings are CPU numpy — `util.dot_score` then errors with
        # device mismatch. Numpy on both sides keeps it portable.
        q_emb = self.model.encode(
            query, convert_to_numpy=True, normalize_embeddings=False
        )
        filtered = self.embeddings[filter_idx]
        scores = util.dot_score(q_emb, filtered)[0]

        k = min(top_k, len(scores))
        top_values, top_indices = torch.topk(scores, k)

        return [
            (self.chunks[filter_idx[int(local_i)]], float(value))
            for value, local_i in zip(top_values.tolist(), top_indices.tolist())
        ]


def build_retriever(
    manifest_path: Path = Path("corpus/manifest.json"),
    model_name: str = "multi-qa-MiniLM-L6-cos-v1",
    cache_dir: Path = Path("embeddings"),
) -> ChunkEmbeddingRetriever:
    """End-to-end factory: load → chunk → embed → wrap in retriever.

    Reuses the ING-03 SentenceTransformer singleton, so the model is
    loaded exactly once across ingestion and retrieval.
    """
    from src.ingestion import (
        _get_st_model,
        chunk_corpus,
        embed_chunks,
        load_corpus,
    )

    chunks = chunk_corpus(load_corpus(manifest_path))
    embeddings, chunk_ids = embed_chunks(chunks, model_name, cache_dir)
    model = _get_st_model(model_name)
    return ChunkEmbeddingRetriever(chunks, embeddings, chunk_ids, model)
