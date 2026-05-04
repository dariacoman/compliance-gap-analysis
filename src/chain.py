"""CHN-01..CHN-07 — five-step obligation-level reasoning chain.

The unit of comparison is the atomic obligation, not the chunk (D-008).

  Step 1 (CHN-01)  decompose user query into focused sub-questions
                   (1 LLM call; cap at 4 sub-questions per decisions.md §3)
  Step 2 (CHN-02)  per-sub-question regulation retrieval (no LLM call)
  Step 3 (CHN-03)  atomic obligation extraction from retrieved regulation
                   chunks (1 LLM call per sub-question; cap ~5 obligations)
  Step 4 (CHN-04)  per-obligation matching with threshold-grounded silence
                   detection. Phase 1: silence by cosine similarity vs
                   τ (deterministic, no LLM). Phase 2: 4-state classifier
                   for surviving obligations (1 batched LLM call per
                   sub-question; per-obligation is the FLEX-1 escalation).
                   Token-budget guard at 5K tokens for Gemma, 15K for Llama
                   (decisions.md §5).
  Step 5 (CHN-05)  register synthesis from per-obligation rows (1 LLM
                   call). All fields except `gap_characterisation`
                   mechanically derived from chain state.

Cost per uncached query: ~6–8 LLM calls. Verbose mode (CHN-06) prints
intermediate state — retrieval similarities, extracted obligations,
silence-threshold checks, per-obligation classifications. End-to-end
latency target on Gemma uncached: <90s (CHN-07).

Chain code types against `LLMClient` ABC (FLEX-6 strip-safety
discipline) — never against `RoutingClient` or a concrete adapter.

Reference: compliance-gap-analysis-spec.md § Group: Reasoning Chain.
"""
