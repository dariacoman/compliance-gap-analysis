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
